---
name: margin-reporting
description: Generates weekly and ad-hoc margin reports with SKU-level profitability, channel comparison, trend indicators, and below-floor alerts. Use when the weekly P&L is due, an ad-hoc margin review is requested, or below-floor alerts need investigation.
allowed-tools: Read, Write, mcp__plugin_supabase_supabase__execute_sql
---

# Margin Reporting

**Announce at start:** "I'm using the margin-reporting skill to generate the margin report."

## Goal

Query Supabase for SKU-level margin data and channel profitability, compute trend indicators, flag all below-floor SKUs and negative-margin items, and write a structured margin report to `data/finance-reports.json`. Read-only — never modifies financial records.

## Process

1. **Query SKU margins** — Run `product_margin_detail` view via `execute_sql`. Label COGS confidence on every row: `confirmed` or `estimated`. An unlabeled row is a data quality error.
2. **Query channel rollup** — Run `channel_profitability_monthly`. Compute trend arrows per channel: ▲ ≥+2pp, ▼ ≥−2pp, ─ <2pp change.
3. **Run category rollup** — Aggregate SKU margins by category. Flag any category average below floor.
4. **Identify below-floor alerts** — Flag all SKUs where `margin < channel_floor`. Mark negative-margin rows as URGENT. See `references/queries.md` for floor thresholds.
5. **Check Dharma Giving line** — Confirm 5% Forest Hermitage allocation appears as an accounting expense line, not a marketing or promotion line.
6. **Assemble report** — Format per `references/queries.md` template: Executive Summary → By Category → By Channel → Below-Floor Alerts → Action Items.
7. **Write output** — Save to `data/finance-reports.json`. Log observability entry to `data/agent-runs.json` per `_templates/observability.md`.

## Output

- **Primary:** `data/finance-reports.json` — full margin report with trend indicators and below-floor alerts
- **Secondary:** `data/agent-runs.json` — one observability entry per `_templates/observability.md`
- **Terminal:** Executive summary with anomaly count and any URGENT flags

**Verification:** All COGS rows carry a confidence label (confirmed or estimated). Trend arrows applied to all channel rows. Every SKU below floor appears in Below-Floor Alerts. Negative-margin SKUs marked URGENT. Dharma Giving is an accounting expense line. Output written to `data/finance-reports.json`. No financial records modified.

## Common Rationalizations

| Thought | Reality |
|---|---|
| "COGS is probably close enough to skip the label" | Every estimate must be labeled. Unlabeled numbers imply confirmed data. |
| "The variance is small, I'll smooth it over" | Surface all anomalies. A $50 gap today can be $5,000 next quarter. |
| "Dharma Giving lowers apparent margin, I'll exclude it" | It is a real expense. Include it with its accounting label — never omit. |
| "This channel is below floor but volume is tiny" | Floor violations are flagged regardless of volume. `general-manager` decides what to do. |

## Edge Cases

- **Supabase unavailable:** Log `status: "blocked"` to `data/agent-runs.json`. Do not produce a partial report with unlabeled gaps.
- **COGS data not yet confirmed:** Report the section with an explicit `"estimated"` confidence label. Omission hides the gap.
- **Dharma Giving not present in data:** Flag missing line in the report — do not silently omit it.

## Rules

- NEVER report any COGS row without a confidence label.
- NEVER smooth over discrepancies — surface them with the dollar amount.
- NEVER classify Dharma Giving as marketing, promotion, or brand spend.
- NEVER modify financial records — this skill is read-only.

## Environment

- **MCP server:** Supabase (`execute_sql`)
- **Data files:** `data/finance-reports.json`, `data/agent-runs.json`
- **Reference files:** `references/queries.md`, `_templates/observability.md`

## Works Well With

- **Invoked by:** `finance-analyst` agent
