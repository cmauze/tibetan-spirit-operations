---
name: fulfillment-domestic
description: Route and process domestic (US) orders for fulfillment by warehouse-manager in Asheville, NC. Use this skill when a new Shopify order is received, when generating daily pick/pack lists, when selecting carriers and generating shipping labels, or when handling fulfillment exceptions (backorders, address issues, multi-item orders).
version: "0.1.0"
category: operations
tags: [fulfillment, shipping, domestic]
author: operations-team
model: sonnet
cacheable: true
estimated_tokens: 800
phase: 1
depends_on: [shared/brand-guidelines, shared/channel-config]
external_apis: [supabase, shopify]
cost_budget_usd: 0.15
---

# Domestic Fulfillment Skill

## Purpose

Process US domestic orders through the warehouse-manager's Asheville warehouse. This skill handles order routing, pick list generation, carrier selection, and exception handling.

## Order Routing Logic

When a new order comes in, determine the fulfillment route:

```
1. Is the shipping address in Mexico/Latin America?
   → Route to mexico-fulfillment (fulfillment-mexico skill)

2. Is this an FBA-eligible order from Amazon?
   → Already fulfilled by Amazon FBA

3. Is any item in the order Nepal-pipeline only (not in Asheville stock)?
   → Flag for Nepal fulfillment coordination (fulfillment-nepal skill)
   → If mix of in-stock + Nepal items, consider split shipment

4. All other US orders → warehouse-manager (this skill)
```

## Daily Pick/Pack List Generation

Run daily at 6 AM ET. Query `orders` table for:
- Status: `unfulfilled` or `partially_fulfilled`
- Fulfillment route: `domestic`
- Ordered before midnight previous day

Generate a pick list sorted by:
1. Priority orders first (expedited shipping, VIP customers)
2. Single-item orders (fastest to pack)
3. Multi-item orders (grouped by location in warehouse)

### Pick List Format

For each order, include:
- Order number and customer name
- Items with SKU, quantity, and bin location
- Shipping method selected by customer
- Any special instructions (gift wrapping, notes)
- Recommended carrier and service level

## Carrier Selection Rules

Read `skills/operations/fulfillment-domestic/carrier-rules.md` for the full decision matrix. Summary:

| Criteria | Carrier | Service |
|----------|---------|---------|
| Light items (<1 lb), standard shipping | USPS | First Class |
| Medium items (1-5 lb), standard shipping | USPS | Priority Mail |
| Heavy/bulky items (>5 lb) | UPS Ground or DHL | Ground |
| Expedited shipping selected | USPS Priority Express or UPS 2-Day | Express |
| Fragile items (singing bowls, statues) | UPS | Ground (better handling) |
| International (non-domestic) | DHL eCommerce or USPS Priority Int'l | Varies |

**Cost optimization**: Always compare rates via Shippo before selecting. The rules above are defaults — if Shippo shows a cheaper option that meets the delivery window, use it.

## Shipping Label Generation

Via Shippo API:
1. Create shipment with sender (Asheville warehouse) and recipient addresses
2. Get rates from all configured carriers
3. Select optimal rate per carrier rules
4. Purchase label
5. Update order in Shopify with tracking number
6. Update `orders` table in Supabase with fulfillment status

## Exception Handling

### Address Validation Failures
- Shippo validates addresses automatically
- If validation fails: flag for warehouse-manager to review, do not auto-ship
- Common issues: apartment number missing, PO Box for UPS shipment

### Backorder Items
- If `inventory_extended.total_on_hand` = 0 for any line item:
  - Check `nepal_pipeline` for incoming stock with `nepal_eta`
  - If ETA < 14 days: hold order, notify customer of delay
  - If ETA > 14 days or no pipeline: escalate to operations-manager for sourcing decision

### Oversized/Fragile Items
- Singing bowls >10 inches: require custom boxing, flag for warehouse-manager
- Statues >$200: double-box, add insurance
- Thangkas: ship in tube, never fold

## Phase 1 Behavior

In Phase 1, this skill generates the pick list and shipping recommendations but does NOT:
- Purchase shipping labels automatically
- Mark orders as fulfilled
- Send tracking notifications to customers

All actions require warehouse-manager's confirmation via the dashboard. The skill presents a "ready to ship" queue each morning.

## Output

```json
{
  "date": "2026-03-21",
  "pick_list": [
    {
      "order_number": "#1042",
      "customer": "Jane Smith",
      "items": [{"sku": "TS-INC-NADO-HAPPINESS", "qty": 2, "bin": "A3"}],
      "shipping_method": "standard",
      "recommended_carrier": "USPS Priority Mail",
      "estimated_cost": 8.45,
      "special_notes": null
    }
  ],
  "exceptions": [],
  "total_orders": 12,
  "estimated_ship_cost": 98.40
}
```
