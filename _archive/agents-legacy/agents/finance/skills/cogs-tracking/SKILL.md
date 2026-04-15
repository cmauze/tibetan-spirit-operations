---
name: cogs-tracking
description: Track and maintain per-SKU cost of goods sold (COGS) including purchase price, freight, duty, and landed cost. Use this skill when recording new supplier invoices, updating product costs, calculating margins for pricing decisions, or when any skill needs accurate COGS data. This is the foundation for all profitability analysis.
version: "0.1.0"
category: finance
tags: [cogs, cost, margin]
author: operations-team
model: sonnet
cacheable: true
estimated_tokens: 850
phase: 1
depends_on: [shared/brand-guidelines, shared/supabase-ops-db]
external_apis: [supabase]
cost_budget_usd: 0.15
---

# COGS Tracking Skill

## Purpose

Maintain accurate per-SKU cost data in the `products` table so every other skill (pricing, margin reporting, channel profitability) has reliable cost information to work with.

## COGS Components

Total landed cost per unit = Purchase Price + Freight + Duty + Processing

```
landed_cost = purchase_price_usd + freight_per_unit + (purchase_price_usd * duty_rate) + processing_per_unit
```

### 1. Purchase Price
- Recorded in NPR (Nepalese Rupee) at time of purchase
- Converted to USD using exchange rate at time of payment
- Stored in `products.cogs_confirmed` (validated) or `products.cogs_estimated` (fallback)
- Source: Supplier invoices tracked in `supplier_payments` table

### 2. Freight Per Unit
- Total shipping cost from Nepal to Asheville ÷ number of units in shipment
- Varies significantly by shipment method (air freight ~$8-15/kg, sea freight ~$2-5/kg)
- Stored in `products.freight_per_unit`
- Updated each time a new shipment arrives with actual costs

### 3. Duty Rate
- US import duty varies by product category and HS code
- Stored in `products.duty_rate` (decimal, e.g., 0.05 for 5%)
- HS codes stored in `products.duty_hs_code`
- Key rates for our categories:
  - Incense: Generally duty-free or minimal (HS 3307)
  - Prayer flags (textiles): ~5-12% (HS 6307)
  - Singing bowls (metal): ~2-5% (HS 8306)
  - Statues (religious articles): Often duty-free (HS 9703 for handmade art)
  - Thangkas (paintings): Duty-free if original art (HS 9701)

### 4. Processing Per Unit
- FBA prep costs (if applicable): labeling, poly-bagging ($0.50-2.00/unit)
- Quality inspection costs
- Typically $0-2 per unit, often absorbed into overhead

## COGS Confidence Levels

Every product has a `cogs_confidence` enum:

| Level | Meaning | Action |
|-------|---------|--------|
| **confirmed** | COGS validated from actual supplier invoices + freight records | Use for all calculations |
| **estimated** | COGS estimated from category averages or similar products | Flag in reports, use for estimates |
| **unknown** | No cost data available | Cannot calculate margins — escalate |

**Phase 1 target**: Move all products from "estimated" (category averages) to "confirmed" (actual invoices) within first 90 days. The operations-manager's Nepal team provides invoice data; ceo validates.

## Category-Level Estimates (Fallback)

Until SKU-level COGS are confirmed, use these category averages from the financial model:

| Category | Avg COGS % of Revenue | Confidence |
|----------|----------------------|------------|
| Incense | 22.5% | Medium |
| Prayer Flags | 17.5% | Medium |
| Malas / Jewelry | 22.5% | Medium |
| Singing Bowls | 30% | Low |
| Statues | 35% | Low |
| Thangkas (painted) | 42.5% | Low |
| Thangkas (prints) | 12.5% | High |
| Offering Sets | 30% | Medium |

Low-confidence categories (singing bowls, statues, painted thangkas) have wide variance — individual items can range ±15% from the average. Prioritize getting confirmed COGS for these categories.

## Workflow: Recording a New Supplier Invoice

1. operations-manager provides invoice details (supplier name, items, quantities, NPR amounts)
2. Record in `supplier_payments` table with NPR amount, exchange rate, USD equivalent
3. Calculate per-unit purchase price: `total_usd / total_units`
4. Update `products.cogs_confirmed` for each SKU on the invoice
5. Update `products.cogs_confidence` to "confirmed"
6. Recalculate `products.freight_per_unit` if this invoice includes freight costs
7. Log the update to `skill_invocations` with full context

## Workflow: Monthly COGS Review

Run monthly (1st of month). For each product:
1. Check if `cogs_confidence` is still "confirmed" — has anything changed?
2. Check if exchange rate has moved >5% since last COGS update
3. Check if freight costs have changed with new shipment data
4. Flag any products where margin has dropped below `margin_floor_by_channel`
5. Generate report for ceo with COGS changes and margin implications

## Exchange Rate Handling

Nepal supplier payments are in NPR. The NPR/USD rate fluctuates.

- Record the exchange rate at time of each payment
- Use the payment-date rate for COGS calculations (not current rate)
- If rate moves >5% since last purchase, flag for margin review
- Source exchange rate from a reliable API (e.g., exchangerate-api.com)

## Output

```json
{
  "sku": "TS-INC-NADO-HAPPINESS",
  "cogs_components": {
    "purchase_price_usd": 2.15,
    "freight_per_unit": 0.45,
    "duty_amount": 0.00,
    "processing": 0.00,
    "total_landed_cost": 2.60
  },
  "confidence": "confirmed",
  "last_updated": "2026-03-15",
  "margin_at_current_price": {
    "shopify": 0.74,
    "etsy": 0.68,
    "amazon": 0.58
  }
}
```
