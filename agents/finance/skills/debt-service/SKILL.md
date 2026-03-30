---
name: debt-service
description: Track and manage all debt obligations — the investor ops loan, spiritual-director payout schedule, and quarterly inventory loan reconciliation. Use this skill on the monthly cron (1st of month), when ceo requests a debt status check, or when cash-flow planning needs current debt balances. Generates payment schedules, tracks balances, and alerts on upcoming obligations.
version: "0.1.0"
category: finance
tags: [debt, payments, obligations]
author: operations-team
model: sonnet
cacheable: true
estimated_tokens: 1500
phase: 1
depends_on: [shared/brand-guidelines, shared/supabase-ops-db]
external_apis: [supabase]
cost_budget_usd: 0.15
---

# Debt Service Skill

## Purpose

Tibetan Spirit has three distinct debt instruments with different structures. This skill tracks all of them in one place so the ceo always knows exactly what's owed, what's due next, and how debt service impacts cash flow.

### The Three Obligations

| Instrument | Principal | Rate | Repayment Structure | Start |
|------------|-----------|------|---------------------|-------|
| **Ops Loan** | $250,000 | 0% interest-free | $3,000/mo starting 202707, flexible | 202604 |
| **Spiritual-Director Payout** | $270,000 | 0% interest-free | $3,000/mo (Y1-5), $1,500/mo (Y6-10) | 202604 |
| **Inventory Loan** | Variable (draws) | 0% interest-free | Quarterly reconciliation — repay cost basis of items sold | 202604 |

**Why this matters**: All three are interest-free, which is unusual. The risk isn't interest cost — it's cash flow timing. The quarterly inventory repayment creates $15-57K cash hits at quarter-end that can collide with marketing spend peaks (especially Q4 holiday). This skill's job is to make those collisions visible before they happen.

## Data Model

### Ops Loan Tracking

Track in `debt_payments` table:

```sql
-- Ops loan balance calculation
SELECT
    250000 AS original_principal,
    COUNT(*) FILTER (WHERE payment_date IS NOT NULL) AS payments_made,
    COALESCE(SUM(amount) FILTER (WHERE payment_date IS NOT NULL), 0) AS total_paid,
    250000 - COALESCE(SUM(amount) FILTER (WHERE payment_date IS NOT NULL), 0) AS remaining_balance
FROM debt_payments
WHERE obligation_type = 'ops_loan';
```

### Spiritual-Director Payout Schedule

The spiritual-director payout is a fixed obligation on the books — $36K/yr for years 1-5, then $18K/yr for years 6-10. Total: $270K.

```sql
-- Spiritual-director payout balance
SELECT
    270000 AS total_obligation,
    COALESCE(SUM(amount) FILTER (WHERE payment_date IS NOT NULL), 0) AS total_paid,
    270000 - COALESCE(SUM(amount) FILTER (WHERE payment_date IS NOT NULL), 0) AS remaining,
    MIN(due_date) FILTER (WHERE payment_date IS NULL) AS next_due_date,
    3000 AS next_payment_amount
FROM debt_payments
WHERE obligation_type = 'spiritual_director_payout';
```

### Inventory Loan Balance

The inventory loan is the most complex — draws happen when inventory is purchased (investor-funded), repayments happen quarterly based on actual COGS of items sold.

```sql
-- Inventory loan running balance
SELECT
    COALESCE(SUM(draw_amount), 0) AS total_draws,
    COALESCE(SUM(repayment_amount), 0) AS total_repayments,
    COALESCE(SUM(draw_amount), 0) - COALESCE(SUM(repayment_amount), 0) AS current_balance,
    MAX(quarter_end) AS last_reconciliation
FROM inventory_loan_ledger;
```

## Monthly Report Workflow

```
1. GATHER BALANCES
   a. Query ops loan: payments made, remaining balance
   b. Query spiritual-director payout: payments made this year, remaining obligation
   c. Query inventory loan: current draw balance, last quarterly reconciliation

2. CALCULATE UPCOMING OBLIGATIONS (next 90 days)
   a. Ops loan: $3K/mo if past repayment start date (202707)
   b. Spiritual-director payout: $3K/mo (always)
   c. Inventory loan: estimate next quarter's COGS repayment from trailing revenue

3. CASH FLOW IMPACT
   a. Sum all monthly obligations
   b. Compare to projected operating cash flow from margin-reporting
   c. Flag if upcoming obligations exceed 50% of projected monthly cash generation
   d. Flag if ending cash balance would drop below $20K safety threshold

4. GENERATE REPORT
   a. Debt summary dashboard
   b. Payment schedule (next 6 months)
   c. Cash flow impact analysis
   d. Alerts and recommendations
```

## Report Format

