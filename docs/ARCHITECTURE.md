# Tibetan Spirit Operations — Architecture
# Last updated: 2026-04-14 | Branch: refactor/align-repo-conventions

Full operational detail lives in `docs/OPERATIONS-REFERENCE.md`. This document is the structural overview.

---

## System Overview

tibetan-spirit-ops automates operations for [tibetanspirit.com](https://tibetanspirit.com) — a Shopify D2C store selling Himalayan artisan goods (incense, singing bowls, malas, prayer flags, thangkas, statues, ritual supplies). Six specialized AI agents handle the operational surface. All customer-facing outputs require human approval before execution.

---

## Tech Stack

| Layer | Technology | Notes |
|-------|-----------|-------|
| Commerce | Shopify (GraphQL Admin API 2026-01) | Source of truth for orders, products, inventory |
| Database | Supabase/PostgreSQL (Pro tier) | Structured data + task inbox + audit trail |
| AI runtime | Claude Code + Anthropic API | Fork execution model per agent |
| Helpdesk | Intercom Essentials | CS email ingestion, knowledge base |
| Notifications | Slack #ts-operations | Internal ops alerts and approvals |
| Email | Shortwave Pro (Gmail) | CS email management |
| Observability | Langfuse (self-hosted) | Prompt versioning, cost tracking, evals |
| Infrastructure | PM2 (current) → Railway cron (planned) | Workflow scheduling |
| MCP servers | Shopify, Supabase, Slack, Gmail | Tool access for Claude Code agents |

---

## Agent Architecture

Six agents, each with a soul file, config, and domain-specific skills. All use the **fork execution model** — isolated invocations, no shared state between runs.

| Agent | Model | Budget | Role |
|-------|-------|--------|------|
| Fulfillment Manager | Opus | $2.00 | Order tracking, shipping, supplier coordination |
| Inventory Analyst | Opus | $2.00 | Stock monitoring, restock alerts, demand forecasting |
| CS Drafter | Opus | $2.00 | Email drafts via triage → enrichment → draft. NEVER auto-sends. |
| Marketing Strategist | Opus | $2.00 | Campaign briefs, content calendar, targeting |
| Catalog Curator | Opus | $5.00 | Product descriptions via evaluator-optimizer loop |
| Finance Analyst | Opus | $0.50 | Weekly P&L, COGS tracking, margin analysis |

Agent definitions: `.claude/agents/`. Skills: `agents/{agent}/skills/`.

**Shared skills** (loaded by all agents): brand-guidelines, product-knowledge, escalation-matrix, channel-config, supabase-ops-db, tibetan-calendar.

**Skill loading** is three-tier: name+description at startup (~50 tokens/skill), full body on trigger (~2K tokens), dependencies at invocation.

---

## Data Layer

Supabase PostgreSQL — source of truth for all structured data.

**Core tables:** `ts_products` (559 rows), `ts_orders` (19.4K+), `ts_customers`, `ts_inventory`, `ts_cogs`

**Three-schema structure:**
- **Registry:** companies, agents, skills, agent_skills, workflows, workflow_steps
- **Runtime:** task_inbox, workflow_runs, workflow_health, spend_records
- **Eval:** eval_suites, prompt_versions, eval_runs, eval_results

**Materialized views:** `channel_profitability_monthly`, `product_margin_detail`, `inventory_health`, `marketing_roas_trailing`

**Connection:** `lib/ts_shared/supabase_client.py` (singleton, service key, bypasses RLS)

---

## Workflow Architecture (HITL)

All workflows follow: **draft → Supabase task_inbox → Slack alert → human reviews → human sends/executes**.

| Workflow | Schedule | Approval Tier |
|----------|----------|--------------|
| `daily_summary` | 6pm daily | Auto-logged |
| `weekly_pnl` | Mon 6am | CEO review |
| `cs_email_drafts` | Every 30min | CS Lead approval |
| `inventory_alerts` | 9am daily | Ops Manager review |
| `campaign_brief` | Weekly | CEO review |
| `product_descriptions` | Manual | CEO + Ops review |

**Graduation tiers** (based on override rate):
- Tier 3: Explicit approval — all new workflows start here
- Tier 2: Draft + 4hr auto-approve — override rate < 25% for 30+ days
- Tier 1: Auto-execute, log only — override rate near-zero, extended period

---

## Infrastructure

**Current:** PM2 for local workflow scheduling.

**Planned:** Railway cron jobs trigger standalone Python workflow scripts. Each script: loads agent soul + skills → queries Supabase → calls Anthropic API with prompt caching → writes to `task_inbox` → sends Slack alert → logs to `skill_invocations`.

**Dashboard:** React PWA (`ts-command-center/`) — task inbox, health monitoring, cost tracking, workflow/agent registry, eval dashboard.

**Hook system:** Two layers — user-level hooks (universal safety, from `~/.claude/settings.json`) and project-level hooks (`.claude/hooks/`). Budget enforcement via `budget-check.sh`. Activity audit via `log-activity.sh`.

---

## Key File Map

```
tibetan-spirit-ops/
├── CLAUDE.md                     ← Project index (≤120 lines)
├── docs/
│   ├── ARCHITECTURE.md           ← This file
│   ├── CHANGELOG.md              ← Change history
│   └── OPERATIONS-REFERENCE.md  ← Full operational detail
├── agents/                       ← AI team (soul.md, config.yaml, skills/)
│   ├── shared/                   ← Cross-agent skills (6 skills)
│   └── {domain}/                 ← customer-service, operations, finance, marketing, ecommerce, category-management
├── lib/ts_shared/                ← Shared Python library (Supabase client, Claude client)
├── workflows/                    ← Cron-triggered workflow scripts
├── tests/
├── workspace/plans/              ← Implementation plans
└── .claude/
    ├── agents/                   ← Agent soul files and configs
    ├── hooks/                    ← Project-level enforcement hooks
    └── rules/                    ← Operational rules (brand-voice, supabase, org-roles, etc.)
```
