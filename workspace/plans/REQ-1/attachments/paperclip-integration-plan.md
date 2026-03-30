# Paperclip Integration Plan — Concepts Now, Software Later

**Date:** 2026-03-30
**Decision:** Adopt Paperclip's organizational concepts immediately. Defer running Paperclip's Node.js server to post-MVP (revisit Q3 2026).

---

## What We Adopt Now

### 1. Agent-Centric File Structure

Move from domain-organized `skills/` to agent-organized `agents/` at repo root:

```
agents/
├── shared/                          # Cross-agent resources (not an agent)
│   ├── brand-guidelines/SKILL.md    # Constitutional values — loaded by ALL agents
│   ├── product-knowledge/SKILL.md
│   ├── escalation-matrix/SKILL.md
│   ├── channel-config/SKILL.md
│   ├── supabase-ops-db/SKILL.md
│   └── tibetan-calendar/SKILL.md
│
├── customer-service/
│   ├── soul.md                      # Agent identity + judgment framework
│   ├── config.yaml                  # Model, budget, skills list, heartbeat
│   └── skills/
│       ├── ticket-triage/SKILL.md
│       ├── order-inquiry/SKILL.md
│       ├── product-guidance/SKILL.md
│       ├── return-request/SKILL.md
│       ├── practice-inquiry/SKILL.md
│       └── review-solicitation/SKILL.md
│
├── operations/
│   ├── soul.md
│   ├── config.yaml
│   └── skills/
│       ├── fulfillment-domestic/SKILL.md
│       ├── inventory-management/SKILL.md
│       ├── fulfillment-mexico/SKILL.md
│       ├── fulfillment-nepal/SKILL.md
│       ├── supplier-communication/SKILL.md
│       ├── amazon-fba-replenishment/SKILL.md
│       ├── travel-coordination/SKILL.md
│       ├── etsy-sync-monitoring/SKILL.md
│       └── warehouse-management/SKILL.md
│
├── finance/
│   ├── soul.md
│   ├── config.yaml
│   └── skills/
│       ├── cogs-tracking/SKILL.md
│       ├── margin-reporting/SKILL.md
│       ├── reconciliation/SKILL.md
│       ├── nepal-payments/SKILL.md
│       ├── debt-service/SKILL.md
│       ├── amazon-fee-analysis/SKILL.md
│       └── channel-profitability/SKILL.md
│
├── marketing/
│   ├── soul.md
│   ├── config.yaml
│   └── skills/
│       ├── campaign-architecture/SKILL.md
│       ├── meta-ads/SKILL.md
│       ├── google-ads/SKILL.md
│       ├── amazon-ppc/SKILL.md
│       ├── etsy-ads/SKILL.md
│       ├── pinterest-ads/SKILL.md
│       ├── ab-testing/SKILL.md
│       ├── email-sms/SKILL.md
│       ├── seo/SKILL.md
│       ├── social-content/SKILL.md
│       ├── performance-reporting/SKILL.md
│       ├── creative-library/SKILL.md
│       ├── drift-detection/SKILL.md
│       ├── inventory-aware-advertising/SKILL.md
│       └── funnel-decomposition/SKILL.md
│
├── ecommerce/
│   ├── soul.md
│   ├── config.yaml
│   └── skills/
│       ├── cross-channel-parity/SKILL.md
│       ├── etsy-content-optimization/SKILL.md
│       ├── amazon-listing-optimization/SKILL.md
│       ├── site-health/SKILL.md
│       ├── content-performance/SKILL.md
│       ├── agentic-discovery/SKILL.md
│       ├── collection-management/SKILL.md
│       └── product-photography-standards/SKILL.md
│
└── category-management/
    ├── soul.md
    ├── config.yaml
    └── skills/
        ├── competitive-research/SKILL.md
        ├── pricing-strategy/SKILL.md
        ├── category-portfolio/SKILL.md
        ├── assortment-planning/SKILL.md
        ├── promotion-strategy/SKILL.md
        ├── subscription-curation/SKILL.md
        ├── wholesale-strategy/SKILL.md
        └── marketplace-expansion/SKILL.md
```

### 2. Soul Files (New Artifact)

Each agent gets a soul.md defining character and judgment framework. Not technical procedures (that's SKILL.md) — this is WHO the agent IS.

### 3. Values Guardrail Framework

Constitutional values layer in `agents/shared/brand-guidelines/SKILL.md`:
- Non-negotiable constraints that override task instructions
- Frequency caps for marketing
- Content tier classification (auto-publish / CEO / spiritual-director / never)
- Product framing rules and terminology preservation
- Dharma Giving integrity rules

### 4. Structured CEO Decision Support

Every agent output must include:
- Status indicator (GREEN/YELLOW/RED)
- Decisions needed (with recommendation, alternative, risk of inaction)
- Values compliance check
- Cost transparency

### 5. Graduation Model

Paperclip's 7-day reliability check → our Phase 1 (30-day, 200-invocation, <2% error) → Phase 2 (autonomous).

---

## What We Defer

| Concept | Status | When |
|---------|--------|------|
| Paperclip Node.js server | DEFER | Post-MVP, when >6 agents |
| Paperclip dashboard | SKIP | Use ts-command-center instead |
| Heartbeat scheduler | DEFER | Railway cron stays for now |
| Paperclip's PostgreSQL | SKIP | Supabase is our database |
| TRANSLATION.md | Create for reference | Sprint S1 |
| company-config.json | DEFER | Not needed without Paperclip server |
| heartbeat.yaml / tools.yaml | DEFER | Use config.yaml (our format) instead |

---

## Skill Path Migration

All skill references change from `skills/{domain}/{skill}` to `agents/{agent}/skills/{skill}`.
Shared skills: `agents/shared/{skill}`.

The `claude_client.py` skill loader updates:
- `load_skill("customer-service/ticket-triage")` → looks in `agents/customer-service/skills/ticket-triage/SKILL.md`
- `load_skill("shared/brand-guidelines")` → looks in `agents/shared/brand-guidelines/SKILL.md`
- The `depends_on` paths in frontmatter use the same convention

---

## config.yaml Format (Per Agent)

```yaml
# agents/finance/config.yaml
name: finance-analyst
description: "Financial conscience of Tibetan Spirit"
model: claude-sonnet-4-6
max_turns: 20
budget_usd: 1.00
skills:
  - shared/brand-guidelines
  - shared/channel-config
  - shared/supabase-ops-db
  - finance/cogs-tracking
  - finance/margin-reporting
  - finance/reconciliation
workflows:
  - weekly_pnl
```
