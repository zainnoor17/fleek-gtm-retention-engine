# Fleek_Feature_Opportunity_Analysis

**Stage 4A: evidence base for the Next Best Action (NBA) engine.** This stage is descriptive only. There is no model, no score and no per-account NBA.
**Inputs:** the portfolio dataset (unchanged) and the locked Stage 3 / 3.1 segmentation in `Fleek_Dependency_Scoring.xlsx`.
**New workbook tabs:**
- **Feature Data:** per-account feature view, basket type, milestones, archetype and a proposed Rising Tail flag.
- **Feature Analysis:** summary tables.

All figures are live formulas and were cross-checked against an independent Python rebuild.

> **Read every comparison here as association, not causation.** This is one 6-month cross-section of 300 accounts. Feature usage largely reflects how big, old or AM-managed an account already is.
>
> Two of the behaviours, **app active days and Make-an-Offer, are inputs to the Dependency Score.** Their gap between Broker-Reliant and self-serving accounts is therefore partly built in. **PDP (product page) views, chat, video, handpick and bundles are not in the score**, so comparisons on those are independent evidence.

---

## A. Executive Findings

1. **Self-serve customers are defined by discovery behaviour, not by which features they touch.**
   - Low-dependency Key/Core accounts median **550 PDP views and 40 app days** in six months. Migration Candidates median **4.5 PDP views and 4.5 app days**, a difference of more than 100× on browsing.
   - **Every one of the 78 Broker-Reliant accounts has 15 or fewer PDP views.** PDP views are not a score input, so this is the cleanest independent confirmation of the dependency segmentation.
2. **Chat, video and handpick are high-touch behaviours, not self-serve ones.**
   - Broker-Reliant accounts (26% of accounts) generate **57% of chat threads, 81% of video requests and 78% of handpick orders.**
   - `chat_threads` counts conversations with Fleek, not with sellers. Pushing chat or video would *increase* human dependency. **Neither should be a self-serve nudge.**
3. **Make-an-Offer is broadly used but shallow.**
   - 61% of accounts have made an offer, but the median among users is 2. **91% of all offers come from low-dependency accounts, and 72% from Tail accounts.**
   - Heavy offer use goes with self-serve behaviour, *not* with growth. ACC-211 (71 offers) and ACC-214 (53 offers) are both shrinking.
4. **Bundles are the default, not a lever.**
   - 84% of accounts have bought a bundle, and **197 accounts (66%) buy only bundles**, most of them small Tail accounts.
   - "Bundle adoption" can only mean something for the 48 handpick-only accounts. Build-a-Bundle can't be identified at all.
5. **Among Key/Core accounts, no feature separates GMV except the high-touch ones.**
   - Video users have a median GMV of £6.2k against £3.9k for non-users. They are also older, Key and broker-led accounts.
   - Self-serve behaviours (app ≥20 days, PDP ≥200, offers ≥3) mark *who self-serves*, not *who spends more*.
6. **In the long tail, engagement goes with repeat buying.**
   - Among low-dependency Tail accounts, those with 20+ app days repeat-purchase **61% vs 15%**, and those with 200+ PDP views **55% vs 15%**.
   - Busier buyers generate more app activity, so the direction of cause is unknown.
7. **High engagement does not protect spend.**
   - Of 16 "independent browser-buyers", only 7 are Growing or Stable.
   - Three highly engaged Key/Core self-serve accounts are shrinking: **ACC-211, 214 and 051 (£21k)**.
   - **50 Tail accounts browse heavily but have bought at most twice**, and 35 of them have lapsed.
8. **No Migration Candidate meets any self-serve milestone.**
   - 0 of 22 reach 10+ app days, 50+ PDP views or 3+ offers. Among repeat self-servers, 92%, 89% and 68% reach them respectively.
   - The **"≥2 self-serve orders" Phase 1 criterion does not mean independent discovery.** 24 of the 44 Broker-Reliant accounts with 2+ self-serve orders have 5 or fewer PDP views.
