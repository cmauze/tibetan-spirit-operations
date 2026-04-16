# Description Quality Rubric

Reference for the `description-optimizer` skill. All product descriptions must score ≥8/10 on every dimension before advancing to the catalog drafts queue.

---

## Required Structure (150-250 words)

| Sentence | Content |
|----------|---------|
| 1 | What the item IS and what purpose or context it serves (brand-first) |
| 2-3 | Craftsmanship, sourcing, and materials — specific terms required |
| 4-5 | Practical guidance: how to use, care instructions, intended context |
| 6 (optional) | Provenance, artisan story, or sourcing context |

---

## 5-Dimension Rubric

### Dimension 1 — Brand-First Framing
**Criterion:** The description leads with the brand's core value proposition before any material, aesthetic, or commercial detail.

| Score | Meaning |
|-------|---------|
| 10 | Opens with explicit brand context; no generic commercial framing anywhere |
| 8-9 | Opens with brand context; minor commercial language appears later |
| 5-7 | Brand and commercial framing compete; unclear which leads |
| <5 | Description leads with aesthetics, price, or lifestyle framing |

**Test:** Read only the first sentence. Does it tell the customer what makes this product distinctive to your brand? If not, score ≤7.

---

### Dimension 2 — Brand Accuracy
**Criterion:** Brand-specific and category-specific terms are used correctly. No conflation with competitors or generic alternatives.

| Score | Meaning |
|-------|---------|
| 10 | All terms verified; no conflation; brand references are specific and accurate |
| 8-9 | Terms correct; one minor imprecision that does not misrepresent the brand |
| 5-7 | Noticeable conflation or vague brand language |
| <5 | Brand-prohibited vocabulary present, or significant misrepresentation |

**Escalation rule:** When uncertain whether a term is used correctly, flag for `brand-specialist`. Do not generate plausible explanations.

---

### Dimension 3 — SEO Authenticity
**Criterion:** Search terms reflect how your actual customers search — not how generic shoppers search.

| Score | Meaning |
|-------|---------|
| 10 | All search terms are customer-native; no generic commercial keywords |
| 8-9 | Primary terms authentic; one commercial keyword present but not dominant |
| 5-7 | Mixed — commercial and authentic terms compete |
| <5 | Optimized for generic audience, not your customers |

---

### Dimension 4 — Cross-Channel Consistency
**Criterion:** The same product tells the same story on every sales channel. Formatting may differ; meaning and framing must not.

| Score | Meaning |
|-------|---------|
| 10 | Identical brand framing, terminology, and provenance across all channels |
| 8-9 | Consistent framing; minor formatting differences only |
| 5-7 | Channel-specific meaning differences; one channel uses different framing |
| <5 | Product positioned differently across channels |

---

### Dimension 5 — Specificity
**Criterion:** Provenance, maker, and technique are named — not gestured at.

| Score | Meaning |
|-------|---------|
| 10 | Specific maker, region, technique, and material source named and verifiable |
| 8-9 | Specific region or technique named; one element vague but not misleading |
| 5-7 | Generic provenance language without specifics |
| <5 | No provenance; description could apply to any similar product |

---

## Scoring Record Format

Each queue entry must include:

```json
{
  "rubric_scores": {
    "brand_first_framing": 9,
    "brand_accuracy": 8,
    "seo_authenticity": 9,
    "cross_channel_consistency": 10,
    "specificity": 8
  },
  "revision_cycles": 1,
  "flagged_terms": [],
  "ai_generated": true
}
```

If any score is <8, the entry must not appear in the queue. If `flagged_terms` is non-empty, the entry waits for `brand-specialist` review before advancing.
