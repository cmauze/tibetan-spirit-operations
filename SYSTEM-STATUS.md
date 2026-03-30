# Tibetan Spirit AI Ops — System Status & Technical Reference

> Current state of all working capabilities, live connections, and database schemas.
> Generated 2026-03-29 from live Supabase queries and codebase inspection.

---

## Live Connections

| Service | Status | Details |
|---------|--------|---------|
| **Supabase PostgreSQL** | Connected | Project `lxxqxwfzjnzxzxhsncmz` · MCP server configured · Service key auth (bypasses RLS) |
| **Shopify Admin API** | Connected | Store: `tibetanspirits.myshopify.com` · API version 2025-01 · OAuth token active · HMAC webhook secret configured |
| **Anthropic API** | Key configured | `ANTHROPIC_API_KEY` in `.env` · Not yet invoked in production (server not deployed) |
| **Re:amaze** | Not connected | Placeholder in `.env` |
| **Shippo** | Not connected | Placeholder in `.env` |
| **Klaviyo** | Not connected | Placeholder in `.env` |
| **Meta Ads** | Not connected | Placeholder in `.env` |
| **Google Ads** | Not connected | Placeholder in `.env` |
| **Amazon SP API** | Not connected | Placeholder in `.env` |
| **Langfuse** | Not connected | Phase 2 observability — commented out |

---

## What's Actually Working Today

### Data in Supabase (populated)

| Table | Rows | Source | Notes |
|-------|------|--------|-------|
| `orders` | **19,403** | Shopify CSV import + API backfill | Full history 2018-06-29 → 2026-03-24. All Shopify channel. |
| `products` | **559** | Shopify API backfill | All active. COGS/freight/duty fields exist but are **unpopulated** (all NULL). |

### Data in Supabase (schema deployed, empty)

| Table | Rows | Purpose |
|-------|------|---------|
| `inventory_extended` | 0 | Cross-channel stock levels — awaits Shopify inventory sync |
| `skill_invocations` | 0 | Audit trail — populates when server processes first skill |
| `competitive_intel` | 0 | Competitor pricing — populates when category-management skills run |
| `marketing_performance` | 0 | Ad spend/ROAS — populates when ad platform APIs connect |
| `supplier_payments` | 0 | Nepal supplier invoices — populates via manual entry or finance skills |

### Scripts (runnable now)

| Script | What it does | Verified? |
|--------|--------------|-----------|
| `scripts/backfill_shopify.py` | Paginates Shopify Admin API → upserts products & orders into Supabase | Yes — 559 products synced |
| `scripts/import_orders_csv.py` | Imports historical Shopify CSV exports → Supabase orders table | Yes — 19,403 orders imported |
| `scripts/test_shopify_connection.py` | Smoke test: auth, list products, list orders, simulate fulfillment routing | Yes |
| `scripts/shopify_token_capture.py` | One-time OAuth flow to capture Shopify access token | Yes — token captured |
| `scripts/validate_skill.py` | Validates SKILL.md frontmatter, required sections, cultural anti-patterns | Yes |
| `scripts/validate_schema.py` | Validates Supabase schema matches expected tables/views/enums | Yes |
| `scripts/validate_cross_refs.py` | Ensures skills reference valid table/column names | Yes |

### Tests (all passing)

| Test file | Tests | What it covers |
|-----------|-------|----------------|
| `tests/test_server.py` | ~10 | Health endpoint, HMAC verification, API key auth, skill execution (mocked) |
| `tests/test_supabase_client.py` | ~3 | Singleton caching, env var validation |
| `tests/test_logging_utils.py` | ~5 | Invocation logging format, Supabase insert (mocked) |
| `tests/evals/test_ticket_triage.py` | ~12 | Ticket classification against sample emails |

### Server (built, not deployed)

The FastAPI server (`server/server.py`, 326 lines) is complete with:
- 6 agent configurations with model routing and budget caps
- Shopify webhook receivers with HMAC verification
- Skill execution via Claude Agent SDK
- Audit logging to `skill_invocations`
- Dockerfile for Railway deployment
- **Status**: Railway connected to GitHub, deployment not yet verified live

