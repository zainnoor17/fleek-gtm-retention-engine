"""Fleek GTM & Retention Operating System - Streamlit UI.

Presentation + local workflow layer only. Every classification, NBA, status and draft comes
from the fleek_engine pipeline (via fleek_engine.demo.DemoSession). Nothing is ever sent.

Run:  streamlit run app.py
"""
from __future__ import annotations

import os

import altair as alt
import pandas as pd
import streamlit as st

from fleek_engine.demo import DemoSession
from fleek_engine.playbooks import playbook_library

STATE_DIR = os.environ.get("FLEEK_STATE_DIR", "state")
SERIES = "#2a78d6"          # single-series bar colour (validated reference palette, slot 1)
PRI = ["P0", "P1", "P2", "P3", "P4"]
TIER = {"Key": 0, "Core": 1, "Tail": 2}
AUTO = "Ready — Automated"
VIEWS = ["Portfolio Overview", "Action Queue", "Account Detail", "Human Queue", "Migration", "Change / Rerun", "Playbooks & Data Notes"]
ROLES = ["Account Manager", "Customer Success / Growth", "Portfolio Lead", "Portfolio Lead + Account Manager"]
DATA_ISSUES = [
    ("February completeness unconfirmed", "All 5 accounts updated in new_accounts changed only in February. Momentum and 36 February-sensitive flags depend on it."),
    ("Order-channel attribution changed between extracts", "ACC-006 and ACC-008 moved orders from AM-placed to self-serve between files. Broker reliance and Phase 1 entry depend on this."),
    ("ACC-005 'Duplicate' status unresolved", "5th-largest account (£24.6k) is on HOLD; GMV may be double-counted."),
    ("Web tracking coverage unknown", "Some accounts have self-serve orders with 0 app days / 0 product views."),
    ("Offer acceptance unavailable", "Cannot tell why heavy offer-makers (e.g. ACC-086, ACC-211) do or don't convert."),
    ("Chat / video time window unclear", "No _6m suffix; chat correlates with tenure. Treated as context only, never as a target."),
    ("AM cost unavailable", "Service Model Review cannot quantify ROI."),
]

st.set_page_config(page_title="Fleek GTM & Retention OS", layout="wide")


# ----------------------------------------------------------------------------- data
def get_session() -> DemoSession:
    s = DemoSession(STATE_DIR)
    s.ensure_baseline()
    return s


def queue_sort(df: pd.DataFrame) -> pd.DataFrame:
    return (df.assign(_p=df["attention_priority"].map(PRI.index), _t=df["value_tier"].map(TIER))
              .sort_values(["_p", "_t", "gmv_total_6m"], ascending=[True, True, False]).drop(columns=["_p", "_t"]))


def money(x: float) -> str:
    return f"£{x:,.0f}"


def codes(s: str) -> list[str]:
    return [c.strip() for c in str(s).split(";") if c.strip()]


def bar(df: pd.DataFrame, cat: str, title: str):
    """Single-series horizontal bar: count with GMV in the tooltip."""
    g = df.groupby(cat).agg(accounts=("account_id", "size"), gmv=("gmv_total_6m", "sum")).reset_index()
    g["gmv_fmt"] = g["gmv"].map(money)
    base = alt.Chart(g, title=title).encode(
        y=alt.Y(f"{cat}:N", sort="-x", title=None, axis=alt.Axis(labelLimit=260)),
        x=alt.X("accounts:Q", title="Accounts", axis=alt.Axis(grid=True, gridOpacity=0.25, tickMinStep=1)),
        tooltip=[alt.Tooltip(f"{cat}:N", title="Group"), alt.Tooltip("accounts:Q", title="Accounts"), alt.Tooltip("gmv_fmt:N", title="6m GMV")])
    bars = base.mark_bar(color=SERIES, size=18, cornerRadiusEnd=4)
    labels = base.mark_text(align="left", dx=4, color="gray").encode(text="accounts:Q")
    return (bars + labels).properties(height=alt.Step(30))


def nav_to_account(acc: str):
    st.session_state["acc_select"] = acc
    st.session_state["nav"] = "Account Detail"


