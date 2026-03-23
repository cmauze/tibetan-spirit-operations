---
name: fulfillment-nepal
description: Track inbound shipments from Nepal suppliers through customs clearance into US inventory. Use this skill when a Nepal shipment is dispatched, when customs documentation is needed, when a shipment clears customs, or when landed costs need calculation for integration with cogs-tracking. Manages nepal_pipeline and nepal_eta columns in inventory_extended.
---

# Nepal Fulfillment Skill

## Purpose

Manage the inbound supply chain from Kathmandu Valley workshops to the Asheville warehouse. This skill handles:
1. **Shipment tracking** from Nepal dispatch to Asheville receipt
2. **Customs documentation** including HS code assignment and commercial invoices
3. **Duty estimation** based on product category and declared value
4. **Landed cost calculation** feeding into cogs-tracking for margin accuracy
5. **Inventory pipeline updates** keeping `nepal_pipeline` and `nepal_eta` current

Nepal shipments typically arrive via air freight (7-14 days) or sea freight (45-60 days). The skill must keep pipeline visibility accurate so fulfillment-domestic and inventory-management can plan around incoming stock.

## Shipment Lifecycle

```
1. PO CONFIRMED (supplier-communication confirms order)
   -> Update inventory_extended: nepal_pipeline = ordered_qty, nepal_eta = estimated_date
   -> Log to skill_invocations

2. DISPATCHED (supplier confirms shipment with tracking/AWB)
   -> Update nepal_eta based on actual dispatch date + transit estimate
   -> Record shipping method (air/sea), carrier, tracking number
   -> Generate customs pre-clearance docs if not already done

3. IN TRANSIT
   -> Monitor carrier tracking for milestone updates
   -> If nepal_eta passes without delivery -> trigger shipment inquiry via supplier-communication
   -> Alert Jhoti if delay >3 days beyond nepal_eta

4. CUSTOMS CLEARANCE
   -> Verify commercial invoice matches PO
   -> Confirm HS codes are assigned for all line items
   -> Calculate estimated duty based on declared value + duty_rate
   -> If customs holds shipment -> escalate to Jhoti + Chris

5. DELIVERED TO ASHEVILLE
   -> Fiona confirms receipt and condition
   -> Update inventory_extended: nepal_pipeline = 0, total_on_hand += received_qty
   -> Calculate actual landed cost per unit
   -> Push landed cost to cogs-tracking skill
   -> Log receipt in skill_invocations
```

## HS Code Reference

Key HS codes for Tibetan Spirit product categories. Store in `products.duty_hs_code`:

| Category | HS Code | Description | Typical Duty Rate |
|----------|---------|-------------|-------------------|
| Incense | 3307.41 | Agarbatti and other odoriferous preparations | 0-2% |
| Prayer Flags | 6307.90 | Other made-up textile articles | 5-12% |
| Singing Bowls | 8306.29 | Bells, gongs — base metal | 2-5% |
| Statues (handmade) | 9703.00 | Original sculptures and statuary | 0% (duty-free as art) |
| Thangkas (hand-painted) | 9701.10 | Paintings, drawings — hand-executed | 0% (duty-free as art) |
| Thangkas (prints) | 4911.91 | Printed pictures, designs | 0-2% |
| Malas (wood/seed) | 9601.90 | Worked vegetable carving material | 2-5% |
| Malas (gemstone) | 7116.20 | Articles of precious/semi-precious stones | 2-6.5% |
| Offering Sets (metal) | 8306.29 | Bells, gongs, and similar — base metal | 2-5% |
| Dorje/Ghanta | 8306.29 | Bells, gongs, and similar — base metal | 2-5% |

**Important**: Handmade art (thangkas, statues) often qualifies for duty-free entry under HS 97xx. Jhoti should obtain certificates of authenticity from the workshop to support this classification. When in doubt, use the higher-duty classification and flag for review.

## Data Queries

### Current Nepal pipeline inventory

```sql
SELECT
    ie.sku,
    p.title,
    ie.nepal_pipeline,
    ie.nepal_eta,
    ie.total_on_hand,
    ie.reorder_trigger_qty,
    p.duty_hs_code,
    p.duty_rate,
    p.cogs_confirmed,
    p.freight_per_unit
FROM inventory_extended ie
JOIN products p ON p.id = ie.product_id
WHERE p.status = 'active'
  AND ie.nepal_pipeline > 0
ORDER BY ie.nepal_eta ASC;
```

### Overdue shipments (past ETA)

```sql
SELECT
    ie.sku,
    p.title,
    ie.nepal_pipeline,
    ie.nepal_eta,
    CURRENT_DATE - ie.nepal_eta AS days_overdue
FROM inventory_extended ie
JOIN products p ON p.id = ie.product_id
WHERE ie.nepal_pipeline > 0
  AND ie.nepal_eta < CURRENT_DATE
ORDER BY days_overdue DESC;
```

### Update pipeline on dispatch