### Local Data Assets

| File | Size | Contents |
|------|------|----------|
| `data/orders_export_1.csv` | 8.8 MB | Shopify historical order export (batch 1) |
| `data/orders_export_2.csv` | 7.2 MB | Shopify historical order export (batch 2) |
| `data/charges_export.numbers` | 6.2 MB | Shopify billing/charges for SaaS cost analysis |
| `ts-financial-model-v4d.xlsx` | — | Financial model (latest, data-validated from Supabase queries) |

---

## Orders Data — What's In There

**19,403 orders** · Shopify only · June 2018 through March 2026

| Year | Orders | Revenue | Avg Order Value |
|------|--------|---------|-----------------|
| 2018 | 872 | $81,075 | $92.98 |
| 2019 | 2,087 | $171,981 | $82.41 |
| 2020 | 3,698 | $207,953 | $56.23 |
| 2021 | 3,738 | $243,374 | $65.11 |
| 2022 | 2,660 | $180,606 | $67.90 |
| 2023 | 1,837 | $157,298 | $85.63 |
| 2024 | 2,233 | $106,338 | $47.62 |
| 2025 | 1,768 | $219,911 | $124.38 |
| 2026 (YTD) | 510 | $84,614 | $165.91 |
| **Total** | **19,403** | **$1,453,151** | **$74.89** |

---

## Database Schemas (from live Supabase)

### Enums

```sql
CREATE TYPE sales_channel    AS ENUM ('shopify', 'etsy', 'amazon', 'wholesale');
CREATE TYPE fulfillment_route AS ENUM ('domestic', 'mexico', 'nepal');
CREATE TYPE cogs_confidence_level AS ENUM ('confirmed', 'estimated', 'unknown');
CREATE TYPE payment_status   AS ENUM ('pending', 'approved', 'paid', 'overdue', 'cancelled');
CREATE TYPE trigger_source   AS ENUM ('webhook', 'cron', 'manual');
```

### Migrations Applied

| Version | Name |
|---------|------|
| 20260323064342 | `initial_schema` |
| 20260323064356 | `indexes_and_triggers` |
| 20260323064423 | `materialized_views` |

### Database Function

```sql
-- Auto-updates updated_at on every UPDATE
CREATE FUNCTION update_updated_at_column() RETURNS trigger;
-- Applied via trigger on all 7 tables
```

---

### Table: `products` — 559 rows

Shopify product catalog with COGS extension fields.

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | uuid | NO | `gen_random_uuid()` | PK |
| `shopify_id` | bigint | NO | — | Unique. Shopify's product ID. |
| `title` | text | NO | — | Product name |
| `handle` | text | YES | — | URL slug |
| `sku` | text | YES | — | Primary SKU |
| `price` | numeric | YES | — | Retail price (USD) |
| `status` | text | YES | `'active'` | Shopify product status |
| `cogs_confirmed` | numeric | YES | — | **Unpopulated.** Verified cost of goods. |
| `cogs_estimated` | numeric | YES | — | **Unpopulated.** Estimated COGS. |
| `freight_per_unit` | numeric | YES | — | **Unpopulated.** Shipping cost per unit. |
| `duty_rate` | numeric | YES | — | **Unpopulated.** Import duty rate (decimal). |
| `duty_hs_code` | text | YES | — | **Unpopulated.** Harmonized System code. |
| `margin_floor_by_channel` | jsonb | YES | — | **Unpopulated.** Min acceptable margin per channel. |
| `cogs_confidence` | cogs_confidence_level | YES | `'unknown'` | All rows currently `unknown`. |
| `created_at` | timestamptz | NO | `now()` | |
| `updated_at` | timestamptz | NO | `now()` | Auto-updated via trigger. |

**Indexes:** PK (`id`), unique (`shopify_id`), btree (`shopify_id`, `sku`, `status`)

