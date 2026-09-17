# Fleek Retention Case Study: Stage 3.1 Refinement Pass

**Unchanged:** the dependency score, the value tiers, the ±20% momentum threshold and the nine action segments.
**Result:** the nine segments and their counts are identical to Stage 3 (22 / 25 / 8 / 2 / 21 / 4 / 2 / 6 / 210), and all validation checks still pass (300 accounts, each assigned exactly once, GMV total £845,401).
Every new field is a context flag or guardrail. None of them changes an account's segment. All are live workbook formulas, and each one was rebuilt independently in Python and matches the workbook on every account.

---

## A. What Changed

| Change | Detail |
|---|---|
| Momentum label | "New in H2" is renamed **"H2 Active / No H1 GMV"**. The calculation is unchanged. |
| Segment labels | Segment 4 → **Establish / Re-establish / Observe**. Segment 7 → **Onboard / Re-engage / Learn**. Membership is unchanged. |
| New fields | `lifecycle_context`, `key_account_signoff_required`, `borderline_momentum`, `february_sensitive` (plus the ex-February momentum used to set it), `lapse_context`, `material_broker_inconsistency` (plus the implied score, tier, behavioural segment and action segment), `phase1_rollout_status`, and a combined guardrail-warnings text field |
| Renamed | `migration_pilot_eligible` → `phase1_cohort_eligible`. The "Pilot Cohort" tab → **Phase 1 Cohort**. Eligibility criteria are unchanged. |
| **Correction to Stage 3** | The Stage 3 report said none of the four accounts that cross the 20% broker gate would become Broker-Reliant. **That was wrong.** If the order-count percentage were used, ACC-078 and ACC-111 would score Medium and move from Long-Tail to Cost-to-Serve (see G). The Stage 3 report has been corrected. |

**Rules used (all thresholds are on the Assumptions tab):**

| Field | Rule |
|---|---|
| `lifecycle_context` | If H1 = 0 and H2 > 0: tenure ≤6 months → **New Customer**; tenure >6 months → **Returned Customer**. Every other account → **Existing Customer**. |
| `key_account_signoff_required` | Migration Candidate **and** Key |
| `borderline_momentum` | Has GMV in both H1 and H2, **and** the H2-vs-H1 change is within 5 points (inclusive) of +20% or −20% |
| `february_sensitive` | Momentum is recalculated **without February**: Sep–Nov average per month against Dec–Jan average per month, using the same ±20% rule. The flag is TRUE if the account's momentum group changes. The groups are: Growing/Stable (treated as one), Declining, Lapsed, H2-only, and no activity. |
| `lapse_context` (Lapsed accounts only) | **One-Off / Insufficient History — Verify** if orders ≤2 **or** only one month with GMV. Otherwise **Established Buyer Lapsed**. |
| `material_broker_inconsistency` | Comparing the provided broker % with the % implied by manual and self-serve order counts: it crosses the 20% gate, **or** changes the broker scoring band, **or** changes the dependency tier |
| `phase1_rollout_status` | **Not Eligible** if the Phase 1 criteria aren't met. **Manual Review** if they are met but the account has a material broker inconsistency, borderline momentum or February sensitivity. Otherwise **Ready**. |

**Two judgement calls you should know about:**

1. **The February test differs from the Stage 3 quick check.**
   - Stage 3 compared Oct–Nov with Dec–Jan. That silently removed **September** as well as February, which led to wrong flags. ACC-024 and ACC-033 are examples: dropping September, not February, changed their result.
   - The Stage 3.1 test keeps the official Sep–Nov period and removes only February, comparing monthly averages.
   - Result: the Stage 3 method would flag 42 accounts; the corrected test flags 36.
2. **The one-off threshold is ≤2 orders, not ≤1.**
   - Two orders give a single gap between purchases. That isn't enough to call it a buying pattern, and it matches the existing low-confidence rule.
   - A strict ≤1 rule would have labelled **ACC-002 (£70.7k from 2 orders)** an "Established Buyer". That label would be commercially misleading.

---

## B. Lifecycle Breakdown

| lifecycle_context | Accounts | GMV |
|---|---:|---:|
| New Customer | 49 | £16,411 |
| Returned Customer | 24 | £33,051 |
| Existing Customer | 227 | £795,939 |

**Accounts you asked me to check:**

| Account | Tenure (months) | H1 → H2 | Segment | lifecycle_context |
|---|---:|---|---|---|
| ACC-011 | 34 | £0 → £15,600 | 4 | **Returned** |
| ACC-047 | 10 | £0 → £3,200 | 4 | **Returned** |
| ACC-048 | 14 | £0 → £3,113 | 7 | **Returned** |
| ACC-217 | 3 | £0 → £2,402 | 7 | **New** |

Both accounts in Segment 4 are returning customers, not new ones. Segment 7 has one of each.

