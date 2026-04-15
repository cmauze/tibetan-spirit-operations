---
name: order-inquiry
description: Handle "where is my order" and order status questions by looking up order details in Shopify and the Supabase operations database. Use this skill when a customer asks about order status, tracking, delivery timeline, or has concerns about a delayed shipment. This is the most common customer inquiry type (~40% of tickets).
version: "0.1.0"
category: customer-service
tags: [orders, status, shopify]
author: operations-team
model: haiku
cacheable: true
estimated_tokens: 850
phase: 1
depends_on: [shared/brand-guidelines, shared/product-knowledge]
external_apis: [supabase, shopify]
cost_budget_usd: 0.05
---

# Order Inquiry Skill

## Purpose

Customers asking about their order status is the single most common inquiry. This skill looks up the order, determines the current status, and generates an accurate, helpful response.

## Workflow

### Step 1: Identify the Order

Extract order identification from the customer's message:
- Order number (e.g., #1042, TS-1042)
- Email address (look up by customer email)
- Name + approximate date (last resort lookup)

Query the `orders` table in Supabase, or use the Shopify API directly if needed.

### Step 2: Determine Status

Map the order's fulfillment status to a customer-friendly explanation:

| Internal Status | Customer-Facing Status | Explanation |
|----------------|----------------------|-------------|
| `unfulfilled` | Being Prepared | Order received, being picked and packed |
| `partially_fulfilled` | Partially Shipped | Some items shipped, others being prepared |
| `fulfilled` + no tracking | Shipped | Label created, awaiting carrier scan |
| `fulfilled` + tracking active | On Its Way | In transit with carrier |
| `fulfilled` + delivered | Delivered | Carrier confirms delivery |
| `cancelled` | Cancelled | Order was cancelled (check reason) |
| `refunded` | Refunded | Refund processed |

### Step 3: Handle Special Cases

**Nepal-sourced items (longer lead times):**
Some products ship directly from our Nepal workshop. These have 2-4 week lead times. Check the `fulfillment_route` field — if it's "nepal", set appropriate expectations and explain the artisan sourcing context positively.

**FBA orders:**
Orders fulfilled by Amazon have separate tracking. Check `fulfillment_route = 'fba'` and direct customer to Amazon tracking.

**Delayed orders (>7 business days domestic, >21 days international):**
- Acknowledge the delay directly — don't make excuses
- Check carrier tracking for the last scan event
- If tracking shows no movement for 5+ days, escalate to warehouse-manager (domestic) or operations-manager (international)
- Offer a concrete next step: "I'm looking into this right now and will update you within 24 hours"

**Order not found:**
- Verify the email address and order number
- Check if the order might be under a different email
- If genuinely not found, ask the customer for their order confirmation email
- Do NOT say "we have no record of your order" — say "I'm having trouble locating your order with that information. Could you share your order confirmation email so I can look it up?"

### Step 4: Generate Response

Use the response template from `agents/customer-service/skills/ticket-triage/response-templates.md` as a starting point, but personalize:
- Include the specific tracking number and carrier
- If delayed, acknowledge proactively
- If delivered but customer claims non-receipt, escalate to operations-manager (Tier 2)
- For Nepal-sourced items, briefly explain the artisan sourcing — customers generally appreciate knowing their item is being crafted specifically

## Data Sources

1. **Supabase `orders` table** — Primary lookup for order status, fulfillment route
2. **Shopify Orders API** — Fallback for real-time status if Supabase sync is delayed
3. **Shippo API** — For detailed tracking events (carrier scans, delivery confirmation)

## Output

```json
{
  "order_found": true,
  "order_number": "#1042",
  "status": "on_its_way",
  "tracking_number": "9400...",
  "carrier": "USPS",
  "estimated_delivery": "2026-03-25",
  "response_draft": "...",
  "needs_escalation": false,
  "escalation_reason": null
}
```
