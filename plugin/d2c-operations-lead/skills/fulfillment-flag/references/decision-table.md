# Fulfillment Decision Table

## Exception Routing

| Condition | Route To | Channel | Language |
|-----------|----------|---------|----------|
| Unfulfilled >24h | `operations-manager` | Dashboard | Bahasa Indonesia, formal |
| Missing tracking after ship date | `warehouse-manager` | Dashboard | Mandarin |
| Domestic + international components | Manual review flag | Dashboard | — |
| International supplier deadline <7 days | `general-manager` | Chat/Slack | Strategic decision |
| Address validation failure | `operations-manager` (hold order) | Dashboard | Bahasa Indonesia, formal |
| Inventory conflict (Shopify vs warehouse) | `warehouse-manager` (trust physical count) | Dashboard | Mandarin |
| Regional/international shipping address | `regional-fulfillment` | Email | Regional team handles |

## Carrier Rules (flag when violated)

Configure per your shipping setup. Common patterns:
- Light packages (<1 lb): economy carrier (e.g., USPS)
- Heavy or fragile items: premium carrier with handling (e.g., UPS)
- International: international carrier (e.g., DHL)
- Fragile/high-value items: custom packaging + insurance required
- Oversized items: special shipping method required
