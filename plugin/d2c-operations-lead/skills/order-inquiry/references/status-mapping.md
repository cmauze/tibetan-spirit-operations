# Order Status Mapping

Reference for Step 2 and Step 3 of the order-inquiry workflow.

## Internal → Customer-Facing Status

| Internal Status | Customer-Facing Language | Notes |
|----------------|--------------------------|-------|
| `unfulfilled` | "Being Prepared" | Order received, not yet picked/packed |
| `partially_fulfilled` | "Partially Shipped" | Some items shipped, remainder still processing |
| `fulfilled` (no tracking) | "Shipped" | Fulfillment confirmed but carrier scan not yet available |
| `fulfilled` + tracking URL | "On Its Way" | Include tracking link in response |
| `fulfilled` + delivered event | "Delivered" | Confirm delivery date from carrier |

## Special Cases

### Long-Lead-Time Items (International Sourcing)
Items sourced from international artisan partners may carry extended lead times before fulfillment. When a customer inquires:
- Explain the sourcing context positively — these items are crafted by skilled artisans
- Provide the expected fulfillment window (not a delivery date)
- Do not apologize for the lead time; frame it as part of the item's provenance

### Marketplace-Fulfilled Orders (e.g., FBA)
Orders fulfilled through marketplaces (Amazon FBA, etc.) are tracked through the marketplace, not Shopify. Shopify fulfillment status will not reflect the true state.
- Do not use Shopify tracking data for marketplace-fulfilled orders
- Direct the customer to their marketplace order confirmation for tracking
- If the customer purchased on your site but the order routes to marketplace fulfillment, explain this clearly

### Delayed Orders
A shipment is considered delayed when:
- **Domestic:** No delivery scan within 7 business days of ship date
- **International:** No delivery scan within 21 business days of ship date

When a delay is confirmed:
1. Acknowledge the delay directly in the first sentence — do not bury it
2. State what is known (last carrier scan, current location if available)
3. Offer a concrete next step: carrier investigation request, replacement, or refund
4. Escalate to `operations-manager` if a carrier claim needs to be filed

### Order Not Found
When no order matches the customer's provided information:
- **Never say** "we have no record of that order"
- Ask the customer to locate their original confirmation email
- Try alternate lookups: different email address, guest vs. account order, potential typo in order number
- If still unresolved after two attempts, escalate for manual investigation