9. **Segment 6 (Growth Opportunity) is 4 young, lumpy, all-reseller accounts.**
   - Each has 5–6 months' tenure, and 73–100% of each account's H2 GMV came in a single month.
   - ACC-216 has had **no GMV since December** despite being labelled "Growing".
   - A Rising Tail watchlist adds **6 accounts (£8.2k)**. Together, the growth pool is small: this portfolio's money is in the broker-led book.
10. **Retention segments need human action, not product nudges.** All 25 Protect accounts are broker-led, product-blind accounts (median 30 chats, 8 PDP views). An automated feature prompt has nothing to build on.

---

## B. Feature Adoption

| Feature | % using | Median (all) | Median (users) | Top-10 accounts' share | BR / AM-Self / SS usage | Key / Core / Tail usage | Pattern |
|---|---:|---:|---:|---:|---|---|---|
| App active days | 98% | 7 | 7 | 20% | 97 / 98 / 97% | 100 / 96 / 98% | **Broadly adopted, but intensity differs:** 92% of app days come from low-dep accounts |
| PDP views | 95% | 61 | 67 | 37% | 97 / 98 / 88% | 100 / 96 / 94% | **Intensity is the signal:** BR median 5, AM-self 119, SS 81. 99% of views come from low-dep accounts. |
| Make-an-Offer | 61% | 1 | 2 | 42% | 81 / 56 / 51% | 67 / 78 / 57% | **Broad but shallow.** BR accounts try it once (max 2). Volume comes from self-servers. |
| Chat threads (with Fleek) | 78% | 3 | 5 | 29% | **99** / 79 / 59% | 100 / 98 / 72% | **A human-contact channel:** 57% of volume from BR accounts. BR median 17.5 vs SS 1. |
| Video call requests | **17%** | 0 | 1 | **68%** | 37 / 11 / 9% | 56 / 33 / 10% | **Sparse and concentrated:** ACC-014 (36), 006 (24), 003 (18). 81% from BR, 49% from Key. |
| Handpick orders | 34% | 0 | 2 | 45% | 63 / 27 / 19% | **94** / 71 / 21% | **Mainly used by already-valuable accounts:** 78% from BR, 51% from Key |
| Bundle orders | 84% | 1 | 1 | 29% | 79 / 82 / 91% | 72 / 75 / 87% | **The default product for small buyers** |
| Bundle GMV share | – | 100% | – | – | BR median 69% | Key 28%, Tail 100% | **Effectively a product-mix field:** 197 at 100%, 48 at 0%, 55 mixed |

**Usage by action segment (median):**

| Segment | App days | PDP | Offers | Chat | Handpick | Bundle GMV % | Video users |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1 Migration Candidate | 4.5 | 4.5 | 1 | 20.5 | 2 | 41% | 59% |
| 2 Protect / Retain First | 4 | 8 | 1 | 30 | 3 | 55% | 40% |
| 3 Win-Back / Verify | 3 | 4 | 1 | 38 | 1 | 73% | 12% |
| 5 Cost-to-Serve | 3 | 5 | 1 | 6 | 0 | 100% | 19% |
| **6 Growth Opportunity** | **54.5** | **736** | **9** | 33 | 2 | 80% | 25% |
| 7 Onboard / Re-engage | 25.5 | 485 | 0.5 | 12 | 2 | 50% | 0% |
| 8 Retention / Reactivation | 45 | 372 | 3 | 27.5 | 1 | 30% | 17% |
| 9 Long-Tail Nurture | 9.5 | 94.5 | 1 | 1.5 | 0 | 100% | 10% |

**Summary against your five questions:**

| Question | Answer |
|---|---|
| Broadly adopted | App, PDP, bundles |
| Concentrated in a few accounts | Video, and to a lesser extent handpick and offers |
| Mainly used by already-valuable accounts | Handpick, video, chat |
| Mainly used by self-serve customers | PDP intensity, app intensity, offer volume |
| Mostly absent from the portfolio | Video (83% have never used it) |

---

## C. What Strong Self-Serve Looks Like

**Reference populations (definitions are transparent):**

