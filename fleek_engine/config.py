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
