# Tibetan Spirit — Review Checklist (Updated 2026-04-17)

**Status:** Awaiting Chris's review before agent proceeds with updates
**Handoff:** `workspace/plans/2026-04-17-v8-model-updates-handoff.md`

---

## Assumptions to Confirm FIRST

These questions must be answered before the update agent begins work. They are listed in priority order — blocking items first.

### Product Line Structure

- [ ] **Full product line list for forecasting.** Chris started the list: "Shrine Items, Incense, Malas, ..." — what are the remaining lines? Suggested groupings based on 2025 Shopify data ($116K total):

  | Proposed Line | 2025 Revenue | % | Includes |
  |---|---|---|---|
  | Incense & Consumables | ~$30K | 26% | Incense Sticks, Powdered Incense, Incense accessories |
  | Shrine Items (Core, <$1K) | ~$40K+ | 35%+ | Singing Bowls, Thangkas, Statues, Ritual Objects, Prayer Flags, etc. |
  | Malas | ~$13K | 11% | Full Malas, Wrist Malas, Mala Counters, Mala Bags |
  | Shrine Items (Premium) | $0 | 0% | NEW — Kathmandu-sourced rare/antique items |
  | Other | ~$23K+ | 20%+ | Books, Texts, Pendants, Amulets, Katag, Robes, etc. |
  | Uncategorized ("None") | ~$15K | 13% | What are these? Need classification |

- [ ] **What is the "None" category?** $14,692 in 2025 revenue is uncategorized in Shopify. What products are these?
- [ ] **Should each product line have its own growth rate and COGS?** (e.g., Incense has 22% COGS vs Shrine Items at 33%) Or should we keep blended COGS and just show the revenue split?

### Team & Roles

- [ ] **Kathmandu Operations Manager — who is this person?** Named hire or TBD?
- [ ] **Jothi's updated title.** The deal proposal currently lists Jothi as "Operations Manager" in Southeast Asia. With the new Kathmandu hire taking that title, what is Jothi's role? (e.g., "Logistics Coordinator", "Supply Chain Manager"?)
- [ ] **Ops Manager salary.** What is the Kathmandu Ops Manager's monthly cost? This changes the personnel budget starting Month 1.

### Financial Model

- [ ] **Personnel double-count check.** Current personnel budget: $6,833/mo for M1-M4. Dr. Lye's $3K/mo seller payout is a SEPARATE line item. Confirm the $6,833 does NOT include Dr. Lye — otherwise we're double-counting $36K/yr.
- [ ] **Marketing learning period.** July-September 2026 is very low ad spend (team learning ROAS). What fraction of standard? Suggested: 25% of normal rate. OK?
- [ ] **Holiday 2026 multiplier.** Chris said 1-1.5x standard. Model at 1.25x?
- [ ] **How many payment options for Dr. Lye/investor?** Suggested 4 options (see handoff Change 6). Enough?

---

## Current Deliverables — What's Right, What Needs Updating

### 1. Financial Model v7 (→ v8)

**File:** `deliverables/outputs/docs/ts-financial-model-v7-2026-04-16.xlsx`
**Config:** `scripts/financial_model/config/model_v7.yaml`

**What's right (keep):**
- [x] 36-month projection structure (June 2026 - May 2029)
- [x] COGS at 30% blended (validated against product sheet)
- [x] D2C / TS Travels full separation
- [x] Channel scenario toggles (Shopify Only → Full Business)
- [x] Capital structure ($350K ops capital + $30K Truist CD)
- [x] Foundation giving (10% of profitable months)

**What needs updating:**
- [ ] **Product line breakouts** — Revenue split by product line (Shrine Core, Shrine Premium, Incense, Malas, etc.), not just by channel
- [ ] **Product-line-specific COGS** — Incense ~22%, Shrine Items ~33%, Premium tier ~40-60%
- [ ] **Ops Manager joins June 2026** — Personnel costs change: add Kathmandu OM salary from M1. Remove "CS hire in October" framing.
- [ ] **Marketing ramp** — M1: $0, M2-M4: learning rate (~25% of standard), M5+: full rate. Holiday 2026: 1.25x (not 2x).
- [ ] **Date labels** — Xlsx should show "Jun 26", "Jul 26" etc. (already does). But Assumptions tab text should say "June 2026" not "Month 1".
- [ ] **Seller payment options** — Model the P&L impact of each payment structure option
- [ ] **Premium tier revenue** — Reframe "High-Value Dropship" as "Shrine Items (Premium)" with updated ramp reflecting Kathmandu relationship-building time

