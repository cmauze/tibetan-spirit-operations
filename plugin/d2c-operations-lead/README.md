# d2c-operations-lead

D2C operations plugin for Claude Code. Encodes operational workflows for Shopify-based direct-to-consumer brands: customer service triage and drafting, fulfillment exception handling, inventory restocking, margin reporting, marketing discipline, and catalog description optimization.

## Skills

| Skill | Domain | Description |
|-------|--------|-------------|
| cs-triage | Customer Service | Email classification → 7 categories with escalation routing |
| cs-pipeline | Customer Service | End-to-end: triage → enrichment → draft → approval queue |
| shopify-query | Data Access | Real-time Shopify GraphQL lookups (orders, products, inventory) |
| order-inquiry | Customer Service | Order status → customer-facing language with special case handling |
| fulfillment-flag | Operations | Exception flagging and routing for fulfillment anomalies |
| margin-reporting | Finance | Weekly P&L with SKU-level margins, channel comparison, below-floor alerts |
| campaign-brief | Marketing | Structured briefs with tier classification and frequency cap enforcement |
| restock-calc | Inventory | Reorder point, safety stock, and restock quantity recommendations |
| description-optimizer | Catalog | Evaluator-optimizer loop with 5-dimension quality rubric |

## Prerequisites

- Shopify store with GraphQL Admin API access
- Database (Supabase recommended) with order, product, inventory, and COGS tables
- Gmail integration (for CS pipeline)
- Team notification channel (Slack recommended)

## Installation

```
/plugins install d2c-operations-lead
```

## Configuration

Each skill references generic role IDs. Configure your team's role mapping:

| Role ID | Responsibility |
|---------|---------------|
| `general-manager` | Final approvals, strategy, pricing |
| `operations-manager` | Orders, inventory POs, supplier comms |
| `warehouse-manager` | Pick/pack/ship, inventory counts |
| `brand-specialist` | Brand-sensitive content review, cultural accuracy |
| `regional-fulfillment` | Regional/international fulfillment |

Configure in your project's CLAUDE.md or org-roles rule file.

## Regeneration

Plugin skills are auto-generated from project `skills/` by `scripts/publish-plugin.sh`.
The script applies sanitization rules from `sanitize.yaml` to remove
Tibetan Spirit-specific operational details (spiritual routing, cultural terms,
internal paths, team member names).

**Do not edit plugin skills/ directly.** Edit project skills/ and re-run the script:

```
bash scripts/publish-plugin.sh
```

Sanitization rules are defined in `plugin/d2c-operations-lead/sanitize.yaml`.
Add new rules there when project skills diverge in new ways.
