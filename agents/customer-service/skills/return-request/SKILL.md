---
name: return-request
description: Process customer return and refund requests by evaluating eligibility, determining approval authority, and drafting customer responses. Use this skill when a customer requests a return, refund, or exchange. Routes to the correct approver based on order value. Sacred items require special handling. Phase 1 requires human approval for ALL refunds.
version: "0.1.0"
category: customer-service
tags: [returns, refunds, policy]
author: operations-team
model: sonnet
cacheable: true
estimated_tokens: 3000
phase: 1
depends_on: [shared/brand-guidelines, shared/channel-config]
external_apis: [supabase, shopify]
cost_budget_usd: 0.15
---

# Return Request Processing Skill

## Purpose

Evaluate return requests against Tibetan Spirit's return policy, determine the correct approval path, and draft both the customer response and the internal approval brief. This skill must balance customer satisfaction with business protection while respecting the sacred nature of certain products.

Key responsibilities:
1. **Assess eligibility** -- time window, item condition, product type
2. **Route to correct approver** based on refund value thresholds
3. **Handle sacred items** with additional care and escalation
4. **Draft customer response** appropriate to the decision
5. **Brief operations-manager in formal Bahasa Indonesia** for operations follow-through

## Return Policy Summary

- **Window**: 30 days from delivery date
- **Condition**: Items must be unused and in original packaging
- **Shipping**: Prepaid return label for US orders; international customers pay return shipping
- **Processing**: Refunds issued within 5-7 business days of receiving the return
- **Exceptions**: See sacred items and final sale rules below

## Decision Tree

```
1. Is this a return, exchange, or refund-without-return request?
   -> Classify the request type

2. ELIGIBILITY CHECK:
   a. Was the order delivered within the last 30 days?
      -> Query order delivery date (see SQL below)
      -> No: DENY (outside return window)
      -> Yes: Continue
   b. Is the item in returnable condition?
      -> Customer claims unused/original packaging: Continue
      -> Customer admits use/damage: PARTIAL_REFUND or DENY depending on context
   c. Is this a final-sale item?
      -> Some clearance/sale items marked non-returnable: DENY
      -> Otherwise: Continue

3. SACRED ITEM CHECK:
   Is the item a consecrated/blessed item (specific thangkas, statues with puja)?
   -> Yes: Special handling required (see Sacred Items section below)
   -> No: Continue to approval routing

4. APPROVAL ROUTING (by refund value):
   a. Refund amount < $30:
      -> AUTO_APPROVE (generate RMA, draft customer email)
      -> Still requires human confirmation in Phase 1
   b. Refund amount $30 - $100:
      -> ESCALATE_OPS_MANAGER (Bahasa Indonesia briefing + English draft)
   c. Refund amount > $100:
      -> ESCALATE_CEO (dashboard approval queue)
   d. Any refund where customer mentions legal action or chargeback:
      -> URGENT -> ceo (regardless of amount)

5. GENERATE OUTPUT:
   a. RMA number (format: RMA-{YYYY}-{sequence})
   b. Customer response draft
   c. Internal approval brief (English + Bahasa Indonesia for operations-manager)
   d. Return shipping instructions
```

## Sacred Items — Special Handling

Some products carry spiritual significance that requires special return consideration:

- **Consecrated statues**: If a customer reports the statue was blessed or consecrated in a ceremony, advise them to consult with their teacher about appropriate disposition. Do not ask them to return a consecrated item through standard shipping.
- **Thangkas that have been hung on a shrine**: Traditional protocol suggests these should not be casually returned. Offer store credit instead of return.
- **Malas used in practice**: Once a mala has been used for mantra counting, it carries the practitioner's energy. Offer store credit rather than asking for physical return.

For any sacred item return question you are unsure about, escalate to spiritual-director. Never advise a customer to "just send it back" without considering the spiritual dimension.

**Draft language for sacred item situations:**
> We understand that sacred items carry special significance once they become part of your practice. Rather than asking you to return the item, we'd like to offer you store credit toward something that may better serve your needs. If you have questions about the appropriate way to handle a consecrated item, we can connect you with our spiritual advisor.

## Data Queries

### Look up order and delivery status

```sql
SELECT
    o.id,
    o.order_number,
    o.email,
    o.total_price,
    o.financial_status,
    o.fulfillment_status,
    o.created_at,
    o.delivered_at,
    o.line_items,
    o.channel,
    CURRENT_DATE - DATE(o.delivered_at) AS days_since_delivery
FROM orders o
WHERE o.order_number = $1
  AND o.financial_status = 'paid';
```

### Check if item is marked final sale

```sql
SELECT
    p.sku,
    p.title,
    p.tags,
    p.status
FROM products p
WHERE p.sku = $1
  AND 'final-sale' = ANY(p.tags);
```

### Log return request

```sql
INSERT INTO skill_invocations (
    agent_name,
    skill_name,
    trigger_source,
    raw_input,
    structured_result,
    model_used,
    confidence_score,
    phase,
    human_approved
) VALUES (
    'customer-service',
    'return-request',
    $1,
    $2,
    $3,
    $4,
    $5,
    1,
    false
);
```

## Response Templates

### Approved Return (within policy)