### 2. Deal Proposal v2 (→ v3)

**File:** `deliverables/outputs/docs/ts-deal-proposal-v2-2026-04-16.md`

**What's right (keep):**
- [x] Overall tone — warm, honest, accessible
- [x] Secured promissory note / UCC-1 structure
- [x] D2C / Travels separation in revenue tables
- [x] Monk ordination framing (respectful, well-placed)
- [x] "Range of Outcomes" section
- [x] Tax considerations section

**What needs updating:**
- [ ] **Section 3, Year 1 plan:** Replace "CS hire (October 2026)" with Kathmandu Operations Manager joining June 2026. Add the premium sourcing initiative as a major Y1 activity.
- [ ] **Section 3, Year 1 plan:** Advertising starts July 1 with 3-month learning period, not big marketing push from day one. Revise the marketing narrative.
- [ ] **Section 3, Year 1 plan:** Holiday 2026 is modest (1-1.5x), not aggressive.
- [ ] **Section 5 (Team table):** Replace "CS Hire (Oct 2026)" row with Kathmandu Operations Manager. Clarify Jothi's updated role.
- [ ] **Section 6 (Deal structure):** Replace single $270K payment structure with options table for Hun and investor to choose between.
- [ ] **Revenue tables:** Update with v8 model numbers after product line restructuring.
- [ ] **All date references:** Replace "month 3", "month 13" etc. with "August 2026", "June 2027".
- [ ] **Growth narrative:** Add the Kathmandu premium sourcing as a strategic differentiator — this is significant and currently missing entirely.

### 3. Tax & Legal Checklist

**File:** `deliverables/outputs/docs/ts-tax-legal-checklist-2026-04-16.md`

**What's right (keep):**
- [x] 3-tier structure (Must-Do / Should-Do / Administrative)
- [x] Form 8594 guidance
- [x] Seller payout characterization analysis
- [x] Inventory facility definition
- [x] Documents needed from attorney

**What needs updating:**
- [ ] **Deal Summary table:** Update to reflect payment options (not a single structure)
- [ ] **Item 2 (Seller Payout):** Expand to address tax implications of each payment option (upfront vs installment vs hybrid). Different options have different capital gains / ordinary income treatment.
- [ ] **Item 4 (Promissory Note):** Update to reflect that this is one of several options, not the decided structure.
- [ ] **Add a new section:** "Seller Payment Structure Options" with a table showing each option and its tax implications for both parties.

### 4. Vision Deck

**File:** `deliverables/outputs/decks/ts-vision-deck-2026-04-15.md`

**What needs updating (full refresh):**
- [ ] **Slide 2 (What We Have Today):** Update metrics — $7,500/mo (not $8,500), 30% COGS (not 24.8%), ~$75 AOV (not $134 — confirm this change from v6 to v7 is accurate)
- [ ] **Slide 5 (Revenue Trajectory):** Replace v6 numbers ($173K/$773K/$1.24M) with v8 model output
- [ ] **Slide 6 (Path to Profitability):** Update EBITDA and cash — v8 will differ from both v6 and v7 due to marketing timing changes
- [ ] **Slide 7 (Channel Strategy):** Add product line view alongside channel view. Replace "M3", "M13" with calendar dates.
- [ ] **Slide 8 (Growth Roadmap):** Replace "M1-M12", "M13-M24" with calendar date ranges. Add Kathmandu premium sourcing initiative.
- [ ] **Slide 12 (Team):** Add Kathmandu Operations Manager, update Jothi's role
- [ ] **Slide 10 (Capital Requirements):** Update if Y1 marketing number changes
- [ ] **Slide 11 (Range of Outcomes):** Update with v8 scenarios
- [ ] **All slides:** Replace all "M3", "M13" etc. with "August 2026", "June 2027"

---

## Review Order (Updated)

1. **Confirm assumptions above** — these block everything else
2. **Review the handoff document** at `workspace/plans/2026-04-17-v8-model-updates-handoff.md` — anything missing?
3. Agent executes updates (model → docs → deck, in parallel where possible)
4. Chris reviews updated deliverables

---

## Open Questions for After Updates

- [ ] Should we present BOTH a conservative (30% COGS) and moderate (25% COGS) scenario in the deal proposal?
- [ ] Is the $100K inventory facility cap still right given the premium tier addition?
- [ ] Does the premium tier need its own inventory facility terms (items may be $2K-$10K each)?
- [ ] Due diligence research agent (future session): benchmark assumptions against market data
