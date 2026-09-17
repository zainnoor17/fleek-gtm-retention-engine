# Fleek_Next_Best_Action_Report

**Stage 4B:** an account-level Next Best Action (NBA) engine.
- **Design:** transparent rules only. There is no model, no score and no hidden weighting.
- **Scope:** Stages 1–4A are unchanged. The only structural addition is the promoted `rising_tail_watchlist` context flag.
- **Workbook:** `Fleek_Dependency_Scoring.xlsx` has three new tabs: **NBA Engine** (one row per account), **NBA Summary** (the action queue and validation) and **NBA Library** (reason codes, statuses and priorities).
- **Verification:** every output is a live formula, and an independent Python rebuild matches all 300 accounts field by field.

---

## A. Executive Findings

1. **Every account has exactly one recommended action, one execution status and one priority.** All 14 validation checks pass (section L).
2. **"What should happen" is kept separate from "can it happen now".** For example:
   - ACC-001 keeps the recommendation *Guided Self-Serve Migration* but needs *Human Sign-Off*.
   - ACC-005 keeps *Retention Conversation* but is on *HOLD* until its duplicate status is resolved.
3. **Human work is concentrated but manageable.**
   - **75 accounts need a person.** They hold **86.7% of GMV**.
   - **225 accounts can run automatically.** They hold 13.3% of GMV. 215 of them get Automated Nurture.
4. **Revenue protection is the largest human queue.**
   - **P1 covers 39 accounts and 35.5% of GMV.** Every one is a Key or Core account needing a retention conversation (27) or a check on whether it is still buying (12).
   - P2 covers 24 accounts and 47.0% of GMV. This is mostly migration, and £309k of it is the seven Key accounts awaiting sign-off.
5. **Migration has 5 accounts ready to start (£25k).**
   - 5 more need manual review and 7 Key accounts need sign-off.
   - **No Migration Candidate yet meets any self-serve milestone.** All 22 start at *Baseline*.
6. **The recency check changes one growth account.** ACC-216 is labelled "Growing" but has had no GMV since December, so it is routed to a *Verify* check (P1, human) instead of an automated nudge. The other three Growth Opportunity accounts get *Reinforce Successful Behaviour*; none needs a new feature push.
7. **The six Rising Tail accounts do not all get the same action:**
   - Reinforce: ACC-068, 083, 085. ACC-083 and 085 also get an optional handpick trial.
   - Discovery-to-Offer: ACC-219.
   - Nurture until their buying pattern is established: ACC-065, 086.
8. **Retention cases never receive product nudges.** The three accounts that are heavily engaged but shrinking (ACC-211, 214, 051) are sent to a human to look at supply, price or how well they convert. More engagement is not the fix.
9. **The engine never recommends more chat, more video or broad bundle adoption.** A formula checks every target behaviour for this.

---

## B. NBA Rule Architecture

```
Locked inputs (Stages 1-3.1)
  Dependency tier, value tier, momentum, action segment, guardrail flags
        │
        ▼
New context (Stage 4B)
  recent_activity_status · rising_tail_watchlist · discovery gap
  strong self-serve pattern · largest-H2-month share
        │
        ▼
nba_reason_code   (one of 18 codes, chosen by action segment + context)
        │  looked up in the NBA Library
        ▼
primary_nba · delivery_mode · default priority · target_behaviour · success_measure
        │
        ├──► execution_status   (separate guardrail layer; never changes primary_nba)
        ├──► attention_priority (P0-P4)
        └──► secondary_test · nurture_subcontext · guardrail_codes · migration fields
```

**New context rules:**

| Field | Rule |
|---|---|
| `recent_activity_status` | **Recently Active:** January or February GMV above zero.<br>Otherwise **No Meaningful History** if the account has ≤2 orders or only one month with GMV.<br>Otherwise **Recent Inactivity**.<br>A zero February on its own is context only, because February completeness is unconfirmed. |
| `rising_tail_watchlist` | The Stage 4A rule, now shown on the Segmentation tab (column AW). It matches the expected 6 accounts exactly. |
| Discovery gap | Low dependency, 50+ PDP views and fewer than 3 offers |
| Strong self-serve pattern | Low dependency, Growing or Stable, Recently Active, 50+ PDP views, and GMV in 3 or more months |

