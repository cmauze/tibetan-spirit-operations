-- =============================================================================
-- Channel Profitability (P&L by Channel After Fees)
-- =============================================================================
-- True P&L by sales channel including COGS, channel fees, and gross profit.
--
-- Fee structures (from channel-config SKILL.md):
--   Shopify:   2.5% + $0.30 per transaction
--   Etsy:      ~10% effective (6.5% transaction + 3% + $0.25 processing)
--   Amazon:    ~30% effective (15% referral + FBA fees)
--   Wholesale: 0% fees (40-50% off retail pricing absorbs the discount)
--
-- Parameters:
--   :start_date — period start (inclusive), e.g. '2026-01-01'
--   :end_date   — period end (inclusive), e.g. '2026-03-31'
--   :channel    — optional channel filter (NULL for all channels)
-- =============================================================================

SELECT
    o.channel,
    COUNT(*)                                                     AS order_count,
    SUM(o.total_price)                                           AS revenue,

    -- COGS: sum of (quantity * unit COGS) across line items
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

    -- Channel fees
    SUM(
        CASE o.channel
            WHEN 'shopify'   THEN o.total_price * 0.025 + 0.30
            WHEN 'etsy'      THEN o.total_price * 0.10
            WHEN 'amazon'    THEN o.total_price * 0.30
            WHEN 'wholesale' THEN 0
        END
    )                                                            AS total_fees,

    -- Gross profit = revenue - COGS - fees
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

    -- Gross margin percentage
    CASE WHEN SUM(o.total_price) > 0
        THEN ROUND((
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
        ) / SUM(o.total_price), 4)
        ELSE 0
    END                                                          AS margin_pct,

    -- Average order value
    ROUND(AVG(o.total_price), 2)                                 AS avg_order_value

FROM orders o
WHERE o.created_at >= :start_date::TIMESTAMPTZ
  AND o.created_at <  (:end_date::DATE + INTERVAL '1 day')
  AND (:channel IS NULL OR o.channel = :channel::sales_channel)
GROUP BY o.channel
ORDER BY revenue DESC;
