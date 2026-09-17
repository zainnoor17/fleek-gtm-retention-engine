"""Run orchestration: state store, new-account ingestion, change detection, idempotent action logging."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from . import config as C
from .execution import generate_execution_plan
from .pipeline import clean_data, run_analytics

ENGINE_VERSION = "stage5-v1"
SNAPSHOT_COLS = ["account_id", "primary_nba", "execution_status", "attention_priority", "migration_progress_status",
                 "guardrail_codes", "action_state", "action_key", "input_row_hash", "run_id"]
LOG_COLS = ["run_id", "run_timestamp", "account_id", "previous_primary_nba", "current_primary_nba", "previous_execution_status",
            "current_execution_status", "previous_priority", "current_priority", "action_state", "change_type", "change_flags",
            "generated_action", "human_owner", "notes"]
HUMAN = lambda s: s != "Ready — Automated"


def process_new_accounts(base_raw: pd.DataFrame, new_raw: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Upsert: existing IDs are replaced by the newer row (no duplicates); unseen IDs are appended."""
    base, new = clean_data(base_raw), clean_data(new_raw)
    existing = set(base["account_id"])
    updated = sorted(set(new["account_id"]) & existing)
    added = sorted(set(new["account_id"]) - existing)
    merged = pd.concat([base[~base["account_id"].isin(new["account_id"])], new], ignore_index=True)
    merged = merged.sort_values("account_id").reset_index(drop=True)
    assert merged["account_id"].is_unique
    return merged, {"updated_ids": updated, "added_ids": added, "base_size": len(base), "new_rows": len(new), "result_size": len(merged)}


def _row_hash(df: pd.DataFrame) -> pd.Series:
    cols = C.REQUIRED_COLUMNS
    x = df[cols].astype(object).where(df[cols].notna(), "")
    return x.map(str).agg("|".join, axis=1).map(lambda s: hashlib.sha1(s.encode()).hexdigest()[:12])


def fingerprint(df: pd.DataFrame) -> str:
    h = hashlib.sha256((ENGINE_VERSION + "".join(sorted(_row_hash(clean_data(df))))).encode()).hexdigest()
    return h[:16]


def _action_key(e: pd.DataFrame) -> pd.Series:
    """Identity of an outbound/queued action. Same key => same action => never regenerated."""
    s = (e["account_id"] + "|" + e["playbook_id"] + "|" + e["nba_reason_code"] + "|" + e["execution_status"] + "|"
         + e["message_template_id"] + "|" + e["secondary_test_template_id"])
    return s.map(lambda x: hashlib.sha1(x.encode()).hexdigest()[:12])


def compare_runs(prev: pd.DataFrame | None, cur: pd.DataFrame) -> pd.DataFrame:
    """Return per-account change_type (primary) and change_flags (all)."""
    c = cur[["account_id", "primary_nba", "execution_status", "attention_priority", "migration_progress_status", "guardrail_codes", "input_row_hash"]].copy()
    if prev is None or prev.empty:
        c["change_type"], c["change_flags"] = "BASELINE", "BASELINE"
        for k in ["primary_nba", "execution_status", "attention_priority", "migration_progress_status", "guardrail_codes", "input_row_hash"]:
            c["prev_" + k] = ""
        return c
    p = prev.set_index("account_id")
    for k in ["primary_nba", "execution_status", "attention_priority", "migration_progress_status", "guardrail_codes", "input_row_hash"]:
        c["prev_" + k] = c["account_id"].map(p[k]).fillna("")
    is_new = ~c["account_id"].isin(p.index)
    pn = c["prev_attention_priority"].str[1:].apply(lambda x: int(x) if x else 9)
    cn = c["attention_priority"].str[1:].astype(int)
    flags = {
        "NEW_ACCOUNT": is_new,
        "NBA_CHANGED": ~is_new & (c["prev_primary_nba"] != c["primary_nba"]),
        "PRIORITY_INCREASED": ~is_new & (cn < pn),
        "PRIORITY_DECREASED": ~is_new & (cn > pn),
        "EXECUTION_STATUS_CHANGED": ~is_new & (c["prev_execution_status"] != c["execution_status"]),
        "ENTERED_HUMAN_QUEUE": ~is_new & ~HUMAN(c["prev_execution_status"]) & HUMAN(c["execution_status"]),
        "LEFT_HUMAN_QUEUE": ~is_new & HUMAN(c["prev_execution_status"]) & ~HUMAN(c["execution_status"]),
        "MIGRATION_PROGRESS_CHANGED": ~is_new & (c["prev_migration_progress_status"] != c["migration_progress_status"]),
        "GUARDRAILS_CHANGED": ~is_new & (c["prev_guardrail_codes"] != c["guardrail_codes"]),   # internal only
        "DATA_UPDATED": ~is_new & (c["prev_input_row_hash"] != c["input_row_hash"]),   # internal only
    }
    order = list(flags)  # precedence
    c["change_flags"] = pd.DataFrame(flags).apply(lambda r: ";".join(k for k in order if r[k]), axis=1)
    material = [k for k in order if k not in ("DATA_UPDATED", "GUARDRAILS_CHANGED")]
    c["change_type"] = pd.DataFrame(flags)[material].apply(lambda r: next((k for k in material if r[k]), "NO_MATERIAL_CHANGE"), axis=1)
    return c