**Sample row:**
```json
{
  "shopify_id": 1830555123757,
  "title": "\"A Stream of Blessings\": A Daily Recitation for the Fifteen Nairātmyā Goddesses",
  "handle": "a-stream-of-blessings-...",
  "sku": "E002",
  "price": "8.00",
  "status": "active",
  "cogs_confirmed": null,
  "cogs_confidence": "unknown"
}
```

---

### Table: `orders` — 19,403 rows

All Shopify orders from June 2018 to present with fulfillment routing.

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | uuid | NO | `gen_random_uuid()` | PK |
| `shopify_id` | bigint | YES | — | Unique. Shopify's order ID. |
| `order_number` | text | YES | — | Display order number (e.g. "20210") |
| `email` | text | YES | — | Customer email |
| `channel` | sales_channel | NO | `'shopify'` | All rows currently `shopify`. |
| `total_price` | numeric | YES | — | Order total (USD) |
| `currency` | text | YES | `'USD'` | |
| `fulfillment_status` | text | YES | — | Shopify fulfillment status (null = unfulfilled) |
| `fulfillment_route` | fulfillment_route | YES | — | `domestic`, `mexico`, or `nepal` (set by import script) |
| `line_items` | jsonb | YES | — | Array of `{sku, title, price, quantity}` objects |
| `shipping_address` | jsonb | YES | — | Full address with lat/lon, country_code, province_code |
| `created_at` | timestamptz | NO | `now()` | Order creation date |
| `updated_at` | timestamptz | NO | `now()` | Auto-updated via trigger. |

**Indexes:** PK (`id`), unique (`shopify_id`), btree (`channel`, `created_at`, `fulfillment_status + fulfillment_route`, `shopify_id`)

**Sample `line_items` element:**
```json
{"sku": "I82o", "price": "15.00", "title": "Kar Sur (Bhutan)", "quantity": 2}
```

**Sample `shipping_address`:**
```json
{
  "city": "Edmonds", "province": "Washington", "country": "United States",
  "country_code": "US", "province_code": "WA", "zip": "98026",
  "address1": "6114 137th Pl SW", "latitude": 47.8736, "longitude": -122.3164
}
```

---

### Table: `inventory_extended` — 0 rows

Cross-channel inventory view. FK to `products.id`.

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | uuid | NO | `gen_random_uuid()` | PK |
| `product_id` | uuid | NO | — | FK → `products.id` |
| `sku` | text | YES | — | |
| `total_on_hand` | int | NO | `0` | Total physical inventory |
| `shopify_available` | int | NO | `0` | Shopify available qty |
| `fba_allocated` | int | NO | `0` | Allocated to Amazon FBA |
| `fba_in_transit` | int | NO | `0` | In transit to FBA warehouse |
| `nepal_pipeline` | int | NO | `0` | Ordered from Nepal, not yet received |
| `nepal_eta` | date | YES | — | Expected arrival date |
| `reorder_trigger_qty` | int | NO | `5` | Reorder point |
| `safety_stock` | int | NO | `2` | Minimum buffer stock |
| `created_at` | timestamptz | NO | `now()` | |
| `updated_at` | timestamptz | NO | `now()` | Auto-updated via trigger. |

**Indexes:** PK (`id`), btree (`product_id`, `sku`)

---

### Table: `skill_invocations` — 0 rows

