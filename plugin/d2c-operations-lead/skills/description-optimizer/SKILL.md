---
name: description-optimizer
description: Use when product descriptions need scoring against the quality rubric, revision through the evaluator-optimizer loop, or cross-channel consistency checking.
---

# Description Optimizer

## Overview

Runs the evaluator-optimizer loop on product descriptions — scoring against the 5-dimension rubric, revising until all dimensions pass, and verifying cross-channel consistency before queuing for review.

## When to Use

**Invoke when:**
- A new product description needs scoring before catalog entry
- An existing description is flagged for quality review
- Cross-channel consistency needs to be verified (Shopify, Etsy, Amazon, etc.)

**Do NOT use for:**
- Descriptions that have already passed review and are live
- Category strategy decisions
- Publishing directly to any channel — output goes to the catalog drafts queue only

## Workflow

1. **Parse structure** — Confirm 6-sentence structure per `references/rubric.md`. Rewrite to spec if missing.
2. **Score all 5 dimensions** — Apply `references/rubric.md`. Record score (1-10) + one-line rationale per dimension.
3. **Gate check** — Any dimension <8 → revise failing dimension(s) only, re-score. Max 3 cycles.
4. **Cross-channel check** — Same brand framing, terminology, and provenance across all sales channels.
5. **Flag uncertain terms** — Brand-specific or cultural terms you're not certain about → flag for `brand-specialist`. Never generate plausible-sounding explanations.
6. **Write to queue** — Append to catalog drafts queue with `"ai_generated": true` and `"rubric_scores"`.

After 3 failed cycles: flag for human review, do not advance.

## Common Rationalizations

| Rationalization | Reality |
|----------------|---------|
| "The score is 7.5 — close enough to advance" | <8 means revise. The threshold is not a suggestion. |
| "Different marketplace shoppers expect different framing" | Cross-channel consistency is non-negotiable. Products tell the same story everywhere. |
| "I'm fairly sure this is the right term" | Uncertainty = flag for `brand-specialist`. Plausible is not accurate. |
| "The SEO keywords will hurt the score but help conversion" | Brand-authentic framing is the SEO strategy. Commercial keywords are a separate failing. |

## Red Flags

- Advancing a description with any dimension score <8
- Using generic commercial keywords instead of brand-authentic terms
- Misrepresenting product category or positioning across channels
- Generating explanations for uncertain terms without verified sourcing
- Writing directly to any sales channel — queue only

## Verification

- [ ] All 5 rubric dimensions scored with numeric score + rationale
- [ ] No dimension below 8
- [ ] 6-sentence structure confirmed (sentence 6 optional)
- [ ] Cross-channel variants use identical brand framing and terminology
- [ ] No brand-prohibited vocabulary
- [ ] Uncertain terms flagged for `brand-specialist` — not explained
- [ ] `"ai_generated": true` in queue entry
- [ ] `"rubric_scores"` object in queue entry
