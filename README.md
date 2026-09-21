# Fleek GTM & Retention Engine

A rules-based operating tool for a 300-account B2B marketplace portfolio. Each morning it answers four questions:

1. **What needs attention?** One priority (P0–P4), one next best action and one execution status per account.
2. **Why?** Reason code, rationale, guardrail codes and an internal brief for every account that needs a person.
3. **What happens next?** Owner role, channel, first action, follow-up day, and a customer draft (or the reason the draft is withheld).
4. **What changed since yesterday?** Upserts a new batch, detects material changes, and logs only those. Rerunning the same input creates nothing new.

> **Nothing is ever sent.** Customer drafts are previews. The optional workflow buttons in the UI only update local CSV state and write an audit row.

---

## The problem

Fleek's account managers (AMs) source stock for many buyers. Leadership wants to move suitable buyers towards self-serve without losing revenue. The data shows why that is hard:

- **Revenue is concentrated.** The Gini coefficient is 0.81. ACC-001 alone is 20% of GMV, and the top 50 accounts are 82%.
- **Dependence sits in the valuable accounts.** The 78 broker-reliant accounts are 26% of the portfolio but hold **83% of GMV**.
- **Those accounts are mostly shrinking.** In the high-dependency, high-value quadrant, 33 of 57 accounts are declining or have lapsed.

So the first conversation with most valuable accounts is about **retention, not migration**. The tool keeps these two jobs apart. It automates the low-risk long tail and puts human attention where the money and the risk are.

**Baseline result:** human attention is focused on **75 accounts representing 86.7% of GMV**. The other 225 accounts (13.3% of GMV) run through automated, low-risk playbooks.

## Pipeline

```
Portfolio workbook (future: CRM extract)
  └─ process_new_accounts()      upsert a new batch by account_id
      └─ clean_data → score_dependency → build_segments → apply_guardrails
         → build_feature_context → assign_nba            (Stages 1–4B, rules only)
          └─ generate_execution_plan()                    (Stage 5: playbook, owner, channel, draft/brief, state)
              └─ RunStore.run()                           fingerprint → compare_runs → action registry → action log
                  └─ guardrail_checks()                   19 hard checks, must all be 0
                      └─ app.py (Streamlit)               overview, queues, detail, migration, change log
```

See [`docs/architecture.md`](docs/architecture.md) for the diagram.

## Key design decisions

| Decision | Why |
|---|---|
| **Transparent rules, no ML, no blended score** | Only 300 accounts over 6 months, with lumpy buying. Every output can be traced to a threshold in `fleek_engine/config.py`. |
| **GMV is kept out of dependency; momentum is kept out of value** | Dependency (how much a buyer relies on an AM), value (Key/Core/Tail) and momentum (H2 vs H1) are three separate axes. The action segment combines them explicitly, so a large account is never mistaken for a dependent one, and a shrinking account is never mistaken for a small one. |
| **Discovery behaviour is the migration signal** | All 78 broker-reliant accounts have 15 or fewer product views in six months. Phase 1 therefore targets independent browsing and app use; offers are only supporting evidence. |
| **Chat and video are never self-serve targets** | Broker-reliant accounts generate 57% of chat threads and 81% of video requests. Pushing either would increase human dependency, and a guardrail check blocks it in drafts and targets. |
| **Gated dependency score (50/30/20, broker ≤20% → 0)** | Without the gate, 79 of 93 "Medium" accounts had zero AM-placed orders. |
| **"What should happen" is kept separate from "can it happen now"** | `primary_nba` is kept apart from `execution_status`. For example, ACC-001 is still a migration candidate but needs Key sign-off, and ACC-005 is on HOLD because of its duplicate status. |
| **Priority sorts but never scores** | The queue sorts P0→P4, then Key→Core→Tail, then GMV. There is no extra ranking number. |
| **Retention before migration** | Segments 2, 3 and 8 (protect, win-back and reactivation) are never automated and never get a growth nudge. |
| **Migration never means withdrawing support** | Phase 1 is an AM-led walkthrough with support kept in place. A GMV guardrail at day 45 restores high-touch support if spend drops. |
| **Lumpy buyers go to Manual Review** | A lumpy buyer has fewer than 3 GMV months or fewer than 5 orders. For these accounts a 90-day GMV check can't tell a normal gap from a real drop. |
| **Material-change logging plus an idempotent action registry** | The action key is a hash of account + playbook + reason + status + template, so a rerun can never re-issue an action. |
| **Role labels only** | The data contains no named staff. Self Serve accounts that need a person are flagged `named_owner_required`. |

## How to run

Requires Python 3.10 or later.

```bash
cd fleek_gtm_engine
python -m venv .venv && source .venv/bin/activate      # optional
pip install -r requirements.txt

# UI
streamlit run app.py                                   # opens http://localhost:8501
# state is written to ./state (override with FLEEK_STATE_DIR=/path)

# Tests
python -m pytest -q

# Reproducible demo evidence (RUN001 -> RUN002 -> RUN003, fixed timestamps)
python demo_runs.py                                    # rewrites demo_state/ and demo_outputs/

# CLI daily run
python run_pipeline.py --state state --timestamp 2026-09-18T07:00Z
python run_pipeline.py --state state --new-accounts-sheet new_accounts --timestamp 2026-09-19T07:00Z
python run_pipeline.py --state state --new-accounts-sheet new_accounts --timestamp 2026-09-19T07:05Z   # identical rerun

# Throughput check (synthetic, see Limitations)
python scripts/scale_test.py
```

## Demo steps (UI)