**How reason codes are assigned, by action segment:**

| Segment | Rule → reason code |
|---|---|
| 1 Migration Candidate | Key → `MIGRATION_KEY_SIGNOFF`<br>Phase 1 Ready → `MIGRATION_PHASE1_READY`<br>Phase 1 Manual Review → `MIGRATION_PHASE1_REVIEW`<br>otherwise → `MIGRATION_PRE_ENTRY` |
| 2 Protect / Retain First | `DECLINING_KEY_CORE` |
| 3 Win-Back / Verify | Established buyer → `LAPSED_ESTABLISHED`<br>thin history → `LAPSED_THIN_HISTORY` |
| 4 Establish / Re-establish / Observe | New customer → `NEW_CUSTOMER`<br>returned customer → `RETURNED_CUSTOMER` |
| 5 Cost-to-Serve | Recently Active → `COST_TO_SERVE_ACTIVE`<br>otherwise → `DORMANT_LOW_VALUE` |
| 6 Growth Opportunity | Recent Inactivity → `RECENT_INACTIVITY`<br>discovery gap → `BROWSING_LOW_OFFERS`<br>otherwise → `HEALTHY_STRONG_SELF_SERVE` |
| 7 Onboard / Re-engage / Learn | Recent Inactivity → `RECENT_INACTIVITY`<br>otherwise → `NEW_CUSTOMER` or `RETURNED_CUSTOMER` |
| 8 Retention / Reactivation | Declining → `ENGAGED_BUT_SHRINKING` (if archetype matches) or `DECLINING_KEY_CORE`<br>Lapsed → established or thin-history code |
| 9 Long-Tail, on Rising Tail watchlist | Not recently active → `DORMANT_LOW_VALUE`<br>discovery gap → `BROWSING_LOW_OFFERS`<br>strong pattern → `RISING_TAIL`<br>otherwise → `RISING_TAIL_EARLY` |
| 9 Long-Tail, other | Discovery gap, Recently Active, Growing/Stable/H2-active and 2+ orders → `BROWSING_LOW_OFFERS`<br>otherwise → `LONG_TAIL_STANDARD` |

**The 18 reason codes map to 8 primary actions.** Range Expansion runs only as a `secondary_test`.

| Reason code | primary_nba | Delivery | Default priority |
|---|---|---|---|
| DECLINING_KEY_CORE, ENGAGED_BUT_SHRINKING | Retention Conversation | Human | P1 |
| LAPSED_ESTABLISHED, LAPSED_THIN_HISTORY, RECENT_INACTIVITY | Verify Demand / Win-Back | Human | P1 |
| MIGRATION_PHASE1_READY / _REVIEW / _KEY_SIGNOFF | Guided Self-Serve Migration | Hybrid | P2 |
| MIGRATION_PRE_ENTRY | Guided Self-Serve Migration | Human | P3 |
| RETURNED_CUSTOMER / NEW_CUSTOMER | Establish / Re-establish | Human / Automated | P2 |
| HEALTHY_STRONG_SELF_SERVE | Reinforce Successful Behaviour | Automated | P2 |
| RISING_TAIL | Reinforce Successful Behaviour | Automated | P3 |
| BROWSING_LOW_OFFERS | Discovery-to-Offer Enablement | Automated | P2 (P3 if Tail) |
| COST_TO_SERVE_ACTIVE | Service Model Review | Human | P3 |
| RISING_TAIL_EARLY | Automated Nurture | Automated | P3 |
| DORMANT_LOW_VALUE, LONG_TAIL_STANDARD | Automated Nurture | Automated | P4 |

**`execution_status` is decided in this order; the first rule that applies wins:**
1. Duplicate status → **HOLD — Critical Data Issue**
2. Key Migration Candidate → **Human Sign-Off Required**
3. Phase 1 Manual Review → **Human Review Required**
4. Automated action where the implied broker % would change the segment, **or** an automated growth nudge (Discovery-to-Offer or Reinforce) on borderline or February-sensitive momentum → **Human Review Required**
5. Otherwise → **Ready — Human / Hybrid / Automated**, according to the delivery mode