Audit trail for every AI skill execution.

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | uuid | NO | `gen_random_uuid()` | PK |
| `timestamp` | timestamptz | NO | `now()` | When the skill ran |
| `agent_name` | text | NO | — | e.g. `operations`, `customer-service` |
| `skill_name` | text | NO | — | e.g. `fulfillment-domestic` |
| `skill_version` | text | YES | — | |
| `trigger_source` | trigger_source | NO | `'manual'` | `webhook`, `cron`, or `manual` |
| `raw_input` | jsonb | YES | — | Full input payload |
| `raw_output` | jsonb | YES | — | Full output from Claude |
| `structured_result` | jsonb | YES | — | Parsed/structured output |
| `model_used` | text | YES | — | e.g. `claude-haiku-4-5-20251001` |
| `input_tokens` | int | YES | — | |
| `output_tokens` | int | YES | — | |
| `cached_tokens` | int | YES | — | Prompt-cached tokens |
| `cost_usd` | numeric | YES | — | Computed cost |
| `latency_ms` | int | YES | — | End-to-end execution time |
| `confidence_score` | numeric | YES | — | Skill's self-reported confidence (0-1) |
| `phase` | smallint | YES | — | CHECK: `1` or `2` |
| `human_approved` | boolean | YES | — | Did a human approve the output? |
| `error` | text | YES | — | Error message if failed |
| `created_at` | timestamptz | NO | `now()` | |
| `updated_at` | timestamptz | NO | `now()` | Auto-updated via trigger. |

**Indexes:** PK (`id`), btree (`timestamp`, `agent_name + skill_name`, `skill_name + timestamp`, `trigger_source`)

---

### Table: `competitive_intel` — 0 rows

Competitor pricing snapshots.

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | uuid | NO | `gen_random_uuid()` | PK |
| `product_category` | text | NO | — | e.g. "singing-bowls", "incense" |
| `competitor_name` | text | NO | — | |
| `competitor_url` | text | YES | — | |
| `price` | numeric | YES | — | Competitor's price (USD) |
| `last_checked` | timestamptz | NO | `now()` | |
| `source` | text | YES | — | Where the data came from |
| `created_at` | timestamptz | NO | `now()` | |
| `updated_at` | timestamptz | NO | `now()` | Auto-updated via trigger. |

**Indexes:** PK (`id`), btree (`product_category`, `product_category + competitor_name`, `last_checked`)

---

### Table: `marketing_performance` — 0 rows

Daily ad spend and performance metrics by channel/campaign.

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | uuid | NO | `gen_random_uuid()` | PK |
| `date` | date | NO | — | |
| `channel` | text | NO | — | Ad platform (meta, google, amazon, etsy, pinterest) |
| `campaign_id` | text | YES | — | Platform-specific campaign ID |
| `ad_spend` | numeric | NO | `0` | |
| `revenue` | numeric | NO | `0` | Attributed revenue |
| `roas` | numeric | YES | — | Return on ad spend |
| `cpc` | numeric | YES | — | Cost per click |
| `ctr` | numeric | YES | — | Click-through rate |
| `impressions` | int | NO | `0` | |
| `clicks` | int | NO | `0` | |
| `created_at` | timestamptz | NO | `now()` | |
| `updated_at` | timestamptz | NO | `now()` | Auto-updated via trigger. |

**Indexes:** PK (`id`), btree (`date`, `channel + date`, `campaign_id + date`)

---

### Table: `supplier_payments` — 0 rows

Nepal supplier invoice and payment tracking.

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | uuid | NO | `gen_random_uuid()` | PK |
| `supplier_name` | text | NO | — | |
| `invoice_number` | text | YES | — | |
| `amount_npr` | numeric | YES | — | Amount in Nepali Rupees |
| `amount_usd` | numeric | YES | — | USD equivalent |
| `exchange_rate` | numeric | YES | — | NPR/USD rate at time of payment |
| `payment_status` | payment_status | NO | `'pending'` | `pending → approved → paid` |
| `payment_method` | text | YES | — | Wire, PayPal, etc. |
| `due_date` | date | YES | — | |
| `created_at` | timestamptz | NO | `now()` | |
| `updated_at` | timestamptz | NO | `now()` | Auto-updated via trigger. |

**Indexes:** PK (`id`), btree (`payment_status`, `supplier_name + payment_status`, `due_date`)

---

## Materialized Views

All four views are deployed. They return data when their source tables are populated.

### `channel_profitability_monthly`

Monthly P&L by sales channel. Joins `orders` ↔ `products` on SKU for COGS lookup.

