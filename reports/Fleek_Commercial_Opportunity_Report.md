# Fleek Retention Case Study: Commercial Opportunity Analysis

**Question:** How commercially important is it for Fleek to successfully influence this customer's behaviour?
**Scope:** understanding only. There is no Migration Priority Score yet, and dependency and value are not combined into a single number.
**Source:** `Accounts` tab (300 accounts, Sep 2025 to Feb 2026). The source file was not modified.
**Carried forward:** the gated Self-Serve Dependency Score (64 High / 14 Medium / 222 Low).
**Companion workbook:** `Fleek_Dependency_Scoring.xlsx`, which now includes a **Commercial View** tab (per account) and a **Commercial Summary** tab. Both use live formulas, and the thresholds are on the Assumptions tab.

---

## Headline

1. **The portfolio is extremely concentrated.** The Gini coefficient is 0.81. One account (ACC-001) is 20% of GMV, the top 10 are 51%, and the top 50 are 82%. The bottom 150 accounts together are 3.6%.
2. **Broker dependency sits almost entirely in the valuable part of the book.** The 78 High and Medium Dependency accounts are 26% of accounts but **83% of GMV**. Setting ACC-001 aside does not change the picture: High Dependency accounts still hold 65% of the remaining GMV. This is a correlation, not a causal link.
3. **`gmv_trend_pct` is not fit for purpose.** It is simply (Feb − Sep) ÷ Sep, which I confirmed on all 150 populated rows. It is blank for half the portfolio. 77% of the populated values are −100%, and in 22 of 150 cases it gives the wrong direction of travel. **Do not use it in any score.**
4. **Among accounts that are both high-value and dependent, most are shrinking.** In the higher-dependency / higher-value quadrant (57 accounts, **80.5% of GMV**), 33 accounts are declining or have lapsed when you compare Dec–Feb with Sep–Nov. For many of these, the first conversation has to be about retaining them, not about moving them to self-serve.

---

## 1. Commercial Variables: What Is Usable

| Variable | Behaviour | Usable? |
|---|---|---|
| `gmv_total_6m` | Complete, from £7 to £170,132 | **Yes**. This is the core value measure. |
| `gmv_sep` … `gmv_feb` | Complete. Sums to the total within £1–2 (rounding). | **Yes**. They are needed to rebuild trend and recency. |
| `gmv_trend_pct` | (Feb − Sep) ÷ Sep. Blank for 150 rows. | **No** (section 5) |
| `orders_6m` | 158 accounts (53%) have 1 order | Yes, as a confidence check (Spearman correlation with GMV = 0.80) |
| `tenure_months` | 154 accounts have been customers for ≤6 months | Context only. Accounts older than 6 months hold 88% of GMV. |
| `account_status` | Active 165, blank 134, "Duplicate" 1 | Weak. ACC-005 ("Duplicate") is the **5th-largest account (£24.6k)**. |
| `buyer_persona` | 279 Resellers, 21 Retailers | Context. Retailers are 7% of accounts but 28% of GMV, mostly because of ACC-001. |
| `region` / `country` | UK has 135 accounts and 46% of GMV. ROW has 7 accounts with the highest median (£3.3k). | Context only for now |

**Caveat on the window:** six months of GMV is lumpy. 180 accounts (60%) spent in only one month. That means an account's 6-month value can depend on a single order. ACC-002 is £70.7k from 2 orders and ACC-011 is £15.6k from 1 order.

---

## 2. GMV Distribution

| Stat | Value |
|---|---:|
| Total | £845,401 |
| Min | £7 |
| Q1 | £195 |
| Median | £392 |
| Mean | £2,818 |
| Q3 | £1,688 |
| 90th / 95th percentile | £4,643 / £11,493 |
| Max | £170,132 |

The distribution is heavily right-skewed: the mean is 7× the median, and 75% of accounts spent less than £1.7k.

**The bands from the brief:**

| Band | Accounts | % accts | GMV | % GMV | High+Med dependency |
|---|---:|---:|---:|---:|---:|
| <£1k | 201 | 67.0% | £62.6k | 7.4% | 10 |
| £1k–2k | 30 | 10.0% | £42.6k | 5.0% | 11 |
| £2k–5k | 42 | 14.0% | £143.4k | 17.0% | 33 |
| £5k–10k | 9 | 3.0% | £59.7k | 7.1% | 7 |
| £10k–25k | 14 | 4.7% | £228.1k | 27.0% | 13 |
| £25k–50k | 2 | 0.7% | £68.1k | 8.1% | 2 |
| £50k+ | 2 | 0.7% | £240.8k | 28.5% | 2 |

