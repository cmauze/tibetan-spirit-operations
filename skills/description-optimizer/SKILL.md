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

1. **Parse structure** — Confirm the description follows the 6-sentence structure (see `references/rubric.md`). If structure is missing, rewrite to spec before scoring.
2. **Score all 5 dimensions** — Apply the rubric in `references/rubric.md`. Record numeric score (1-10) and one-line rationale for each dimension.
3. **Gate check** — If any dimension scores <8, go to step 4. If all ≥8, go to step 5.
4. **Revise** — Rewrite only the failing dimension(s). Do NOT rewrite passing content. Re-score. Repeat until all ≥8 or 3 revision cycles are exhausted.
5. **Cross-channel consistency check** — Verify the same core story (practice framing, terminology, provenance) is consistent across Shopify, Etsy, and Amazon variants.
6. **Flag uncertain terms** — Any cultural term you are not certain about: flag for Dr. Hun Lye review. Do NOT generate plausible-sounding explanations.
7. **Write to queue** — Append approved draft to `data/catalog-drafts-queue.json` with `"ai_generated": true` and `"rubric_scores"` object.

After 3 failed revision cycles: flag for human review, do not advance to queue.

## Common Rationalizations

| Rationalization | Reality |
|----------------|---------|
| "The score is 7.5 — close enough to advance" | <8 means revise. The threshold is not a suggestion. |
| "Etsy shoppers expect different framing than practitioners" | Cross-channel consistency is non-negotiable. A mala is never "jewelry." |
| "I'm fairly sure this is the right cultural term" | Uncertainty = flag for Dr. Hun Lye. Plausible is not accurate. |
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
- [ ] Uncertain cultural terms flagged for Dr. Hun Lye — not explained
- [ ] `"ai_generated": true` in queue entry
- [ ] `"rubric_scores"` object in queue entry
