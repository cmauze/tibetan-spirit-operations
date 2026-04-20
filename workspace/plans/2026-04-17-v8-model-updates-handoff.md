# Handoff: v8 Model & Deal Docs Updates

**Date:** 2026-04-17
**For:** New agent session
**Context:** The v7 financial model, deal proposal v2, tax/legal checklist, and vision deck were completed on 2026-04-16. Chris has reviewed them and provided corrections and new information that require updates across all deliverables. This handoff captures everything needed to execute those updates.

---

## What Exists Today

| Deliverable | Path | Status |
|---|---|---|
| Financial model config | `scripts/financial_model/config/model_v7.yaml` | Needs restructuring → v8 |
| Model engine | `scripts/financial_model/model.py` | Needs product-line-level revenue support |
| XLSX builder | `scripts/financial_model/build_xlsx.py` | Needs product line tabs, date format fix |
| Unit tests | `tests/test_model_v7.py` | 32 tests passing, will need updates |
| Deal proposal v2 | `deliverables/outputs/docs/ts-deal-proposal-v2-2026-04-16.md` | Needs corrections below |
| Tax/legal checklist | `deliverables/outputs/docs/ts-tax-legal-checklist-2026-04-16.md` | Needs payment options added |
| Vision deck | `deliverables/outputs/decks/ts-vision-deck-2026-04-15.md` | Still uses v6 numbers, needs full refresh |
| COGS validation | Memory at `project_ts_cogs_validated.md` | 30% COGS confirmed accurate |

**Key reference files:**
- Product line COGS data: `/Users/chrismauze/Downloads/TS Product Lines.xlsx`
- Deal structure analysis: `deliverables/outputs/docs/deal-structure-analysis-2026-04-15.md`
- v6 extract (for comparison): `data/financial-model/v6-extract-2026-04-15.json`

---

## Change 1: Operations Manager, Not CS Hire

**Current state:** The model and deal docs reference a "CS hire" joining October 2026.

**Correction:** This role is the **Operations Manager**, joining **June 2026** (Month 1, not Month 5). He will also handle CS responsibilities, but his primary role is operations. He will be located in **Kathmandu, Nepal** — not the US.

**Where to update:**
- `model_v7.yaml`: Personnel timing — the Ops Manager cost starts Month 1, not Month 5. Revisit the M1-M4 vs M5-M12 personnel split.
- Deal proposal v2, Section 5 ("Who's Running This"): Replace "CS Hire (Oct 2026)" with the Kathmandu-based Operations Manager joining June 2026. Update the table and description. Note: Jothi is listed as current "Operations Manager" in the deal proposal — clarify whether Jothi's title changes or whether there are now two ops roles. Chris's note says "our Operations Manager" will be in Kathmandu; the deal proposal currently lists Jothi as Operations Manager in Southeast Asia.
- Vision deck, Team slide: Same update.

**IMPORTANT — Confirm with Chris before proceeding:** What is Jothi's updated role title if the new Kathmandu hire is "Operations Manager"? Is the new hire a named person or TBD?

---

## Change 2: Kathmandu Premium Product Line (New Business Initiative)

**What it is:** The Kathmandu-based Operations Manager will establish relationships with local vendors who carry high-end statues and other items in their Kathmandu shops. He will:
1. Find vendors and improve the core supply chain for existing lower-priced items
2. Photograph and list high-end items found in Kathmandu shops
3. After a customer orders, purchase and drop-ship directly from Kathmandu to the customer

This creates a **two-tier product structure**:
- **Core Product Line**: Items currently sold and planned, generally <$1K (what exists today)
- **Rare/Antique/Premium Tier**: High-end items sourced from Kathmandu shops, photographed and listed, drop-shipped after order

**Timeline:** This initiative begins immediately in June 2026 but takes time to build — positioning as a high-end supplier requires relationship building, photography infrastructure, and brand credibility in the premium market. Revenue from this line should ramp slowly.

