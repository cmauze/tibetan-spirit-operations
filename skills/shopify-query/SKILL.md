---
name: shopify-query
description: >
  On-demand Shopify store queries for agent workflows. Order lookup, product search,
  inventory levels, recent orders, customer info. Trigger: "look up order", "check inventory",
  "shopify query", "find product", "customer lookup".
model: inherit
---

# Shopify Query Skill

Query Tibetan Spirit's Shopify store for real-time data. Use when agents need fresh data not yet synced to Supabase, or for specific lookups (order by number, customer by email).

## When to Use This vs Supabase

| Need | Use |
|------|-----|
| Aggregate reports, P&L, margin analysis | Supabase (`ts_orders`, `ts_products`) |
| Specific order lookup (CS response) | This skill — freshest data |
| Product search by name/SKU | This skill for live catalog, Supabase for enriched data |
| Low stock alerts | This skill for real-time, Supabase for historical trends |
| Customer info for CS enrichment | This skill |
| Bulk data (all orders, full catalog) | `scripts/backfill_shopify.py` → Supabase |

## Commands

Run from the project root (`~/code/active/tibetan-spirit-ops/`):

### Order Lookup
```bash
python3 scripts/shopify_query.py order <order_number>
```
Returns: order details, line items, shipping address, fulfillment + tracking info, customer email.

### Product Search
```bash
python3 scripts/shopify_query.py product "<sku_or_title>"
```
Searches active products by SKU (exact) or title (substring). Returns matches with price, stock, type.

### Inventory Check
```bash
python3 scripts/shopify_query.py inventory --low 5
```
Without `--low`: returns first 50 products sorted by stock level.
With `--low N`: returns only products below N units.

### Recent Orders
```bash
python3 scripts/shopify_query.py recent-orders --days 7
```
Returns orders from the last N days with revenue total and per-order summary.

### Customer Lookup
```bash
python3 scripts/shopify_query.py customer "email@example.com"
```
Returns: name, order count, total spent, tags, address. For CS enrichment only — never export PII.

## Output Format

All commands return JSON to stdout. Errors return `{"error": "..."}`.

## Constraints

- **Read-only.** This skill NEVER modifies Shopify data.
- **CCPA compliance.** Log every customer data access with purpose. Never store PII outside the draft/log context.
- **Rate limits.** Shopify REST API: 40 requests/minute for private apps. The script does not add retry logic — if rate-limited, wait and retry manually.
- **No bulk operations.** For full catalog sync, use `scripts/backfill_shopify.py` instead.
- **Credentials.** Reads SHOPIFY_STORE_URL and SHOPIFY_ACCESS_TOKEN from .env. Never expose these values.
