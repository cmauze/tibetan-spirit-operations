---
name: cross-channel-parity
description: Monitor and enforce product listing consistency across Shopify (D2C), Etsy, and Amazon FBA channels. Detect drift in pricing, descriptions, inventory, and images. Produce daily parity reports and route corrections through appropriate approval workflows. Phase 1 — all corrections require human approval.
version: "0.1.0"
category: ecommerce
tags: [channels, consistency, parity]
author: operations-team
model: sonnet
cacheable: true
estimated_tokens: 1600
phase: 1
depends_on: [shared/brand-guidelines, shared/channel-config, shared/product-knowledge]
external_apis: [supabase, shopify]
cost_budget_usd: 0.15
---

# Cross-Channel Parity

## Purpose

Ensure that customers see consistent, accurate product information regardless of which channel they shop on. Detect and resolve drift between channels before it causes customer confusion, margin erosion, or overselling.

Shopify is the source of truth. Etsy and Amazon listings should reflect Shopify data, adjusted for channel-specific optimization (titles, tags, fee-adjusted pricing) but consistent on core product facts (description accuracy, inventory availability, images).

## What Parity Means (and Does Not Mean)

**Parity IS:**
- Same product facts (materials, dimensions, origin, practice context) across all channels
- Inventory availability reflects actual stock (no overselling, no phantom stock)
- Pricing follows the channel-specific markup rules defined in `agents/shared/channel-config/SKILL.md`
- Images are current and consistent across channels

**Parity is NOT:**
- Identical titles (Etsy titles are SEO-optimized differently from Shopify)
- Identical descriptions (each channel has platform-specific formatting and emphasis)
- Identical prices (channels have different fee structures requiring different markups)

## Daily Scan Process

The cross-channel parity check runs as a daily cron job. The scan follows this sequence:

### Step 1: Build Product Map

```
For each active product in Shopify:
    Query Supabase products table for:
        - shopify_product_id
        - etsy_listing_id (if listed on Etsy)
        - amazon_asin (if listed on Amazon)
        - current Shopify price
        - current inventory (from inventory_extended)
    Build cross-reference map: {SKU -> {shopify, etsy, amazon}}
```

### Step 2: Check Each Parity Dimension

For each product with listings on 2+ channels, check:

#### Price Parity
```
Expected Etsy price = Shopify price * etsy_markup_factor (from channel-config)
Expected Amazon price = Shopify price * amazon_markup_factor (from channel-config)

IF actual_etsy_price differs from expected by >5%:
    FLAG as price_drift
    severity = "warning" if <10%, "critical" if >=10%

IF actual_amazon_price differs from expected by >5%:
    FLAG as price_drift
    severity = "warning" if <10%, "critical" if >=10%
```

#### Inventory Parity
```
available_to_sell = total_on_hand - fba_allocated - in_transit_reserved - safety_stock

IF etsy_listed_quantity > available_to_sell:
    FLAG as oversell_risk, severity = "critical"
IF amazon_listed_quantity > (available_to_sell - etsy_reserved):
    FLAG as oversell_risk, severity = "critical"
IF any channel shows "in stock" but available_to_sell = 0:
    FLAG as phantom_stock, severity = "critical"
IF any channel shows "out of stock" but available_to_sell > 0:
    FLAG as missed_sales, severity = "warning"
```

#### Description Parity
```
For each product, extract core facts from Shopify description:
    - Material
    - Dimensions/size
    - Origin/sourcing
    - What's included (mallet, cushion, etc.)

Compare against Etsy and Amazon descriptions:
IF core fact is missing from a channel listing:
    FLAG as content_drift, severity = "warning"
IF core fact contradicts between channels (e.g., different dimensions):
    FLAG as content_conflict, severity = "critical"
```

#### Image Parity
```
IF Shopify primary image updated more recently than Etsy/Amazon:
    FLAG as image_stale, severity = "low"
IF Etsy listing has fewer than 5 images:
    FLAG as insufficient_photos, severity = "warning"
```

## Decision Tree: Auto-Fix vs. Escalate