**Note:** The current model already has a "High-Value Dropship (Kathmandu)" channel starting Month 13 at $3K AOV. This is conceptually the same line but needs to be reframed as the "Rare/Antique/Premium" tier rather than a separate channel. Consider whether it should start earlier (the Ops Manager begins sourcing in June 2026, even if first sales come later) and whether the ramp needs adjustment given the relationship-building time.

**Where to update:**
- `model_v7.yaml`: Reframe the dropship channel config. Consider earlier start with slower ramp.
- Deal proposal v2: Add this initiative to Year 1 plan and growth narrative. This is a significant strategic differentiator worth highlighting.
- Vision deck: Add to growth roadmap and channel strategy.

---

## Change 3: Product Line Revenue Breakouts

**Current state:** The model projects revenue by **channel** (Shopify, Etsy, Amazon, etc.). Chris wants revenue also broken out by **product line** for forecasting.

**Product lines for forecasting (CONFIRM WITH CHRIS — the list was incomplete):**
- Shrine Items — Core (<$1K, current catalog)
- Shrine Items — Rare/Antique/Premium (new Kathmandu sourcing)
- Incense (consumables)
- Malas
- [Additional lines TBD — Chris trailed off. Ask before proceeding.]

**2025 Shopify revenue data for calibrating product line splits ($116,536 total, non-Bhutan trips):**

| Proposed Line | Product Types (from Shopify) | 2025 Revenue | % of Total |
|---|---|---|---|
| **Incense** | Incense Sticks ($21,614), Powdered Incense (est. ~$8,500), Incense accessories ($205) | ~$30,300 | ~26% |
| **Malas** | Full Malas ($9,571), Wrist Malas ($1,453), Mala Counters ($970), Mala Bags ($853) | ~$12,850 | ~11% |
| **Shrine Items (Core)** | Singing Bowls, Thangkas ($2,508), Mandalas ($2,251), Kapalas & Spoons ($1,423), Phurbas & Driguks ($1,382), Bhumpa ($1,335), Vajra ($757), Kangling ($722), Tingshak ($482), Conch ($460), Prayer Wheel ($433), Shrine Fabrics ($327), Offering Plates ($283), Stupa ($204), Ritual Arrow ($941), Melong ($894), Other Ritual Items ($1,288), Tormas ($335+$125), Prayer Flags (est. ~$8,500) | ~$40,000+ | ~35%+ |
| **Other** | Amulets ($1,983), Katag ($1,913), Pecha Cover ($1,845), Books ($1,340), Pendants ($1,221), Dharma Bags ($440), Robes ($423), Practice Texts ($459), Tea ($133), Perfume ($116), Pouches ($93), Stamps ($72), Wearables ($52), Donations ($62), "None" category ($14,692) | ~$23,000+ | ~20%+ |
| **Shrine Items (Premium)** | Not in 2025 data — new line starting 2026 | $0 | 0% |

**Note on data gaps:** The user's pasted data starts at "Thangka $2,508" — the top revenue items (Incense Sticks $21,614, "None" $14,692, Full Malas $9,571, Powdered Incense, Prayer Flags, Singing Bowls) are visible in the screenshot chart but exact values for Powdered Incense, Prayer Flags, and Singing Bowls weren't in the pasted text. Estimated from chart visual. The "None" category ($14,692) is uncategorized — ask Chris what these are.

**Shopify query for non-Bhutan trip revenue:**
```
FROM sales
  SHOW total_sales
  WHERE product_type != 'Deposit'
    AND product_type != 'Payment'
  GROUP BY product_type WITH TOTALS
  DURING last_year
```
The `product_type` filter for Deposits and Payments removes Bhutan trip revenue. Additionally, trip products had "bhutan" in the title, but the payment type filter is more complete (captured additional payments not linked to Bhutan product titles). At least $30K was also collected in cash on the first trip day for expenses and tips.

**Architecture decision needed:** The current model engine (`model.py`) projects by channel, not by product line. Adding product-line-level projections requires deciding:
1. Should product lines be modeled independently with their own growth rates and COGS? (More accurate, more complex)
2. Or should the channel-level model stay and product line splits be applied as percentage allocations? (Simpler, less accurate)

Chris's intent seems to be option 1 for at least the Premium tier (different COGS, different ramp). Confirm approach before implementing.

