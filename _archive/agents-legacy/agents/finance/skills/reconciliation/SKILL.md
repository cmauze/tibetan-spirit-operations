---
name: reconciliation
description: Reconcile revenue across all sales channels (Shopify, Etsy, Amazon) against QuickBooks and the Supabase operations database. Use this skill for daily reconciliation checks, weekly margin reports, monthly P&L preparation, or whenever discrepancies are detected between channel reports and financial records.
version: "0.1.0"
category: finance
tags: [reconciliation, accounting, discrepancy]
author: operations-team
model: sonnet
cacheable: true
estimated_tokens: 1000
phase: 1
depends_on: [shared/brand-guidelines, shared/supabase-ops-db]
external_apis: [supabase]
cost_budget_usd: 0.15
---

# Revenue Reconciliation Skill

## Purpose

Ensure that revenue reported by each sales channel matches what's recorded in QuickBooks and the Supabase operations database. Catch discrepancies early — a $50 error today could be a $5,000 pattern by month-end.

## Reconciliation Cadence

| Frequency | Scope | Trigger |
|-----------|-------|---------|
| **Daily** (6 AM ET) | Previous day's orders across all channels vs. Supabase | Cron |
| **Weekly** (Monday 9 AM ET) | Week-to-date revenue by channel vs. QuickBooks | Cron |
| **Monthly** (2nd business day) | Full month P&L reconciliation | Cron + ceo review |

## Daily Reconciliation Workflow

### Step 1: Pull Channel Data

For each active channel, get yesterday's order totals:

**Shopify:**
- Query Shopify Orders API for orders created yesterday
- Sum: gross revenue, discounts, shipping collected, taxes collected, refunds
- Net revenue = gross - discounts - refunds

**Etsy (when live):**
- Query Etsy Receipts API for yesterday's transactions
- Account for Etsy fees (6.5% transaction + 3% payment processing)

**Amazon (when live):**
- Query Amazon Settlement Report or SP-API for yesterday's orders
- Account for referral fees (15%) + FBA fees

### Step 2: Compare Against Supabase

Query `orders` table for the same date range:
```sql
SELECT channel,
       COUNT(*) as order_count,
       SUM(total_price) as gross_revenue,
       SUM(total_discounts) as discounts,
       SUM(total_shipping) as shipping_collected,
       SUM(total_tax) as tax_collected
FROM orders
WHERE DATE(created_at) = DATE('yesterday')
  AND financial_status != 'voided'
GROUP BY channel;
```

### Step 3: Identify Discrepancies

Compare channel source data vs. Supabase records:

| Check | Acceptable Variance | Action if Exceeded |
|-------|--------------------|--------------------|
| Order count mismatch | 0 (exact match) | Flag immediately — missing orders |
| Revenue variance | <$5 or <0.5% | Log only |
| Revenue variance $5-$50 | N/A | Flag for ceo, 48-hour SLA |
| Revenue variance >$50 | N/A | Flag URGENT for ceo, 24-hour SLA |
| Refund not reflected | 0 (exact match) | Flag — refunds must propagate |

### Step 4: Generate Report

Daily reconciliation report format:

```
DAILY RECONCILIATION — 2026-03-20
═══════════════════════════════════

SHOPIFY
  Orders: 12 (Supabase: 12) ✓
  Gross Revenue: $1,847.50 (Supabase: $1,847.50) ✓
  Refunds: $0.00 ✓
  Net Revenue: $1,847.50 ✓

ETSY
  Orders: 3 (Supabase: 3) ✓
  Gross Revenue: $245.00 (Supabase: $245.00) ✓

DISCREPANCIES: None

DAILY TOTAL: $2,092.50 across 15 orders
```

## Weekly QuickBooks Reconciliation

Compare Supabase weekly totals against QuickBooks:

1. Export QuickBooks revenue by category for the week
2. Query Supabase for the same period grouped by channel
3. Compare totals — acceptable variance is <$25 or <1%
4. Common discrepancy sources:
   - Timing differences (order placed end of day, recorded next day)
   - Refunds processed in different periods
   - Manual QuickBooks entries not reflected in Supabase
   - Foreign currency conversion differences

## Monthly P&L Reconciliation

The most comprehensive check. Produces a full P&L comparison:

1. **Revenue**: Channel revenue vs. QuickBooks income accounts
2. **COGS**: Supabase `products.cogs_confirmed` × units sold vs. QuickBooks COGS entries
3. **Fees**: Calculated channel fees vs. actual platform invoices
4. **Shipping**: Shippo actual costs vs. shipping collected from customers
5. **Operating Expenses**: QuickBooks expense categories vs. budgeted amounts

Output feeds into the `channel_profitability_monthly` materialized view.

## Idempotency

Reconciliation is a read-heavy, write-light operation, but when it does write (logging discrepancies, updating sync status):
- Check `skill_invocations` for a reconciliation run on the same date before running
- Use `ON CONFLICT` for any upsert operations
- Never modify order or financial data — only flag discrepancies for human review

## Phase 1 Behavior

- Daily reconciliation runs automatically and logs results
- Discrepancies >$5 appear in ceo's approval queue
- No automated corrections — all fixes require human action
- Monthly P&L requires ceo's explicit review and sign-off

## QuickBooks Integration Note

QuickBooks API access is not yet configured. Until it is:
- Weekly and monthly reconciliation steps that require QuickBooks are skipped
- Log a reminder that QuickBooks integration is pending
- Daily channel-vs-Supabase reconciliation still runs (doesn't need QuickBooks)

## Output

```json
{
  "date": "2026-03-20",
  "type": "daily",
  "channels": {
    "shopify": {"orders": 12, "gross_revenue": 1847.50, "status": "matched"},
    "etsy": {"orders": 3, "gross_revenue": 245.00, "status": "matched"}
  },
  "discrepancies": [],
  "total_revenue": 2092.50,
  "total_orders": 15,
  "quickbooks_status": "not_connected"
}
```
