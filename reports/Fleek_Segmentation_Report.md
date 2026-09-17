# Fleek Retention Case Study: Segmentation Layer (Stage 3)

**Scope:** implement and validate the behavioural and action segments. There is no Migration Priority Score, no Next Best Action and no dashboard at this stage.
**Pipeline:** Raw data → Dependency → Behavioural Segment → Commercial Value → Momentum → **Action Segment**.
**Source data:** unchanged (`Accounts` tab, 300 rows). The dependency method is unchanged (gated 50/30/20). Every classification in the workbook is a live formula; nothing was typed in by hand.

---

## A. Validation

**All 300 accounts are segmented exactly once. Every check passes.**

| Check | Result |
|---|---|
| Accounts segmented | 300 of 300 |
| Distinct account_ids | 300 (no duplicates) |
| Null or UNASSIGNED `action_segment` | 0 |
| Null or UNASSIGNED `behavioural_segment` | 0 |
| Rows matching **exactly one** of the 9 rule conditions | 300 |
| Segment counts sum to | 300 |
| Segment GMV sums to portfolio GMV | £845,401 = £845,401 |

The one-rule-per-account check doesn't reuse the segment formula. A separate column tests all nine conditions on each row and counts how many are true. Every row returns exactly 1.

The results were also rebuilt independently in Python and match the workbook on every account, for segments, pilot flag and data-quality flags. None of the expected totals were hard-coded. **They all reproduced exactly.**

**One small implementation note.** "Declining" uses a strict rule: H2 more than 20% below H1. In stage 2 the workbook formula counted exactly −20% as Declining. No account sits exactly on the line, so no result changed.

---

## B. Behavioural Segments

| Behavioural segment | Accounts | GMV | % accounts | % GMV | Median GMV |
|---|---:|---:|---:|---:|---:|
| Broker-Reliant | 78 | £701,881 | 26.0% | **83.0%** | £3,492 |
| AM-Owned / Self-Serving | 132 | £78,472 | 44.0% | 9.3% | £306 |
| Self-Serve | 90 | £65,048 | 30.0% | 7.7% | £266 |

These match the expected 78 / 132 / 90.

| Value tier | Key | Core | Tail |
|---|---:|---:|---:|
| Broker-Reliant | 17 | 40 | 21 |
| AM-Owned / Self-Serving | 0 | 5 | 127 |
| Self-Serve | 1 | 6 | 83 |

---

## C. Action Segments

| # | Action segment | Accts | GMV 6m | % accts | % GMV | Median GMV | Median orders | Value mix (Key / Core / Tail) | Momentum mix | Low-conf. |
|---|---|---:|---:|---:|---:|---:|---:|---|---|---:|
| 1 | Migration Candidate | 22 | £372,264 | 7.3% | **44.0%** | £4,596 | 8 | 7 / 15 / 0 | 12 growing, 10 stable | 0 |
| 2 | Protect / Retain First | 25 | £187,688 | 8.3% | **22.2%** | £3,906 | 8 | 7 / 18 / 0 | 25 declining | 0 |
| 3 | Win-Back / Verify | 8 | £101,754 | 2.7% | 12.0% | £3,781 | 3 | 2 / 6 / 0 | 8 lapsed | 3 |
| 4 | Establish / Observe | 2 | £18,800 | 0.7% | 2.2% | £9,400 | 3.5 | 1 / 1 / 0 | 2 new in H2 | 1 |
| 5 | Cost-to-Serve / Low-Touch | 21 | £21,375 | 7.0% | 2.5% | £1,071 | 2 | 0 / 0 / 21 | 12 lapsed, 3 new, 3 stable, 2 growing, 1 declining | 11 |
| 6 | Growth Opportunity | 4 | £21,991 | 1.3% | 2.6% | £4,957 | 8 | 0 / 4 / 0 | 4 growing | 0 |
| 7 | Onboard / Learn | 2 | £5,515 | 0.7% | 0.7% | £2,758 | 6.5 | 0 / 2 / 0 | 2 new in H2 | 0 |
| 8 | Retention / Reactivation | 6 | £32,123 | 2.0% | 3.8% | £3,805 | 4.5 | 1 / 5 / 0 | 3 declining, 3 lapsed | 3 |
| 9 | Long-Tail Automated Nurture | 210 | £83,891 | 70.0% | 9.9% | £273 | 1 | 0 / 0 / 210 | 126 lapsed, 66 new, 11 growing, 5 declining, 2 stable | 182 |
| | **Total** | **300** | **£845,401** | 100% | 100% | | | | | 200 |

