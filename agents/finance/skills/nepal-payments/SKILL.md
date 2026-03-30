---
name: nepal-payments
description: Track NPR payments to Nepal suppliers using the supplier_payments table. Use this skill for recording new invoices, monitoring USD/NPR exchange rates, matching invoices to POs, managing payment schedules, and coordinating payment approval with operations-manager (Bahasa Indonesia) and ceo. Feeds exchange rate data to cogs-tracking for accurate COGS.
version: "0.1.0"
category: finance
tags: [nepal, payments, supplier]
author: operations-team
model: sonnet
cacheable: true
estimated_tokens: 1600
phase: 1
depends_on: [shared/brand-guidelines, shared/supabase-ops-db]
external_apis: [supabase]
cost_budget_usd: 0.15
---

# Nepal Payments Skill

## Purpose

Manage the financial relationship with Nepal suppliers. Payments flow in Nepalese Rupees (NPR) while Tibetan Spirit operates in USD. This skill ensures:
1. **Invoices are recorded** accurately in both NPR and USD
2. **Exchange rates are tracked** at time of each transaction
3. **Invoices match POs** from supplier-communication
4. **Payment schedules are maintained** with upcoming due dates visible
5. **operations-manager is briefed in formal Bahasa Indonesia** on all payment actions
6. **ceo approves** all payments before wire transfer

Nepal suppliers typically expect payment terms of 50% advance on PO confirmation and 50% on shipment. Wire transfers take 2-3 business days. The exchange rate at time of payment determines the actual USD cost.

## Decision Tree

```
1. What triggered this skill?
   a. New supplier invoice received
      -> RECORD_INVOICE: match to PO, record NPR/USD amounts, set due date
   b. Payment due date approaching (within 7 days)
      -> PAYMENT_REMINDER: brief operations-manager, queue ceo approval
   c. Exchange rate check (daily cron)
      -> RATE_MONITOR: check for >3% movement, alert if significant
   d. Payment execution approved by ceo
      -> RECORD_PAYMENT: update payment_status, log exchange rate used
   e. Monthly payment reconciliation
      -> RECONCILE: match all payments to invoices, flag discrepancies

2. For RECORD_INVOICE:
   a. Match invoice to existing PO (by supplier + items + amounts)
   b. If no matching PO -> flag as unmatched, escalate to operations-manager
   c. Record in supplier_payments with current exchange rate
   d. Calculate USD equivalent
   e. Set payment_status = 'pending'
   f. Brief operations-manager in Bahasa Indonesia

3. For PAYMENT_REMINDER:
   a. Query upcoming payments (see SQL below)
   b. Calculate USD amount at current exchange rate
   c. Compare to rate at invoice time (flag if >3% movement)
   d. Draft approval request for ceo
   e. Brief operations-manager with payment summary in Bahasa Indonesia

4. For RATE_MONITOR:
   a. Fetch current USD/NPR rate
   b. Compare to rate used in outstanding invoices
   c. If movement >3%: alert ceo with impact on outstanding payables
   d. If movement >5%: flag as URGENT — may want to accelerate or delay payment
```

## Data Queries

### Record new invoice

```sql
INSERT INTO supplier_payments (
    supplier_name,
    invoice_number,
    amount_npr,
    amount_usd,
    exchange_rate,
    payment_status,
    payment_method,
    due_date
) VALUES ($1, $2, $3, $4, $5, 'pending', $6, $7)
ON CONFLICT (invoice_number) DO NOTHING
RETURNING id;
```

### Upcoming payments (due within 14 days)

```sql
SELECT
    id,
    supplier_name,
    invoice_number,
    amount_npr,
    amount_usd,
    exchange_rate,
    payment_status,
    payment_method,
    due_date,
    due_date - CURRENT_DATE AS days_until_due
FROM supplier_payments
WHERE payment_status IN ('pending', 'approved')
  AND due_date <= CURRENT_DATE + INTERVAL '14 days'
ORDER BY due_date ASC;
```

### Outstanding payables by supplier

```sql
SELECT
    supplier_name,
    COUNT(*) AS invoice_count,
    SUM(amount_npr) AS total_npr,
    SUM(amount_usd) AS total_usd,
    MIN(due_date) AS earliest_due
FROM supplier_payments
WHERE payment_status = 'pending'
GROUP BY supplier_name
ORDER BY earliest_due ASC;
```

### Record payment execution

```sql
UPDATE supplier_payments
SET payment_status = 'paid',
    payment_date = CURRENT_DATE,
    actual_exchange_rate = $1,
    actual_amount_usd = $2
WHERE id = $3;
```

### Payment history for a supplier

```sql
SELECT
    invoice_number,
    amount_npr,
    amount_usd,
    exchange_rate,
    payment_status,
    payment_method,
    due_date,
    payment_date
FROM supplier_payments
WHERE supplier_name = $1
ORDER BY due_date DESC
LIMIT 20;
```

## Exchange Rate Monitoring