**Caveat:** `lifecycle_context` only separates new from returning customers among the H2-only accounts. There are 154 accounts with tenure of 6 months or less, and 105 of them are labelled "Existing Customer" because they bought in H1. That label means "had H1 activity", not "long-standing customer".

---

## C. Key-Account Sign-Off

**7 accounts, £309,427 (36.6% of portfolio GMV):** ACC-001, 003, 004, 006, 007, 012 and 016.
All seven are Migration Candidates excluded from Phase 1.

---

## D. Borderline Momentum

**9 accounts, £254,384 (30.1% of GMV).**

| Account | H2 vs H1 | Momentum | Segment | Value |
|---|---:|---|---|---|
| ACC-001 | −18.1% | Stable | 1 Migration | Key |
| ACC-003 | −19.9% | Stable | 1 Migration | Key |
| ACC-004 | −15.7% | Stable | 1 Migration | Key |
| ACC-024 | −19.2% | Stable | 1 Migration | Core (**Phase 1**) |
| ACC-033 | −15.4% | Stable | 1 Migration | Core (**Phase 1**) |
| ACC-059 | −21.5% | Declining | 2 Protect | Core |
| ACC-064 | −16.6% | Stable | 5 Cost-to-Serve | Tail |
| ACC-056 | **+18.5%** | Stable | 1 Migration | Core (**Phase 1**) |
| ACC-230 | **+23.3%** | Growing | 9 Long-Tail | Tail |

All six accounts you listed are confirmed. An independent check of the +20% boundary found two more: ACC-056 and ACC-230.
**6 of the 22 Migration Candidates are borderline, including 3 of the 7 Key accounts.**

---

## E. February Sensitivity

**36 accounts are February-sensitive (£253,661, 30.0% of GMV).**

| What would change without February | Accounts |
|---|---:|
| H2-only account → no activity at all (their only purchase was in February; all Tail) | 21 |
| Declining → Lapsed | 6 |
| Growing → Lapsed | 4 |
| Stable → Declining | 3 |
| Declining → Stable | 2 |

Ten of the 36 are Key or Core accounts, so the difference would change how their segment is read:

**Migration Candidates affected: 4 of 22**

| Account | Official momentum | Without February |
|---|---|---|
| ACC-001 | Stable | **Declining** |
| ACC-003 | Stable | **Declining** |
| ACC-039 | Growing | **Lapsed** |
| ACC-058 | Growing | **Lapsed** |

**Protect / Retain First accounts affected: 6**

- ACC-023, 040, 046 and 053 would become **Lapsed**: February was their only H2 purchase.
- ACC-018 and ACC-059 would become **Stable**.

**Checking the six accounts from Stage 3:**
- ACC-001, 003, 039 and 058 are **confirmed** as February-sensitive.
- **ACC-024 and ACC-033 are not.** Their Stage 3 flag came from also dropping September. They are still flagged as borderline in D.

**Phase 1: one account is affected, ACC-058.** Its "Growing" status rests entirely on a £1,295 February order; it had nothing in December or January.

---

## F. Lapse Context

**149 Lapsed accounts:**
- **Established Buyer Lapsed: 14 accounts, £23.7k**
- **One-Off / Insufficient History — Verify: 135 accounts, £144.5k**

| Segment | Established | One-Off / Verify |
|---|---:|---:|
| 3. Win-Back / Verify | 2 (ACC-015 £11.5k; ACC-062 £2.0k) | 6 (ACC-002, 026, 032, 044, 050, 060) |
| 5. Cost-to-Serve | 2 | 10 |
| 8. Retention / Reactivation | 0 | 3 (ACC-038, **042**, **215**) |
| 9. Long-Tail | 10 | 116 |

**The accounts you asked me to check:**
- **ACC-002:** 2 orders across 2 months → Verify
- **ACC-042:** 1 order → Verify
- **ACC-215:** 1 order → Verify

**What this means for win-back work:** among Key and Core accounts, only **2 lapsed customers are genuine win-back cases**. The other 9 need a check on how often they buy before anyone calls them churned. ACC-050 is an example: it placed 6 orders, all in October.

---

## G. Material Broker Inconsistencies

**18 accounts, down from 85 under the previous flag, which fired on any gap over 10 points.**

- **4 cross the 20% gate:** ACC-048, 078, 111 and 120
- **10 change dependency tier**
- The rest change broker scoring band only
- 9 of the 18 have a gap of 10 points or less. These are cases sitting right at a band boundary, such as ACC-012 (provided 59%, implied 61%).

**Would any segment change if the implied % were used? Yes, for 2 accounts, both Tail and low value:**

| Account | Provided → implied | Implied score | Segment now → with implied % |
|---|---|---:|---|
| ACC-078 | 16% → 25% | 47.5 (Medium) | 9 Long-Tail → **5 Cost-to-Serve** (£1,366) |
| ACC-111 | 19% → 25% | 40.0 (Medium) | 9 Long-Tail → **5 Cost-to-Serve** (£592) |