session = get_session()
run_ids = session.run_ids()
run_id = run_ids[-1]
plan = queue_sort(session.plan())
meta = session.meta(run_id)
guard = session.guardrails()
human = plan[plan["execution_status"] != AUTO]
autoq = plan[plan["execution_status"] == AUTO]
total_gmv = plan["gmv_total_6m"].sum()

# ----------------------------------------------------------------------------- sidebar
with st.sidebar:
    st.markdown("### Fleek GTM & Retention OS")
    st.caption(f"Current run **{run_id}** · {meta['accounts']} accounts · {meta['run_timestamp']}")
    st.caption(meta.get("label", ""))
    view = st.radio("View", VIEWS, key="nav")
    acting = st.selectbox("Acting as (role label, local demo only)", ROLES, key="acting_role")
    st.info("Demo mode: nothing is sent. Drafts are previews; buttons only update local state.")

# ============================================================================= 1. Overview
if view == "Portfolio Overview":
    st.title("Portfolio Overview")
    h_share = human["gmv_total_6m"].sum() / total_gmv
    st.markdown(f"#### Human attention is focused on **{len(human)} accounts** representing **{h_share:.1%}** of GMV.")
    st.caption(f"The other {len(autoq)} accounts ({autoq['gmv_total_6m'].sum() / total_gmv:.1%} of GMV) run through automated, low-risk playbooks.")
    c = st.columns(4)
    c[0].metric("Accounts", f"{len(plan)}")
    c[1].metric("Portfolio GMV (6m)", money(total_gmv))
    c[2].metric(f"Human queue · {money(human['gmv_total_6m'].sum())}", f"{len(human)}")
    c[3].metric(f"Automated queue · {money(autoq['gmv_total_6m'].sum())}", f"{len(autoq)}")
    st.markdown("**Attention priority**")
    c = st.columns(5)
    labels = {"P0": "Critical hold", "P1": "Revenue protection", "P2": "Active intervention", "P3": "Growth / efficiency", "P4": "Automated / monitor"}
    for i, p in enumerate(PRI):
        sub = plan[plan["attention_priority"] == p]
        c[i].metric(f"{p} · {labels[p]}", len(sub))
        c[i].caption(f"{money(sub['gmv_total_6m'].sum())} GMV")
    st.markdown("**Execution status**")
    c = st.columns(4)
    c[0].metric("Critical blockers (HOLD)", int(plan["execution_status"].str.startswith("HOLD").sum()))
    c[1].metric("Awaiting human review", int((plan["execution_status"] == "Human Review Required").sum()))
    c[2].metric("Awaiting sign-off", int((plan["execution_status"] == "Human Sign-Off Required").sum()))
    c[3].metric("Ready for automated execution", len(autoq))
    left, right = st.columns(2)
    left.altair_chart(bar(plan, "primary_nba", "Accounts by primary NBA"), width="stretch")
    right.altair_chart(bar(plan, "behavioural_segment", "Accounts by behavioural segment"), width="stretch")

    n_pass = int((guard["violations"] == 0).sum())
    ok = n_pass == len(guard)
    (st.success if ok else st.error)(f"{n_pass} / {len(guard)} execution guardrails passing on {run_id}")
    with st.expander("Guardrail and validation detail"):
        st.dataframe(guard, hide_index=True, width="stretch")
        checks = pd.DataFrame([
            ("Accounts classified exactly once", plan["account_id"].is_unique and len(plan) == meta["accounts"]),
            ("One primary NBA / execution status / priority per account",
             bool(plan[["primary_nba", "execution_status", "attention_priority"]].ne("").all().all())),
            ("No prohibited automated actions (Segments 2/3/8, Broker-Reliant growth, Recent Inactivity growth)",
             int(guard.set_index("check").loc[["Segments 2/3/8 with automated action or growth nudge", "Broker-Reliant with automated growth nudge",
                                               "Recent Inactivity with automated growth action"], "violations"].sum()) == 0),
            ("No message on HOLD", int(guard.set_index("check").loc["HOLD accounts with any outbound draft", "violations"]) == 0),
            ("No migration message before sign-off", int(guard.set_index("check").loc["Sign-off accounts with a migration draft before sign-off", "violations"]) == 0),
            ("No duplicate actions in registry", bool(session.registry()["action_key"].is_unique)),
        ], columns=["check", "pass"])
        st.dataframe(checks, hide_index=True, width="stretch")
        st.caption("Full pytest suite: `python -m pytest` (see README).")

    st.subheader("Open data questions")
    st.caption("Surfaced deliberately - the recommendations carry these uncertainties.")
    st.table(pd.DataFrame(DATA_ISSUES, columns=["Issue", "Why it matters"]))

