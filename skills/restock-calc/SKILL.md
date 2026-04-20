---
name: restock-calc
description: Computes reorder points, restock quantities, and safety stock for each SKU using velocity data, lead times, and seasonal demand signals. Use when calculating reorder points, computing recommended order quantities, or determining safety stock before a Buddhist calendar event.
allowed-tools: Read, Write, mcp__plugin_supabase_supabase__execute_sql
model: sonnet
review: opus
---

# Restock Calculator

**Announce at start:** "I'm using the restock-calc skill to compute restock recommendations."

## Goal

Calculate reorder points, restock quantities, and safety stock for each SKU using 30-day velocity data, lead-time tier (domestic vs. Nepal-sourced), and seasonal demand adjustments. Produce recommendations only — never implies purchase commitments or modifies inventory records.

## Process

1. **Identify data source** — Query `ts_inventory` via Supabase `execute_sql`. Fall back to `data/inventory-snapshot.json` if Supabase is unavailable. Label every figure explicitly: `confirmed` (Supabase) or `estimated` (snapshot).
2. **Calculate daily velocity** — Pull 30-day average daily sales from `ts_orders`. Adjust for upcoming Buddhist calendar events (Losar, Saga Dawa, Vesak, Q4) using seasonal multipliers from `references/formulas.md`.
3. **Compute reorder point, safety stock, and restock quantity** — Apply formulas from `references/formulas.md`. For Nepal-sourced items, always use 8–12 week lead time (conservative). Flag immediately if any top-20 SKU is below critical alert threshold (7 days supply).
4. **Flag overstock** — Apply overstock threshold: >180 days supply with no active promotion. Write overstock flags to the output alongside restock recommendations.
5. **Write output** — Append to `data/restock-recommendations.json` with confidence labels and data source noted for each row. Log observability entry to `data/agent-runs.json` per `_templates/observability.md`.

## Output

- **Primary:** `data/restock-recommendations.json` — per-SKU recommendations with confidence labels
- **Secondary:** `data/agent-runs.json` — one observability entry per `_templates/observability.md`
- **Terminal:** Critical alerts first, then restock summary, then overstock flags

**Verification:** Data source labeled (Supabase confirmed or snapshot estimated) on every row. Daily velocity uses 30-day avg from `ts_orders`. Nepal-sourced items use 90-day quantity and 8–12 week lead time. `fba_allocated`, `fba_in_transit`, `nepal_pipeline`, `nepal_eta` checked. Overstock threshold applied. Output written to `data/restock-recommendations.json`. No purchase commitment language present.

## Common Rationalizations

| Thought | Reality |
|---|---|
| "Daily velocity is roughly known, I'll skip the label" | Every figure needs an explicit confidence label. Unlabeled numbers imply confirmed data. |
| "The Nepal lead time is probably shorter this time" | Use 8–12 weeks conservative. Never assume a faster timeline without confirmed supplier data. |
| "Low-margin SKU, I'll skip the safety stock calc" | If it serves a practitioner need, compute it regardless of margin. |
| "FBA fields aren't in the snapshot, I'll use on-hand only" | Note missing fields explicitly — do not silently ignore them. |

## Edge Cases

- **Missing FBA fields in snapshot:** Note in the output row with `"fba_data": "unavailable"`. Do not silently compute without them.
- **Top-20 SKU below critical threshold:** Flag as URGENT immediately in terminal output and in `data/restock-recommendations.json`.
- **Seasonal event approaching within 30 days:** Apply demand multiplier and note the event name in the recommendation row.

## Rules

- NEVER compute reorder quantity without checking sourcing tier (domestic vs. Nepal).
- NEVER omit confidence label on any figure.
- NEVER use Shopify count when it conflicts with warehouse physical count.
- NEVER imply a purchase commitment in the output — recommendations only.

## Environment

- **MCP server:** Supabase (`execute_sql`)
- **Data files:** `data/restock-recommendations.json`, `data/inventory-snapshot.json`, `data/agent-runs.json`
- **Reference files:** `references/formulas.md`, `_templates/observability.md`

## Works Well With

- **Invoked by:** `inventory-analyst` agent
- **Preceded by:** `shopify-query` (for real-time stock check when counts conflict)
