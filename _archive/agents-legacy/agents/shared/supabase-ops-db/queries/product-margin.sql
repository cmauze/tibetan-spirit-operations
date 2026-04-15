-- =============================================================================
-- Product Margin by SKU with COGS Confidence
-- =============================================================================
-- Returns per-SKU margin breakdown including landed cost components.
-- Uses confirmed COGS when available, falls back to estimated.
--
-- Parameters:
--   :status_filter — product status (default 'active')
--   :confidence    — optional COGS confidence filter (confirmed/estimated/unknown)
--
-- Usage:
--   Replace :status_filter with 'active' and :confidence with desired level,
--   or remove the confidence WHERE clause to see all products.
-- =============================================================================

SELECT
    p.sku,
    p.title,
    p.price                                                      AS retail_price,
    p.cogs_confidence,

    -- Cost components
    COALESCE(p.cogs_confirmed, p.cogs_estimated)                 AS cogs,
    p.freight_per_unit,
    p.duty_rate,
    COALESCE(p.cogs_confirmed, p.cogs_estimated, 0)
        * COALESCE(p.duty_rate, 0)                               AS duty_amount,

    -- Landed cost = cogs + freight + duty
    COALESCE(p.cogs_confirmed, p.cogs_estimated, 0)
        + COALESCE(p.freight_per_unit, 0)
        + (COALESCE(p.cogs_confirmed, p.cogs_estimated, 0) * COALESCE(p.duty_rate, 0))
                                                                 AS landed_cost,

    -- Gross margin (before channel fees)
    p.price
        - (COALESCE(p.cogs_confirmed, p.cogs_estimated, 0)
           + COALESCE(p.freight_per_unit, 0)
           + (COALESCE(p.cogs_confirmed, p.cogs_estimated, 0) * COALESCE(p.duty_rate, 0)))
                                                                 AS gross_margin,

    -- Margin percentage
    CASE WHEN p.price > 0
        THEN ROUND((
            p.price
            - (COALESCE(p.cogs_confirmed, p.cogs_estimated, 0)
               + COALESCE(p.freight_per_unit, 0)
               + (COALESCE(p.cogs_confirmed, p.cogs_estimated, 0) * COALESCE(p.duty_rate, 0)))
        ) / p.price, 4)
        ELSE 0
    END                                                          AS margin_pct,

    -- Channel margin floors for comparison
    p.margin_floor_by_channel

FROM products p
WHERE p.status = :status_filter
  AND (:confidence IS NULL OR p.cogs_confidence = :confidence::cogs_confidence_level)
ORDER BY margin_pct ASC;
