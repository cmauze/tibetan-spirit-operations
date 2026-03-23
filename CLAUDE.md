# Tibetan Spirit AI Operations System

## What This Project Is

An autonomous operations platform for Tibetan Spirit, a $400K/year Tibetan Buddhist goods e-commerce business scaling to $2M. The system uses Claude-powered skills to handle order processing, inventory management, customer service, marketing, category management, and financial reconciliation across Shopify (primary), Etsy, and Amazon FBA channels.

## Architecture Overview

**Runtime**: Claude Agent SDK (Python) on Railway — not Claude Code CLI.
**Database**: Supabase PostgreSQL — the coordination layer between all skills. Skills query the database directly rather than communicating with each other.
**Observability**: Supabase `skill_invocations` table (Phase 1) → Langfuse OTEL integration (Phase 2).
**Durability**: Simple retry with exponential backoff + idempotency checks. No LangGraph/Temporal.

### The Six Agents

"Agent" = a trigger mechanism that invokes Claude with the right skills. All six use the same Claude models.

| Agent | Trigger | Primary Skills |
|-------|---------|----------------|
| **Customer Service** | Re:amaze webhook (new ticket) | ticket-triage, order-inquiry, product-guidance, return-request |
| **Operations** | Shopify webhook (new order, inventory change) + daily cron | fulfillment-domestic, inventory-management, supplier-communication |
| **Ecommerce Manager** | Daily cron + Shopify product update webhook | cross-channel-parity, etsy-content-optimization, site-health |
| **Category Manager** | Weekly cron + manual invocation | competitive-research, pricing-strategy, assortment-planning |
| **Marketing Manager** | Daily cron + ad platform alerts | meta-ads, google-ads, performance-reporting, drift-detection |
| **Finance** | Daily cron (reconciliation) + monthly cron (P&L) | cogs-tracking, reconciliation, margin-reporting |

### Model Routing Strategy

- **Haiku 4.5** ($1/$5 per MTok): Classification, simple lookups, email categorization
- **Sonnet 4.6** ($3/$15 per MTok): Most business tasks — drafting, analysis, recommendations
- **Opus 4.6** ($5/$25 per MTok): Complex financial analysis, strategic recommendations only

Default to Haiku for triage, Sonnet for execution. Use prompt caching aggressively (90% savings on cached tokens within 5-minute TTL).

## Key People

- **Chris Mauzé** — CEO/founder. Approves pricing changes, budget increases, strategic decisions. Interacts via Claude Code CLI and React dashboard.
- **Jhoti** — Operations Manager in Indonesia. Approves orders, reviews inventory alerts, manages Nepal supplier relationships. Interacts via mobile dashboard (Bahasa Indonesia) and WhatsApp. All communications with Jhoti MUST be in formal Bahasa Indonesia (use "Anda" not "kamu", frame instructions as suggestions with "Mungkin bisa...").
- **Fiona** — Warehouse manager in Asheville, NC. Handles pick/pack/ship for domestic orders. Interacts via dashboard (English) for daily pick lists.
- **Dr. Hun Lye** — Spiritual director. Answers Buddhist practice questions escalated from customer service. Interacts via email only.
- **Omar** — Mexico fulfillment partner (Espíritu Tibetano). Handles Latin American orders. Interacts via email only.

## Skill Authoring Guidelines

Every skill is a folder containing at minimum a `SKILL.md` file. Follow these patterns:

### SKILL.md Structure
```yaml
---
name: skill-name
description: When to trigger and what it does. Be specific about trigger conditions.
---
```

Then markdown instructions that Claude follows. Explain the *why* before the *how*. Use imperative form.

### Progressive Disclosure
- Keep SKILL.md under 500 lines
- Put detailed reference material in separate `.md` files within the skill folder
- Put deterministic logic (calculations, API calls, data transforms) in `.py` scripts
- Claude reads reference files only when needed, runs scripts without loading them into context

### Shared Knowledge
Skills in `skills/shared/` contain cross-cutting knowledge loaded by multiple agents:
- `brand-guidelines/` — Voice, tone, cultural sensitivity
- `product-knowledge/` — Product taxonomy, authenticity markers (from Dr. Hun Lye)
- `channel-config/` — Store URLs, fee structures, API scopes per channel
- `escalation-matrix/` — Who handles what, contact methods, response SLAs
- `supabase-ops-db/` — Schema reference, pre-built queries, connection patterns

Reference shared skills from domain skills like: "Read `skills/shared/product-knowledge/SKILL.md` for product details."

### Phase 1 → Phase 2 Graduation
Every skill starts in Phase 1 (human approval required). After demonstrating reliable performance (typically 30-90 days, 200+ invocations, <2% error rate), it graduates to Phase 2 (autonomous with reporting). Skills auto-demote to Phase 1 if drift detection flags anomalies.

## Database Conventions

All skills that need data query Supabase directly. Key tables:
- `products` — Shopify product data + COGS fields (cogs_confirmed, duty_rate, margin_floor_by_channel)
- `inventory_extended` — Cross-channel stock (fba_allocated, in_transit, nepal_pipeline, reorder_trigger_qty)
- `competitive_intel` — Competitor prices, last_checked timestamps, source URLs
- `supplier_payments` — Nepal supplier payment tracking (NPR amounts, USD equivalents, status)
- `marketing_performance` — Ad spend, revenue, ROAS, CPC by channel and campaign
- `skill_invocations` — Audit trail: every skill run logged with inputs, outputs, cost, confidence

Connection pattern: Use the shared Supabase client in `lib/shared/src/ts_shared/supabase_client.py`.

## Development Workflow

1. **Write skills locally** using Claude Code CLI: `claude -p "use the ticket-triage skill on this test email"`
2. **Test with the skill-creator** eval framework for quality validation
3. **Deploy to Railway** — skills are loaded by `server.py` at startup, invoked via webhook/cron triggers
4. **Monitor** via Supabase `skill_invocations` table, graduating skills as they prove reliable

## File Organization

```
tibetan-spirit-ops/
├── CLAUDE.md                    ← You are here
├── skills/                      ← All skill definitions
│   ├── shared/                  ← Cross-agent knowledge
│   ├── customer-service/        ← CS Agent skills
│   ├── operations/              ← Ops Agent skills
│   ├── ecommerce/               ← Ecommerce Manager skills
│   ├── category-management/     ← Category Manager skills
│   ├── marketing/               ← Marketing Manager skills
│   └── finance/                 ← Finance Agent skills
├── lib/shared/                  ← Shared Python libraries
├── server/                      ← FastAPI server + webhook handlers
├── dashboard/                   ← React PWA (future)
└── tests/                       ← Skill tests and evals
```

## Important Cultural Context

Tibetan Spirit sells sacred Buddhist items. Every customer interaction, product description, and marketing message must demonstrate respect for Buddhist traditions. Key rules:
- Never use "exotic" or "mystical" — frame products through their practice context
- Buddhist terminology stays untranslated: mala, thangka, dharma, sangha
- Products have spiritual significance — singing bowls are meditation instruments, not "home decor"
- The 5% Dharma Giving (profit to Forest Hermitage) is a genuine commitment, not a marketing angle
- When in doubt about cultural sensitivity, escalate to Dr. Hun Lye
