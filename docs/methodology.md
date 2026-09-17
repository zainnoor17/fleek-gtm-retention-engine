# Methodology (summary)

**Data:** 300 accounts, September 2025 to February 2026, from the `Accounts` sheet. A 50-row `new_accounts` batch is used for the second run.
**Where the detail lives:** the full reasoning, tables and pressure tests for each stage are in `reports/`. Every threshold below is defined in `fleek_engine/config.py`.
**Approach:** rules only. There is no model, no weighting beyond the specified dependency score, and no code written for individual accounts.

---

## 1. Dependency (Stage 1)

**Score:** `0.5 × broker + 0.3 × app + 0.2 × offer`. Each sub-score is banded 0, 25, 50, 75 or 100.

| Sub-score | 0 | 25 | 50 | 75 | 100 |
|---|---|---|---|---|---|
| Broker % | ≤20 | <40 | <60 | <80 | ≥80 |
| App active days | >30 | ≥20 | ≥10 | ≥5 | <5 |
| Offers | ≥5 | ≥3 | 2 | 1 | 0 |

- **Gate:** if broker reliance is 20% or lower, the score is 0.
  - Without the gate, low app use plus zero offers adds up to 50 points even for accounts with no AM-placed orders.
  - Before the gate, 79 of 93 "Medium" accounts had zero AM-placed orders.
- **Tiers:**

  | Tier | Score | Accounts | Share of GMV |
  |---|---|---:|---:|
  | High | ≥70 | 64 | 72.2% |
  | Medium | 40–69 | 14 | 10.9% |
  | Low | <40 | 222 | 17.0% |

- **Benchmark:** the gated score was checked against a simple binary rule. See the Stage 1 report.
- **Behavioural segment:**
  - Any account that is not Low → **Broker-Reliant** (78 accounts, 83.0% of GMV)
  - Low and Account Managed → **AM-Owned / Self-Serving** (132 accounts)
  - Low and Self Serve → **Self-Serve** (90 accounts)
- **Caveat:** `broker_reliance_pct` does not reconcile with the order counts in 157 rows. The provided % is used as the source of truth. The order-count version is kept as a guardrail (section 5).

## 2. Value tiers (Stage 2)

| Tier | 6-month GMV | Accounts | Share of GMV |
|---|---|---:|---:|
| Key | ≥ £10k | 18 | 63.5% |
| Core | ≥ £2k | 51 | 24.0% |
| Tail | below £2k | 231 | 12.5% |

- The portfolio is very concentrated. The Gini coefficient is 0.81, and ACC-001 alone is 20% of GMV.
- `gmv_trend_pct` is not used. It is only (Feb − Sep) ÷ Sep, it is blank for 150 rows, and it points the wrong way in 22 cases.

## 3. Momentum (Stages 2–3.1)

Momentum compares H2 GMV (December to February) with H1 GMV (September to November).

| Momentum | Rule | Accounts |
|---|---|---:|
| Growing | at least +20% | 29 |
| Stable | between −20% and +20% | 15 |
| Declining | more than 20% below | 34 |
| Lapsed | H1 > 0 and H2 = 0 | 149 |
| H2 Active / No H1 GMV | H1 = 0 and H2 > 0 | 73 |