- **A. Strong self-serve:** Low dependency and Key/Core value. **12 accounts.**
- **B. Growing strong self-serve:** A plus Growing or Stable momentum (= Segment 6). **4 accounts.**
- **C. High-engagement self-serve:** Low dependency, 20+ app days (the start of the lowest-dependency app band) and 3+ offers, at any GMV. **35 accounts (28 Tail).**
- **Also used: repeat self-servers.** Low dependency and 3+ orders. **37 accounts.** This is the largest population with a real buying pattern.

**Medians by group:**

| Group | n | App days | PDP | Offers | Chat | Video users | Handpick | Bundle orders | Bundle GMV % | Orders | Self-serve share | GMV | Tenure (mo) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| A Strong self-serve | 12 | **40** | **550** | 4.5 | 21 | 17% | 1 | 5.5 | 67% | 8 | 100% | £3,805 | **5** |
| B Growing strong self-serve | 4 | 54.5 | 736 | 9 | 33 | 25% | 2 | 6 | 80% | 8 | 100% | £4,957 | 5 |
| C High-engagement self-serve | 35 | 36 | 455 | 9 | 13 | 17% | 1 | 2 | 87% | 4 | 100% | £925 | 6 |
| Repeat self-servers | 37 | 30 | 341 | 4 | 7 | – | 1 | 4 | 87% | 4 | 100% | £1,166 | – |
| Migration Candidates | 22 | **4.5** | **4.5** | 1 | 20.5 | 59% | 2 | 5 | 41% | 8 | **31%** | £4,596 | **12** |
| AM-Owned / Self-Serving (all) | 132 | 11 | 119 | 1 | 3 | 11% | 0 | 1 | 100% | 1 | 100% | £306 | 7 |
| Lower-value self-serve (Low, Tail) | 210 | 9.5 | 94.5 | 1 | 1.5 | 10% | 0 | 1 | 100% | 1 | 100% | £273 | 6 |

**What sets successful self-servers apart:**
1. **Browsing depth.** PDP views are about 100× those of Migration Candidates at similar GMV and order counts. Self-servers view about 10 PDPs per app day; Broker-Reliant accounts view about 1.5.
2. **Regular app use.** 40 app days against 4.5.
3. **Some offer activity.** 75% of group A use offers; the median is 4.5.

**What does *not* set them apart:**
- **Chat:** similar counts (21 vs 20.5).
- **Handpick:** both groups use it (83% vs 73%).
- **Bundle orders:** similar (5.5 vs 5).
- **Video:** used *less* by self-servers (17% vs 59%).

**Confounders:**
- **Tenure:** successful self-servers are young (median 5 months) while broker-led accounts are established (12 months). The difference may reflect onboarding era or AM assignment policy rather than a behaviour anyone can copy.
- **Sample size:** groups A and B are small (12 and 4).

---

## D. Feature Relationships

**1) Low-dependency Tail accounts (n = 210): the largest comparable population, with value tier and dependency held constant**

| Feature | Users (n) | Median GMV (users vs non-users) | Repeat rate (users vs non-users) | Growing/Stable (users vs non-users) |
|---|---:|---|---|---|
| App days ≥20 | 54 | £506 vs £216 | **61% vs 15%** | 13% vs 4% |
| PDP views ≥200 | 60 | £453 vs £244 | **55% vs 15%** | 8% vs 5% |
| Offers ≥3 | 62 | £363 vs £251 | **48% vs 18%** | 13% vs 3% |
| Chat ≥1 | 146 | £310 vs £160 | 35% vs 8% | 8% vs 2% |
| Video ≥1 | 20 | £297 vs £271 | 25% vs 27% | 0% vs 7% |
| Handpick ≥1 | 43 | £471 vs £249 | 53% vs 20% | 14% vs 4% |
| Mixed basket | 16 | £954 vs £262 | 94% vs 21% *(partly mechanical)* | 25% vs 5% |

**2) Key/Core accounts (n = 69)**
- Self-serve behaviours identify low-dependency accounts: 100% of app ≥20, PDP ≥200 and offers ≥3 users are low-dependency. They do not identify higher spend (median £4.6k vs £4.3k for app ≥20).
- Video users have higher GMV (£6.2k vs £3.9k) and a better Growing/Stable rate (52% vs 29%). They are also older and more Key-weighted, so this is most likely a size effect.