- Source: exchangerate-api.com (free tier, daily updates)
- Track USD/NPR rate daily
- Current rate (as of project start): approximately 133 NPR per 1 USD
- Alert thresholds:
  - **>3% movement** from rate on outstanding invoices: notify ceo via dashboard
  - **>5% movement**: flag URGENT, recommend accelerating or delaying payment depending on direction
- Store rate history for trend analysis

### FX Impact Calculation

When preparing a payment, calculate the FX impact:

```
fx_impact_usd = amount_npr * (1/current_rate - 1/invoice_rate)

If fx_impact_usd > 0: rate moved favorably (NPR weakened, cheaper in USD)
If fx_impact_usd < 0: rate moved unfavorably (NPR strengthened, more expensive in USD)
```

Include this in every payment approval request so the ceo can make informed timing decisions.

## Bahasa Indonesia Payment Briefing (for operations-manager)

```
RINGKASAN PEMBAYARAN SUPPLIER
================================

Supplier: {supplier_name}
Nomor Invoice: {invoice_number}
Tanggal Jatuh Tempo: {due_date}

RINCIAN PEMBAYARAN:
- Jumlah (NPR): रू {amount_npr}
- Kurs saat invoice: {invoice_rate} NPR/USD -> ${invoice_usd}
- Kurs saat ini: {current_rate} NPR/USD -> ${current_usd}
- Dampak kurs: {favorable/unfavorable} ${abs(fx_impact)}

STATUS: {MENUNGGU PERSETUJUAN / DISETUJUI / DIBAYAR}

TINDAKAN YANG DIPERLUKAN:
Mungkin bisa Anda periksa invoice ini dan konfirmasi kesesuaian dengan pesanan.

CATATAN:
{Any relevant context about this supplier or payment}
```

## Model Routing

- **Invoice recording**: Haiku 4.5 -- structured data entry, deterministic matching
- **Exchange rate monitoring**: Haiku 4.5 -- simple comparison, threshold checks
- **Payment approval drafting**: Sonnet 4.6 -- needs to explain FX impact clearly to ceo
- **Bahasa Indonesia briefing**: Sonnet 4.6 -- formal register quality matters
- **Monthly reconciliation**: Sonnet 4.6 -- pattern detection, discrepancy analysis

## Phase 1 Behavior

In Phase 1, ALL payment actions require human approval:
- Invoice recording: operations-manager confirms the invoice matches the PO
- Payment scheduling: ceo approves all payments before wire transfer
- Exchange rate alerts: informational only, no automatic timing decisions
- No automatic wire transfers -- ceo initiates payments manually after approval

Payment approval flow:
1. Skill drafts payment request with FX analysis
2. operations-manager reviews invoice match (Bahasa Indonesia briefing)
3. ceo approves USD amount and timing
4. ceo executes wire transfer manually
5. Skill records the payment with actual exchange rate used

## Escalation Paths

| Situation | Route To | Method | SLA |
|-----------|----------|--------|-----|
| New invoice recorded | operations-manager | WhatsApp (Bahasa Indonesia) | 24 hours |
| Payment due within 7 days | operations-manager -> ceo | WhatsApp -> Dashboard | 48 hours |
| Payment overdue | ceo | Dashboard + email | 24 hours |
| FX rate moved >3% | ceo | Dashboard | 48 hours |
| FX rate moved >5% | ceo | Dashboard (URGENT) | 24 hours |
| Invoice doesn't match PO | operations-manager | WhatsApp (Bahasa Indonesia) | 24 hours |
| Invoice >$2,000 USD | ceo | Dashboard + email | 24 hours |
| Supplier claims non-receipt of payment | ceo + operations-manager | Dashboard + WhatsApp | 12 hours |

Read `skills/shared/escalation-matrix/SKILL.md` for the full escalation reference.

## Output Format

```json
{
  "action": "RECORD_INVOICE | PAYMENT_REMINDER | RATE_MONITOR | RECORD_PAYMENT | RECONCILE",
  "supplier_name": "Patan Metalworks",
  "invoice_number": "PM-2026-089",
  "amount_npr": 120000,
  "amount_usd_at_invoice": 900.90,
  "exchange_rate_at_invoice": 133.20,
  "current_exchange_rate": 134.50,
  "amount_usd_at_current_rate": 892.19,
  "fx_impact_usd": 8.71,
  "fx_direction": "favorable",
  "due_date": "2026-04-01",
  "days_until_due": 10,
  "payment_status": "pending",
  "po_match": "TS-PO-2026-047",
  "ops_manager_briefing_id": "...",
  "escalation_target": "operations-manager | ceo | ceo_and_operations-manager | null",
  "phase": 1,
  "requires_approval": true,
  "confidence": 0.90
}
```

## Dependencies

- Read `skills/shared/supabase-ops-db/SKILL.md` for database schema (supplier_payments table)
- Coordinates with `skills/operations/supplier-communication/SKILL.md` for PO reference
- Feeds payment data to `skills/finance/cogs-tracking/SKILL.md` for COGS confirmation
- Read `skills/shared/escalation-matrix/SKILL.md` for routing decisions