---

## Change 4: Advertising Timing and Holiday Spend

**Current state:**
- Marketing starts Month 1 (June 2026) as a percentage of product revenue
- Q4 multiplier: 2.0x during Oct-Jan
- Y1 marketing: 63% of product revenue

**Corrections:**
1. **Advertising begins July 1** (Month 2, not Month 1). June is setup/onboarding only — zero ad spend.
2. **July-September (Months 2-4): Very small ad spend.** This is a 3-month learning period for the team and agents to understand ad platforms, learn how to dial in ROAS, etc. Model this as a fraction of the normal rate (suggest 25-33% of standard, confirm with Chris).
3. **Holiday 2026 (Oct-Dec): 1.0-1.5x standard** (NOT 2x+). The team is too new to go big on the first holiday season. Model at 1.25x.
4. **Holiday Y2 and Y3: Bigger spending** — the 2.0x multiplier is fine for years 2 and 3.

**Impact:** This should significantly reduce Y1 marketing spend and improve Y1 EBITDA. The current model shows $110K marketing in Y1 — with delayed start and lower holiday boost, this could drop to ~$60-80K.

**Where to update:**
- `model_v7.yaml`: Add monthly-level marketing overrides or ramp schedule. The current config only supports yearly pct — the model engine may need a monthly marketing schedule to handle the July start and learning period.
- `model.py`: May need to support a marketing ramp schedule (e.g., M1: 0%, M2-4: 0.20, M5-M9: 0.63, M10-12: 0.63*1.25) instead of a flat annual pct.
- `build_xlsx.py`: Update Assumptions tab to reflect the new marketing schedule.
- Deal proposal v2: Update the marketing narrative — the $110K Y1 figure will change.
- Vision deck: Update financial tables.

---

## Change 5: Date Formatting — "Month Year" Not "Month N"

**Current state:** Documents reference "M3", "M13", "Month 13", etc.

**Correction:** Always use calendar date format: "August 2026" not "M3" or "Month 3". Since the model starts June 2026:

| Model Month | Calendar Date |
|---|---|
| M1 | June 2026 |
| M3 | August 2026 |
| M4 | September 2026 |
| M7 | December 2026 |
| M13 | June 2027 |
| M25 | June 2028 |

**Where to update:** All deliverables — deal proposal, tax checklist, vision deck, xlsx assumptions tab, and review plan. The YAML config can keep numeric months internally, but all human-readable output should use "Month Year" format.

---

## Change 6: Seller Payment Options (Dr. Hun Lye)

**Current state:** The deal proposes a single structure: $3,000/mo × 60 months + $1,500/mo × 60 months = $270K secured promissory note.

**Update:** Present **multiple payment structure options** for Dr. Hun Lye and the investor to choose between:

| Option | Structure | Total to Seller | NPV (approx) |
|---|---|---|---|
| A | $300,000 upfront at closing | $300,000 | $300,000 |
| B | $90,000 upfront + $36,000/yr × 5 years + $18,000/yr × 5 years | $360,000 | Lower |
| C | Current: $0 upfront + $3,000/mo × 60 + $1,500/mo × 60 | $270,000 | Lowest |
| D | [Other combos — suggest 1-2 more blends] | Varies | Varies |

**Key considerations to present alongside the options:**
- Upfront payment requires more capital at closing but eliminates ongoing obligation
- Deferred payment preserves operating cash but creates long-term liability
- Tax implications differ: upfront vs installment sale treatment (reference tax checklist Item 2)
- Dr. Hun Lye's preference may depend on his ordination timeline
- Investor's preference depends on capital availability and risk tolerance

**Confirm with Chris:** $36K/yr is currently in the model as `seller_payout.monthly_y1_5: 3000`. Is Dr. Lye's salary already captured as a **separate** line item in the personnel costs? The current model has it ONLY as `seller_payout` ($3K/mo). It should NOT be double-counted. If the personnel budget ($6,833 M1-M4) already includes Dr. Lye's $3K, then the model is double-counting.

