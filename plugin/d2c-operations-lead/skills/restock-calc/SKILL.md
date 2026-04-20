---
name: restock-calc
description: Use when inventory levels need threshold calculation, restock quantities need computing, or demand-based reorder recommendations are needed.
model: sonnet
review: opus
---

# Restock Calculator

## Overview

Computes reorder points, restock quantities, and safety stock for each SKU using velocity data, lead times, and seasonal demand signals. Produces recommendations only — never makes purchase commitments.

## When to Use

**Invoke when:**
- Calculating whether a SKU has crossed its reorder point
- Computing a recommended order quantity for domestic or international-sourced items
- Determining safety stock for a SKU ahead of a seasonal event
- Validating that an existing recommendation used the correct lead-time tier

**Do NOT use for:**
- Generating the full inventory report (use inventory analyst agent)
- Modifying inventory records or placing orders
- Reconciling Shopify vs. warehouse counts (inventory analyst owns that)

## Workflow

1. **Identify data source** — Query inventory table via database; fall back to local snapshot file. Label every figure: confirmed or estimated.
2. **Calculate daily velocity** — 30-day avg daily sales from `orders table`. Adjust for upcoming seasonal events.
3. **Compute reorder point, safety stock, and restock quantity** — Apply formulas from `references/formulas.md`. Flag immediately if a top-20 SKU is below critical alert threshold.
4. **Flag overstock** — Apply overstock threshold from `references/formulas.md`.
5. **Write output** — Append to restock recommendations file with confidence labels and data source.

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "Daily velocity is roughly known, I'll skip the label" | Every figure needs explicit confidence label — confirmed or estimated. |
| "The international lead time is probably shorter this time" | Use conservative lead time estimates. Never assume a faster timeline. |
| "Low-margin SKU, I'll skip the safety stock calc" | If it serves a customer need, compute it regardless of margin. |
| "Marketplace fields aren't in the snapshot, I'll use on-hand only" | Note the missing fields explicitly; do not silently ignore them. |

## Red Flags

- Computing reorder quantity without checking sourcing tier (domestic vs. international)
- Omitting confidence label on any figure
- Using Shopify count when it conflicts with warehouse count
- Implying a purchase commitment in the output
- Skipping safety stock for a SKU because volume is low

## Verification

- [ ] Data source labeled: database (confirmed) or snapshot (estimated)
- [ ] Daily velocity uses 30-day avg from orders table
- [ ] Reorder point = velocity × 14 (velocity × 7 for top-20 SKUs)
- [ ] Safety stock = max(velocity × 6, 2 units)
- [ ] International-sourced items use 90-day quantity with conservative lead time
- [ ] Marketplace-specific fields checked when available
- [ ] Overstock threshold applied: >180 days supply, no active promotion
- [ ] No purchase commitment language in output