| Column | Type | Source |
|--------|------|--------|
| `month` | date | `date_trunc('month', orders.created_at)` |
| `channel` | sales_channel | `orders.channel` |
| `order_count` | bigint | `count(*)` |
| `revenue` | numeric | `sum(total_price)` |
| `total_cogs` | numeric | Line items × `products.cogs_confirmed` (falls back to `cogs_estimated`) |
| `total_fees` | numeric | Shopify 2.5%+$0.30 · Etsy 10% · Amazon 30% · Wholesale 0% |
| `gross_profit` | numeric | `revenue - cogs - fees` |
| `margin_pct` | numeric | `gross_profit / revenue` |

**Unique index:** `(month, channel)`

**Note:** Currently returns revenue and fees but COGS = 0 for all rows because `products.cogs_confirmed` and `cogs_estimated` are NULL.

---

### `product_margin_detail`

Per-SKU landed cost and margin calculation. Active products only.

| Column | Type | Source |
|--------|------|--------|
| `product_id` | uuid | `products.id` |
| `sku` | text | |
| `title` | text | |
| `retail_price` | numeric | `products.price` |
| `cogs_confidence` | enum | |
| `cogs` | numeric | `COALESCE(cogs_confirmed, cogs_estimated)` |
| `freight_per_unit` | numeric | |
| `duty_rate` | numeric | |
| `landed_cost` | numeric | `cogs + freight + (cogs × duty_rate)` |
| `gross_margin` | numeric | `price - landed_cost` |
| `margin_pct` | numeric | `gross_margin / price` |
| `margin_floor_by_channel` | jsonb | Min acceptable margin per channel |

**Unique index:** `(product_id)`

**Note:** Currently all margin fields = 0 or NULL because COGS data is unpopulated.

---

### `inventory_health`

Stock status with days-of-supply calculation. Joins `inventory_extended` ↔ `products` ↔ 30-day `orders` sales velocity.

| Column | Type | Source |
|--------|------|--------|
| `product_id` | uuid | |
| `sku` | text | |
| `title` | text | |
| `total_on_hand` | int | |
| `shopify_available` | int | |
| `fba_allocated` | int | |
| `fba_in_transit` | int | |
| `nepal_pipeline` | int | |
| `nepal_eta` | date | |
| `reorder_trigger_qty` | int | |
| `safety_stock` | int | |
| `available_to_sell` | int | `total_on_hand - fba_allocated - safety_stock` |
| `avg_daily_sales` | numeric | L30D sales velocity from orders line items |
| `days_of_supply` | numeric | `total_on_hand / avg_daily_sales` (9999 if no sales) |
| `stock_status` | text | `stockout`, `critical`, `reorder`, or `healthy` |

**Unique index:** `(product_id)`

**Note:** Empty — requires `inventory_extended` population.

---

### `marketing_roas_trailing`

Rolling 7-day and 30-day ROAS by channel and campaign.

| Column | Type | Source |
|--------|------|--------|
| `channel` | text | |
| `campaign_id` | text | |
| `spend_7d` | numeric | |
| `revenue_7d` | numeric | |
| `roas_7d` | numeric | `revenue_7d / spend_7d` |
| `spend_30d` | numeric | |
| `revenue_30d` | numeric | |
| `roas_30d` | numeric | `revenue_30d / spend_30d` |
| `impressions_30d` | int | |
| `clicks_30d` | int | |

**Unique index:** `(channel, campaign_id)`

**Note:** Empty — requires `marketing_performance` population.

---

## Skills — Current Readiness

### Production-Ready (21 skills) — detailed instructions, decision trees, output formats

