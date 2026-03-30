---
name: etsy-content-optimization
description: Optimize Etsy listings for search visibility using Etsy-specific SEO (titles, 13 tags, descriptions), Buddhist goods category expertise, photography standards, and fee-aware pricing. Load this skill when creating new Etsy listings, optimizing existing ones, analyzing listing performance, or preparing Shopify products for Etsy cross-listing. Phase 1 — all listings require human review before publishing.
version: "0.1.0"
category: ecommerce
tags: [etsy, listings, seo]
author: operations-team
model: sonnet
cacheable: true
estimated_tokens: 2000
phase: 1
depends_on: [shared/brand-guidelines, shared/channel-config, shared/product-knowledge]
external_apis: [supabase, etsy]
cost_budget_usd: 0.15
---

# Etsy Content Optimization

## Purpose

Create and optimize Etsy product listings that rank well in Etsy search, convert browsers to buyers, and accurately represent Tibetan Spirit's authentic Buddhist practice items. Etsy SEO differs significantly from Shopify and Google SEO — this skill encodes the platform-specific rules.

**Key principle**: Never push Shopify-optimized content directly to Etsy. Each channel needs native content optimized for its search algorithm and buyer behavior.

## Etsy SEO Fundamentals

### How Etsy Search Works
Etsy search uses a two-phase process:
1. **Query matching**: Etsy matches the buyer's search terms against listing titles, tags, categories, and attributes
2. **Ranking**: Matched listings are ranked by relevance, listing quality score, recency, and shop quality

Titles and tags are equally weighted for query matching — a keyword in a tag has the same matching power as one in the title. However, titles also appear in Google search results, so they serve double duty.

### Title Optimization (140 Characters Max)

**Rules:**
- Front-load the most important keywords (first 40 characters show in search results)
- Use natural, readable phrases — not keyword spam
- Include: product type + material + key attribute + practice context
- Separate keyword phrases with commas or pipes
- Do not repeat words already in tags (wastes title space)

**Formula**: `[Primary Keyword] [Material/Type] - [Practice Context] - [Key Differentiator] - [Gift/Occasion if relevant]`

**Examples:**
```
GOOD: "Hand-Hammered Singing Bowl, 7 Inch Bronze Meditation Bowl, Buddhist Practice Instrument"
BAD:  "Bowl Singing Bowl Hammered Bowl Bronze Bowl Meditation Bowl" (keyword stuffing)
BAD:  "Beautiful Handmade Bowl for Your Home" (no specific product keywords, frames as decor)
```

**Buddhist goods specific guidance:**
- Lead with the traditional product name: "Mala", "Thangka", "Singing Bowl", not "Prayer Beads Bracelet" or "Tibetan Painting"
- Include the practice context: "Meditation", "Buddhist Practice", "Mantra Counting"
- Include materials: "Bodhi Seed", "Hand-Hammered Bronze", "Block-Printed Cotton"
- Never use: "home decor", "decorative", "zen" as a generic adjective, "boho", "bohemian"

### Tag Strategy (13 Tags Maximum)

Every listing gets exactly 13 tags. Tags are multi-word phrases (up to 20 characters each). Etsy matches tags as phrases, not individual words.

**Tag allocation framework (13 tags):**

| Slots | Category | Examples |
|-------|----------|---------|
| 3-4 | Product type variations | "singing bowl", "meditation bowl", "tibetan bowl", "sound bowl" |
| 2-3 | Material/attribute | "hand hammered", "bronze bowl", "seven metal" |
| 2-3 | Use/practice context | "meditation tool", "buddhist practice", "sound healing" |
| 2-3 | Buyer intent / occasion | "yoga gift", "spiritual gift", "mindfulness gift" |
| 1-2 | Long-tail specific | "7 inch singing bowl", "nepal handmade" |

**Tag rules:**
- Do not repeat exact phrases from the title (Etsy already indexes the title)
- Use all 13 slots — empty slots are wasted visibility
- Phrases, not single words: "meditation bowl" not "meditation"
- No punctuation in tags
- Include common misspellings or alternative terms buyers might search
- Refresh tags quarterly based on Etsy search analytics and seasonal trends