**3) Momentum, among the 78 accounts with GMV in both halves** (so that Growing/Stable is meaningful)

| Group | Users | Growing/Stable (users vs non-users) |
|---|---:|---|
| App ≥20 | 17 | 65% vs 54% |
| Offers ≥1 | 61 | 54% vs 65% |
| Chat ≥10 | 52 | 52% vs 65% |
| Video ≥1 | 26 | 58% vs 56% |
| **Handpick ≥1** | 56 | **46% vs 82%** |
| **Bundle-only** | 22 | **82% vs 46%** |
| Broker-Reliant only: handpick users | 39 | 44% vs 71% |

**No feature is reliably associated with better momentum.** The handpick/bundle split is the strongest signal, but n = 22 for bundle-only accounts. It may simply reflect that large, lumpy handpick buyers swing more between months. **Treat it as a hypothesis, not a lever.**

**Product-type economics:** median average order value is £549 for accounts where more than half of orders are handpick, £317 for those with some handpick, and £220 for bundle-only accounts. Handpick is the higher-ticket product.

**Plain statement:** feature usage here mostly reflects customer size, maturity and service model. None of these comparisons shows that encouraging a feature would raise spend.

---

## E. Customer Archetypes

These are six rule-based patterns, assigned in priority order. They are live on the Feature Data tab and are analysis labels, not NBAs.

| Archetype | Rule | Accounts | GMV | % GMV | Growing/Stable | Where they sit |
|---|---|---:|---:|---:|---:|---|
| **Broker-led, product-blind** | Broker-Reliant (all have ≤15 PDP views) | 78 | £701.9k | 83.0% | 35% | Segments 1–5 |
| **Independent browser-buyer** | Low dep, 20+ app days, 200+ PDP views, 3+ offers, 3+ orders | 16 | £31.3k | 3.7% | 44% | Segment 6 (3), Segment 9 (13) |
| **Engaged but shrinking (Key/Core)** | Low dep, Key/Core, Declining/Lapsed, 20+ app days or 200+ PDP views | 3 | £21.0k | 2.5% | 0% | Segment 8: ACC-211, 214, 051 |
| **Engaged, not converting** | Low dep, 20+ app days or 200+ PDP views, ≤2 orders | 50 | £22.1k | 2.6% | 2% | Segment 9. 35 lapsed; 20 make 3+ offers. |
| **Light-touch repeat buyer** | Low dep, 2+ orders, below the engagement bar | 30 | £32.0k | 3.8% | 30% | Mostly Segment 9 |
| **One-off low-touch buyer** | Low dep, 1 order, low engagement | 123 | £37.2k | 4.4% | 0% | Segment 9 (85% bundle-only) |

**Combinations you asked about:**

| Combination | Finding |
|---|---|
| Browsing + offers | Yes. This is the independent browser-buyer. |
| Chat + offers | No distinct pattern. Chat tracks AM contact. |
| Video + high-value orders | Video users have a higher median AOV (£386 vs £269). This is Key-weighted. |
| Bundles + repeat ordering | Bundle-only accounts are mostly single-order buyers. No link to repeat buying. |
| Handpick-heavy vs bundle-heavy | This is a split of broker-led/Key accounts against Tail accounts, as above |
| High app use, low conversion | Yes: "Engaged, not converting" |
| High engagement, declining GMV | Yes: "Engaged but shrinking" |
| Meaningful GMV with almost no product engagement | Yes: "Broker-led, product-blind", which holds 83% of GMV |

---

## F. Growth Opportunity Accounts (Segment 6)

All four are **Resellers**, **5–6 months' tenure**, low dependency, and Growing. **All four have a blank status.** Monthly GMV is shown Sep → Feb.

