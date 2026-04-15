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
- Cross-channel consistency needs to be verified (Shopify, Etsy, Amazon)

**Do NOT use for:**
- Descriptions that have already passed review and are live
- Category strategy decisions (use `category-judgment` rule)
- Publishing directly to any channel — output goes to `data/catalog-drafts-queue.json` only

## Workflow

1. **Parse structure** — Confirm 6-sentence structure per `references/rubric.md`. Rewrite to spec if missing.
2. **Score all 5 dimensions** — Apply `references/rubric.md`. Record score (1-10) + one-line rationale per dimension.
3. **Gate check** — Any dimension <8 → revise failing dimension(s) only, re-score. Max 3 cycles.
4. **Cross-channel check** — Same practice framing, terminology, and provenance across Shopify, Etsy, Amazon.
5. **Flag uncertain terms** — Cultural terms you're not certain about → flag for `spiritual-director`. Never generate plausible-sounding explanations.
6. **Write to queue** — Append to `data/catalog-drafts-queue.json` with `"ai_generated": true` and `"rubric_scores"`.

After 3 failed cycles: flag for human review, do not advance.

## Common Rationalizations

| Rationalization | Reality |
|----------------|---------|
| "The score is 7.5 — close enough to advance" | <8 means revise. The threshold is not a suggestion. |
| "Etsy shoppers expect different framing than practitioners" | Cross-channel consistency is non-negotiable. A mala is never "jewelry." |
| "I'm fairly sure this is the right cultural term" | Uncertainty = flag for `spiritual-director`. Plausible is not accurate. |
| "The SEO keywords will hurt the score but help conversion" | Practice-first framing is the SEO strategy. Commercial keywords are a separate failing. |

## Red Flags

- Advancing a description with any dimension score <8
- Using commercial keywords (wellness, boho, decor, relaxation tool, tapestry)
- Describing a mala as jewelry, a thangka as wall art, or a singing bowl as a sound bowl
- Generating cultural explanations without verified sourcing
- Writing directly to Shopify, Etsy, or Amazon — queue only

## Verification

- [ ] All 5 rubric dimensions scored with numeric score + rationale
- [ ] No dimension below 8
- [ ] 6-sentence structure confirmed (sentence 6 optional)
- [ ] Cross-channel variants use identical practice framing and terminology
- [ ] No banned vocabulary (exotic, mystical, oriental, ancient secrets, zen vibes, namaste)
- [ ] Sacred terms untranslated (mala, thangka, dharma, sangha, puja, mandala)
- [ ] Uncertain cultural terms flagged for `spiritual-director` — not explained
- [ ] `"ai_generated": true` in queue entry
- [ ] `"rubric_scores"` object in queue entry
