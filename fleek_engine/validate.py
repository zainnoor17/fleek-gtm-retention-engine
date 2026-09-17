"""Hard execution guardrails. Every check returns the number of violating rows (must be 0)."""
import re

import pandas as pd

from . import config as C

BANNED_PHRASES = r"churn|stopped buying|algorithm|dependency|migrat|score|noticed you|broker|account manager effort|cost"
BENEFIT_CLAIMS = r"increase|boost|grow|more sales|better|profit|revenue|margin|guarantee"
CHAT_VIDEO = r"\bchat|video"


def _words(s: str) -> int:
    body = s.split("\n\nBest,")[0]
    return len(re.findall(r"[A-Za-z']+", body))


def guardrail_checks(e: pd.DataFrame) -> pd.DataFrame:
    drafts = e["draft_customer_message"].fillna("")
    has_draft = drafts != ""
    seg = e["action_segment"].str[0]
    growth = e["primary_nba"].isin(C.GROWTH_NBAS)
    checks = {
        "Every account has exactly one row": int(e["account_id"].duplicated().sum()),
        "Every account has primary_nba / execution_status / priority / action_state / owner": int(
            e[["primary_nba", "execution_status", "attention_priority", "action_state", "owner_role"]].isin(["", None]).any(axis=1).sum()
            + e[["primary_nba", "execution_status", "attention_priority", "action_state", "owner_role"]].isna().any(axis=1).sum()),
        "HOLD accounts with any outbound draft": int((e["execution_status"].str.startswith("HOLD") & (has_draft | (e["secondary_test_draft"] != ""))).sum()),
        "Sign-off accounts with a migration draft before sign-off": int(((e["execution_status"] == "Human Sign-Off Required") & has_draft).sum()),
        "Human Review Required with automated outbound": int(((e["execution_status"] == "Human Review Required") & (has_draft | e["automation_eligible"])).sum()),
        "Segments 2/3/8 with automated action or growth nudge": int((seg.isin(["2", "3", "8"]) & ((e["delivery_mode"] == "Automated") | growth)).sum()),
        "Service Model Review with a customer draft": int(((e["primary_nba"] == "Service Model Review") & has_draft).sum()),
        "Recent Inactivity with automated growth action": int(((e["recent_activity_status"] == "Recent Inactivity") & growth & e["automation_eligible"]).sum()),
        "Broker-Reliant with automated growth nudge": int(((e["behavioural_segment"] == "Broker-Reliant") & growth).sum()),
        "Key Migration Candidate not on sign-off": int((e["key_account_signoff_required"] & (e["execution_status"] != "Human Sign-Off Required")).sum()),
        "Drafts / targets encouraging chat or video": int(drafts.str.contains(CHAT_VIDEO, case=False, regex=True).sum()
                                                          + e["secondary_test_draft"].str.contains(CHAT_VIDEO, case=False, regex=True).sum()),
        "Drafts with banned phrases (churn, algorithm, dependency, migration, score...)": int(
            drafts.str.contains(BANNED_PHRASES, case=False, regex=True).sum()),
        "Range Expansion drafts claiming a benefit": int(e["secondary_test_draft"].str.contains(BENEFIT_CLAIMS, case=False, regex=True).sum()),
        "Range drafts sent to holdout arm": int(((e["secondary_test_arm"] == "Holdout") & (e["secondary_test_draft"] != "")).sum()),
        "Drafts containing internal numbers (£, %, digits)": int(drafts.str.contains(r"[£%0-9]", regex=True).sum()),
        "Drafts outside 40-100 words": int(drafts[has_draft].map(_words).pipe(lambda w: ((w < 40) | (w > 100)).sum())),
        "Drafts with unfilled product placeholder": int(drafts.str.contains("{product}", regex=False).sum()),
        "Human-queue accounts without an internal brief": int(((e["execution_status"] != "Ready — Automated") & (e["internal_task_brief"] == "")).sum()),
        "Self Serve human actions not flagged for a named owner": int(((e["ownership"] == "Self Serve") & (e["owner_role"] != "Automation") & ~e["named_owner_required"]).sum()),
    }
    return pd.DataFrame({"check": list(checks), "violations": list(checks.values())})
