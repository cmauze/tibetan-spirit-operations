# Tibetan Spirit Operations Reference
# Relocated from CLAUDE.md v2 — detail preserved here, loaded on-demand via @include or skill

## Architecture Detail

### Execution Model
Standalone Python workflow scripts triggered by Railway cron jobs. Each workflow:
1. Loads agent soul file + relevant SKILL.md files into Claude's system prompt
2. Queries Supabase for business data
3. Calls Anthropic API with prompt caching
4. Writes results to Supabase `task_inbox` for human review via dashboard (Phase 1) or auto-executes (Phase 2)
5. Sends Slack alerts to the relevant team member
6. Logs cost and audit trail to Supabase `skill_invocations`

### Data Layer
Supabase PostgreSQL (Pro tier) — source of truth for all structured data.

### Human Layer
React PWA dashboard (ts-command-center/) — task inbox, health monitoring, cost tracking, workflow/agent registry, eval dashboard. Supabase `task_inbox` is the HITL state machine.

### Notifications
Slack for all internal comms. WhatsApp reserved for Nepal supplier communications only.

### Helpdesk
Intercom Essentials — CS email ingestion, help center/knowledge base, customer conversation management.

### Wiki
Notion for Academy modules (Jothi training) and internal playbooks only.

## The Six Workflows (Target State)

| Workflow | Schedule | Model | Approval | Description |
|----------|----------|-------|----------|-------------|
| `daily_summary` | 6pm daily | Haiku | Auto-logged | Order count, revenue, AOV, flags |
| `weekly_pnl` | Mon 6am | Sonnet | CEO | P&L with trends, margins, recommendations |
| `cs_email_drafts` | Every 30min | Haiku→Sonnet | CS Lead | Triage→enrich→draft via Intercom |
| `inventory_alerts` | 9am daily | Sonnet | Ops Manager | Stock levels, reorder suggestions, PO drafts |
| `campaign_brief` | Weekly | Sonnet | CEO | Campaign themes, targeting, copy outlines |
| `product_descriptions` | Manual | Sonnet | CEO + Ops | Evaluator-optimizer loop with rubric scoring |

## Model Routing

- **Haiku 4.5** (`claude-haiku-4-5-20251001`): Classification, triage, simple summaries. $1/$5 per MTok.
- **Sonnet 4.6** (`claude-sonnet-4-6`): Most business tasks. $3/$15 per MTok.
- **Opus 4.6** (`claude-opus-4-6`): Complex financial analysis only. $15/$75 per MTok.

## Team

| Role | Person | Language | Contact |
|------|--------|----------|---------|
| `ceo` | Chris Mauzé | English | Slack/Dashboard/Email |
| `operations-manager` | Jothi | Bahasa Indonesia (formal) | Slack/Dashboard |
| `customer-service-lead` | TBD | English | Dashboard/Email |
| `warehouse-manager` | Fiona | Chinese (Mandarin) | Dashboard |
| `spiritual-director` | Dr. Hun Lye | English | Email only |
| `mexico-fulfillment` | Omar | Spanish | Email only |

## Hook System

Hooks enforce policies with 100% determinism. Two layers fire in sequence:

### User-Level Hooks (inherited from `~/.claude/settings.json`)

Universal safety hooks that apply to every project. Centralized 2026-04-05.

| Event | Script | Matcher | Purpose |
|-------|--------|---------|---------|
| PreToolUse | `dangerous-actions-blocker.sh` | `Bash\|Edit\|Write` | Blocks destructive commands, force pushes, secret writes |
| PreToolUse | `unicode-injection-scanner.sh` | `Edit\|Write` | Detects Unicode injection vectors |
| PostToolUse | `output-secrets-scanner.sh` | all | Scans output for leaked secrets |

### Project-Level Hooks (`.claude/settings.json` → `.claude/hooks/`)

| Event | Script | Matcher | Async | Purpose |
|-------|--------|---------|-------|---------|
| PreToolUse | `budget-check.sh` | `mcp__shopify__.*\|Bash` | no | Per-agent budget enforcement |
| PostToolUse | `log-activity.sh` | `Bash\|Write\|Edit\|mcp__.*` | yes | Activity logging for audit trail |

Note: `.env` write blocking and secrets scanning are handled by user-level hooks (dangerous-actions-blocker.sh and stop-secrets-check.sh).

### Exit Codes

| Code | Meaning | Behavior |
|------|---------|----------|
| 0 | Allow | Tool call proceeds |
| 1 | Warn | Non-blocking warning. Tool still proceeds. |
| 2 | Block | Tool call prevented. **Always use exit 2 for security-critical enforcement.** |

