---
name: shopify-query
description: Use when an agent needs real-time Shopify data not yet synced to Supabase, or a specific lookup by order number, SKU, or customer email.
---

# Shopify Query

## Overview

Queries Tibetan Spirit's Shopify store for real-time data when agents need fresh data not yet synced to Supabase.

## When to Use

- Specific order lookup for CS enrichment (freshest data)
- Product search by SKU/name against live catalog
- Real-time low stock check
- Customer info for CS enrichment
- **Do NOT use for:** aggregate reports (use Supabase), bulk data sync (use `scripts/backfill_shopify.py`), write operations (not supported)

## Workflow

1. Determine query type (order, product, inventory, recent-orders, customer)
2. Run the appropriate command from `references/query-patterns.md`
3. Parse JSON response; handle `{"error": "..."}` if present
4. Log any customer data access with purpose (CCPA compliance)

| Need | Use |
|------|-----|
| Aggregate reports, P&L, margins | Supabase (`ts_orders`, `ts_products`) |
| Specific order lookup (CS) | This skill -- freshest data |
| Product search by SKU/name | This skill for live catalog |
| Real-time low stock | This skill |
| Customer info (CS enrichment) | This skill |
| Bulk data (full catalog) | `scripts/backfill_shopify.py` -> Supabase |

## Common Rationalizations

| Rationalization | Reality |
|----------------|---------|
| "Supabase has this data, I'll use that for CS" | Supabase may lag 24h. For CS enrichment, use this skill. |
| "I'll query all orders to be thorough" | Always use date filters. Bulk queries belong in backfill script. |

## Red Flags

- Exposing SHOPIFY_ACCESS_TOKEN in any output
- Bulk operations without date filters
- Using this for aggregate reporting (use Supabase)
- Storing customer PII outside draft/log context

## Verification

- [ ] Credentials not logged or exposed
- [ ] Date filter applied for order queries
- [ ] Customer data access logged with purpose (CCPA)
- [ ] Output is JSON; error field handled before proceeding
