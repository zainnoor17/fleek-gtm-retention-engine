# Loom walkthrough (7–9 minutes)

These are talking points, not a script to read word for word. Say them in your own words.

## Before you record

- Run `streamlit run app.py`. Click **Reset demo** on Change / Rerun so you start from RUN001 only.
- Have a second window open on the repo (VS Code or GitHub) showing `README.md` and `docs/architecture.md`.
- Close anything showing personal info. Use a browser width of about 1400px.

---

## 0:00–1:00 · The problem

*Screen: Portfolio Overview, top of page.*

- "Fleek wants to move account-managed buyers towards self-serve without losing revenue. The catch is where the dependence sits."
- "The 78 broker-reliant accounts are a quarter of the book but 83% of GMV. Most of the valuable ones are shrinking."
- "So the first question for many of them isn't how to migrate them. It's how to keep them. I built a tool that keeps those two jobs apart and tells the team, every morning, what needs attention, why, what to do next and what changed."
- "It's all transparent rules. No model and no black-box score, because with 300 accounts and six months of lumpy data, that's the honest choice."

## 1:00–2:00 · Overview

*Screen: Portfolio Overview.*

- Read out the headline: **human attention is focused on 75 accounts representing 86.7% of GMV.** The other 225 run through low-risk automated playbooks.
- Point at the priority row:
  - P0 has 1 account: ACC-005, the duplicate on HOLD.
  - P1 has 39 accounts, about £300k. That's revenue protection.
  - P2 is mostly migration, including £309k of Key accounts that need sign-off.
- Point at execution status: 1 HOLD, 8 in review, 7 awaiting sign-off, 225 automated.
- Expand **19 / 19 execution guardrails passing.** "These are hard checks on every run. For example: nothing goes to HOLD accounts, no migration message before sign-off, no chat or video nudges, no internal numbers in drafts."
- Scroll to the data-quality panel. "I've kept the open questions visible rather than buried. I'll come back to them."

## 2:00–3:00 · Human queue

*Screen: Human Queue.*

- "One queue, grouped by role. There are no named people in the data, so I use role labels. The four Self Serve accounts that need a person are flagged: someone has to own them before work starts."
- **Retention example: ACC-008** (Key, broker-reliant, declining). Open the expander and read the brief headings: Why now / What we know / What to do / What not to do. Then show the draft. "It's a short, personal note asking for a call. There's no mention of dependency or churn and no numbers. It's a preview; nothing is sent."
- **Migration example: ACC-019** (Phase 1 Ready). Click **Open account detail.** Point out 70 dependency, 43% self-serve share, and 15 product views over six months. "It already checks out on its own sometimes, but it doesn't browse. So the goal is discovery, not a push to cut contact."
- Optional: switch to **ACC-001**. "This is our largest account. It's technically a migration candidate, but the draft is withheld until sign-off." Click **Approve (sign-off)** and say: "That only changes local state and writes an audit row."

## 3:00–4:00 · Migration logic

*Screen: Migration.*

- Read the banner: migration means teaching independent discovery **while AM support stays in place.**
- Walk through the four groups:
  - **Ready:** ACC-019, 027, 030, 031
  - **Manual Review:** 6 accounts that are borderline, February-sensitive, lumpy or have inconsistent broker data
  - **Key Sign-Off:** 7 accounts
  - **Pre-Entry:** 5 accounts, each with one self-serve order so far
- "I moved lumpy buyers to review. If someone buys twice a year, a 90-day spend check can't tell a normal gap from a problem."
- Milestone table:
  - product views and app days are the real signals; offers only support them
  - a GMV guardrail applies from day 45
  - if spend drops, support comes back

## 4:00–6:00 · Live rerun

*Screen: Change / Rerun.*

- "This is day two. A new batch arrives." Click **2 · Ingest new_accounts.**
- Read the results:
  - **5 existing accounts updated**
  - **45 new accounts added**
  - **345 in total**
  - **0 duplicates**
  - 46 log rows and 46 new actions: one for each new account, plus one real change
- Scroll to **ACC-211.**
  - "The new batch added February spend, so momentum went from Declining to Stable, and the recommendation changed from Retention to Reinforce."
  - "But the tool didn't just fire an automated 'well done' message. Without February, this account still looks like it's declining. It's February-sensitive, so it's held for a person."
  - "Priority went from P1 to P2 and the status is Human Review Required."
- Point at the quiet updates: ACC-006, 008, 048 and 214 changed data but not decisions. "Those get no alert and no new action."
- Point at **newly entered human queue: 10.** These are new accounts, including one Key retention case and one new Phase 1 Ready account.
- "All five updates changed only February, and two accounts had orders reclassified from AM-placed to self-serve. That's a data question I'd raise before launch."

## 6:00–7:00 · Idempotency

*Screen: Change / Rerun.*

- Click **3 · Re-run identical batch.**
- "Same file again. The fingerprint matches, so there are 0 log rows, 0 new actions, 0 duplicates and every account is unchanged. Nobody gets messaged twice because a job ran twice."
- "Local workflow decisions, like the ACC-001 sign-off, survive the rerun. There's a test for that."
- Open the **Action log** expander. It shows only material changes.

## 7:00–8:00 · Repo and architecture

*Screen: GitHub or VS Code.*

- `README.md` covers the run commands and design decisions.
- `docs/architecture.md` has the Mermaid diagram:
  - blue is automated, orange is human judgement
  - the loop is: new batch → upsert → rerun → compare
- `fleek_engine/`:
  - every threshold is in `config.py`
  - the UI only calls `DemoSession`; there's no business logic in `app.py`
- Tests: `python -m pytest -q` runs 12 tests, covering locked counts, the lumpy rule, idempotency and the UI flow.
- Be honest about scale:
  - "I ran a synthetic 30k-row copy. The rules take about 2 seconds and pass every guardrail."
  - "The full run with CSV state takes about 14 seconds."
  - "That tells you the logic holds at that size, not how it would behave in production."

## Closing (about 30–60 seconds)

- **Open data questions I'd want answered first:**
  - Is February complete?
  - How are orders attributed to AM vs self-serve?
  - What is ACC-005's duplicate?
  - Is web usage in app days?
  - Offer acceptance data
  - What window do chat and video cover?
  - AM cost per account
- **First 30 days** (see `docs/first_30_days.md`):
  - Week 1: validate the data with the owners and review the P1 queue with the AMs.
  - Week 2: start retention conversations and Key sign-off decisions.
  - Week 3: launch Phase 1 with the 4 Ready accounts, with AM support in place.
  - Week 4: first check-ins, and decide on wiring in outcome data.
- "The tool doesn't replace judgement. It makes sure the judgement goes to the 75 accounts where it matters."
