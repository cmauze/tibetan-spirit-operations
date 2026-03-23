---
name: channel-config
description: Store URLs, API credentials scope, fee structures, and platform-specific rules for each sales channel (Shopify D2C, Etsy, Amazon FBA, Wholesale). Load this skill whenever a task involves cross-channel operations, pricing calculations, fee estimation, or platform-specific logic.
---

# Tibetan Spirit Channel Configuration

## Active Channels

### Shopify D2C (Primary)
- **Store URL**: tibetan-spirit.myshopify.com
- **Status**: Live, primary revenue channel
- **Plan**: Shopify Advanced ($299/mo)
- **Payment processing**: Shopify Payments (2.5% + $0.30 per transaction)
- **API scopes needed**: `read_orders`, `write_orders`, `read_products`, `write_products`, `read_inventory`, `write_inventory`, `read_fulfillments`, `write_fulfillments`, `read_customers`
- **Webhook topics**: `orders/create`, `orders/updated`, `inventory_levels/update`, `products/update`
- **Fee structure for margin calculations**:
  - Transaction fee: 2.5% + $0.30
  - No additional marketplace commission
  - Shipping labels at negotiated USPS/DHL rates via Shippo

### Etsy
- **Shop name**: TBD (launching Month 5-6)
- **Status**: Pre-launch
- **Sync method**: CedCommerce or LitCommerce (inventory sync from Shopify)
- **Fee structure**:
  - Listing fee: $0.20 per listing (renews every 4 months or on sale)
  - Transaction fee: 6.5% of sale price (including shipping)
  - Payment processing: 3% + $0.25
  - Offsite ads fee: 12-15% on attributed sales (mandatory above $10K/year revenue)
  - **Total effective fee: ~10-12% per sale**
- **Content rules**: Etsy SEO is different from Shopify. Titles up to 140 chars, front-loaded with keywords. 13 tags per listing. Read `skills/ecommerce/etsy-content-optimization/SKILL.md` for details.
- **Important**: Do NOT push Shopify-optimized descriptions to Etsy. Each channel needs native content.

### Amazon FBA
- **Seller Central account**: TBD (launching Month 4)
- **Status**: Pre-launch, FBA setup in progress
- **Fee structure**:
  - Referral fee: 15% (most categories)
  - FBA fulfillment fee: varies by size/weight ($3.22-$10+ per unit)
  - Monthly storage: $0.87/cubic foot (standard), $2.40/cubic foot (Oct-Dec peak)
  - **Total effective fee: 25-40% per sale depending on item**
- **Margin implications**: Amazon's fee stack means only items with >50% gross margin should be listed
- **FBA prep requirements**: Read `skills/operations/amazon-fba-replenishment/fba-prep-checklist.md`

### Wholesale (Espíritu Tibetano + Dharma Centers)
- **Status**: Planning (launches Month 9+)
- **Terms**: Net 30, minimum order $250
- **Pricing**: 40-50% off retail (standard wholesale keystone)
- **Channel**: Omar handles Mexico distribution; US dharma centers via direct outreach

## Cross-Channel Rules

### Price Parity
- Shopify D2C is the reference price
- Etsy prices = Shopify + markup to offset fees (typically 10-15% higher)
- Amazon prices = Shopify + markup to offset FBA fees (typically 15-25% higher)
- Wholesale = 40-50% below Shopify retail
- **Exception**: Channel-exclusive products or bundles may have independent pricing

### Inventory Allocation
Inventory is centralized in Supabase `inventory_extended` table. Available quantity calculation:
```
available_to_sell = total_on_hand - fba_allocated - in_transit_reserved - safety_stock
```
- Safety stock: 20% of 30-day rolling average sales (minimum 2 units)
- FBA allocation: Reserved for next FBA shipment
- Cross-channel oversell prevention: Inventory webhook updates propagate within 15 minutes

### SKU Convention
Format: `TS-{CATEGORY}-{IDENTIFIER}-{VARIANT}`
Examples:
- `TS-INC-NADO-HAPPINESS` (Nado Poizokhang Happiness incense)
- `TS-MALA-BODHI-108` (Bodhi seed mala, 108 beads)
- `TS-BOWL-HH-7IN` (Hand-hammered singing bowl, 7 inch)