Borderline and February flags do *not* trigger review on actions a human already owns. They appear in `guardrail_codes` so that person sees them.

**`attention_priority`:** P0 applies to any critical blocker. Otherwise the library default is used, with two overrides:
- Tail Discovery-to-Offer accounts → P3
- Human Review cases whose default is P4 → P3

**`secondary_test` (Range Expansion)** is only offered when all of these hold:
- low dependency, Growing or Stable, and Recently Active
- a single product type
- primary action is Reinforce or Discovery-to-Offer, with status Ready — Automated
- Key/Core value, or on the Rising Tail watchlist

It is labelled "experimental; not proven to lift GMV".

---

## C. Portfolio Action Queue

| Primary NBA | Accounts | GMV | % GMV | Key / Core / Tail | Segments | Delivery |
|---|---:|---:|---:|---|---|---|
| Guided Self-Serve Migration | 22 | £372.3k | 44.0% | 7 / 15 / 0 | 1 | 17 Hybrid, 5 Human |
| Retention Conversation | 28 | £208.7k | 24.7% | 8 / 20 / 0 | 2 (25), 8 (3) | Human |
| Verify Demand / Win-Back | 12 | £116.3k | 13.8% | 2 / 10 / 0 | 3 (8), 8 (3), 6 (1) | Human |
| Automated Nurture | 216 | £87.3k | 10.3% | 0 / 0 / 216 | 9 (203), 5 (13) | Automated |
| Establish / Re-establish | 4 | £24.3k | 2.9% | 1 / 3 / 0 | 4 (2), 7 (2) | 3 Human, 1 Automated |
| Reinforce Successful Behaviour | 6 | £22.6k | 2.7% | 0 / 3 / 3 | 6 (3), 9 (3) | Automated |
| Service Model Review | 8 | £11.6k | 1.4% | 0 / 0 / 8 | 5 | Human |
| Discovery-to-Offer Enablement | 4 | £2.3k | 0.3% | 0 / 0 / 4 | 9 | Automated |

| Priority | Accounts | GMV | % GMV | What's in it |
|---|---:|---:|---:|---|
| **P0** | 1 | £24.6k | 2.9% | ACC-005 (HOLD) |
| **P1** | 39 | £300.5k | 35.5% | 24 declining broker-led, 3 engaged-but-shrinking, 11 lapsed, ACC-216. All Key/Core; all human. |
| **P2** | 24 | £397.5k | 47.0% | 17 migration (5 Ready, 5 Review, 7 Key), 4 Establish, 3 Growth Reinforce |
| **P3** | 23 | £39.8k | 4.7% | 8 Service Model Review, 5 pre-entry migration, 6 Rising Tail, 3 long-tail Discovery-to-Offer, ACC-078 review |
| **P4** | 213 | £83.0k | 9.8% | Automated nurture |

**P1 and P2 stay a workable size.** Together they are 63 accounts, 21% of the book. Every P1 and P2 account is Key or Core. The full ordered P0–P3 queue is on NBA Summary. Within each priority level, accounts are ordered by value tier and then GMV; no extra score is involved.

---

## D. Human vs Automated Work

| Execution status | Accounts | GMV | % GMV |
|---|---:|---:|---:|
| Ready — Automated | 225 | £112.6k | 13.3% |
| Ready — Human | 55 | £351.6k | 41.6% |
| Ready — Hybrid | 5 | £25.1k | 3.0% |
| Human Review Required | 7 | £22.2k | 2.6% |
| Human Sign-Off Required | 7 | £309.4k | 36.6% |
| HOLD — Critical Data Issue | 1 | £24.6k | 2.9% |

**Human Review Required (7):**
- **Phase 1 Manual Review (5):** ACC-020, 024, 033, 056, 058.
- **ACC-078 (Nurture) and ACC-111 (Discovery-to-Offer):** both are automated actions, but the broker % implied by their order counts would move them into Cost-to-Serve.

**Cautions on automated work:**
- **135 of the 216 Automated Nurture accounts are Account Managed** with no broker use. Automation is appropriate, but their AM coverage should be reviewed alongside it (J).
- **Self Serve accounts on human actions** (e.g. ACC-211, 214, 216) have no AM. The owner needs to be a named customer-success or growth person.

