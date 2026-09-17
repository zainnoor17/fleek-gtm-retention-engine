"""Run: python -m pytest -q"""
import pandas as pd
import pytest

from fleek_engine import config as C
from fleek_engine.pipeline import load_data, migration_progress, run_analytics
from fleek_engine.execution import generate_execution_plan
from fleek_engine.runs import RunStore, process_new_accounts
from fleek_engine.validate import guardrail_checks

SRC = "data/Fleek_Retention_Case_Study_Portfolio_Data.xlsx"


@pytest.fixture(scope="module")
def base():
    return load_data(SRC, "Accounts")


@pytest.fixture(scope="module")
def plan(base):
    return generate_execution_plan(run_analytics(base))


def test_locked_segment_counts(plan):
    got = plan["action_segment"].value_counts().to_dict()
    assert got == {C.SEGMENTS[1]: 22, C.SEGMENTS[2]: 25, C.SEGMENTS[3]: 8, C.SEGMENTS[4]: 2, C.SEGMENTS[5]: 21,
                   C.SEGMENTS[6]: 4, C.SEGMENTS[7]: 2, C.SEGMENTS[8]: 6, C.SEGMENTS[9]: 210}
    assert plan["behavioural_segment"].value_counts().to_dict() == {"AM-Owned / Self-Serving": 132, "Self-Serve": 90, "Broker-Reliant": 78}


def test_phase1_lumpy_refinement(plan):
    assert sorted(plan.loc[plan.phase1_rollout_status == "Ready", "account_id"]) == ["ACC-019", "ACC-027", "ACC-030", "ACC-031"]
    assert plan.set_index("account_id").loc["ACC-036", "execution_status"] == "Human Review Required"


def test_nba_distribution(plan):
    assert plan["primary_nba"].value_counts().to_dict() == {
        "Automated Nurture": 216, "Retention Conversation": 28, "Guided Self-Serve Migration": 22, "Verify Demand / Win-Back": 12,
        "Service Model Review": 8, "Reinforce Successful Behaviour": 6, "Establish / Re-establish": 4, "Discovery-to-Offer Enablement": 4}


def test_guardrails(plan):
    checks = guardrail_checks(plan)
    assert checks["violations"].sum() == 0, checks[checks.violations > 0]


def test_new_accounts_upsert(base):
    merged, info = process_new_accounts(base, load_data(SRC, "new_accounts"))
    assert len(info["updated_ids"]) == 5 and len(info["added_ids"]) == 45
    assert len(merged) == 345 and merged["account_id"].is_unique


def test_idempotent_rerun(base, tmp_path):
    store = RunStore(tmp_path)
    merged, _ = process_new_accounts(base, load_data(SRC, "new_accounts"))
    store.run(base, "t1")
    store.run(merged, "t2")
    log_n, reg_n = len(store.log), len(store.registry)
    r3 = store.run(merged, "t3")
    assert r3["summary"]["identical_to_previous_input"]
    assert r3["summary"]["log_rows_written"] == 0 and r3["summary"]["new_actions_generated"] == 0
    assert len(store.log) == log_n and len(store.registry) == reg_n
    assert len(store.snapshot) == 345 and store.snapshot["account_id"].is_unique


def test_unchanged_data_new_run_no_actions(base, tmp_path):
    """Same data on a later day (not flagged identical because state differs) still generates nothing."""
    store = RunStore(tmp_path)
    store.run(base, "t1")
    r = store.run(base.sample(frac=1, random_state=1), "t2")   # row order shuffled
    assert r["summary"]["new_actions_generated"] == 0 and r["summary"]["log_rows_written"] == 0


def test_migration_progress(plan):
    mon = pd.DataFrame([
        dict(account_id="ACC-019", days=90, pdp=40, app=8, offers=2, orders=4, self_serve_orders=3, gmv=4000),   # capability
        dict(account_id="ACC-027", days=45, pdp=16, app=2, offers=0, orders=10, self_serve_orders=3, gmv=2000),  # progressing
        dict(account_id="ACC-030", days=60, pdp=30, app=7, offers=1, orders=1, self_serve_orders=1, gmv=200),    # GMV breach
        dict(account_id="ACC-031", days=30, pdp=2, app=1, offers=0, orders=2, self_serve_orders=0, gmv=900),     # baseline
    ])
    s = migration_progress(plan, mon)
    got = dict(zip(plan["account_id"], s))
    assert got["ACC-019"] == "Self-Serve Capability Demonstrated"
    assert got["ACC-027"] == "Progressing"
    assert got["ACC-030"] == "At Risk"
    assert got["ACC-031"] == "Baseline"
    assert got["ACC-001"] == "Baseline" and got["ACC-100"] == "N/A"
