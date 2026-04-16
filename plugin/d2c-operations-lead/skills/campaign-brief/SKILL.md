---
name: campaign-brief
description: Use when a marketing campaign needs a structured brief, content calendar entry, or seasonal promotion plan for `general-manager` review.
---

# Campaign Brief

## Overview

Generates a structured campaign brief for D2C marketing initiatives, classifying content by tier and enforcing frequency caps before anything reaches `general-manager` for approval. Output is queued, never scheduled.

## When to Use

- **Invoke when:** a marketing initiative, seasonal event, or content calendar entry needs a formal brief for review

## Workflow

1. **Classify tier** — Apply the Content Tier Framework. If uncertain, escalate to Tier 3. Tier 4 is blocked; stop immediately and explain why.
2. **Check frequency caps** — Verify promotional email count and ad impression caps before drafting. If caps are at limit, do not draft — flag to `general-manager`.
3. **Check seasonal context** — For culturally or brand-significant events: approach with appropriate reverence and tone. Flag if the brief risks commercial momentum overriding significance.
4. **Draft the brief** — Use the format in `references/brief-template.md`.
5. **Verify compliance** — Run the Verification checklist before outputting.
6. **Queue output** — Write to `data/marketing-briefs-queue.json` with `"ai_generated": true`. Never publish or schedule.

## Common Rationalizations

| Rationalization | Reality |
|----------------|---------|
| "This is educational content, not promotional" | If it drives traffic to a product, it is Tier 2 minimum. Classify honestly. |
| "Our charitable mission makes this mission-driven, not marketing" | Charitable allocations are accounting lines, never campaign angles. |
| "We're just one email over the cap — it's a soft limit" | The cap is hard. Not sending is sometimes the correct decision. |
| "This seasonal event creates urgency" | Urgency language is Tier 4. Seasonal reverence is Tier 2/3. |

## Red Flags

- Any urgency, scarcity, or countdown language in draft copy (Tier 4 — block)
- Healing or spiritual benefit claims ("promotes mindfulness," "reduces stress")
- Charitable/mission commitments mentioned as a reason to purchase
- New Age conflation (chakra, energy, wellness framing)
- Brief produced without checking frequency caps
- Tier 3 content missing `brand-specialist` review note

## Verification

- [ ] Content tier classified correctly (Tier 4 = blocked, not queued)
- [ ] Frequency caps verified before drafting
- [ ] "What This Campaign Does NOT Do" section is substantive, not boilerplate
- [ ] No prohibited tactics (urgency, scarcity, FOMO, healing claims)
- [ ] Charitable allocation not present in any customer-facing copy
- [ ] Tier 3 brief flagged for `brand-specialist` review before `general-manager`
- [ ] Output written to `data/marketing-briefs-queue.json` with `"ai_generated": true`
- [ ] Compliance log entry includes `"ai_generated": true` and data accessed
