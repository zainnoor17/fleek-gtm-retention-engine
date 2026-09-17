# Fleek_Execution_Playbook_Report

**Stage 5 answers one question: if the tool ran every morning, what would happen next?**

- **Scope:** Stages 1–4B are unchanged apart from the one approved Phase 1 refinement.
- **Where the logic lives:** in reusable Python code (`fleek_gtm_engine/`). The Excel workbook is now a QA and analyst view of that code's output.
- **Verification:** the code reproduces every workbook formula output for all 300 accounts, field by field.
- **Nothing is sent.** Every customer draft is marked "not sent", and no action is recorded as completed.

---

## 0. Phase 1 Refinement (Applied First)

**Rule:** an account that would otherwise be Phase 1 Ready but has `buyer_cadence = Lumpy` now goes to **Manual Review**, which means **Human Review Required**.
- **Lumpy** means fewer than 3 months with GMV, or fewer than 5 orders.
- This is a general rule, not an exception written for one account.

**Validated result:**

| | Before | After |
|---|---|---|
| **Ready** | ACC-019, 027, 030, **036**, 031 | **ACC-019, 027, 030, 031** (£21.2k) |
| **Manual Review** | ACC-020, 024, 033, 056, 058 | ACC-020, 024, 033, **036**, 056, 058 (£24.1k) |

- **ACC-036** moved because it has 37 orders but GMV in only two months.
- **New guardrail code:** `LUMPY_CADENCE`, shown on every Migration Candidate with lumpy buying (ACC-020, 034, 036, 039, 057, 058).
- **Nothing else changed:** every other Stage 4B output is identical to before.

---

## A. Execution Architecture

```
new batch ─► process_new_accounts()   upsert by account_id (update existing, append new)
                    │
raw data ─► clean_data() ─► score_dependency() ─► build_segments() ─► apply_guardrails()
          ─► build_feature_context() ─► assign_nba()                          [Stages 1-4B, locked]
                    │
                    ▼
generate_execution_plan()   playbook, owner_role, channel, first action, follow-up,
                            draft message / internal brief, action_state, secondary-test arm
                    │
                    ▼
RunStore.run()   fingerprint input ─► compare_runs() vs last snapshot ─► change_type
                 ─► action registry (idempotent keys) ─► action_log (material changes only)
                    │
                    ▼
guardrail_checks()   19 hard tests ─► outputs/ CSVs ─► Excel QA tabs
```

**Separation of concerns:**
- The NBA engine decides **what** should happen: `primary_nba`, `execution_status` and `attention_priority`.
- The execution layer decides **how**: playbook, owner, channel, message or brief, and state.
- The run layer decides **whether anything is new**: change detection, the action registry and the log.

**Scale:** a synthetic portfolio of 30,000 accounts runs end to end in about 1.3 seconds with zero guardrail violations. All rules are vectorised, and there is no account-specific code.

---

## B. Playbook Library

There are 9 playbooks: 8 primary NBAs plus one secondary experiment. The full fields are on the **Playbook Library** tab, followed by every message template.

| ID | Primary NBA | Owner | Channel | First action | Follow-up | Stop / escalate |
|---|---|---|---|---|---|---|
| PB01 | Retention Conversation | AM (broker-led) / CS-Growth (self-serve) | Personal email, then call | Read brief; send outreach to book a call | Day 7; plan review day 30; GMV check day 90 | Stop if a pause is confirmed. Escalate to Portfolio Lead after 2 unanswered attempts or a further Key decline. |
| PB02 | Verify Demand / Win-Back | AM / CS-Growth | Personal email, then call | Established buyer: win-back. One-off / thin history: **cadence check, do not assume churn.** | Day 14 | Stop when cadence is confirmed (set a reminder for their buying window) or a churn reason is logged |
| PB03 | Guided Self-Serve Migration | AM (Portfolio Lead sign-off for Key) | AM call + in-app walkthrough; automated tracking | Ready: Day 0 walkthrough. Review: resolve guardrail. Key: sign-off. Pre-entry: second self-serve checkout. | Day 15–30, 45, 90 | Stop and restore high-touch support if At Risk. Reassess if nothing has changed by day 90. |
| PB04 | Establish / Re-establish | Automation (new) / AM-CS (returned Key/Core) | Onboarding message / personal email + call | New: onboarding message. Returned: welcome-back outreach. | Day 14 (new) / Day 10 (returned) | Stop at the second order or once a cadence is agreed |
| PB05 | Discovery-to-Offer | Automation | Email / in-app | One Make an Offer prompt | One follow-up at day 14, only if still browsing with <3 offers; then stop | Stop at 3 offers, after 2 messages, or if the account becomes inactive or declining |
| PB06 | Reinforce Successful Behaviour | Automation | Email / in-app | One light reinforcement message | At most one per 30 days | **Never runs on Recent Inactivity.** A declining account is routed to a human. |
| PB07 | Service Model Review | Portfolio Lead | **Internal only** | Review card → maintain / lower-touch / automated nurture / revisit | Decision within 14 days | Decision logged. No ROI calculated, because AM cost data isn't available. |
| PB08 | Automated Nurture | Automation | Email / in-app | Message chosen by sub-context | Dormant 60 days; others 30 days | Stop after an order, an unsubscribe, or 2 unanswered dormant messages (then pause 6 months) |
| PB09 | Range Expansion Test (secondary) | Automation (Growth owns the experiment) | Email / in-app, **treatment arm only** | 50/50 split by account_id hash; the holdout group gets nothing | Read-out after 90 days | One message only. **No benefit claims.** |

