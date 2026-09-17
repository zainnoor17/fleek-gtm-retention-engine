# Human vs Automation

**Principle:** automate the decisions that are cheap to get wrong. Keep a person on anything where one mistake could cost a Key account or damage trust.
**Baseline (RUN001):** 75 accounts (£732.8k, 86.7% of GMV) need a person. 225 accounts (£112.6k, 13.3%) are handled automatically.

## What the engine automates

| Step | Output | Why automation is safe here |
|---|---|---|
| Dependency score and tier | 0–100 score, High / Medium / Low | Fixed bands and a gate. Easy to audit against `config.py`. |
| Segmentation | Behavioural segment, value tier, momentum, one of 9 action segments | The validation proves each account matches exactly one rule. |
| Guardrail flags | HOLD, KEY_SIGNOFF, BORDERLINE, FEB_SENSITIVE, LUMPY_CADENCE, MATERIAL_BROKER_INCONSISTENCY, LOW_CONFIDENCE, etc. | Flags only *route* an account. They never trigger contact. |
| NBA assignment | Reason code, primary NBA, execution status, priority | Rule order is explicit. Keeping the NBA separate from execution status stops a recommendation from becoming an action on its own. |
| Execution plan | Owner role, channel, first action, follow-up day, template, brief | Deterministic. Checked by 19 guardrails. |
| Customer drafts | 40–100 words, no internal numbers, no banned phrases | Preview only. Nothing is sent. |
| Change detection | change_type, log rows, action registry | Idempotent: an identical rerun creates 0 actions. |
| Migration progress | Baseline / Progressing / Capability Demonstrated / At Risk | Calculated from 90-day inputs once they exist. At Risk sends the account back to a human. |

### Automated queue (225 accounts)

| Action | Accounts |
|---|---:|
| Nurture: dormant (60-day cadence) | 139 |
| Nurture: new customer onboarding | 46 |
| Nurture: returned customer | 17 |
| Nurture: light-touch repeat / standard / engaged-not-converting / rising-tail early | 13 |
| Reinforce Successful Behaviour | 6 |
| Discovery-to-Offer | 3 |
| Establish (new customer, ACC-217) | 1 |
| *Also:* Range Expansion secondary test, treatment arm (ACC-083 and 085, which are already counted under Reinforce) | (2) |

- **139 of these accounts are Account Managed** and carry `notify_am_before_send`. The AM hears about a message before anything could go out.
- **Automation is never used for:**
  - accounts in Segments 2, 3 or 8 (protect, win-back, reactivation)
  - Broker-Reliant accounts that would get a growth nudge
  - accounts showing Recent Inactivity
  - accounts on HOLD, awaiting review or awaiting sign-off
  - Service Model Review

## What needs human judgement

| Decision | Who (role) | Accounts at baseline | Why a person decides |
|---|---|---:|---|
| Retention conversation | Account Manager (25), CS / Growth (2) | 27 | Spend is falling on valuable accounts. Only a conversation can find the cause (supply, price, service or competitor). |
| Verify demand / win-back | Account Manager (10), CS / Growth (2) | 12 | Most "lapses" rest on one or two orders. Someone has to confirm whether the account has churned or buys on a seasonal or project cadence. |
| Phase 1 migration, Ready | Account Manager | 4 | The Day 0 walkthrough is led by a person, and AM support stays in place. |
| Phase 1 Manual Review | Account Manager | 6 | Borderline, February-sensitive, lumpy or broker-inconsistent accounts. The data can't settle these. |
| Key migration sign-off | Portfolio Lead + Account Manager | 7 (£309k) | The downside is too large to start without sign-off. Declining is a valid outcome. |
| Migration pre-entry | Account Manager | 5 | Encourage a second self-serve checkout without reducing support. |
| Re-establish (returned Key/Core) | Account Manager | 3 | This is about the relationship, not a message template. |
| Service Model Review | Portfolio Lead | 8 | There is no AM cost data, so the call is qualitative and internal only. |
| Data reviews / HOLD | Portfolio Lead | 3 (ACC-078, 111; HOLD ACC-005) | These accounts would be re-segmented if the order-count broker % is correct. ACC-005 needs its duplicate status resolved before any contact. |
| Owner assignment | Portfolio Lead | 4 (ACC-211, 214, 215, 216; these are also counted in the rows above) | Self Serve accounts have no AM. A named person must be assigned before work starts. |

**By owner role:**

| Owner role | Accounts |
|---|---:|
| Account Manager | 53 |
| Portfolio Lead | 11 |
| Portfolio Lead + Account Manager | 7 |
| Customer Success / Growth | 4 |

## How the two meet

- **The tool prepares; a person decides.**
  - Every human-queue account gets a brief in the same order: Why now / What we know / What to do / What not to do / Success.
  - It also gets either a draft or a clear reason the draft is withheld.
- **Local workflow buttons in the UI** record decisions as `action_state` changes, each with an audit row:
  - reviewed / approved
  - rejected / declined
  - in progress
  - completed

  **They never send anything.**
- **Automation hands work back to a person when risk rises.** On a rerun, the account goes to (or stays with) a person if any of these happen:
  - a Key or Core account's momentum turns Declining
  - a growth signal rests on February alone. In RUN002, ACC-211's NBA became Reinforce, but it went to Human Review instead of an automated message.
  - the migration GMV guardrail is breached (At Risk means support is restored)

## Where people should overrule the tool

- **Local knowledge.** The account manager knows about a seasonal pause, a supply issue or a relationship change that the data can't show.
- **Thin history.** An account has 1–2 orders, so any momentum or share figure is fragile (`LOW_CONFIDENCE`).
- **Doubtful data.** February completeness and order-channel attribution are not yet confirmed. Treat February-sensitive and broker-inconsistent flags as prompts to check, not as facts.
