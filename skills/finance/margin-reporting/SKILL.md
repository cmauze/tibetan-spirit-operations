---
name: margin-reporting
description: Generate weekly margin reports from the product_margin_detail materialized view. Use this skill on the weekly cron (Monday 9 AM ET), when Chris requests an ad-hoc margin review, or when pricing-strategy needs current margin data. Breaks down profitability by SKU, category, and channel with trend indicators and below-floor alerts.
---

# Margin Reporting Skill

## Purpose

Produce a clear, actionable margin report that tells Chris exactly where the business is making and losing money. This skill reads pre-computed data from the `product_margin_detail` materialized view and transforms it into a report with:
1. **SKU-level margins** with COGS confidence indicators
2. **Category rollups** showing which product lines drive profit
3. **Channel comparison** showing true profitability after all fees
4. **Trend arrows** (up/down/flat vs. prior week)
5. **Below-floor alerts** for SKUs violating minimum margin thresholds

The report is for Chris's strategic decision-making. It must be accurate, concise, and highlight what needs attention.

## Report Generation Workflow

```
1. GATHER DATA
   a. Query product_margin_detail view for all active SKUs
   b. Query channel_profitability_monthly for channel-level rollup
   c. Query prior week's report from skill_invocations for trend comparison

2. CALCULATE TRENDS
   a. For each SKU: compare current margin % to prior week
   b. Assign trend indicator:
      - margin improved >= 2pp  -> up_arrow (green)
      - margin declined >= 2pp  -> down_arrow (red)
      - margin changed < 2pp   -> flat (neutral)

3. FLAG BELOW-FLOOR SKUs
   a. Check each SKU's margin against margin_floor_by_channel (JSONB)
   b. If margin < floor for ANY channel: flag for review
   c. If margin < 0 (negative) on any channel: flag URGENT

4. GENERATE REPORT
   a. Executive summary (3-5 lines)
   b. SKU detail table
   c. Category rollup
   d. Channel comparison
   e. Action items (below-floor SKUs, COGS unknowns, trend alerts)
```

## Data Queries

### SKU-level margin data

```sql
SELECT
    pmd.sku,
    p.title,
    p.cogs_confirmed,
    p.cogs_estimated,
    p.cogs_confidence,
    p.freight_per_unit,
    p.duty_rate,
    p.margin_floor_by_channel,
    pmd.shopify_margin_pct,
    pmd.etsy_margin_pct,
    pmd.amazon_margin_pct,
    pmd.shopify_units_sold_7d,
    pmd.etsy_units_sold_7d,
    pmd.amazon_units_sold_7d,
    pmd.total_revenue_7d,
    pmd.total_cogs_7d,
    pmd.total_gross_profit_7d
FROM product_margin_detail pmd
JOIN products p ON p.sku = pmd.sku
WHERE p.status = 'active'
ORDER BY pmd.total_gross_profit_7d DESC;
```

### Category rollup

```sql
SELECT
    p.category,
    COUNT(DISTINCT pmd.sku) AS sku_count,
    SUM(pmd.total_revenue_7d) AS category_revenue,
    SUM(pmd.total_cogs_7d) AS category_cogs,
    SUM(pmd.total_gross_profit_7d) AS category_profit,
    ROUND(
        SUM(pmd.total_gross_profit_7d) / NULLIF(SUM(pmd.total_revenue_7d), 0) * 100,
        1
    ) AS margin_pct
FROM product_margin_detail pmd
JOIN products p ON p.sku = pmd.sku
WHERE p.status = 'active'
GROUP BY p.category
ORDER BY category_profit DESC;
```

### Channel profitability (from materialized view)

```sql
SELECT
    channel,
    revenue,
    cogs,
    channel_fees,
    shipping_cost,
    gross_profit,
    ROUND(gross_profit / NULLIF(revenue, 0) * 100, 1) AS margin_pct
FROM channel_profitability_monthly
WHERE month = DATE_TRUNC('month', CURRENT_DATE)
ORDER BY gross_profit DESC;
```

### Below-floor SKUs

```sql
SELECT
    pmd.sku,
    p.title,
    p.margin_floor_by_channel,
    pmd.shopify_margin_pct,
    pmd.etsy_margin_pct,
    pmd.amazon_margin_pct
FROM product_margin_detail pmd
JOIN products p ON p.sku = pmd.sku
WHERE p.status = 'active'
  AND (
    pmd.shopify_margin_pct < (p.margin_floor_by_channel->>'shopify')::numeric
    OR pmd.etsy_margin_pct < (p.margin_floor_by_channel->>'etsy')::numeric
    OR pmd.amazon_margin_pct < (p.margin_floor_by_channel->>'amazon')::numeric
  )
ORDER BY LEAST(
    pmd.shopify_margin_pct,
    COALESCE(pmd.etsy_margin_pct, 100),
    COALESCE(pmd.amazon_margin_pct, 100)
) ASC;
```

### Prior week comparison (from skill_invocations)

```sql
SELECT structured_result
FROM skill_invocations
WHERE skill_name = 'margin-reporting'
  AND timestamp >= CURRENT_DATE - INTERVAL '14 days'
ORDER BY timestamp DESC
LIMIT 1;
```

## Report Format

The weekly report uses this structure. Trend arrows indicate change from prior week.

