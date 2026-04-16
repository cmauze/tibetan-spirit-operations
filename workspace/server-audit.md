# Server Audit — Tibetan Spirit Operations

Generated: 2026-04-16 | Source: Full codebase inspection of ~/code/active/tibetan-spirit-ops/

---

## Executive Summary

tibetan-spirit-ops is **production-ready** with 49K LOC, 6 agents, 9 skills, 10 rules, 4 hooks. The **only component requiring an always-on server is the Shopify webhook receiver** (FastAPI, 295 LOC). Everything else — scheduled reports, agent invocations, HITL workflows — can migrate to Cowork scheduling.

All 9 skills are candidates for extraction into the `d2c-operations-lead` plugin. The plugin gets generalized copies; tibetan-spirit-ops retains its branded originals unchanged.

---

## Component Classification

### MUST STAY SERVER

| Component | File/Location | Reason | Notes |
|-----------|--------------|--------|-------|
| FastAPI webhook receiver | `server/server.py` (295 LOC) | HTTP endpoint for Shopify order/inventory events, HMAC-validated | Dockerized for Railway, stateless |
| Supabase schema + data | `supabase/` + Supabase Pro instance | 19.4K+ orders, 559 products, HITL task_inbox, audit trail | Three-layer schema (registry/runtime/eval) |
| CCPA gate hook | `.claude/hooks/ccpa-gate.sh` (24 LOC) | Blocks gmail_send tools at invocation time (exit 2 = hard block) | CCPA ADMT compliance requirement |
| Activity log hook | `.claude/hooks/log-activity.sh` (67 LOC) | Audit trail to data/agent-runs.json | Async, fire-and-forget |
| Session context hook | `.claude/hooks/session-context.sh` (56 LOC) | Injects git state, agent activity, CS queue status | Fires on session start/resume/clear/compact |
| Slack notify hook | `.claude/hooks/slack-notify.sh` (112 LOC) | Routes notifications to #ts-operations channels | Async, rate-limited 5/hour/channel |
| Shared library | `lib/ts_shared/` (13 modules, 43KB) | Supabase client, Claude client, cost tracker, org resolution, notifications | TS-specific infrastructure |
| Agent definitions | `agents/` (6 files) | TS-specific personas with budget/tool grants, multilingual routing | Brand-specific soul files |
| Operational rules | `rules/` (10 files, 22KB) | Brand voice, cultural sensitivity, judgment frameworks | Non-negotiable, TS-specific |
| Utility scripts | `scripts/` (14 files, 3.4K LOC) | Shopify sync, COGS import, schema validation, skill validation | TS-specific operational tooling |

### MIGRATE TO COWORK (Scheduling Candidates)

| Component | Current Trigger | Cowork Model | Migration Notes |
|-----------|----------------|-------------|-----------------|
| `scripts/daily_summary.py` (274 LOC) | PM2 cron (daily 6pm) | Cowork scheduled task | Standalone script, Haiku model, outputs to Slack |
| `scripts/weekly_pnl.py` (401 LOC) | PM2 cron (Mon 6am) | Cowork scheduled task | Standalone script, Sonnet model, outputs to task_inbox |
| 6 agent invocations | Manual / script-triggered | Cowork fork execution | Already fork-based, standalone invocations |
| HITL task_inbox | Supabase polling + Slack | Cowork task management | Already structured as state machine |
| Cost tracking | Per-invocation Supabase logging | Cowork spend dashboard | Logs to spend_records table |

### EXTRACT TO PLUGIN (d2c-operations-lead)

| Skill | Generalizability | Key Generalizations Needed |
|-------|-----------------|---------------------------|
| cs-triage | HIGH | Remove TS-specific categories (Dharma guidance, Nepal supplier), replace with generic D2C categories |
| cs-pipeline (W) | HIGH | Remove brand voice references, generalize approval routing |
| shopify-query | HIGH | Already generic — parameterize store URL |
| order-inquiry | HIGH | Remove TS-specific delivery estimates (Nepal lead times) |
| fulfillment-flag | MEDIUM | Remove Nepal/Asheville routing, generalize to configurable warehouses |
| campaign-brief | HIGH | Remove TS frequency caps and prohibited tactics list, make configurable |
| restock-calc | HIGH | Remove Buddhist calendar awareness, generalize lead-time tiers |
| margin-reporting | MEDIUM | Remove TS-specific COGS categories, generalize P&L template |
| description-optimizer | MEDIUM | Extract evaluator-optimizer loop engine; TS-specific rubric stays in project |

