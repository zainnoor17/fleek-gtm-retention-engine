"""Reproducible demo: RUN001 baseline -> RUN002 new_accounts upsert -> RUN003 identical rerun.

Writes evidence to demo_state/ (engine state) and demo_outputs/ (queues, guardrails, summary).
Usage:  python demo_runs.py
"""
import json
import shutil
from pathlib import Path

from fleek_engine.demo import DemoSession
from fleek_engine.execution import EXEC_QUEUE_COLUMNS
from fleek_engine.validate import guardrail_checks

STATE, OUT = Path("demo_state"), Path("demo_outputs")


def save(res, name):
    OUT.mkdir(exist_ok=True)
    res["execution"][EXEC_QUEUE_COLUMNS + ["change_type", "change_flags", "generated_action"]].to_csv(OUT / f"{name}_execution_queue.csv", index=False)
    guardrail_checks(res["execution"]).to_csv(OUT / f"{name}_guardrails.csv", index=False)


def main():
    shutil.rmtree(OUT, ignore_errors=True)
    s = DemoSession(STATE)
    s.reset()
    r1 = s.run_baseline("2026-09-18T07:00Z"); save(r1, "run1")
    r2 = s.run_new_accounts("2026-09-19T07:00Z", "Second run: new_accounts upsert"); save(r2, "run2")
    r3 = s.run_new_accounts("2026-09-19T07:05Z", "Idempotency: identical input re-run"); save(r3, "run3")
    info = s.meta("RUN002")["ingestion"]
    shutil.rmtree(STATE / "runs", ignore_errors=True)   # full plans are regenerable; keep the committed evidence small
    snap = s.store.snapshot
    summary = {
        "ingestion": info,
        "runs": [r["summary"] for r in (r1, r2, r3)],
        "snapshot_rows": len(snap), "snapshot_unique_ids": snap["account_id"].nunique(),
        "log_rows_total": len(s.log()), "registry_rows_total": len(s.registry()),
        "registry_unique_keys": s.registry()["action_key"].nunique(),
        "guardrail_violations": {n: int(guardrail_checks(r["execution"])["violations"].sum()) for n, r in (("run1", r1), ("run2", r2), ("run3", r3))},
    }
    (OUT / "demo_summary.json").write_text(json.dumps(summary, indent=2, default=str))
    r2["log_rows"].to_csv(OUT / "run2_changes.csv", index=False)
    print(json.dumps({k: v for k, v in summary.items() if k != "ingestion"}, indent=2, default=str))


if __name__ == "__main__":
    main()