---

## C. Human Queue (RUN001 baseline)

**75 accounts, £732.8k (86.7% of GMV).**

| Owner role | Accounts | What they do |
|---|---:|---|
| Account Manager | 53 | 25 retention, 10 verify/win-back, 3 re-establish, 15 migration (4 Ready, 6 Review, 5 pre-entry) |
| Portfolio Lead | 11 | ACC-005 on HOLD, 8 Service Model Reviews, 2 data reviews (ACC-078, 111) |
| Portfolio Lead + Account Manager | 7 | Key migration sign-off |
| **Customer Success / Growth** | 4 | **ACC-211, 214, 215, 216.** These are Self Serve accounts with no AM, so each is flagged `named_owner_required`. **A named person must be assigned before any work starts.** |

**Action states in the human queue:**

| State | Accounts |
|---|---:|
| Draft Ready | 51 |
| Awaiting Human Review | 8 |
| Not Started (internal reviews) | 8 |
| Awaiting Sign-Off | 7 |
| On Hold | 1 |

Every human-queue account has an **internal task brief** laid out as: Why now / What we know / What to do / What not to do / Success.

**Example brief: ACC-002, Verify**

> **WHY NOW:** Apparent lapse rests on 1-2 orders or one buying month; cadence is unknown.
> **WHAT WE KNOW:**
> - Key, Broker-Reliant, £70,650.
> - Lapsed, last GMV in October, 2 orders over 2 months.
> - Broker reliance 70% (1 AM-placed / 1 self-serve order).
> - 6 product views, 2 offers.
> - Warnings: MATERIAL_BROKER_INCONSISTENCY; LOW_CONFIDENCE.
>
> **WHAT TO DO:** Do not assume churn. Verify expected purchase frequency first.
> **WHAT NOT TO DO:** Do not treat as churn or run a discount-led win-back.

---

## D. Automated Queue (RUN001)

**225 accounts, £112.6k.** All are **Draft Ready (queued, not sent).**

| Automated action | Accounts | Template |
|---|---:|---|
| Nurture – dormant | 139 | NUR_DORMANT (60-day cadence) |
| Nurture – new customer onboarding | 46 | NUR_NEW |
| Nurture – returned customer | 17 | NUR_RETURNED |
| Nurture – light-touch repeat / standard / engaged-not-converting / rising-tail early | 4 / 4 / 3 / 2 | NUR_REPEAT / NUR_STANDARD / NUR_ENGAGED / NUR_RISING |
| Reinforce Successful Behaviour | 6 | REINFORCE |
| Discovery-to-Offer | 3 | DTO (ACC-111 is held for review) |
| Establish (new, ACC-217) | 1 | EST_NEW (includes a Make an Offer tip, because the account browses heavily but has made no offers) |
| Range Expansion secondary test | 2 (ACC-083, 085) | RANGE_HANDPICK. Both fall in the treatment arm. **Two accounts are far too few to learn anything; this is the design, not a result.** |

**139 automated accounts are Account Managed** and carry `notify_am_before_send = TRUE`, so the AM should be told before anything goes out.

---

## E. Guided Migration Workflow

| Group | Accounts | Status | Customer draft |
|---|---|---|---|
| Phase 1 Ready | ACC-019, 027, 030, 031 | Ready — Hybrid, AM | MIG_DAY0 (walkthrough invitation) |
| Phase 1 Manual Review | ACC-020, 024, 033, 036, 056, 058 | Human Review Required | **Withheld** until the review is done |
| Key sign-off | ACC-001, 003, 004, 006, 007, 012, 016 | Human Sign-Off Required | **Withheld** until sign-off |
| Pre-entry | ACC-029, 034, 039, 049, 057 | Ready — Human | MIG_PREENTRY (tip on checking out directly; sourcing continues as usual) |