### DEPRECATE

| Component | Status | Reason |
|-----------|--------|--------|
| `_archive/` directory | Legacy agent configs | Superseded by current 6-agent model |
| PM2 scheduling | Active but being replaced | Railway cron is target; Cowork is next step |
| Langfuse integration | Commented out in pyproject.toml | Not yet integrated, Phase 2 feature |

---

## Server Architecture Detail

### FastAPI Server (`server/server.py`)

- **Framework:** FastAPI 0.115+ with Uvicorn
- **Runtime:** Python 3.12+ with Node 20 (Agent SDK CLI requirement)
- **Deployment:** Dockerized for Railway (ephemeral sessions)
- **Health check:** HTTP GET `/health` (30s interval)
- **Endpoints:**
  - Shopify webhook receiver (HMAC signature validation)
  - Agent config routing (6 agent domains, 9 skills)
  - Skill loading from `skills/{name}/SKILL.md`
  - Claude Agent SDK worker integration
- **Dependencies:** `server/requirements.txt` — FastAPI, Uvicorn, Claude Agent SDK >=0.1.48, Supabase >=2.0, python-dotenv, httpx

### Supabase Schema (Three-Layer)

**Registry Layer** (what exists):
- `companies`, `agents`, `skills`, `agent_skills`, `workflows`

**Runtime Layer** (what happens):
- `task_inbox` (HITL state machine), `workflow_runs`, `workflow_health`, `spend_records`, `skill_invocations`

**Eval Layer** (experimental):
- `eval_suites`, `prompt_versions`, `eval_runs`, `eval_results`

**Business Data** (pre-existing):
- `ts_products` (559 rows), `ts_orders` (19.4K+), `ts_customers`, `ts_inventory`, `ts_cogs`

**Materialized Views:**
- `channel_profitability_monthly`, `product_margin_detail`, `inventory_health`, `marketing_roas_trailing`

---

## Collaborator Impact Assessment

| Role | Person | Daily Usage | Plugin Extraction Impact |
|------|--------|-------------|------------------------|
| CEO | Chris | Approvals, reports | **None** — plugin is a copy, not a move |
| Ops Manager | Jothi | Orders, inventory, CS drafts | **None** — tibetan-spirit-ops unchanged |
| Spiritual Director | Dr. Hun Lye | Content review (email only) | **None** |
| Warehouse Manager | Fiona | Pick/pack/ship (Dashboard) | **None** |
| Mexico Fulfillment | Omar | LatAm orders (email) | **None** |

**Verdict: Zero collaborator impact.** Plugin extraction copies skills out; source system is unchanged.

---

## Cowork Migration Recommendations (Future Work)

1. **Immediate:** Migrate `daily_summary.py` and `weekly_pnl.py` from PM2 to Cowork scheduled tasks
2. **Short-term:** Move agent invocations to Cowork fork execution (already fork-based, minimal changes)
3. **Medium-term:** Replace Supabase `task_inbox` polling with Cowork task management
4. **Keep:** Shopify webhook receiver on Railway — Cowork cannot receive external webhooks
5. **Keep:** All 4 hooks — must fire at Claude Code tool-invocation time

---

## Compliance Notes

- **CCPA ADMT:** cs-drafter drafts only, never sends. Enforced by ccpa-gate.sh (exit 2). This constraint carries into the plugin as a documented requirement, not a hook.
- **Cultural escalation:** Uncertain dharma content → Spiritual Director. This is TS-specific and stays in the project, not the plugin.
- **PII:** No customer data, real names, or brand-specific secrets in plugin skills.
- **Frequency caps:** 2 promo emails/month is TS policy. Plugin version makes this configurable.

---

## Verification of Planning Doc Claim

> "Only tibetan-spirit-ops has genuine server needs (Shopify webhook receiver). Everything else is replaceable by Cowork scheduling."

**CONFIRMED.** The Shopify webhook receiver (`server/server.py`) is the only component requiring an always-on HTTP endpoint. All scheduled tasks, agent invocations, and HITL workflows are standalone and can migrate to Cowork.