```
MONTHLY DEBT SERVICE REPORT — {month}
══════════════════════════════════════════

DEBT SUMMARY
─────────────────────────────────────────
| Obligation     | Balance    | Monthly  | Next Due   |
|----------------|------------|----------|------------|
| Ops Loan       | $238,000   | $3,000   | 2027-08-01 |
| SD Payout      | $234,000   | $3,000   | 2026-05-01 |
| Inventory Loan | $47,200    | (qtrly)  | 2026-06-30 |
| TOTAL DEBT     | $519,200   | $6,000+  |            |

UPCOMING OBLIGATIONS (Next 90 Days)
─────────────────────────────────────────
| Date       | Type           | Amount  | Cash After |
|------------|----------------|---------|------------|
| 2026-05-01 | SD payout      | $3,000  | $258,319   |
| 2026-06-01 | SD payout      | $3,000  | $239,636   |
| 2026-06-30 | Inv reconcile  | $14,853 | $224,783   |

ALERTS
─────────────────────────────────────────
- None this month. Cash position healthy.
```

## Quarterly Inventory Reconciliation

This is the most operationally complex piece. At quarter-end:

1. **Pull product COGS sold** from orders for the quarter's 3 months
2. **Only include investor-funded inventory** — exclude any inventory purchased with operating cash
3. **Costing method**: Specific identification for items >$25, FIFO for bulk items <$25
4. **Generate reconciliation statement** showing draws vs. repayments
5. **Submit to investor** within 7 days of quarter-end
6. **Record payment** once made

```sql
-- Quarterly COGS for inventory reconciliation
SELECT
    DATE_TRUNC('quarter', order_date) AS quarter,
    SUM(
        CASE
            WHEN p.cogs_confidence = 'confirmed' THEN li.quantity * p.cogs_confirmed
            ELSE li.quantity * p.cogs_estimated
        END
    ) AS total_cogs_sold,
    COUNT(DISTINCT li.sku) AS skus_sold,
    SUM(li.quantity) AS units_sold
FROM order_line_items li
JOIN products p ON p.sku = li.sku
WHERE p.inventory_funding = 'investor'
  AND order_date >= DATE_TRUNC('quarter', CURRENT_DATE) - INTERVAL '3 months'
  AND order_date < DATE_TRUNC('quarter', CURRENT_DATE)
GROUP BY DATE_TRUNC('quarter', order_date);
```

## Model Routing

- **Balance lookups and payment recording**: Haiku 4.5 — deterministic queries
- **Monthly report generation**: Sonnet 4.6 — needs narrative about cash flow timing
- **Cash flow impact analysis and recommendations**: Sonnet 4.6 — business judgment needed
- **Quarterly inventory reconciliation**: Sonnet 4.6 — costing method decisions, edge cases

## Phase 1 Behavior

In Phase 1, this skill:
- Generates reports and alerts but does NOT make payments
- Does NOT modify loan terms or repayment schedules
- Does NOT communicate directly with investors

All actions require human decision:
- ceo reviews monthly debt report via dashboard
- ceo initiates all payments manually
- Quarterly inventory reconciliation requires ceo approval before submission to investor

## Escalation Paths

| Situation | Route To | Method | SLA |
|-----------|----------|--------|-----|
| Routine monthly report | ceo | Dashboard | 1st of month |
| Cash < $20K safety threshold projected | ceo | Dashboard + email | 24 hours |
| Quarterly inventory reconciliation due | ceo | Dashboard + email | 7 days before quarter-end |
| Payment overdue (>5 days past due) | ceo | Email alert | Immediate |
| Debt-to-revenue ratio > 2.0x | ceo | Dashboard (flagged) | Monthly |

Read `agents/shared/escalation-matrix/SKILL.md` for the full escalation reference.

## Output Format

```json
{
  "report_type": "monthly",
  "as_of_date": "2026-05-01",
  "obligations": {
    "ops_loan": {
      "original_principal": 250000,
      "total_paid": 0,
      "remaining_balance": 250000,
      "monthly_payment": 3000,
      "repayment_start": "2027-07",
      "status": "pre-repayment"
    },
    "spiritual_director_payout": {
      "total_obligation": 270000,
      "total_paid": 3000,
      "remaining": 267000,
      "monthly_payment": 3000,
      "current_year_paid": 3000,
      "current_year_target": 36000
    },
    "inventory_loan": {
      "total_draws": 20000,
      "total_repayments": 0,
      "current_balance": 20000,
      "last_reconciliation": null,
      "next_reconciliation_due": "2026-06-30"
    }
  },
  "total_debt": 537000,
  "upcoming_90_days": [
    {"date": "2026-06-01", "type": "spiritual_director_payout", "amount": 3000}
  ],
  "cash_flow_impact": {
    "monthly_fixed_obligations": 3000,
    "next_quarterly_estimate": 14853,
    "projected_cash_after_obligations": 242636
  },
  "alerts": [],
  "phase": 1,
  "confidence": 0.95
}
```

## Dependencies

- Read `agents/shared/supabase-ops-db/SKILL.md` for database schema
- Uses COGS data from `agents/finance/skills/cogs-tracking/SKILL.md` for inventory reconciliation
- Feeds into `agents/finance/skills/margin-reporting/SKILL.md` for cash flow context
- Read `agents/shared/escalation-matrix/SKILL.md` for routing decisions