# ============================================================================= 2. Action queue
elif view == "Action Queue":
    st.title("Action Queue")
    st.caption("One row per account. Sorted P0 → P4, then Key → Core → Tail, then GMV. No additional ranking score.")
    filt = {
        "attention_priority": "Priority", "primary_nba": "Primary NBA", "execution_status": "Execution status",
        "owner_role": "Owner role", "value_tier": "Value tier", "behavioural_segment": "Behavioural segment",
        "action_segment": "Action segment", "action_state": "Action state",
    }
    q = plan.copy()
    cols = st.columns(4)
    for i, (col, lab) in enumerate(filt.items()):
        opts = sorted(q[col].unique(), key=lambda v: PRI.index(v) if v in PRI else str(v))
        sel = cols[i % 4].multiselect(lab, opts, key=f"f_{col}")
        if sel:
            q = q[q[col].isin(sel)]
    st.caption(f"{len(q)} accounts · {money(q['gmv_total_6m'].sum())}")
    show = ["account_id", "attention_priority", "gmv_total_6m", "value_tier", "behavioural_segment", "action_segment", "primary_nba",
            "execution_status", "owner_role", "action_state", "recent_activity_status", "guardrail_codes"]
    st.dataframe(q[show], hide_index=True, width="stretch", height=520,
                 column_config={"gmv_total_6m": st.column_config.NumberColumn("GMV 6m (£)", format="localized"),
                                "attention_priority": "Priority", "guardrail_codes": st.column_config.TextColumn("Warnings / guardrails", width="large")})
    if len(q):
        pick = st.selectbox("Open an account", q["account_id"], key="queue_pick")
        st.button("Open account detail", on_click=nav_to_account, args=(pick,), key="open_detail")

