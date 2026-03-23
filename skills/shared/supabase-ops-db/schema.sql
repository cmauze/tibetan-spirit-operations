-- =============================================================================
-- Tibetan Spirit Operations Database Schema
-- =============================================================================
-- Extends Shopify's product data with COGS, competitive intel, cross-channel
-- inventory, supplier payments, marketing metrics, and AI skill audit logging.
--
-- Deploy order:
--   1. Extensions
--   2. Enum types
--   3. Tables (dependency order)
--   4. Indexes
--   5. Trigger function + triggers
--   6. Materialized views
--   7. pg_cron schedules
-- =============================================================================


-- ---------------------------------------------------------------------------
-- 1. Extensions
-- ---------------------------------------------------------------------------

CREATE EXTENSION IF NOT EXISTS "pgcrypto";   -- gen_random_uuid()
-- CREATE EXTENSION IF NOT EXISTS "pg_cron";  -- scheduled refresh (may not be available)


-- ---------------------------------------------------------------------------
-- 2. Enum types
-- ---------------------------------------------------------------------------

CREATE TYPE cogs_confidence_level AS ENUM ('confirmed', 'estimated', 'unknown');
CREATE TYPE sales_channel          AS ENUM ('shopify', 'etsy', 'amazon', 'wholesale');
CREATE TYPE fulfillment_route      AS ENUM ('domestic', 'mexico', 'nepal');
CREATE TYPE payment_status         AS ENUM ('pending', 'approved', 'paid', 'overdue', 'cancelled');
CREATE TYPE trigger_source         AS ENUM ('webhook', 'cron', 'manual');


-- ---------------------------------------------------------------------------
-- 3. Tables
-- ---------------------------------------------------------------------------

