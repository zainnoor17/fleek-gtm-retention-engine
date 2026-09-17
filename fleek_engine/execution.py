"""Execution layer: HOW each NBA happens (owner, channel, drafts, internal briefs, action state).

Customer drafts use placeholders ({first_name}, {sender_name}) - never invented names - and only
facts available in the data (e.g. product type bought). No internal metrics appear in drafts.
"""
from __future__ import annotations

import hashlib

import numpy as np
import pandas as pd

from . import config as C
from .playbooks import NBA_TO_PLAYBOOK, playbook_library

MONTH_NAMES = dict(zip(C.MONTHS, ["September", "October", "November", "December", "January", "February"]))

# ----------------------------------------------------------------------------- helpers
def _product_phrase(basket: str) -> str:
    return {"Bundle-only": "bundles", "Handpick-only": "handpicked stock"}.get(basket, "bundles and handpicked stock")


def _last_month(row) -> str:
    for m in reversed(C.MONTHS):
        if row[m] > 0:
            return MONTH_NAMES[m]
    return "n/a"


def _arm(account_id: str) -> str:
    return "Treatment" if int(hashlib.md5(account_id.encode()).hexdigest(), 16) % 2 == 0 else "Holdout"


def _money(x: float) -> str:
    return f"£{x:,.0f}"


# ----------------------------------------------------------------------------- customer drafts
SIGN = "\n\nBest,\n{sender_name}"

