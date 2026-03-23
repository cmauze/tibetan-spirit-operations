---
name: inventory-management
description: Monitor stock levels across all channels, generate reorder alerts, and manage cross-channel inventory allocation. Use this skill when inventory webhooks fire, during daily/weekly inventory audits, when checking if a product can be listed on a new channel, or when planning FBA replenishment quantities. This skill queries the Supabase inventory_extended table as its primary data source.
---

# Inventory Management Skill

## Purpose

Maintain accurate cross-channel inventory, prevent stockouts and overselling, and generate timely reorder recommendations.

## Data Model

All inventory data lives in the Supabase `inventory_extended` table. Key fields:

```
product_id          — FK to products table
sku                 — Product SKU
total_on_hand       — Physical units in Asheville warehouse
shopify_available   — Units available on Shopify (may differ from total_on_hand)
fba_allocated       — Units reserved for next FBA shipment
fba_in_transit      — Units currently shipping to Amazon FCs
nepal_pipeline      — Units ordered from Nepal suppliers, not yet received
nepal_eta           — Expected arrival date for Nepal pipeline
reorder_trigger_qty — When total_on_hand drops below this, trigger reorder
safety_stock        — Minimum units to maintain (20% of 30-day avg sales, min 2)
last_synced         — Timestamp of last Shopify sync
```

## Daily Inventory Check (Cron — 6 AM ET)

Run the `reorder-triggers.py` script or query directly:

```sql
SELECT p.sku, p.title, ie.total_on_hand, ie.reorder_trigger_qty,
       ie.nepal_pipeline, ie.nepal_eta, ie.fba_allocated,
       ie.total_on_hand - ie.fba_allocated - ie.safety_stock AS available_to_sell
FROM inventory_extended ie
JOIN products p ON p.id = ie.product_id
WHERE p.status = 'active'
  AND ie.total_on_hand <= ie.reorder_trigger_qty
ORDER BY (ie.total_on_hand - ie.safety_stock) ASC;
```

## Reorder Logic

When stock drops below `reorder_trigger_qty`:

### Step 1: Check Nepal Pipeline
Is there stock already on the way (`nepal_pipeline > 0` and `nepal_eta` within 30 days)?
- **Yes, sufficient**: Log the alert but note incoming stock. No action needed.
- **Yes, insufficient**: Recommend additional reorder to cover the gap.
- **No**: Recommend new reorder.

### Step 2: Calculate Reorder Quantity
```
reorder_qty = (avg_daily_sales * 90) - total_on_hand - nepal_pipeline + safety_stock
```
90-day cover accounts for Nepal lead times (typically 4-8 weeks from order to delivery).

### Step 3: Generate Reorder Recommendation

Produce a recommendation for Jhoti (in Bahasa Indonesia):

```
Yth. Jhoti,

Stok berikut memerlukan pemesanan ulang:

SKU: TS-INC-NADO-HAPPINESS
Judul: Nado Poizokhang Happiness Incense
Stok saat ini: 5 unit
Rata-rata penjualan harian: 1.2 unit
Hari persediaan tersisa: ~4 hari
Jumlah pemesanan yang disarankan: 100 unit
Pemasok: Dinesh (Kathmandu)

Mungkin bisa disetujui untuk pemesanan ulang?

[Setuju] [Tolak] [Ubah Jumlah]
```

### Step 4: Handle Stockouts

If `total_on_hand = 0` AND `nepal_pipeline = 0`:
1. **Immediately**: Flag as URGENT to Jhoti + Chris
2. **Marketing**: Trigger `inventory-aware-advertising` skill to pause ads for this SKU
3. **Shopify**: Set product to "sold out" (don't unpublish — preserves SEO)
4. **Dashboard**: Add to stockout report

## Cross-Channel Allocation

Available-to-sell calculation per channel:
```
shopify_available = total_on_hand - fba_allocated - fba_in_transit - safety_stock
etsy_available = shopify_available  (synced via CedCommerce)
amazon_available = fba_allocated + fba_in_transit  (separate FBA pool)
```

**Oversell prevention**: When Shopify inventory webhook fires with a decrease, immediately check if the new level falls below the combined committed quantities across channels. If so, reduce availability on secondary channels (Etsy first, then Amazon FBA pauses restocking).

## Weekly Inventory Report (Cron — Monday 8 AM ET)

Generate a summary for Chris and Jhoti:

| Metric | Details |
|--------|---------|
| Total SKUs tracked | Count of active products |
| Stockout items | SKUs with 0 available |
| Low stock items | SKUs below reorder trigger |
| In-transit from Nepal | Items and ETAs |
| FBA allocation status | What's allocated vs. shipped to Amazon |
| Inventory turnover | 30-day rolling by category |
| Dead stock candidates | Items with 0 sales in 60+ days |

## Scripts

- `reorder-triggers.py` — Queries Supabase for low-stock items, generates reorder recommendations
  - Run via cron daily or on inventory webhook
  - Output: JSON array of reorder recommendations

## Phase 1 Behavior

All reorder recommendations require human approval (Jhoti or Chris). The skill generates recommendations and presents them in the approval queue. It does NOT:
- Place orders with suppliers automatically
- Adjust inventory levels directly
- Change product availability on any channel

Graduate to Phase 2 after 200+ correct recommendations with <2% error rate.