| | **ACC-212** | **ACC-025** | **ACC-213** | **ACC-216** |
|---|---|---|---|---|
| Ownership / country | Self Serve / Germany | **Account Managed** / UK | Self Serve / France | Self Serve / France |
| GMV 6m | £8,581 | £5,014 | £4,899 | £3,497 |
| Monthly GMV | 0 · 2,075 · 604 · 0 · **4,310** · 1,593 | 150 · 0 · 0 · **4,089** · 82 · 694 | 0 · 396 · 472 · **3,053** · 978 · **0** | 0 · 961 · 433 · **2,103** · **0 · 0** |
| H1 → H2 (momentum) | £2,679 → £5,903 (+120%) | £150 → £4,865 (+3,143%) | £868 → £4,031 (+364%) | £1,394 → £2,103 (+51%) |
| Orders (self-serve) | 8 (8) | 8 (7; 1 manual) | 8 (8) | 11 (11) |
| App days / PDP views | 78 / 612 | 59 / 860 | 29 / **70** | 50 / 1,416 |
| Offers | 5 | 5 | **37** | 13 |
| Chat / video | 48 / 1 | **91** / 0 | 18 / 0 | 16 / 0 |
| Handpick / bundle orders / bundle GMV share | 3 / 5 / 63% | 5 / 3 / 71% | 1 / 7 / 89% | **0** / 11 / **100%** |
| Archetype | Independent browser-buyer | Independent browser-buyer | Light-touch repeat buyer | Independent browser-buyer |
| **Strengths** | Balanced: browsing, regular app use, mixed basket, the highest GMV in the segment | Heavy browsing and a mixed basket | A heavy offer-maker who converts | The most browsing and the most orders in the segment |
| **Apparent gaps** | Offers are low for its browsing level (5 offers against 612 PDP views) | 91 Fleek chats: may still lean on human contact despite 1 manual order. H2 is 84% one December order. | Narrow discovery (70 PDP views); rarely buys handpick. No February GMV. | Never bought handpick. **No GMV in January or February.** |
| **Plausible lever (not final)** | Offer adoption (self-serve peers median 4.5–9 offers). Keep reinforcing current behaviour. | Grow current behaviour; confirm the December spike can repeat. Watch chat dependence. | Discovery breadth (browse more stock) | A handpick trial, since handpick has a higher AOV. First, **confirm the account is still active.** |

**Caution:**
- All four are very young accounts, so "Growing" may simply be a normal ramp-up.
- Each account's H2 GMV is dominated by one month (73–100%; for ACC-216, all of H2 is one December month).
- ACC-216 and ACC-213 had no February GMV, so they could slide into Retention next period.

**Segment 6 needs a recency check before any growth prompt.**

---

## G. Rising Tail / Growth Watchlist

**Proposed rule (context flag only; the primary segment does not change).** An account is flagged when all of these hold:

- Low dependency and Tail value
- GMV of £1,000 or more
- 3 or more orders
- **Either** Growing/Stable momentum, **or** "H2 Active / No H1 GMV" with 2 or more months of GMV
- **And** either 20+ app days or 3+ offers

**Result: 6 accounts, £8,220.**