---

## E. Guided Migration Plan

| Group | Accounts | GMV | Status | Buyer cadence |
|---|---|---:|---|---|
| **Phase 1 Ready** | ACC-019, 027, 030, 031, 036 | £25.1k | Ready — Hybrid, P2 | 4 Regular; ACC-036 Lumpy |
| **Phase 1 Manual Review** | ACC-020, 024, 033, 056, 058 | £20.2k | Human Review Required, P2 | 3 Regular; ACC-020, 058 Lumpy |
| **Key sign-off** | ACC-001, 003, 004, 006, 007, 012, 016 | £309.4k | Human Sign-Off Required, P2 | all Regular |
| **Pre-entry** | ACC-029, 034, 039, 049, 057 (only 1 self-serve order each) | £17.5k | Ready — Human, P3 | mixed |

**Why each Manual Review account is on hold:**

| Account | Guardrail codes |
|---|---|
| ACC-020 | Material broker inconsistency, single-month H2 spike |
| ACC-024 | Borderline momentum |
| ACC-033 | Borderline momentum |
| ACC-056 | Borderline momentum, material inconsistency, no February GMV |
| ACC-058 | February-sensitive, single-month H2 spike |

**How it runs:**
1. **Entry.** The Stage 3.1 criteria are unchanged. Having 2 or more self-serve orders shows the customer *can check out*; it is not treated as proof of migration.
2. **Intervention.** Led by the AM, with automated tracking. The focus is **independent discovery** (browsing product pages) and **regular app use**. The AM keeps sourcing and does not withdraw support. Make-an-Offer is encouraged but optional. Chat and video stay available as AM tools; they are not targets.
3. **Key accounts.** Nothing starts without explicit sign-off. ACC-001 and ACC-003 are also borderline and February-sensitive; without February both would read as *Declining*. The sign-off reviewer should expect that approving these two may not be appropriate.
4. **Pre-entry accounts.** The AM encourages a second self-serve checkout, then the account is re-assessed for Phase 1.
5. **Rerun.** Enter the 90-day monitoring data in the yellow input columns on NBA Engine (BC–BI). `migration_progress_status` then updates automatically.

**Migration baselines (all 22 accounts are at Baseline):**

| Account | Status | PDP views (6m) | App days | Offers | Self-serve share | Cadence |
|---|---|---:|---:|---:|---:|---|
| ACC-019 | Ready | 15 | 2 | 1 | 43% | Regular |
| ACC-027 | Ready | 14 | 3 | 1 | 28% | Regular |
| ACC-030 | Ready | 2 | 2 | 0 | 40% | Regular |
| ACC-031 | Ready | 1 | 5 | 1 | 25% | Regular |
| ACC-036 | Ready | 2 | 6 | 1 | 24% | Lumpy |
| Benchmark: repeat self-servers (median) | – | 341 | 30 | 4 | 100% | – |

---

## F. Phase 1 Success Metrics

**Milestones and 90-day targets (all on the Assumptions tab, rows 76–85):**

| Milestone | 6-month reference | 90-day "Progressing" | 90-day "Capability Demonstrated" | Why |
|---|---|---|---|---|
| **M1 Independent discovery** (PDP views) | ≥50 | **≥15** | **≥25** | No Broker-Reliant account reached 15 views in *six* months. Reaching 15 in three months is therefore already a clear break from the broker pattern.<br>25 per 90 days matches the slowest tenth of repeat self-servers (about 52 per 6 months).<br>Halving the 6-month figure happens to give the same 25. |
| **M2 Habitual app use** (app days) | ≥10 | **≥5** | **≥6** | The most active Broker-Reliant account had 8 days in 6 months, about 4 per quarter. A straight halving (5) barely clears that, so capability is set at 6 (roughly every other week).<br>This is weaker evidence because app days are a Dependency Score input. |
| **M3 Self-directed negotiation** (offers) | ≥3 | – | Supportive only (≥2) | Broker-Reliant accounts max out at 2 offers in 6 months, and 32% of repeat self-servers make fewer than 3. It is not required. |
| **M4 Increasing self-serve purchasing** | Baseline self-serve share | – | ≥1 self-serve order in the window **and** self-serve share above baseline | The dataset has no order timestamps, so the trend can't be measured yet. The baseline share is stored for comparison. |