TEMPLATES = {
    "RET_AM": ("Hi {first_name},\n\nI'd like to set up a short call to review how sourcing through Fleek is working for you at the moment "
               "and what you're planning to buy over the next few months. It will help me make sure the stock I source for you ({product}) "
               "is the right fit. Would sometime later this week or early next week suit you?" + SIGN),
    "RET_CS": ("Hi {first_name},\n\nI'm part of the Fleek team and wanted to hear how the platform is working for your buying at the moment. "
               "Is anything making it harder to find or secure the stock you need? I'd value a short call to understand what would be most useful "
               "for you over the coming months. Would a quick call this week work?" + SIGN),
    "WINBACK": ("Hi {first_name},\n\nIt's been a little while since we last caught up, so I wanted to check in on your buying plans for the "
                "coming months. If you're sourcing {product} again soon, I'd be glad to talk through what you're looking for and how we can help. "
                "Would a quick call be useful?" + SIGN),
    "VERIFY_CADENCE": ("Hi {first_name},\n\nThanks for your previous orders with Fleek. I wanted to check how you usually plan your stock buying "
                       "(seasonal, project by project, or ongoing) so we can get in touch at the right moments rather than too often. "
                       "Happy to talk on a quick call, or just reply here with what works for you." + SIGN),
    "CHECKIN": ("Hi {first_name},\n\nI wanted to check in on how your stock planning looks for the next couple of months. Is there anything "
                "you're looking for that you haven't been able to find on Fleek? If it helps, I'm happy to jump on a quick call or you can "
                "simply reply with what you need." + SIGN),
    "MIG_DAY0": ("Hi {first_name},\n\nAlongside the stock I source for you, I'd like to show you how to browse Fleek's full range directly in the app, "
                 "so you can look through {product} whenever it suits you, make an offer where it fits and place orders yourself. "
                 "I'm still here for anything you need. Could we do a short walkthrough together this week?" + SIGN),
    "MIG_PREENTRY": ("Hi {first_name},\n\nA quick tip: whenever you spot something you like while browsing the Fleek app, you can place the order "
                     "directly there, at a time that suits you. I'll keep sourcing for you as usual, so nothing changes on my side. "
                     "Let me know if a short walkthrough of the app would be helpful." + SIGN),
    "EST_NEW": ("Hi {first_name},\n\nWelcome to Fleek, and thanks for your recent orders. A couple of tips as you build your buying routine: you can "
                "browse available stock in the app whenever suits you, and if a price doesn't quite work, you can use Make an Offer on items "
                "you're interested in. We're here if you need anything." + SIGN),
    "EST_NEW_NO_OFFER": ("Hi {first_name},\n\nWelcome to Fleek, and thanks for your recent orders. As you build your buying routine, it's worth "
                         "checking the app regularly for {product} that suit your range. If you'd like help finding something specific, just "
                         "reply to this message and we'll point you in the right direction." + SIGN),
    "EST_RETURNED": ("Hi {first_name},\n\nGreat to see you ordering with Fleek again. I'd love to catch up on what you're sourcing at the moment "
                     "and how often you're planning to buy, so we can make sure the right {product} is in front of you. Would a quick call "
                     "in the next week or two work?" + SIGN),
    "DTO": ("Hi {first_name},\n\nIf you spot an item you like on Fleek but the price doesn't quite work for you, you can use Make an Offer "
            "directly from the product page to propose your own price. It's a simple way to negotiate on stock you're already looking at, "
            "and you stay in control of what you pay." + SIGN),
    "REINFORCE": ("Hi {first_name},\n\nThanks for being an active Fleek buyer. Just a quick note to keep an eye on the app for {product} that "
                  "fits your range, and to let you know we're here if there's anything specific you're trying to source. "
                  "Reply any time and we'll help." + SIGN),
    "NUR_DORMANT": ("Hi {first_name},\n\nWhenever you're planning your next stock buy, you can browse {product} on the Fleek app at any time. "
                    "If you're looking for something specific, reply to this message and we'll do our best to help you find it."
                    " No pressure, just a friendly reminder that we're here." + SIGN),
    "NUR_NEW": ("Hi {first_name},\n\nThanks for ordering with Fleek. As you get started, you can browse available stock in the app whenever suits "
                "you, and use Make an Offer if a price doesn't quite work. If you're looking for something specific, reply here and we'll help." + SIGN),
    "NUR_RETURNED": ("Hi {first_name},\n\nWelcome back to Fleek, and thanks for your recent order. You can browse {product} in the app whenever "
                     "it suits you. If there's anything specific you're sourcing at the moment, reply to this message and we'll help point "
                     "you in the right direction." + SIGN),
    "NUR_REPEAT": ("Hi {first_name},\n\nThanks for your recent orders with Fleek. A quick reminder that you can browse {product} in the app "
                   "whenever you're ready for your next buy. If there's something particular you're after, just reply to this message and we'll be happy to help." + SIGN),
    "NUR_ENGAGED": ("Hi {first_name},\n\nIf you've found items on Fleek that you like, you can check out directly from the product page, or use "
                    "Make an Offer if the price doesn't quite work for you. If something is holding you back from ordering, reply here and "
                    "let us know, as we'd be glad to help." + SIGN),
    "NUR_ONEOFF": ("Hi {first_name},\n\nThanks for your order with Fleek. Whenever you're planning your next stock buy, you can browse {product} "
                   "in the app at any time. If you're looking for something specific, reply to this message and we'll help." + SIGN),
    "NUR_STANDARD": ("Hi {first_name},\n\nA quick reminder that you can browse {product} on the Fleek app whenever you're planning your next buy, at a time that suits you. "
                     "If there's something specific you're looking for, reply to this message and we'll do our best to help." + SIGN),
    "NUR_RISING": ("Hi {first_name},\n\nThanks for your recent orders with Fleek. Whenever you're planning your next buy, the app is the quickest "
                   "way to browse {product} and make an offer where a price doesn't quite work. If you're looking for something specific, "
                   "reply here and we'll help." + SIGN),
    "RANGE_HANDPICK": ("Hi {first_name},\n\nWould you like to explore another way of sourcing stock? Alongside the bundles you usually buy, Fleek "
                       "also offers handpicked stock, which you can browse in the app. It's there if you ever want to try it; if you have "
                       "any questions, just reply to this message." + SIGN),
    "RANGE_BUNDLE": ("Hi {first_name},\n\nWould you like to explore another way of sourcing stock? Alongside the handpicked stock you usually buy, "
                     "Fleek also offers bundles, which you can browse in the app. They're there if you ever want to try them; if you have "
                     "any questions, just reply to this message." + SIGN),
}

NURTURE_TEMPLATE = {"Dormant": "NUR_DORMANT", "New customer onboarding": "NUR_NEW", "Returned customer": "NUR_RETURNED",
                    "Light-touch repeat buyer": "NUR_REPEAT", "Engaged, not converting": "NUR_ENGAGED",
                    "One-off purchaser": "NUR_ONEOFF", "Standard long tail": "NUR_STANDARD", "Rising tail – early pattern": "NUR_RISING"}


