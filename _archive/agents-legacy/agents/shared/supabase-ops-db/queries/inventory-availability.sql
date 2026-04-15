-- =============================================================================
-- Cross-Channel Inventory Availability
-- =============================================================================
-- Returns inventory status for all active products including FBA allocation,
-- in-transit stock, Nepal pipeline, and calculated available-to-sell quantity.
--
-- Parameters:
--   :stock_status_filter — optional filter: 'stockout', 'critical', 'reorder', 'healthy'
--                          Pass NULL to see all statuses.
--
-- Available-to-sell formula (from channel-config SKILL.md):
--   available_to_sell = total_on_hand - fba_allocated - safety_stock
-- =============================================================================

SELECT
    ie.sku,
    p.title,
    p.status                                                     AS product_status,

    -- Stock levels by location
    ie.total_on_hand,
    ie.shopify_available,
    ie.fba_allocated,
    ie.fba_in_transit,
    ie.nepal_pipeline,
    ie.nepal_eta,

    -- Thresholds
    ie.reorder_trigger_qty,
    ie.safety_stock,

    -- Calculated availability
    ie.total_on_hand - ie.fba_allocated - ie.safety_stock        AS available_to_sell,

    -- Stock status classification
    CASE
        WHEN ie.total_on_hand <= 0                               THEN 'stockout'
        WHEN ie.total_on_hand <= ie.safety_stock                 THEN 'critical'
        WHEN ie.total_on_hand <= ie.reorder_trigger_qty          THEN 'reorder'
        ELSE 'healthy'
    END                                                          AS stock_status,

    -- Days of supply (based on 30-day trailing sales)
    COALESCE(daily_sales.avg_daily, 0)                           AS avg_daily_sales,
    CASE WHEN COALESCE(daily_sales.avg_daily, 0) > 0
        THEN ROUND(ie.total_on_hand / daily_sales.avg_daily)
        ELSE NULL
    END                                                          AS days_of_supply

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
WHERE p.status = 'active'
  AND (
    :stock_status_filter IS NULL
    OR CASE
        WHEN ie.total_on_hand <= 0                               THEN 'stockout'
        WHEN ie.total_on_hand <= ie.safety_stock                 THEN 'critical'
        WHEN ie.total_on_hand <= ie.reorder_trigger_qty          THEN 'reorder'
        ELSE 'healthy'
    END = :stock_status_filter
  )
ORDER BY
    CASE
        WHEN ie.total_on_hand <= 0                               THEN 1
        WHEN ie.total_on_hand <= ie.safety_stock                 THEN 2
        WHEN ie.total_on_hand <= ie.reorder_trigger_qty          THEN 3
        ELSE 4
    END,
    ie.sku;
