---
name: shopify-query
description: Queries Tibetan Spirit's Shopify store for real-time data not yet synced to Supabase. Use when an agent needs a specific order lookup, live inventory check, product search by SKU, or customer info for CS enrichment.
allowed-tools: Read, Write, Bash
---

# Shopify Query

**Announce at start:** "I'm using the shopify-query skill to fetch live data from Shopify."

## Goal

Execute a targeted Shopify GraphQL query to retrieve real-time data for a specific lookup — order status, product inventory, or customer information for CS enrichment. Always uses read-only operations. All queries use the GraphQL Admin API 2026-01 via the Shopify MCP server.

## Prerequisites

- Supabase has been checked first for aggregate or historical queries. Use this skill only when Supabase data may be stale (CS enrichment, specific order lookup, real-time stock check).

## Process

1. **Determine query type** — Identify whether this is: order lookup (CS enrichment), product search by SKU/name, real-time inventory check, or customer info lookup. See routing table below.
2. **Run the query** — Apply the appropriate query pattern from `references/query-patterns.md`. Always include date range filters for order queries — never pull unbounded order history.
3. **Parse the response** — Handle `{"error": "..."}` if present before proceeding. Log the query purpose to the activity log.
4. **Return results** — Pass structured results to the calling skill or agent. Do not persist raw Shopify responses — extract only what's needed. Log observability entry to `data/agent-runs.json` per `_templates/observability.md`.

**Query routing:**

| Need | Use |
|------|-----|
| Aggregate reports, P&L, margins | Supabase — not this skill |
| Specific order lookup (CS enrichment) | This skill — freshest data |
| Product search by SKU/name | This skill — live catalog |
| Real-time low stock check | This skill |
| Customer info (CS enrichment) | This skill |
| Bulk data (full catalog export) | `scripts/backfill_shopify.py` → Supabase |

## Output

- **Primary:** Structured data returned to the calling skill (not written to a file by default)
- **Secondary:** `data/agent-runs.json` — one observability entry per `_templates/observability.md`
- **Terminal:** Query type, result summary, and any errors encountered

**Verification:** Credentials not logged or exposed. Date filter applied for all order queries. Error field handled before passing results to caller. No bulk operations run without explicit date bounds.

## Data Hygiene

- Never log or expose SHOPIFY_ACCESS_TOKEN in any output, terminal message, or data file.
- Never store customer PII (email, address, phone) outside the draft/log context that requested it — access is scoped to the current request.
- Log the purpose of every customer data access in `data/agent-runs.json` (e.g., `"inputs_summary": {"purpose": "cs-enrichment", "order_id": "12345"}`).
- Never write customer email addresses or shipping addresses to persistent data files.

## Common Rationalizations

| Thought | Reality |
|---|---|
| "Supabase has this data, I'll use that for CS" | Supabase may lag 24h. For CS enrichment, use this skill for fresh data. |
| "I'll query all orders to be thorough" | Always use date filters. Unbounded queries belong in the backfill script. |

## Edge Cases

- **Rate limit hit (HTTP 429):** Claude Code's built-in retry handles backoff — do not add custom retry logic. Log as `status: "partial"` if partial data was retrieved.
- **Query returns error field:** Handle the error before passing results. Log the error in `data/agent-runs.json` with `status: "error"`.
- **Customer not found:** Return empty result — do not synthesize or guess customer data.

## Rules

- NEVER expose SHOPIFY_ACCESS_TOKEN in any output.
- NEVER run bulk operations without date filters.
- NEVER use this skill for aggregate reporting — use Supabase.
- READ ONLY — no write operations via this skill.

## Environment

- **API:** Shopify GraphQL Admin API 2026-01 via `GeLi2001/shopify-mcp`
- **Data files:** `data/agent-runs.json`
- **Reference files:** `references/query-patterns.md`, `_templates/observability.md`
- **Rules:** `.claude/rules/shopify-api.md`

## Works Well With

- **Invoked by:** `cs-drafter` (CS enrichment), `fulfillment-manager` (order status), `inventory-analyst` (real-time stock)
- **Preceded by:** Supabase query for anything where Supabase data is sufficient