# ============================================================================= 3. Account detail
elif view == "Account Detail":
    st.title("Account Detail")
    ids = list(plan["account_id"])
    if st.session_state.get("acc_select") not in ids:
        st.session_state["acc_select"] = ids[0]
    acc = st.selectbox("Account", ids, key="acc_select")
    r = plan.set_index("account_id").loc[acc]

    st.markdown(f"### {acc} · {r.attention_priority} · {r.primary_nba}")
    st.caption(f"{r.action_segment} · {r.behavioural_segment} · execution: **{r.execution_status}** · owner: **{r.owner_role}** · state: **{r.action_state}**")

    st.subheader("Account snapshot")
    c = st.columns(5)
    c[0].metric("GMV (6m)", money(r.gmv_total_6m))
    c[1].metric("Value tier", r.value_tier)
    c[2].metric("Orders (6m)", int(r.orders_6m))
    c[3].metric("Momentum", r.momentum)
    c[4].metric(f"Dependency · {r.dependency_tier}", f"{float(r.dependency_score):.1f}")
    st.caption(f"Recent activity: **{r.recent_activity_status}** · Ownership: {r.ownership} · {r.buyer_persona}, {r.country} · tenure {int(r.tenure_months)} months · "
               f"Sep–Nov {money(r.h1_gmv)} → Dec–Feb {money(r.h2_gmv)} · lifecycle: {r.lifecycle_context}")

    st.subheader("Behaviour")
    c = st.columns(6)
    c[0].metric("Broker reliance", f"{int(r.broker_reliance_pct)}%")
    c[1].metric("AM / self-serve orders", f"{int(r.manual_orders)} / {int(r.self_serve_orders)}")
    c[2].metric("App active days", int(r.app_active_days_6m))
    c[3].metric("Product page views", int(r.pdp_views_6m))
    c[4].metric("Offers made", int(r.make_an_offer_6m))
    c[5].metric("Product mix", r.basket_type)
    st.caption(f"Context only (not targets): {int(r.chat_threads)} chats with Fleek · {int(r.video_call_requests)} video requests · "
               f"{int(r.handpick_orders)} handpick / {int(r.bundle_orders)} bundle orders · archetype: {r.archetype}")

    st.subheader("Recommendation")
    c = st.columns([2, 1])
    with c[0]:
        st.markdown(f"**{r.primary_nba}** — reason `{r.nba_reason_code}`")
        st.write(r.nba_rationale)
        st.markdown(f"**Target behaviour:** {r.target_behaviour}")
        st.markdown(f"**Success measure:** {r.success_measure}")
        st.markdown(f"**First action:** {r.first_action} · follow-up in {int(r.follow_up_days)} days · channel: {r.recommended_channel}")
    with c[1]:
        st.markdown(f"**Execution status:** {r.execution_status}")
        st.markdown(f"**Owner role:** {r.owner_role}")
        st.markdown(f"**Attention priority:** {r.attention_priority}")
        st.markdown(f"**Playbook:** {r.playbook_id}")
        if str(r.named_owner_required) == "True":
            st.warning("Self Serve account: a named human owner must be assigned (none exists in the data).")
        if str(r.notify_am_before_send) == "True":
            st.info("AM-owned account: notify the AM before any automated send.")

    st.subheader("Guardrails")
    g = codes(r.guardrail_codes)
    if g:
        st.markdown(" ".join(f"`{x}`" for x in g))
    else:
        st.caption("No guardrail warnings for this account.")

    st.subheader("Execution")
    if r.internal_task_brief:
        st.markdown("**Internal task brief**")
        st.code(r.internal_task_brief, language=None, wrap_lines=True)
    if r.draft_customer_message:
        st.markdown("**Draft customer message (preview only - not sent)**")
        st.code(r.draft_customer_message, language=None, wrap_lines=True)
    else:
        st.warning(f"Customer message: {r.draft_status}")
    if r.secondary_test:
        st.markdown(f"**Secondary experiment:** {r.secondary_test} · arm: {r.secondary_test_arm}")
        if r.secondary_test_draft:
            st.code(r.secondary_test_draft, language=None, wrap_lines=True)
    if r.primary_nba == "Automated Nurture":
        st.caption(f"Nurture sub-context: {r.nurture_subcontext}")

    st.subheader("Local workflow")
    actions = session.allowed_actions(r.action_state, r.execution_status)
    if r.execution_status.startswith("HOLD"):
        st.error("On HOLD: resolve the data issue in the source, then rerun. No actions available.")
    elif not actions:
        st.caption("No manual workflow step for this state (automated accounts are handled by the automation queue).")
    else:
        bcols = st.columns(len(actions))
        for i, label in enumerate(actions):
            if bcols[i].button(label, key=f"wf_{acc}_{label}"):
                new = session.update_action_state(acc, label, acting)
                st.success(f"{acc}: action state → {new} (local only; nothing sent).")
                st.rerun()
    aud = session.audit()
    aud = aud[aud["account_id"] == acc]
    if len(aud):
        st.dataframe(aud, hide_index=True, width="stretch")

