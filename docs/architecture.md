# Architecture

## Overview

```mermaid
flowchart TD
    SRC["Portfolio workbook<br/>(Accounts sheet)<br/><i>future: CRM extract</i>"]
    NEW["new_accounts batch"]

    subgraph ING["Ingestion (automated)"]
        UPS["process_new_accounts()<br/>upsert by account_id"]
        CLN["clean_data()<br/>required columns, types, DQ flags"]
    end

    subgraph RULES["Rules engine (automated, deterministic)"]
        DEP["Dependency<br/>gated 50/30/20 score + tier"]
        SEG["Segmentation<br/>behavioural segment, value tier,<br/>momentum, 9 action segments"]
        GR["Guardrails<br/>HOLD, Key sign-off, borderline,<br/>FEB_SENSITIVE, lumpy, broker inconsistency"]
        FEAT["Feature context<br/>milestones, discovery gap,<br/>recency, rising tail"]
        NBA["NBA<br/>reason code, primary_nba,<br/>execution_status, priority"]
    end

    subgraph EXEC["Execution planner (automated)"]
        PLAN["generate_execution_plan()<br/>playbook, owner role, channel,<br/>first action, follow-up,<br/>draft OR withheld reason, brief, action_state"]
        VAL["guardrail_checks()<br/>19 hard checks = 0"]
    end

    subgraph STATE["State / registry (automated)"]
        FP["fingerprint()"]
        CMP["compare_runs()<br/>change_type vs last snapshot"]
        REG[("action_registry<br/>idempotent action keys")]
        LOG[("action_log<br/>material changes only")]
        SNAP[("account_snapshot")]
        HIST[("run_history")]
    end

    subgraph UI["Streamlit UI (app.py)"]
        OVR["Portfolio overview<br/>priorities, statuses, guardrail badge,<br/>data-quality panel"]
        HQ["Human queue<br/><b>HUMAN JUDGEMENT</b>"]
        AUTO["Automated drafts<br/>preview only - never sent"]
        MIG["Migration tracking<br/>Ready / Review / Sign-off / Pre-entry"]
        CHG["Change log / reruns"]
        WF["Local workflow buttons<br/>approve / decline / in progress / completed<br/>+ workflow_audit"]
    end

    SRC --> UPS
    NEW --> UPS
    UPS --> CLN --> DEP --> SEG --> GR --> FEAT --> NBA --> PLAN
    PLAN --> FP --> CMP
    PLAN --> VAL
    VAL --> OVR
    CMP --> REG
    CMP --> LOG
    CMP --> SNAP
    FP --> HIST
    SNAP --> OVR
    SNAP --> HQ
    SNAP --> AUTO
    SNAP --> MIG
    LOG --> CHG
    HIST --> CHG
    HQ --> WF
    WF -- "action_state only" --> SNAP

    classDef human fill:#fde7c8,stroke:#b86e00,color:#3d2600
    classDef auto fill:#dbe9fb,stroke:#2a78d6,color:#0b2a4f
    class HQ,WF human
    class UPS,CLN,DEP,SEG,GR,FEAT,NBA,PLAN,VAL,FP,CMP,OVR,AUTO,MIG,CHG auto
```

**Legend:** blue nodes are automated and deterministic. Orange nodes are where a person makes a judgement. `guardrail_checks()` runs on every plan and its result is shown in the UI. A failing check is a defect to fix, not something to override. A static render is in [architecture.png](architecture.png).

## The daily loop

```mermaid
sequenceDiagram
    participant Batch as new_accounts batch
    participant Eng as fleek_engine
    participant Store as RunStore (state/)
    participant UI as app.py

    Batch->>Eng: process_new_accounts(base, batch)
    Note over Eng: update 5 existing IDs, append 45 new
    Eng->>Eng: run_analytics() + generate_execution_plan()
    Eng->>Store: fingerprint(input)
    Store-->>Eng: identical_to_previous_input?
    Eng->>Store: compare_runs(prev snapshot, current)
    Note over Store: NEW_ACCOUNT / NBA_CHANGED / PRIORITY_* /<br/>EXECUTION_STATUS_CHANGED / ENTERED|LEFT_HUMAN_QUEUE /<br/>MIGRATION_PROGRESS_CHANGED / NO_MATERIAL_CHANGE
    Eng->>Store: register new action keys only
    Eng->>Store: append log rows for material changes only
    Store-->>UI: snapshot, log, history
    UI->>Store: (optional) local action_state change + audit row
    Note over Batch,UI: identical rerun -> 0 log rows, 0 new actions, 0 duplicates,<br/>existing action_state preserved
```

## Separation of concerns

| Layer | Decides | Code |
|---|---|---|
| Rules engine | **What** should happen: `primary_nba`, `execution_status`, `attention_priority` | `pipeline.py`, `config.py` |
| Execution planner | **How** it happens: playbook, owner role, channel, draft or brief, `action_state` | `execution.py`, `playbooks.py` |
| Run layer | **Whether anything is new**: fingerprint, change type, registry, log | `runs.py` |
| Validation | **Whether the plan is safe to show**: 19 checks | `validate.py` |
| Service layer | Baseline, upsert and identical-rerun orchestration, plus local workflow transitions | `demo.py` |
| UI | Presentation only. Every number comes from the engine output. | `app.py` |

## Automated vs human

| Automated (no person needed to decide) | Human judgement (the tool prepares, a person decides) |
|---|---|
| Scoring, segmentation, guardrail flags and NBA assignment | Retention conversations (Segments 2 and 8) |
| Choosing an owner role, channel, template and follow-up day | Verify / win-back: is this churn or a normal buying cadence? |
| Drafting automated nurture, reinforce and discovery-to-offer messages (preview) | Phase 1 migration Day 0 walkthrough, plus reviews at day 45 and day 90 |
| Change detection, deduplication and the log | Manual Review (borderline, February-sensitive, lumpy or broker-inconsistent accounts) |
| Guardrail validation | Key account migration sign-off |
| Migration progress status once 90-day inputs arrive | Service Model Review (depends on AM cost data we don't have) |
| | Resolving the HOLD on ACC-005 |
| | Assigning a named owner to Self Serve accounts in the human queue |

More detail is in [human_vs_automation.md](human_vs_automation.md).

## Production path (not built)

- Replace the CSV `RunStore` with database tables: snapshot, log and registry, with a unique constraint on `action_key`.
- Take input from a CRM or warehouse extract instead of the workbook. The ingestion contract is `REQUIRED_COLUMNS` in `config.py`.
- Send only `Ready — Automated` rows through an email or CRM tool, with suppression and unsubscribe handling. Human rows stay as tasks.
- Write outcome events (sent, replied, order, 90-day monitoring) back into the snapshot so that `In Progress` and `Completed` reflect real work.