def _template_id(r) -> str:
    code, nba = r.nba_reason_code, r.primary_nba
    if nba == "Service Model Review":
        return ""
    if code in ("DECLINING_KEY_CORE", "ENGAGED_BUT_SHRINKING"):
        return "RET_CS" if r.ownership == "Self Serve" else "RET_AM"
    if code == "LAPSED_ESTABLISHED":
        return "WINBACK"
    if code == "LAPSED_THIN_HISTORY":
        return "VERIFY_CADENCE"
    if code == "RECENT_INACTIVITY":
        return "CHECKIN"
    if code in ("MIGRATION_PHASE1_READY", "MIGRATION_PHASE1_REVIEW", "MIGRATION_KEY_SIGNOFF"):
        return "MIG_DAY0"
    if code == "MIGRATION_PRE_ENTRY":
        return "MIG_PREENTRY"
    if code == "NEW_CUSTOMER":
        return "EST_NEW" if r.discovery_gap else "EST_NEW_NO_OFFER"
    if code == "RETURNED_CUSTOMER":
        return "EST_RETURNED"
    if nba == "Discovery-to-Offer Enablement":
        return "DTO"
    if nba == "Reinforce Successful Behaviour":
        return "REINFORCE"
    if nba == "Automated Nurture":
        return NURTURE_TEMPLATE.get(r.nurture_subcontext, "NUR_STANDARD")
    return ""


def _draft_block_reason(r) -> str:
    """Why a draft is withheld (empty string = draft allowed)."""
    if r.execution_status == "HOLD — Critical Data Issue":
        return "Withheld: account on HOLD (critical data issue)"
    if r.primary_nba == "Service Model Review":
        return "None: internal-only review"
    if r.execution_status == "Human Sign-Off Required":
        return "Withheld until sign-off is recorded"
    if r.execution_status == "Human Review Required":
        return "Withheld until human review is complete"
    return ""


# ----------------------------------------------------------------------------- internal briefs
WHAT_TO_DO = {
    "DECLINING_KEY_CORE": "Book a conversation. Explore stock availability, price, assortment fit, buying cadence, competitor/offline wholesaler use and operational friction. Agree a recovery plan.",
    "ENGAGED_BUT_SHRINKING": "Book a conversation. The customer already uses the product heavily: explore stock availability, price, offer outcomes and competitor use.",
    "LAPSED_ESTABLISHED": "Win-back conversation about upcoming buying needs and what would bring them back.",
    "LAPSED_THIN_HISTORY": "Do not assume churn. Verify expected purchase frequency first, then set the next contact window.",
    "RECENT_INACTIVITY": "Check the account is still buying and why there was no January/February GMV before any automated growth action.",
    "MIGRATION_PHASE1_READY": "Run the Phase 1 plan: Day 0 app walkthrough focused on finding stock independently; check-in Day 15-30; formal review Day 45; outcome Day 90.",
    "MIGRATION_PHASE1_REVIEW": "Resolve the listed guardrail(s) (verify order history / momentum), then decide Ready or not suitable. Record the decision.",
    "MIGRATION_KEY_SIGNOFF": "Portfolio Lead and AM decide whether a gradual self-serve shift is appropriate. Record approve / decline and conditions.",
    "MIGRATION_PRE_ENTRY": "Encourage a second self-serve checkout on stock the customer already wants; keep sourcing as usual; re-assess for Phase 1 next run.",
    "RETURNED_CUSTOMER": "Welcome-back conversation: what brought them back, what they are sourcing now, how often they plan to buy.",
    "COST_TO_SERVE_ACTIVE": "Review the card and decide: maintain support / move to lower-touch / automated nurture / revisit later.",
}
WHAT_NOT = {
    "DECLINING_KEY_CORE": "Do not reduce AM support or push migration; do not suggest the customer is at fault; do not propose chat/video/feature usage as the fix.",
    "ENGAGED_BUT_SHRINKING": "Do not send more product nudges - engagement is not the problem.",
    "LAPSED_ESTABLISHED": "Do not say 'you churned' or 'you've stopped buying'.",
    "LAPSED_THIN_HISTORY": "Do not treat as churn or run a discount-led win-back.",
    "RECENT_INACTIVITY": "Do not trigger automated growth messages until the check is complete.",
    "MIGRATION_PHASE1_READY": "Do not remove AM support; do not mention cost reduction or 'migration'.",
    "MIGRATION_PHASE1_REVIEW": "Do not contact the customer about self-serve changes until review is complete.",
    "MIGRATION_KEY_SIGNOFF": "No migration communication before sign-off.",
    "MIGRATION_PRE_ENTRY": "Do not reduce sourcing support.",
    "RETURNED_CUSTOMER": "Do not treat them as a brand-new customer.",
    "COST_TO_SERVE_ACTIVE": "No customer message. No ROI claim (no AM cost data).",
}