| Domain | Skill | Model Target |
|--------|-------|-------------|
| **Shared** | brand-guidelines | — (loaded by all agents) |
| **Shared** | product-knowledge | — |
| **Shared** | escalation-matrix | — |
| **Shared** | channel-config | — |
| **Shared** | supabase-ops-db | — |
| **Shared** | tibetan-calendar | — |
| **Customer Service** | ticket-triage | Haiku |
| **Customer Service** | order-inquiry | Sonnet |
| **Customer Service** | product-guidance | Sonnet |
| **Customer Service** | return-request | Sonnet |
| **Operations** | fulfillment-domestic | Sonnet |
| **Operations** | inventory-management | Sonnet |
| **Operations** | fulfillment-mexico | Sonnet |
| **Operations** | fulfillment-nepal | Sonnet |
| **Operations** | supplier-communication | Sonnet |
| **Ecommerce** | cross-channel-parity | Sonnet |
| **Ecommerce** | etsy-content-optimization | Sonnet |
| **Finance** | cogs-tracking | Sonnet |
| **Finance** | reconciliation | Sonnet |
| **Finance** | margin-reporting | Sonnet |
| **Finance** | nepal-payments | Sonnet |

### Detailed Stubs (7 skills) — full structure and logic, recently fleshed out

| Domain | Skill | Lines |
|--------|-------|-------|
| **Finance** | debt-service | 237 |
| **Finance** | amazon-fee-analysis | 267 |
| **Finance** | channel-profitability | 330 |

### Outline Stubs (28 skills) — scope defined, awaiting implementation detail

| Domain | Count | Skills |
|--------|-------|--------|
| Customer Service | 2 | practice-inquiry, review-solicitation |
| Operations | 3 | amazon-fba-replenishment, travel-coordination, etsy-sync-monitoring |
| Ecommerce | 6 | site-health, content-performance, amazon-listing-optimization, agentic-discovery, collection-management, product-photography-standards |
| Category Mgmt | 8 | competitive-research, pricing-strategy, category-portfolio, assortment-planning, promotion-strategy, subscription-curation, wholesale-strategy, marketplace-expansion |
| Marketing | 14 | campaign-architecture, creative-library, meta-ads, google-ads, amazon-ppc, etsy-ads, pinterest-ads, ab-testing, email-sms, seo, social-content, performance-reporting, drift-detection, inventory-aware-advertising |

---

## Server Agent Configs (from `server.py`)

| Agent | Model | Max Turns | Budget | Skills Loaded |
|-------|-------|-----------|--------|---------------|
| customer-service | Haiku 4.5 | 10 | $0.25 | brand-guidelines, product-knowledge, escalation-matrix, ticket-triage |
| operations | Sonnet 4.6 | 15 | $0.50 | channel-config, escalation-matrix, fulfillment-domestic, inventory-management |
| ecommerce | Sonnet 4.6 | 15 | $0.50 | channel-config, cross-channel-parity, etsy-content-optimization |
| category-management | Sonnet 4.6 | 20 | $1.00 | channel-config, product-knowledge, supabase-ops-db |
| marketing | Sonnet 4.6 | 15 | $0.75 | channel-config, brand-guidelines |
| finance | Sonnet 4.6 | 20 | $1.00 | channel-config, supabase-ops-db, cogs-tracking, reconciliation |

---

## What's NOT Working Yet

| Item | Blocker |
|------|---------|
| **Railway deployment** | Build connected to GitHub, not yet verified live |
| **Shopify webhooks** | Need Railway URL to register endpoints |
| **Live skill execution** | Server not deployed → no webhook processing |
| **COGS data** | 559 products have no cost data — margin views return 0 |
| **Inventory sync** | `inventory_extended` empty — needs Shopify inventory locations API integration |
| **Ad platform APIs** | Meta, Google, Amazon, Etsy, Pinterest — all placeholder credentials |
| **Re:amaze integration** | Customer service webhook not connected |
| **Shippo integration** | Carrier rate/label API not connected |
| **Dashboard (React PWA)** | Not started |
| **Phase 2 observability** | Langfuse commented out |

---

## Review: Implementation Brief & Action Plan v2

Cross-referencing `ts-ops-implementation-brief.md` and `ts-ops-action-plan-v2.md` against the actual codebase and live Supabase state.