### Description Structure

Etsy descriptions do not directly impact search ranking (Etsy confirmed this), but they significantly impact conversion rate — the buyer reads the description to decide whether to purchase.

**Template:**

```
[Opening paragraph — 2-3 sentences]
What this item IS and its practice context. Connect it to the buyer's intention.

[Details section]
- Material: [specific]
- Size: [dimensions and weight]
- Origin: [workshop/region]
- Includes: [what ships with the product — mallet, cushion, pouch, etc.]

[Practice context paragraph]
How this item is used in Buddhist practice. Brief, educational, respectful.
Read skills/shared/brand-guidelines/SKILL.md for voice and tone.

[Care instructions]
Brief maintenance guidance.

[Shipping and handling]
Processing time, shipping method, packaging.

[About Tibetan Spirit]
2-3 sentences about sourcing, artisan relationships, 5% Dharma Giving commitment.
```

**Do not include**: Etsy shop policies (those go in the shop policy section), return details (shop policy section), keywords stuffed into descriptions.

## Photography Requirements

Etsy is a visual-first platform. Photo quality directly impacts click-through rate and conversion.

### Minimum Requirements
- **First image**: Clean, bright product photo on white or neutral background. This is the search result thumbnail — it must immediately communicate what the product is.
- **Total images**: 5-10 per listing (Etsy allows 10)
- **Resolution**: Minimum 2000px on shortest side
- **Format**: JPG, natural lighting preferred
- **Aspect ratio**: Etsy displays at 4:5 — optimize for this crop

### Recommended Photo Sequence
1. **Hero shot**: Product on clean background, well-lit
2. **Scale reference**: Product in context showing size (in hand, on altar, next to common object)
3. **Detail shot**: Close-up of craftsmanship (hammer marks on bowls, brushstrokes on thangkas, bead detail on malas)
4. **Practice context**: Product in use or displayed in a practice setting (shrine, meditation space)
5. **Alternate angles**: Back, bottom, additional views
6. **Packaging/contents**: What the buyer will receive (bowl + mallet + cushion, etc.)

### Cultural Sensitivity in Photography
- Display items respectfully — on a clean surface, thoughtfully arranged
- Do not place sacred items on the floor or among unrelated commercial objects
- If showing items in a practice context, ensure the setting is authentic and respectful
- Read `skills/shared/brand-guidelines/cultural-sensitivity.md` for full guidelines

## Pricing with Etsy Fees

Etsy's fee structure is complex. Every listing must be priced to maintain target margin after all fees.

### Fee Breakdown

| Fee | Rate | Applied To |
|-----|------|-----------|
| Listing fee | $0.20 | Per listing (charged on creation and every 4-month renewal, or on each sale) |
| Transaction fee | 6.5% | Sale price + shipping price charged to buyer |
| Payment processing | 3% + $0.25 | Sale price + shipping + tax |
| Offsite ads | 12-15% | Attributed sales only (mandatory above $10K/year revenue) |

### Pricing Formula

```
Etsy Price = Shopify Price * (1 + Fee Markup)

Where Fee Markup:
  Without offsite ads attribution: ~10-12%
  With offsite ads attribution:    ~22-27%

Conservative pricing (assume some offsite ads traffic):
  Etsy Price = Shopify Price * 1.15  (15% markup over Shopify)
```

**Decision logic:**
```
IF product Shopify price < $25:
    Etsy markup = 15% (fees eat more at lower price points)
ELIF product Shopify price $25-$100:
    Etsy markup = 12%
ELIF product Shopify price > $100:
    Etsy markup = 10% (absolute fee amount is higher, percentage can be lower)

ALWAYS verify: Etsy price - all fees > COGS * (1 + minimum_margin_floor)
IF margin < margin_floor_by_channel['etsy']:
    FLAG for ceo review — product may not be viable on Etsy
```

