# Tibetan Spirit AI Operations System

## What This Project Is

An autonomous operations platform for Tibetan Spirit, a $400K/year Tibetan Buddhist goods e-commerce business scaling to $2M. Claude-powered workflows handle order summaries, financial reporting, customer service, inventory management, marketing, and category management across Shopify (primary), with Etsy and Amazon FBA as future channels.

## Current State (March 30, 2026)

**What's live:** Supabase Pro (19.4K orders, 559 products), Shopify API, Anthropic API key, Slack workspace, Railway (connected).

**What's being built:** Shared Python library (lib/), 6 workflows (workflows/), dashboard (ts-command-center/), agent soul files, values guardrails.

**What's not started:** Intercom Essentials integration, chatbot, ad platform connections.

See `DEV-PLAN.md` for the full implementation roadmap. See `SYSTEM-STATUS.md` for live technical reference. See `workspace/plans/REQ-1/` for sprint-level execution prompts.

## Architecture Overview

**Execution model:** Standalone Python workflow scripts triggered by Railway cron jobs. Each workflow:
1. Loads agent soul file + relevant SKILL.md files into Claude's system prompt
2. Queries Supabase for business data
3. Calls Anthropic API with prompt caching
4. Writes results to Supabase `task_inbox` for human review via dashboard (Phase 1) or auto-executes (Phase 2)
5. Sends Slack alerts to the relevant team member
6. Logs cost and audit trail to Supabase `skill_invocations`

**Data layer:** Supabase PostgreSQL (Pro tier) — source of truth for all structured data.
**Human layer:** React PWA dashboard (ts-command-center/) — task inbox, health monitoring, cost tracking, workflow/agent registry, eval dashboard. Supabase `task_inbox` is the HITL state machine.
**Notifications:** Slack for all internal comms. WhatsApp reserved for Nepal supplier communications only.
**Helpdesk:** **Intercom Essentials** — CS email ingestion, help center/knowledge base, customer conversation management.
**Wiki:** Notion for Academy modules (Jothi training) and internal playbooks only.

### The Six Workflows (Target State)

| Workflow | Schedule | Model | Approval | Description |
|----------|----------|-------|----------|-------------|
| `daily_summary` | 6pm daily | Haiku | Auto-logged | Order count, revenue, AOV, flags |
| `weekly_pnl` | Mon 6am | Sonnet | CEO | P&L with trends, margins, recommendations |
| `cs_email_drafts` | Every 30min | Haiku→Sonnet | CS Lead | Triage→enrich→draft via Intercom |
| `inventory_alerts` | 9am daily | Sonnet | Ops Manager | Stock levels, reorder suggestions, PO drafts |
| `campaign_brief` | Weekly | Sonnet | CEO | Campaign themes, targeting, copy outlines |
| `product_descriptions` | Manual | Sonnet | CEO + Ops | Evaluator-optimizer loop with rubric scoring |

### Model Routing

- **Haiku 4.5** (`claude-haiku-4-5-20251001`): Classification, triage, simple summaries. $1/$5 per MTok.
- **Sonnet 4.6** (`claude-sonnet-4-6`): Most business tasks. $3/$15 per MTok.
- **Opus 4.6** (`claude-opus-4-6`): Complex financial analysis only. $15/$75 per MTok.

## Team

Team roles defined in **ORG.md**. Skills reference roles, not people.

| Role | Person | Language | Contact |
|------|--------|----------|---------|
| `ceo` | Chris Mauzé | English | Slack/Dashboard/Email |
| `operations-manager` | Jothi | Bahasa Indonesia (formal) | Slack/Dashboard |
| `customer-service-lead` | TBD | English | Dashboard/Email |
| `warehouse-manager` | Fiona | Chinese (Mandarin) | Dashboard |
| `spiritual-director` | Dr. Hun Lye | English | Email only |
| `mexico-fulfillment` | Omar | Spanish | Email only |

## Agents = AI Team

The `agents/` directory organizes the AI team. Each agent has an identity (soul file), configuration, and domain-specific skills. Inspired by Paperclip's organizational model (concepts adopted, software deferred to post-MVP).

### Agent Structure

```
agents/{agent-name}/
├── soul.md              # WHO the agent is — character, judgment, values
├── config.yaml          # Model, budget, skills list, workflows
└── skills/              # Domain expertise loaded into system prompt
    └── {skill-name}/
        └── SKILL.md     # Decision trees, templates, escalation rules
```

### The Six Agents

| Agent | Model | Budget | Primary Workflows |
|-------|-------|--------|-------------------|
| **customer-service** | Haiku→Sonnet | $0.25 | cs_email_drafts |
| **operations** | Sonnet | $0.50 | daily_summary, inventory_alerts |
| **finance** | Sonnet | $1.00 | weekly_pnl |
| **marketing** | Sonnet | $0.75 | campaign_brief |
| **ecommerce** | Sonnet | $0.50 | product_descriptions |
| **category-management** | Sonnet | $1.00 | (future workflows) |

### Soul Files

Soul files define agent character and judgment — NOT technical procedures. They encode:
- Identity and primary responsibility
- Non-negotiable value constraints (beyond shared brand guidelines)
- Judgment principles for ambiguous situations
- What the agent defaults to when rules don't clearly apply