**`migration_progress_status` rules, applied in order:**
1. No monitoring data yet → **Baseline**
2. GMV guardrail breached → **At Risk**
3. M1 ≥25, M2 ≥6, and M4 met → **Self-Serve Capability Demonstrated**
4. M1 ≥15 or M2 ≥5 → **Progressing**
5. 90 days elapsed with no progress → **At Risk**
6. Otherwise → **Baseline** (still within the window)

**`gmv_guardrail` rules:**

| Buyer type | Definition | Rule |
|---|---|---|
| **Regular** | 3+ months with GMV and 5+ orders | Expected 90-day GMV is half the 6-month GMV. From **day 45**, the account is **At Risk** if GMV to date is below **70%** of the pro-rated expectation. |
| **Lumpy** | Everyone else | **No numeric threshold.** At Risk if there is no order within the account's usual gap (6 ÷ months with GMV, rounded). The AM reviews at day 45 and day 90. |

- **Why 70%:** the Stable band already allows ±20%, and the extra 10 points absorb the added noise of a 90-day window compared with 6 months.
- **Not an automatic stop:** the guardrail flags the account for a human decision.
- **Weakness:** it cannot tell migration effects apart from market-wide changes. Compare cohort GMV against the Manual Review and Key accounts that have not been migrated before attributing any decline to the intervention.

---

## G. Growth Opportunity Accounts (Segment 6)

| Account | GMV | Recent activity | Reason code → NBA | Execution | Priority | Why |
|---|---:|---|---|---|---|---|
| **ACC-212** | £8,581 | Active (Jan, Feb) | HEALTHY_STRONG_SELF_SERVE → **Reinforce Successful Behaviour** | Ready — Automated | P2 | A strong independent browser-buyer (612 PDP views, 78 app days, 5 offers, mixed basket). No gap that justifies a new nudge. |
| **ACC-025** | £5,014 | Active (Jan, Feb) | HEALTHY_STRONG_SELF_SERVE → **Reinforce** | Ready — Automated | P2 | Strong browsing (860 PDP views), mixed basket. **Warning `H2_SINGLE_MONTH_SPIKE`:** 84% of H2 GMV was one December order. It is Account Managed with 91 Fleek chats, so the AM should be told that a light-touch automated message is going out. |
| **ACC-213** | £4,899 | Active (Jan; **no February GMV**) | HEALTHY_STRONG_SELF_SERVE → **Reinforce** | Ready — Automated | P2 | A heavy offer-maker (37 offers) with narrower browsing (70 PDP views, still above the 50 threshold). Mixed basket, so no range test. Warning: `NO_FEB_GMV`. |
| **ACC-216** | £3,497 | **Recent Inactivity** (none in Jan or Feb) | RECENT_INACTIVITY → **Verify Demand / Win-Back** | Ready — Human | **P1** | Labelled Growing, but all of H2 was one December month and nothing has followed. The automated growth nudge is blocked: check the account is still buying first. The handpick trial it would otherwise qualify for is also withheld. |

None of the four qualifies for Discovery-to-Offer, because all already make 5 or more offers. **No feature push is justified for any of them.**

---

## H. Rising Tail

The watchlist is now on the Segmentation tab (column AW). It independently reproduces the Stage 4A list: **6 accounts, £8.2k.**

| Account | Key facts | Reason code → NBA | Secondary test | Priority |
|---|---|---|---|---|
| ACC-068 | Growing, GMV in 3 months, 157 PDP views, 5 offers, mixed basket | RISING_TAIL → Reinforce | – | P3 |
| ACC-083 | Growing, GMV in 4 months (Jan and Feb), 371 PDP views, 14 offers, bundle-only | RISING_TAIL → Reinforce | **Handpick trial** | P3 |
| ACC-085 | Growing, GMV in 4 months, 95 PDP views, 5 offers, bundle-only, Retailer | RISING_TAIL → Reinforce | **Handpick trial** | P3 |
| ACC-219 | New customer, GMV in 3 months, 548 PDP views, **2 offers** | BROWSING_LOW_OFFERS → **Discovery-to-Offer** | – (no H1 history, so not "healthy") | P3 |
| ACC-065 | Returned customer, H2 only, GMV in 2 months | RISING_TAIL_EARLY → Automated Nurture | – | P3 |
| ACC-086 | Growing, but GMV in only 2 months (Oct, Feb); 1,590 PDP views, 50 offers; **February-sensitive** | RISING_TAIL_EARLY → Automated Nurture | – | P3 |