**Assessment:** seven bands are too many for this portfolio.
- The top two bands contain 2 accounts each. At that size they are individual named accounts, not segments.
- The £5k–10k band has only 9 accounts.
- The £1k–2k band is a transition zone.

A natural-breaks test on log GMV puts the upper break at **about £3k**, and a two-group split lands at about £900. So the data points to a value line somewhere between £1k and £3k.

**Recommended value tiers for the next stage:**

| Tier | Rule | Accounts | % GMV | High+Med dependency |
|---|---|---:|---:|---:|
| Key | ≥ £10k | 18 | 63.5% | 17 |
| Core | £2k–£10k | 51 | 24.0% | 40 |
| Tail | < £2k | 231 | 12.5% | 21 |

---

## 3. Concentration

| Top N accounts | Share of GMV | Smallest account in group |
|---|---:|---:|
| Top 1 | 20.1% | £170.1k |
| Top 5 | 39.4% | £24.6k |
| Top 10 | 51.3% | £17.0k |
| Top 20 | 65.6% | £8.6k |
| Top 50 | 81.6% | £3.4k |

**Among dependent accounts:**

| Segment | Accounts | Total GMV | % portfolio GMV | Mean | Median |
|---|---:|---:|---:|---:|---:|
| High Dependency | 64 | £610.0k | 72.2% | £9,531 | £3,492 |
| Medium Dependency | 14 | £91.9k | 10.9% | £6,562 | £3,619 |
| Low / Not broker-led | 222 | £143.5k | 17.0% | £646 | £287 |

GMV is also concentrated within the High group: its top 5 accounts are 54% of the group's GMV, and its top 14 are 77%.

**Of the top 20 accounts by GMV, 18 are broker-led.** The two exceptions are ACC-211 (£13.4k) and ACC-212 (£8.6k), both Self Serve power users.

---

## 4. Is Dependency Concentrated Among High-Value Customers?

**Yes.**
- The median dependent account spends about **12× the median non-dependent account** (£3.5k–£3.6k against £287).
- 17 of the 18 Key accounts are High or Medium Dependency.
- Among Tail accounts, 21 of 231 are.
- Across the portfolio, dependency score and GMV have a Spearman correlation of 0.66.

**What this does not show:** it does not show that dependency *causes* higher spend, or the reverse. Dependency, GMV, order count and tenure all move together: broker-led accounts are older and order more often. The most plausible reading is that Fleek assigns AMs to, and brokers for, the accounts that are already large. That is a selection effect, and this data cannot separate it from any other explanation.

**Implication:** migration is not a way to trim the tail. Migrating dependent accounts means changing how Fleek's most important revenue is bought, so the downside risk sits squarely on the accounts that matter most.

---

## 5. How `gmv_trend_pct` Behaves

**Definition, reverse-engineered:** `ROUND((gmv_feb − gmv_sep) / gmv_sep × 100)`. This matches all 150 populated rows exactly. The field is blank whenever `gmv_sep = 0`.

| | Value |
|---|---:|
| Populated / blank | 150 / 150 |
| Min / max | −100% / +833% |
| Median / mean | −100% / −67.8% |
| Exactly −100% | 115 (77% of populated) |
| −99% to −50% | 7 |
| −50% to −10% | 10 |
| −10% to +10% (flat) | 3 |
| +10% to +50% | 7 |
| > +50% | 8 (3 above +200%) |

**Why it misleads:**
- **It compares two single months** and ignores October to January. Monthly GMV is lumpy, so an empty February reads as −100%.
- **−100% does not mean churn.** It only means no GMV in February. 17 of the 115 accounts bought in December or January, and 59 of them are one-order accounts that bought only in September.
- **Blank does not mean no trend.** The 150 blank rows include 26 multi-month accounts that are clearly growing (13), declining (7) or stable (6). ACC-019 is an example: £639 → £3,723 per month, with no trend shown.
- **The direction is wrong in 22 of 150 cases**, and in 9 of them the sign is reversed:
  - ACC-001 shows +67%, but its Dec–Feb GMV is 18% below Sep–Nov.
  - ACC-013 shows +61%, but H2 is down 56%.
  - ACC-016 shows −100%, but H2 is up 67%.
- **We can't tell whether February is a complete month.** If the extract was taken mid-February, every February-based figure is understated. **Confirm with the data owner.**

**Replacement used here (Commercial View tab):** H2 (Dec–Feb) against H1 (Sep–Nov), using all six months.
- **Growing:** H2 at least 20% above H1
- **Stable:** within ±20%
- **Declining:** H2 more than 20% below H1
- **Lapsed:** no GMV in Dec–Feb
- **New:** no GMV in Sep–Nov

Two supporting fields go with it: **months with GMV** and **last month with GMV**.

