# Fleek Retention Case Study: Self-Serve Dependency Score

**Scope:** identifying and classifying broker-reliant accounts only. There is no app, dashboard or GMV-based prioritisation at this stage.
**Source:** `Fleek - Retention Case Study - Portfolio Data.xlsx`, `Accounts` tab (300 accounts, Sep 2025 to Feb 2026).
**Companion file:** `Fleek_Dependency_Scoring.xlsx`. Every score in it is a live formula driven by an Assumptions tab.

---

## Headline

The proposed 50/30/20 score ranks broker-led accounts sensibly. **The flaw is in how the score is built, not in the weights.** Low app use and zero offers add up to 50 points even when an account has never had an order placed by an AM. As a result, **79 of the 93 "Medium" accounts have zero AM-placed orders.** Forty-one of those are Self Serve accounts with 0% broker reliance. They are dormant or low-engagement accounts, not broker-dependent ones.

**Fix:** add one gate. If broker reliance is 20% or lower, the account is not broker-led and its score is 0. The weights stay as they are.

| Recommended result | Accounts | % of accounts | % of 6m GMV |
|---|---:|---:|---:|
| High Dependency (≥70) | 64 | 21.3% | 72.2% |
| Medium Dependency (40–69) | 14 | 4.7% | 10.9% |
| Low / Not broker-led (<40) | 222 | 74.0% | 17.0% |

---

## 1. Dataset & Data Quality

**Structure.** The file has three tabs: `Accounts` (300 × 27, used here), `new_accounts` (50 rows for a later batch run) and `Readme` (a column dictionary). Every account has a unique ID, and there are no duplicate rows. The split is 210 Account Managed (ACC-001 to 210) and 90 Self Serve (ACC-211 to 300). Numeric fields are integers, apart from `gmv_trend_pct`. The source file was not modified.

**Issues found (the first two matter most):**

| # | Issue | Evidence | Handling |
|---|---|---|---|
| 1 | **`broker_reliance_pct` does not reconcile to the order counts**, although the Readme says `manual_orders` is "the count behind" it | 157 of 300 rows differ by more than 2 points from manual ÷ (manual + self-serve). ACC-011 has 1 manual order and 0 self-serve but shows 50%. ACC-002 has 1 of each (should be 50%) but shows 70%. Recomputing from the counts would move 21 accounts to a different band. | Used the % as given, since your brief makes the file the source of truth. **Ask the data owner which figure is authoritative.** |
| 2 | **AM accounts with zero manual orders still show 1–20% broker reliance** | 122 AM accounts have 0 manual orders but broker % between 0 and 20. All 90 Self Serve accounts are exactly 0. | Read as a noise floor. The recommended gate treats ≤20% as "no meaningful broker use". |
| 3 | Broker % is **bimodal** | 218 accounts sit at 0–20%, 4 at exactly 20%, **none at 21–39%**, and 78 at 41–84% | The 20–40 band is empty in this batch. It is kept for future batches. |
| 4 | Very thin order histories | 158 of 300 accounts have 1 order. 15 broker-led accounts have ≤2 orders, so their broker % rests on one or two events. | Low-confidence flag. They are not excluded. |
| 5 | ACC-005 is marked `account_status = "Duplicate"` | No matching record found by persona, country, tenure or GMV | Kept and scored (Medium, £24.6k). **Do not contact until verified.** |
| 6 | `account_status` blank | 134 rows (all Self Serve plus 44 AM). The only values present are Active and Duplicate. | Not used |
| 7 | `gmv_trend_pct` blank | 150 rows, which are exactly the rows where `gmv_sep = 0` (division by zero) | Not used |
| 8 | GMV rounding | 38 rows where the monthly sum is off by £1–2 from `gmv_total_6m` | Immaterial |
| 9 | **Ambiguous: does `app_active_days_6m` include web?** | 7 accounts have self-serve orders but 0 app days. ACC-218 has 4 self-serve orders, 0 app days and 0 product-page views. | Flagged. If web use isn't counted, the app sub-score overstates dependency for web buyers. |
| 10 | `new_accounts` overlap | 5 IDs already exist in Accounts (ACC-006, 008, 048, 211, 214) | Out of scope for now. Relevant to the batch-update stage. |

---

## 2. Variable Analysis

| | Broker reliance % | App active days (6m) | Make-an-offer (6m) |
|---|---:|---:|---:|
| Min | 0 | 0 | 0 |
| Q1 | 0 | 3.75 | 0 |
| Median | 11 | 7 | 1 |
| Mean | 22.1 | 13.3 | 2.9 |
| Q3 | 48 | 16 | 2 |
| Max | 84 | 113 | 71 |

