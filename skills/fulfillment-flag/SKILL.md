---
name: fulfillment-flag
description: Use when orders need exception flagging, fulfillment routing review, or shipping anomalies require team coordination.
---

# Fulfillment Flag

## Overview

Identifies fulfillment exceptions and routes them to the correct team member before a problem compounds. A delayed shipment is always better than a mis-routed one.

## When to Use

- **Invoke when:** An order is unfulfilled beyond threshold, tracking is missing after ship date, address validation fails, routing is ambiguous, or inventory counts conflict
- **Do NOT use for:** Standard order flow, routine fulfillment updates, or Shopify order modification (write operations require human approval)

## Workflow

1. **Evaluate the trigger** — Identify the exception type from the decision table below
2. **Investigate before escalating** — Check the order in Shopify and warehouse dashboard; Nepal supplier delays have infrastructure causes, not neglect
3. **Draft the flag** — Write the exception summary with order ID, trigger condition, and recommended action
4. **Route to the correct person** — Use the decision table to select the role and channel; use the correct language and register
5. **Queue to comms file** — Append to `data/fulfillment-comms-queue.json` with `"ai_generated": true`; never send directly

### Decision Table

| Condition | Route To | Channel | Language |
|-----------|----------|---------|----------|
| Unfulfilled >24h | `operations-manager` | Dashboard | Bahasa Indonesia, formal |
| Missing tracking after ship date | `warehouse-manager` | Dashboard | Mandarin |
| Domestic + international components | Manual review flag | Dashboard | — |
| Nepal supplier deadline <7 days | `ceo` | Slack | English |
| Address validation failure | `operations-manager` (hold order) | Dashboard | Bahasa Indonesia, formal |
| Inventory conflict (Shopify vs warehouse) | `warehouse-manager` (trust physical count) | Dashboard | Mandarin |

### Carrier Rules (flag when violated)

- USPS: light packages (<1 lb), standard domestic
- UPS: heavy or fragile items, oversized domestic
- DHL: international
- Singing bowls >10 in → custom boxing required
- Statues >$200 → double-box + insurance required
- Thangkas → tube shipping required

## Common Rationalizations

| Rationalization | Reality |
|----------------|---------|
| "I'll auto-route the mixed domestic/international order to save time" | NEVER auto-route mixed orders — flag for manual review every time |
| "The Nepal supplier is just a few days late, I'll wait" | Surface to Chris before the deadline passes; investigate first, but don't absorb the delay silently |
| "Shopify says we have stock, so we're fine" | Trust the physical count when it conflicts; Shopify can be stale |
| "I'll send the flag directly to Jothi over Slack" | Queue to `data/fulfillment-comms-queue.json`; never send directly |

## Red Flags

- Routing an order without flagging when routing is ambiguous
- Auto-routing an order with both domestic and international components
- Escalating a Nepal supplier delay without first investigating infrastructure causes
- Using "kamu" instead of "Anda" in Bahasa Indonesia comms
- Writing to the comms queue without `"ai_generated": true`
- Flagging with Shopify inventory data when physical count is available and conflicts

## Verification

- [ ] Exception type identified from decision table
- [ ] Investigation completed before escalation (no assumption of negligence)
- [ ] Correct role, channel, and language used per decision table
- [ ] Mixed domestic/international orders flagged for manual review — not auto-routed
- [ ] Flag queued to `data/fulfillment-comms-queue.json`, not sent
- [ ] `"ai_generated": true` included in queue entry
- [ ] Carrier and packaging rules checked for relevant orders
