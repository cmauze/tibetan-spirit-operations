---
name: cs-triage
description: Use when a customer email arrives and needs classification and routing before any response is drafted.
---

<HARD-GATE>
Brand-sensitive emails MUST be checked FIRST before any other classification. If the email contains questions about brand values, cultural significance, or product authenticity that require specialist knowledge, it escalates immediately to `brand-specialist` — no draft is created, no automated response is attempted.
</HARD-GATE>

# CS Email Triage

## Overview

Classifies incoming customer emails into 7 canonical categories and routes to the appropriate response workflow or escalation path. Brand-sensitive topics are always checked first.

## When to Use

- Incoming customer email needs classification before drafting
- CS drafter needs a category assignment for routing
- **Do NOT use for:** already-classified emails, internal team communications

## Workflow

1. Check for brand-sensitive content FIRST — if detected, escalate to `brand-specialist` immediately, do NOT draft
2. Check for complaint signals — priority handling
3. Multi-category: use highest severity (`complaint > order-issue > return-request > wholesale-inquiry > product-question > shipping-status`)
4. If uncertain: classify as `product-question`, flag for `general-manager` review
5. Apply brand voice checks (see Verification)
6. Log classification with `"ai_generated": true` for compliance

See `references/classification-matrix.md` for category signal words, response templates, and escalation paths.

## Common Rationalizations

| Rationalization | Reality |
|----------------|---------|
| "The question mentions the brand but it's really about the product" | If it touches brand values or cultural sensitivity, it is `brand-sensitive`. When uncertain, escalate. |
| "I'll draft a tentative response and flag it" | For `brand-sensitive`, do NOT draft. Escalation is the only output. |
| "Complaint is mild, I'll downgrade it" | Classify by content, not intensity. |

## Red Flags

- Drafting a response when category is `brand-sensitive`
- Downgrading complaint severity based on tone mildness
- Skipping brand voice checks
- Missing `"ai_generated": true` in log

## Verification

- [ ] Brand-sensitive check run FIRST
- [ ] Category assigned from canonical 7 categories only
- [ ] No brand-prohibited vocabulary used
- [ ] Products framed per brand guidelines
- [ ] No claims beyond product specifications
- [ ] Compliance log entry includes `"ai_generated": true`