# ============================================================================= 4. Human queue
elif view == "Human Queue":
    st.title("Human Queue")
    st.caption("Accounts that need a person. Role labels only - no named staff exist in the data.")
    c = st.columns(5)
    c[0].metric("P0", int((human["attention_priority"] == "P0").sum()))
    c[1].metric("P1", int((human["attention_priority"] == "P1").sum()))
    c[2].metric("Awaiting human review", int((human["execution_status"] == "Human Review Required").sum()))
    c[3].metric("Awaiting sign-off", int((human["execution_status"] == "Human Sign-Off Required").sum()))
    c[4].metric("Self Serve: owner needed", int((human["named_owner_required"].astype(str) == "True").sum()))
    role = st.radio("Owner role", ["All"] + ROLES, horizontal=True, key="hq_role")
    hq = human if role == "All" else human[human["owner_role"] == role]
    st.caption(f"{len(hq)} accounts · {money(hq['gmv_total_6m'].sum())}")
    st.dataframe(hq[["attention_priority", "account_id", "owner_role", "gmv_total_6m", "primary_nba", "execution_status", "action_state", "guardrail_codes"]],
                 hide_index=True, width="stretch", column_config={"gmv_total_6m": st.column_config.NumberColumn("GMV (£)", format="localized")})
    for _, r in hq.iterrows():
        flag = " · NAMED OWNER NEEDED" if str(r.named_owner_required) == "True" else ""
        with st.expander(f"{r.attention_priority} · {r.account_id} · {money(r.gmv_total_6m)} · {r.primary_nba} · {r.execution_status}{flag}"):
            st.markdown(f"**Why now:** {r.nba_rationale_short}")
            st.markdown(f"**Owner:** {r.owner_role} · **State:** {r.action_state} · **First action:** {r.first_action}")
            if codes(r.guardrail_codes):
                st.markdown("**Blockers / warnings:** " + " ".join(f"`{x}`" for x in codes(r.guardrail_codes)))
            st.code(r.internal_task_brief, language=None, wrap_lines=True)
            if r.draft_customer_message:
                st.markdown("Draft (preview only):")
                st.code(r.draft_customer_message, language=None, wrap_lines=True)
            else:
                st.warning(f"Customer message: {r.draft_status}")
            st.button("Open account detail", key=f"hq_open_{r.account_id}", on_click=nav_to_account, args=(r.account_id,))

# ============================================================================= 5. Migration
elif view == "Migration":
    st.title("Guided Self-Serve Migration")
    st.info("Migration means teaching the customer to discover and buy stock independently **while AM support stays in place**. "
            "It never means withdrawing support.")
    mc = plan[plan["action_segment"].str.startswith("1.")].copy()
    mc["self_serve_share"] = mc["self_serve_orders"] / mc["orders_6m"]
    groups = [("Phase 1 Ready", "MIGRATION_PHASE1_READY"), ("Manual Review", "MIGRATION_PHASE1_REVIEW"),
              ("Key Sign-Off", "MIGRATION_KEY_SIGNOFF"), ("Pre-Entry", "MIGRATION_PRE_ENTRY")]
    c = st.columns(4)
    for i, (lab, code) in enumerate(groups):
        sub = mc[mc["nba_reason_code"] == code]
        c[i].metric(f"{lab} · {money(sub['gmv_total_6m'].sum())}", len(sub))
    cols = ["account_id", "gmv_total_6m", "dependency_score", "dependency_tier", "self_serve_share", "pdp_views_6m", "app_active_days_6m",
            "make_an_offer_6m", "buyer_cadence", "phase1_rollout_status", "execution_status", "migration_progress_status", "guardrail_codes"]
    cfg = {"gmv_total_6m": st.column_config.NumberColumn("GMV (£)", format="localized"),
           "self_serve_share": st.column_config.NumberColumn("Self-serve share", format="%.0f%%"),
           "pdp_views_6m": "PDP baseline (6m)", "app_active_days_6m": "App days baseline (6m)", "make_an_offer_6m": "Offers (6m)"}
    tabs = st.tabs([g[0] for g in groups])
    notes = {"MIGRATION_PHASE1_READY": "Regular buyers with healthy spend and 2+ self-serve orders, no guardrail warnings. AM-led Day 0 walkthrough.",
             "MIGRATION_PHASE1_REVIEW": "Meet entry criteria but a guardrail (borderline / February-sensitive momentum, lumpy cadence, broker % inconsistency) must be resolved first. Drafts withheld.",
             "MIGRATION_KEY_SIGNOFF": "Key accounts: no migration communication before Portfolio Lead + AM sign-off. ACC-001/003 are borderline and February-sensitive.",
             "MIGRATION_PRE_ENTRY": "Only one self-serve order so far: AM encourages a second self-serve checkout before Phase 1."}
    for t, (lab, code) in zip(tabs, groups):
        with t:
            st.caption(notes[code])
            sub = mc[mc["nba_reason_code"] == code].copy()
            sub["self_serve_share"] = sub["self_serve_share"] * 100
            st.dataframe(sub[cols], hide_index=True, width="stretch", column_config=cfg)
    st.subheader("90-day Phase 1 milestones")
    st.table(pd.DataFrame([
        ("M1 Independent discovery", "Product page views", "≥15 = Progressing · ≥25 = Capability", "Strongest signal: no broker-reliant account exceeds 15 views in six months"),
        ("M2 Habitual app use", "App active days", "≥5 = Progressing · ≥6 = Capability", "Supportive (partly inside the dependency score)"),
        ("M3 Self-directed negotiation", "Offers", "≥2 supportive only", "Not required for success"),
        ("M4 Self-serve purchasing", "Self-serve share of orders", "≥1 self-serve order and share above baseline", "Needs order-level history going forward"),
        ("GMV preservation", "90-day GMV", "Regular buyers: At Risk below 70% of pro-rated expectation from day 45 · Lumpy buyers: human review", "At Risk → restore high-touch support"),
    ], columns=["Milestone", "Measure", "90-day reference", "Notes"]))
    st.caption("Timeline: Day 0 walkthrough · Day 15–30 light check-in · Day 45 formal review · Day 90 outcome "
               "(Capability Demonstrated / Progressing – extend / At Risk – restore support / No change – reassess). "
               "All accounts start at Baseline until 90-day monitoring data is entered.")