**90-day plan for Ready accounts:**

| When | What happens |
|---|---|
| **Day 0** | The AM runs a walkthrough on finding stock independently, browsing regularly, shortlisting where the app supports it, using Make an Offer where it fits, and checking out themselves. **AM support stays in place.** |
| **Day 15–30** | Light check-in covering product views, app days, offers and any self-serve orders. |
| **Day 45** | Formal review of M1–M4 against the GMV guardrail. |
| **Day 90** | One of four outcomes: **Self-Serve Capability Demonstrated** / **Progressing – Extend** / **At Risk – Restore support** / **No Change – Reassess**. |

**The message framing** is about faster access to the full range, browsing whenever suits the customer, and direct control over purchasing. It never mentions cost reduction or "migration"; a guardrail test checks for this.

**Monitoring on a rerun:** 90-day inputs update `migration_progress_status` automatically. This is covered by unit tests with sample inputs:
- ACC-019 → Capability Demonstrated
- ACC-027 → Progressing
- ACC-030 → At Risk (GMV guardrail breached)
- ACC-031 → Baseline

---

## F. Message / Task Generation

**Customer drafts:** 276 in RUN001 (22 templates in the library).
- **Length:** 45–68 words.
- **Placeholders:** `{first_name}` and `{sender_name}` only; no invented names.
- **Only one data-driven detail:** the product type the customer buys (bundles and/or handpicked stock).
- **Not included:** internal metrics, numbers or £ figures.

**No draft is produced for:**

| Case | Accounts |
|---|---:|
| HOLD | 1 |
| Service Model Review | 8 |
| Awaiting human review | 8 |
| Awaiting sign-off | 7 |

**Language rules:**
- **Banned:** churn, "stopped buying", algorithm, dependency, migration, score, "noticed you", broker, cost.
- **No chat or video prompts.**
- **Range Expansion drafts** use "Would you like to explore another way of sourcing stock?" and make no claim of benefit.

**Sample: Retention Conversation, AM-owned account**

> Hi {first_name},
>
> I'd like to set up a short call to review how sourcing through Fleek is working for you at the moment and what you're planning to buy over the next few months. It will help me make sure the stock I source for you (handpicked stock) is the right fit. Would sometime later this week or early next week suit you?
>
> Best,
> {sender_name}

**Sample: Verify cadence (thin history)**

> Hi {first_name},
>
> Thanks for your previous orders with Fleek. I wanted to check how you usually plan your stock buying (seasonal, project by project, or ongoing) so we can get in touch at the right moments rather than too often. Happy to talk on a quick call, or just reply here with what works for you.
>
> Best,
> {sender_name}

---

## G. Action State & Logging

**`action_state` values:**

| State | When it applies |
|---|---|
| Not Started | Internal tasks |
| Draft Ready | Human or automated drafts that have been generated but not sent |
| Awaiting Human Review | Human Review Required |
| Awaiting Sign-Off | Key migration accounts |
| On Hold | Critical data issue |
| In Progress, Completed, No Action Required | Reserved for real execution feedback. **No account is set to these, because nothing has actually been done.** |

**State files** (`state/`, CSV here; a database table in production):

| File | Contents |
|---|---|
| `account_snapshot` | Latest decision per account, with the action key and a hash of the input row |
| `action_log` | The requested log fields |
| `action_registry` | One row per generated action key |
| `run_history` | Input fingerprint and counts for each run |

**How a rerun behaves:**
- **Action key:** a hash of account + playbook + reason code + execution status + template. **The same key is never generated twice.**
- **Log rows:** written only for BASELINE, NEW_ACCOUNT or a material change.
- **Unchanged accounts** keep their existing `action_state`.
- **Change types:** NEW_ACCOUNT, NBA_CHANGED, PRIORITY_INCREASED, PRIORITY_DECREASED, EXECUTION_STATUS_CHANGED, ENTERED_HUMAN_QUEUE, LEFT_HUMAN_QUEUE, MIGRATION_PROGRESS_CHANGED, NO_MATERIAL_CHANGE.
- **Internal-only flags:** GUARDRAILS_CHANGED and DATA_UPDATED are recorded but never trigger an alert.

---

## H. `new_accounts` Second Run (RUN002)