ACC-086 is the clearest case of engagement not turning into purchases: 50 offers but only 3 orders. The missing offer-acceptance data would explain it (M).

---

## I. Retention / Win-Back

| Group | Accounts | GMV | NBA / execution | Notes |
|---|---:|---:|---|---|
| Protect / Retain First | 25 | £187.7k | Retention Conversation, Ready — Human, P1 (ACC-005 is HOLD, P0) | 4 have had **no GMV in Jan or Feb** (ACC-022, 052, 059, 061), so they should be contacted first within P1. 6 are February-sensitive; 4 of those would read Lapsed without February. |
| Engaged but shrinking | 3 (ACC-211, 214, 051) | £21.0k | Retention Conversation, Human, P1 | "Product adoption is not the issue." The target explicitly rules out more product nudges. ACC-211 (Key, Self Serve) has had no GMV since December. |
| Established buyer lapsed | 2 (ACC-015, 062) | £13.5k | Win-back conversation, P1 | Genuine churn cases |
| Thin-history lapse | 9 | £99.3k | Verify cadence, P1 | Includes **ACC-002 (£70.7k from 2 orders)**, which should be verified before anyone calls it churn |
| Growth account gone quiet | 1 (ACC-216) | £3.5k | Verify, P1 | See G |

**The validation confirms no Retention, Win-Back or Reactivation account receives an automated action.**

---

## J. Cost-to-Serve / Long Tail

**Service Model Review (8 accounts, £11.6k, human, P3):** ACC-064, 067, 071, 074, 075, 077, 080, 104. These are low-value, broker-reliant accounts that are still buying. This is an internal decision about AM coverage, not something the customer sees.

**Dormant Cost-to-Serve (13 accounts, £9.8k):** Automated Nurture (P4). No human time is spent on them.

**Long Tail (Segment 9, 210 accounts):**
- 203 are on Automated Nurture.
- 4 get Discovery-to-Offer: ACC-219, 111, 160, 256. ACC-111 is under review.
- 3 get Reinforce.

**Nurture sub-contexts (all 216 nurture accounts):**

| Sub-context | Accounts |
|---|---:|
| Dormant | 139 |
| New customer onboarding | 46 |
| Returned customer | 17 |
| Light-touch repeat buyer | 5 |
| Standard long tail | 4 |
| Engaged, not converting | 3 |
| Rising tail – early pattern | 2 |

Most "engaged, not converting" accounts (Stage 4A found 50) end up in Dormant because they have lapsed.

**Open operational question:** 135 of the nurture accounts are Account Managed but low-value and not broker-led. The engine automates them, but their AM assignment needs a separate portfolio decision. That is out of scope for the engine.

---

## K. Edge Cases

| Account | Output | Why it matters |
|---|---|---|
| **ACC-005** | Retention Conversation / **HOLD** / P0 | The recommendation is kept, but nothing runs until the duplicate status is resolved. It is the 5th-largest account. |
| **ACC-001** | Migration / **Sign-Off** / P2 | £170k (20% of GMV). Borderline and February-sensitive, so sign-off may reasonably be declined. |
| **ACC-002** | Verify / Human / P1 | £70.7k from 2 orders. Its broker % inconsistency changes the tier but not the segment. |
| **ACC-011** | Re-establish / Human / P2 | Key account that returned after a gap (tenure 34 months). One order, No Meaningful History. |
| **ACC-036** | Migration / **Ready — Hybrid** | Passes every Stage 3.1 rule but is Lumpy: 37 orders in only 2 GMV months, a single-month spike, and no February GMV. **This is the weakest Ready account.** Consider moving it to review before launch. |
| **ACC-078 / ACC-111** | Nurture / Discovery-to-Offer with **Human Review** | The broker % implied by their order counts would put them in Cost-to-Serve |
| **ACC-217** | Establish (New) / Automated / P2 | New customer who browses heavily but has made 0 offers, so the onboarding target includes Make-an-Offer |
| **ACC-211** | Retention / Human / P1 | Key Self Serve account with no AM; it needs a named human owner |
| **ACC-160, ACC-256** | Discovery-to-Offer / Automated / P3 | £249 and £263 accounts qualify through the long-tail rule. Low stakes, but they show that the rule has no GMV floor. |

