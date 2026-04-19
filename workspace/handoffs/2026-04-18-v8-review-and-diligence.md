# Handoff: v8 Model Review + Deal Diligence Follow-up

**Date:** April 18, 2026
**From:** Previous session (v8 model build + deal docs update)
**Branch:** `main` (merged from `feat/v8-model-product-lines`)

---

## What Was Done

Built v8 financial model (product-line-based, replacing channel-based v7) and updated all deal documents. 7 commits, 60/60 tests passing. All changes merged to main and pushed.

Key changes from v7:
- Revenue modeled by product line (Shrine Core 38%, Incense 29%, Malas 19%, Prayer Flags 6%, Other 9%) instead of by channel
- Marketing ramp: M1=0%, M2-M4=33% of standard, M5+=full rate. Y1 holiday=1.25x (not 2x)
- Personnel simplified: flat $6,833/mo Y1 (Jothi is the Ops Manager, no separate CS hire)
- Premium product line added (Kathmandu rare/antique sourcing, M7 start, $3K AOV)
- Payment options: 4 structures (A-D) replacing single $270K deferred
- TS Travels validated: April 2026 Bhutan trip = $97,432 online + ~$50K cash est. = ~$147K (model uses $150K)

---

## Files to Review

### Model Engine
- [ ] `/Users/chrismauze/code/active/tibetan-spirit-ops/scripts/financial_model/config/model_v8.yaml:1` — Product line configs, growth rates, marketing ramp schedule, personnel tiers
- [ ] `/Users/chrismauze/code/active/tibetan-spirit-ops/deliverables/outputs/docs/ts-financial-model-v8-2026-04-17.xlsx` — Open in Excel/Sheets, spot-check Assumptions tab and D2C P&L tab

### Deal Documents
- [ ] `/Users/chrismauze/code/active/tibetan-spirit-ops/deliverables/outputs/docs/ts-deal-proposal-v3-2026-04-17.md:1` — Payment options table (4 options A-D), team table (Jothi = Kathmandu Ops Mgr, no CS hire), product line revenue table, Bhutan trip validation, all calendar dates
- [ ] `/Users/chrismauze/code/active/tibetan-spirit-ops/deliverables/outputs/docs/ts-tax-legal-checklist-2026-04-16.md:16` — Updated payment schedule row + new Section 2a (payment option tax implications)
- [ ] `/Users/chrismauze/code/active/tibetan-spirit-ops/deliverables/outputs/decks/ts-vision-deck-2026-04-17.md:1` — All slides: revenue trajectory, profitability, product line table, growth roadmap with calendar dates, team slide, Bhutan trip validation

### Code (tests cover it)
- [ ] `/Users/chrismauze/code/active/tibetan-spirit-ops/scripts/financial_model/model.py:143` — Marketing ramp, platform fee schedule, simplified personnel, product-line P&L
- [ ] `/Users/chrismauze/code/active/tibetan-spirit-ops/scripts/financial_model/build_xlsx.py:155` — Assumptions tab renders v8 config
- [ ] `/Users/chrismauze/code/active/tibetan-spirit-ops/tests/test_model_v8.py:1` — 28 tests, all passing

---

## Pending: Feedback from Lopon (Dr. Hun Lye)

Deal diligence questions have been sent to Dr. Hun Lye via Google Doc:
**https://docs.google.com/document/d/11aY1FHm2FEqbMjnYTNnnXAyZb2IUlIuLvjXPQqoy-W4/edit?tab=t.0#heading=h.vlsoo0x62f3q**

Reference file: `/Users/chrismauze/code/active/tibetan-spirit-ops/workspace/references/deal-diligence-questions.md:1`

**When responses come back:**
1. Read the Google Doc responses
2. Check whether any answers change assumptions in the v8 model (especially: COGS rates, supplier terms, inventory valuation, trip logistics/pricing)
3. If model assumptions change, update `model_v8.yaml`, re-run `python3 scripts/financial_model/build_xlsx.py`, run tests, and propagate new numbers to deal docs
4. Update the deal proposal and tax checklist with any new information from Lopon's responses
5. Flag anything that affects deal structure or payment option recommendations

---

## Pending: Bhutan Trip Cash Receipts

The model assumes $150K/trip. April 2026 Bhutan trip actuals:
- Online payments: **$97,432** (confirmed)
- Cash receipts: **~$50K estimated** (not yet confirmed)
- Total: **~$147K** (close to $150K model assumption)

**If cash receipts come in lower than $50K:**
1. Update `model_v8.yaml:83` — change `revenue_per_trip` to the actual total
2. Re-run the model: `python3 scripts/financial_model/build_xlsx.py`
3. Run tests: `python3 -m pytest tests/test_model_v7.py tests/test_model_v8.py -v`
4. Update revenue tables in deal proposal v3 (lines 102, 110), vision deck (line 172), and "A note on these numbers" paragraph
5. The TS Travels validation sentence in the deal proposal (line 79) and vision deck (line 174) should be updated with actuals

---

## v8 Model Summary Numbers

| | Y1 | Y2 | Y3 |
|---|---|---|---|
| D2C Revenue | $166,972 | $425,284 | $821,309 |
| Travels Revenue | $0 | $300,000 | $300,000 |
| Total Revenue | $166,972 | $725,284 | $1,121,309 |
| EBITDA | -$156,058 | -$98,759 | +$4,180 |
| Ending Cash | $93,942 | $95,183 | $149,363 |
| Marketing | $94,372 | $248,166 | $317,778 |
| Personnel | $81,996 | $90,000 | $102,000 |

---

## Unrelated Uncommitted Changes

These were on disk before this session and are not part of the v8 work:
- `deliverables/outputs/docs/ts-deal-proposal-v2-2026-04-16.md` — minor edit (CS hire date change)
- `skills/restock-calc/SKILL.md` — modified
- Several untracked workspace plan files
