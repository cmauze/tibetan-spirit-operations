# Fulfillment Decision Table

## Exception Routing

| Condition | Route To | Channel | Notes |
|-----------|----------|---------|-------|
| Unfulfilled >24h | `operations-manager` | Dashboard/chat | Standard ops escalation |
| Missing tracking after ship date | `warehouse-manager` | Dashboard | Warehouse investigation |
| Domestic + international components | Manual review flag | Dashboard | NEVER auto-route |
| International supplier deadline <7 days | `general-manager` | Chat/Slack | Strategic decision |
| Address validation failure | `operations-manager` (hold order) | Dashboard | Hold until resolved |
| Inventory conflict (Shopify vs warehouse) | `warehouse-manager` (trust physical count) | Dashboard | Physical count wins |
| Regional/international shipping address | `regional-fulfillment` | Email | Regional team handles |

## Carrier Rules (flag when violated)

Configure per your shipping setup. Common patterns:

- Light packages (<1 lb): economy carrier (e.g., USPS)
- Heavy or fragile items: premium carrier with handling (e.g., UPS)
- International: international carrier (e.g., DHL)
- Fragile/high-value items: custom packaging + insurance required
- Oversized items: special shipping method required

Document your product-specific carrier rules in this file when configuring the plugin.
