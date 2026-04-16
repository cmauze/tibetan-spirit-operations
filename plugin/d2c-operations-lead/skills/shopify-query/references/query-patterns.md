# Shopify Query — Command Reference

All queries use the Shopify GraphQL Admin API. Configure your store URL and access token in environment variables.

## Query Types

### Order Lookup
Look up a specific order by order number. Returns: order details, line items, shipping address, fulfillment + tracking info, customer email.

### Product Search
Search active products by SKU (exact) or title (substring). Returns matches with price, stock, type.

### Inventory Check
List products sorted by stock level. Optionally filter to items below a threshold.

### Recent Orders
Returns orders from last N days with revenue total and per-order summary. Always use date filters.

### Customer Lookup
Look up customer by email. Returns: name, order count, total spent, tags, address. For CS enrichment only — never export PII.

## Constraints
- **Read-only.** NEVER modifies Shopify data.
- **Rate limits:** Respect Shopify's GraphQL cost-based rate limits (1,000-point bucket, 50 points/sec refill). Keep queries under 100 points — limit page sizes to 50 items, max 2 nesting levels.
- **Credentials:** Read from environment variables. Never expose in output.
