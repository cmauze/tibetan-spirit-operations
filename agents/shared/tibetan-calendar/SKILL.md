---
name: tibetan-calendar
description: Tibetan Buddhist liturgical calendar with key dates, seasonal business implications, and marketing/inventory planning triggers. Load this skill when planning marketing campaigns, scheduling promotions, building inventory forecasts, creating seasonal content, or answering customer questions about Buddhist holidays and observances.
version: "0.1.0"
category: shared
tags: [calendar, liturgical, seasonal]
author: operations-team
model: haiku
cacheable: true
estimated_tokens: 1350
phase: 1
depends_on: [shared/brand-guidelines]
external_apis: []
cost_budget_usd: 0.05
---

# Tibetan Buddhist Calendar

## Purpose

Provide accurate dates for major Tibetan Buddhist observances and translate them into actionable business triggers for marketing, inventory, and content planning. This skill is the single source of truth for seasonal planning across all Tibetan Spirit agents.

## 2026 Key Dates

The Tibetan calendar is lunisolar. Gregorian equivalents shift each year. Dates below are based on published Tibetan calendar conversions for the Iron Horse year (2083 in Tibetan reckoning).

| Date (2026) | Observance | Significance | Confidence |
|-------------|-----------|-------------|------------|
| Feb 17 | **Losar** (Tibetan New Year) | New Year celebration. Iron Horse year begins. Major gifting season. | Confirmed |
| Feb 17 - Mar 1 | **Losar period** | 15-day celebration period following New Year | Confirmed |
| Mar 3 | **Chotrul Duchen** | Day of Miracles. First of four great Buddhist festivals. Marks the final day of Losar celebrations. Merit multiplied. | Approximate |
| May 16 - Jun 14 | **Saga Dawa month** | Holiest month in Tibetan Buddhism. The month of Shakyamuni Buddha's birth, enlightenment, and parinirvana. Merit from practice and generosity is multiplied. | Approximate |
| May 31 | **Saga Dawa Duchen** | Full moon of Saga Dawa. The single most sacred day of the year. Birth, enlightenment, and parinirvana of the Buddha. | Approximate |
| Jul 14 | **Chokor Duchen** | Buddha's First Turning of the Wheel of Dharma. Celebrates the first teaching (Four Noble Truths) at Sarnath. | Approximate |
| Nov 11 | **Lhabab Duchen** | Buddha's Descent from Heaven. Celebrates the Buddha's return from teaching his mother in the god realm. | Approximate |

**Approximate dates**: Dates marked "approximate" are based on standard Tibetan calendar calculations but may shift by 1-2 days depending on the specific calendar tradition followed. Cross-check with published Tibetan calendars (e.g., Tibetan calendar from Library of Tibetan Works and Archives) as the year progresses.

### The Four Great Festivals (Duchen)

These four days are when merit from positive actions is believed to be multiplied 10 million times. They are the highest-priority dates for marketing and inventory planning:

1. **Chotrul Duchen** (Mar 3) — Day of Miracles
2. **Saga Dawa Duchen** (May 31) — Buddha's birth, enlightenment, and parinirvana
3. **Chokor Duchen** (Jul 14) — First Teaching
4. **Lhabab Duchen** (Nov 11) — Descent from Heaven

## Decision Logic: Seasonal Business Planning

### Pre-Holiday Triggers

For each major observance, the following timeline applies:

```
6 weeks before: Inventory check — ensure stock levels for seasonal items
4 weeks before: Marketing content creation — email campaigns, social posts, blog content
3 weeks before: Email campaign scheduled — first mention of upcoming observance
2 weeks before: Promotional pricing (if applicable) activated
1 week before:  Reminder email — last chance for pre-holiday delivery
Day of:         Social media post honoring the observance (educational, not sales-focused)
1 week after:   Post-holiday content — continued practice relevance
```

### Seasonal Product Priorities