## Legacy Agent Structure (Paperclip-inspired)

```
agents/{agent-name}/
├── soul.md              # WHO the agent is — character, judgment, values
├── config.yaml          # Model, budget, skills list, workflows
└── skills/              # Domain expertise loaded into system prompt
    └── {skill-name}/
        └── SKILL.md     # Decision trees, templates, escalation rules
```

### Shared Skills (loaded by ALL agents)
- `brand-guidelines/` — Constitutional values, voice, cultural sensitivity, frequency caps
- `product-knowledge/` — Product taxonomy, authenticity markers
- `escalation-matrix/` — Role-based routing with thresholds
- `channel-config/` — Shopify Growth plan, fee structures
- `supabase-ops-db/` — Schema reference, pre-built queries
- `tibetan-calendar/` — Liturgical dates, seasonal triggers

### Three-Tier Skill Loading
1. **Tier 1 (Startup):** Name + description only for all skills (~50 tokens/skill)
2. **Tier 2 (On-Trigger):** Full SKILL.md body when skill is relevant (~2K tokens)
3. **Tier 3 (At-Invocation):** Dependencies resolve + shared resources load

### SKILL.md Frontmatter Schema
```yaml
---
name: ticket-triage
description: |
  Classify incoming CS tickets.
version: "1.0.0"
category: customer-service
tags: [triage, email, haiku]
model: haiku
cacheable: true
estimated_tokens: 800
phase: 1
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

## Database Detail

### Three-Layer Schema (Sprint S1 Prompt 1D)
- **Registry:** companies, agents, skills, agent_skills, workflows, workflow_steps
- **Runtime:** task_inbox, workflow_runs, workflow_health, spend_records
- **Eval:** eval_suites, prompt_versions, eval_runs, eval_results

### Materialized Views
`channel_profitability_monthly`, `product_margin_detail`, `inventory_health`, `marketing_roas_trailing`

### Connection
`lib/ts_shared/supabase_client.py` (singleton, service key, bypasses RLS)

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

## File Organization (Full)

```
tibetan-spirit-ops/
├── CLAUDE.md                          ← Slim index (≤120 lines)
├── ORG.md                             ← Role-based org chart
├── DEV-PLAN.md                        ← Implementation roadmap
├── SYSTEM-STATUS.md                   ← Live technical reference
├── pyproject.toml
├── docs/
│   └── OPERATIONS-REFERENCE.md        ← You are here (full detail)
├── agents/                            ← AI team
│   ├── shared/                        ← Cross-agent skills (6 skills)
│   ├── customer-service/
│   ├── operations/
│   ├── finance/
│   ├── marketing/
│   ├── ecommerce/
│   └── category-management/
├── lib/ts_shared/                     ← Shared Python library
├── workflows/                         ← Claude workflow definitions (cs-workflow)
├── scripts/                           ← Utility scripts
├── server/                            ← FastAPI (future)
├── tests/
├── workspace/plans/REQ-1/
├── data/                              ← Local data assets (gitignored)
└── temp/                              ← Planning docs + research (gitignored)
```

## Environment Variables

```bash
# Already configured
SUPABASE_URL, SUPABASE_SERVICE_KEY, ANTHROPIC_API_KEY
SHOPIFY_API_TOKEN, SHOPIFY_WEBHOOK_SECRET

# Sprint S1 additions
NOTION_API_KEY, SLACK_BOT_TOKEN
SLACK_CHANNEL_OPS, SLACK_CHANNEL_CS, SLACK_CHANNEL_ALERTS

# Sprint S2 additions
HELPDESK_PLATFORM=intercom
INTERCOM_ACCESS_TOKEN, INTERCOM_ADMIN_ID, INTERCOM_WEBHOOK_SECRET
NEXT_PUBLIC_SUPABASE_URL, NEXT_PUBLIC_SUPABASE_ANON_KEY

# Future (graceful degradation if missing)
KLAVIYO_API_KEY, META_ADS_ACCESS_TOKEN, GOOGLE_ADS_DEVELOPER_TOKEN
TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN
```

## Paperclip Integration Status

**Concepts adopted:** Agent-centric file structure, soul files, org chart model, graduation checklist, values guardrail framework.

**Software deferred:** Paperclip Node.js server not installed. Dashboard, heartbeat scheduler, and ticketing system use our own implementations (ts-command-center + Railway cron + Supabase task_inbox). Revisit Paperclip software adoption Q3 2026 when agent count exceeds 6.