Segments 1–5 are all Broker-Reliant. Segments 6–9 split by behaviour as follows:

| Segment | AM-Owned / Self-Serving | Self-Serve |
|---|---:|---:|
| 6. Growth Opportunity | 1 | 3 |
| 7. Onboard / Learn | 1 | 1 |
| 8. Retention / Reactivation | 3 | 3 |
| 9. Long-Tail Automated Nurture | 127 | 83 |

All nine segment counts match your expected figures.

**What the table says:** segments 1 to 3 (55 accounts) hold **78% of GMV**. Within that, **more of the money is in accounts that are declining or have stopped buying (segments 2 and 3, 34%)** than in accounts that are ready for a migration test and aren't Key accounts (Core Migration Candidates, 7.4%).

---

## D. Migration Pilot

**10 accounts qualify: £45,308 of GMV, 5.4% of the portfolio.**
Rule: Migration Candidate, Core value, at least 3 orders, at least 2 self-serve orders, and not marked Duplicate. `action_segment` is unchanged for all of them.

| Account | Dep. score (tier) | GMV | Orders | Manual | Self-serve | Self-serve share | Momentum (H2 vs H1) | Flags |
|---|---|---:|---:|---:|---:|---:|---|---|
| ACC-019 | 70 (High) | £7,716 | 7 | 4 | 3 | 43% | Growing (+334%) | – |
| ACC-020 | 67.5 (Med) | £6,452 | 3 | 1 | 2 | 67% | Stable (−14%) | **Broker % vs counts +15pts** |
| ACC-024 | 70 (High) | £5,214 | 14 | 9 | 5 | 36% | Stable (**−19%**) | – |
| ACC-027 | 82.5 (High) | £4,678 | 25 | 18 | 7 | 28% | Stable (+5%) | – |
| ACC-030 | 87.5 (High) | £4,415 | 5 | 3 | 2 | 40% | Growing (+289%) | – |
| ACC-031 | 75 (High) | £4,372 | 8 | 6 | 2 | 25% | Growing (+166%) | – |
| ACC-033 | 65 (Med) | £3,925 | 8 | 4 | 4 | 50% | Stable (−15%) | – |
| ACC-036 | 75 (High) | £3,879 | 37 | 28 | 9 | 24% | Growing (+851%) | – |
| ACC-056 | 62.5 (Med) | £2,380 | 5 | 3 | 2 | 40% | Stable (+19%) | – |
| ACC-058 | 67.5 (Med) | £2,277 | 8 | 4 | 4 | 50% | Growing (+32%) | – |

Together these accounts have 80 manual and 40 self-serve orders. Every one has already placed orders without an AM and is not shrinking.

**The 12 Migration Candidates that don't qualify:**
- **7 are Key accounts**, which the rule excludes by design: ACC-001, 003, 004, 006, 007, 012 and 016.
- **5 are Core accounts with only one self-serve order**: ACC-029, 034, 039, 049 and 057.

---

## E. Exceptions and Edge Cases

