---
name: fulfillment-mexico
description: Route Latin American orders to mexico-fulfillment at Espiritu Tibetano for fulfillment. Use this skill when a new order has a shipping address in Mexico, Central America, or South America, or when generating the mexico-fulfillment queue. Simpler than domestic fulfillment — mexico-fulfillment handles local shipping. Communication is via email only.
version: "0.1.0"
category: operations
tags: [fulfillment, mexico, international]
author: operations-team
model: sonnet
cacheable: true
estimated_tokens: 1350
phase: 1
depends_on: [shared/brand-guidelines, shared/channel-config]
external_apis: [supabase]
cost_budget_usd: 0.15
---

# Mexico / Latin America Fulfillment Skill

## Purpose

Route orders destined for Latin America through the mexico-fulfillment Espiritu Tibetano operation in Mexico. The mexico-fulfillment partner maintains a small inventory of bestsellers and handles local fulfillment, which avoids expensive international shipping from Asheville and speeds delivery to LATAM customers.

This is a simpler workflow than domestic fulfillment:
1. **Detect** LATAM orders from shipping address
2. **Check** if mexico-fulfillment has the items in stock
3. **Email mexico-fulfillment** with order details and shipping instructions
4. **Track** fulfillment and relay tracking to the customer

## Order Routing Logic

```
1. Is the shipping address in a LATAM country?
   -> Check country code against LATAM list (see below)
   -> Yes: Continue with this skill
   -> No: Route to fulfillment-domestic or other skill

2. Does mexico-fulfillment have the ordered items in stock?
   -> Query mexico-fulfillment's inventory allocation (see SQL below)
   -> Yes: Route to mexico-fulfillment for fulfillment
   -> No: Can we ship from Asheville internationally?
      -> If item value > $50 and customer paid international shipping: ship from Asheville
      -> Otherwise: notify customer of delay, coordinate restock with mexico-fulfillment

3. Is this a new product mexico-fulfillment doesn't carry?
   -> Flag for ceo to decide whether to add to mexico-fulfillment's assortment
```

### LATAM Country Codes

Route to mexico-fulfillment for these shipping destinations:
- **Mexico**: MX
- **Central America**: GT, BZ, SV, HN, NI, CR, PA
- **South America**: CO, VE, EC, PE, BO, CL, AR, UY, PY, BR

**Note**: Brazil (BR) may have additional import complexity. Flag BR orders for ceo review until process is established.

## Data Queries

### Detect LATAM orders pending fulfillment

```sql
SELECT
    o.id,
    o.order_number,
    o.email,
    o.total_price,
    o.shipping_address_country,
    o.shipping_address_city,
    o.fulfillment_status,
    o.line_items
FROM orders o
WHERE o.fulfillment_status = 'unfulfilled'
  AND o.shipping_address_country IN ('MX','GT','BZ','SV','HN','NI','CR','PA',
                                      'CO','VE','EC','PE','BO','CL','AR','UY','PY','BR')
  AND o.fulfillment_route IS NULL
ORDER BY o.created_at ASC;
```

### Check mexico-fulfillment's current inventory

The mexico-fulfillment stock is tracked as a location allocation. Query products on hand:

```sql
SELECT
    ie.sku,
    p.title,
    ie.mexico_on_hand,
    ie.total_on_hand
FROM inventory_extended ie
JOIN products p ON p.id = ie.product_id
WHERE p.status = 'active'
  AND ie.mexico_on_hand > 0
ORDER BY p.title;
```

### Mark order as routed to Mexico

```sql
UPDATE orders
SET fulfillment_route = 'mexico',
    fulfillment_notes = $1
WHERE id = $2;
```

## Email to mexico-fulfillment

All communication with mexico-fulfillment is via email to omar@espiritutibetano.mx. The mexico-fulfillment partner reads English and Spanish. Keep emails clear, structured, and actionable.

### Order Fulfillment Email Template

```
Subject: Tibetan Spirit Order #{order_number} — Ship to {city}, {country}

Hi,

We have a new order for Latin America fulfillment:

ORDER #{order_number}
Customer: {customer_name}
Ship to:
  {address_line_1}
  {address_line_2}
  {city}, {state} {zip}
  {country}

ITEMS:
| SKU | Product | Qty |
|-----|---------|-----|
| {sku} | {title} | {qty} |

Shipping method: {standard / express as selected by customer}
Order total: ${total_price} USD

Please confirm when shipped and provide tracking number.

Thanks,
Tibetan Spirit Operations
```

### Restock Request Email Template

```
Subject: Inventory Restock — Espiritu Tibetano

Hi,

We'd like to replenish the following items at your location:

| SKU | Product | Qty to Send | Current Stock |
|-----|---------|-------------|---------------|
| {sku} | {title} | {restock_qty} | {current_mexico_on_hand} |

We'll ship from Asheville via {carrier}. Expected arrival: {eta}.

Please confirm you can receive this shipment.

Thanks,
Tibetan Spirit Operations
```

## Model Routing

- **Order routing detection**: Haiku 4.5 -- address parsing and country matching is simple classification
- **Email drafting to mexico-fulfillment**: Haiku 4.5 -- templated emails with data fill, low complexity
- **Stock-out decisions** (ship from Asheville vs. wait): Sonnet 4.6 -- requires judgment on cost/customer impact

## Phase 1 Behavior

In Phase 1, this skill:
- Detects LATAM orders and drafts the email to mexico-fulfillment
- Queues the email for review (does NOT auto-send)
- ceo or operations-manager approves before email is sent to mexico-fulfillment
- Tracking updates from mexico-fulfillment are manually entered

Graduation criteria: after 50+ orders fulfilled through mexico-fulfillment with <5% issue rate, move to Phase 2 (auto-send emails, auto-update tracking).

## Escalation Paths

| Situation | Route To | Method | SLA |
|-----------|----------|--------|-----|
| Standard LATAM order | mexico-fulfillment | Email | 24 hours |
| mexico-fulfillment out of stock on ordered item | ceo | Dashboard | 24 hours |
| Brazil order (import complexity) | ceo | Dashboard | 48 hours |
| mexico-fulfillment hasn't confirmed shipment in 48 hours | ceo | Dashboard | 24 hours |
| Customer complaint about LATAM delivery | ceo | Dashboard | 24 hours |
| Restock shipment to mexico-fulfillment needed | ceo (approval) -> warehouse-manager (ship) | Dashboard | 1 week |

Read `skills/shared/escalation-matrix/SKILL.md` for the full escalation reference.

## Output Format

```json
{
  "order_number": "#2048",
  "fulfillment_route": "mexico",
  "destination_country": "MX",
  "destination_city": "Mexico City",
  "items": [
    {
      "sku": "TS-INC-NADO-HAPPINESS",
      "title": "Nado Poizokhang Happiness Incense",
      "quantity": 3,
      "mexico_has_stock": true
    }
  ],
  "mexico_email_draft": "...",
  "stock_sufficient": true,
  "escalation_target": "mexico-fulfillment | ceo | null",
  "phase": 1,
  "requires_approval": true,
  "confidence": 0.92
}
```

## Dependencies

- Read `skills/shared/supabase-ops-db/SKILL.md` for database schema
- Read `skills/shared/channel-config/SKILL.md` for shipping zone definitions
- Read `skills/shared/escalation-matrix/SKILL.md` for routing decisions
- Coordinates with `skills/operations/fulfillment-domestic/SKILL.md` when shipping from Asheville internationally
