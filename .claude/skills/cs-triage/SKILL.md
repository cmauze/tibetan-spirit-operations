# CS Email Triage Skill

Classifies incoming customer emails and routes them to the appropriate response workflow.

## Classification Categories

| Category | Signal Words/Patterns | Response Template | Escalation |
|----------|----------------------|-------------------|------------|
| shipping-status | "where is my order", "tracking", "when will it arrive", "shipping update" | Tracking lookup + ETA | None |
| order-issue | "wrong item", "damaged", "broken", "missing", "incorrect" | Apology + resolution options | Chris reviews |
| product-question | "what is", "how to use", "difference between", "recommend" | Product knowledge response | None |
| return-request | "return", "refund", "exchange", "send back" | Acknowledge + return policy | Chris reviews |
| wholesale-inquiry | "wholesale", "bulk order", "reseller", "B2B", >$500 mentioned | Acknowledge + escalate | Chris directly |
| spiritual-guidance | "dharma", "practice", "meditation", "blessing", "mantra", "lineage", "lama" | DO NOT DRAFT | Dr. Hun Lye |
| complaint | negative tone, "disappointed", "unacceptable", "terrible" | Empathetic + priority flag | Chris priority |

## Classification Rules

1. Check for spiritual-guidance FIRST — if detected, escalate immediately, do not draft
2. Check for complaint signals — these get priority handling
3. Multi-category emails: use the highest-severity category (complaint > order-issue > return > others)
4. If uncertain: classify as product-question (safest default) and flag for Chris review

## Response Templates

### Greeting
```
Dear [First Name],

Thank you for reaching out to Tibetan Spirit.
```

### Shipping Status
```
We've looked into your order #[ORDER] and here's the latest:
[tracking info / ETA]

If you have any other questions, we're here to help.
```

### Order Issue
```
We're sorry to hear about this experience with your order. We take great care in
preparing each item, and we want to make this right.

[Specific response based on issue type]

We'll follow up within [timeframe] with next steps.
```

### Return Request
```
We understand. Our return policy allows returns within 30 days of delivery for
items in original condition.

To start the process:
1. [return steps]
2. [shipping instructions]

We'll process your [refund/exchange] within [timeframe] of receiving the item.
```

### Product Question
```
Great question! [Product name] is [description rooted in practice context].

[Specific answer]

If you'd like more guidance on choosing the right [product type] for your practice,
we're happy to help.
```

### Wholesale Inquiry
```
Thank you for your interest in carrying Tibetan Spirit products. We'd love to
explore this with you.

Chris Mauzé, our founder, handles wholesale relationships directly. He'll be in
touch within [timeframe] to discuss your needs.
```

## Cultural Sensitivity Checks (MANDATORY)

Before finalizing ANY draft, verify ALL of the following:

- [ ] No banned terms: exotic, mystical, oriental, ancient secrets, zen vibes, namaste
- [ ] Sacred terms untranslated: mala, thangka, dharma, sangha, puja, mandala
- [ ] Products framed through practice, not decor ("for your meditation practice" not "for your living room")
- [ ] No spiritual promises ("this mala has been traditionally used for..." not "this mala will bring you...")
- [ ] Dharma Giving (5%) never mentioned
- [ ] Customer's spiritual level never assumed

## CCPA Compliance

- Log every customer data access with purpose in data/cs-drafts-log.json
- Never store customer PII outside the draft/log context
- If customer requests data deletion, escalate to Chris immediately
- AI-generated drafts must note "AI-drafted, human-reviewed" in internal metadata
