# Description Quality Rubric

Reference for the `description-optimizer` skill. All product descriptions must score ≥8/10 on every dimension before advancing to the catalog drafts queue.

---

## Required Structure (150-250 words)

| Sentence | Content |
|----------|---------|
| 1 | What the item IS and what tradition or practice it serves |
| 2-3 | Craftsmanship, sourcing, and materials — specific terms required |
| 4-5 | Practical guidance: how to use, care instructions, practice context |
| 6 (optional) | Cultural context, lineage, or sourcing story |

---

## 5-Dimension Rubric

### Dimension 1 — Practice-First Framing
**Criterion:** The description leads with spiritual or contemplative purpose before any material, aesthetic, or commercial detail.

| Score | Meaning |
|-------|---------|
| 10 | Opens with explicit practice context; no commercial framing anywhere in the description |
| 8-9 | Opens with practice context; minor commercial language appears later |
| 5-7 | Practice and commercial framing compete; unclear which leads |
| <5 | Description leads with aesthetics, price, or lifestyle framing |

**Test:** Read only the first sentence. Does it tell a practitioner why this item exists in their practice? If not, score ≤7.

---

### Dimension 2 — Cultural Accuracy
**Criterion:** Buddhist and Himalayan terms are used correctly. No conflation with New Age, Hinduism, or generic "spirituality." No banned vocabulary.

| Score | Meaning |
|-------|---------|
| 10 | All terms verified; no conflation; lineage references are specific and accurate |
| 8-9 | Terms correct; one minor imprecision that does not misrepresent the tradition |
| 5-7 | Noticeable conflation or vague cultural language |
| <5 | Banned vocabulary present, or significant misrepresentation |

**Banned vocabulary:** exotic, mystical, oriental, ancient secrets, zen vibes, namaste, chakra (in Buddhist context), energy (as spiritual force), boho, wellness (applied to sacred items)

**Sacred terms stay untranslated and unclarified in parentheses:**
- "Mala" — not "prayer bracelet" or "meditation beads necklace"
- "Thangka" — not "tapestry," "wall art," or "Tibetan painting"
- "Puja items" — not "altar decor" or "ritual accessories"
- "Dharma" — Buddha's teachings specifically, not generic "spiritual path"
- "Sangha" — community of practitioners, not generic "community"
- "Mandala" — cosmological diagram with specific tradition, not "circular design"

**Escalation rule:** When uncertain whether a term is used correctly, flag for `spiritual-director`. Do not generate plausible explanations. Score the dimension conservatively until confirmed.

---

### Dimension 3 — SEO Authenticity
**Criterion:** Search terms reflect how practitioners actually search — not how lifestyle consumers search.

| Score | Meaning |
|-------|---------|
| 10 | All search terms are practitioner-native; no commercial keywords |
| 8-9 | Primary terms authentic; one commercial keyword present but not dominant |
| 5-7 | Mixed — commercial and authentic terms compete |
| <5 | Optimized for lifestyle/wellness audience, not practitioners |

**Acceptable patterns:**
- "Tibetan singing bowl for meditation"
- "mala beads for mantra practice"
- "thangka painting Drikung Kagyu"
- "108-bead mala for japa meditation"

**Not acceptable:**
- "relaxation sound bowl"
- "spiritual home decor"
- "zen meditation accessories"
- "boho altar piece"
- "mindfulness tools"

---

### Dimension 4 — Cross-Channel Consistency
**Criterion:** The same product tells the same story on Shopify, Etsy, and Amazon. Channel formatting may differ; meaning and framing must not.

| Score | Meaning |
|-------|---------|
| 10 | Identical practice framing, terminology, and provenance across all channels |
| 8-9 | Consistent framing; minor formatting differences only |
| 5-7 | Channel-specific meaning differences; one channel uses different framing |
| <5 | Product positioned differently across channels (e.g., "jewelry" on Etsy, "practice tool" on Shopify) |

**Hard rules:**
- A mala is never described as jewelry on any platform
- A thangka is never "wall art" or "tapestry" on any platform
- A singing bowl is never a "sound bowl" or "relaxation tool" on any platform

---

### Dimension 5 — Specificity
**Criterion:** Provenance, artisan region, and technique are named — not gestured at.

| Score | Meaning |
|-------|---------|
| 10 | Specific artisan region, technique, and material source named and verifiable |
| 8-9 | Specific region or technique named; one element vague but not misleading |
| 5-7 | Generic provenance language ("Himalayan," "traditional") without specifics |
| <5 | No provenance; description could apply to any similar product |

**Examples:**
- "Hand-rolled in Kathmandu by Newari incense makers using juniper harvested from the Helambu valley" — scores 10
- "Handmade in Nepal using traditional techniques" — scores 5
- "Authentic Himalayan craftsmanship" — scores 3

---

## Scoring Record Format

Each queue entry must include:

```json
{
  "rubric_scores": {
    "practice_first_framing": 9,
    "cultural_accuracy": 8,
    "seo_authenticity": 9,
    "cross_channel_consistency": 10,
    "specificity": 8
  },
  "revision_cycles": 1,
  "flagged_terms": [],
  "ai_generated": true
}
```

If any score is <8, the entry must not appear in the queue. If `flagged_terms` is non-empty, the entry waits for `spiritual-director` review before advancing.