```
Hi {first_name},

Thank you for reaching out about returning your order. I'm happy to help.

I've initiated a return for:
- Order #{order_number}
- Item: {product_title}
- RMA Number: {rma_number}

Here's what to do next:
1. Pack the item in its original packaging
2. Use the prepaid return label attached to this email
3. Drop the package at any USPS location

Once we receive and inspect the item, your refund of ${refund_amount} will be processed within 5-7 business days to your original payment method.

If you have any questions, I'm here to help.

Warm regards,
Tibetan Spirit
```

### Denied Return (outside window)

```
Hi {first_name},

Thank you for reaching out. I understand you'd like to return your order from {order_date}.

Unfortunately, our return window is 30 days from delivery, and your order was delivered on {delivery_date} ({days_since_delivery} days ago). We're unable to process a standard return at this time.

However, I'd like to help find a solution:
- If there's a quality issue with the item, please let me know and we'll look into it separately
- We can offer a {discount_percentage}% discount on your next order as a gesture of goodwill

Is there anything else I can help with?

Warm regards,
Tibetan Spirit
```

### Sacred Item — Store Credit Offer

```
Hi {first_name},

Thank you for reaching out about your {product_title}.

We understand that sacred items carry special significance, especially once they've become part of your practice. Rather than asking you to return the item through standard shipping, we'd like to offer you ${store_credit_amount} in store credit toward something that may better serve your needs.

If you have questions about the appropriate way to care for or pass along a consecrated item, we can connect you with our spiritual advisor, who has deep experience in these matters.

Please let me know how you'd like to proceed.

With gratitude,
Tibetan Spirit
```

## Bahasa Indonesia Briefing (for operations-manager)

For returns routed to operations-manager ($30-$100):

```
PERMINTAAN PENGEMBALIAN BARANG
================================

Pelanggan: {customer_name}
Nomor Pesanan: #{order_number}
Produk: {product_title}
Jumlah Pengembalian: ${refund_amount}

RINCIAN:
- Tanggal pengiriman: {delivery_date}
- Hari sejak pengiriman: {days_since_delivery}
- Alasan: {reason}
- Kondisi barang: {condition}

REKOMENDASI:
{Recommendation in Bahasa Indonesia}
Mungkin bisa Anda setujui pengembalian dana ini. Pelanggan memenuhi syarat kebijakan kami.

TINDAKAN YANG DIPERLUKAN:
Silakan setujui atau tolak melalui dashboard.

DRAFT BALASAN PELANGGAN:
{English customer response draft included for operations-manager to review}
```

## Model Routing

- **Eligibility check**: Haiku 4.5 -- date math and policy lookup, deterministic
- **Sacred item assessment**: Sonnet 4.6 -- requires cultural sensitivity and judgment
- **Customer response drafting**: Sonnet 4.6 -- tone and empathy matter
- **Bahasa Indonesia briefing**: Sonnet 4.6 -- formal register quality
- **Legal threat / chargeback handling**: Sonnet 4.6 -- high-stakes communication

## Phase 1 Behavior

**CRITICAL: In Phase 1, ALL refunds require human approval regardless of amount.**

Even the <$30 "auto-approve" tier generates an approval request. The thresholds determine *who* approves, not whether approval is needed:
- <$30: operations-manager can approve (quick WhatsApp confirmation)
- $30-$100: operations-manager reviews with full briefing
- >$100: ceo approves via dashboard

No refund is processed, no RMA is issued, and no customer response is sent without human sign-off.

## Escalation Paths

| Situation | Route To | Method | SLA |
|-----------|----------|--------|-----|
| Return <$30, within policy | operations-manager | WhatsApp (Bahasa Indonesia) | 24 hours |
| Return $30-$100, within policy | operations-manager | WhatsApp (Bahasa Indonesia) | 24 hours |
| Return >$100 | ceo | Dashboard | 24 hours |
| Sacred item return question | spiritual-director | Email | 48 hours |
| Customer mentions chargeback/legal | ceo | Dashboard + email (URGENT) | 4 hours |
| Quality defect claim | operations-manager | WhatsApp (Bahasa Indonesia) | 12 hours |
| Outside return window but sympathetic case | ceo | Dashboard | 48 hours |

Read `skills/shared/escalation-matrix/SKILL.md` for the full escalation reference.

## Output Format

```json
{
  "request_type": "return | exchange | refund_only",
  "order_number": "#1042",
  "customer_email": "customer@example.com",
  "item_sku": "TS-BOWL-HH-5IN",
  "item_title": "Tibetan Singing Bowl - 5 inch",
  "refund_amount": 89.95,
  "days_since_delivery": 12,
  "eligible": true,
  "denial_reason": null,
  "sacred_item": false,
  "approval_tier": "ESCALATE_OPS_MANAGER",
  "rma_number": "RMA-2026-0142",
  "customer_response_draft": "...",
  "jhoti_briefing_id": "...",
  "escalation_target": "operations-manager | ceo | spiritual-director | null",
  "urgency": "normal | urgent",
  "phase": 1,
  "requires_approval": true,
  "confidence": 0.91
}
```

## Dependencies

- Read `skills/shared/supabase-ops-db/SKILL.md` for database schema
- Read `skills/shared/brand-guidelines/SKILL.md` for customer communication tone
- Read `skills/shared/brand-guidelines/cultural-sensitivity.md` for sacred item handling
- Read `skills/shared/product-knowledge/SKILL.md` for product category details
- Read `skills/shared/escalation-matrix/SKILL.md` for routing decisions