---

## L. Validation

These checks run live on NBA Summary. **All pass.**

| Check | Result |
|---|---|
| 300 accounts in engine | ✔ 300 |
| Every account has a primary_nba / execution_status / attention_priority | ✔ 300 / 300 / 300 |
| Reason codes missing from the library | ✔ 0 |
| Broker-Reliant account given an automated growth nudge | ✔ 0 |
| Declining Key/Core account given an automated action | ✔ 0 |
| Key Migration Candidate not on sign-off / set to Ready-Automated or Hybrid | ✔ 0 / 0 |
| Critical blocker not on HOLD | ✔ 0 |
| Recently inactive account given a growth nudge | ✔ 0 |
| Retention segments (2, 3, 8) with automated delivery | ✔ 0 |
| Target behaviour mentions chat or video | ✔ 0 |
| Row-level invalid-combination checks (11 per row, also covering migration-NBA consistency and secondary-test eligibility) | ✔ 0 |

The Stage 3 segmentation checks on Segment Summary also still pass.

---

## M. What We Still Cannot Know From This Dataset

- **Migration progress.** There are no order timestamps or by-channel order history, so M4 (self-serve share trend) and the 90-day milestones can't be measured until data is collected over a monitoring window.
- **Why engaged accounts don't convert.** There are no offer acceptance or rejection rates and no search or stock-availability data. This affects ACC-086, ACC-211 and the 50 "engaged, not converting" accounts.
- **Whether February is complete.** This affects 36 February-sensitive accounts and every "no February GMV" warning.
- **The window behind chat and video counts.** They may be lifetime totals rather than 6 months.
- **Whether web browsing is tracked.** Some accounts have self-serve orders but 0 app days or 0 PDP views.
- **Product type by order channel.** We can't tell whether handpick orders are placed by the customer or by the AM.
- **Whether any action works.** The data is observational. Only rollout with comparison groups can show whether an action changes spend.
- **What ACC-005's duplicate status refers to,** and whether GMV is double-counted.
- **Cost to serve.** There is no AM time or cost data, so Service Model Review can't be put in financial terms.

---

## N. Recommendations for the Execution / Agent Stage

1. **Build one playbook per primary NBA (8) plus the Range Expansion test.** Each should have an owner role (AM, customer success, or automation), a channel, a cadence and exit criteria. Use `target_behaviour` and `success_measure` as the specification.
2. **Execution gating.** The agent should only act on rows with **Ready — Automated**. It should create tasks for **Ready — Human** and **Ready — Hybrid**, and route **Human Review**, **Sign-Off** and **HOLD** rows to named approvers with the `guardrail_codes` attached.
3. **Human queue order.** Work P0 → P1 → P2, then by value tier and GMV. Within P1, contact recently inactive Protect accounts first (ACC-022, 052, 059, 061).
4. **Phase 1 launch.** Start with the 5 Ready accounts. Consider holding ACC-036 back (K). Track the Manual Review and Key accounts as an informal comparison group, and record 90-day inputs at day 45 and day 90.
5. **Batch reruns.** When `new_accounts` is ingested, update the 5 existing IDs in place and append the 45 new ones. Rerun the full chain (segmentation → context → NBA), then compare how each account's NBA changed so that alerts only fire on changes.
6. **Data requests:**
   - Confirm February completeness.
   - Resolve ACC-005.
   - Offer acceptance data.
   - Order timestamps with channel.
   - The window used for chat and video counts.
   - Web tracking coverage.
   - AM cost per account.
7. **Guardrails for generated messages:**
   - No message may encourage chat or video as a self-serve behaviour.
   - No growth messages go to accounts in Segments 2, 3 or 8.
   - Range Expansion messages must not claim a benefit.
