---
name: channel-profitability
description: Calculate true per-channel profitability after ALL costs (COGS, platform fees, fulfillment, payment processing, allocated overhead) for Shopify D2C, Amazon FBA, Etsy, wholesale, and TS Travels. Use this skill on the monthly cron (5th of month, after reconciliation completes), when pricing-strategy needs channel margin data, or when ceo is evaluating channel expansion/contraction decisions. This is the single source of truth for "which channel actually makes money."
version: "0.1.0"
category: finance
tags: [channel, profitability, p-and-l]
author: operations-team
model: sonnet
cacheable: true
estimated_tokens: 2100
phase: 1
depends_on: [shared/brand-guidelines, shared/supabase-ops-db, shared/channel-config]
external_apis: [supabase]
cost_budget_usd: 0.15
---

# Channel Profitability Skill

## Purpose

Revenue by channel is vanity. Profit by channel is sanity. A $10K month on Amazon sounds great until you realize $3.5K went to Amazon fees, $2.8K was COGS, and $800 was FBA prep — leaving $2,900 (29% margin) vs. the same product on Shopify at 62% margin.

This skill calculates the *true* profitability of each channel by stacking ALL costs — not just the obvious ones. It uses the `channel_profitability_monthly` materialized view plus channel-specific fee calculations to give the ceo one report that answers: "Where should I invest the next marketing dollar?"

## Channel Cost Structures

### Shopify D2C (Products)
```
Revenue
- Payment processing: 2.4% + $0.30/txn (Shopify Payments)
- Shopify platform: $299/mo fixed (allocated per unit)
- COGS: per-SKU from cogs-tracking
- Shipping: actual Shippo cost (avg ~11.5% of revenue)
- Customer service: allocated Re:amaze cost
- Marketing: attributed spend from campaign-architecture
= Channel Profit
```

### Amazon FBA
```
Revenue
- Referral fee: 8-20% by category
- FBA fulfillment: $3.22-$6.75/unit
- Monthly storage: $0.87-2.40/cuft
- Return processing: ~3% of units * fulfillment fee
- FBA prep: $0.50-2.00/unit (warehouse-manager or 3PL)
- COGS: per-SKU from cogs-tracking
- Inbound shipping to FC: allocated per unit
- Amazon advertising (PPC): attributed spend
= Channel Profit
```

### Etsy
```
Revenue
- Transaction fee: 6.5% of item price + shipping
- Payment processing: 3% + $0.25/txn
- Listing fee: $0.20/listing (renews every 4 months)
- Offsite ads fee: 15% if >$10K trailing 12mo (mandatory)
- COGS: per-SKU from cogs-tracking
- Shipping: actual cost
- Etsy Ads (optional): attributed spend
= Channel Profit
```

### Wholesale (Espíritu Tibetano + Others)
```
Revenue (wholesale price = ~50-60% of retail)
- COGS: per-SKU from cogs-tracking
- Bulk shipping: actual freight cost
- Payment processing: wire/ACH (~$15-25/transfer)
- Account management: allocated mexico-fulfillment time
= Channel Profit
```

### TS Travels
```
Revenue
- COGS: ~80% (tours, accommodations, guides, transport)
- Payment processing: 2.4% + $0.30/txn
- Marketing: attributed spend
- spiritual-director consulting: allocated per trip
= Channel Profit
```

## Data Queries

### Monthly Channel Profitability (from materialized view)

```sql
SELECT
    channel,
    revenue,
    cogs,
    channel_fees,
    shipping_cost,
    marketing_allocated,
    overhead_allocated,
    gross_profit,
    ROUND(gross_profit / NULLIF(revenue, 0) * 100, 1) AS gross_margin_pct,
    gross_profit - marketing_allocated - overhead_allocated AS net_profit,
    ROUND(
        (gross_profit - marketing_allocated - overhead_allocated)
        / NULLIF(revenue, 0) * 100, 1
    ) AS net_margin_pct
FROM channel_profitability_monthly
WHERE month = DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month')
ORDER BY net_profit DESC;
```

### Channel Trend (3-month rolling)

```sql
SELECT
    channel,
    month,
    revenue,
    net_profit,
    ROUND(net_profit / NULLIF(revenue, 0) * 100, 1) AS net_margin_pct,
    LAG(ROUND(net_profit / NULLIF(revenue, 0) * 100, 1)) OVER (
        PARTITION BY channel ORDER BY month
    ) AS prior_month_margin_pct
FROM channel_profitability_monthly
WHERE month >= DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '3 months'
ORDER BY channel, month;
```

