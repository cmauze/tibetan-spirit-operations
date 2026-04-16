# CS Triage -- Classification Matrix

## Category Signals

| Category | Signal Words/Patterns | Response Action | Escalation |
|----------|----------------------|-----------------|------------|
| shipping-status | "where is my order", "tracking", "when will it arrive", "shipping update" | Tracking lookup + ETA | None |
| order-issue | "wrong item", "damaged", "broken", "missing", "incorrect" | Apology + resolution options | `general-manager` reviews |
| product-question | "what is", "how to use", "difference between", "recommend" | Product knowledge response | None |
| return-request | "return", "refund", "exchange", "send back" | Acknowledge + return policy | `general-manager` reviews |
| wholesale-inquiry | "wholesale", "bulk order", "reseller", "B2B", amount >$500 | Acknowledge + escalate | `general-manager` directly |
| brand-sensitive | Brand-specific signal words configured per store | DO NOT DRAFT | `brand-specialist` |
| complaint | negative tone, "disappointed", "unacceptable", "terrible" | Empathetic + priority flag | `general-manager` priority |

## Response Templates

### Greeting
Dear [First Name],

Thank you for reaching out.

### Shipping Status
We've looked into your order #[ORDER] and here's the latest:
[tracking info / ETA]

If you have any other questions, we're here to help.

### Order Issue
We're sorry to hear about this experience with your order. We take great care in preparing each item, and we want to make this right.

[Specific response based on issue type]

We'll follow up within [timeframe] with next steps.

### Return Request
We understand. Our return policy allows returns within [N] days of delivery for items in original condition.

To start the process:
1. [return steps]
2. [shipping instructions]

We'll process your [refund/exchange] within [timeframe] of receiving the item.

### Product Question
Great question! [Product name] is [description per brand guidelines].

[Specific answer]

If you'd like more guidance on choosing the right [product type] we're happy to help.

### Wholesale Inquiry
Thank you for your interest in carrying our products. We'd love to explore this with you.

Our team will be in touch within [timeframe] to discuss your needs.