| Item | Result |
|---|---|
| Rows in `new_accounts` | 50 |
| **Existing IDs updated in place** | **5** (ACC-006, 008, 048, 211, 214) |
| **New IDs appended** | **45** (ACC-301 to ACC-345) |
| Duplicate IDs | 0 |
| **Resulting portfolio** | **345 accounts, £929.1k GMV** (+£69.3k from new accounts) |
| Log rows written | 46 (45 NEW_ACCOUNT + 1 NBA_CHANGED) |
| New actions generated | 46 |
| Existing accounts with no material change | 299 |

**Changes to existing accounts:**

| Account | What changed | Engine response |
|---|---|---|
| **ACC-211** | February GMV of £3,500 added. Momentum went from Declining to **Stable (−13%)**, so the account moved from Segment 8 to **6 Growth Opportunity**. | NBA changed from Retention Conversation to **Reinforce**, but **Human Review Required**: the account is now February-sensitive (without February it would read Declining). Priority went from P1 to **P2**. Owner is CS-Growth; the draft is withheld. |
| ACC-008 | February GMV of £3,000 added; broker reliance changed from 84% to 66%; order channels reclassified | NBA unchanged. Now flagged BORDERLINE (−21%) and MATERIAL_BROKER_INCONSISTENCY (internal GUARDRAILS_CHANGED flag). |
| ACC-048, 214 | February GMV added | NBA unchanged; guardrail codes updated |
| ACC-006 | February GMV added; broker reliance changed from 84% to 64%; self-serve orders went from 2 to 5 | No change (still Key sign-off). Internal DATA_UPDATED flag only. |

**New accounts (45; 37 Tail, 6 Core, 2 Key):**
- **Human queue: 10**
  - Retention: ACC-301 (Key, £16.4k), ACC-303
  - Verify: ACC-305, 306
  - Key sign-off: ACC-302
  - **Phase 1 Ready: ACC-304** (Core, regular buyer, blank status)
  - Migration pre-entry: ACC-308
  - Re-establish: ACC-307
  - Service Model Review: ACC-310, 313
- **Automated nurture: 35.** One of these, **ACC-311**, joins the Rising Tail watchlist.

**Portfolio after RUN002:**

| Measure | RUN001 | RUN002 |
|---|---|---|
| Priority (P0 / P1 / P2 / P3 / P4) | 1 / 39 / 24 / 23 / 213 | 1 / 42 / 28 / 27 / 247 |
| Human queue | 75 | **85** (10 new accounts; no existing account entered or left) |
| Phase 1 Ready | 4 | 5 (ACC-304 added) |

**Pattern worth raising:** all five updated accounts changed **only in February**, and some orders were reclassified between AM-placed and self-serve. This supports the Stage 3.1 concern that the original February was incomplete. It also shows that order-channel attribution can change between extracts. **Both points should be confirmed with the data owner before Phase 1 launches.**

---

## I. Idempotency Test (RUN003)

The exact RUN002 input was run again five minutes later.

| Check | Result |
|---|---|
| Input fingerprint matches RUN002 | ✔ `identical_to_previous_input = True` |
| Accounts | 345 (no duplicates; snapshot has 345 unique IDs) |
| Log rows written | **0** (total stays at 346) |
| New actions generated | **0** (registry stays at 346 rows, all unique keys) |
| Change types | 345 × NO_MATERIAL_CHANGE |
| Action states | Identical to RUN002 |

**Additional unit test:** the same data with rows in a different order, on a later run, also generates 0 actions and 0 log rows. Identity is based on `account_id` and the decision fields, not on row position.

**Test suite:** `python -m pytest` → **8 passed**. The tests cover:
- locked segment counts
- the Phase 1 lumpy rule
- the NBA distribution
- guardrails
- upsert
- idempotency (both variants)
- migration-progress transitions

---

## J. Guardrail Validation

All **19 checks show 0 violations** on RUN001, RUN002 and RUN003 (see the **Execution Guardrails** tab):
- one row per account
- every account has an NBA, status, priority, state and owner
- **HOLD → no outbound message**
- **Sign-off → no migration message**
- **Human Review → no automated outbound**
- **Segments 2, 3 and 8 → no automated or growth actions**
- **Service Model Review → no customer draft**
- **Recent Inactivity → no automated growth action**
- Broker-Reliant → no growth nudge
- Key MC always goes to sign-off
- **no chat or video encouragement**
- no banned phrases
- **Range drafts make no benefit claim**
- nothing sent to the holdout arm
- no internal numbers in drafts
- 40–100 words per draft
- no unfilled placeholders
- every human-queue account has a brief
- every Self Serve human action is flagged for a named owner