Context flags (these never change an account's segment):

- **`february_sensitive`:** momentum is recalculated without February, comparing monthly averages. The flag is set when the momentum group changes. 36 accounts are flagged.
- **`borderline_momentum`:** the H2-vs-H1 change is within 5 points of ±20%. 9 accounts are flagged.
- **`lapse_context`:**
  - **One-Off / Verify** if the account has 2 or fewer orders, or only one month with GMV.
  - Otherwise **Established Buyer Lapsed**.
- **`lifecycle_context`:** New Customer, Returned Customer or Existing Customer.

## 4. Action segments (Stage 3)

Each account matches exactly one of nine rules, based on dependency × value × momentum:

| # | Segment | Rule | Accounts | Share of GMV |
|---|---|---|---:|---:|
| 1 | Migration Candidate | Broker-Reliant, Key/Core, Growing or Stable | 22 | 44.0% |
| 2 | Protect / Retain First | Broker-Reliant, Key/Core, Declining | 25 | 22.2% |
| 3 | Win-Back / Verify | Broker-Reliant, Key/Core, Lapsed | 8 | 12.0% |
| 4 | Establish / Re-establish / Observe | Broker-Reliant, Key/Core, H2-only | 2 | 2.2% |
| 5 | Cost-to-Serve / Low-Touch | Broker-Reliant, Tail | 21 | 2.5% |
| 6 | Growth Opportunity | Low dependency, Key/Core, Growing or Stable | 4 | 2.6% |
| 7 | Onboard / Re-engage / Learn | Low dependency, Key/Core, H2-only | 2 | 0.7% |
| 8 | Retention / Reactivation | Low dependency, Key/Core, Declining or Lapsed | 6 | 3.8% |
| 9 | Long-Tail Automated Nurture | Low dependency, Tail | 210 | 9.9% |

## 5. Guardrails (Stages 3.1 and 5)

These route accounts. They never contact anyone.

| Guardrail | Effect |
|---|---|
| `CRITICAL_DATA_BLOCKER` | ACC-005 has "Duplicate" status → **HOLD**, P0, no drafts. |
| `KEY_SIGNOFF` | A Key Migration Candidate → **Human Sign-Off Required**. |
| `PHASE1_MANUAL_REVIEW` | An eligible Phase 1 account with a warning goes to **Human Review Required**. Warnings are: material broker inconsistency, borderline momentum, February sensitivity, or **lumpy cadence** (fewer than 3 GMV months or fewer than 5 orders; added in Stage 5). |
| `MATERIAL_BROKER_INCONSISTENCY` | The order-count broker % would cross the gate, or change the band or tier. If it would also change the account's segment, automated actions are held (ACC-078, 111). |
| February-sensitive or borderline growth signal | An automated growth action is held for human review. |
| `LOW_CONFIDENCE`, `H2_SINGLE_MONTH_SPIKE`, `NO_FEB_GMV` | Shown to the reviewer as context. |

- **Phase 1 eligibility:** Migration Candidate, Core, at least 3 orders, at least 2 self-serve orders, and not a duplicate.
- **Result:**
  - **Ready (4):** ACC-019, 027, 030, 031
  - **Manual Review (6)**
  - **Key Sign-Off (7)**
  - **Pre-Entry (5)**

## 6. Feature findings (Stage 4A; association, not causation)

- **Discovery is the divide.** All 78 Broker-Reliant accounts have 15 or fewer product page views. PDP views are not a score input, so this is independent confirmation of the segmentation.
- **Chat, video and handpick are high-touch behaviours.** Broker-Reliant accounts generate 57% of chat threads, 81% of video requests and 78% of handpick orders. **These are never targets.**
- **Make-an-Offer is widely used but shallow.** Heavy offer use does not protect spend: ACC-211 made 71 offers and is shrinking.
- **Bundles are the default.** 66% of accounts buy only bundles, so bundle adoption is not a lever.
- **No Migration Candidate meets any self-serve milestone.** The milestones are 10+ app days, 50+ PDP views and 3+ offers. Having 2 or more self-serve orders does not mean an account discovers stock independently.
- **In the long tail, engagement goes with repeat buying.** Among low-dependency Tail accounts, those with 20+ app days repeat-purchase 61% of the time, against 15% for the rest. The direction of cause is unknown.

## 7. NBA architecture (Stage 4B)

1. **Assign a reason code.** An ordered `np.select` over segment and context sets it: recency, discovery gap, strong self-serve pattern, rising-tail watchlist, lifecycle, lapse context and Phase 1 status. There are 18 reason codes.
2. **Map to an action.** Each code maps to a `primary_nba` (8 actions), a delivery mode and a default priority.
3. **Set the execution status separately.**

   | Order | Condition | Execution status |
   |---|---|---|
   | 1 | Duplicate | HOLD |
   | 2 | Key Migration Candidate | Sign-off |
   | 3 | Manual Review | Review |
   | 4 | Automated action on a doubtful signal | Review |
   | 5 | None of the above | Ready — Human / Hybrid / Automated |

4. **Set the priority.**

   | Priority | Covers |
   |---|---|
   | P0 | Critical hold |
   | P1 | Revenue protection |
   | P2 | Active intervention (migration, re-establish, growth) |
   | P3 | Growth / efficiency |
   | P4 | Automated / monitor |

5. **Sort the queue.** Priority, then value tier, then GMV. There is no composite score.

**Baseline counts:**

| Priority | Accounts |
|---|---:|
| P0 | 1 |
| P1 | 39 |
| P2 | 24 |
| P3 | 23 |
| P4 | 213 |

- 75 accounts are in the human queue (86.7% of GMV).
- 225 accounts are automated (13.3% of GMV).

## 8. Execution rules (Stage 5)

- **9 playbooks** (8 primary plus 1 secondary experiment) and **22 message templates**.
- **Owner role:**

  | Owner role | Handles |
  |---|---|
  | Account Manager | Broker-led and AM-owned human work |
  | Customer Success / Growth | Self Serve human work (flagged `named_owner_required`) |
  | Portfolio Lead | HOLD, Service Model Review, data reviews |
  | Portfolio Lead + Account Manager | Key sign-off |
  | Automation | Everything automated |

- **Drafts:**
  - 40–100 words
  - `{first_name}` and `{sender_name}` placeholders only
  - the only data-driven detail is the product type the customer buys
  - no internal numbers
  - **banned words:** churn, stopped buying, algorithm, dependency, migration, score, noticed you, broker, cost
  - no chat or video prompts
- **When a draft is withheld:** the account is on HOLD, awaiting review, awaiting sign-off, or has a Service Model Review. The UI shows the reason instead of a draft.
- **Internal brief** (for every human-queue account): Why now / What we know / What to do / What not to do / Success.
- **`action_state`:** Not Started, Draft Ready, Awaiting Human Review, Awaiting Sign-Off, On Hold, In Progress, Completed, No Action Required. The last three change only through local workflow events.
- **Validation:** 19 execution guardrail checks must all return 0 (`validate.py`). They pass on RUN001, RUN002 and RUN003.

## 9. Rerun and change detection (Stage 5)

- **Upsert:** `new_accounts` updates existing IDs in place and appends new ones. RUN002 updated 5 accounts (ACC-006, 008, 048, 211, 214) and added 45 (ACC-301 to 345), for a total of 345 accounts and 0 duplicates.
- **Input fingerprint:** a hash of the engine version plus the sorted per-row hashes, so row order doesn't matter. When the input is identical, `identical_to_previous_input = True`.
- **`compare_runs`:** compares each account with its last snapshot and assigns a change type:
  - NEW_ACCOUNT
  - NBA_CHANGED
  - PRIORITY_INCREASED / PRIORITY_DECREASED
  - EXECUTION_STATUS_CHANGED
  - ENTERED_HUMAN_QUEUE / LEFT_HUMAN_QUEUE
  - MIGRATION_PROGRESS_CHANGED
  - NO_MATERIAL_CHANGE

  GUARDRAILS_CHANGED and DATA_UPDATED are recorded as internal flags only.
- **Action key:** a hash of account + playbook + reason + status + template (+ secondary-test template). The registry never holds a duplicate key. Log rows are written only for a baseline, a new account or a material change. Accounts with no material change keep their `action_state`.
- **RUN002 results:**
  - 46 log rows and 46 new actions
  - **ACC-211:** Retention Conversation (P1) → Reinforce (P2), Human Review Required, because the growth signal is FEB_SENSITIVE
  - 10 new accounts entered the human queue
- **RUN003 (identical input):** 0 log rows, 0 new actions, 345 × NO_MATERIAL_CHANGE.

## 10. Limitations

- **Data window and shape.** There is one 6-month cross-section, and 53% of accounts have a single order. Results show association, not causation.
- **Data questions still open:**
  - Is February complete? All 5 updated accounts changed only in February.
  - Order-channel attribution changed between extracts.
  - What does ACC-005's duplicate status mean?
  - Does web usage appear in the app-days count?
  - There is no offer-acceptance data.
  - What time window do the chat and video counts cover?
  - There is no AM cost data.
- **No outcomes.** There is no outcome data or 90-day monitoring feed yet, so migration progress stays at Baseline.
- **Inconsistency to resolve with the business.** In `migration_progress()`, an account at day 90 with no progress is labelled **At Risk** (support restored). The playbook text describes a separate "No Change – Reassess" outcome. The code is the more conservative of the two. It was left unchanged because Stage 5 logic is locked.
- **Thresholds.** They are calibrated on this portfolio only. The Range Expansion test has n = 2.
- **Prototype infrastructure.** State is local CSV, single-user, with no send integration.