Reference `skills/shared/channel-config/SKILL.md` for complete fee structure and cross-channel pricing rules.

## Shop Sections

Organize listings into Etsy shop sections that mirror Tibetan Spirit's product taxonomy:

| Section | Products |
|---------|---------|
| Singing Bowls | All singing bowls, mallets, cushions |
| Malas & Prayer Beads | Full malas, wrist malas, mala accessories |
| Thangkas & Sacred Art | Hand-painted thangkas, prints, mandala art |
| Incense | Sticks, ropes, powder, dhoop, holders |
| Prayer Flags | Lung ta, dar cho, all sizes |
| Statues & Figures | All deity statues, all materials |
| Offering Sets & Ritual Items | Water bowls, butter lamps, dorje, ghanta |
| Gift Sets | Curated collections for gifting |

## Decision Logic: Listing Optimization Workflow

```
1. Is this a new listing or optimization of existing?
   → New: Use full listing creation template (title + 13 tags + description + photos check)
   → Existing: Pull current Etsy analytics first

2. For existing listings, check performance:
   IF impressions < 100/month AND listing age > 30 days:
       → Title and tag refresh needed — research current search terms
   IF impressions > 100 AND click-through < 2%:
       → Photo optimization needed — first image is not compelling
   IF click-through > 2% AND conversion < 1%:
       → Description/pricing optimization — buyers are interested but not purchasing
   IF conversion > 1%:
       → Listing is performing well — minor optimization only

3. For all listings, verify:
   - No cultural anti-patterns in any text (read brand-guidelines/cultural-sensitivity.md)
   - Practice context is primary framing (not decorative/commercial)
   - Pricing includes Etsy fee markup over Shopify base
   - All 13 tags are populated
   - Minimum 5 photos uploaded
```

## Phase 1 Behavior

All Etsy listing changes require human approval before publishing:

- **New listings**: Draft complete listing (title, tags, description, pricing, photo list) and queue for ceo's review in dashboard
- **Title/tag changes**: Show current vs. proposed with rationale. Queue for approval.
- **Pricing changes**: Show Shopify base, Etsy fee calculation, proposed Etsy price, projected margin. Queue for ceo's approval.
- **Description edits**: Show diff. Queue for approval.
- **Never publish directly** — all changes go through the approval queue

Graduation to Phase 2 (after 200+ successful listing optimizations with <2% revert rate): auto-publish tag and description updates. Title and pricing changes remain Phase 1 (human approval).

## Model Routing

- **Keyword research and tag generation**: Haiku 4.5 (structured data task, pattern matching)
- **Title writing**: Sonnet 4.6 (requires balancing SEO with brand voice and cultural sensitivity)
- **Description writing**: Sonnet 4.6 (requires nuanced brand voice, practice context framing)
- **Performance analysis and optimization recommendations**: Sonnet 4.6 (requires analytical judgment)

## Output Format

For each listing optimization, produce:

```json
{
  "action": "create | optimize",
  "shopify_product_id": "if cross-listing",
  "etsy_listing_id": "if optimizing existing",
  "title": "optimized 140-char title",
  "tags": ["tag1", "tag2", "... up to 13"],
  "description": "full description text",
  "shop_section": "section name",
  "pricing": {
    "shopify_base": 0.00,
    "etsy_fee_markup_pct": 0.00,
    "etsy_price": 0.00,
    "estimated_margin_after_fees": 0.00
  },
  "photo_checklist": {
    "hero_shot": true,
    "scale_reference": true,
    "detail_shot": true,
    "practice_context": true,
    "total_photos": 0
  },
  "optimization_notes": "rationale for key decisions",
  "requires_approval": true
}
```

## Dependencies

- **References**: `skills/shared/product-knowledge/SKILL.md` (product details), `skills/shared/brand-guidelines/SKILL.md` (voice/tone), `skills/shared/channel-config/SKILL.md` (fees and pricing rules)
- **Referenced by**: `skills/ecommerce/cross-channel-parity/SKILL.md` (parity checks include Etsy content)