| Account | Segment | What's odd | Implication |
|---|---|---|---|
| **ACC-001** (£170k, 20% of GMV) | 1. Migration Candidate | "Stable" at **−18%**, 2 points from Declining. If February is excluded, it reads as Declining. Only 3 app days and 0 offers. | The rule treats the largest account in the book the same as a £2.3k account. It is correctly kept out of the pilot, but the label alone invites the wrong action. |
| **ACC-002** (£70.7k) | 3. Win-Back / Verify | 2 orders, both in Sep–Oct, nothing since. Low confidence. The provided broker % is 70%, but the order counts give 50% (the tier would be Medium; the segment would not change). | This could be a buyer who purchases rarely in large amounts rather than a lapsed regular. Treat "Verify" as the first step before any "win-back". |
| **ACC-005** (£24.6k) | 2. Protect / Retain First | Status is **Duplicate**. It is the 5th-largest account and down 60% in H2. | If it really duplicates another account, its GMV is double-counted, and the decline could just be orders moving to the other ID. **Critical blocker:** hold all action until verified. |
| **ACC-011** (£15.6k) | 4. Establish / Observe | A single December order. Tenure is **34 months**, so it is a returning customer, not a new one. The provided broker % is 50%, but the counts give 100%. | "New in H2" is the wrong label here, and "learning the account" is the wrong frame for a returning customer. |
| **ACC-211** (£13.4k, Self Serve) | 8. Retention / Reactivation | The most engaged account in the book on offers (71; 100 app days), yet down 52% with no GMV since December | A correct result. The largest self-serve account is the biggest retention risk outside the broker-led group. |
| **ACC-212** (£8.6k, Self Serve) | 6. Growth Opportunity | Up 120%, 78 app days, 0% broker reliance | A correct result and the clearest growth case. |
| ACC-042, ACC-215 | 8. Retention / Reactivation | A single order each (£3.5k and £3.9k) in one month | Reactivation assumes a pattern existed. These are single purchases that never repeated. |
| ACC-048 | 7. Onboard / Learn | 14 months' tenure, no GMV in Sep–Nov, came back in January | A returning customer again, not onboarding |
| ACC-059 | 2. Protect / Retain First | −21.5%, 1.5 points past the Declining line | A borderline case, like ACC-001 on the other side of the line |

---

## F. Rule Critique

None of these required a rule change for the build to be technically correct, so the rules are exactly as you specified. The evidence and recommendations follow.

**1. The ±20% momentum line is too sharp for the accounts that matter most.**
Six Migration Candidates sit within 5 points of −20%: ACC-001 (−18%), ACC-003 (−19.9%), ACC-024 (−19%), ACC-004 (−16%), ACC-033 (−15%) and ACC-056 (+19%). ACC-059 (−21.5%) falls just the other side.
→ *Recommend* a "borderline momentum" warning for accounts within 5 points of the threshold, not a new threshold.

**2. Momentum depends on February, and February may be incomplete.**
Re-running momentum on Oct–Nov against Dec–Jan (leaving February out) turns **6 of the 22 Migration Candidates** Declining or Lapsed: ACC-001, 003, 024, 033, 039 and 058. **Three of those are in the pilot** (ACC-024, 033, 058).
If February is actually short, the current calls are too pessimistic, not too generous. Either way, one month of lumpy GMV decides the segment for about a quarter of this group.
→ *Recommend* confirming February's completeness before selecting the pilot.

**3. Migration Candidate mixes Key and Core accounts.**
The 7 Key accounts in segment 1 hold £309k (**36.6% of GMV**), and ACC-001 is one of them.
→ *Recommend* splitting segment 1 into Key and Core sub-segments, or adding a flag that requires AM sign-off for Key accounts. The pilot rule already makes this separation, but the segment label does not.

