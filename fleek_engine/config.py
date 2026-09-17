"""All rule parameters in one place (mirrors the workbook Assumptions tab)."""

MONTHS = ["gmv_sep", "gmv_oct", "gmv_nov", "gmv_dec", "gmv_jan", "gmv_feb"]
H1_MONTHS, H2_MONTHS = MONTHS[:3], MONTHS[3:]

REQUIRED_COLUMNS = [
    "account_id", "ownership", "buyer_persona", "region", "country", "account_status", "tenure_months",
    "gmv_total_6m", "orders_6m", *MONTHS, "gmv_trend_pct", "broker_reliance_pct", "manual_orders",
    "self_serve_orders", "app_active_days_6m", "pdp_views_6m", "make_an_offer_6m", "chat_threads",
    "video_call_requests", "handpick_orders", "bundle_orders", "bundle_gmv_share_pct",
]

# Stage 1 - Self-Serve Dependency
DEP_WEIGHTS = {"broker": 0.5, "app": 0.3, "offer": 0.2}
BROKER_GATE = 20            # broker_reliance_pct <= gate -> score 0
BROKER_BANDS = [20, 40, 60, 80]   # <=20:0, <40:25, <60:50, <80:75, else 100
APP_BANDS = [30, 20, 10, 5]       # >30:0, >=20:25, >=10:50, >=5:75, else 100
OFFER_BANDS = [5, 3, 2, 1]        # >=5:0, >=3:25, ==2:50, ==1:75, else 100
TIER_HIGH, TIER_MEDIUM = 70, 40

# Stage 2/3 - value and momentum
KEY_GMV, CORE_GMV = 10_000, 2_000
MOMENTUM_BAND = 0.20

# Stage 3 / 3.1 - guardrails
PHASE1_MIN_ORDERS, PHASE1_MIN_SELF_SERVE = 3, 2
RAW_BROKER_GAP = 10
BORDERLINE_BAND = 0.05
NEW_CUSTOMER_MAX_TENURE = 6
LAPSE_ONEOFF_MAX_ORDERS, LAPSE_ONEOFF_MAX_MONTHS = 2, 1
LOW_CONFIDENCE_MAX_ORDERS = 2

# Stage 4A - feature context
M1_PDP, M2_APP, M3_OFFERS = 50, 10, 3
ENGAGED_APP, ENGAGED_PDP = 20, 200
INDEP_OFFERS, INDEP_ORDERS = 3, 3
RISING_GMV, RISING_ORDERS, RISING_APP, RISING_OFFERS = 1_000, 3, 20, 3

# Stage 4B - NBA engine
DTO_PDP, DTO_MAX_OFFERS = 50, 3
REINFORCE_MIN_MONTHS = 3
LT_DTO_MIN_ORDERS = 2
SPIKE_SHARE = 0.8
REGULAR_MIN_MONTHS, REGULAR_MIN_ORDERS = 3, 5     # buyer cadence (Stage 5: Lumpy -> Phase 1 Manual Review)

# Phase 1 monitoring (90-day)
WINDOW_DAYS = 90
PROG_PDP, PROG_APP = 15, 5
CAP_PDP, CAP_APP = 25, 6
GMV_GUARDRAIL_SHARE, GMV_GUARDRAIL_FIRST_DAY = 0.7, 45

SEGMENTS = {
    1: "1. Migration Candidate", 2: "2. Protect / Retain First", 3: "3. Win-Back / Verify",
    4: "4. Establish / Re-establish / Observe", 5: "5. Cost-to-Serve / Low-Touch", 6: "6. Growth Opportunity",
    7: "7. Onboard / Re-engage / Learn", 8: "8. Retention / Reactivation", 9: "9. Long-Tail Automated Nurture",
}
H2_ONLY = "H2 Active / No H1 GMV"
ONE_OFF = "One-Off / Insufficient History — Verify"
ESTABLISHED = "Established Buyer Lapsed"