**Where to update:**
- Deal proposal v2, Section 6: Replace the single payment structure with an options table. Frame as "the following options are presented for discussion."
- Tax/legal checklist: Add a note about how each option affects tax treatment (installment sale eligibility, capital gains vs ordinary income timing).
- Financial model: The model should show the P&L impact of each option (Option A requires $300K at closing vs $3K/mo ongoing). Consider adding a sensitivity toggle.

---

## Change 7: Confirm Dr. Lye's Salary in Model

Chris asks: "Dr Lye's salary ($36k) is included in the current financial model of the business as salary expense, right?"

**Current model answer:** Yes — `costs.seller_payout.monthly_y1_5: 3000` ($36K/yr) is included as a separate operating expense line item called "Seller Payout." It is NOT inside the personnel budget.

Verify there is no double-counting: the personnel costs (`monthly_m1_to_m4: 6833`, etc.) should NOT include Dr. Lye's $3K. If they do, the model over-counts by $36K/yr.

---

## Execution Order

The agent should proceed in this order:

1. **Confirm product lines and open questions with Chris** before touching any files:
   - Full product line list for forecasting (Chris's list was incomplete: "Shrine Items, Incense, Malas, ...")
   - What is the "None" category ($14,692 in 2025 data)?
   - Jothi's role title now that the Kathmandu hire is "Operations Manager"
   - Is the Kathmandu Ops Manager a named person or TBD?
   - Personnel budget: does $6,833 M1-M4 include Dr. Lye's $3K or not?
   - Marketing learning-period spend level (suggested 25-33% of standard)
   - How many payment options to present (suggested 4)

2. **Update model config and engine** (can parallelize model changes):
   - Product line restructuring in YAML
   - Marketing ramp schedule support in model.py
   - Date formatting in build_xlsx.py
   - Re-run tests, fix any failures

3. **Regenerate xlsx** with updated model

4. **Update deal proposal v2** → v3:
   - Ops Manager correction
   - Kathmandu premium line narrative
   - Payment options table
   - Updated financial tables from new model
   - Date formatting
   - Marketing timing narrative

5. **Update tax/legal checklist** with payment options section

6. **Update vision deck** with v8 numbers and all corrections

7. **Update review checklist** (already done below — but refresh after all changes land)

---

## 2025 Revenue Data (Full Dump for Reference)

From Shopify analytics, filtered to exclude Bhutan trip revenue (product_type != 'Deposit' AND product_type != 'Payment'), "last year" = 2025:

**Total: $116,535.53**

Top items (from chart, some values estimated):
- Incense Sticks: $21,613.95
- None (uncategorized): $14,691.77
- Full Malas: $9,570.70
- Powdered Incense: ~$8,500 (from chart)
- Prayer Flags: ~$8,500 (from chart)

Remaining items (from table):
- Thangka: $2,508.26
- Mandala: $2,251.24
- Amulet: $1,982.93
- Katag: $1,913.04
- Pecha Cover: $1,844.69
- Wrist Malas: $1,452.87
- Kapalas & Spoons: $1,422.94
- Phurbas & Driguks: $1,382.09
- Book: $1,340.33
- Bhumpa: $1,334.55
- Other Ritual Items: $1,288.11
- Pendant: $1,220.54
- Mala Counters: $970.04
- Ritual Arrow: $941.32
- Melong: $893.46
- Mala Bags: $852.52
- Vajra: $757.44
- Kangling: $722.45
- Tingshak: $482.01
- Conch: $460.00
- Dharma Bag: $439.86
- Prayer Wheel: $432.50
- Robes: $422.51
- Tormas: $335.36
- Shrine Fabrics: $327.28
- Offering Plates: $282.60
- Practice Texts (Restricted): $239.77
- Practice Texts (Unrestricted): $219.44
- Incense accessories: $205.16
- Stupa: $204.20
- Tea: $133.00
- Torma: $125.00
- Perfume: $115.90
- Pouch: $93.48
- Stamps: $72.13
- Donations: $62.29
- Wearables: $52.20
- Gift Card: $0.00

**Additional data note:** At least $30K was collected in cash on the Bhutan trip for on-ground expenses and tips — this won't appear in Shopify data.