**4. "New in H2" usually means "came back", not "new".**
24 of the 73 New-in-H2 accounts have been customers for more than 6 months. Three of the four accounts in segments 4 and 7 are returning customers: ACC-011, ACC-047 and ACC-048. Only ACC-217 (3 months' tenure) is genuinely new.
→ *Recommend* splitting the label by tenure: "New customer" (6 months or less) and "Returned in H2" (more than 6 months). Returned Key or Core accounts fit better with Verify than with Onboard.

**5. "Lapsed" covers both one-off buyers and regular buyers who stopped.**
- 3 of the 8 Win-Back accounts have only a single month of history.
- 2 of the 6 Retention/Reactivation accounts made a single order.
- The largest Win-Back account (ACC-002) has 2 orders.

→ *Recommend* flagging lapsed accounts with single-month history as "one-off buyer, verify". Also consider splitting segment 8 into Retention (declining) and Reactivation (lapsed); the current 3/3 split already mixes two different problems.

**6. Most of Cost-to-Serve / Low-Touch are no longer buying.**
12 of the 21 accounts are lapsed (£9.3k), and 11 are low confidence. An account that isn't buying doesn't use AM time.
→ *Recommend* a "dormant" sub-flag, so that cost-to-serve work focuses on the 9 accounts that are still active.

**7. The £2k line hides promising Tail accounts, and Growth Opportunity is too small to act on.**
- Growth Opportunity has only 4 accounts (2.6% of GMV).
- Long-Tail includes growing, highly engaged accounts just under £2k: ACC-068 (£1.7k, 31 app days), ACC-083 (49 days, 14 offers), ACC-085, and ACC-086 (105 days, 50 offers).
- 127 of the 210 Long-Tail accounts are AM-Owned. They have a median of £296, account for 7.1% of GMV and show no broker usage. That raises a question about AM coverage, not about migration.

→ *Recommend* a "rising tail" flag (Tail, Growing, GMV of £1k or more; 4 accounts today) and a separate review of AM assignment for the 127.

**8. The broker-inconsistency flag is too broad to be useful.**
It fires on 85 accounts, but 69 of them are AM-Owned accounts with zero manual orders and a provided figure of 11–20%. Those differences are below the 20% gate on both measures and change nothing.
The differences that could matter are:
- 9 accounts where the broker band would change;
- 4 accounts that would cross the gate (ACC-048, 078, 111, 120);
- 5 accounts where the tier would change (ACC-002, 011, 074, 113, 128).

> **Correction (Stage 3.1):** this section originally said all four gate-crossers would still score Low and that no segment would change. That was wrong. With the implied percentage, ACC-078 and ACC-111 score Medium and would move from Long-Tail Automated Nurture to Cost-to-Serve / Low-Touch (£1,958 combined). The full check in Stage 3.1 found 18 material inconsistencies, 10 tier changes and 2 segment changes. No Key or Core account changes segment.
→ *Recommend* flagging only differences that change the band or the gate.

**9. The pilot rule has one soft spot.**
ACC-020 qualifies on 3 orders, only 1 of them manual. Its provided broker reliance is 48%, but the order counts give 33%, which makes its dependency evidence the weakest in the cohort.
Also, an absolute count of self-serve orders admits ACC-036 (9 of 37 orders, 24%) but excludes ACC-034 (1 of 4, 25%).
→ *Recommend* treating a material broker inconsistency as grounds for manual review before inclusion. That would drop the cohort to 9 accounts. Also note that **10 accounts are too few for a controlled test**: define a comparison group, or match accounts in pairs, before calling it an experiment.

---

## G. Files Changed

**`Fleek_Dependency_Scoring.xlsx`** (updated in place). Tab order is now: Assumptions, Segment Summary, Segmentation, Pilot Cohort, Summary, Commercial Summary, Commercial View, Scored Accounts, Interesting Accounts, Data Quality.

| Tab | Change |
|---|---|
| **Segmentation** | **New.** One row per account with every field you specified: `behavioural_segment`, Commercial Value Tier, H1/H2, Momentum, `action_segment`, `migration_pilot_eligible`, the rules-matched check, five flag columns, implied broker % and gap, and a combined flags text column. All are formulas. |
| **Segment Summary** | **New.** Validation checks (with an all-pass cell), behavioural table, behavioural × value table, action-segment table with medians and breakdowns by behaviour, value and momentum, pilot totals, and data-quality flag counts |
| **Pilot Cohort** | **New.** All 22 Migration Candidates with a live eligibility result, the reason for any exclusion and their metrics |
| **Assumptions** | **Modified.** Added pilot minimums (3 orders, 2 self-serve orders) and the inconsistency threshold (10 pts), plus notes on the critical blocker and on February. Momentum label clarified. |
| **Commercial View** | **Modified.** Momentum formula now uses a strict "less than −20%" for Declining, per the spec. No results changed. |
| **Data Quality** | **Modified.** Four rows added: February completeness, "New in H2" versus tenure, broker % crossing the gate, and broker % changing the tier |
| Scored Accounts, Summary, Commercial Summary, Interesting Accounts | Unchanged in logic |

**New file:** `Fleek_Segmentation_Report.md` (this report), saved in your Job Search folder and in the project.
**Source dataset:** not modified.
