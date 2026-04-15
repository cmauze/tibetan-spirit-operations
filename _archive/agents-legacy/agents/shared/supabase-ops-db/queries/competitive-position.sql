-- =============================================================================
-- Competitive Price Position by Category
-- =============================================================================
-- Compares Tibetan Spirit's pricing against competitors by product category.
-- Shows our price range, competitor price range, and price position.
--
-- Parameters:
--   :category_filter — optional product_category filter (NULL for all)
--   :stale_days      — max days since last competitor check (default 14)
-- =============================================================================

WITH our_prices AS (
    -- Average retail price per product category
    -- Categories are derived from SKU convention: TS-{CATEGORY}-...
    SELECT
        SPLIT_PART(p.sku, '-', 2)                               AS category_code,
        COUNT(*)                                                  AS our_product_count,
        ROUND(MIN(p.price), 2)                                   AS our_min_price,
        ROUND(AVG(p.price), 2)                                   AS our_avg_price,
        ROUND(MAX(p.price), 2)                                   AS our_max_price
    FROM products p
    WHERE p.status = 'active'
      AND p.sku IS NOT NULL
    GROUP BY SPLIT_PART(p.sku, '-', 2)
),
competitor_prices AS (
    -- Latest competitor pricing by category
    SELECT
        ci.product_category,
        ci.competitor_name,
        COUNT(*)                                                  AS listing_count,
        ROUND(MIN(ci.price), 2)                                  AS comp_min_price,
        ROUND(AVG(ci.price), 2)                                  AS comp_avg_price,
        ROUND(MAX(ci.price), 2)                                  AS comp_max_price,
        MAX(ci.last_checked)                                      AS last_checked,
        -- Flag stale data
        CASE WHEN MAX(ci.last_checked) < now() - (:stale_days || ' days')::INTERVAL
            THEN TRUE ELSE FALSE
        END                                                       AS is_stale
    FROM competitive_intel ci
    GROUP BY ci.product_category, ci.competitor_name
)
SELECT
    cp.product_category,
    cp.competitor_name,
    cp.listing_count,

    -- Competitor pricing
    cp.comp_min_price,
    cp.comp_avg_price,
    cp.comp_max_price,

    -- Our pricing (matched by category)
    op.our_product_count,
    op.our_min_price,
    op.our_avg_price,
    op.our_max_price,

    -- Price position: positive = we are higher, negative = we are lower
    ROUND(op.our_avg_price - cp.comp_avg_price, 2)              AS price_diff,
    CASE WHEN cp.comp_avg_price > 0
        THEN ROUND((op.our_avg_price - cp.comp_avg_price) / cp.comp_avg_price * 100, 1)
        ELSE NULL
    END                                                          AS price_diff_pct,

    -- Data freshness
    cp.last_checked,
    cp.is_stale

FROM competitor_prices cp
LEFT JOIN our_prices op
    ON LOWER(cp.product_category) = LOWER(op.category_code)
WHERE (:category_filter IS NULL OR cp.product_category = :category_filter)
ORDER BY cp.product_category, cp.competitor_name;
