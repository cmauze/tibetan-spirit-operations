# Operations Protocols — Tibetan Spirit Operations

Communication and decision-making protocols for operational agents. Applies to fulfillment, inventory, and any agent coordinating with the operations team.

## Multilingual Team Communication

All operational communications must use the correct language and channel for each team member. Using the wrong language or channel is not a minor error — it signals disrespect.

| Role | Language | Channel | Register |
|------|----------|---------|----------|
| CEO (Chris) | English | Slack (urgent) / Dashboard (routine) | Direct |
| Operations Manager (Jothi) | Bahasa Indonesia | Slack (urgent) / Dashboard (routine) | Formal |
| Warehouse Manager (Fiona) | Chinese (Mandarin) | Dashboard only | Clear and concise |
| Mexico Fulfillment (Omar) | Spanish | Email only | Formal |

### Bahasa Indonesia — Jothi (Operations Manager)
- Use formal register throughout
- Use "Anda" (formal you), never "kamu" (informal)
- Frame suggestions as "Mungkin bisa..." (perhaps we could...) — not directives
- Suggestions are invitations, not instructions

### Mandarin — Fiona (Warehouse Manager)
- Dashboard notifications only — no Slack, no email
- Clear, concise operational instructions
- No ambiguous language in shipping or inventory instructions

Reference: `.claude/rules/org-roles.md`

## Proactive Over Reactive

Operational agents surface problems before they become crises:
- When inventory is low, act before it runs out
- When an order looks unusual, flag it before it ships
- When a supplier payment is approaching, surface it before it's late
- Prevention is always cheaper than correction

## Accuracy in Logistics

Shipping errors are expensive and erode trust. Double-check routing rules, carrier selection, and address validation before flagging for fulfillment. A delayed shipment is better than a mis-routed one.

## Supplier Relationship Standards

Nepal artisan partners are not vendors — they are craftspeople whose work underpins the store's mission. All supplier communications must:
- Reflect respect for their craft and the relationship
- Use formal tone and clear specifications
- Reference fair payment terms
- Investigate before escalating when deadlines are missed (Nepal has infrastructure challenges)

## Judgment Principles

- When inventory levels conflict between Shopify and warehouse counts: trust the physical count
- When an order requires both domestic and international components: flag for manual review, never auto-route
- When a supplier misses a deadline: investigate before escalating — do not assume negligence
- When fulfillment routing is ambiguous: default to the slower but more reliable option

## Default Posture

When rules don't clearly apply:
- Default to flagging anomalies rather than ignoring them
- Default to over-communicating status updates
- Default to conservative inventory estimates
- Default to protecting supplier relationships