Tier changes that don't change the segment (High ↔ Medium are both Broker-Reliant): ACC-002, 011, 035, 041, 056, 074, 113 and 128.
**No Key or Core account changes segment.** The provided % remains the scoring input.

---

## H. Phase 1 Migration Cohort

| Status | Accounts | GMV | % GMV |
|---|---|---:|---:|
| **Ready** | ACC-019, 027, 030, 031, 036 | £25,060 | 3.0% |
| **Manual Review** | ACC-020, 024, 033, 056, 058 | £20,248 | 2.4% |
| **Not Eligible** (Migration Candidates) | 7 Key (001, 003, 004, 006, 007, 012, 016) + 5 with only one self-serve order (029, 034, 039, 049, 057) | £326,956 | 38.7% |

**Why each Manual Review account is there:**

| Account | Reason |
|---|---|
| **ACC-020** | Material broker inconsistency. Provided 48% (band 50) against implied 33% (band 25). The tier stays Medium (the implied score is 55), but the evidence of dependency is weaker. **The rule places it in Manual Review; it has not been excluded.** |
| ACC-024 | Borderline (−19.2%) |
| ACC-033 | Borderline (−15.4%) |
| ACC-056 | Material inconsistency (implied tier would be High) **and** borderline (+18.5%) |
| ACC-058 | February-sensitive |

---

## I. Edge Cases Still Worth Challenging

1. **ACC-001 (£170k) triggers all three momentum and value guardrails:** Key sign-off, borderline, and February-sensitive. Without February it would be Protect / Retain First. ACC-003 is the same. **In practice, the two largest Migration Candidates look more like Protect accounts.** The sign-off flag covers this, but a reviewer should expect the AM to override the label.
2. **Two of the five Ready accounts are "Growing" because of a single month.**
   - **ACC-036:** H1 £369 against H2 £3,510, and all of H2 came in January (+851%).
   - **ACC-030:** all of H2 is one £3,513 January order (+289%).

   Neither is borderline or February-sensitive, so both pass. Both are single-month spikes on a small base. *Possible guardrail for later: require GMV in at least 2 of the H2 months before an account counts as Ready.* I haven't implemented it.
3. **ACC-036 has 37 orders but GMV in only 2 of 6 months.** That is unusual enough to check with the data owner before using it as a Phase 1 reference account.
4. **The ACC-058 "Growing" call rests on a single February order.** If February turns out to be incomplete, the call could become more positive, not less. Either way it is fragile.
5. **Lapsed is dominated by thin histories (135 of 149).** Win-back is effectively a two-account programme among Key and Core accounts.
6. **The material inconsistency flag still catches small gaps at band boundaries** (9 of 18 are ≤10 points). If this proves noisy in review, you could add a minimum gap (for example, 5 points) *as well as* the band change. I haven't changed it.
7. **ACC-005** (Duplicate status, £24.6k, Protect) is still unresolved. It remains the only critical blocker.

---

## J. Files and Tabs Changed

**`Fleek_Dependency_Scoring.xlsx`**

| Tab | Change |
|---|---|
| **Segmentation** | 17 new columns (AF–AV): the guardrail fields, the ex-February momentum, the implied broker sub-score, score, tier, behavioural segment and action segment, a "would change" flag, the rollout status and a combined warnings field. Column U is renamed `phase1_cohort_eligible`. The momentum label and segment 4/7 labels are updated. |
| **Segment Summary** | New "Stage 3.1 guardrails" section: lifecycle table, flag table (with counts for Migration Candidates, Key/Core and Phase 1), Phase 1 status table, and a guardrails-by-segment matrix. Labels updated. The validation block is unchanged and still passes. |
| **Phase 1 Cohort** | Renamed from Pilot Cohort and rebuilt: rollout status, reasons for exclusion or manual review, borderline and February flags, ex-February momentum, implied broker % and sign-off flag, sorted Ready → Manual Review → Not Eligible |
| **Assumptions** | Rows 45–53 added: borderline band (5 pts), New Customer tenure limit (6), one-off thresholds (≤2 orders, ≤1 month), and plain-language rules for the February test, material inconsistency, Key sign-off and Phase 1 status. Phase 1 labels renamed. |
| **Commercial View / Commercial Summary** | Momentum label renamed to "H2 Active / No H1 GMV". No logic change. |
| **Data Quality** | Stage 3 rows replaced with updated February, lifecycle, gate-crossing (**with the correction**), material-inconsistency and thin-lapse rows |

**Also changed:**
- `Fleek_Segmentation_Report.md` (Stage 3): section F.8 is corrected on gate-crossers.
- **New:** `Fleek_Segmentation_Stage3_1_Report.md` (this report).

**Source dataset:** not modified.