# ============================================================================= 6. Change / rerun
elif view == "Change / Rerun":
    st.title("Change Detection & Reruns")
    st.caption("Step 1 runs automatically on first load. Buttons run the real engine against the source workbook; nothing is sent.")
    b = st.columns(4)
    b[0].button("1 · Baseline (300 accounts)", disabled=True, key="btn_base", help="Runs automatically on first load")
    if b[1].button("2 · Ingest new_accounts", key="btn_ingest", disabled=len(run_ids) >= 2, type="primary"):
        session.run_new_accounts(label="Second run: new_accounts upsert")
        st.rerun()
    if b[2].button("3 · Re-run identical batch", key="btn_identical", disabled=len(run_ids) < 2):
        session.run_new_accounts(label="Identical input re-run")
        st.rerun()
    if b[3].button("Reset demo", key="btn_reset"):
        session.reset()
        session.ensure_baseline()
        st.rerun()

    hist = session.history()
    st.subheader("Run history")
    st.dataframe(hist[["run_id", "run_timestamp", "label", "accounts", "log_rows_written", "new_actions_generated", "identical_to_previous_input", "change_type_counts"]],
                 hide_index=True, width="stretch")

    if len(run_ids) == 1:
        st.info("Only the baseline exists. Click **2 · Ingest new_accounts** to process the new batch.")
    else:
        prev_id = run_ids[-2]
        prev = session.plan(prev_id).set_index("account_id")
        cur = plan.set_index("account_id")
        st.subheader(f"What changed in {run_id} (vs {prev_id})")
        ing = meta.get("ingestion", {})
        identical = str(meta["identical_to_previous_input"]) == "True"
        new_ids = cur.index.difference(prev.index)
        c = st.columns(6)
        # Counts are relative to the previous run: an identical re-run applies nothing new.
        c[0].metric("Existing accounts updated", 0 if identical else len(ing.get("updated_ids", [])))
        c[1].metric("New accounts added", len(new_ids))
        c[2].metric("Portfolio size", meta["accounts"])
        c[3].metric("Duplicate account IDs", int(cur.index.duplicated().sum()))
        c[4].metric("Log rows written", meta["log_rows_written"])
        c[5].metric("New actions created", meta["new_actions_generated"])

        if identical:
            st.success(f"Idempotent rerun: identical input to {prev_id}. 0 new log rows, 0 new actions, "
                       f"{(cur['change_type'] == 'NO_MATERIAL_CHANGE').sum()} / {len(cur)} accounts unchanged, "
                       f"{int(cur.index.duplicated().sum())} duplicate accounts. Registry: {len(session.registry())} rows, all unique keys.")
        if ing.get("updated_ids"):
            prefix = (f"Same batch as {prev_id} ({len(ing['updated_ids'])} existing IDs, {len(ing.get('added_ids', []))} new IDs) - already applied, so nothing changes. "
                      if identical else "Updated IDs: ")
            st.caption(prefix + ("" if identical else ", ".join(ing["updated_ids"])))
        common = cur.index.intersection(prev.index)
        diff = pd.DataFrame({
            "prev_nba": prev.loc[common, "primary_nba"], "nba": cur.loc[common, "primary_nba"],
            "prev_priority": prev.loc[common, "attention_priority"], "priority": cur.loc[common, "attention_priority"],
            "prev_status": prev.loc[common, "execution_status"], "status": cur.loc[common, "execution_status"],
            "change_flags": cur.loc[common, "change_flags"], "guardrail_codes": cur.loc[common, "guardrail_codes"],
        })
        c = st.columns(4)
        c[0].metric("NBA changes (existing)", int((diff.nba != diff.prev_nba).sum()))
        c[1].metric("Priority changes (existing)", int((diff.priority != diff.prev_priority).sum()))
        c[2].metric("Execution-status changes", int((diff.status != diff.prev_status).sum()))
        entered = list(new_ids[cur.loc[new_ids, "execution_status"] != AUTO]) + list(diff.index[(diff.prev_status == AUTO) & (diff.status != AUTO)])
        c[3].metric("Newly entered human queue", len(entered))

        changed = diff[(diff.nba != diff.prev_nba) | (diff.priority != diff.prev_priority) | (diff.status != diff.prev_status)]
        if len(changed):
            st.markdown("**Existing accounts with a material change**")
            st.dataframe(changed.reset_index(), hide_index=True, width="stretch")
            if "ACC-211" in changed.index:
                r = diff.loc["ACC-211"]
                st.warning(f"**ACC-211** changed from *{r.prev_nba}* ({r.prev_priority}) to *{r.nba}* ({r.priority}); execution status is now "
                           f"**{r.status}**. The new batch added February GMV, which lifts momentum to Stable - but the account is "
                           f"`FEB_SENSITIVE` (without February it would still read Declining), so the automated message is held for a human check.")
        quiet = diff[diff.change_flags.str.contains("DATA_UPDATED") & ~diff.index.isin(changed.index)]
        if len(quiet):
            st.markdown("**Updated data, no material change (internal flags only - no alert, no new action)**")
            st.dataframe(quiet[["nba", "priority", "status", "change_flags", "guardrail_codes"]].reset_index(), hide_index=True, width="stretch")
        if len(new_ids):
            st.markdown("**New accounts**")
            nw = cur.loc[new_ids].reset_index()
            st.dataframe(queue_sort(nw)[["account_id", "attention_priority", "value_tier", "gmv_total_6m", "primary_nba", "execution_status", "owner_role"]],
                         hide_index=True, width="stretch", column_config={"gmv_total_6m": st.column_config.NumberColumn("GMV (£)", format="localized")})
        st.markdown(f"**Newly entered human queue ({len(entered)}):** " + (", ".join(sorted(entered)) if entered else "none"))

    with st.expander("Action log (material changes only)"):
        st.dataframe(session.log().iloc[::-1], hide_index=True, width="stretch")
    with st.expander("Local workflow audit trail"):
        st.dataframe(session.audit(), hide_index=True, width="stretch")

# ============================================================================= 7. Playbooks & notes
else:
    st.title("Playbooks & Data Notes")
    st.subheader("Playbook library")
    st.dataframe(playbook_library(), hide_index=True, width="stretch")
    st.subheader("Open data questions")
    st.table(pd.DataFrame(DATA_ISSUES, columns=["Issue", "Why it matters"]))
    st.subheader("What the engine will never do")
    st.markdown("- Send anything (drafts are previews)\n- Message accounts on HOLD, awaiting review, or before Key sign-off\n"
                "- Automate retention, win-back or reactivation work (Segments 2, 3, 8)\n- Encourage chat or video as a self-serve behaviour\n"
                "- Claim that the Range Expansion test lifts GMV\n- Re-send because the pipeline re-ran")