```
1. Is the drift in INVENTORY?
   → Inventory sync failures are time-sensitive (overselling risk)
   → Phase 1: FLAG as critical, draft correction, queue for human approval
   → Phase 2 (graduated): Auto-fix inventory sync within 15 minutes
   → ALWAYS log the correction in skill_invocations

2. Is the drift in PRICING?
   → Price drift <5%: Log only, include in daily report
   → Price drift 5-10%: WARNING — draft correction, queue for ceo approval
   → Price drift >10%: CRITICAL — draft correction, queue for ceo approval with alert
   → NEVER auto-correct pricing, even in Phase 2

3. Is the drift in DESCRIPTIONS?
   → Missing core fact: Draft updated description, queue for approval
   → Contradicting facts: CRITICAL — flag for immediate review
   → Style/formatting differences: ACCEPTABLE (channels have different content needs)
   → NEVER auto-correct descriptions in Phase 1

4. Is the drift in IMAGES?
   → Stale images: Low priority — include in weekly report
   → Missing images: Warning — flag for content team
```

## Output Format

### Daily Parity Report

```json
{
  "report_date": "YYYY-MM-DD",
  "scan_summary": {
    "products_scanned": 0,
    "products_with_multi_channel": 0,
    "products_in_parity": 0,
    "products_with_drift": 0
  },
  "drift_items": [
    {
      "sku": "TS-BOWL-HH-7IN",
      "product_name": "Hand-Hammered Singing Bowl 7 inch",
      "channels_affected": ["shopify", "etsy"],
      "drift_type": "price_drift | inventory_drift | content_drift | image_stale",
      "severity": "critical | warning | low",
      "details": {
        "dimension": "price",
        "shopify_value": "149.00",
        "etsy_value": "149.00",
        "expected_etsy_value": "166.88",
        "drift_pct": 12.0
      },
      "recommended_action": "Update Etsy price to $166.88 (12% markup per channel-config)",
      "auto_fixable": false,
      "requires_approval_from": "ceo"
    }
  ],
  "corrections_applied": [],
  "corrections_pending_approval": []
}
```

### Correction Request (queued for approval)

```json
{
  "correction_id": "parity-YYYYMMDD-001",
  "sku": "TS-BOWL-HH-7IN",
  "channel": "etsy",
  "field": "price",
  "current_value": "149.00",
  "proposed_value": "166.88",
  "rationale": "Etsy price should be Shopify base ($149) * 1.12 markup = $166.88 per channel pricing rules",
  "severity": "critical",
  "requires_approval": true,
  "approval_target": "ceo"
}
```

## Phase 1 Behavior

All corrections require human approval before execution:

- **Inventory corrections**: Queue for operations-manager's review (operational). If oversell risk is imminent, also alert ceo.
- **Price corrections**: Queue for ceo's review via dashboard approval queue.
- **Description corrections**: Queue for ceo's review. Show current vs. proposed text.
- **Image updates**: Queue for ceo's review. Low priority — included in weekly report, not daily alerts.

**Escalation thresholds** (trigger immediate alerts, not just daily report):
- Any oversell risk (inventory on channel > available stock)
- Price drift > 10% on any active listing
- Contradicting product facts between channels

## Phase 2 Graduation Criteria

After demonstrating reliable performance (target: 90+ days, 200+ corrections, <2% error rate):

- **Auto-fix**: Inventory sync corrections (within 15 minutes of detection)
- **Remains human-approved**: All pricing changes, all description changes, all image changes
- **Auto-demote to Phase 1**: If any auto-correction is reverted by a human, or if error rate exceeds 2% in a 30-day window

## Model Routing

- **Daily scan and data comparison**: Haiku 4.5 (structured data comparison, pattern matching)
- **Description diff analysis**: Sonnet 4.6 (needs judgment about whether differences are acceptable channel optimization vs. actual drift)
- **Correction drafting and report generation**: Sonnet 4.6 (needs to write clear rationale and proposed corrections)

## Dependencies

- **References**: `agents/shared/channel-config/SKILL.md` (fee structures, markup rules, SKU conventions), `agents/shared/product-knowledge/SKILL.md` (product facts for validation), `agents/shared/escalation-matrix/SKILL.md` (approval routing)
- **Data sources**: Supabase `products` table, `inventory_extended` table, Shopify API, Etsy API, Amazon SP-API
- **Referenced by**: `agents/ecommerce/skills/etsy-content-optimization/SKILL.md`, operations agents (inventory sync)
