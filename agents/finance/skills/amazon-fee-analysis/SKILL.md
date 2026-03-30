---
name: amazon-fee-analysis
description: Calculate and track all Amazon FBA fees (referral, fulfillment, storage, returns) to determine true per-SKU profitability on Amazon. Use this skill when launching new products on Amazon, during monthly fee reconciliation, when pricing-strategy needs Amazon-specific margin data, or when investigating why an ASIN is unprofitable. Runs on weekly cron and on-demand.
version: "0.1.0"
category: finance
tags: [amazon, fees, fba]
author: operations-team
model: sonnet
cacheable: true
estimated_tokens: 1700
phase: 1
depends_on: [shared/brand-guidelines, shared/channel-config]
external_apis: [supabase, amazon]
cost_budget_usd: 0.15
---

# Amazon Fee Analysis Skill

## Purpose

Amazon takes 30-45% of every sale through a complex stack of fees. This skill breaks down exactly where each dollar goes so the ceo can make informed decisions about which products belong on Amazon and at what price. Without this, you're guessing whether Amazon is profitable — and for sacred Buddhist items with moderate ASPs ($15-80 range), fee pressure is real.

## Amazon Fee Structure for Tibetan Spirit

### Fee Components (in order of impact)

| Fee Type | Typical Range | Calculation | Notes |
|----------|---------------|-------------|-------|
| **Referral Fee** | 15% | % of item price + shipping | Religious/spiritual items category |
| **FBA Fulfillment** | $3.22-$6.75 | Per-unit, weight/size based | Standard-size: most TS products |
| **Monthly Storage** | $0.87-2.40/cuft | Per-cuft, monthly | Peak surcharge Oct-Dec |
| **Returns Processing** | $3.22-$6.75 | Same as fulfillment fee | Only on returned items |
| **Removal/Disposal** | $0.97-$1.85 | Per-unit | For slow-moving inventory |

### Category-Specific Referral Rates

Tibetan Spirit products fall into multiple Amazon categories:

| Product Type | Amazon Category | Referral % | Min Referral |
|-------------|-----------------|------------|--------------|
| Incense | Health & Household | 8% or 15% | $1.00 |
| Singing Bowls | Musical Instruments | 15% | $1.00 |
| Malas/Jewelry | Jewelry (handmade) | 20% | $2.00 |
| Statues | Home Décor | 15% | $1.00 |
| Prayer Flags | Home Décor | 15% | $1.00 |
| Thangkas | Artwork | 15% | $1.00 |

**Key risk**: Malas classified as jewelry face a 20% referral fee, which may make low-priced malas (<$25) unprofitable on Amazon. Consider listing under "Meditation Accessories" category instead (15%).

### FBA Size Tiers

| Size Tier | Dimensions | Weight | Fulfillment Fee |
|-----------|-----------|--------|-----------------|
| Small standard | ≤15x12x0.75" | ≤16oz | $3.22 |
| Large standard | ≤18x14x8" | ≤20lb | $4.75-$6.75 |
| Small oversize | ≤60x30" | ≤70lb | $9.73+ |
| Large oversize | ≤108" longest | ≤150lb | $89.98+ |