-- Products — master catalog (synced from Shopify + COGS extension fields)
CREATE TABLE products (
    id                     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    shopify_id             BIGINT UNIQUE NOT NULL,
    title                  TEXT NOT NULL,
    handle                 TEXT,
    sku                    TEXT,
    price                  NUMERIC(10,2),
    status                 TEXT DEFAULT 'active',

    -- COGS extension fields
    cogs_confirmed         NUMERIC(10,2),
    cogs_estimated         NUMERIC(10,2),
    freight_per_unit       NUMERIC(10,2),
    duty_rate              NUMERIC(5,4),         -- decimal, e.g. 0.0500 = 5%
    duty_hs_code           TEXT,
    margin_floor_by_channel JSONB,               -- {"shopify": 0.40, "etsy": 0.35, ...}
    cogs_confidence        cogs_confidence_level DEFAULT 'unknown',

    created_at             TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at             TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE products IS 'Master product catalog synced from Shopify with COGS extension fields.';
COMMENT ON COLUMN products.cogs_confirmed IS 'Validated COGS from actual supplier invoices (USD).';
COMMENT ON COLUMN products.cogs_estimated IS 'Estimated COGS from category averages (USD fallback).';
COMMENT ON COLUMN products.margin_floor_by_channel IS 'Minimum acceptable margin per channel as JSON: {"shopify": 0.40, ...}';


-- Inventory Extended — cross-channel stock levels
CREATE TABLE inventory_extended (
    id                     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id             UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    sku                    TEXT,
    total_on_hand          INT NOT NULL DEFAULT 0,
    shopify_available      INT NOT NULL DEFAULT 0,
    fba_allocated          INT NOT NULL DEFAULT 0,
    fba_in_transit         INT NOT NULL DEFAULT 0,
    nepal_pipeline         INT NOT NULL DEFAULT 0,
    nepal_eta              DATE,
    reorder_trigger_qty    INT NOT NULL DEFAULT 5,
    safety_stock           INT NOT NULL DEFAULT 2,

    created_at             TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at             TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE inventory_extended IS 'Cross-channel inventory view. Refreshed on Shopify webhook + daily sync.';
COMMENT ON COLUMN inventory_extended.fba_allocated IS 'Units reserved for next Amazon FBA shipment.';
COMMENT ON COLUMN inventory_extended.nepal_pipeline IS 'Units ordered from Nepal suppliers, not yet received.';


-- Orders — order history across all channels
CREATE TABLE orders (
    id                     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    shopify_id             BIGINT UNIQUE,
    order_number           TEXT,
    email                  TEXT,
    channel                sales_channel NOT NULL DEFAULT 'shopify',
    total_price            NUMERIC(10,2),
    currency               TEXT DEFAULT 'USD',
    fulfillment_status     TEXT,
    fulfillment_route      fulfillment_route,
    line_items             JSONB,
    shipping_address       JSONB,

    created_at             TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at             TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE orders IS 'Order history across all sales channels.';
COMMENT ON COLUMN orders.line_items IS 'Array of {sku, title, quantity, price} objects.';


-- Competitive Intel — competitor pricing data
CREATE TABLE competitive_intel (
    id                     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_category       TEXT NOT NULL,
    competitor_name        TEXT NOT NULL,
    competitor_url         TEXT,
    price                  NUMERIC(10,2),
    last_checked           TIMESTAMPTZ NOT NULL DEFAULT now(),
    source                 TEXT,

    created_at             TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at             TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE competitive_intel IS 'Competitor pricing populated by weekly competitive scan skill.';


-- Supplier Payments — Nepal supplier payment tracking
CREATE TABLE supplier_payments (
    id                     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    supplier_name          TEXT NOT NULL,
    invoice_number         TEXT,
    amount_npr             NUMERIC(12,2),
    amount_usd             NUMERIC(10,2),
    exchange_rate          NUMERIC(10,4),
    payment_status         payment_status NOT NULL DEFAULT 'pending',
    payment_method         TEXT,
    due_date               DATE,

    created_at             TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at             TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE supplier_payments IS 'Nepal supplier payment tracking in NPR and USD.';
COMMENT ON COLUMN supplier_payments.exchange_rate IS 'NPR/USD rate at time of payment.';


-- Marketing Performance — daily channel/campaign snapshots
CREATE TABLE marketing_performance (
    id                     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    date                   DATE NOT NULL,
    channel                TEXT NOT NULL,
    campaign_id            TEXT,
    ad_spend               NUMERIC(10,2) NOT NULL DEFAULT 0,
    revenue                NUMERIC(10,2) NOT NULL DEFAULT 0,
    roas                   NUMERIC(8,4),
    cpc                    NUMERIC(8,4),
    ctr                    NUMERIC(8,6),
    impressions            INT NOT NULL DEFAULT 0,
    clicks                 INT NOT NULL DEFAULT 0,

    created_at             TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at             TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE marketing_performance IS 'Daily marketing performance snapshots by channel and campaign.';


-- Skill Invocations — audit trail for every AI action
CREATE TABLE skill_invocations (
    id                     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp              TIMESTAMPTZ NOT NULL DEFAULT now(),
    agent_name             TEXT NOT NULL,
    skill_name             TEXT NOT NULL,
    skill_version          TEXT,
    trigger_source         trigger_source NOT NULL DEFAULT 'manual',
    raw_input              JSONB,
    raw_output             JSONB,
    structured_result      JSONB,
    model_used             TEXT,
    input_tokens           INT,
    output_tokens          INT,
    cached_tokens          INT,
    cost_usd               NUMERIC(10,6),
    latency_ms             INT,
    confidence_score       NUMERIC(3,2),
    phase                  SMALLINT CHECK (phase IN (1, 2)),
    human_approved         BOOLEAN,
    error                  TEXT,

    created_at             TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at             TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE skill_invocations IS 'Audit trail: every skill run logged with inputs, outputs, cost, confidence.';
COMMENT ON COLUMN skill_invocations.phase IS '1 = human approval required, 2 = autonomous.';


-- ---------------------------------------------------------------------------
-- 4. Indexes
-- ---------------------------------------------------------------------------

-- Products
CREATE INDEX idx_products_shopify_id  ON products (shopify_id);
CREATE INDEX idx_products_sku         ON products (sku);
CREATE INDEX idx_products_status      ON products (status);

-- Inventory Extended
CREATE INDEX idx_inventory_product_id ON inventory_extended (product_id);
CREATE INDEX idx_inventory_sku        ON inventory_extended (sku);

-- Orders
CREATE INDEX idx_orders_shopify_id        ON orders (shopify_id);
CREATE INDEX idx_orders_channel           ON orders (channel);
CREATE INDEX idx_orders_created_at        ON orders (created_at);
CREATE INDEX idx_orders_channel_created   ON orders (channel, created_at);
CREATE INDEX idx_orders_fulfillment       ON orders (fulfillment_status, fulfillment_route);

-- Competitive Intel
CREATE INDEX idx_competitive_category     ON competitive_intel (product_category);
CREATE INDEX idx_competitive_last_checked ON competitive_intel (last_checked);
CREATE INDEX idx_competitive_cat_comp     ON competitive_intel (product_category, competitor_name);

-- Supplier Payments
CREATE INDEX idx_supplier_status          ON supplier_payments (payment_status);
CREATE INDEX idx_supplier_due_date        ON supplier_payments (due_date);
CREATE INDEX idx_supplier_name_status     ON supplier_payments (supplier_name, payment_status);

-- Marketing Performance
CREATE INDEX idx_marketing_date           ON marketing_performance (date);
CREATE INDEX idx_marketing_channel_date   ON marketing_performance (channel, date);
CREATE INDEX idx_marketing_campaign       ON marketing_performance (campaign_id, date);

-- Skill Invocations
CREATE INDEX idx_skill_inv_timestamp      ON skill_invocations (timestamp);
CREATE INDEX idx_skill_inv_agent          ON skill_invocations (agent_name, skill_name);
CREATE INDEX idx_skill_inv_skill_ts       ON skill_invocations (skill_name, timestamp);
CREATE INDEX idx_skill_inv_trigger        ON skill_invocations (trigger_source);


-- ---------------------------------------------------------------------------
-- 5. Auto-update trigger for updated_at
-- ---------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_products_updated_at
    BEFORE UPDATE ON products
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_inventory_updated_at
    BEFORE UPDATE ON inventory_extended
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_orders_updated_at
    BEFORE UPDATE ON orders
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_competitive_intel_updated_at
    BEFORE UPDATE ON competitive_intel
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_supplier_payments_updated_at
    BEFORE UPDATE ON supplier_payments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_marketing_performance_updated_at
    BEFORE UPDATE ON marketing_performance
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_skill_invocations_updated_at
    BEFORE UPDATE ON skill_invocations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();


-- ---------------------------------------------------------------------------
-- 6. Materialized Views
-- ---------------------------------------------------------------------------

-- Channel Profitability (Monthly)
-- Calculates P&L by channel: revenue, estimated COGS, channel fees, gross profit.
-- Fee rates: Shopify 2.5%+$0.30, Etsy ~10%, Amazon ~30%, Wholesale 0%.
CREATE MATERIALIZED VIEW channel_profitability_monthly AS
SELECT
    date_trunc('month', o.created_at)::DATE                     AS month,
    o.channel,
    COUNT(*)                                                     AS order_count,
    SUM(o.total_price)                                           AS revenue,
    SUM(
        COALESCE(
            (SELECT SUM(
                (li->>'quantity')::INT *
                COALESCE(p.cogs_confirmed, p.cogs_estimated, 0)
            )
            FROM jsonb_array_elements(o.line_items) AS li
            LEFT JOIN products p ON p.sku = li->>'sku'),
            0
        )
    )                                                            AS total_cogs,
    SUM(
        CASE o.channel
            WHEN 'shopify'   THEN o.total_price * 0.025 + 0.30
            WHEN 'etsy'      THEN o.total_price * 0.10
            WHEN 'amazon'    THEN o.total_price * 0.30
            WHEN 'wholesale' THEN 0
        END
    )                                                            AS total_fees,
    SUM(o.total_price)
        - SUM(
            COALESCE(
                (SELECT SUM(
                    (li->>'quantity')::INT *
                    COALESCE(p.cogs_confirmed, p.cogs_estimated, 0)
                )
                FROM jsonb_array_elements(o.line_items) AS li
                LEFT JOIN products p ON p.sku = li->>'sku'),
                0
            )
        )
        - SUM(
            CASE o.channel
                WHEN 'shopify'   THEN o.total_price * 0.025 + 0.30
                WHEN 'etsy'      THEN o.total_price * 0.10
                WHEN 'amazon'    THEN o.total_price * 0.30
                WHEN 'wholesale' THEN 0
            END
        )                                                        AS gross_profit,
    CASE WHEN SUM(o.total_price) > 0
        THEN (
            SUM(o.total_price)
            - SUM(
                COALESCE(
                    (SELECT SUM(
                        (li->>'quantity')::INT *
                        COALESCE(p.cogs_confirmed, p.cogs_estimated, 0)
                    )
                    FROM jsonb_array_elements(o.line_items) AS li
                    LEFT JOIN products p ON p.sku = li->>'sku'),
                    0
                )
            )
            - SUM(
                CASE o.channel
                    WHEN 'shopify'   THEN o.total_price * 0.025 + 0.30
                    WHEN 'etsy'      THEN o.total_price * 0.10
                    WHEN 'amazon'    THEN o.total_price * 0.30
                    WHEN 'wholesale' THEN 0
                END
            )
        ) / SUM(o.total_price)
        ELSE 0
    END                                                          AS margin_pct
FROM orders o
GROUP BY date_trunc('month', o.created_at)::DATE, o.channel
WITH NO DATA;

CREATE UNIQUE INDEX idx_channel_prof_month_channel
    ON channel_profitability_monthly (month, channel);


-- Product Margin Detail
-- Per-SKU margin with landed cost breakdown.
-- landed_cost = cogs + freight + (cogs * duty_rate)
CREATE MATERIALIZED VIEW product_margin_detail AS
SELECT
    p.id                                                         AS product_id,
    p.sku,
    p.title,
    p.price                                                      AS retail_price,
    p.cogs_confidence,
    COALESCE(p.cogs_confirmed, p.cogs_estimated)                 AS cogs,
    p.freight_per_unit,
    p.duty_rate,
    COALESCE(p.cogs_confirmed, p.cogs_estimated, 0)
        + COALESCE(p.freight_per_unit, 0)
        + (COALESCE(p.cogs_confirmed, p.cogs_estimated, 0) * COALESCE(p.duty_rate, 0))
                                                                 AS landed_cost,
    p.price
        - (COALESCE(p.cogs_confirmed, p.cogs_estimated, 0)
           + COALESCE(p.freight_per_unit, 0)
           + (COALESCE(p.cogs_confirmed, p.cogs_estimated, 0) * COALESCE(p.duty_rate, 0)))
                                                                 AS gross_margin,
    CASE WHEN p.price > 0
        THEN (
            p.price
            - (COALESCE(p.cogs_confirmed, p.cogs_estimated, 0)
               + COALESCE(p.freight_per_unit, 0)
               + (COALESCE(p.cogs_confirmed, p.cogs_estimated, 0) * COALESCE(p.duty_rate, 0)))
        ) / p.price
        ELSE 0
    END                                                          AS margin_pct,
    p.margin_floor_by_channel
FROM products p
WHERE p.status = 'active'
WITH NO DATA;

CREATE UNIQUE INDEX idx_product_margin_product_id
    ON product_margin_detail (product_id);


-- Inventory Health
-- Days of supply and stockout risk by SKU.
CREATE MATERIALIZED VIEW inventory_health AS
SELECT
    ie.product_id,
    ie.sku,
    p.title,
    ie.total_on_hand,
    ie.shopify_available,
    ie.fba_allocated,
    ie.fba_in_transit,
    ie.nepal_pipeline,
    ie.nepal_eta,
    ie.reorder_trigger_qty,
    ie.safety_stock,
    ie.total_on_hand - ie.fba_allocated - ie.safety_stock        AS available_to_sell,
    COALESCE(daily_sales.avg_daily, 0)                           AS avg_daily_sales,
    CASE WHEN COALESCE(daily_sales.avg_daily, 0) > 0
        THEN ROUND(ie.total_on_hand / daily_sales.avg_daily)
        ELSE 9999
    END                                                          AS days_of_supply,
    CASE
        WHEN ie.total_on_hand <= 0                               THEN 'stockout'
        WHEN ie.total_on_hand <= ie.safety_stock                 THEN 'critical'
        WHEN ie.total_on_hand <= ie.reorder_trigger_qty          THEN 'reorder'
        ELSE 'healthy'
    END                                                          AS stock_status
FROM inventory_extended ie
JOIN products p ON p.id = ie.product_id
LEFT JOIN LATERAL (
    SELECT
        COALESCE(
            SUM((li->>'quantity')::INT)::NUMERIC / GREATEST(
                EXTRACT(DAY FROM now() - MIN(o.created_at)),
                1
            ),
            0
        ) AS avg_daily
    FROM orders o,
         jsonb_array_elements(o.line_items) AS li
    WHERE li->>'sku' = ie.sku
      AND o.created_at >= now() - INTERVAL '30 days'
) daily_sales ON TRUE
WITH NO DATA;

CREATE UNIQUE INDEX idx_inventory_health_product_id
    ON inventory_health (product_id);


-- Marketing ROAS (Trailing 7 and 30 days)
CREATE MATERIALIZED VIEW marketing_roas_trailing AS
SELECT
    mp.channel,
    mp.campaign_id,
    SUM(CASE WHEN mp.date >= CURRENT_DATE - 7  THEN mp.ad_spend   ELSE 0 END) AS spend_7d,
    SUM(CASE WHEN mp.date >= CURRENT_DATE - 7  THEN mp.revenue    ELSE 0 END) AS revenue_7d,
    CASE WHEN SUM(CASE WHEN mp.date >= CURRENT_DATE - 7 THEN mp.ad_spend ELSE 0 END) > 0
        THEN SUM(CASE WHEN mp.date >= CURRENT_DATE - 7 THEN mp.revenue   ELSE 0 END)
           / SUM(CASE WHEN mp.date >= CURRENT_DATE - 7 THEN mp.ad_spend  ELSE 0 END)
        ELSE 0
    END                                                                         AS roas_7d,
    SUM(CASE WHEN mp.date >= CURRENT_DATE - 30 THEN mp.ad_spend   ELSE 0 END) AS spend_30d,
    SUM(CASE WHEN mp.date >= CURRENT_DATE - 30 THEN mp.revenue    ELSE 0 END) AS revenue_30d,
    CASE WHEN SUM(CASE WHEN mp.date >= CURRENT_DATE - 30 THEN mp.ad_spend ELSE 0 END) > 0
        THEN SUM(CASE WHEN mp.date >= CURRENT_DATE - 30 THEN mp.revenue   ELSE 0 END)
           / SUM(CASE WHEN mp.date >= CURRENT_DATE - 30 THEN mp.ad_spend  ELSE 0 END)
        ELSE 0
    END                                                                         AS roas_30d,
    SUM(CASE WHEN mp.date >= CURRENT_DATE - 30 THEN mp.impressions ELSE 0 END) AS impressions_30d,
    SUM(CASE WHEN mp.date >= CURRENT_DATE - 30 THEN mp.clicks      ELSE 0 END) AS clicks_30d
FROM marketing_performance mp
WHERE mp.date >= CURRENT_DATE - 30
GROUP BY mp.channel, mp.campaign_id
WITH NO DATA;

CREATE UNIQUE INDEX idx_mkt_roas_channel_campaign
    ON marketing_roas_trailing (channel, campaign_id);


-- ---------------------------------------------------------------------------
-- 7. pg_cron Schedules (run manually if pg_cron unavailable)
-- ---------------------------------------------------------------------------
-- Uncomment these if pg_cron is available on your Supabase instance:
--
-- SELECT cron.schedule('refresh-channel-profitability', '0 * * * *',
--     $$REFRESH MATERIALIZED VIEW CONCURRENTLY channel_profitability_monthly$$);
--
-- SELECT cron.schedule('refresh-product-margin', '0 * * * *',
--     $$REFRESH MATERIALIZED VIEW CONCURRENTLY product_margin_detail$$);
--
-- SELECT cron.schedule('refresh-inventory-health', '*/15 * * * *',
--     $$REFRESH MATERIALIZED VIEW CONCURRENTLY inventory_health$$);
--
-- SELECT cron.schedule('refresh-marketing-roas', '0 * * * *',
--     $$REFRESH MATERIALIZED VIEW CONCURRENTLY marketing_roas_trailing$$);
