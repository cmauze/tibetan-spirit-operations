---
name: product-knowledge
description: Tibetan Spirit product taxonomy, authenticity markers, and category expertise sourced from Dr. Hun Lye. Load this skill when answering product questions, creating product descriptions, evaluating new products for sourcing, or helping customers choose items for their practice. Also load for category management decisions about assortment and pricing.
---

# Tibetan Spirit Product Knowledge

This skill encodes the product expertise of the Tibetan Spirit team, particularly Dr. Hun Lye's deep knowledge of Buddhist sacred items and Jhoti's sourcing experience in Nepal.

## Product Taxonomy

Tibetan Spirit's catalog organizes into these primary categories:

| Category | Avg. Price Range | COGS Range | Key Differentiator |
|----------|-----------------|------------|-------------------|
| Incense | $8–$45 | 15–25% | Monastery-produced, traditional recipes |
| Prayer Flags | $12–$35 | 15–20% | Block-printed, cotton, traditional colors |
| Malas (Prayer Beads) | $18–$120 | 20–30% | Authentic materials, 108-bead standard |
| Singing Bowls | $45–$500+ | 25–35% | Hand-hammered, tonal quality verified |
| Statues | $35–$800+ | 30–40% | Lost-wax casting, hand-finished |
| Thangkas (Paintings) | $25–$2,000+ | 35–50% | Hand-painted vs. high-quality prints |
| Offering Sets | $15–$75 | 25–35% | Practice-specific configurations |
| Ritual Items | $10–$200 | 20–35% | Dorje, ghanta, kapala, etc. |

## Detailed Category References

For deep product knowledge by category, read the relevant reference file:

- `skills/shared/product-knowledge/singing-bowls.md` — Tonal grading, metal composition, size-to-use mapping
- `skills/shared/product-knowledge/thangkas.md` — Hand-painted vs. print, artist traditions, deity identification
- `skills/shared/product-knowledge/incense.md` — Nado Poizokhang varieties, monastery sources, scent profiles
- `skills/shared/product-knowledge/malas.md` — Materials, bead counts, significance by tradition
- `skills/shared/product-knowledge/statues.md` — Casting methods, finish grades, deity identification
- `skills/shared/product-knowledge/prayer-flags.md` — Block printing, color symbolism, sizing

## Authenticity Framework

Every product should be assessable on three dimensions:

1. **Provenance**: Where was it made? By whom? Can we verify the supply chain?
   - Direct Nepal workshop sourcing (highest confidence)
   - Verified supplier with established relationship (high confidence)
   - New supplier, samples validated by Dr. Hun Lye (medium confidence)
   - Unverified wholesale source (low confidence — do not list without validation)

2. **Craftsmanship**: Does the item meet traditional standards?
   - Materials consistent with traditional methods
   - Proportions and iconography follow established canons (especially for statues and thangkas)
   - Finish quality appropriate to the tradition

3. **Practice Alignment**: Is this item genuinely useful for Buddhist practice?
   - Items should serve a real practice function
   - Avoid "Buddhist-themed" novelty items
   - When in doubt, Dr. Hun Lye makes the final call

## Sourcing Network

- **Primary**: Kathmandu Valley workshops (Jhoti manages relationships, quarterly visits)
- **Incense**: Nado Poizokhang monastery (Bhutan), various Kathmandu incense makers
- **Thangkas**: Newari painting workshops in Patan and Bhaktapur
- **Singing Bowls**: Specific smiths in Patan known for traditional seven-metal technique
- **Supplier payments**: NPR (Nepalese Rupee) — tracked in `supplier_payments` table with USD equivalents

## Questions to Escalate to Dr. Hun Lye

- "Is this deity depiction iconographically correct?"
- "Can this item be used for [specific practice]?"
- "Is there a traditional protocol for [using/displaying/disposing of] this item?"
- "A customer is asking about the spiritual significance of [specific item]"
- Any question about Buddhist doctrine or meditation instruction