1. **Portfolio Overview.** Shows the 75 / 86.7% statement, the P0–P4 counts, execution status, NBA and segment charts, the "19 / 19 execution guardrails passing" badge (expand it for the detail) and the data-quality panel.
2. **Human Queue.** Filter by role.
   - Retention example: **ACC-008**.
   - Migration example: **ACC-019** (Phase 1 Ready).
   - The 4 Self Serve accounts that need a named owner are ACC-211, 214, 215 and 216.
3. **Account Detail.**
   - **ACC-001** withholds its draft until Key sign-off. Clicking *Approve (sign-off)* changes local state only.
   - **ACC-005** is on HOLD and has no workflow buttons.
4. **Migration.** Shows the four groups:
   - **Ready:** ACC-019, 027, 030, 031
   - **Manual Review:** 6 accounts
   - **Key Sign-Off:** 7 accounts
   - **Pre-Entry:** 5 accounts

   Below the groups are the 90-day milestones.
5. **Change / Rerun.**
   - Click **2 · Ingest new_accounts**. Expect 5 accounts updated, 45 added, 345 in total, 0 duplicates, 46 log rows and 46 new actions. **ACC-211** changes from Retention Conversation (P1) to Reinforce (P2) with Human Review Required, because it is `FEB_SENSITIVE`.
   - Click **3 · Re-run identical batch**. Expect 0 log rows, 0 new actions and 0 duplicates.
   - **Reset demo** restores the baseline.

## Tests

`python -m pytest -q` runs 12 tests.

- **`tests/test_engine.py` (8 tests)** covers:
  - locked segment counts
  - the Phase 1 lumpy rule and the Ready cohort
  - the NBA distribution
  - guardrails
  - upsert
  - idempotency (identical input, and reordered rows)
  - migration-progress transitions
- **`tests/test_app.py` (4 tests)** uses Streamlit AppTest to check:
  - all 7 views render
  - the 75 / 86.7% statement and the 19/19 badge
  - the UI rerun flow (5 / 45 / 345, the ACC-211 warning, then 0 / 0 / 0 on the identical rerun)
  - ACC-001's draft is withheld and its sign-off works
  - ACC-005 has no workflow buttons
  - local workflow state survives an identical rerun

## Structure

```
app.py                  Streamlit UI (presentation + local-only workflow; no business rules)
fleek_engine/
  config.py             every threshold, segment label, NBA library and NBA text
  pipeline.py           dependency, segments, guardrails, feature context, NBA, migration progress
  playbooks.py          9 playbooks
  execution.py          execution plan: owner, channel, templates (22), briefs, state
  runs.py               upsert, fingerprint, change detection, RunStore (CSV state)
  validate.py           19 execution guardrail checks
  demo.py               DemoSession service layer used by the UI and demo_runs.py
run_pipeline.py         CLI
demo_runs.py            reproducible 3-run demo
scripts/scale_test.py   synthetic throughput check
tests/                  pytest suites
data/                   source workbook (unmodified)
demo_state/             committed engine state after RUN003 (snapshot, log, registry, history)
demo_outputs/           committed evidence: queues, guardrails, RUN002 changes, summary
reports/                Stage 1–5 analysis reports + Fleek_Dependency_Scoring.xlsx (QA workbook)
docs/                   architecture, methodology, human vs automation, demo script, first 30 days
```

`state/` and `outputs/` are created at runtime and are git-ignored.

## Limitations

- **Six months of data, one cross-section.** Feature findings show association, not causation. Many accounts have only one order, so their momentum and broker share rest on very few events.
- **Open data questions** (also shown in the UI):
  - Is February complete?
  - Order-channel attribution changed between extracts.
  - What does ACC-005's "Duplicate" status mean?
  - Does web usage appear in the app-days count?
  - There is no offer-acceptance data.
  - What time window do the chat and video counts cover?
  - There is no AM cost data, so Service Model Review can't show ROI.
- **No outcome data yet.** Replies, orders after contact, and the 90-day migration monitoring inputs are not wired in. States such as `In Progress` and `Completed` only change through the local demo buttons.
- **Local CSV state, single user.** There is no auth, no concurrency control and no CRM or email integration. The acting role in the UI is a label, not an identity.
- **The Range Expansion test has n = 2.** It is a design, not a result.
- **Thresholds come from this one portfolio** and should be revisited once there is outcome data.

### Scaling test (what was measured)

`scripts/scale_test.py` copies the 300 accounts 100 times, giving 30,000 rows with new IDs and the same behaviour patterns. It then times the engine on one machine. On the build machine (Python 3.11, pandas 3.0) the latest run gave:

| Step | Time | Result |
|---|---:|---|
| Analytics + execution plan | ~2.0 s | 30,000 rows, 30,000 unique IDs |
| 19 guardrail checks | ~0.3 s | 0 violations |
| Full `RunStore.run` (plan, change detection, CSV state) | ~13.6 s | 30,000 log rows (baseline) |
| Identical rerun | ~14.6 s | 0 log rows, 0 new actions |

This shows the rules are vectorised and still correct at that row count. It does **not** show performance on a real, varied 30k portfolio, with CRM or email latency, or with concurrent users. Most of the full-run time is CSV state handling and row hashing.

## Production data integration

The case-study implementation reads from the supplied Excel workbook because that is the source dataset provided.

The rules engine itself is source-agnostic. In production, the ingestion layer could be replaced by a CRM export, warehouse query, database table, or API feed without changing the segmentation, next-best-action, or execution logic.

The current implementation has been benchmarked on 30,000 synthetic accounts. At larger production scale, I would move persistent state from CSV files into a database and connect the engine directly to Fleek's warehouse or CRM.