# reason code -> (primary_nba, delivery_mode, default priority)
NBA_LIBRARY = {
    "DECLINING_KEY_CORE": ("Retention Conversation", "Human", "P1"),
    "ENGAGED_BUT_SHRINKING": ("Retention Conversation", "Human", "P1"),
    "LAPSED_ESTABLISHED": ("Verify Demand / Win-Back", "Human", "P1"),
    "LAPSED_THIN_HISTORY": ("Verify Demand / Win-Back", "Human", "P1"),
    "RECENT_INACTIVITY": ("Verify Demand / Win-Back", "Human", "P1"),
    "MIGRATION_PHASE1_READY": ("Guided Self-Serve Migration", "Hybrid", "P2"),
    "MIGRATION_PHASE1_REVIEW": ("Guided Self-Serve Migration", "Hybrid", "P2"),
    "MIGRATION_KEY_SIGNOFF": ("Guided Self-Serve Migration", "Hybrid", "P2"),
    "MIGRATION_PRE_ENTRY": ("Guided Self-Serve Migration", "Human", "P3"),
    "RETURNED_CUSTOMER": ("Establish / Re-establish", "Human", "P2"),
    "NEW_CUSTOMER": ("Establish / Re-establish", "Automated", "P2"),
    "HEALTHY_STRONG_SELF_SERVE": ("Reinforce Successful Behaviour", "Automated", "P2"),
    "BROWSING_LOW_OFFERS": ("Discovery-to-Offer Enablement", "Automated", "P2"),
    "RISING_TAIL": ("Reinforce Successful Behaviour", "Automated", "P3"),
    "RISING_TAIL_EARLY": ("Automated Nurture", "Automated", "P3"),
    "COST_TO_SERVE_ACTIVE": ("Service Model Review", "Human", "P3"),
    "DORMANT_LOW_VALUE": ("Automated Nurture", "Automated", "P4"),
    "LONG_TAIL_STANDARD": ("Automated Nurture", "Automated", "P4"),
}
GROWTH_NBAS = {"Discovery-to-Offer Enablement", "Reinforce Successful Behaviour"}