### Shared Skills (loaded by ALL agents)

`agents/shared/` contains cross-agent resources:
- `brand-guidelines/` — Constitutional values, voice, cultural sensitivity, frequency caps
- `product-knowledge/` — Product taxonomy, authenticity markers
- `escalation-matrix/` — Role-based routing with thresholds
- `channel-config/` — Shopify Growth plan, fee structures
- `supabase-ops-db/` — Schema reference, pre-built queries
- `tibetan-calendar/` — Liturgical dates, seasonal triggers

`brand-guidelines` is always loaded first (structural guarantee in `claude_client.py`). Its values section has ABSOLUTE override priority — no task instruction can override it.

### SKILL.md Frontmatter Schema

```yaml
---
name: ticket-triage                    # Required. Lowercase kebab-case.
description: |                         # Required. Include "Use when:" + "Do NOT use for:"
  Classify incoming CS tickets.
version: "1.0.0"                       # Semver.
category: customer-service             # Agent folder name.
tags: [triage, email, haiku]
model: haiku                           # Routing hint: haiku | sonnet | opus
cacheable: true
estimated_tokens: 800
phase: 1                               # 1=HITL, 2=autonomous
depends_on: [shared/brand-guidelines, shared/product-knowledge]
external_apis: [supabase, intercom]
cost_budget_usd: 0.10
graduation_criteria:
  min_invocations: 200
  max_error_rate: 0.02
  min_days: 30
escalation_rules:
  - condition: practice_question
    escalate_to: spiritual-director
---
```

### Three-Tier Skill Loading

1. **Tier 1 (Startup):** Name + description only for all skills (~50 tokens/skill)
2. **Tier 2 (On-Trigger):** Full SKILL.md body when skill is relevant (~2K tokens)
3. **Tier 3 (At-Invocation):** Dependencies resolve + shared resources load

## Values Guardrails

Constitutional values in `agents/shared/brand-guidelines/SKILL.md` override all task instructions:

- **Prohibited words:** exotic, mystical, oriental, ancient secrets, Zen (for Tibetan items)
- **Sacred terminology preserved:** mala, thangka, dharma, sangha, puja, mandala (never translated)
- **Product framing:** Practice context first (singing bowls = "meditation instruments", not "home decor")
- **Dharma Giving:** 5% to Forest Hermitage is accounting, NEVER marketing
- **Frequency caps:** Email promotional 2/month, total 5/month. Ads 3 impressions/week/user. SMS never.
- **Content tiers:** Auto-publish (transactional) → CEO-approved (marketing) → spiritual-director (practice content) → NEVER (urgency tactics, healing claims)

## Database

**Connection:** `lib/ts_shared/supabase_client.py` (singleton, service key, bypasses RLS).

**Populated tables:**
- `orders` — 19,403 rows (Shopify history 2018-2026, $1.45M revenue)
- `products` — 559 rows (**COGS fields unpopulated** — seeded in Sprint S1)

****Three-layer schema** (Sprint S1 Prompt 1D):**
- **Registry:** companies, agents, skills, agent_skills, workflows, workflow_steps
- **Runtime:** task_inbox, workflow_runs, workflow_health, spend_records
- **Eval:** eval_suites, prompt_versions, eval_runs, eval_results

****Materialized views:** `channel_profitability_monthly`, `product_margin_detail`, `inventory_health`, `marketing_roas_trailing`.

## File Organization

