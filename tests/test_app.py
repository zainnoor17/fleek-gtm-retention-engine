"""UI smoke + workflow tests (Streamlit AppTest). Run: python -m pytest -q"""
from pathlib import Path

import pytest

from fleek_engine.demo import DemoSession

APP = str(Path(__file__).resolve().parent.parent / "app.py")
VIEWS = ["Portfolio Overview", "Action Queue", "Account Detail", "Human Queue", "Migration", "Change / Rerun", "Playbooks & Data Notes"]


@pytest.fixture()
def app(tmp_path, monkeypatch):
    st_testing = pytest.importorskip("streamlit.testing.v1")
    monkeypatch.setenv("FLEEK_STATE_DIR", str(tmp_path / "state"))
    at = st_testing.AppTest.from_file(APP, default_timeout=120)
    at.run()
    return at


def _goto(at, view):
    at.sidebar.radio(key="nav").set_value(view).run()
    assert not at.exception, at.exception


def test_all_views_render(app):
    assert not app.exception
    assert any("Human attention is focused on **75 accounts** representing **86.7%**" in m.value for m in app.markdown)
    assert any("19 / 19 execution guardrails passing" in s.value for s in app.success)
    for v in VIEWS:
        _goto(app, v)


def test_rerun_flow_in_ui(app):
    _goto(app, "Change / Rerun")
    app.button(key="btn_ingest").click().run()
    assert not app.exception
    metrics = {m.label: m.value for m in app.metric}
    assert metrics["Existing accounts updated"] == "5" and metrics["New accounts added"] == "45" and metrics["Portfolio size"] == "345"
    assert any("ACC-211" in w.value and "FEB_SENSITIVE" in w.value for w in app.warning)
    app.button(key="btn_identical").click().run()
    metrics = {m.label: m.value for m in app.metric}
    assert metrics["Log rows written"] == "0" and metrics["New actions created"] == "0" and metrics["Duplicate account IDs"] == "0"
    assert metrics["Existing accounts updated"] == "0" and metrics["New accounts added"] == "0" and metrics["Portfolio size"] == "345"
    assert any("Idempotent rerun" in s.value for s in app.success)


def test_account_detail_withholds_and_workflow(app):
    _goto(app, "Account Detail")
    app.selectbox(key="acc_select").set_value("ACC-001").run()           # Key sign-off: draft withheld
    assert any("Withheld until sign-off" in w.value for w in app.warning)
    labels = [b.label for b in app.button]
    assert "Approve (sign-off)" in labels
    app.button(key="wf_ACC-001_Approve (sign-off)").click().run()
    assert not app.exception
    app.selectbox(key="acc_select").set_value("ACC-005").run()           # HOLD: no workflow buttons, no draft
    assert any("On HOLD" in e.value for e in app.error)
    assert not any(b.key and b.key.startswith("wf_ACC-005") for b in app.button)


def test_local_workflow_state_survives_identical_rerun(tmp_path):
    s = DemoSession(tmp_path / "state")
    s.ensure_baseline()
    s.run_new_accounts(label="run2")
    assert s.update_action_state("ACC-019", "Mark In Progress", "Account Manager") == "In Progress"
    assert s.update_action_state("ACC-001", "Decline", "Portfolio Lead + Account Manager") == "No Action Required"
    with pytest.raises(ValueError):
        s.update_action_state("ACC-005", "Mark In Progress", "Portfolio Lead")          # HOLD: no transitions
    reg = len(s.registry())
    s.run_new_accounts(label="identical")
    p = s.plan().set_index("account_id")
    assert p.loc["ACC-019", "action_state"] == "In Progress"
    assert p.loc["ACC-001", "action_state"] == "No Action Required"
    assert len(s.registry()) == reg and len(s.audit()) == 2
