# Fulfillment Decision Table

## Exception Routing

| Condition | Route To | Channel | Language |
|-----------|----------|---------|----------|
| Unfulfilled >24h | `operations-manager` | Dashboard | Bahasa Indonesia, formal |
| Missing tracking after ship date | `warehouse-manager` | Dashboard | Mandarin |
| Domestic + international components | Manual review flag | Dashboard | — |
| Nepal supplier deadline <7 days | `general-manager` | Slack | English |
| Address validation failure | `operations-manager` (hold order) | Dashboard | Bahasa Indonesia, formal |
| Inventory conflict (Shopify vs warehouse) | `warehouse-manager` (trust physical count) | Dashboard | Mandarin |
| Latin American shipping address | `mexico-fulfillment` | Email | Spanish |

## Carrier Rules (flag when violated)

- USPS: light packages (<1 lb), standard domestic
- UPS: heavy or fragile items, oversized domestic
- DHL: international
- Singing bowls >10 in → custom boxing required
- Statues >$200 → double-box + insurance required
- Thangkas → tube shipping required
