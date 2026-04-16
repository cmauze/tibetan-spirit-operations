# Shopify Query -- Command Reference

All queries use the Shopify GraphQL Admin API. Configure your store URL and access token in environment variables.
All return JSON to stdout. Errors return `{"error": "..."}`.

## Order Lookup
```bash
python3 scripts/shopify_query.py order <order_number>
```
Returns: order details, line items, shipping address, fulfillment + tracking info, customer email.

## Product Search
```bash
python3 scripts/shopify_query.py product "<sku_or_title>"
```
Searches active products by SKU (exact) or title (substring). Returns matches with price, stock, type.

## Inventory Check
```bash
python3 scripts/shopify_query.py inventory --low 5
```
Without `--low`: first 50 products sorted by stock level.
With `--low N`: only products below N units.

## Recent Orders
```bash
python3 scripts/shopify_query.py recent-orders --days 7
```
Returns orders from last N days with revenue total and per-order summary.

## Customer Lookup
```bash
python3 scripts/shopify_query.py customer "email@example.com"
```
Returns: name, order count, total spent, tags, address. For CS enrichment only -- never export PII.

## Constraints
- **Read-only.** NEVER modifies Shopify data.
- **Rate limits:** 40 requests/minute for private apps. No built-in retry. If rate-limited, wait and retry.
- **Credentials:** Reads SHOPIFY_STORE_URL and SHOPIFY_ACCESS_TOKEN from .env. Never expose.
