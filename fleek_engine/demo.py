"""Demo / UI service layer over the engine.

Wraps RunStore so the Streamlit app and demo_runs.py share one code path:
baseline run -> new_accounts upsert -> identical rerun, plus local-only workflow
state updates with an audit trail. No business rules live here, and nothing is
ever sent externally.
"""
from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from .pipeline import load_data
from .runs import RunStore, process_new_accounts
from .validate import guardrail_checks

DEFAULT_SOURCE = Path(__file__).resolve().parent.parent / "data" / "Fleek_Retention_Case_Study_Portfolio_Data.xlsx"
AUDIT_COLS = ["timestamp", "account_id", "acting_role", "decision", "from_state", "to_state", "note"]

# Local-only workflow transitions: current action_state -> {button label: (new state, decision code)}
WORKFLOW = {
    "Awaiting Human Review": {"Mark reviewed - approve": ("Not Started", "REVIEW_APPROVED"),
                              "Reject action": ("No Action Required", "REVIEW_REJECTED")},
    "Awaiting Sign-Off": {"Approve (sign-off)": ("Not Started", "SIGNOFF_APPROVED"),
                          "Decline": ("No Action Required", "SIGNOFF_DECLINED")},
    "Draft Ready": {"Mark In Progress": ("In Progress", "STARTED")},
    "Not Started": {"Mark In Progress": ("In Progress", "STARTED")},
    "In Progress": {"Mark Completed": ("Completed", "COMPLETED")},
}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class DemoSession:
    def __init__(self, state_dir: str | Path, source: str | Path = DEFAULT_SOURCE):
        self.dir = Path(state_dir)
        self.source = Path(source)
        self.store = RunStore(self.dir)
        (self.dir / "runs").mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------ runs
    def reset(self) -> None:
        shutil.rmtree(self.dir, ignore_errors=True)
        self.__init__(self.dir, self.source)

    def _save(self, res: dict, info: dict | None) -> dict:
        rid = res["summary"]["run_id"]
        res["execution"].to_csv(self.dir / "runs" / f"{rid}_plan.csv", index=False)
        guardrail_checks(res["execution"]).to_csv(self.dir / "runs" / f"{rid}_guardrails.csv", index=False)
        meta = dict(res["summary"])
        meta["ingestion"] = info or {}
        (self.dir / "runs" / f"{rid}_meta.json").write_text(json.dumps(meta, indent=2, default=str))
        return res

    def run_baseline(self, timestamp: str | None = None) -> dict:
        base = load_data(self.source, "Accounts")
        return self._save(self.store.run(base, timestamp or _now(), "Baseline: 300-account portfolio"), None)

    def run_new_accounts(self, timestamp: str | None = None, label: str = "new_accounts upsert") -> dict:
        merged, info = process_new_accounts(load_data(self.source, "Accounts"), load_data(self.source, "new_accounts"))
        return self._save(self.store.run(merged, timestamp or _now(), label), info)

    def ensure_baseline(self) -> None:
        if not self.run_ids():
            self.run_baseline()

    # ------------------------------------------------------------------ reads
    def run_ids(self) -> list[str]:
        h = self.store.history
        return list(h["run_id"]) if len(h) else []

    def history(self) -> pd.DataFrame:
        return self.store.history

    def meta(self, run_id: str) -> dict:
        return json.loads((self.dir / "runs" / f"{run_id}_meta.json").read_text())

    def plan(self, run_id: str | None = None) -> pd.DataFrame:
        """Execution plan for a run, with the CURRENT action_state from the snapshot for the latest run."""
        ids = self.run_ids()
        run_id = run_id or ids[-1]
        p = pd.read_csv(self.dir / "runs" / f"{run_id}_plan.csv", keep_default_na=False)
        if run_id == ids[-1]:
            snap = self.store.snapshot.set_index("account_id")["action_state"]
            p["action_state"] = p["account_id"].map(snap).fillna(p["action_state"])
        return p

    def guardrails(self, run_id: str | None = None) -> pd.DataFrame:
        run_id = run_id or self.run_ids()[-1]
        return pd.read_csv(self.dir / "runs" / f"{run_id}_guardrails.csv")

    def log(self) -> pd.DataFrame:
        return self.store.log

    def registry(self) -> pd.DataFrame:
        return self.store.registry

    def audit(self) -> pd.DataFrame:
        f = self.dir / "workflow_audit.csv"
        return pd.read_csv(f, dtype=str, keep_default_na=False) if f.exists() else pd.DataFrame(columns=AUDIT_COLS)

    # ------------------------------------------------------------------ local workflow (never external)
    def allowed_actions(self, action_state: str, execution_status: str) -> dict:
        if execution_status.startswith("HOLD") or execution_status == "Ready — Automated":
            return {}
        return WORKFLOW.get(action_state, {})

    def update_action_state(self, account_id: str, button: str, acting_role: str, note: str = "") -> str:
        snap = self.store.snapshot
        idx = snap.index[snap["account_id"] == account_id]
        if len(idx) != 1:
            raise KeyError(account_id)
        cur = snap.loc[idx[0], "action_state"]
        plan = self.plan()
        status = plan.loc[plan["account_id"] == account_id, "execution_status"].iloc[0]
        allowed = self.allowed_actions(cur, status)
        if button not in allowed:
            raise ValueError(f"'{button}' not allowed from state '{cur}'")
        new_state, decision = allowed[button]
        snap.loc[idx[0], "action_state"] = new_state
        self.store._write("account_snapshot", snap)
        row = pd.DataFrame([dict(timestamp=_now(), account_id=account_id, acting_role=acting_role, decision=decision,
                                 from_state=cur, to_state=new_state, note=note or "Local demo state only - nothing sent")])
        self.store._write("workflow_audit", pd.concat([self.audit(), row], ignore_index=True))
        return new_state