Accounts with only one active month can only be classified as New or Lapsed. Treat momentum as reliable only where there are at least 2 active months.

| Momentum | Accounts | % GMV | High+Med dependency |
|---|---:|---:|---:|
| Growing | 29 | 16.5% | 14 |
| Stable | 15 | 32.3% | 13 |
| Declining | 34 | 25.4% | 26 |
| Lapsed | 149 | 19.9% | 20 |
| New in H2 | 73 | 5.9% | 5 |

Twenty dependent accounts have lapsed, with their last GMV in September (6), October (7) or November (7).

---

## 6. Extreme Trends: What They Actually Represent

Monthly GMV is shown in £ for Sep | Oct | Nov | Dec | Jan | Feb.

**Very high positive growth**

| Account | Monthly GMV | 6m GMV | Trend | H2 vs H1 | Orders | Dep. score / tier | Reading |
|---|---|---:|---:|---:|---:|---|---|
| ACC-029 | 203 · 293 · 0 · 0 · 2,123 · 1,895 | £4.5k | +833% | +710% | 5 | 80 High | A genuine step-up from a tiny September base. Real growth, but a £4.5k account; the 833% says more about the £203 base than the opportunity. |
| ACC-025 | 150 · 0 · 0 · 4,089 · 82 · 694 | £5.0k | +363% | +3,143% | 8 | 0 Low | The growth is one £4k December order. February is still only £694. It is lumpy, not a trend. |
| ACC-083 | 148 · 148 · 0 · 0 · 359 · 562 | £1.2k | +280% | +211% | 8 | 0 Low | Real direction, trivial value (£1.2k in total). |

**Strong positive growth (>+50%)**

| Account | Monthly GMV | 6m GMV | Trend | H2 vs H1 | Orders | Dep. score / tier | Reading |
|---|---|---:|---:|---:|---:|---|---|
| ACC-001 | 27,469 · 41,827 · 24,249 · 20,463 · 10,300 · 45,824 | £170.1k | +67% | **−18%** | 46 | 87.5 High | The "growth" is one strong February. Over the whole half-year the account is flat to slightly down. |
| ACC-013 | 1,643 · 3,907 · 4,416 · 1,703 · 0 · 2,647 | £14.3k | +61% | **−56%** | 21 | 62.5 Medium | The trend points the wrong way. This account is declining. |
| ACC-021 | 717 · 568 · 2,581 · 872 · 343 · 1,117 | £6.2k | +56% | **−40%** | 19 | 75 High | Same pattern: the field says growth, the fuller picture says decline. |

**Strong negative (−99% to −50%)**

| Account | Monthly GMV | 6m GMV | Trend | H2 vs H1 | Orders | Dep. score / tier | Reading |
|---|---|---:|---:|---:|---:|---|---|
| ACC-008 | 5,080 · 3,329 · 4,049 · 6,095 · 0 · 713 | £19.3k | −86% | −45% | 16 | 100 High | Real decline, but less severe than −86% suggests, and December was the account's best month. A Key account that is fully dependent and declining: a **retention risk**. |
| ACC-017 | 3,693 · 3,067 · 951 · 0 · 2,899 · 339 | £11.0k | −91% | −58% | 37 | 82.5 High | Declining, but still ordering. |
| ACC-055 | 1,610 · 399 · 212 · 0 · 194 · 99 | £2.5k | −94% | −87% | 12 | 70 High | A steady fade across the whole window. Small, but a clear pattern. |

**Exactly −100%**

| Account | Monthly GMV | 6m GMV | Trend | H2 vs H1 | Orders | Dep. score / tier | Reading |
|---|---|---:|---:|---:|---:|---|---|
| ACC-002 | 36,244 · 34,406 · 0 · 0 · 0 · 0 | £70.7k | −100% | Lapsed | 2 | 77.5 High (low confidence) | Two large orders, then nothing for four months. The **biggest single retention risk** in the book. This data can't tell whether it is churn or a buyer who purchases infrequently. |
| ACC-015 | 7,711 · 1,040 · 2,730 · 0 · 0 · 0 | £11.5k | −100% | Lapsed | 8 | 75 High | A Key account with no GMV since November. Retention risk. |
| ACC-016 | 1,496 · 2,370 · 351 · 4,431 · 2,604 · 0 | £11.3k | −100% | **+67%** | 26 | 82.5 High | A false alarm. December and January were the account's strongest months, and only February is empty. |
| ACC-208 | 53 · 0 · 0 · 0 · 0 · 0 | £53 | −100% | Lapsed | 1 | 0 Low | A one-off £53 purchase. The −100% carries no commercial meaning. |

---

## 7. Dependency × Commercial Value (2×2)

