---
name: supabase-ops-db
description: Supabase PostgreSQL schema reference, connection patterns, and pre-built query templates for the Tibetan Spirit operations database. Load this skill whenever you need to query the database, write data, or understand the data model. Every skill that touches business data should reference this skill.
---

# Supabase Operations Database

## Connection

- **URL**: Set via `SUPABASE_URL` environment variable
- **Key**: Use `SUPABASE_SERVICE_KEY` (bypasses RLS) for agent system operations
- **Client**: Use shared client from `lib/shared/src/ts_shared/supabase_client.py`

## Schema Overview

The database extends Shopify's data model with fields Shopify can't store natively (COGS, competitive intel, cross-channel inventory, supplier payments). A lightweight sync process keeps Supabase in sync with Shopify's canonical data.

### Core Tables

Read `skills/shared/supabase-ops-db/schema.sql` for the full DDL. Key tables:

**`products`** — Master product catalog
- Synced from Shopify: `shopify_id`, `title`, `handle`, `sku`, `price`, `status`
- Extended fields: `cogs_confirmed`, `cogs_estimated`, `freight_per_unit`, `duty_rate`, `duty_hs_code`, `margin_floor_by_channel` (JSONB), `cogs_confidence` (enum: confirmed/estimated/unknown)

**`inventory_extended`** — Cross-channel inventory view
- `product_id`, `sku`, `total_on_hand`, `shopify_available`, `fba_allocated`, `fba_in_transit`, `nepal_pipeline`, `nepal_eta`, `reorder_trigger_qty`, `safety_stock`
- Refreshed on Shopify inventory webhook + daily sync

**`orders`** — Order history across all channels
- Synced from Shopify (primary) with Etsy/Amazon orders added
- `channel` enum: shopify, etsy, amazon, wholesale
- `fulfillment_status`, `fulfillment_route` (domestic/mexico/nepal)

**`competitive_intel`** — Competitor pricing data
- `product_category`, `competitor_name`, `competitor_url`, `price`, `last_checked`, `source`
- Populated by weekly competitive scan skill

**`supplier_payments`** — Nepal supplier payment tracking
- `supplier_name`, `invoice_number`, `amount_npr`, `amount_usd`, `exchange_rate`, `payment_status`, `payment_method`, `due_date`

**`marketing_performance`** — Daily marketing snapshots
- `date`, `channel`, `campaign_id`, `ad_spend`, `revenue`, `roas`, `cpc`, `ctr`, `impressions`, `clicks`

**`skill_invocations`** — Audit trail for every AI action
- `id`, `timestamp`, `agent_name`, `skill_name`, `skill_version`, `trigger_source` (webhook/cron/manual)
- `raw_input` (JSONB), `raw_output` (JSONB), `structured_result` (JSONB)
- `model_used`, `input_tokens`, `output_tokens`, `cached_tokens`, `cost_usd`, `latency_ms`
- `confidence_score`, `phase` (1 or 2), `human_approved` (boolean), `error` (text)

### Materialized Views

Refreshed via `pg_cron` on Supabase:

- **`channel_profitability_monthly`** — P&L by channel: revenue, COGS, fees, shipping, gross profit, margin %
  - Refresh: hourly
- **`product_margin_detail`** — Per-SKU margin including COGS, channel fees, shipping estimate
  - Refresh: hourly
- **`inventory_health`** — Days of supply, reorder urgency, stockout risk by SKU
  - Refresh: every 15 minutes
- **`marketing_roas_trailing`** — 7-day and 30-day trailing ROAS by channel and campaign
  - Refresh: hourly

## Pre-Built Queries

See `skills/shared/supabase-ops-db/queries/` for ready-to-use SQL:

- `product-margin.sql` — Get margin by SKU with COGS confidence
- `inventory-availability.sql` — Cross-channel availability including FBA and in-transit
- `competitive-position.sql` — Price position vs. competitors by category
- `channel-profitability.sql` — True P&L by channel after all fees

## Query Patterns

When writing queries against this database:
1. Always filter by `status = 'active'` on the products table unless explicitly analyzing archived items
2. Use the materialized views for read-heavy analytics — they're pre-computed and fast
3. For write operations, always include idempotency checks (e.g., `ON CONFLICT DO NOTHING` or check for existing records)
4. Log every write operation to `skill_invocations` with the full context
5. Use parameterized queries — never interpolate user input directly into SQL