```sql
UPDATE inventory_extended
SET nepal_pipeline = $1,
    nepal_eta = $2
WHERE sku = $3;
```

### Record receipt (delivered to Asheville)

```sql
UPDATE inventory_extended
SET total_on_hand = total_on_hand + $1,
    nepal_pipeline = GREATEST(nepal_pipeline - $1, 0),
    nepal_eta = NULL
WHERE sku = $2;
```

## Landed Cost Calculation

When a shipment is received, calculate the actual landed cost per unit:

```
landed_cost_per_unit =
    (purchase_price_npr / exchange_rate_at_payment)   -- purchase price in USD
  + (total_freight_cost / total_units_in_shipment)    -- freight allocation
  + (declared_value_usd * duty_rate)                  -- duty per unit
  + processing_per_unit                               -- customs broker, handling
```

Push this to cogs-tracking by updating:
- `products.cogs_confirmed` = landed_cost_per_unit
- `products.freight_per_unit` = freight allocation
- `products.cogs_confidence` = 'confirmed'

## Transit Time Estimates

Used when calculating `nepal_eta` from dispatch date:

| Method | Transit | Cost/kg | Use When |
|--------|---------|---------|----------|
| Air freight (express) | 5-7 days | $12-18/kg | Stockout risk, high-value items |
| Air freight (standard) | 10-14 days | $8-12/kg | Normal reorders |
| Sea freight | 45-60 days | $2-5/kg | Large bulk orders, no urgency |

Add 3-5 business days for US customs clearance on top of transit time.

## Model Routing

- **Pipeline status checks**: Haiku 4.5 -- simple data lookups, no analysis needed
- **Customs document preparation**: Sonnet 4.6 -- requires accurate HS classification and compliance knowledge
- **Landed cost calculation**: Haiku 4.5 -- deterministic math, run via Python script
- **Delay assessment and escalation**: Sonnet 4.6 -- judgment needed on severity and stakeholder communication

## Phase 1 Behavior

In Phase 1, this skill provides visibility and recommendations but does NOT:
- Automatically update inventory on receipt (Fiona confirms first)
- File customs entries without Jhoti review
- Change HS codes without Chris approval (tariff classification has legal implications)

All inventory updates require human confirmation:
- Fiona confirms physical receipt and condition
- Jhoti reviews customs documents before filing
- Chris approves any HS code changes or duty disputes

## Escalation Paths

| Situation | Route To | Method | SLA |
|-----------|----------|--------|-----|
| Shipment dispatched (routine update) | Jhoti | WhatsApp (Bahasa Indonesia) | Informational |
| Shipment 1-3 days overdue | Jhoti | WhatsApp (Bahasa Indonesia) | 24 hours |
| Shipment >7 days overdue | Jhoti + Chris | WhatsApp + Dashboard | 12 hours |
| Customs hold or inspection | Jhoti + Chris | WhatsApp + Dashboard | 12 hours |
| Customs duty dispute | Chris | Dashboard + email alert | 24 hours |
| Goods received with damage | Jhoti + Fiona | WhatsApp + Dashboard | Same day |
| Goods received, quantity mismatch | Jhoti | WhatsApp (Bahasa Indonesia) | 24 hours |

Read `skills/shared/escalation-matrix/SKILL.md` for the full escalation reference.

## Output Format

```json
{
  "shipment_id": "NS-2026-014",
  "status": "PO_CONFIRMED | DISPATCHED | IN_TRANSIT | CUSTOMS | DELIVERED | OVERDUE",
  "supplier_name": "Patan Metalworks",
  "shipping_method": "air_standard",
  "carrier": "Nepal Airlines Cargo",
  "tracking_number": "NA-784521",
  "items": [
    {
      "sku": "TS-BOWL-HH-7IN",
      "quantity_shipped": 20,
      "declared_value_usd": 675.00,
      "hs_code": "8306.29",
      "estimated_duty_rate": 0.03,
      "estimated_duty_usd": 20.25
    }
  ],
  "nepal_eta": "2026-04-05",
  "days_overdue": 0,
  "landed_cost_estimate": {
    "purchase_usd": 675.00,
    "freight_usd": 120.00,
    "duty_usd": 20.25,
    "processing_usd": 45.00,
    "total_usd": 860.25,
    "per_unit_usd": 43.01
  },
  "escalation_target": "jhoti | chris_and_jhoti | fiona | null",
  "phase": 1,
  "requires_approval": true,
  "confidence": 0.85
}
```

## Dependencies

- Read `skills/shared/supabase-ops-db/SKILL.md` for database schema
- Read `skills/shared/product-knowledge/SKILL.md` for product categories and HS mapping
- Coordinates with `skills/operations/supplier-communication/SKILL.md` for PO and inquiry drafting
- Feeds landed cost data to `skills/finance/cogs-tracking/SKILL.md`
- Read `skills/shared/escalation-matrix/SKILL.md` for routing decisions