**Value threshold: £2,000 of 6-month GMV.** Why £2k:
- It sits inside the £1k–£3k range where the data suggests a break.
- The 69 accounts above it hold 87.5% of GMV. Below it, the median account is about £300.
- It matches the GMV line in your original binary definition, which keeps the story consistent.

**Dependency axis:** Higher = High or Medium (score ≥40, so every one of these accounts is broker-led). Lower = Low.

|  | **Lower value (<£2k)** | **Higher value (≥£2k)** |
|---|---|---|
| **Lower dependency** | **210 accounts · £83.9k · 9.9% GMV**<br>Median £273. 154 have a single order. 83 are Self Serve.<br>126 lapsed, 66 new in H2.<br>*e.g. ACC-208 (£53, one order), ACC-202 (£85)* | **12 accounts · £59.6k · 7.1% GMV**<br>Mostly self-serve power users (7 Self Serve, 5 AM).<br>*e.g. ACC-211 (£13.4k, 100 app days, 71 offers, declining), ACC-212 (£8.6k, growing), ACC-025 (AM, £5.0k, 59 app days)*<br>→ The "grow self-serve spend" population, not a migration one. |
| **Higher dependency** | **21 accounts · £21.4k · 2.5% GMV**<br>20 High, 1 Medium. Median £1,071.<br>**11 low-confidence, 12 lapsed.**<br>*e.g. ACC-105 (£710, 1 order, score 95), ACC-123 (£454, score 82.5)*<br>→ A cost-to-serve question, and several may already be gone. | **57 accounts · £680.5k · 80.5% GMV**<br>44 High, 13 Medium. Median £4.4k. All Account Managed.<br>17 Key (≥£10k), 40 Core.<br>**25 declining, 8 lapsed, 12 growing, 10 stable, 2 new.**<br>*e.g. ACC-001, ACC-003, ACC-006, ACC-008, ACC-009, ACC-010* |

**How much the quadrant moves if the threshold moves:**

| Threshold | Dependent + higher value | % GMV |
|---|---:|---:|
| £1k | 68 | 82.3% |
| £1.5k | 60 | 81.1% |
| **£2k** | **57** | **80.5%** |
| £3k | 46 | 77.4% |
| £5k | 24 | 67.4% |

Between £1k and £3k the quadrant's share of GMV barely changes, so the conclusion does not depend on the exact threshold. Only at £5k does it narrow to a Key-account list.

**Where are the accounts that are both highly dependent and commercially significant?**
They are the 57 accounts in the bottom-right quadrant: all Account Managed, 80.5% of GMV. Within it, the 17 Key accounts alone carry 62% of portfolio GMV, and **they cannot be treated as one population**:

| Sub-group inside the quadrant | Accounts | Examples | What it suggests (for the next stage, not a decision) |
|---|---:|---|---|
| Growing or stable | 22 | ACC-001, ACC-003, ACC-004, ACC-006, ACC-007, ACC-012, ACC-016, ACC-019 | The safest place to test a gradual move to self-serve, because the relationship is healthy |
| Declining | 25 | ACC-008, ACC-009, ACC-010, ACC-013, ACC-014, ACC-017 | Stabilise first. Reducing broker contact while spend falls is a risky combination. |
| Lapsed | 8 | ACC-002, ACC-015, ACC-022 | Win-back or a check on whether the account is still alive. Migration doesn't apply yet. |
| New in H2 | 2 | ACC-011 (£15.6k, one order) | Too little history to judge |

**Flags inside this quadrant:**
- ACC-005 is marked "Duplicate" but is the 5th-largest account.
- 4 accounts are low-confidence (≤2 orders), including ACC-002 and ACC-011, which together are £86k.
- 3 accounts have a blank status.

---

## What This Means for the Migration Priority Score (Not Built Yet)

1. **Use `gmv_total_6m` for value, banded into Key / Core / Tail.** Don't use raw £, or ACC-001 swamps everything.
2. **Keep momentum and recency as a separate risk dimension**, and do not fold them into value. A declining Key account and a growing Key account are worth the same today but need opposite approaches.
3. **Drop `gmv_trend_pct`.** Replace it with the H2-vs-H1 comparison, with a minimum of 2 active months.
4. **Carry the confidence flags forward:** accounts with ≤2 orders, and ACC-005.
5. **Questions for the data owner:**
   - Is February a complete month?
   - Is the "Duplicate" status on ACC-005 real?
   - Is 6-month GMV the right value window, or is a 12-month figure available?

---

*Note: your message was cut off partway through Step 7 ("…when we later create Migration Pri…"). This report covers Steps 1–7. If there were further steps or a specific output format, send them and I'll extend it.*
