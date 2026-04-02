---
paths:
  - "skills/**"
  - "scripts/**"
  - "lib/**"
---

# Shopify API Interaction Rules

Tibetan Spirit's Shopify store is the production revenue source. All Shopify API interactions must be read-only in automated workflows. Write operations (order modifications, inventory updates, product changes) require human approval and are executed through scripts that Chris runs manually.

## API Version

Use GraphQL Admin API version 2026-01 exclusively. Do not use the REST API or older GraphQL versions. The MCP server (GeLi2001/shopify-mcp) handles authentication and version pinning.

## Rate Limits

Shopify's GraphQL API uses a cost-based rate limiting system with a 1,000-point bucket that refills at 50 points per second. Complex queries (nested connections, large page sizes) cost more points. Keep individual queries under 100 points by limiting page sizes to 50 items and avoiding deeply nested connections (max 2 levels). If you need to process the full product catalog (559 products), use cursor-based pagination with `after` parameter rather than offset pagination.

When the MCP server returns a rate limit error (HTTP 429 or cost exceeded), Claude Code's built-in retry mechanism handles backoff automatically. Do not add custom retry logic on top of this.

## Read Operations (Automated)

Permitted in automated workflows: querying orders (with date range filters), reading product details and inventory levels, fetching customer information for CS enrichment, and reading collection and metafield data.

Always include date range filters when querying orders to avoid pulling the entire order history. Default to the last 7 days unless the workflow specifies otherwise.

## Write Operations (Manual Only)

These operations are NEVER performed by automated agents: updating product descriptions or metadata (staged in Supabase first), modifying inventory quantities, changing prices or discounts, creating or cancelling orders, modifying fulfillment status, and updating customer records. All of these are prepared as drafts in Supabase's `task_inbox` and executed by Chris after review.