**Broker reliance %.** The distribution is strongly bimodal. There are 92 accounts at 0% and 126 at 1–19% (every one of those is Account Managed), then a gap, then 78 accounts between 41% and 84%. Among Account Managed accounts the median is only 17%, and **122 of the 210 AM accounts (58%) had no AM-placed orders at all** in the window. The top band is thin: 13 accounts are at 80% or above, and the maximum is 84%.

**App active days.** Right-skewed. By the brief's bands: 0–4 days = 103 accounts, 5–9 = 81, 10–19 = 53, 20–30 = 32, >30 = 31. Account Managed and Self Serve accounts look almost identical (medians 7 and 8), so **ownership says little about platform usage.**

**Make-an-offer.** 0 offers = 117 accounts (39%), 1 = 81 (27%), 2 = 33 (11%), 3–4 = 23 (8%), 5+ = 46 (15%). The spread is long-tailed, with a few power users (maximum 71).

**The important cluster.** All 78 accounts with broker reliance of 40% or more have **8 or fewer app days and 2 or fewer offers** (offers: 15 at 0, 46 at 1, 17 at 2). They account for **83% of portfolio GMV**. Low engagement is therefore a defining trait of broker-led accounts. The reverse does not hold: plenty of accounts with no broker use also have low engagement. Broker % correlates only weakly with app days (Spearman −0.27) and not at all with offers (0.00). It correlates strongly with tenure (0.72), which means the dependent accounts are older, established customers.

---

## 3. Scoring Methodology

Each variable is converted to a 0–100 sub-score, where higher means more dependent:

| Sub-score | 0 | 25 | 50 | 75 | 100 |
|---|---|---|---|---|---|
| Broker reliance % | ≤20%* | 21–39% | 40–59% | 60–79% | ≥80% |
| App active days | >30 | 20–30 | 10–19 | 5–9 | 0–4 |
| Offers made | 5+ | 3–4 | 2 | 1 | 0 |

\*The brief said <20%. See section 7. The brief also left the boundaries at exactly 40, 60 and 80 undefined. I assigned each boundary value to the higher band (for example, 80% scores 100). This affects 3 accounts.

**Score = 0.5 × Broker + 0.3 × App + 0.2 × Offer**, **gated**: if broker reliance is ≤20%, the score is 0.
GMV is excluded, as you specified.

---

## 4. Portfolio Classification

**The brief as proposed (no gate, <20% band):**

| Tier | Accounts | % |
|---|---:|---:|
| High (≥70) | 64 | 21.3% |
| Medium (40–69) | 93 | 31.0% |
| Low (<40) | 143 | 47.7% |

**This Medium tier is not a real segment.** 79 of its 93 accounts have **zero manual orders**, 71 have made just one order, and 40 have been customers for less than 6 months, which caps how many app days they could have logged. They reach 50 points purely through low activity. With the brief's weights, an account with no broker use can score at most 50, so the Medium threshold of 40 lets them in automatically.

**Recommended (gated):**

| Tier | Accounts | % | % GMV | AM / Self Serve |
|---|---:|---:|---:|---|
| High | 64 | 21.3% | 72.2% | 64 / 0 |
| Medium | 14 | 4.7% | 10.9% | 14 / 0 |
| Low | 222 | 74.0% | 17.0% | 132 / 90 |

The High tier does not change at all. Every Medium account now uses a broker for 40–59% of its orders. The distribution looks lopsided, but it matches the data: the portfolio really is split between 78 broker-led accounts and 222 that are not. I don't recommend adjusting thresholds to make Medium larger.

---

## 5. Benchmark Against the Original Binary Definition

The benchmark reproduces exactly: **14** accounts meet all four conditions and **45** meet exactly three.

**The original 14 under the new score:** 10 High and 4 Medium, with none Low.
The 4 Medium accounts (ACC-020, 058, 062, 035) have broker reliance of 47–55% and 5–7 app days, so they score 67.5, just under 70. They are partially broker-led rather than fully dependent. ACC-020 is also weak evidence: only 1 of its 3 orders was manual, which works out at 33% from the counts even though the file shows 48%.

**The 45 near-misses:** 35 High, 9 Medium, 1 Low. The failed condition was **offers > 0 for 43 of them**, GMV ≤ £2k for 1 and broker ≤ 40% for 1.