| Season | High-Demand Products | Marketing Angle |
|--------|---------------------|----------------|
| **Losar (Feb)** | Prayer flags, incense, offering sets, khatas | New year blessings, fresh start for practice, hanging new prayer flags |
| **Saga Dawa (May-Jun)** | Malas, statues, thangkas, offering bowls | Deepening practice, generosity month, merit multiplication |
| **Chokor Duchen (Jul)** | Dharma books, malas, meditation cushions | Study, practice renewal, the Buddha's teaching |
| **Lhabab Duchen (Nov)** | Incense, prayer flags, statues | Devotion, gratitude, year-end practice |
| **Western holidays (Nov-Dec)** | All categories — gifting focus | Meaningful gifts for practitioners (not "Buddhist gifts for non-Buddhists") |

### Content Rules for Holiday Marketing

When creating marketing content around Buddhist observances:

1. **Lead with the observance, not the sale**: "Saga Dawa — the holiest month in Tibetan Buddhism" before any product mention
2. **Educate**: Many Western customers are unfamiliar with the Tibetan calendar. Brief, respectful explanations build trust and community
3. **Do not commercialize sacred dates**: A "Losar Sale" is acceptable (similar to how practitioners buy new prayer flags for the New Year). A "Buddha's Enlightenment Blowout" is not.
4. **Mention the 5% Dharma Giving** during Saga Dawa month — this is when it is most contextually relevant. Frame as genuine spiritual commitment, not sales tactic.
5. **Offer practice context**: "Many practitioners use Saga Dawa month to deepen their mala practice" is more appropriate than "Buy a mala for Saga Dawa."

### Inventory Planning Triggers

When this skill is loaded for inventory planning:

```
IF observance is within 6 weeks:
    Query inventory_extended for seasonal product categories
    IF any SKU below reorder_trigger_qty:
        Flag for immediate reorder (lead times are 2-8 weeks)
        Escalate to operations-manager via WhatsApp (Bahasa Indonesia)
    IF prayer flags below 20 units total:
        ALERT — prayer flags are high-demand before Losar, Saga Dawa, and Lhabab Duchen

IF Losar is within 8 weeks:
    Verify incense stock (Nado varieties especially)
    Verify prayer flag stock (all sizes)
    Verify offering set stock
    This is the single highest-demand period — plan for 2x normal sales volume
```

## Phase 1 Behavior

All seasonal marketing campaigns, promotional pricing, and email sends require human approval before execution:

- **Marketing content**: Draft and queue for ceo's review via dashboard
- **Promotional pricing**: Propose via dashboard approval queue. Never activate discounts automatically.
- **Email campaigns (>500 recipients)**: Require ceo's approval per escalation matrix
- **Inventory reorders**: Propose to operations-manager; they confirm with suppliers
- **Social media posts**: Draft and queue for ceo's review

## Model Routing

- **Date lookups and calendar queries**: Haiku 4.5 (simple retrieval from this reference)
- **Marketing content drafting**: Sonnet 4.6 (needs cultural sensitivity and brand voice)
- **Inventory planning analysis**: Sonnet 4.6 (needs judgment about quantities and timing)

## Output Format

When queried for calendar information, return:

```json
{
  "query_type": "date_lookup | seasonal_planning | inventory_trigger | content_calendar",
  "observance": "name of the observance",
  "date_2026": "YYYY-MM-DD",
  "confidence": "confirmed | approximate",
  "business_actions": [
    {
      "action": "description of recommended action",
      "owner": "ceo | operations-manager | warehouse-manager | system",
      "deadline": "YYYY-MM-DD",
      "priority": "high | medium | low"
    }
  ],
  "content_guidance": "brief note on appropriate tone/framing for this observance",
  "inventory_flags": ["SKU or category alerts if applicable"]
}
```

## Dependencies

- **Referenced by**: marketing agents (campaign timing), operations agents (inventory planning), ecommerce agents (seasonal content), customer-service agents (answering holiday questions)
- **References**: `skills/shared/brand-guidelines/SKILL.md` for content tone, `skills/shared/escalation-matrix/SKILL.md` for approval routing
