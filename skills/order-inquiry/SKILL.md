---
name: order-inquiry
description: Use when a customer asks about order status, tracking, delivery timeline, or has concerns about a delayed shipment.
---

# CS Order Inquiry

## Overview

Resolves customer questions about order status, tracking, and delivery by querying live order data and translating internal fulfillment states into customer-friendly language.

## When to Use

- **Invoke when:** Customer asks where their order is, requests a tracking number, questions a delivery estimate, or expresses concern about a delay
- **Do NOT use for:** Returns, cancellations, product questions, or complaints unrelated to shipment status — route those through cs-triage first

## Workflow

1. **Identify the order** — Locate via order number (preferred), confirmation email, or name + purchase date. If multiple matches exist, confirm with customer before proceeding.

2. **Query order status** — Pull from Supabase `ts_orders` first; fall back to Shopify GraphQL API for real-time state. Map internal status to customer-facing language per `references/status-mapping.md`.

3. **Handle special cases** — Nepal-sourced items (2–4 week lead times), FBA orders, delayed orders (>7 biz days domestic, >21 international), or order not found. See `references/status-mapping.md`.

4. **Draft the response** — Apply brand voice: warm, informative, practice-aware. Acknowledge any delay directly before offering next steps. Never use urgency language.

5. **Queue for human review** — All drafts go to the CS queue. CCPA ADMT compliance requires human approval before sending. Log with `"ai_generated": true`.

## Common Rationalizations

| Rationalization | Reality |
|----------------|---------|
| "I'll estimate delivery from the ship date" | Never guess. Pull actual carrier data or state it's unavailable. |
| "The delay is minor, I won't mention it" | Acknowledge delays directly. Customers who discover it themselves lose trust. |
| "We have no record of this order" | Never say this. Ask the customer to check their confirmation email first. |
| "FBA orders work the same way" | They don't. FBA fulfillment and tracking data comes from Amazon, not Shopify. |

## Red Flags

- Sending any response without human review (CCPA violation)
- Guessing a delivery date when carrier data is unavailable
- Using "we have no record" language before exhausting lookup options
- Skipping the Nepal sourcing explanation when it's relevant
- Missing `"ai_generated": true` in the log entry

## Verification

- [ ] Order located via at least one identifier (order number, email, name+date)
- [ ] Status pulled from `ts_orders` or Shopify fallback
- [ ] Customer-facing status uses mapped language (not internal enum)
- [ ] Special case rules applied if Nepal-sourced, FBA, delayed, or not found
- [ ] Response acknowledges delay before offering resolution (if applicable)
- [ ] No urgency language, no guessed delivery dates
- [ ] Draft queued in CS queue, not sent
- [ ] Log entry includes `"ai_generated": true`
