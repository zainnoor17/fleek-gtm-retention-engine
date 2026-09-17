"""Throughput check: tile the 300-account portfolio into a synthetic N-account batch and time the engine.

This measures single-machine runtime on duplicated rows (same behaviour patterns, new IDs).
It is NOT evidence of behaviour on a real 30k portfolio, data variety, CRM latency or concurrency.

Usage:  python scripts/scale_test.py [copies]      (default 100 -> 30,000 accounts)
"""
import sys
import tempfile
import time
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fleek_engine.demo import DEFAULT_SOURCE  # noqa: E402
from fleek_engine.execution import generate_execution_plan  # noqa: E402
from fleek_engine.pipeline import load_data, run_analytics  # noqa: E402
from fleek_engine.runs import RunStore  # noqa: E402
from fleek_engine.validate import guardrail_checks  # noqa: E402


def main(copies: int = 100) -> None:
    base = load_data(DEFAULT_SOURCE, "Accounts")
    frames = []
    for i in range(copies):
        f = base.copy()
        f["account_id"] = f["account_id"] + f"-S{i:03d}"
        frames.append(f)
    big = pd.concat(frames, ignore_index=True)

    t0 = time.perf_counter()
    plan = generate_execution_plan(run_analytics(big))
    t1 = time.perf_counter()
    checks = guardrail_checks(plan)
    t2 = time.perf_counter()
    with tempfile.TemporaryDirectory() as tmp:
        res = RunStore(tmp).run(big, "2026-01-01T00:00Z", "scale test")
        t3 = time.perf_counter()
        res2 = RunStore(tmp).run(big, "2026-01-01T00:05Z", "scale test identical rerun")
        t4 = time.perf_counter()

    print(f"accounts: {len(plan):,}  unique ids: {plan['account_id'].nunique():,}")
    print(f"analytics + execution plan: {t1 - t0:.2f}s")
    print(f"19 guardrail checks: {t2 - t1:.2f}s  violations: {int(checks['violations'].sum())}")
    print(f"full RunStore.run (plan + change detection + CSV state): {t3 - t2:.2f}s  log rows: {res['summary']['log_rows_written']}")
    print(f"identical rerun: {t4 - t3:.2f}s  log rows: {res2['summary']['log_rows_written']}  new actions: {res2['summary']['new_actions_generated']}")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 100)
