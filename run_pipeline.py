"""CLI: run the daily pipeline against a portfolio file, optionally ingesting a new batch.

Examples
  python run_pipeline.py --state state --timestamp 2026-09-18T07:00Z
  python run_pipeline.py --state state --new-accounts-sheet new_accounts --timestamp 2026-09-19T07:00Z
"""
import argparse
from pathlib import Path

import pandas as pd

from fleek_engine.execution import EXEC_QUEUE_COLUMNS
from fleek_engine.pipeline import load_data
from fleek_engine.runs import RunStore, process_new_accounts
from fleek_engine.validate import guardrail_checks

DEFAULT_INPUT = "data/Fleek_Retention_Case_Study_Portfolio_Data.xlsx"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default=DEFAULT_INPUT)
    ap.add_argument("--sheet", default="Accounts")
    ap.add_argument("--new-accounts-sheet", default=None, help="sheet (in --input) holding a new batch to upsert")
    ap.add_argument("--state", default="state")
    ap.add_argument("--out", default="outputs")
    ap.add_argument("--timestamp", required=True)
    ap.add_argument("--label", default="")
    a = ap.parse_args()

    raw = load_data(a.input, a.sheet)
    info = None
    if a.new_accounts_sheet:
        raw, info = process_new_accounts(raw, load_data(a.input, a.new_accounts_sheet))
    res = RunStore(a.state).run(raw, a.timestamp, a.label)
    out = Path(a.out) / res["summary"]["run_id"]
    out.mkdir(parents=True, exist_ok=True)
    res["execution"][EXEC_QUEUE_COLUMNS + ["change_type", "change_flags", "generated_action"]].to_csv(out / "execution_queue.csv", index=False)
    res["log_rows"].to_csv(out / "changes.csv", index=False)
    checks = guardrail_checks(res["execution"])
    checks.to_csv(out / "guardrail_checks.csv", index=False)
    print(res["summary"])
    if info:
        print({k: (v if not isinstance(v, list) else len(v)) for k, v in info.items()})
    print("guardrail violations:", int(checks["violations"].sum()))


if __name__ == "__main__":
    main()
