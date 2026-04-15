# Tibetan Spirit — Growth Roadmap
**Date:** 2026-04-14
**Goal:** $100-200k → $1-2M annual revenue
**Constraint:** No heavy advertising, no urgency tactics, no tactics that compromise spiritual positioning

---

## Strategic Growth Engines

### Engine 1: Subscription ARR — The Quarterly
A curated quarterly box built around Dr. Hun Lye's seasonal practice letters. No comparable competitor has this.

**Box contents:**
- Curated premium incense (selected for the practice season)
- Handwritten-style letter from Dorje Lopon Dr. Hun Lye on the upcoming dharma season
- Small artisan piece (1-of-a-kind from Kathmandu network partners)
- Printed catalog of available 1-of-a-kind offerings from the dharma shop network

**Revenue model:**
- Target: 500 subscribers × $100/quarter = $200k ARR
- Scale: 2,000 subscribers × $100/quarter = $800k ARR
- Lower CAC per LTV vs. one-time buyers; deepens community relationship

### Engine 2: Etsy Channel Expansion
Etsy's algorithm surfaces handmade/spiritual goods to practitioners who don't yet know tibetanspirit.com exists. Etsy acquires, Shopify converts to loyal customers.

**Why Etsy (not Amazon):**
- Practitioners actively browse Etsy for authentic spiritual goods
- Etsy Ads are keyword-targeted, not algorithmic pressure — brand-safe
- Etsy → email list → Shopify → subscription is the natural funnel
- Amazon dilutes brand positioning; Etsy amplifies it

### Engine 3: Wholesale + Dharma Community Channels
Dharma centers, retreat centers, meditation studios buy in bulk and provide context-native endorsement. Dr. Hun Lye's lineage connections are warm-door distribution that already exists.

---

## Future Agents & Skills to Build

These are NOT in the current sprint. Build after the agent/skill rewrite is complete.

### P0 — Subscription Infrastructure
| Component | Type | Purpose |
|-----------|------|---------|
| `subscription-manager` | Agent | Quarterly box lifecycle: curation, subscriber management, renewal tracking, churn detection |
| `quarterly-letter` | Skill | Format Dr. Hun Lye's practice notes → email + print-ready PDF template |
| `catalog-print` | Skill | Generate quarterly printed catalog from active 1-of-a-kind inventory |

### P1 — Etsy Channel
| Component | Type | Purpose |
|-----------|------|---------|
| `etsy-sync` | Agent | Sync Shopify listings → Etsy, manage Etsy messages, Etsy-specific copy variants |
| `etsy-optimization` | Skill | Etsy-specific SEO, tag optimization, Etsy Ads brief generation |

### P2 — Content & Community
| Component | Type | Purpose |
|-----------|------|---------|
| `seasonal-planning` | Skill | Buddhist calendar → content/product calendar (Losar, Saga Dawa, Vesak, Q4) |
| `practice-guide-writer` | Skill | Long-form SEO content: practice guides, product education articles |
| `wholesale-pipeline` | Skill | B2B inquiry handling, wholesale price sheets, dharma center outreach templates |

### P3 — Optimization
| Component | Type | Purpose |
|-----------|------|---------|
| `subscriber-ltv` | Skill | Churn prediction, upsell moment identification, reactivation triggers |
| `channel-profitability` | Skill | Compare Shopify vs Etsy vs Wholesale margin by channel |

---

## Implementation Sequence

1. **Now (current sprint):** Rewrite all 6 agents + 2 skills to OB2 standards
2. **Next sprint:** Build P0 subscription infrastructure (subscription-manager agent + quarterly-letter skill)
3. **Sprint +2:** Etsy channel (etsy-sync agent + etsy-optimization skill)
4. **Sprint +3:** Content engine (seasonal-planning + practice-guide-writer)
5. **Sprint +4:** Wholesale pipeline + subscriber LTV optimization

---

## Reference Notes
- DEV-PLAN.md contains the technical architecture for the agent layer
- Dr. Hun Lye's seasonal letters are the unique differentiator — protect this relationship carefully
- Etsy requires separate API integration (not currently in the Shopify MCP stack)
- Subscription fulfillment logistics (Jothi coordination) is the operational constraint to solve first