| Account | GMV | Orders | Momentum / lifecycle | App days / PDP / offers | Basket | Note |
|---|---:|---:|---|---|---|---|
| ACC-065 | £1,812 | 5 | H2-only / Returned | 55 / 675 / 4 | Bundle | Dec–Jan only, nothing in February |
| ACC-068 | £1,706 | 5 | Growing | 31 / 157 / 5 | Mixed | 35 chats, 19 months' tenure |
| ACC-083 | £1,217 | 8 | Growing | 49 / 371 / 14 | Bundle | The clearest rising account: bought in Jan and Feb |
| ACC-085 | £1,166 | 4 | Growing | 18 / 95 / 5 | Bundle | **Retailer.** Qualifies on offers only. |
| ACC-086 | £1,153 | 3 | Growing | **105 / 1,590 / 50** | Mixed | Very engaged, but only 2 purchase months (Oct, Feb). 96 chats. |
| ACC-219 | £1,166 | 5 | H2-only / **New** (3 months' tenure) | 39 / 548 / 2 | Mixed | A genuinely new customer ramping up |

**Validation against Stage 3:**
- ACC-068, 083, 085 and 086 are confirmed.
- ACC-065 and ACC-219 are new additions; they qualify through the H2-active clause.
- ACC-078 (Stable, £1,366) is **excluded**: 10 app days, 0 offers, 24 PDP views, and its broker-% inconsistency means it could be broker-led.

**Threshold sensitivity:**

| GMV threshold | Accounts |
|---|---:|
| £750 | 9 (adds ACC-090, 093, 221) |
| £1,000 | 6 |
| £1,500 | 2 |

---

## H. Migration Behaviour

**Current behaviour of Migration Candidates (22):**

| Group | n | App days | PDP views | Offers | Chat | Self-serve share | Handpick / bundle orders | Video users |
|---|---:|---|---|---|---|---|---|---|
| **Phase 1 Ready** | 5 | 2–6 | 1–15 | 0–1 | 4–34 | 24–43% | mixed | 3 of 5 |
| **Phase 1 Manual Review** | 5 | 2–7 | 3–12 | 0–2 | 9–27 | 36–67% | mixed | 2 of 5 |
| **Key Migration Candidates** | 7 | 1–8 | 1–8 | 0–2 | 16–**182** | 14–39% | 6 of 7 handpick-heavy (13–40 orders); ACC-016 buys only bundles | 7 of 7 |
| Low-dep repeat self-servers (benchmark) | 37 | median 30 | median 341 | median 4 | median 7 | 100% | bundle-leaning | – |

**Ready and Manual Review accounts look alike on product behaviour.** They differ only on the Stage 3.1 guardrails. Key accounts are the most human-intensive: 7 of 7 use video, chat runs up to 182, and they buy mostly handpick.

**Which behaviours would show a broker-reliant account learning to self-serve?**

Each proposed milestone below is tested against the same evidence: the level no Broker-Reliant account reaches, versus how many repeat self-servers reach it.

| Milestone | Threshold (6-month basis) | Broker-Reliant accounts reaching it | Repeat self-servers reaching it | Verdict |
|---|---|---:|---:|---|
| **M1 – Independent discovery** | 50+ PDP views | **0 of 78** (max 15) | **89%** | **Strongest milestone.** Not a score input, so the evidence is independent. |
| **M2 – Habitual app use** | 10+ app days | 0 of 78 (max 8) | 92% | Strong, but partly built into the score. Use it together with M1. |
| **M3 – Self-directed negotiation** | 3+ offers | 0 of 78 (max 2) | 68% | Useful. Not every successful self-server makes offers, so it is **supportive, not mandatory.** |
| **M4 – Repeat self-checkout** | Rising self-serve share across consecutive orders | – | – | **Needed but not enough on its own.** 24 of 44 BR accounts with 2+ self-serve orders barely browse, so a self-serve order may just be a checkout on stock the AM sourced. |
| Seller communication | – | – | – | **Can't be measured.** `chat_threads` is contact with Fleek. |
| Bundle use | – | – | – | **Not a milestone.** MCs already buy bundles (median 5 orders). |
| Handpick self-purchase | – | – | – | **Can't be measured.** There is no product-type-by-channel breakdown. |
| Reduced Fleek chat per order | Falling trend | – | – | **Monitor only.** The BR median is 2.6 chats per order against 1.5 for repeat self-servers; the gap is small and the data window is unclear. |

**Implications:**
- **Current state:** 0 of 22 Migration Candidates meet M1, M2 or M3 today.
- **Phase 1 success test:** the cohort should be judged on **M1 + M2 (+ M3), with GMV preserved**, not only on self-serve order counts.
- **Reference levels:** the thresholds come from a 6-month snapshot. Stage 4B needs to set monitoring windows and pro-rate them (for example, roughly 25 PDP views and 5 app days per quarter).

---

## I. Retention / Win-Back: Human Action First

| Segment | What the data shows | Correct next step | Automated feature nudge? |
|---|---|---|---|
| **2 Protect / Retain First** (25, 22% GMV) | All 25 are broker-led and product-blind. Median 30 chats, 8 PDP views, 4 app days. 10 use video; 21 buy handpick. Spend is falling. | **AM conversation:** find out why spend fell (supply, price, fit, competitor). Keep the human support in place. | **No.** Nothing on the product side to build on, and pulling back human contact during decline is risky. |
| **3 Win-Back / Verify** (8, 12% GMV) | 6 of 8 have thin histories (e.g. ACC-002: £70.7k from 2 orders). Median 38 chats. | **Established lapsed** (ACC-015, 062): AM win-back. **One-off** (002, 026, 032, 044, 050, 060): verify how often they buy before treating it as churn. | **No.** |
| **8 Retention / Reactivation** (6) | ACC-211, 214 and 051 are *heavily* engaged (6,665 / 665 / 2,403 PDP views; 71 / 53 / 4 offers) but shrinking. ACC-215, 038 and 042 were one-off buyers. | **Engaged-but-shrinking accounts:** a human or research conversation. Engagement is not the problem; conversion or supply may be (offer acceptance isn't in the data). **One-offs:** verify. | **No.** A "use more features" prompt would be wrong for accounts already using them heavily. |
| 5 Cost-to-Serve (21) | 12 lapsed; 15 bundle-only; median 6 chats | This is a decision about service model and AM coverage. Dormant accounts need no action. | Only after a human decides the service model |

The engine needs an explicit outcome: **"Human intervention required – no automated feature recommendation."** It should apply to all of Segments 2 and 3, the engaged-but-shrinking accounts in Segment 8, Key sign-off accounts, and any account with a critical blocker (ACC-005).

---

## J. Proposed Next-Best-Action Taxonomy

Nine action types are proposed below; they are not implemented yet. Chat and video are **deliberately not** self-serve nudges (see A2). Video can stay as a tool AMs use for Key and Protect accounts.

| # | Action type | Objective | Qualifying signals | Disqualifying signals | Delivery | Applies to segments |
|---|---|---|---|---|---|---|
| 1 | **Human Review / Hold** | Stop automation where the risk or data quality is too high | Critical blocker; Key sign-off; Phase 1 Manual Review; material broker inconsistency on Key/Core accounts | – | **Human** | Any. Takes priority over everything else. |
| 2 | **Retention Conversation** | Stabilise falling spend | Declining momentum on Key/Core; engaged-but-shrinking | Lapsed on a thin history (→ 3) | **Human (AM)** | 2; 8 (declining) |
| 3 | **Verify Demand / Win-Back** | Tell real churn apart from infrequent buying; recover established lapsed buyers | Lapsed, Key/Core. Established buyer → win-back; one-off → verify cadence. | Tail lapsed (→ 9) | **Human** for Key/Core | 3; 8 (lapsed) |
| 4 | **Guided Self-Serve Migration** | Replace some AM-led buying with customer-led discovery while keeping GMV | Phase 1 Ready; progress measured by M1 PDP, M2 app days, M3 offers, M4 self-serve share | Borderline or February-sensitive momentum; Key without sign-off; declining GMV during the pilot | **Human-led start, automated milestone tracking** | 1 |
| 5 | **Discovery-to-Offer Enablement** | Turn browsing into negotiation and purchase | Low dependency; browses (PDP ≥50) but makes few offers (<3); momentum not Declining/Lapsed | Broker-Reliant; retention segments; already a heavy offer-maker | **Automated** | 6, 7, Rising Tail. Selected "engaged, not converting" accounts in 9. |
| 6 | **Range Expansion Test (handpick ↔ bundle)** | Test whether a single-product-type self-server will try the other product | Low dep; Key/Core or Rising Tail; single product type; healthy momentum | Declining/Lapsed; Broker-Reliant; mixed basket already | **Automated test with a holdout.** Evidence is weak (D3). | 6, 7, Rising Tail |
| 7 | **Reinforce Successful Behaviour** | Keep strong self-servers growing without disrupting them | Segment 6 or independent browser-buyer with recent GMV | No GMV in the latest month(s) (e.g. ACC-216) → recency check first | **Automated, light touch** | 6, Rising Tail |
| 8 | **Establish / Onboard** | Build a buying pattern | New Customer → onboarding. Returned Customer, Key/Core → re-establish. | – | **New: automated. Returned Key/Core: human.** | 4, 7 |
| 9 | **Automated Nurture** | Low-cost engagement across the tail | Segment 9. Sub-variants: *engaged-not-converting* (conversion prompts), *one-off* (low-frequency reminders), *Rising Tail* (promote to action 5 or 7) | Rising Tail accounts should be routed up | **Automated** | 9. Also dormant accounts in 5. |

**Cost-to-Serve (Segment 5)** fits under action 1 (a human decision on service model) followed by action 9 for dormant accounts. It doesn't need its own action type until Fleek defines a low-touch service model.

---

## K. Data Quality / Limitations

| Issue | Evidence | Impact |
|---|---|---|
| **Chat is contact with Fleek, not sellers** | Readme definition. BR accounts generate 57% of chats. | You can't build a "communicating with sellers" milestone. Chat is a proxy for human dependency. |
| **Unclear window for chat and video** | No `_6m` suffix. Chat correlates more with tenure (0.62) than with 6-month orders (0.58). ACC-137 has 181 chats on 2 orders / £344. | Chat may be a lifetime count. Don't compare it directly with 6-month fields. |
| **Self-serve orders without browsing** | 24 of 44 BR accounts with 2+ self-serve orders have ≤5 PDP views | "Self-serve order" may mean customer checkout of AM-sourced stock |
| **App/web tracking gaps** | 7 accounts have self-serve orders but 0 app days; 15 have 0 PDP views; 5 have offers but 0 PDP views (e.g. ACC-222: 7 offers, 0 views) | Web activity may not be captured. Engagement is understated for some accounts. |
| **Product-type fields** | handpick + bundle = orders for 292 accounts; 7 have mixed orders; ACC-153 has neither. Bundle GMV share is 100% for 197 accounts. | Bundle is a proxy for all non-handpick stock. **Build-a-Bundle can't be identified.** |
| **Video is sparse** | 51 users; the top 10 accounts hold 68% of requests (ACC-014 alone: 36) | Too thin for rules beyond "the account uses it" |
| **Extreme values** | PDP 6,665 (ACC-211); chat 182 (ACC-012) | Use thresholds, not raw intensity |
| **Circularity** | App days and offers are Dependency Score inputs | Their gaps are partly built in. PDP views are the independent test. |
| **No funnel data** | No offer acceptance, no search, no per-event timestamps | "Engaged, not converting" can't be diagnosed |
| **Tenure confounding** | Self-servers are ~5 months old; broker-led accounts ~12 | Differences may reflect when and how accounts were onboarded |
| **Small samples** | Segment 6 = 4 accounts; strong self-serve = 12 | Profiles are illustrative, not statistical |
| Carried forward | February completeness unconfirmed; ACC-005 duplicate; status blank for all Self Serve accounts | As in Stage 3.1 |

---

## L. Recommendations for Stage 4B

1. **Encode the NBA as a priority-ordered rule table**, not a score: Human Review → Retention → Verify/Win-Back → Migration → Establish/Onboard → Discovery-to-Offer / Range Test / Reinforce → Automated Nurture. Each account gets **one primary action**, with the reason codes that triggered it.
2. **Add the self-serve milestone fields** (M1 PDP ≥50, M2 app days ≥10, M3 offers ≥3, M4 self-serve share trend) to the Phase 1 Cohort tab as **baseline and target**. Set a monitoring window (e.g. 90 days, pro-rated) and a GMV-preservation guardrail (e.g. stop if cohort GMV falls beyond a set tolerance).
3. **Promote `rising_tail_watchlist` into Segmentation** as a context flag, if you approve the rule in G.
4. **Gate feature nudges on peer evidence:**
   - **Discovery-to-Offer:** only for browsers who aren't making offers.
   - **Range Expansion:** only for single-product-type accounts with healthy momentum, and only as a test with a holdout.
   - **No chat or video nudges.**
5. **Add a recency guardrail for automated growth actions:** no GMV in the latest month means a check first. ACC-216 and ACC-213 are the cases.
6. **Measurement:** Phase 1 has 5 Ready accounts, so use matched comparisons (e.g. Manual Review accounts once cleared, or similar Protect/Migration accounts) rather than claiming a controlled experiment.
7. **Data requests before Stage 4B goes live:**
   - Is February complete?
   - What window do `chat_threads` and `video_call_requests` cover?
   - Is web browsing captured?
   - Offer acceptance rate.
   - Product type by order channel (handpick bought self-serve vs via an AM).
   - What does ACC-005's Duplicate status refer to?