def _brief(r, pb_success: str) -> str:
    code = r.nba_reason_code
    if r.execution_status == "HOLD — Critical Data Issue":
        todo = "Resolve the Duplicate status (find/merge the matching record, confirm GMV is not double-counted) before any contact. Underlying action once cleared: " + r.primary_nba + "."
        dont = "No outbound communication while on HOLD."
    elif r.execution_status == "Human Review Required" and r.delivery_mode == "Automated" and not r.implied_action_change:
        todo = ("Momentum is borderline or depends on February GMV (unconfirmed month). Confirm the recent buying trend, "
                "then release or re-route the automated " + r.primary_nba + " message.")
        dont = "Do not release the automated message until the momentum check is done."
    elif r.execution_status == "Human Review Required" and r.delivery_mode == "Automated":
        todo = ("Order counts imply a different broker reliance than the provided figure, which would move this account to "
                f"{r.implied_action_segment}. Verify order-channel data, then release or re-route the automated action.")
        dont = "Do not release the automated message until verified."
    else:
        todo = WHAT_TO_DO.get(code, "Follow the playbook.")
        dont = WHAT_NOT.get(code, "")
    mom = r.momentum
    if r.h1_gmv > 0 and r.h2_gmv > 0:
        mom += f" (Sep-Nov {_money(r.h1_gmv)} -> Dec-Feb {_money(r.h2_gmv)})"
    facts = [
        f"{r.value_tier}, {r.behavioural_segment}, {r.ownership}; {_money(r.gmv_total_6m)} 6m GMV; {r.buyer_persona}, {r.country}; tenure {int(r.tenure_months)} months.",
        f"Momentum: {mom}; {r.recent_activity_status} (last GMV month: {r.last_gmv_month}); {int(r.orders_6m)} orders over {int(r.active_months)} month(s).",
        f"Dependency: {r.dependency_tier} (broker reliance {int(r.broker_reliance_pct)}%; {int(r.manual_orders)} AM-placed / {int(r.self_serve_orders)} self-serve orders).",
        f"Engagement: {int(r.pdp_views_6m)} product views, {int(r.app_active_days_6m)} app days, {int(r.make_an_offer_6m)} offer(s), {int(r.chat_threads)} Fleek chats, {int(r.video_call_requests)} video requests; basket {r.basket_type}.",
    ]
    if r.guardrail_codes:
        facts.append(f"Warnings: {r.guardrail_codes}.")
    return (f"WHY NOW: {r.nba_rationale_short}\n"
            f"WHAT WE KNOW:\n- " + "\n- ".join(facts) + "\n"
            f"WHAT TO DO: {todo}\n"
            f"WHAT NOT TO DO: {dont}\n"
            f"SUCCESS: {pb_success}")


RATIONALE = {
    "DECLINING_KEY_CORE": "Commercially important, broker-led spend is falling.",
    "ENGAGED_BUT_SHRINKING": "Heavily self-serving account whose spend is falling; product adoption is not the issue.",
    "LAPSED_ESTABLISHED": "Established buyer with a repeat pattern has had no GMV since November or earlier.",
    "LAPSED_THIN_HISTORY": "Apparent lapse rests on 1-2 orders or one buying month; cadence is unknown.",
    "RECENT_INACTIVITY": "Growth-type account with an established pattern but no January/February GMV.",
    "MIGRATION_PHASE1_READY": "Broker-reliant Core account with healthy, regular spend and repeat self-serve checkout, but little independent browsing.",
    "MIGRATION_PHASE1_REVIEW": "Meets Phase 1 entry criteria but a guardrail (borderline/February-sensitive momentum, lumpy cadence or broker % inconsistency) must be resolved.",
    "MIGRATION_KEY_SIGNOFF": "Key broker-reliant account with healthy spend; downside risk too large for automated initiation.",
    "MIGRATION_PRE_ENTRY": "Broker-reliant Core account with healthy spend but only one self-serve order.",
    "RETURNED_CUSTOMER": "Long-tenured customer returned in Dec-Feb after no Sep-Nov spend.",
    "NEW_CUSTOMER": "New customer buying only in Dec-Feb.",
    "HEALTHY_STRONG_SELF_SERVE": "Growing or stable self-serving account with strong independent browsing and recent activity.",
    "BROWSING_LOW_OFFERS": "Independent browser making few offers.",
    "RISING_TAIL": "Rising Tail account with an established recent self-serve pattern.",
    "RISING_TAIL_EARLY": "Rising Tail account whose buying pattern is not yet established.",
    "COST_TO_SERVE_ACTIVE": "Low-value broker-reliant account that is still buying.",
    "DORMANT_LOW_VALUE": "Low-value account with no recent GMV.",
    "LONG_TAIL_STANDARD": "Low-value, low-dependency account.",
}


