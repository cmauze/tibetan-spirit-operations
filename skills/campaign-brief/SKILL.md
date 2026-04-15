---
name: campaign-brief
description: Use when a marketing campaign needs a structured brief, content calendar entry, or seasonal promotion plan for Chris's review.
---

# Campaign Brief

## Overview

Generates a structured campaign brief for Tibetan Spirit marketing initiatives, classifying content by tier and enforcing frequency caps before anything reaches Chris for approval. Output is queued, never scheduled.

## When to Use

- **Invoke when:** a marketing initiative, seasonal event, or content calendar entry needs a formal brief for CEO review
- **Do NOT use for:** transactional emails (order confirmations, shipping notices — these are Tier 1, no brief needed), customer service responses, product descriptions, or any content that would require a brief to already exist

## Workflow

1. **Classify tier** — Apply the Content Tier Framework. If uncertain, escalate to Tier 3. Tier 4 is blocked; stop immediately and explain why.
2. **Check frequency caps** — Verify promotional email count (≤2/month) and ad impression caps (≤3/user/week) before drafting. If caps are at limit, do not draft — flag to Chris.
3. **Check seasonal context** — For Losar, Saga Dawa, Vesak, or Q4: approach with reverence. Flag if the brief risks commercial momentum overriding spiritual significance.
4. **Draft the brief** — Use the canonical format below. Do not invent fields or omit sections.
5. **Verify compliance** — Run the Verification checklist before outputting.
6. **Queue output** — Write to `data/marketing-briefs-queue.json` with `"ai_generated": true`. Never publish or schedule.

**Canonical brief format:**
```
# Campaign Brief: [Name]
**Objective:** [single sentence]
**Timing:** [dates]
**Audience:** [segment]
**Tier:** [2 or 3]
## Core Message
## Channels
## Content Requirements
## What This Campaign Does NOT Do
```

## Common Rationalizations

| Rationalization | Reality |
|----------------|---------|
| "This is educational content, not promotional" | If it drives traffic to a product, it is Tier 2 minimum. Classify honestly. |
| "Dharma Giving makes this mission-driven, not marketing" | Dharma Giving is an accounting line, never a campaign angle. |
| "We're just one email over the cap — it's a soft limit" | The cap is hard. Not sending is sometimes the correct decision. |
| "This seasonal event creates urgency" | Urgency language is Tier 4. Seasonal reverence is Tier 2/3. |

## Red Flags

- Any urgency, scarcity, or countdown language in draft copy (Tier 4 — block)
- Healing or spiritual benefit claims ("promotes mindfulness," "reduces stress")
- Dharma Giving mentioned as a reason to purchase
- New Age conflation (chakra, energy, wellness framing)
- Brief produced without checking frequency caps
- Tier 3 content missing Spiritual Director review note

## Verification

- [ ] Content tier classified correctly (Tier 4 = blocked, not queued)
- [ ] Frequency caps verified before drafting
- [ ] "What This Campaign Does NOT Do" section is substantive, not boilerplate
- [ ] No prohibited tactics (urgency, scarcity, FOMO, healing claims)
- [ ] Dharma Giving not present in any customer-facing copy
- [ ] Tier 3 brief flagged for Spiritual Director review before CEO
- [ ] Output written to `data/marketing-briefs-queue.json` with `"ai_generated": true`
- [ ] CCPA log entry includes `"ai_generated": true` and data accessed
