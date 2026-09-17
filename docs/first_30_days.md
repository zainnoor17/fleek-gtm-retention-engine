# First 30 days

**Goal:** run the tool as a daily operating rhythm without increasing risk to the accounts that hold 87% of GMV. Each week has one exit criterion. If a week misses it, the next week's scope shrinks. The timeline does not stretch to cover it.

## Week 1: Trust the inputs, then the queue

| Action | Tool touchpoint | Owner |
|---|---|---|
| Resolve the open data questions with the data owner: February completeness, AM vs self-serve order attribution, ACC-005's duplicate status, web vs app tracking, the chat/video window, offer acceptance, AM cost | *Playbooks & Data Notes* panel; RUN002 evidence (5 updates changed only February; ACC-006 and 008 reclassified) | Portfolio Lead + Data |
| Resolve the **ACC-005 HOLD** (P0) | Account Detail: HOLD brief | Portfolio Lead |
| Walk each AM through their slice of the **P1 queue** (39 accounts, about £300k) and collect their overrides | Human Queue → Account Manager filter; briefs | AMs |
| Assign named owners to the 4 Self Serve accounts in the human queue (ACC-211, 214, 215, 216) | Human Queue: "Self Serve: owner needed" | Portfolio Lead |
| Set up the daily run (scheduled `run_pipeline.py` or the UI) | Change / Rerun; `state/` | Ops / me |

**Exit criterion:** February and attribution confirmed or corrected. If a correction changes inputs, rerun and review the change log. The P1 queue has been reviewed, and every override is recorded with a reason.

## Week 2: Protect revenue first

| Action | Tool touchpoint | Owner |
|---|---|---|
| Start **retention conversations** (27) and **verify / win-back checks** (12), using the draft previews as a starting point. AMs send from their own tools. | Account Detail: brief + draft; mark **In Progress** | AMs, CS/Growth |
| Clear the **8 Manual Review** items: the 6 Phase 1 reviews, plus ACC-078 and 111 once attribution is known | Migration → Manual Review; approve or reject buttons | AMs + Portfolio Lead |
| Make **Key sign-off decisions** on the 7 accounts (£309k). Declining is a valid outcome. | Migration → Key Sign-Off; approve or decline buttons | Portfolio Lead + AM |
| Run the **8 Service Model Reviews** (qualitative until AM cost data exists) | Human Queue → Portfolio Lead | Portfolio Lead |
| Book the Day 0 walkthroughs for the **4 Ready accounts**, but only if Week 1 confirmed February and attribution. If not, keep them booked and move the dates. | Migration → Ready | AMs |

**Exit criterion:** every P1 account is In Progress or has a logged reason for not starting. Every sign-off and review decision is recorded in the audit trail.

> **Why Phase 1 doesn't run before Week 3:** the Ready cohort is defined by momentum and broker share. Those are exactly the fields the RUN002 batch showed can move when February or order attribution is corrected. Starting Day 0 a week later costs little. Starting on a mis-classified account costs the relationship.

## Week 3: Start Phase 1 carefully

| Action | Tool touchpoint | Owner |
|---|---|---|
| Hold a Day 0 walkthrough with the **4 Ready accounts** (ACC-019, 027, 030, 031). **AM support stays in place.** | Migration → Ready; MIG_DAY0 draft | AMs |
| Add any reviewed or approved accounts from Week 2 to the Day 0 list | Migration tabs | AMs |
| Turn on the **automated queue** only after the suppression list is agreed and AMs have been notified (139 AM-owned accounts carry `notify_am_before_send`) | Action Queue → Execution status = Ready — Automated | CS/Growth + AMs |
| Pre-entry: encourage a second self-serve checkout on the 5 pre-entry accounts | Migration → Pre-Entry | AMs |

**Exit criterion:** Phase 1 accounts have a Day 0 date and a Day 45 review in the calendar. Automated sends (if switched on) go out only to `Ready — Automated` rows.

## Week 4: Close the loop

| Action | Tool touchpoint | Owner |
|---|---|---|
| Day 15–30 light check-ins on Phase 1 accounts: product views, app days, offers, self-serve orders | 90-day milestone table | AMs |
| Define the **outcome feed**: sent, replied, ordered, and the 90-day monitoring inputs that `migration_progress()` expects | `fleek_engine/pipeline.py::migration_progress` | Me + Data |
| Review the first month's change logs and the human overrides. Were the alerts useful? Were any false positives caused by the February or attribution issues? Tune playbook wording from AM feedback, but not the thresholds. | Change / Rerun → Action log; workflow audit | Portfolio Lead + me |
| Agree the day-90 outcome rule for "no progress". The code currently says At Risk (restore support); the playbook text says "No Change – Reassess". | docs/methodology.md §10 | Portfolio Lead |
| Plan the production path: a database state store, a CRM feed, send integration for automated rows only | docs/architecture.md | Me + Eng |
| Decide the **Phase 2 candidates**: Manual Review accounts that cleared, approved Key accounts, and pre-entry accounts that reached two self-serve orders | Migration tabs after rerun | Portfolio Lead + AMs |
| Review **AM coverage of low-value accounts** (Cost-to-Serve segment, the Service Model Review outcomes, and the 139 AM-owned accounts in automated nurture) | Human Queue → Portfolio Lead; Action Queue filters | Portfolio Lead |
| Fix the **weekly operating cadence**: daily run, a Monday P0/P1 review, a Thursday migration and sign-off review, and a monthly threshold and override review | Overview + Change / Rerun | Portfolio Lead |

**Exit criterion:** a short read-out covering what changed in the portfolio, which rules were overridden and why, which thresholds to revisit, and a decision on moving the state store and integrations to production.

## What I would not do in the first 30 days

- **Launch migration for Key accounts** without sign-off, or pitch migration to anyone as "less support".
- **Report results from the Range Expansion test.** There are 2 accounts, so it is a design, not a result.
- **Tune thresholds before outcome data exists.** Record overrides instead, and let those drive changes later.
- **Automate anything** in Segments 2, 3 or 8, or for accounts showing Recent Inactivity.