# ----------------------------------------------------------------------------- main
def _owner(r) -> str:
    es = r.execution_status
    if es == "HOLD — Critical Data Issue":
        return "Portfolio Lead"
    if es == "Human Sign-Off Required":
        return "Portfolio Lead + Account Manager"
    if r.primary_nba == "Service Model Review":
        return "Portfolio Lead"
    if es == "Human Review Required" and r.delivery_mode == "Automated" and r.implied_action_change:
        return "Portfolio Lead"
    if es == "Ready — Automated":
        return "Automation"
    return "Customer Success / Growth" if r.ownership == "Self Serve" else "Account Manager"


def _channel(r) -> str:
    nba = r.primary_nba
    if nba == "Service Model Review":
        return "Internal review (no customer contact)"
    if nba == "Guided Self-Serve Migration":
        return "AM call + in-app walkthrough; automated milestone tracking"
    if r.delivery_mode == "Automated":
        return "Email / in-app message"
    return "Personal email, then call" if r.ownership == "Self Serve" else "Personal email from AM, then call"


def _follow_up(r) -> int:
    if r.primary_nba == "Automated Nurture":
        return 60 if r.nurture_subcontext == "Dormant" else 30
    if r.nba_reason_code == "RETURNED_CUSTOMER":
        return 10
    if r.nba_reason_code == "RECENT_INACTIVITY":
        return 14
    return int(r.pb_follow_up_days)


def _initial_state(r) -> str:
    es = r.execution_status
    if es == "HOLD — Critical Data Issue":
        return "On Hold"
    if es == "Human Sign-Off Required":
        return "Awaiting Sign-Off"
    if es == "Human Review Required":
        return "Awaiting Human Review"
    if r.primary_nba == "Service Model Review":
        return "Not Started"
    return "Draft Ready"


def _first_action(r) -> str:
    code, es = r.nba_reason_code, r.execution_status
    if es == "HOLD — Critical Data Issue":
        return "Portfolio Lead resolves the Duplicate status; no contact until cleared."
    if es == "Human Sign-Off Required":
        return "Portfolio Lead + AM sign-off decision on a gradual self-serve shift."
    if es == "Human Review Required" and r.delivery_mode == "Automated" and r.implied_action_change:
        return "Verify order-channel data; then release or re-route the automated message."
    if es == "Human Review Required" and r.delivery_mode == "Automated":
        return "Confirm the recent buying trend (borderline / February-dependent momentum); then release or re-route the automated message."
    if es == "Human Review Required":
        return "AM resolves the Phase 1 guardrail(s) before any customer contact."
    return {
        "DECLINING_KEY_CORE": "Read brief; send outreach to book a review call.",
        "ENGAGED_BUT_SHRINKING": "Read brief; send outreach to book a call.",
        "LAPSED_ESTABLISHED": "Send win-back check-in.",
        "LAPSED_THIN_HISTORY": "Send cadence check-in (verify, don't assume churn).",
        "RECENT_INACTIVITY": "Send check-in; hold automated growth messages.",
        "MIGRATION_PHASE1_READY": "Day 0: AM walkthrough call on independent stock discovery.",
        "MIGRATION_PRE_ENTRY": "AM encourages a second self-serve checkout.",
        "RETURNED_CUSTOMER": "Send welcome-back outreach; book a call.",
        "NEW_CUSTOMER": "Send onboarding message.",
        "COST_TO_SERVE_ACTIVE": "Portfolio Lead reviews account card and records a service decision.",
    }.get(code, "Queue automated message (" + r.primary_nba + ").")