**What the binary definition missed:** 64 accounts with broker reliance of 40% or more fell outside the 14.
- 63 of them were excluded **at least partly because they made 1 or 2 offers in six months**. Forty-three failed on offers alone and 20 failed on both offers and GMV.
- 1 was excluded on GMV alone (ACC-074: 70% broker, 0 offers, £1,448).
- Under the new score, 54 of these are High.

**Main takeaway:** the `offers = 0` condition did most of the excluding. It treated one offer in six months as proof of self-serve behaviour. ACC-006 (84% broker, 3 app days, £23k) and ACC-009 (24 manual orders, 1 app day, £18.7k) were both excluded because they had made a single offer.

**Scored lower despite meeting the old definition:** the 4 Medium accounts above. In both approaches, the GMV > £2k condition was holding back dependency judgements that should not depend on value. 20 High-dependency accounts have GMV of £2k or less.

**Surprising result:** ACC-042 was a near-miss under the old definition and scores 50 (Medium) under the brief as proposed. It has **zero manual orders**. It is a one-order, £3.5k account that barely uses the app. That is a dormancy problem, not a dependency problem.

---

## 6. Interesting Accounts

| Cat. | Account | GMV 6m | Orders (manual) | Broker % | App days | Offers | Score | Why it matters |
|---|---|---:|---|---:|---:|---:|---:|---|
| A | ACC-008 | £19.3k | 16 (13) | 84 | 4 | 0 | 100 | Highest possible sub-score on every variable |
| A | ACC-014 | £11.7k | 27 (22) | 81 | 5 | 0 | 92.5 | A long, consistent history of AM-placed orders |
| A | ACC-006 | £23.2k | 14 (12) | 84 | 3 | 1 | 95 | Strongly dependent; excluded from the old 14 for one offer |
| B | ACC-105 | £710 | 1 (1) | 82 | 4 | 1 | 95 | Scores as dependent, but tiny and low confidence |
| B | ACC-123 | £454 | 3 (2) | 70 | 4 | 1 | 82.5 | Dependent but low value, so a cost-to-serve case rather than a revenue case |
| B | ACC-077 | £1.4k | 5 (4) | 81 | 4 | 1 | 95 | Scores 95 on under £1.5k of GMV |
| C | ACC-001 | £170.1k | 46 (32) | 69 | 3 | 0 | 87.5 | 20% of portfolio GMV. Any migration here is a key-account decision. |
| C | ACC-003 | £41.0k | 36 (27) | 74 | 1 | 2 | 77.5 | High value, clearly dependent; old definition excluded it for 2 offers |
| C | ACC-002 | £70.6k | 2 (1) | 70 | 2 | 2 | 77.5 | **Low confidence**: £70k from 2 orders, and the counts give 50%, not 70% |
| D | ACC-009 | £18.7k | 35 (24) | 68 | 1 | 1 | 82.5 | Excluded by the old definition for making 1 offer |
| D | ACC-016 | £11.3k | 26 (18) | 68 | 1 | 1 | 82.5 | Excluded for 1 offer |
| D | ACC-017 | £11.0k | 37 (29) | 78 | 4 | 1 | 82.5 | Excluded for 1 offer |
| D | ACC-074 | £1.4k | 2 (1) | 70 | 8 | 0 | 80 | Excluded only because GMV was under £2k |
| E | ACC-051 | £3.0k | 7 (1) | 12 | 113 | 4 | 0 | Account Managed, yet has the most app days in the portfolio (and 2,403 product-page views) |
| E | ACC-072 | £1.5k | 5 (1) | 20 | 77 | 17 | 0 | Account Managed; 4 of 5 orders self-serve, 17 offers |
| E | ACC-025 | £5.0k | 8 (1) | 8 | 59 | 5 | 0 | Account Managed; 7 of 8 orders self-serve |
| Flag | ACC-005 | £24.6k | 14 (7) | 50 | 8 | 1 | 62.5 | Status is "Duplicate"; verify before any action |

**On E:** being Account Managed is an assignment, not a behaviour. 132 of the 210 AM accounts are not broker-led under this method. For these accounts the question is whether they need an AM at all, not how to migrate them.

**On B vs C:** there are 17 High accounts under £1.5k GMV and 14 High accounts at £10k or more (together 55.5% of GMV). Dependency is equally high in both groups, but the commercial response should be completely different. That supports keeping GMV out of this score and using it in the Migration Priority Score instead.

---

## 7. Methodology Assessment

**The weights hold up. The design needed one change, and the bands need two small fixes.**

