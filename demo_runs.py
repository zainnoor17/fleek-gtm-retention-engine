"""Reproducible demo: baseline run -> new_accounts second run -> identical-input rerun (idempotency)."""
import json
import shutil
from pathlib import Path

import pandas as pd

from fleek_engine.execution import EXEC_QUEUE_COLUMNS
from fleek_engine.pipeline import load_data
from fleek_engine.runs import RunStore, process_new_accounts
from fleek_engine.validate import guardrail_checks

SRC = "data/Fleek_Retention_Case_Study_Portfolio_Data.xlsx"
STATE, OUT = Path("demo_state"), Path("demo_outputs")


def save(res, name):
    OUT.mkdir(exist_ok=True)
    res["execution"][EXEC_QUEUE_COLUMNS + ["change_type", "change_flags", "generated_action"]].to_csv(OUT / f"{name}_execution_queue.csv", index=False)
    guardrail_checks(res["execution"]).to_csv(OUT / f"{name}_guardrails.csv", index=False)


def main():
    shutil.rmtree(STATE, ignore_errors=True); shutil.rmtree(OUT, ignore_errors=True)
    store = RunStore(STATE)
    base = load_data(SRC, "Accounts")
    r1 = store.run(base, "2026-09-18T07:00Z", "Baseline: 300-account portfolio"); save(r1, "run1")

    merged, info = process_new_accounts(base, load_data(SRC, "new_accounts"))
    r2 = store.run(merged, "2026-09-19T07:00Z", "Second run: new_accounts upsert"); save(r2, "run2")

    merged_again, _ = process_new_accounts(base, load_data(SRC, "new_accounts"))
    r3 = store.run(merged_again, "2026-09-19T07:05Z", "Idempotency: identical input re-run"); save(r3, "run3")

    snap = store.snapshot
    summary = {
        "ingestion": {k: v for k, v in info.items()},
        "runs": [r["summary"] for r in (r1, r2, r3)],
        "snapshot_rows": len(snap), "snapshot_unique_ids": snap["account_id"].nunique(),
        "log_rows_total": len(store.log), "registry_rows_total": len(store.registry),
        "registry_unique_keys": store.registry["action_key"].nunique(),
        "guardrail_violations": {n: int(guardrail_checks(r["execution"])["violations"].sum()) for n, r in (("run1", r1), ("run2", r2), ("run3", r3))},
    }
    (OUT / "demo_summary.json").write_text(json.dumps(summary, indent=2, default=str))
    r2["log_rows"].to_csv(OUT / "run2_changes.csv", index=False)
    print(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    main()