### Factual Corrections

**1. The brief underestimates what already exists.**

The brief's "Current Repo State" section describes the repo accurately at the file level, but the "Questions to Resolve" section treats key infrastructure as uncertain:

> "Supabase vs Notion for structured data? ... suggests a Supabase integration was planned or started."

**Reality:** Supabase is fully deployed and populated. 7 tables, 4 materialized views, 5 custom enums, 3 migrations, `updated_at` triggers on all tables, 19,403 orders and 559 products loaded. This is not "planned or started" — it's the most mature piece of the system.

> "What's in server/server.py? Is this a webhook endpoint?"

**Reality:** It's a 326-line FastAPI application with complete Shopify HMAC webhook verification, 6 agent configurations with model routing and budget caps, skill execution via Claude Agent SDK, and audit logging. It has a Dockerfile, passing tests, and was connected to Railway. Not a mystery — it's the execution engine.

> "dashboard/ — Existing dashboard (status TBD)"

**Reality:** `dashboard/` is an empty directory. Nothing to evaluate or remove.

**2. The brief's proposed architecture is a simplification, not an evolution.**

The brief proposes replacing the current system (Agent SDK + Supabase + FastAPI + Railway) with a simpler one (raw Anthropic API + Notion + standalone scripts + cron). This is a valid architectural choice for 5.5 orders/day, but the doc frames it as building forward when it's actually a reset that would discard:

- The working Agent SDK integration in `server.py`
- The Supabase schema, migrations, materialized views, and 19,403 rows of historical data
- The test suite (30 passing tests)
- The 21 production-ready skills designed around the current architecture

The brief should explicitly acknowledge this tradeoff: "We're choosing to simplify because the current system is over-engineered for our volume, and the cost is re-implementing skill execution as standalone scripts."

**3. Naming discrepancy: "Jothi" vs "Jhoti".**

The action plan uses "Jothi" throughout. The repo's CLAUDE.md, escalation-matrix skill, and all existing skills use "Jhoti." One of these needs to be standardized. The CLAUDE.md also specifies Jhoti is based in Indonesia (not "Jakarta / Kathmandu" as the action plan states). Clarify which is current.

**4. The action plan's "Week 1" tasks are already done.**

Action plan W1.1 says:
> "Generate Shopify Admin API credentials" / "Write a test script: pull last 30 days of orders"

These are complete. The Shopify OAuth token is captured (`shopify_token_capture.py`), the connection test script works (`test_shopify_connection.py`), and the full backfill scripts have already loaded all data into Supabase. The plan should start from the actual current state, not re-do completed work.

**5. Fiona speaks Chinese, not English.**

The action plan correctly notes this (M09: "Communication protocols: Fiona in Chinese"), but CLAUDE.md says Fiona "interacts via dashboard (English) for daily pick lists." The brief's CS workflow mentions "Chinese drafts for any queries Fiona needs to handle" which is correct. This should be reconciled in CLAUDE.md.

### Architecture Decision: What to Keep, What to Simplify

The core tension between the two documents:

| Aspect | Current Repo | Brief's Proposal |
|--------|-------------|-----------------|
| Execution | Agent SDK on Railway (always-on server) | Standalone Python scripts (cron-triggered) |
| Data layer | Supabase PostgreSQL | Notion databases (or Supabase for data + Notion for UI) |
| HITL | `skill_invocations` table + dashboard | Notion task inbox + WhatsApp |
| Observability | `skill_invocations` → Langfuse (Phase 2) | Notion cost log + git history |
| Skill loading | Server loads skills into Agent SDK context | Scripts load SKILL.md into raw API calls |
| Deployment | Railway (Docker) | Local cron (Mac Mini or laptop) |

**Recommendation:** Hybrid approach. Keep what works, simplify what doesn't.