**Weight sensitivity (brief's bands, no gate):**

| Weights | High | Medium | Low | Medium with 0 broker sub-score | Max score with 0 broker | Rank corr. vs 50/30/20 within broker-led |
|---|---:|---:|---:|---:|---:|---:|
| 50/30/20 | 64 | 93 | 143 | 77 | 50 | 1.00 |
| 60/25/15 | 55 | 63 | 182 | 38 | 40 | 0.996 |
| 50/25/25 | 50 | 102 | 148 | 72 | 50 | 0.990 |
| 40/30/30 | 64 | 125 | 111 | 109 | 60 | 0.981 |
| Broker only | 54 | 24 | 222 | 0 | 0 | — |

1. **No weighting fixes the leakage.** Moving weight towards engagement (40/30/30) makes it worse. 60/25/15 only reduces it. The cause is structural: the score is additive, so engagement alone can produce a mid-range score. A gate solves that directly and is easy to explain.
2. **Within the broker-led group, the weights barely change the ranking** (correlation of 0.98 or higher). Because every broker-led account has ≤8 app days and ≤2 offers, the app and offer sub-scores only take the values 75/100 and 50/75/100 within that group. In practice broker % sets the tier, and app and offer activity separate borderline cases (40–59% broker → Medium or High). That is the right role for them. 50/30/20 gives the finest resolution (13 distinct score levels, against 7 for 50/25/25), so **keep it**.
3. **Change the broker 0-band to ≤20%.** Four accounts sit at exactly 20%, and three of them have **no manual orders**. One of those, ACC-171, scores 62.5 (Medium) under the <20% rule.
4. **Keep the app and offer bands as absolute cut-offs**, not percentiles, so a new batch is scored on the same scale. Be aware that in this data the bands above 10 days and above 2 offers only ever apply to non-broker accounts, which the gate removes.
5. **Tier thresholds 70 / 40 are acceptable once the gate is in place.** After gating, no score falls between 0 and 62.5, so the 40 threshold now marks where broker use begins rather than splitting the dormant accounts from the rest.
6. **Weak spots to own in an interview:**
   - broker % rests on 1–2 orders for 15 accounts;
   - broker % disagrees with the order counts for 157 rows;
   - app days may miss web usage;
   - a 6-month window penalises accounts younger than 6 months, although none of the broker-led accounts is younger than 6 months.
   None of these changes the conclusions. All of them should be flagged rather than hidden.

**What happens to the 222 Low accounts:** 87 of them are low-engagement non-broker accounts (Engagement gap ≥75) (45 AM, 42 Self Serve). They are not dependent, but they are candidates for the self-serve growth workstream. The workbook keeps an **Engagement gap** field (app and offer sub-scores reweighted to 0–100) so this signal is available at the next stage.

---

## 8. Recommended Final Methodology

```
Broker sub-score (B):  ≤20% → 0 | 21–39 → 25 | 40–59 → 50 | 60–79 → 75 | ≥80 → 100
App sub-score (A):     >30 days → 0 | 20–30 → 25 | 10–19 → 50 | 5–9 → 75 | 0–4 → 100
Offer sub-score (O):   5+ → 0 | 3–4 → 25 | 2 → 50 | 1 → 75 | 0 → 100

Self-Serve Dependency Score = 0                          if broker reliance ≤ 20%
                            = 0.5·B + 0.3·A + 0.2·O      otherwise

High ≥ 70  |  Medium 40–69  |  Low < 40
Flags (not score inputs): Low confidence if orders_6m ≤ 2 · Engagement gap = (0.3·A + 0.2·O) / 0.5
```

**Two-minute verbal version:**
> "The score asks one question: how much does this customer rely on our AMs to buy? First, a gate: if fewer than about one in five of their orders are placed by an AM, they aren't broker-dependent, full stop. Low app use for those customers is an activation problem, which we handle separately. For everyone else, half the score comes from how much of their buying goes through an AM, and the other half checks whether they are doing anything themselves: 30% for how often they open the app, 20% for whether they make offers. Each is banded 0 to 100 so anyone can check the maths. Seventy or above is High dependency. That gives 64 accounts, 21% of the book but 72% of GMV, all Account Managed. Fourteen are Medium: roughly half their orders go through an AM, with some sign of self-use. GMV is deliberately left out. A £450 account and a £170k account can be equally dependent. What to do about each is a separate priority score."

**Before the next stage:** confirm (1) whether the broker % or the order counts are authoritative, (2) whether app days include web use, and (3) what ACC-005's "Duplicate" status refers to.
