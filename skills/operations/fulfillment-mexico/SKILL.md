---
name: fulfillment-mexico
description: Route Latin American orders to Omar at Espiritu Tibetano for fulfillment. Use this skill when a new order has a shipping address in Mexico, Central America, or South America, or when generating Omar's fulfillment queue. Simpler than domestic fulfillment — Omar handles local shipping. Communication is via email only.
---

# Mexico / Latin America Fulfillment Skill

## Purpose

Route orders destined for Latin America through Omar's Espiritu Tibetano operation in Mexico. Omar maintains a small inventory of bestsellers and handles local fulfillment, which avoids expensive international shipping from Asheville and speeds delivery to LATAM customers.

This is a simpler workflow than domestic fulfillment:
1. **Detect** LATAM orders from shipping address
2. **Check** if Omar has the items in stock
3. **Email Omar** with order details and shipping instructions
4. **Track** fulfillment and relay tracking to the customer

## Order Routing Logic

```
1. Is the shipping address in a LATAM country?
   -> Check country code against LATAM list (see below)
   -> Yes: Continue with this skill
   -> No: Route to fulfillment-domestic or other skill

2. Does Omar have the ordered items in stock?
   -> Query Omar's inventory allocation (see SQL below)
   -> Yes: Route to Omar for fulfillment
   -> No: Can we ship from Asheville internationally?
      -> If item value > $50 and customer paid international shipping: ship from Asheville
      -> Otherwise: notify customer of delay, coordinate restock with Omar

3. Is this a new product Omar doesn't carry?
   -> Flag for Chris to decide whether to add to Omar's assortment
```

### LATAM Country Codes

Route to Omar for these shipping destinations:
- **Mexico**: MX
- **Central America**: GT, BZ, SV, HN, NI, CR, PA
- **South America**: CO, VE, EC, PE, BO, CL, AR, UY, PY, BR

**Note**: Brazil (BR) may have additional import complexity. Flag BR orders for Chris review until process is established.

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

### Check Omar's current inventory

Omar's stock is tracked as a location allocation. Query products he has on hand:

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

## Email to Omar

All communication with Omar is via email to omar@espiritutibetano.mx. Omar reads English and Spanish. Keep emails clear, structured, and actionable.

### Order Fulfillment Email Template

```
Subject: Tibetan Spirit Order #{order_number} — Ship to {city}, {country}

Hi Omar,

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

Hi Omar,

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
- **Email drafting to Omar**: Haiku 4.5 -- templated emails with data fill, low complexity
- **Stock-out decisions** (ship from Asheville vs. wait): Sonnet 4.6 -- requires judgment on cost/customer impact

## Phase 1 Behavior

In Phase 1, this skill:
- Detects LATAM orders and drafts the email to Omar
- Queues the email for review (does NOT auto-send)
- Chris or Jhoti approves before email is sent to Omar
- Tracking updates from Omar are manually entered

Graduation criteria: after 50+ orders fulfilled through Omar with <5% issue rate, move to Phase 2 (auto-send emails, auto-update tracking).

## Escalation Paths

| Situation | Route To | Method | SLA |
|-----------|----------|--------|-----|
| Standard LATAM order | Omar | Email | 24 hours |
| Omar out of stock on ordered item | Chris | Dashboard | 24 hours |
| Brazil order (import complexity) | Chris | Dashboard | 48 hours |
| Omar hasn't confirmed shipment in 48 hours | Chris | Dashboard | 24 hours |
| Customer complaint about LATAM delivery | Chris | Dashboard | 24 hours |
| Restock shipment to Omar needed | Chris (approval) -> Fiona (ship) | Dashboard | 1 week |

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
      "omar_has_stock": true
    }
  ],
  "omar_email_draft": "...",
  "stock_sufficient": true,
  "escalation_target": "omar | chris | null",
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