@dataclass
class RunStore:
    """File-backed state (CSV) so every run is inspectable. Swap for a DB table in production."""
    root: Path

    def __post_init__(self):
        self.root = Path(self.root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _read(self, name, cols):
        f = self.root / f"{name}.csv"
        return pd.read_csv(f, dtype=str, keep_default_na=False) if f.exists() else pd.DataFrame(columns=cols)

    def _write(self, name, df):
        df.to_csv(self.root / f"{name}.csv", index=False)

    snapshot = property(lambda self: self._read("account_snapshot", SNAPSHOT_COLS))
    log = property(lambda self: self._read("action_log", LOG_COLS))
    registry = property(lambda self: self._read("action_registry", ["action_key", "account_id", "run_id", "playbook_id", "message_template_id"]))
    history = property(lambda self: self._read("run_history", ["run_id"]))

    def run(self, raw: pd.DataFrame, run_timestamp: str, label: str = "", monitoring: pd.DataFrame | None = None) -> dict:
        fp = fingerprint(raw)
        hist = self.history
        last_fp = hist["input_fingerprint"].iloc[-1] if len(hist) else None
        run_id = f"RUN{len(hist) + 1:03d}"
        d = run_analytics(raw)
        if monitoring is not None:
            from .pipeline import migration_progress
            d["migration_progress_status"] = migration_progress(d, monitoring)
        e = generate_execution_plan(d)
        e["input_row_hash"] = _row_hash(clean_data(raw)).values
        e["action_key"] = _action_key(e)

        prev = self.snapshot if len(hist) else None
        ch = compare_runs(prev, e)
        e = e.merge(ch[["account_id", "change_type", "change_flags"]], on="account_id")
        reg = self.registry
        known = set(reg["action_key"])
        is_new_action = ~e["action_key"].isin(known)

        # action_state: carry forward when nothing material changed; otherwise the fresh initial state
        if prev is not None and len(prev):
            ps = prev.set_index("account_id")["action_state"]
            carry = (e["change_type"] == "NO_MATERIAL_CHANGE") & e["account_id"].isin(ps.index)
            e.loc[carry, "action_state"] = e.loc[carry, "account_id"].map(ps)
        e["generated_action"] = e["action_key"].where(is_new_action, "")

        identical_input = (fp == last_fp)
        log_rows = e[(e["change_type"] != "NO_MATERIAL_CHANGE") & (not identical_input)].copy()
        log_rows = log_rows.assign(
            run_id=run_id, run_timestamp=run_timestamp,
            previous_primary_nba=log_rows["account_id"].map(ch.set_index("account_id")["prev_primary_nba"]),
            current_primary_nba=log_rows["primary_nba"],
            previous_execution_status=log_rows["account_id"].map(ch.set_index("account_id")["prev_execution_status"]),
            current_execution_status=log_rows["execution_status"],
            previous_priority=log_rows["account_id"].map(ch.set_index("account_id")["prev_attention_priority"]),
            current_priority=log_rows["attention_priority"],
            human_owner=log_rows["owner_role"],
            notes=log_rows["draft_status"],
        )[LOG_COLS]
        if identical_input:
            e["generated_action"] = ""  # identical input: nothing new is generated

        new_reg = e[e["generated_action"] != ""][["action_key", "account_id", "playbook_id", "message_template_id"]].assign(run_id=run_id)
        summary = {
            "run_id": run_id, "run_timestamp": run_timestamp, "label": label, "input_fingerprint": fp,
            "identical_to_previous_input": identical_input, "accounts": len(e),
            "log_rows_written": len(log_rows), "new_actions_generated": len(new_reg),
            "change_type_counts": json.dumps(e["change_type"].value_counts().to_dict()),
        }
        self._write("action_log", pd.concat([self.log, log_rows.astype(str)], ignore_index=True))
        self._write("action_registry", pd.concat([reg, new_reg.astype(str)], ignore_index=True))
        self._write("account_snapshot", e.assign(run_id=run_id)[SNAPSHOT_COLS].astype(str))
        self._write("run_history", pd.concat([hist, pd.DataFrame([summary]).astype(str)], ignore_index=True))
        return {"summary": summary, "analytics": d, "execution": e, "changes": ch, "log_rows": log_rows}
