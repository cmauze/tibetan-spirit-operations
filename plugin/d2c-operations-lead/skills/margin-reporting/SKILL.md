---
name: margin-reporting
description: Use when the weekly margin report is due, an ad-hoc margin review is requested, or below-floor alerts need investigation.
---

# Margin Reporting

## Overview

Generates weekly and ad-hoc margin reports with SKU-level profitability, channel comparisons, trend indicators, and below-floor alerts. Read-only — never modifies financial records.

## When to Use

- **Invoke when:** weekly P&L is due, `general-manager` requests a margin review, a below-floor alert needs investigation, or channel profitability needs comparison
- **Do NOT use for:** modifying COGS records, updating pricing, or any write operation on financial data

## Workflow

1. **Query SKU margins** — run SKU-level margin query; label COGS confidence on every row (confirmed vs. estimated)
2. **Query channel rollup** — run channel profitability query; compute trend arrows per channel (▲ ≥+2pp, ▼ ≥−2pp, ─ <2pp)
3. **Run category rollup** — aggregate SKU margins by category; flag any category average below floor
4. **Identify below-floor alerts** — flag all SKUs where `margin < channel_floor`; mark negative-margin rows as URGENT
5. **Check charitable/mission allocations** — if the brand has a charitable allocation (e.g., % of revenue to a cause), confirm it appears as an accounting expense, not a marketing line
6. **Assemble report sections** — Executive Summary → By Category → By Channel → Below-Floor Alerts → Action Items (see `references/queries.md` for full template)
7. **Write output** — save to the finance reports file; log run with `"ai_generated": true`

See `references/queries.md` for SQL query patterns and the full report template.

## Common Rationalizations

| Rationalization | Reality |
|----------------|---------|
| "COGS is probably close enough to skip the label" | Every estimate must be labeled. Unlabeled numbers imply confirmed data. |
| "The variance is small, I'll smooth it over" | Surface all anomalies. A $50 gap today can be $5,000 next quarter. |
| "The charitable allocation lowers apparent margin, I'll exclude it" | It is a real expense. Include it with its accounting label — never omit. |
| "This channel is below floor but volume is tiny" | Floor violations are flagged regardless of volume. `general-manager` decides what to do. |

## Red Flags

- Any COGS row presented without a confidence label (confirmed / estimated)
- Negative-margin SKU not marked URGENT
- Charitable allocation appearing in a marketing or promotion line
- Log entry missing `"ai_generated": true`
- Financial data modified (this skill is read-only)

## Verification

- [ ] All COGS rows labeled: confirmed or estimated
- [ ] Trend arrows applied to all channel rows (▲ / ▼ / ─)
- [ ] Every SKU with margin < channel floor appears in Below-Floor Alerts
- [ ] Negative-margin SKUs marked URGENT
- [ ] Charitable/mission allocation is an accounting expense line, not marketing
- [ ] Run logged with `"ai_generated": true`
- [ ] No financial records modified