# Approved Stage 4B NBA library text (target behaviour / success measure / rationale), keyed by reason code.
NBA_TEXT = {'DECLINING_KEY_CORE': {'target_behaviour': 'AM diagnoses the cause of falling spend (supply, price, service, competitor) and '
                                            'agrees a recovery plan; keep human support in place',
                        'success_measure': 'Next 90-day GMV back to at least the Sep-Nov (H1) level, or decline arrested; root '
                                           'cause logged',
                        'rationale': 'Broker-led spend is falling. Keep human support in place; AM to diagnose the cause before '
                                     'any migration or product nudge.'},
 'ENGAGED_BUT_SHRINKING': {'target_behaviour': 'AM investigates supply, price, competition or conversion friction; no additional '
                                               'product nudges',
                           'success_measure': 'Root cause logged; next 90-day GMV back to at least the Sep-Nov (H1) level',
                           'rationale': 'Already heavily self-serving (high browsing / offers) but spend is falling. Product '
                                        'adoption is not the issue.'},
 'LAPSED_ESTABLISHED': {'target_behaviour': 'Win-back conversation: understand why buying stopped and what would restart it',
                        'success_measure': 'New order within 90 days, or churn reason logged',
                        'rationale': 'Had a repeat buying pattern (3+ orders across 2+ months) and has stopped buying. Genuine '
                                     'win-back case.'},
 'LAPSED_THIN_HISTORY': {'target_behaviour': 'Confirm expected purchase cadence (one-off, seasonal, project buyer) before '
                                             'calling it churn',
                         'success_measure': 'Cadence recorded and account reclassified; order within the stated cadence window',
                         'rationale': 'Apparent lapse rests on 1-2 orders or a single buying month. Verify cadence rather than '
                                      'treating as churn.'},
 'RECENT_INACTIVITY': {'target_behaviour': 'Check the account is still buying and why there was no January/February GMV; hold '
                                           'automated growth nudges',
                       'success_measure': 'Order in next 60 days or reason logged; growth action re-assessed on next run',
                       'rationale': 'Growth-type account with an established pattern but no GMV in January or February. Confirm '
                                    'status before any automated growth nudge.'},
 'MIGRATION_PHASE1_READY': {'target_behaviour': 'Independently discover stock (PDP browsing) and use the app regularly; place '
                                                'more orders self-serve; offers optional',
                            'success_measure': '90 days: Progressing -> Capability Demonstrated (PDP, app days, rising '
                                               'self-serve share) with GMV guardrail held',
                            'rationale': 'Broker-reliant with healthy spend and repeat self-serve checkout but little '
                                         'independent browsing. Suitable for Phase 1 guided migration focused on product '
                                         'discovery.'},
 'MIGRATION_PHASE1_REVIEW': {'target_behaviour': 'As Phase 1 Ready once the guardrail warning is resolved',
                             'success_measure': 'Warning resolved; then as Phase 1 Ready',
                             'rationale': 'Meets Phase 1 entry criteria but carries a guardrail warning '
                                          '(borderline/February-sensitive momentum, lumpy cadence or broker % inconsistency). '
                                          'Resolve before starting migration.'},
 'MIGRATION_KEY_SIGNOFF': {'target_behaviour': 'If approved: gradual shift to independent discovery with AM retained; otherwise '
                                               'keep current service model',
                           'success_measure': 'Sign-off decision logged; if approved, as Phase 1 with a stricter GMV guardrail',
                           'rationale': 'Key broker-reliant account with healthy spend. Technically a migration candidate, but '
                                        'downside risk is too large for automated initiation.'},
 'MIGRATION_PRE_ENTRY': {'target_behaviour': 'AM encourages a second self-serve checkout (Phase 1 entry evidence) without '
                                             'reducing support',
                         'success_measure': '2+ self-serve orders, then re-assess for Phase 1',
                         'rationale': 'Broker-reliant Core account with healthy spend but only one self-serve order. Not yet '
                                      'Phase 1 eligible.'},
 'RETURNED_CUSTOMER': {'target_behaviour': 'Re-establish the relationship and a regular buying cadence',
                       'success_measure': 'Orders in at least 2 of the next 3 months',
                       'rationale': 'Long-tenured customer that returned in H2 after no H1 spend. Re-establish relationship and '
                                    'cadence.'},
 'NEW_CUSTOMER': {'target_behaviour': 'Onboarding: repeat purchase and regular independent browsing',
                  'success_measure': '2+ orders across 2+ months within 90 days',
                  'rationale': 'New customer (tenure <= 6 months) buying only in H2. Establish a repeat buying pattern.'},
 'HEALTHY_STRONG_SELF_SERVE': {'target_behaviour': 'Maintain current browsing and purchasing; light-touch reinforcement only',
                               'success_measure': 'GMV run-rate maintained or higher; GMV in each month of the next quarter',
                               'rationale': 'Low-dependency account with growing/stable spend, recent activity and strong '
                                            'independent browsing. Reinforce what is working.'},
 'BROWSING_LOW_OFFERS': {'target_behaviour': 'Make offers on items already browsed (3+ offers)',
                         'success_measure': '3+ offers within 90 days and at least one offer-led order; GMV not lower',
                         'rationale': 'Low-dependency account browses meaningfully but makes few offers. Encourage self-directed '
                                      'negotiation.'},
 'RISING_TAIL': {'target_behaviour': 'Maintain current browsing and purchasing; light-touch reinforcement',
                 'success_measure': 'Continued monthly purchasing; crosses £2k Core line within 6 months',
                 'rationale': 'Tail account on the Rising Tail watchlist with an established, recent self-serve pattern.'},
 'RISING_TAIL_EARLY': {'target_behaviour': 'Repeat purchase in a third month to establish a pattern',
                       'success_measure': 'Order in a new month within 90 days; re-check watchlist next run',
                       'rationale': 'Tail account on the Rising Tail watchlist whose buying pattern is not yet established.'},
 'COST_TO_SERVE_ACTIVE': {'target_behaviour': 'Internal decision: keep AM coverage, move to low-touch, or automate re-ordering',
                          'success_measure': 'Decision logged; broker effort reduced without GMV loss',
                          'rationale': 'Broker-reliant but low value and still buying. Decide whether continued AM/broker effort '
                                       'is justified.'},
 'DORMANT_LOW_VALUE': {'target_behaviour': 'Automated reactivation only; no human time',
                       'success_measure': 'Any order within 90 days',
                       'rationale': 'Low-value account with no recent GMV. Avoid human time.'},
 'LONG_TAIL_STANDARD': {'target_behaviour': 'Scalable automated engagement matched to nurture sub-context',
                        'success_measure': 'Any repeat order within 90 days',
                        'rationale': 'Low-value, low-dependency account. Scalable automated engagement.'}}