```
WEEKLY MARGIN REPORT — Week of {date}
══════════════════════════════════════════

EXECUTIVE SUMMARY
Revenue: ${total_revenue} ({trend} vs prior week)
Gross Profit: ${total_profit} ({margin_pct}%)
SKUs below floor: {count}
COGS unconfirmed: {count} SKUs

─── BY CATEGORY ───────────────────────────
| Category        | Revenue  | Margin % | Trend |
|-----------------|----------|----------|-------|
| Singing Bowls   | $4,200   | 62.3%    |   ▲   |
| Incense         | $2,800   | 71.5%    |   ─   |
| Malas           | $1,950   | 68.2%    |   ▼   |
| Statues         | $1,400   | 55.8%    |   ▲   |
| Thangkas        | $890     | 48.1%    |   ─   |
| Prayer Flags    | $620     | 78.3%    |   ─   |
| Other           | $340     | 64.0%    |   ▲   |

─── BY CHANNEL ────────────────────────────
| Channel  | Revenue  | Fees    | Margin % |
|----------|----------|---------|----------|
| Shopify  | $9,200   | $280    | 67.4%    |
| Etsy     | $2,100   | $231    | 54.2%    |
| Amazon   | $900     | $315    | 38.1%    |

─── BELOW-FLOOR ALERTS ───────────────────
| SKU                | Channel  | Margin | Floor | Gap   |
|--------------------|----------|--------|-------|-------|
| TS-BOWL-HH-10IN   | Amazon   | 22.1%  | 30%   | -7.9% |
| TS-MALA-TURQ-108  | Etsy     | 28.3%  | 35%   | -6.7% |

─── ACTION ITEMS ──────────────────────────
1. [PRICING] TS-BOWL-HH-10IN below floor on Amazon — consider price increase or delist
2. [COGS] 8 SKUs still at "estimated" confidence — Jhoti to provide invoices
3. [TREND] Mala category margin declined 3.2pp — investigate supplier price increase
```

**Trend arrow rules:**
- **▲** (up): margin improved >= 2 percentage points vs. prior week
- **▼** (down): margin declined >= 2 percentage points vs. prior week
- **─** (flat): margin change < 2 percentage points

## Model Routing

- **Data gathering and calculation**: Haiku 4.5 -- deterministic queries and math
- **Trend analysis and executive summary**: Sonnet 4.6 -- requires narrative judgment about what matters
- **Action item recommendations**: Sonnet 4.6 -- business context needed for actionable suggestions
- **Complex margin analysis** (quarterly deep dives): Opus 4.6 -- strategic recommendations only

## Phase 1 Behavior

In Phase 1, this skill generates reports but does NOT:
- Automatically adjust prices based on margin data
- Delist below-floor products
- Change COGS entries

All actions require human decision:
- Chris reviews the weekly report via dashboard
- Pricing changes go through the pricing-strategy skill with Chris approval
- COGS corrections go through cogs-tracking with Jhoti/Chris confirmation

## Escalation Paths

| Situation | Route To | Method | SLA |
|-----------|----------|--------|-----|
| Routine weekly report | Chris | Dashboard | Monday 9 AM ET |
| SKU with negative margin on any channel | Chris | Dashboard (flagged URGENT) | 24 hours |
| >5 SKUs below floor | Chris | Dashboard + email alert | 24 hours |
| COGS confidence "unknown" on >10% of catalog | Chris + Jhoti | Dashboard + WhatsApp | 1 week |
| Category margin decline >5pp week-over-week | Chris | Dashboard + email alert | 48 hours |
| Ad-hoc report request | Chris | Dashboard | Same day |

Read `skills/shared/escalation-matrix/SKILL.md` for the full escalation reference.

## Output Format

```json
{
  "report_type": "weekly",
  "week_of": "2026-03-16",
  "summary": {
    "total_revenue": 12200.00,
    "total_cogs": 4270.00,
    "total_gross_profit": 7930.00,
    "overall_margin_pct": 65.0,
    "revenue_trend": "up",
    "revenue_change_pct": 4.2,
    "skus_below_floor": 2,
    "skus_cogs_unconfirmed": 8
  },
  "by_category": [
    {
      "category": "Singing Bowls",
      "revenue": 4200.00,
      "margin_pct": 62.3,
      "trend": "up",
      "trend_change_pp": 3.1
    }
  ],
  "by_channel": [
    {
      "channel": "shopify",
      "revenue": 9200.00,
      "fees": 280.00,
      "margin_pct": 67.4
    }
  ],
  "below_floor_alerts": [
    {
      "sku": "TS-BOWL-HH-10IN",
      "channel": "amazon",
      "current_margin_pct": 22.1,
      "floor_pct": 30.0,
      "gap_pp": -7.9
    }
  ],
  "action_items": [
    "TS-BOWL-HH-10IN below floor on Amazon — consider price increase or delist",
    "8 SKUs at estimated COGS — Jhoti to provide invoices"
  ],
  "formatted_report": "...",
  "phase": 1,
  "confidence": 0.92
}
```

## Dependencies

- Read `skills/shared/supabase-ops-db/SKILL.md` for database schema (product_margin_detail view, channel_profitability_monthly view)
- Reads COGS data maintained by `skills/finance/cogs-tracking/SKILL.md`
- Read `skills/shared/channel-config/SKILL.md` for fee structures by channel
- Read `skills/shared/escalation-matrix/SKILL.md` for routing decisions