### Per-SKU Channel Comparison

```sql
SELECT
    pmd.sku,
    p.title,
    p.category,
    pmd.shopify_margin_pct,
    pmd.etsy_margin_pct,
    pmd.amazon_margin_pct,
    pmd.shopify_margin_pct - COALESCE(pmd.amazon_margin_pct, 0) AS shopify_vs_amazon_pp,
    pmd.total_revenue_7d,
    p.margin_floor_by_channel
FROM product_margin_detail pmd
JOIN products p ON p.sku = pmd.sku
WHERE p.status = 'active'
ORDER BY shopify_vs_amazon_pp DESC;
```

### Channel Contribution Analysis

```sql
SELECT
    channel,
    SUM(revenue) AS total_revenue,
    ROUND(SUM(revenue) / NULLIF((SELECT SUM(revenue) FROM channel_profitability_monthly WHERE month = DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month')), 0) * 100, 1) AS revenue_share_pct,
    SUM(net_profit) AS total_profit,
    ROUND(SUM(net_profit) / NULLIF((SELECT SUM(net_profit) FROM channel_profitability_monthly WHERE month = DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month')), 0) * 100, 1) AS profit_share_pct
FROM channel_profitability_monthly
WHERE month = DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month')
GROUP BY channel
ORDER BY total_profit DESC;
```

## Analysis Workflow

```
1. GATHER DATA
   a. Pull channel_profitability_monthly for current and prior months
   b. Pull product_margin_detail for SKU-level channel comparison
   c. Pull marketing spend attribution from marketing_performance
   d. Pull fee data from amazon_fees (for Amazon-specific analysis)

2. CALCULATE FULLY-LOADED PROFITABILITY
   a. For each channel: Revenue - COGS - Fees - Shipping - Marketing - Overhead
   b. Overhead allocation: proportional to revenue or transaction count
   c. Marketing attribution: direct spend per channel from campaign tags

3. COMPARE AND RANK
   a. Rank channels by: net margin %, total profit, profit per order
   b. Identify cross-channel margin gaps (same SKU, different profitability)
   c. Calculate marginal ROI: "if we put $1 more into this channel, what do we get?"

4. GENERATE RECOMMENDATIONS
   a. SKUs that should move channels (profitable on Shopify, not on Amazon)
   b. Channels that deserve more investment (high margin, room to grow)
   c. Channels that need pruning (low margin, high effort)
   d. Pricing gaps: where channel prices should differ

5. GENERATE REPORT
```

## Report Format

```
MONTHLY CHANNEL PROFITABILITY — {month}
══════════════════════════════════════════

CHANNEL P&L COMPARISON
─────────────────────────────────────────────────────────────
| Channel      | Revenue  | COGS    | Fees    | Ship    | Mktg    | Net Profit | Margin |
|--------------|----------|---------|---------|---------|---------|------------|--------|
| Shopify D2C  | $22,000  | $5,280  | $828    | $2,530  | $4,000  | $9,362     | 42.6%  |
| Amazon FBA   | $4,500   | $1,350  | $1,575  | incl    | $900    | $675       | 15.0%  |
| Etsy         | $2,100   | $504    | $357    | $242    | $200    | $797       | 38.0%  |
| Wholesale    | $3,000   | $1,500  | $25     | $180    | $0      | $1,295     | 43.2%  |
| TS Travels   | $16,700  | $13,360 | $401    | $0      | $1,000  | $1,939     | 11.6%  |
| TOTAL        | $48,300  | $21,994 | $3,186  | $2,952  | $6,100  | $14,068    | 29.1%  |

CHANNEL TRENDS (3-month)
─────────────────────────────────────────
| Channel      | M-2     | M-1     | Current | Trend |
|--------------|---------|---------|---------|-------|
| Shopify D2C  | 40.1%   | 41.3%   | 42.6%   |   ▲   |
| Amazon FBA   | 18.2%   | 16.5%   | 15.0%   |   ▼   |
| Etsy         | 35.1%   | 37.2%   | 38.0%   |   ▲   |

KEY INSIGHTS
─────────────────────────────────────────
1. Shopify D2C delivers 67% of total profit on 46% of revenue — highest-leverage channel
2. Amazon margin declining: FBA fee increase + storage surcharge eating into profit
3. Wholesale quietly profitable at 43.2% — explore expanding to 2-3 more retailers
4. 8 SKUs profitable on Shopify but negative on Amazon — recommend delisting

ACTION ITEMS
─────────────────────────────────────────
1. [AMAZON] Review 8 unprofitable ASINs — delist or price-increase
2. [WHOLESALE] Reach out to 2 additional retailers (see assortment-planning)
3. [ETSY] Margin improving — consider expanding Etsy catalog by 15 SKUs
```

