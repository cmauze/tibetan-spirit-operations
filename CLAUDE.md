# Tibetan Spirit Operations — Project Instructions
# File: ~/code/active/tibetan-spirit-ops/CLAUDE.md | Hierarchy: Project | Target: ≤120 lines
# Slim index. Full operational detail in docs/OPERATIONS-REFERENCE.md.

## Purpose
tibetan-spirit-ops automates Tibetan Spirit (tibetanspirit.com) — a Shopify D2C store selling Himalayan artisan goods (incense, singing bowls, malas, prayer flags, thangkas, statues, ritual supplies). Acquired from Dr. Hun Lye (Drikung Kagyu lineage). Both a business and a service to the dharma community.

## Architecture
Claude Code + PM2 + Supabase + Slack. Six specialized agents handle fulfillment, inventory, CS, marketing, catalog, and finance. All use the fork execution model. Cross-project coordination via chris-os Chief of Staff.

Tech stack: Shopify (GraphQL Admin API 2026-01), Supabase/PostgreSQL, Shortwave Pro (Gmail), Slack #ts-operations, Langfuse (self-hosted). MCP servers: Shopify, Supabase, Slack, Gmail.

Full architecture detail: `docs/OPERATIONS-REFERENCE.md`

## Agent Roster

| Agent | Model | Budget | Role |
|-------|-------|--------|------|
| Fulfillment Manager | Opus | $2.00 | Order tracking, shipping, supplier coordination with Jothi |
| Inventory Analyst | Opus | $2.00 | Stock monitoring, restock alerts, demand forecasting |
| CS Drafter | Opus | $2.00 | Email drafts via triage → enrichment → draft. NEVER auto-sends. |
| Marketing Strategist | Opus | $2.00 | Campaign briefs, content calendar, targeting |
| Catalog Curator | Opus | $5.00 | Product descriptions via evaluator-optimizer loop |
| Finance Analyst | Opus | $0.50 | Weekly P&L, COGS tracking, margin analysis |

Agent definitions in `.claude/agents/`. Full workflow specs in `docs/OPERATIONS-REFERENCE.md`.

## Data Layer
Supabase PostgreSQL. Key tables: `ts_products` (559 rows), `ts_orders` (19.4K+), `ts_customers`, `ts_inventory`, `ts_cogs`. Materialized views: `channel_profitability_monthly`, `product_margin_detail`. See `.claude/rules/supabase.md` for query rules.

## Team

| Role | Person | Language |
|------|--------|----------|
| CEO | Chris Mauzé | English |
| Operations Manager | Jothi | Bahasa Indonesia |
| Spiritual Director | Dr. Hun Lye | English |
| Warehouse Manager | Fiona | Chinese (Mandarin) |

## Brand Voice & Cultural Rules
See `.claude/rules/brand-voice.md` and `.claude/rules/cultural-sensitivity.md`. Core principles:

- Warm but not casual. Knowledgeable but not academic.
- Sacred terms stay untranslated: mala, thangka, dharma, sangha, puja, mandala
- Products framed through practice context, not home decor
- 5% Dharma Giving (Forest Hermitage) is accounting, NEVER marketing
- NEVER use: exotic, mystical, oriental, ancient secrets, zen vibes, namaste
- When uncertain about dharma content → escalate to Dr. Hun Lye

## Approval Requirements

| Workflow | Tier | Rationale |
|---|---|---|
| Daily order summary | Auto-logged | Informational |
| Weekly P&L | Auto-logged | Read-only |
| Inventory restock | Review Required | Purchase decisions |
| CS email draft | Decision Needed | Customer-facing |
| Campaign brief | Review Required | Brand + budget |
| Product description | Review Required | Cultural sensitivity |

## Prohibitions
- NEVER send customer emails — draft only, human sends
- NEVER modify Shopify orders, pricing, inventory, or product status
- NEVER process refunds or cancellations
- NEVER use AI-generated images for products
- NEVER trivialize or commercialize Buddhist concepts
- NEVER share customer PII outside Supabase
- NEVER communicate with Jothi on behalf of Chris without approval
- NEVER exceed per-invocation cost budget (enforced by PreToolUse hook)

## Key References
- Full operational detail: `docs/OPERATIONS-REFERENCE.md`
- Dev roadmap: `DEV-PLAN.md`
- System status: `SYSTEM-STATUS.md`
- Org chart: `ORG.md`