def generate_execution_plan(d: pd.DataFrame) -> pd.DataFrame:
    """One execution row per account. Deterministic; no randomness."""
    pbl = playbook_library().set_index("primary_nba")
    e = d.copy()
    e["playbook_id"] = e["primary_nba"].map(NBA_TO_PLAYBOOK)
    e["pb_follow_up_days"] = e["primary_nba"].map(pbl["follow_up_days"])
    e["success_condition"] = e["primary_nba"].map(pbl["success_condition"])
    e["stop_condition"] = e["primary_nba"].map(pbl["stop_condition"])
    e["escalation_condition"] = e["primary_nba"].map(pbl["escalation_condition"])
    e["next_rerun_behaviour"] = e["primary_nba"].map(pbl["next_rerun"])
    e["last_gmv_month"] = e.apply(_last_month, axis=1)
    e["nba_rationale_short"] = e["nba_reason_code"].map(RATIONALE)
    rows = list(e.itertuples(index=False))
    e["owner_role"] = [_owner(r) for r in rows]
    e["named_owner_required"] = (e["ownership"] == "Self Serve") & ~e["owner_role"].isin(["Automation"])
    e["notify_am_before_send"] = (e["ownership"] == "Account Managed") & (e["owner_role"] == "Automation")
    e["recommended_channel"] = [_channel(r) for r in rows]
    e["follow_up_days"] = [_follow_up(r) for r in rows]
    e["first_action"] = [_first_action(r) for r in rows]
    e["action_state"] = [_initial_state(r) for r in rows]
    tids = [_template_id(r) for r in rows]
    blocks = [_draft_block_reason(r) for r in rows]
    e["message_template_id"] = [t if not b else "" for t, b in zip(tids, blocks)]
    e["draft_status"] = [b if b else ("Draft ready (not sent)" if t else "No customer message") for t, b in zip(tids, blocks)]
    e["draft_customer_message"] = [TEMPLATES[t].replace("{product}", _product_phrase(r.basket_type)) if (t and not b) else ""
                                   for t, b, r in zip(tids, blocks, rows)]
    human = e["execution_status"] != "Ready — Automated"
    e["internal_task_brief"] = [_brief(r, r.success_condition) if h else "" for r, h in zip(rows, human)]
    # secondary experiment
    arm = e["account_id"].map(_arm)
    has_test = e["secondary_test"] != ""
    e["secondary_test_arm"] = np.where(has_test, arm, "")
    e["secondary_test_template_id"] = np.where(has_test & (arm == "Treatment"),
                                               np.where(e["secondary_test"].str.contains("handpick"), "RANGE_HANDPICK", "RANGE_BUNDLE"), "")
    e["secondary_test_draft"] = [TEMPLATES[t] if t else "" for t in e["secondary_test_template_id"]]
    e["automation_eligible"] = e["execution_status"] == "Ready — Automated"
    # approved Stage 4B library text (presentation only; does not change any decision)
    txt = C.NBA_TEXT
    e["nba_rationale"] = e["nba_reason_code"].map(lambda c: txt[c]["rationale"])
    e["target_behaviour"] = e["nba_reason_code"].map(lambda c: txt[c]["target_behaviour"])
    e.loc[(e["nba_reason_code"] == "NEW_CUSTOMER") & e["discovery_gap"], "target_behaviour"] += "; introduce Make-an-Offer on items already browsed"
    e["success_measure"] = e["nba_reason_code"].map(lambda c: txt[c]["success_measure"])
    return e


EXEC_QUEUE_COLUMNS = [
    "account_id", "attention_priority", "value_tier", "gmv_total_6m", "action_segment", "primary_nba", "nba_reason_code",
    "execution_status", "action_state", "owner_role", "named_owner_required", "notify_am_before_send", "playbook_id",
    "recommended_channel", "first_action", "follow_up_days", "success_condition", "stop_condition", "escalation_condition",
    "guardrail_codes", "draft_status", "message_template_id", "draft_customer_message", "internal_task_brief",
    "secondary_test", "secondary_test_arm", "secondary_test_draft", "nurture_subcontext", "recent_activity_status",
    "target_behaviour", "success_measure", "lifecycle_context", "rising_tail_watchlist", "phase1_rollout_status", "buyer_cadence", "migration_progress_status",
    "next_rerun_behaviour",
]