## Cross-Channel Pricing Intelligence

One of this skill's unique capabilities: identifying where the same product has very different profitability across channels, which informs whether channel-specific pricing is needed.

**Rule**: Shopify should always be the lowest price (reward D2C customers). Amazon and Etsy can be 10-20% higher to offset fees. Wholesale is 40-50% of retail.

```sql
-- Cross-channel price/margin comparison
SELECT
    p.sku,
    p.title,
    p.shopify_price,
    p.amazon_price,
    p.etsy_price,
    pmd.shopify_margin_pct,
    pmd.amazon_margin_pct,
    pmd.etsy_margin_pct,
    CASE
        WHEN pmd.amazon_margin_pct < 10 AND pmd.shopify_margin_pct > 40
            THEN 'DELIST from Amazon or raise price 15%+'
        WHEN pmd.etsy_margin_pct < 15 AND pmd.shopify_margin_pct > 40
            THEN 'Raise Etsy price 10%+'
        ELSE 'OK'
    END AS recommendation
FROM products p
JOIN product_margin_detail pmd ON pmd.sku = p.sku
WHERE p.status = 'active'
  AND p.amazon_price IS NOT NULL
ORDER BY (pmd.shopify_margin_pct - COALESCE(pmd.amazon_margin_pct, 0)) DESC;
```

## Model Routing

- **Data gathering and calculations**: Haiku 4.5 — deterministic queries and math
- **Monthly report with insights**: Sonnet 4.6 — needs narrative about channel strategy
- **Channel expansion/contraction recommendations**: Sonnet 4.6 — business judgment
- **Quarterly strategic channel review**: Opus 4.6 — only for major channel decisions

## Phase 1 Behavior

In Phase 1, this skill:
- Generates monthly profitability reports
- Identifies unprofitable SKUs by channel
- Recommends pricing and catalog changes

Does NOT:
- Automatically change prices on any channel
- Delist products from any channel
- Adjust marketing spend allocation

All recommendations go through ceo for decision. Pricing changes route through `pricing-strategy` skill.

## Escalation Paths

| Situation | Route To | Method | SLA |
|-----------|----------|--------|-----|
| Monthly channel report | ceo | Dashboard | 5th of month |
| Channel margin drops below 10% | ceo | Dashboard (flagged) | 48 hours |
| New channel launch (first 90 days) | ceo | Weekly report | Weekly |
| Channel becomes net-negative | ceo | Email alert | 24 hours |
| Fee structure change detected | ceo + pricing-strategy | Dashboard + email | 1 week |

Read `skills/shared/escalation-matrix/SKILL.md` for the full escalation reference.

## Output Format

```json
{
  "report_type": "monthly",
  "period": "2026-07",
  "channels": [
    {
      "channel": "shopify",
      "revenue": 22000,
      "cogs": 5280,
      "channel_fees": 828,
      "shipping": 2530,
      "marketing_allocated": 4000,
      "overhead_allocated": 500,
      "net_profit": 8862,
      "net_margin_pct": 40.3,
      "revenue_share_pct": 45.5,
      "profit_share_pct": 63.0,
      "trend": "up",
      "trend_change_pp": 1.3
    }
  ],
  "cross_channel_alerts": [
    {
      "sku": "TS-BOWL-HH-10IN",
      "shopify_margin": 58.2,
      "amazon_margin": -3.1,
      "recommendation": "Delist from Amazon — negative margin after fees"
    }
  ],
  "action_items": [
    "8 SKUs unprofitable on Amazon — recommend delisting",
    "Wholesale channel underexplored — 43% margin, add retailers"
  ],
  "phase": 1,
  "confidence": 0.90
}
```

## Dependencies

- Read `skills/shared/supabase-ops-db/SKILL.md` for database schema (channel_profitability_monthly view, product_margin_detail view)
- Uses COGS from `skills/finance/cogs-tracking/SKILL.md`
- Uses Amazon fee data from `skills/finance/amazon-fee-analysis/SKILL.md`
- Feeds pricing decisions to `skills/category-management/pricing-strategy/SKILL.md`
- Read `skills/shared/channel-config/SKILL.md` for fee structures and API scopes
- Read `skills/shared/escalation-matrix/SKILL.md` for routing decisions