```
tibetan-spirit-ops/
├── CLAUDE.md                          ← You are here
├── **ORG.md**                         ← Role-based org chart
├── DEV-PLAN.md                        ← Implementation roadmap
├── SYSTEM-STATUS.md                   ← Live technical reference
├── pyproject.toml
│
├── agents/                            ← AI team (Paperclip-inspired structure)
│   ├── shared/                        ← Cross-agent skills (6 skills)
│   │   ├── brand-guidelines/SKILL.md  ← Constitutional values — loaded first always
│   │   ├── product-knowledge/SKILL.md
│   │   ├── escalation-matrix/SKILL.md
│   │   ├── channel-config/SKILL.md
│   │   ├── supabase-ops-db/SKILL.md
│   │   └── tibetan-calendar/SKILL.md
│   ├── customer-service/              ← **soul.md** + config.yaml + 6 skills
│   ├── operations/                    ← **soul.md** + config.yaml + 8 skills
│   ├── finance/                       ← **soul.md** + config.yaml + 7 skills
│   ├── marketing/                     ← **soul.md** + config.yaml + 15 skills
│   ├── ecommerce/                     ← **soul.md** + config.yaml + 8 skills
│   └── category-management/           ← **soul.md** + config.yaml + 8 skills
│
├── **lib/ts_shared/**                 ← Shared Python library
│   ├── supabase_client.py             ← Database connection (exists, needs path update)
│   ├── **claude_client.py**           ← Skill loading + API + caching
│   ├── **dashboard_ops.py**           ← Write to Supabase runtime tables
│   ├── notion_config.py               ← Database IDs (exists)
│   ├── **notion_ops.py**              ← Wiki/Academy writes only
│   ├── **org.py**                     ← ORG.md parser + role resolver
│   ├── **notifications.py**           ← Slack client
│   ├── **intercom_client.py**         ← Intercom Essentials REST client
│   ├── **cost_tracker.py**            ← Supabase + Notion dual-write
│   ├── logging_utils.py               ← Audit logging (exists)
│   └── **views.py**                   ← Materialized view refresh
│
├── **workflows/**                     ← Cron-triggered workflow scripts
│   ├── **daily_summary/**config.yaml + run.py
│   ├── **weekly_pnl/**
│   ├── **cs_email_drafts/**
│   ├── **inventory_alerts/**
│   ├── **campaign_brief/**
│   └── **product_descriptions/**
│
├── scripts/                           ← Utility scripts
│   ├── backfill_shopify.py            ← (exists, tested)
│   ├── import_orders_csv.py           ← (exists, tested)
│   ├── **seed_cogs_from_model.py**
│   ├── **build_customer_profiles.py**
│   ├── **sync_shopify_inventory.py**
│   ├── **run_all_workflows.py**
│   ├── **generate_academy_module.py**
│   ├── validate_skill.py              ← (exists, needs agents/ path update)
│   ├── validate_schema.py             ← (exists, tested)
│   └── validate_cross_refs.py         ← (exists, needs agents/ path update)
│
├── server/                            ← FastAPI (future webhook/chatbot)
│   └── server.py                      ← 326 lines, not deployed
│
├── tests/
│   ├── test_*.py                      ← Unit tests
│   └── evals/                         ← Workflow evaluation suites
│
├── workspace/plans/REQ-1/             ← Sprint execution prompts
├── data/                              ← Local data assets (gitignored)
└── temp/                              ← Planning docs + research (gitignored)

**ts-command-center/**                 ← Separate repo (Next.js dashboard on Vercel)
├── src/app/
│   ├── page.tsx                       ← **Dashboard home**
│   ├── **inbox/**                     ← Task Inbox (approve/reject)
│   ├── **health/**                    ← Workflow Health
│   ├── **costs/**                     ← Spend Tracker
│   ├── **workflows/**                 ← Workflow Registry + Eval
│   ├── **agents/**                    ← Agent Registry
│   └── **settings/**                  ← Company management
├── src/lib/                           ← Supabase client, utils
└── messages/                          ← i18n (en, zh, id)
```

Items marked with ** are not yet implemented.

## Override Rate: The Master Metric

```
override_rate = (rejected + modified) / total_reviewed × 100
```

**Starting threshold: 25% flat.** Future per-category thresholds (after 90+ days):
- Financial: 5-10% | Operational: 10-15% | Content: 20-30% | Cultural: always human review

**Graduation tiers:**
- Tier 3 (explicit approval): All new workflows start here
- Tier 2 (draft + 4hr auto-approve): Override rate < 25% for 30+ days
- Tier 1 (auto-execute, log only): Override rate near-zero, extended period

## Important Cultural Context

Tibetan Spirit sells sacred Buddhist items. Every customer interaction, product description, and marketing message must demonstrate respect for Buddhist traditions.

- **Never** use "exotic" or "mystical" — frame products through their practice context
- Buddhist terminology stays **untranslated**: mala, thangka, dharma, sangha, puja, mandala
- Products have spiritual significance — singing bowls are meditation instruments, not "home decor"
- The 5% Dharma Giving (profit to Forest Hermitage) is a genuine commitment, **not a marketing angle**
- When in doubt about cultural sensitivity, **escalate to `spiritual-director`**
- The audience includes serious practitioners who will notice inauthentic marketing
- Restraint is a competitive advantage — not sending an email is sometimes the right decision

## Paperclip Integration Status

**Concepts adopted:** Agent-centric file structure, soul files, org chart model, graduation checklist, values guardrail framework.

**Software deferred:** Paperclip Node.js server not installed. Dashboard, heartbeat scheduler, and ticketing system use our own implementations (ts-command-center + Railway cron + Supabase task_inbox). Revisit Paperclip software adoption Q3 2026 when agent count exceeds 6.

## Environment Variables

```bash
# Already configured
SUPABASE_URL, SUPABASE_SERVICE_KEY, ANTHROPIC_API_KEY
SHOPIFY_API_TOKEN, SHOPIFY_WEBHOOK_SECRET

# **Sprint S1 additions
NOTION_API_KEY, SLACK_BOT_TOKEN
SLACK_CHANNEL_OPS, SLACK_CHANNEL_CS, SLACK_CHANNEL_ALERTS

# **Sprint S2 additions
HELPDESK_PLATFORM=intercom
INTERCOM_ACCESS_TOKEN, INTERCOM_ADMIN_ID, INTERCOM_WEBHOOK_SECRET
NEXT_PUBLIC_SUPABASE_URL, NEXT_PUBLIC_SUPABASE_ANON_KEY

# Future (graceful degradation if missing)
KLAVIYO_API_KEY, META_ADS_ACCESS_TOKEN, GOOGLE_ADS_DEVELOPER_TOKEN
TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN
```