Most TS products are small or large standard. Large singing bowls (10"+) may hit small oversize — check dimensions before listing.

## Data Queries

### Per-SKU Amazon Fee Breakdown

```sql
SELECT
    af.sku,
    p.title,
    af.selling_price,
    af.referral_fee,
    af.fba_fulfillment_fee,
    af.storage_fee_monthly,
    af.return_fee_allocated,
    af.total_amazon_fees,
    af.selling_price - af.total_amazon_fees AS after_fee_revenue,
    p.cogs_confirmed,
    af.selling_price - af.total_amazon_fees - COALESCE(p.cogs_confirmed, p.cogs_estimated) AS net_profit,
    ROUND(
        (af.selling_price - af.total_amazon_fees - COALESCE(p.cogs_confirmed, p.cogs_estimated))
        / NULLIF(af.selling_price, 0) * 100, 1
    ) AS net_margin_pct
FROM amazon_fees af
JOIN products p ON p.sku = af.sku
WHERE af.period = DATE_TRUNC('month', CURRENT_DATE)
ORDER BY net_margin_pct ASC;
```

### Fee Burden by Category

```sql
SELECT
    p.category,
    COUNT(DISTINCT af.sku) AS sku_count,
    AVG(af.total_amazon_fees / NULLIF(af.selling_price, 0) * 100) AS avg_fee_pct,
    SUM(af.total_amazon_fees) AS total_fees_period,
    SUM(af.selling_price - af.total_amazon_fees - COALESCE(p.cogs_confirmed, p.cogs_estimated)) AS category_net_profit
FROM amazon_fees af
JOIN products p ON p.sku = af.sku
WHERE af.period = DATE_TRUNC('month', CURRENT_DATE)
GROUP BY p.category
ORDER BY avg_fee_pct DESC;
```

### Unprofitable ASINs

```sql
SELECT
    af.sku,
    p.title,
    af.selling_price,
    af.total_amazon_fees,
    COALESCE(p.cogs_confirmed, p.cogs_estimated) AS cogs,
    af.selling_price - af.total_amazon_fees - COALESCE(p.cogs_confirmed, p.cogs_estimated) AS net_profit,
    af.units_sold_30d
FROM amazon_fees af
JOIN products p ON p.sku = af.sku
WHERE af.selling_price - af.total_amazon_fees - COALESCE(p.cogs_confirmed, p.cogs_estimated) < 0
  AND af.units_sold_30d > 0
ORDER BY net_profit ASC;
```

### Storage Cost Analysis (Peak Season Awareness)

```sql
SELECT
    af.sku,
    p.title,
    ie.fba_allocated AS fba_units,
    af.storage_fee_monthly,
    af.units_sold_30d,
    CASE
        WHEN af.units_sold_30d = 0 THEN 'STRANDED'
        WHEN ie.fba_allocated / NULLIF(af.units_sold_30d, 0) > 6 THEN 'OVERSTOCKED (6+ mo supply)'
        WHEN ie.fba_allocated / NULLIF(af.units_sold_30d, 0) > 3 THEN 'HIGH (3-6 mo supply)'
        ELSE 'HEALTHY'
    END AS stock_health
FROM amazon_fees af
JOIN products p ON p.sku = af.sku
JOIN inventory_extended ie ON ie.sku = af.sku
WHERE ie.fba_allocated > 0
ORDER BY af.storage_fee_monthly DESC;
```

## Analysis Workflow

```
1. INGEST FEE DATA
   a. Pull Amazon Settlement Reports (bi-weekly)
   b. Parse fee breakdown by transaction type
   c. Allocate storage fees to individual SKUs
   d. Calculate return fee allocation (returns ÷ units sold * fulfillment fee)

2. CALCULATE PER-SKU PROFITABILITY
   a. Revenue = selling price (net of promotions/coupons)
   b. Amazon fees = referral + FBA + storage + return allocation
   c. COGS = from cogs-tracking (confirmed or estimated)
   d. Net profit = Revenue - Amazon fees - COGS
   e. Net margin % = Net profit / Revenue

3. IDENTIFY ACTIONS
   a. Unprofitable SKUs: price increase needed or delist
   b. Overstocked SKUs: create removal order or run promotion
   c. Category mis-classification: reclassify for lower referral fee
   d. Size tier optimization: repackage to fit lower tier

4. GENERATE REPORT
   a. Fee summary by category
   b. Top/bottom 10 SKUs by profitability
   c. Action items with estimated impact
```

## Minimum Viable Price Calculator

For any SKU, calculate the minimum Amazon price to achieve target margin:

```
min_price = (COGS + target_profit) / (1 - referral_rate - fba_fee_pct)

Where:
  fba_fee_pct = fba_fulfillment_fee / selling_price (iterative)
  target_profit = min_margin * selling_price (iterative)
```

Simplified for standard-size items:
```
min_price ≈ (COGS + FBA_fee) / (1 - referral_rate - target_margin)
```

Example: Incense set, COGS $2.60, FBA $3.22, 15% referral, 20% target margin
```
min_price = ($2.60 + $3.22) / (1 - 0.15 - 0.20) = $5.82 / 0.65 = $8.95
```

If Shopify price is $9.99, Amazon price needs to be at least $8.95 to hit 20% margin. This is viable.

## Model Routing

- **Fee data ingestion and calculation**: Haiku 4.5 — deterministic parsing and math
- **Profitability analysis and reporting**: Sonnet 4.6 — business context for recommendations
- **Category re-classification decisions**: Sonnet 4.6 — requires knowledge of Amazon category rules
- **Strategic Amazon channel decisions** (expand/contract catalog): Opus 4.6 — only for quarterly reviews

## Phase 1 Behavior

In Phase 1, this skill:
- Pulls and analyzes fee data
- Generates profitability reports
- Recommends pricing changes and delisting candidates

Does NOT:
- Automatically change Amazon prices
- Create removal orders
- Delist products

All actions go through ceo for approval. Pricing changes route through `pricing-strategy` skill.

## Escalation Paths

| Situation | Route To | Method | SLA |
|-----------|----------|--------|-----|
| Weekly fee report | ceo | Dashboard | Monday |
| SKU negative margin discovered | ceo | Dashboard (flagged) | 48 hours |
| Amazon fee structure change announced | ceo | Email alert | 24 hours |
| Storage fees > 5% of Amazon revenue | ceo | Dashboard + email | 1 week |
| >20% of Amazon catalog unprofitable | ceo | Email (strategic review) | 1 week |

## Output Format

```json
{
  "report_type": "weekly",
  "period": "2026-07-01",
  "summary": {
    "total_amazon_revenue": 4200.00,
    "total_fees": 1470.00,
    "total_cogs": 1260.00,
    "net_profit": 1470.00,
    "fee_pct_of_revenue": 35.0,
    "net_margin_pct": 35.0,
    "active_asins": 45,
    "unprofitable_asins": 3
  },
  "by_category": [
    {
      "category": "Incense",
      "sku_count": 12,
      "revenue": 1800.00,
      "avg_fee_pct": 32.1,
      "net_margin_pct": 38.2
    }
  ],
  "unprofitable_skus": [
    {
      "sku": "TS-MALA-TURQ-108",
      "selling_price": 18.99,
      "total_fees": 8.72,
      "cogs": 4.28,
      "net_profit": 5.99,
      "recommendation": "Price increase to $24.99 or move to Handmade category"
    }
  ],
  "action_items": [
    "3 SKUs unprofitable — see recommendations",
    "Holiday storage surcharge begins Oct 1 — review FBA inventory levels"
  ],
  "phase": 1,
  "confidence": 0.88
}
```

## Dependencies

- Read `agents/shared/supabase-ops-db/SKILL.md` for database schema
- Uses COGS from `agents/finance/skills/cogs-tracking/SKILL.md`
- Feeds into `agents/finance/skills/channel-profitability/SKILL.md` for cross-channel comparison
- Coordinates with `agents/finance/skills/margin-reporting/SKILL.md` for unified margin view
- Read `agents/shared/channel-config/SKILL.md` for Amazon API scopes and fee schedules
