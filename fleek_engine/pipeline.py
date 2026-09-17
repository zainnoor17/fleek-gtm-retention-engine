"""Analytical chain (Stages 1-4B). Vectorised pandas; no account-specific logic."""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import config as C


# ----------------------------------------------------------------------------- load / clean
def load_data(path: str, sheet: str = "Accounts") -> pd.DataFrame:
    return pd.read_excel(path, sheet_name=sheet)


def clean_data(raw: pd.DataFrame) -> pd.DataFrame:
    """Validate schema, normalise types, de-duplicate on account_id (last row wins).

    The source is never modified; a cleaned copy is returned.
    """
    missing = [c for c in C.REQUIRED_COLUMNS if c not in raw.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    df = raw[C.REQUIRED_COLUMNS].copy()
    df["account_id"] = df["account_id"].astype(str).str.strip()
    num = [c for c in C.REQUIRED_COLUMNS if c not in
           ("account_id", "ownership", "buyer_persona", "region", "country", "account_status", "gmv_trend_pct")]
    df[num] = df[num].apply(pd.to_numeric, errors="coerce").fillna(0)
    df["account_status"] = df["account_status"].where(df["account_status"].notna(), None)
    df = df.drop_duplicates("account_id", keep="last").sort_values("account_id").reset_index(drop=True)
    # gmv_trend_pct is retained for reference only - never used in any rule (Stage 2 finding).
    return df


# ----------------------------------------------------------------------------- Stage 1
def _broker_band(p: pd.Series) -> pd.Series:
    b = C.BROKER_BANDS
    return pd.Series(np.select([p <= b[0], p < b[1], p < b[2], p < b[3]], [0, 25, 50, 75], 100), index=p.index)


def score_dependency(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    a, o = d["app_active_days_6m"], d["make_an_offer_6m"]
    d["sub_broker"] = _broker_band(d["broker_reliance_pct"])
    d["sub_app"] = np.select([a > C.APP_BANDS[0], a >= C.APP_BANDS[1], a >= C.APP_BANDS[2], a >= C.APP_BANDS[3]], [0, 25, 50, 75], 100)
    d["sub_offer"] = np.select([o >= C.OFFER_BANDS[0], o >= C.OFFER_BANDS[1], o == C.OFFER_BANDS[2], o == C.OFFER_BANDS[3]], [0, 25, 50, 75], 100)
    w = C.DEP_WEIGHTS
    raw = w["broker"] * d["sub_broker"] + w["app"] * d["sub_app"] + w["offer"] * d["sub_offer"]
    d["dependency_score"] = np.where(d["broker_reliance_pct"] <= C.BROKER_GATE, 0.0, raw)
    d["dependency_tier"] = _tier(d["dependency_score"])
    return d


def _tier(score: pd.Series) -> np.ndarray:
    return np.select([score >= C.TIER_HIGH, score >= C.TIER_MEDIUM], ["High", "Medium"], "Low")


# ----------------------------------------------------------------------------- Stage 2/3
def _momentum(h1: pd.Series, h2: pd.Series) -> np.ndarray:
    with np.errstate(divide="ignore", invalid="ignore"):
        ch = np.where(h1 > 0, h2 / h1.replace(0, np.nan) - 1, np.nan)
    return np.select(
        [(h1 > 0) & (h2 == 0), (h1 == 0) & (h2 > 0), (h1 == 0) & (h2 == 0), ch >= C.MOMENTUM_BAND, ch < -C.MOMENTUM_BAND],
        ["Lapsed", C.H2_ONLY, "No GMV", "Growing", "Declining"], "Stable")


def build_segments(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    g = d["gmv_total_6m"]
    d["value_tier"] = np.select([g >= C.KEY_GMV, g >= C.CORE_GMV], ["Key", "Core"], "Tail")
    d["h1_gmv"] = d[C.H1_MONTHS].sum(axis=1)
    d["h2_gmv"] = d[C.H2_MONTHS].sum(axis=1)
    d["h2_vs_h1"] = np.where(d["h1_gmv"] > 0, d["h2_gmv"] / d["h1_gmv"].replace(0, np.nan) - 1, np.nan)
    d["momentum"] = _momentum(d["h1_gmv"], d["h2_gmv"])
    d["active_months"] = (d[C.MONTHS] > 0).sum(axis=1)
    low, am, ss = d["dependency_tier"] == "Low", d["ownership"] == "Account Managed", d["ownership"] == "Self Serve"
    d["behavioural_segment"] = np.select(
        [~low, low & am, low & ss], ["Broker-Reliant", "AM-Owned / Self-Serving", "Self-Serve"], "UNASSIGNED")
    d["action_segment"] = _action_segment(d["behavioural_segment"] == "Broker-Reliant", low, d["value_tier"], d["momentum"])
    return d


def _action_segment(br: pd.Series, low: pd.Series, value: pd.Series, mom: pd.Series) -> np.ndarray:
    kc, tail = value != "Tail", value == "Tail"
    healthy = mom.isin(["Growing", "Stable"])
    conds = [br & kc & healthy, br & kc & (mom == "Declining"), br & kc & (mom == "Lapsed"), br & kc & (mom == C.H2_ONLY),
             br & tail, low & kc & healthy, low & kc & (mom == C.H2_ONLY),
             low & kc & mom.isin(["Declining", "Lapsed"]), low & tail]
    return np.select(conds, [C.SEGMENTS[i] for i in range(1, 10)], "UNASSIGNED")


# ----------------------------------------------------------------------------- Stage 3.1
def apply_guardrails(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    h1, h2 = d["h1_gmv"], d["h2_gmv"]
    both = (h1 > 0) & (h2 > 0)
    mc = d["action_segment"] == C.SEGMENTS[1]
    d["lifecycle_context"] = np.where((h1 == 0) & (h2 > 0),
                                      np.where(d["tenure_months"] <= C.NEW_CUSTOMER_MAX_TENURE, "New Customer", "Returned Customer"),
                                      "Existing Customer")
    d["key_account_signoff_required"] = mc & (d["value_tier"] == "Key")
    x = d["h2_vs_h1"]
    d["borderline_momentum"] = both & (((x - C.MOMENTUM_BAND).abs() <= C.BORDERLINE_BAND) | ((x + C.MOMENTUM_BAND).abs() <= C.BORDERLINE_BAND))
    # February sensitivity: same H1, Dec+Jan only, compared as monthly averages
    dj = d["gmv_dec"] + d["gmv_jan"]
    d["dec_jan_gmv"] = dj
    with np.errstate(divide="ignore", invalid="ignore"):
        chx = (dj / 2) / (h1 / 3).replace(0, np.nan) - 1
    d["momentum_ex_feb"] = np.select(
        [(h1 == 0) & (dj == 0), dj == 0, h1 == 0, chx >= C.MOMENTUM_BAND, chx < -C.MOMENTUM_BAND],
        ["No activity ex-Feb", "Lapsed", C.H2_ONLY, "Growing", "Declining"], "Stable")
    grp = lambda s: s.replace({"Growing": "Healthy", "Stable": "Healthy"})
    d["february_sensitive"] = grp(d["momentum"]) != grp(pd.Series(d["momentum_ex_feb"], index=d.index))
    d["lapse_context"] = np.where(d["momentum"] != "Lapsed", "N/A",
                                  np.where((d["orders_6m"] <= C.LAPSE_ONEOFF_MAX_ORDERS) | (d["active_months"] <= C.LAPSE_ONEOFF_MAX_MONTHS),
                                           C.ONE_OFF, C.ESTABLISHED))
    # implied broker reliance from order counts (provided % stays the source of truth)
    tot = d["manual_orders"] + d["self_serve_orders"]
    imp = np.where(tot > 0, 100 * d["manual_orders"] / tot.replace(0, np.nan), d["broker_reliance_pct"])
    imp = pd.Series(imp, index=d.index)
    d["implied_broker_pct"] = imp
    d["broker_pct_gap"] = (d["broker_reliance_pct"] - imp).round(0)
    d["implied_sub_broker"] = _broker_band(imp)
    w = C.DEP_WEIGHTS
    d["implied_score"] = np.where(imp <= C.BROKER_GATE, 0.0,
                                  w["broker"] * d["implied_sub_broker"] + w["app"] * d["sub_app"] + w["offer"] * d["sub_offer"])
    d["implied_tier"] = _tier(d["implied_score"])
    d["material_broker_inconsistency"] = (((d["broker_reliance_pct"] <= C.BROKER_GATE) != (imp <= C.BROKER_GATE))
                                          | (d["sub_broker"] != d["implied_sub_broker"]) | (d["dependency_tier"] != d["implied_tier"]))
    ibr = d["implied_tier"] != "Low"
    d["implied_action_segment"] = _action_segment(ibr, ~ibr, d["value_tier"], d["momentum"])
    d["implied_action_change"] = d["implied_action_segment"] != d["action_segment"]
    # data-quality flags
    d["flag_low_confidence"] = d["orders_6m"] <= C.LOW_CONFIDENCE_MAX_ORDERS
    d["flag_single_month"] = d["active_months"] <= 1
    d["flag_duplicate"] = d["account_status"].fillna("").eq("Duplicate")
    d["flag_missing_status"] = d["account_status"].isna()
    d["flag_raw_broker_gap"] = d["broker_pct_gap"].abs() > C.RAW_BROKER_GAP
    # Phase 1 cohort (Stage 3.1 + Stage 5 lumpy-cadence refinement)
    d["buyer_cadence"] = np.where((d["active_months"] >= C.REGULAR_MIN_MONTHS) & (d["orders_6m"] >= C.REGULAR_MIN_ORDERS), "Regular", "Lumpy")
    d["phase1_cohort_eligible"] = (mc & (d["value_tier"] == "Core") & (d["orders_6m"] >= C.PHASE1_MIN_ORDERS)
                                   & (d["self_serve_orders"] >= C.PHASE1_MIN_SELF_SERVE) & ~d["flag_duplicate"])
    warn = d["material_broker_inconsistency"] | d["borderline_momentum"] | d["february_sensitive"] | (d["buyer_cadence"] == "Lumpy")
    d["phase1_rollout_status"] = np.where(~d["phase1_cohort_eligible"], "Not Eligible", np.where(warn, "Manual Review", "Ready"))
    return d


# ----------------------------------------------------------------------------- Stage 4A
def build_feature_context(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    low = d["dependency_tier"] == "Low"
    app, pdp, off, orders = d["app_active_days_6m"], d["pdp_views_6m"], d["make_an_offer_6m"], d["orders_6m"]
    share = d["bundle_gmv_share_pct"]
    d["basket_type"] = np.select([share == 100, share == 0], ["Bundle-only", "Handpick-only"], "Mixed")
    d["m1_pdp_met"], d["m2_app_met"], d["m3_offers_met"] = pdp >= C.M1_PDP, app >= C.M2_APP, off >= C.M3_OFFERS
    engaged = (app >= C.ENGAGED_APP) | (pdp >= C.ENGAGED_PDP)
    d["archetype"] = np.select(
        [d["behavioural_segment"] == "Broker-Reliant",
         low & (d["value_tier"] != "Tail") & d["momentum"].isin(["Declining", "Lapsed"]) & engaged,
         low & (app >= C.ENGAGED_APP) & (pdp >= C.ENGAGED_PDP) & (off >= C.INDEP_OFFERS) & (orders >= C.INDEP_ORDERS),
         low & engaged & (orders <= 2),
         low & (orders == 1) & ~engaged],
        ["Broker-led, product-blind", "Engaged but shrinking (Key/Core)", "Independent browser-buyer",
         "Engaged, not converting", "One-off low-touch buyer"], "Light-touch repeat buyer")
    healthy = d["momentum"].isin(["Growing", "Stable"])
    d["rising_tail_watchlist"] = (low & (d["value_tier"] == "Tail") & (d["gmv_total_6m"] >= C.RISING_GMV) & (orders >= C.RISING_ORDERS)
                                  & (healthy | ((d["momentum"] == C.H2_ONLY) & (d["active_months"] >= 2)))
                                  & ((app >= C.RISING_APP) | (off >= C.RISING_OFFERS)))
    return d


# ----------------------------------------------------------------------------- Stage 4B
def assign_nba(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    low = d["dependency_tier"] == "Low"
    healthy = d["momentum"].isin(["Growing", "Stable"])
    recent = (d["gmv_jan"] > 0) | (d["gmv_feb"] > 0)
    thin = (d["orders_6m"] <= C.LAPSE_ONEOFF_MAX_ORDERS) | (d["active_months"] <= C.LAPSE_ONEOFF_MAX_MONTHS)
    d["recent_activity_status"] = np.select([recent, thin], ["Recently Active", "No Meaningful History"], "Recent Inactivity")
    ra, inactive = d["recent_activity_status"] == "Recently Active", d["recent_activity_status"] == "Recent Inactivity"
    d["discovery_gap"] = low & (d["pdp_views_6m"] >= C.DTO_PDP) & (d["make_an_offer_6m"] < C.DTO_MAX_OFFERS)
    d["strong_pattern"] = low & healthy & ra & (d["pdp_views_6m"] >= C.M1_PDP) & (d["active_months"] >= C.REINFORCE_MIN_MONTHS)
    d["h2_max_share"] = np.where(d["h2_gmv"] > 0, d[C.H2_MONTHS].max(axis=1) / d["h2_gmv"].replace(0, np.nan), np.nan)

    seg = d["action_segment"].str[0]
    new = d["lifecycle_context"] == "New Customer"
    est = d["lapse_context"] == C.ESTABLISHED
    lt_dto = d["discovery_gap"] & ra & (healthy | (d["momentum"] == C.H2_ONLY)) & (d["orders_6m"] >= C.LT_DTO_MIN_ORDERS)
    rt = d["rising_tail_watchlist"]
    conds = [
        (seg == "1") & (d["value_tier"] == "Key"),
        (seg == "1") & (d["phase1_rollout_status"] == "Ready"),
        (seg == "1") & (d["phase1_rollout_status"] == "Manual Review"),
        seg == "1",
        seg == "2",
        (seg == "3") & est, seg == "3",
        (seg == "4") & new, seg == "4",
        (seg == "5") & ra, seg == "5",
        (seg == "6") & inactive, (seg == "6") & d["discovery_gap"], seg == "6",
        (seg == "7") & inactive, (seg == "7") & new, seg == "7",
        (seg == "8") & (d["momentum"] == "Declining") & (d["archetype"] == "Engaged but shrinking (Key/Core)"),
        (seg == "8") & (d["momentum"] == "Declining"), (seg == "8") & est, seg == "8",
        (seg == "9") & rt & ~ra, (seg == "9") & rt & d["discovery_gap"], (seg == "9") & rt & d["strong_pattern"], (seg == "9") & rt,
        (seg == "9") & lt_dto,
    ]
    codes = ["MIGRATION_KEY_SIGNOFF", "MIGRATION_PHASE1_READY", "MIGRATION_PHASE1_REVIEW", "MIGRATION_PRE_ENTRY",
             "DECLINING_KEY_CORE", "LAPSED_ESTABLISHED", "LAPSED_THIN_HISTORY", "NEW_CUSTOMER", "RETURNED_CUSTOMER",
             "COST_TO_SERVE_ACTIVE", "DORMANT_LOW_VALUE", "RECENT_INACTIVITY", "BROWSING_LOW_OFFERS", "HEALTHY_STRONG_SELF_SERVE",
             "RECENT_INACTIVITY", "NEW_CUSTOMER", "RETURNED_CUSTOMER", "ENGAGED_BUT_SHRINKING", "DECLINING_KEY_CORE",
             "LAPSED_ESTABLISHED", "LAPSED_THIN_HISTORY", "DORMANT_LOW_VALUE", "BROWSING_LOW_OFFERS", "RISING_TAIL",
             "RISING_TAIL_EARLY", "BROWSING_LOW_OFFERS"]
    d["nba_reason_code"] = np.select(conds, codes, "LONG_TAIL_STANDARD")
    lib = C.NBA_LIBRARY
    d["primary_nba"] = d["nba_reason_code"].map(lambda c: lib[c][0])
    d["delivery_mode"] = d["nba_reason_code"].map(lambda c: lib[c][1])
    growth = d["primary_nba"].isin(C.GROWTH_NBAS)

    d["execution_status"] = np.select(
        [d["flag_duplicate"], d["key_account_signoff_required"], d["phase1_rollout_status"] == "Manual Review",
         (d["delivery_mode"] == "Automated") & (d["implied_action_change"] | (growth & (d["february_sensitive"] | d["borderline_momentum"]))),
         d["delivery_mode"] == "Human", d["delivery_mode"] == "Hybrid"],
        ["HOLD — Critical Data Issue", "Human Sign-Off Required", "Human Review Required", "Human Review Required",
         "Ready — Human", "Ready — Hybrid"], "Ready — Automated")
    default_p = d["nba_reason_code"].map(lambda c: lib[c][2])
    d["attention_priority"] = np.select(
        [d["flag_duplicate"], (d["nba_reason_code"] == "BROWSING_LOW_OFFERS") & (d["value_tier"] == "Tail"),
         (d["execution_status"] == "Human Review Required") & (default_p == "P4")],
        ["P0", "P3", "P3"], default_p)
    single = d["basket_type"] != "Mixed"
    d["secondary_test"] = np.where(
        low & healthy & ra & single & growth & (d["execution_status"] == "Ready — Automated") & ((d["value_tier"] != "Tail") | rt),
        np.where(d["basket_type"] == "Bundle-only", "Range Expansion Test — trial handpick", "Range Expansion Test — trial bundles"), "")
    is_nurture = d["primary_nba"] == "Automated Nurture"
    d["nurture_subcontext"] = np.where(~is_nurture, "", np.select(
        [d["nba_reason_code"] == "DORMANT_LOW_VALUE", d["nba_reason_code"] == "RISING_TAIL_EARLY", new,
         d["lifecycle_context"] == "Returned Customer", d["momentum"] == "Lapsed",
         d["archetype"] == "Engaged, not converting", d["archetype"] == "One-off low-touch buyer", d["archetype"] == "Light-touch repeat buyer"],
        ["Dormant", "Rising tail – early pattern", "New customer onboarding", "Returned customer", "Dormant",
         "Engaged, not converting", "One-off purchaser", "Light-touch repeat buyer"], "Standard long tail"))
    mc = seg == "1"
    d["self_serve_share"] = d["self_serve_orders"] / d["orders_6m"].replace(0, np.nan)
    d["usual_gap_months"] = np.where(mc, np.round(6 / d["active_months"].replace(0, np.nan)), np.nan)
    d["guardrail_codes"] = _guardrail_codes(d, mc)
    d["migration_progress_status"] = np.where(mc, "Baseline", "N/A")
    return d


def _guardrail_codes(d: pd.DataFrame, mc: pd.Series) -> pd.Series:
    parts = [
        (d["flag_duplicate"], "CRITICAL_DATA_BLOCKER"),
        (d["key_account_signoff_required"], "KEY_SIGNOFF"),
        (d["phase1_rollout_status"] == "Manual Review", "PHASE1_MANUAL_REVIEW"),
        (mc & (d["buyer_cadence"] == "Lumpy"), "LUMPY_CADENCE"),
        (d["borderline_momentum"], "BORDERLINE_MOMENTUM"),
        (d["february_sensitive"], "FEB_SENSITIVE"),
        (d["material_broker_inconsistency"] & ~d["implied_action_change"], "MATERIAL_BROKER_INCONSISTENCY"),
        (d["material_broker_inconsistency"] & d["implied_action_change"], "MATERIAL_BROKER_INCONSISTENCY (segment would change)"),
        ((d["orders_6m"] >= 3) & (d["h2_gmv"] > 0) & (d["h2_max_share"].fillna(0) >= C.SPIKE_SHARE), "H2_SINGLE_MONTH_SPIKE"),
        ((d["gmv_jan"] > 0) & (d["gmv_feb"] == 0), "NO_FEB_GMV (Feb unconfirmed)"),
        (d["flag_low_confidence"], "LOW_CONFIDENCE"),
    ]
    out = pd.Series("", index=d.index)
    for mask, code in parts:
        out = out + np.where(mask, code + "; ", "")
    return out.str.rstrip("; ")


def migration_progress(d: pd.DataFrame, monitoring: pd.DataFrame | None = None) -> pd.Series:
    """Update migration_progress_status from 90-day monitoring inputs (account_id, days, pdp, app, offers,
    orders, self_serve_orders, gmv). Without inputs every Migration Candidate stays at Baseline."""
    status = d["migration_progress_status"].copy()
    if monitoring is None or monitoring.empty:
        return status
    m = d[["account_id", "buyer_cadence", "gmv_total_6m", "usual_gap_months", "self_serve_share"]].merge(monitoring, on="account_id", how="inner")
    regular = m["buyer_cadence"] == "Regular"
    breach = np.where(regular, (m["days"] >= C.GMV_GUARDRAIL_FIRST_DAY) & (m["gmv"] < C.GMV_GUARDRAIL_SHARE * m["gmv_total_6m"] / 180 * m["days"]),
                      (m["days"] >= m["usual_gap_months"] * 30) & (m["orders"] == 0))
    cap = (m["pdp"] >= C.CAP_PDP) & (m["app"] >= C.CAP_APP) & (m["self_serve_orders"] >= 1) & (m["self_serve_orders"] / m["orders"].clip(lower=1) > m["self_serve_share"])
    prog = (m["pdp"] >= C.PROG_PDP) | (m["app"] >= C.PROG_APP)
    new = np.select([breach, cap, prog, m["days"] >= C.WINDOW_DAYS],
                    ["At Risk", "Self-Serve Capability Demonstrated", "Progressing", "At Risk"], "Baseline")
    upd = pd.Series(new, index=m["account_id"])
    idx = d["account_id"].isin(upd.index)
    status[idx] = d.loc[idx, "account_id"].map(upd)
    return status


def run_analytics(raw: pd.DataFrame) -> pd.DataFrame:
    """Full Stage 1-4B chain."""
    d = clean_data(raw)
    d = score_dependency(d)
    d = build_segments(d)
    d = apply_guardrails(d)
    d = build_feature_context(d)
    d = assign_nba(d)
    return d