**"No repeated message on rerun"** is enforced by the action registry and proven in I.

The workbook's own Stage 3 and Stage 4B validation blocks still pass. The NBA Engine formulas match the code output on all 300 accounts.

---

## K. Edge Cases

| Account | Handling |
|---|---|
| **ACC-005** | Retention Conversation, **On Hold**, owner Portfolio Lead. The brief says to resolve the duplicate and confirm GMV isn't double-counted; no contact until then. |
| **ACC-001 / 003** | Migration, Awaiting Sign-Off. Borderline and February-sensitive, so declining sign-off is a legitimate outcome. |
| **ACC-036** | Now Manual Review (LUMPY_CADENCE). The draft is withheld. |
| **ACC-211** | RUN002 shows why the guardrails matter: its growth status depends on one February month, so the automated reinforcement is held for a human check. |
| **ACC-216** | Verify check-in (CHECKIN template), CS-Growth owner. **Named owner required.** |
| **ACC-078 / 111** | Automated actions held because the implied broker % would re-segment them. Owner is Portfolio Lead. |
| **ACC-304 (new)** | Phase 1 Ready despite a blank status and no February GMV. Blank status is not a blocker; the missing February is shown only as a warning. **The AM should confirm before Day 0.** |
| **ACC-025** | Reinforce, automated. The account is AM-owned, so `notify_am_before_send` is set. |
| **Range test** | Deterministic hash assignment puts both eligible accounts in the treatment arm. That is expected with n = 2 and is a reason not to read any result from this sample. |

---

## L. Files / Code Added

**`fleek_gtm_engine/`** (about 1,270 lines, in your Job Search folder)

```
fleek_engine/
  config.py        all thresholds (mirrors the Assumptions tab)
  pipeline.py      load_data, clean_data, score_dependency, build_segments, apply_guardrails,
                   build_feature_context, assign_nba, migration_progress, run_analytics
  playbooks.py     playbook library (9)
  execution.py     generate_execution_plan: owner, channel, templates, briefs, state, test arm
  runs.py          process_new_accounts, fingerprint, compare_runs, RunStore (snapshot/log/registry/history)
  validate.py      guardrail_checks (19 tests)
run_pipeline.py    CLI (daily run, optional --new-accounts-sheet)
demo_runs.py       RUN001 baseline -> RUN002 new_accounts -> RUN003 identical rerun
tests/test_engine.py  8 pytest tests
data/              source workbook copy (unmodified)
demo_outputs/      execution queues, guardrail results, RUN002 changes, demo_summary.json
demo_state/        account_snapshot, action_log, action_registry, run_history
requirements.txt
```

**`Fleek_Dependency_Scoring.xlsx`:**
- **New tabs:**
  - Execution Queue (RUN001)
  - Playbook Library (with all message templates)
  - Change Log (run history and action log)
  - Execution Guardrails
  - Execution Queue Run2
- **Updated tabs:**
  - **Segmentation:** column AU's Phase 1 formula now includes the lumpy rule.
  - **Phase 1 Cohort:** manual-review reasons now list lumpy cadence.
  - **NBA Engine:** adds the `LUMPY_CADENCE` code.
  - **NBA Library:** review wording updated.
  - **Assumptions:** B83/B84 labels and row 88 note.
- The source dataset is unchanged.

**Report:** `Fleek_Execution_Playbook_Report.md`.

---

## M. What Remains for the Final Product Build

1. **Lightweight UI:** a human queue by owner and priority, with the brief, draft and approve/decline buttons that write `action_state` and sign-off decisions back to the state store.
2. **Feedback loop:** record sent, replied, completed and outcome; add the 90-day monitoring inputs; set In Progress / Completed states from real events.
3. **Owner assignment:** map `owner_role` to named people, especially for Self Serve accounts in the human queue.
4. **Integrations:** email or CRM send for Ready — Automated rows only; a suppression list and unsubscribe handling; nurture cadence enforced against the actual send date.
5. **Repository:** README, architecture diagram, commit history, CI running `pytest` and `guardrail_checks`, and a final rerun demo plus a Loom walkthrough plan.
6. **Data requests still open:**
   - Is February complete? (The RUN002 updates suggest it was not.)
   - How are orders attributed to AM vs self-serve, given the reclassification seen between extracts?
   - What does ACC-005's duplicate status refer to?
   - Offer acceptance data.
   - What window do the chat and video counts cover?
   - AM cost per account.
