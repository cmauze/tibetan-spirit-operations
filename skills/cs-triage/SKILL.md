---
name: cs-triage
description: Use when a customer email arrives and needs classification and routing before any response is drafted.
---

<HARD-GATE>
Spiritual guidance emails MUST be checked FIRST before any other classification. If the email contains spiritual guidance requests, it escalates immediately to `spiritual-director` — no draft is created, no automated response is attempted. This is a non-negotiable cultural and business requirement.
</HARD-GATE>

# CS Email Triage

## Overview

Classifies incoming customer emails into 7 canonical categories and routes to the appropriate response workflow or escalation path. Spiritual-guidance is always checked first.

## When to Use

- Incoming customer email needs classification before drafting
- CS drafter needs a category assignment for routing
- **Do NOT use for:** already-classified emails, internal team communications

## Workflow

1. Check for spiritual-guidance FIRST -- if detected, escalate to `spiritual-director` immediately, do NOT draft
2. Check for complaint signals -- priority handling
3. Multi-category: use highest severity (`complaint > order-issue > return-request > wholesale-inquiry > product-question > shipping-status`)
4. If uncertain: classify as `product-question`, flag for `general-manager` review
5. Apply cultural sensitivity checks (see Verification)
6. Log classification with `"ai_generated": true` for CCPA compliance

See `references/classification-matrix.md` for category signal words, response templates, and escalation paths.

## Common Rationalizations

| Rationalization | Reality |
|----------------|---------|
| "The question mentions meditation but it's really about the product" | If it touches practice, it is `spiritual-guidance`. When uncertain, escalate. |
| "I'll draft a tentative response and flag it" | For `spiritual-guidance`, do NOT draft. Escalation is the only output. |
| "Complaint is mild, I'll downgrade it" | Classify by content, not intensity. |

## Red Flags

- Drafting a response when category is `spiritual-guidance`
- Downgrading complaint severity based on tone mildness
- Skipping cultural sensitivity checks
- Missing `"ai_generated": true` in log

## Verification

- [ ] Spiritual-guidance check run FIRST
- [ ] Category assigned from canonical 7 categories only
- [ ] No banned terms (exotic, mystical, oriental, ancient secrets, zen vibes, namaste)
- [ ] Sacred terms untranslated (mala, thangka, dharma, sangha, puja, mandala)
- [ ] Products framed through practice, not decor
- [ ] No spiritual promises or guarantees
- [ ] Dharma Giving not mentioned
- [ ] Customer's spiritual level not assumed
- [ ] CCPA log entry includes `"ai_generated": true`
