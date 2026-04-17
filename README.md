# Tibetan Spirit Operations

Operational automation for [tibetanspirit.com](https://tibetanspirit.com) — a Shopify D2C store selling Himalayan artisan goods (incense, singing bowls, malas, prayer flags, thangkas, statues, ritual supplies). Six specialized AI agents handle fulfillment, inventory, customer service, marketing, catalog, and finance. All customer-facing outputs require human approval before execution. Built on Claude Code + Supabase + Slack.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│  SHOPIFY  (GraphQL Admin API 2026-01)                               │
│  Source of truth: orders, products, inventory, customers            │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────┐
│  SUPABASE / POSTGRESQL                                              │
│  ts_products (559) · ts_orders (19.4K+) · ts_customers             │
│  ts_inventory · ts_cogs · task_inbox · workflow_runs               │
│  Views: channel_profitability · product_margin · inventory_health  │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────┐
│  AGENT LAYER  (Claude Code · Fork Execution Model)                  │
│                                                                     │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐               │
│  │ CS Drafter   │ │ Fulfillment  │ │ Inventory    │               │
│  │ (draft only) │ │ Manager      │ │ Analyst      │               │
│  └──────────────┘ └──────────────┘ └──────────────┘               │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐               │
│  │ Marketing    │ │ Catalog      │ │ Finance      │               │
│  │ Strategist   │ │ Curator      │ │ Analyst      │               │
│  └──────────────┘ └──────────────┘ └──────────────┘               │
│                                                                     │
│  Skills: cs-triage · cs-workflow (W) · shopify-query               │
│  order-inquiry · fulfillment-flag · margin-reporting               │
│  campaign-brief · restock-calc · description-optimizer             │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────┐
│  HUMAN-IN-THE-LOOP                                                  │
│  draft → Supabase task_inbox → Slack #ts-operations → human review │
│  NEVER auto-send customer emails · NEVER modify Shopify directly   │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
           ┌───────────────────┼───────────────────┐
           ▼                   ▼                   ▼
     Slack alerts        Shortwave/Gmail       Langfuse
     (#ts-operations)    (CS email mgmt)       (observability)
```

**MCP servers:** Shopify, Supabase, Slack, Gmail
**Scheduling:** PM2 (current) → Railway cron (planned)

---

## Agent Roster

| Agent | Model | Budget | Role | Key Constraint |
|-------|-------|--------|------|----------------|
| CS Drafter | Opus | $2.00 | Email drafts via triage → enrichment → draft | NEVER auto-sends — draft only, human sends |
| Fulfillment Manager | Opus | $2.00 | Order tracking, shipping, supplier coordination | Coordinates with Jothi (Bahasa Indonesia) |
| Inventory Analyst | Opus | $2.00 | Stock monitoring, restock alerts, demand forecasting | Purchase decisions require Ops Manager review |
| Marketing Strategist | Opus | $2.00 | Campaign briefs, content calendar, targeting | 2 promo emails/month max, no scarcity tactics |
| Catalog Curator | Opus | $5.00 | Product descriptions via evaluator-optimizer loop | Practice-first framing, cultural review gate |
| Finance Analyst | Opus | $0.50 | Weekly P&L, COGS tracking, margin analysis | 5% Dharma Giving is accounting, never marketing |

Agent definitions: `agents/*.md` (symlinked to `.claude/agents/`)

---

## Skill Inventory

| Skill | Job | Used By |
|-------|-----|---------|
| `cs-triage` | Classify inbound CS email (category, urgency, suggested action) | CS Drafter |
| `cs-workflow` **(W)** | Workflow orchestrator: triage → enrichment → draft → approval | CS Drafter |
| `shopify-query` | Real-time Shopify GraphQL queries (orders, products, inventory) | All agents |
| `order-inquiry` | Order status lookup and customer-ready summary | CS Drafter, Fulfillment Manager |
| `fulfillment-flag` | Flag orders for exceptions, routing anomalies, manual review | Fulfillment Manager |
| `margin-reporting` | Weekly P&L generation, COGS tracking, margin analysis | Finance Analyst |
| `campaign-brief` | Structured marketing campaign brief with targeting and budget | Marketing Strategist |
| `restock-calc` | Inventory threshold analysis and restock recommendations | Inventory Analyst |
| `description-optimizer` | Score and rewrite product descriptions (evaluator-optimizer loop) | Catalog Curator |

**(W)** = Workflow orchestrator

All skills live flat in `skills/` (each a directory with SKILL.md + metadata.json). Symlinked to `.claude/skills/` for runtime discovery.

---

## Rules (10)

| Rule | Scope |
|------|-------|
| `brand-voice` | Warm, knowledgeable tone. No corporate speak, no spiritual bypassing. |
| `cultural-sensitivity` | Sacred terms stay untranslated. Never guess on dharma content. |
| `org-roles` | Team directory with language, channel, and escalation protocols |
| `shopify-api` | GraphQL API conventions, rate limits, read-only enforcement |
| `cs-judgment` | Warmth over speed. Escalate sacred matters to Spiritual Director. |
| `finance-judgment` | Accuracy over speed. Surface anomalies immediately. |
| `marketing-discipline` | 2 emails/month cap. No scarcity, FOMO, or healing claims. |
| `operations-protocols` | Proactive over reactive. Respect supplier relationships. |
| `ecommerce-judgment` | Practice context first. SEO serves authenticity, not the reverse. |
| `category-judgment` | Never commoditize sacred categories. Protect artisan margins. |

Rules live in `rules/` (symlinked to `.claude/rules/`).

---

## Hooks (4)

| Hook | Purpose |
|------|---------|
| `ccpa-gate.sh` | CCPA ADMT compliance — blocks unapproved customer-facing actions |
| `log-activity.sh` | Audit trail for all agent activity |
| `session-context.sh` | Loads session context (team, brand rules) at start |
| `slack-notify.sh` | Routes alerts to Slack #ts-operations |

Hooks live in `.claude/hooks/`.

---

## Team

| Role | Person | Language | Channel |
|------|--------|----------|---------|
| CEO | Chris Mauze | English | Slack, Dashboard, Email |
| Operations Manager | Jothi | Bahasa Indonesia (formal) | Slack, Dashboard |
| Spiritual Director | Dr. Hun Lye | English | Email only (48-72hr response) |
| Warehouse Manager | Fiona | Chinese (Mandarin) | Dashboard only |

---

## Workflow Schedule

```
Every 30 min   cs_email_drafts ──→ CS Lead approval
Daily 9am      inventory_alerts ──→ Ops Manager review
Daily 6pm      daily_summary ────→ Auto-logged
Weekly Mon 6am weekly_pnl ───────→ CEO review
Weekly         campaign_brief ───→ CEO review
Manual         product_descriptions → CEO + Ops review
```

All workflows follow: **agent drafts → Supabase task_inbox → Slack alert → human reviews → human executes**.

---

## Directory Map

```
tibetan-spirit-ops/
├── CLAUDE.md                     # Project instructions (slim index)
├── README.md                     # This file (human-readable overview)
├── pyproject.toml                # Python project config
├── .env / .env.example           # Secrets (gitignored) / template
├── agents/                       # 6 agent soul files (.md)
│   ├── cs-drafter.md
│   ├── fulfillment-manager.md
│   ├── inventory-analyst.md
│   ├── marketing-strategist.md
│   ├── catalog-curator.md
│   └── finance-analyst.md
├── skills/                       # 9 skills (flat, each a directory)
│   ├── cs-triage/
│   ├── cs-workflow/              # Workflow orchestrator (W)
│   ├── shopify-query/
│   ├── order-inquiry/
│   ├── fulfillment-flag/
│   ├── margin-reporting/
│   ├── campaign-brief/
│   ├── restock-calc/
│   └── description-optimizer/
├── rules/                        # 10 operational rule files (.md)
├── scripts/                      # Python operational scripts
│   ├── daily_summary.py
│   ├── weekly_pnl.py
│   ├── backfill_shopify.py
│   ├── shopify_query.py
│   ├── import_orders_csv.py
│   ├── seed_cogs_from_model.py
│   └── ...                       # utilities, validators
├── lib/ts_shared/                # Shared Python library
│   ├── supabase_client.py        # Singleton Supabase connection
│   ├── claude_client.py          # Anthropic API wrapper
│   ├── cost_tracker.py           # Per-agent spend tracking
│   ├── notifications.py          # Slack notification helpers
│   └── ...                       # logging, org, views
├── server/                       # Deployment artifacts
│   ├── Dockerfile
│   ├── requirements.txt
│   └── server.py
├── docs/
│   ├── ARCHITECTURE.md           # Structural overview
│   ├── OPERATIONS-REFERENCE.md   # Full operational detail
│   ├── CHANGELOG.md              # Change history
│   └── AGENT-BACKLOG.md          # Planned agent work
├── deliverables/                 # Agent outputs
│   ├── charts/
│   ├── decks/
│   └── docs/
├── workspace/                    # Session artifacts
│   ├── plans/
│   ├── handoffs/
│   ├── results/
│   ├── research/
│   └── scratch/                  # Temporary (gitignored)
├── data/                         # Runtime data (gitignored)
└── .claude/
    ├── settings.json             # Tool permissions + hook config
    ├── agents/                   # Symlinks → agents/*.md
    ├── skills/                   # Symlinks → skills/*/
    ├── rules/                    # Symlinks → rules/*.md
    └── hooks/                    # Project-level enforcement
        ├── ccpa-gate.sh
        ├── log-activity.sh
        ├── session-context.sh
        └── slack-notify.sh
```

**Convention:** Edit canonical files at root (`agents/`, `skills/`, `rules/`). Never edit through `.claude/` symlinks. When adding a new component, create the canonical file and add a symlink in `.claude/`.

---

## Key Constraints

1. **NEVER auto-send customer emails** — All CS output is draft-only. Human reviews and sends via Shortwave/Gmail. This is both a quality standard and a CCPA ADMT compliance requirement.
2. **NEVER modify Shopify directly** — No order changes, pricing updates, inventory adjustments, or product status changes. Read-only via GraphQL.
3. **Practice-first framing** — Products are described through their spiritual practice context, not as home decor or wellness accessories.
4. **Cultural escalation path** — When uncertain about dharma content, product authenticity, or lineage claims, escalate to Spiritual Director (Dr. Hun Lye). Do not generate plausible-sounding explanations.
5. **Multilingual operations** — Jothi communicates in Bahasa Indonesia (formal register). Fiona communicates in Mandarin. Using the wrong language is not a minor error.
6. **5% Dharma Giving** — The commitment to Forest Hermitage is tracked as an accounting line item. It is never used in marketing or customer communications as a reason to purchase.

---

## Resuming Interrupted Work

If picking up this project mid-sprint:

1. Check `workspace/handoffs/` for the latest handoff file
2. Check `workspace/results/` for the most recent session results
3. Read `CLAUDE.md` for current architecture constraints and component inventory
4. Read `docs/ARCHITECTURE.md` for structural overview
5. Run `git log --oneline -10` to see what has been committed recently
6. Check `docs/AGENT-BACKLOG.md` for planned work

Current task tracking is in the Braingrid task system (accessible via Claude Code with Braingrid MCP).
