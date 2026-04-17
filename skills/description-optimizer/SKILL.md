---
name: description-optimizer
description: Runs the evaluator-optimizer loop on product descriptions — scores against the 5-dimension rubric, revises until all dimensions pass, and verifies cross-channel consistency before queuing for review. Use when a product description needs scoring, revision, or cross-channel consistency checking.
allowed-tools: Read, Write
---

# Description Optimizer

**Announce at start:** "I'm using the description-optimizer skill to score and refine this product description."

## Goal

Score a product description against the 5-dimension quality rubric, revise any dimension below the threshold (score <8), confirm cross-channel consistency across Shopify, Etsy, and Amazon, and queue the passing description for human review. Maximum 3 revision cycles; descriptions that do not pass after 3 cycles are flagged for human review, not advanced.

## Process

1. **Parse structure** — Confirm 6-sentence structure per `references/rubric.md`. Rewrite to spec if missing or malformed.
2. **Score all 5 dimensions** — Apply `references/rubric.md`. Record numeric score (1–10) and one-line rationale for each dimension.
3. **Gate check** — Any dimension <8 → revise the failing dimension(s) only, re-score. Repeat up to 3 cycles. After 3 failed cycles, flag for human review — do not advance to queue.
4. **Cross-channel check** — Verify same practice framing, terminology, and provenance across Shopify, Etsy, and Amazon variants. A mala is never "jewelry" on any platform.
5. **Flag uncertain terms** — Cultural terms you are not certain about → flag for `spiritual-director`. Never generate plausible-sounding explanations for uncertain terms.
6. **Write to queue** — Append to `data/catalog-drafts-queue.json` with `"ai_generated": true` and `"rubric_scores"` object. Log observability entry to `data/agent-runs.json` per `_templates/observability.md`.

## Output

- **Primary:** `data/catalog-drafts-queue.json` — passing description with `rubric_scores` and `"ai_generated": true`
- **Secondary:** `data/agent-runs.json` — one observability entry per `_templates/observability.md`
- **Terminal:** Score table per dimension, revision cycle count, and cross-channel status

**Verification:** All 5 rubric dimensions scored ≥8. 6-sentence structure confirmed. Cross-channel variants use identical practice framing and terminology. No banned vocabulary. Sacred terms untranslated. Uncertain cultural terms flagged for `spiritual-director`. Output written to queue, not published to any channel.

## Common Rationalizations

| Thought | Reality |
|---|---|
| "The score is 7.5 — close enough to advance" | <8 means revise. The threshold is not a suggestion. |
| "Etsy shoppers expect different framing than practitioners" | Cross-channel consistency is non-negotiable. A mala is never "jewelry." |
| "I'm fairly sure this is the right cultural term" | Uncertainty = flag for `spiritual-director`. Plausible is not accurate. |
| "The SEO keywords will hurt the score but help conversion" | Practice-first framing is the SEO strategy. Commercial keywords are a separate failing. |

## Edge Cases

- **3 cycles without passing:** Flag for human review. Write the best-attempt draft with scores to `data/catalog-drafts-queue.json` with `"status": "needs-human-review"`. Do not advance as approved.
- **Uncertain cultural term:** Flag in the queue entry with `"cultural_flags": ["<term>"]`. Do not block queue submission — the flag routes the review.
- **Cross-channel inconsistency found:** Revise the inconsistent variant before advancing. Log which channel required the change.

## Rules

- NEVER advance a description with any dimension score <8 (before cycle 3 exhaustion).
- NEVER use commercial keywords: wellness, boho, decor, relaxation tool, tapestry, sound bowl, jewelry.
- NEVER write directly to Shopify, Etsy, or Amazon — queue only.
- ALWAYS include `rubric_scores` object in every queue entry.

## Environment

- **Data files:** `data/catalog-drafts-queue.json`, `data/agent-runs.json`
- **Reference files:** `references/rubric.md`, `_templates/observability.md`
- **Rules:** `.claude/rules/brand-voice.md`, `.claude/rules/cultural-sensitivity.md`, `.claude/rules/ecommerce-judgment.md`

## Works Well With

- **Invoked by:** `catalog-curator` agent (step 4)
- **Preceded by:** `catalog-curator` draft step