| Keep (already working) | Simplify/Replace |
|------------------------|------------------|
| Supabase as data layer (19K orders, schema, views) | Drop the always-on Railway server for now (overkill for 5.5 orders/day) |
| Skills folder structure and all 56 SKILL.md files | Replace Agent SDK execution with standalone scripts calling Anthropic API directly |
| `skill_invocations` table for audit trail | Add Notion as the human-facing HITL layer on top of Supabase |
| Shopify API connection and backfill scripts | Replace webhook-triggered execution with cron-triggered scripts |
| Test suite | Extend with eval tests per the brief's pattern |

This avoids throwing away the Supabase data and schema (the most valuable built asset) while adopting the brief's simpler execution model. The `workflows/` directory pattern from the brief is good — each workflow is a standalone `run.py` that loads skills, calls Claude, writes results to Supabase AND Notion.

### Missing from Both Documents

**1. COGS data population strategy.** Both docs mention COGS but neither has a concrete plan for populating the 559 product rows. The `products` table has columns for `cogs_confirmed`, `cogs_estimated`, `freight_per_unit`, `duty_rate`, and `duty_hs_code` — all NULL. Without this data, the `channel_profitability_monthly` and `product_margin_detail` materialized views return zeros. The financial model session already validated blended COGS at ~24.6% — this data exists in Chris's head and the financial model, it just needs to be loaded into Supabase.

**2. Etsy and Amazon order ingestion.** The `orders` table has a `channel` enum (`shopify`, `etsy`, `amazon`, `wholesale`) but all 19,403 rows are Shopify. Neither doc addresses when/how to ingest Etsy or Amazon orders. The `channel_profitability_monthly` view is designed for cross-channel comparison but has only one channel.

**3. The financial model as a data source.** The `ts-financial-model-v4d.xlsx` (validated in the prior session) contains COGS estimates by category, SaaS costs, and revenue projections. Neither doc mentions using this as a data source to populate Supabase. A simple script could extract the category-level COGS percentages and apply them as `cogs_estimated` values.

**4. Materialized view refresh strategy.** The four materialized views exist but there's no cron or trigger to refresh them. They're stale snapshots until explicitly refreshed with `REFRESH MATERIALIZED VIEW`. The brief's `workflows/` approach would naturally trigger refreshes after data loads, but this should be explicit.

**5. The action plan has no technical architecture section.** It's an excellent operational and onboarding plan, but it doesn't specify: which database (Supabase or Notion), how workflows call Claude (Agent SDK or raw API), where scripts run (local, Railway, or cloud cron), or how the existing 56 skills map to the 6 proposed workflows. The implementation brief covers this; they should be read together.

### Suggestions

**1. Start with one working workflow, not a repo restructure.** Both docs front-load infrastructure work (restructure repo, set up Notion, build lib/ clients). The fastest path to value is: pick one workflow (weekly P&L is the best candidate), write a single `run.py` that loads skills, queries Supabase, calls the Anthropic API, and emails a result. Get that running on real data this week. Then extract shared code into `lib/` as patterns emerge.

**2. Use the financial model to seed COGS.** Write a script that reads category-level COGS percentages from the financial model and applies them as `cogs_estimated` across the 559 products. This immediately unlocks the `channel_profitability_monthly` and `product_margin_detail` views.

**3. The Notion operational layer and Supabase data layer are complementary, not competing.** Supabase holds structured data (orders, products, inventory, costs). Notion holds human workflow state (task inbox, approval queue, wiki). Don't migrate one into the other.

**4. Simplify the Academy.** 37 modules is ambitious for a part-time onboarding. The action plan already prioritizes correctly (foundation modules first), but consider: which modules can be replaced by supervised on-the-job learning? Jothi processing real orders with Chris reviewing is better training than a quiz about order lifecycle.

**5. The `server/` directory isn't dead weight.** Even if you adopt cron-triggered scripts, you'll eventually need webhook endpoints for Shopify order notifications and Re:amaze email intake. Consider keeping `server.py` as a thin webhook receiver that writes to Supabase, and let cron scripts process the queue. This separates event capture (always-on, lightweight) from skill execution (scheduled, heavyweight).
