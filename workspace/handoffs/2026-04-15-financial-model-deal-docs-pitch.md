# Financial Model Completion + Deal Docs + Vision Deck
**Date:** 2026-04-15
**For:** Fresh Claude Code session (Opus recommended)
**Repo:** ~/code/active/tibetan-spirit-ops/

---

## Context

Tibetan Spirit (tibetanspirit.com) is a Shopify D2C store selling Himalayan artisan goods — incense, singing bowls, malas, prayer flags, thangkas, ritual supplies. Acquired from Dr. Hun Lye (Drikung Kagyu lineage). Current revenue ~$20K/mo on Shopify, 559 active products, ~$134 AOV, 30% blended COGS.

A Python financial scenario model already exists at `scripts/financial_model/` with 49 passing tests. It has 7 pure math functions in `analysis.py`, Supabase baseline pull in `baseline.py`, YAML scenario loader in `scenarios.py`, markdown+JSON output in `output.py`, and entry point `run.py`. Five seed scenarios are calibrated against the v6 Excel model.

This handoff has **three workstreams**: (1) finish the financial model, (2) create deal docs for the business owner and investors, (3) create a vision pitch deck.

## Team & Audience

| Person | Role | What they need |
|--------|------|----------------|
| **Chris Mauzé** | CEO / Acquirer | Uses all three deliverables; final approver |
| **Dr. Hun Lye** | Business Owner / Spiritual Director | Deal docs audience — unsophisticated financially, needs to understand and feel comfortable |
| **Chris's investors** | Internal investors | Already bought in. Want to see the vision with zero BS. No hype, no hand-waving. |

---

## Workstream 1: Financial Model Completion

### Current State
- Code exists at `scripts/financial_model/` — 49 tests passing
- 5 seed scenarios in `config/scenarios.yaml` calibrated against v6 Excel
- Baseline pulls live from Supabase (2,240 fulfilled orders, $293K revenue, 559 products, 30% blended COGS)
- Known issue fixed: blended margin time-window mismatch and falsy COGS zero-value bug

### Remaining Work

**1a. Google Sheets Integration**
Enable Chris to edit scenarios in Google Sheets instead of YAML. The YAML file is the source of truth for code, but Chris should be able to:
- View/edit scenarios in a shared Google Sheet
- Pull updated scenarios from the sheet into the model
- This is a convenience layer — the model still runs locally via `python3 scripts/financial_model/run.py`

Consider using `gspread` or a simple CSV export/import. Don't over-engineer — a script that syncs Sheet → YAML is sufficient.

**1b. Baseline Validation Against v6 Excel**
The v6 Excel model is the source of truth that Dr. Hun Lye understands. Before producing deliverables:
- Run the Python model and compare key metrics against the v6 Excel
- Validate: total revenue, blended COGS %, AOV, order volume, margin by category
- Document any discrepancies and their root causes
- The v6 Excel is at: `/Users/chrismauze/Documents/Files/Business/tibetan spirit/` (look for the most recent financial model spreadsheet)

**1c. First Live Model Run**
- Run `python3 scripts/financial_model/run.py` end-to-end
- Verify markdown output at `deliverables/outputs/docs/`
- Verify JSON output at `data/financial-model/`
- Spot-check projection math against hand calculations for 1-2 scenarios
- Generate charts via the `chart-gen` skill if available

---

## Workstream 2: Deal Docs

### Audience
Dr. Hun Lye (business owner) and Chris's investors. Key constraint: **the business owner is fairly unsophisticated financially**. The docs must be high-level, clear, and make him feel comfortable — not intimidated.

### What to Produce

**Investment Proposal / Deal Summary** (1 document, ~5-8 pages)

Structure (adapt, don't copy verbatim from references):
1. **Executive Summary** — What we're proposing, in plain language. One page max.
2. **Business Overview** — What Tibetan Spirit is today: revenue, products, customers, what makes it special. Use the baseline data from the financial model.
3. **Growth Vision** — Where we're taking it: line extensions (the 5 scenarios), channel expansion (Etsy, Amazon, wholesale to dharma centers), subscription model. Reference the financial model projections but present them simply (tables with plain labels, no financial jargon).
4. **Investment & Returns** — What capital is needed, what the expected returns look like at conservative/base/optimistic scenarios. Use sensitivity analysis from the model.
5. **Team & Execution** — Who's doing what. Chris (strategy + AI ops), Dr. Hun Lye (spiritual direction + authenticity), Jothi (operations), existing infrastructure.
6. **Terms Overview** — High-level deal structure. Keep it simple — this is NOT an LOI or legal document. It's a conversation starter.

### Style Guidelines
- Write for someone who runs a small spiritual goods business, not a PE fund
- Plain English. No "EBITDA multiple," no "terminal value," no "IRR"
- Use: "profit margin," "monthly sales," "break-even point," "return on investment"
- Tables over paragraphs for numbers
- When presenting projections, always show conservative alongside base — never just the optimistic case
- Tone: respectful, collaborative, professional but warm

### Reference Materials (for structure inspiration only — NOT tone)
- Attaboy Seed Deck: `/Users/chrismauze/Documents/Files/Business/laurina partners/examples/Attaboy-Seed-Deck.pdf` — good structure for market + product + financials flow, but too VC-oriented for this audience
- VMG/Vacation LOI: `/Users/chrismauze/Documents/Files/Business/laurina partners/examples/Litera Compare Redline - VMG Partners - Vacation Inc. Letter of Intent (Series A Preferred Stock).pdf` — PE growth equity LOI, FAR too complex for this audience. Use only for structural awareness of what a sophisticated deal doc looks like.
- Stars+Honey IC Memo: `/Users/chrismauze/Documents/Claude/Projects/Crane Diligence/Diligence examples/Stars+honey Clean Presentation.pdf` — good "investment merits" table format, risk presentation style
- Vacation IC Memo: `/Users/chrismauze/Documents/Claude/Projects/Crane Diligence/Diligence examples/2026.01.28 Vacation IC.pdf` — good executive summary structure, BETTER/MIXED/UNCHANGED findings framework

### Output
- Save to `deliverables/outputs/docs/ts-deal-proposal-YYYY-MM-DD.md`
- Also generate a clean PDF-ready version (use marp-deck or markdown formatting that converts well)

---

## Workstream 3: Vision Pitch Deck

### Audience
Chris's investors — people who are **already bought in** and want to see the vision. Zero BS. No hype. No "we're disrupting the $82B wellness market." Show them where TS is going with real numbers and clear thinking.

### What to Produce

**Marp slide deck** (~12-15 slides) using the `marp-deck` skill.

Suggested structure (adapt based on what the data actually says):

1. **Title** — Tibetan Spirit: Growth Vision 2026-2028
2. **What We Have** — Current state snapshot: revenue, products, customer base, margins. Real numbers from baseline.
3. **What Makes This Special** — The moat: authentic artisan sourcing, Drikung Kagyu lineage, practitioner audience, Dr. Hun Lye's credibility. Not "we sell meditation stuff" — why THIS business is defensible.
4. **The Opportunity** — Where the whitespace is: line extensions, digital products, subscription, wholesale. Frame through the 5 scenarios.
5. **Financial Model** — Show the scenario comparison table. Side-by-side: what each line extension adds to revenue, margin, breakeven. Use the sensitivity analysis to show range of outcomes.
6. **Growth Roadmap** — Phase 1 ($100-200K → $500K): existing catalog optimization + gift sets + cushions. Phase 2 ($500K → $1M): subscription + courses + Etsy/Amazon. Phase 3 ($1M → $2M): wholesale + brand partnerships.
7. **AI Operations Advantage** — How Chris's AI infrastructure (claude-code agents, automated CS, inventory forecasting) gives TS operational leverage that similar-sized businesses don't have. Be specific — "our CS response time is X" not "we use AI."
8. **Capital Requirements** — What's needed for each phase. Tied directly to the financial model scenarios.
9. **Team** — Chris, Dr. Hun Lye, Jothi, Fiona, Omar. Show the operational team is real and functioning.
10. **Risk & Mitigation** — Be honest. Supply chain (Nepal), single-channel dependency (Shopify), category concentration. Show you've thought about it.
11. **The Ask** — What Chris wants from investors. Clear, direct.

### Style Guidelines
- Data-heavy, narrative-light. Let the numbers talk.
- No stock photos, no clip art, no "inspirational" imagery
- Clean, professional, minimal design
- Every slide should have a "so what" — no slide exists just to fill space
- If a claim can be backed by a number, back it with a number
- Conservative projections with upside scenarios shown as sensitivity ranges

### Reference Materials
- Attaboy Seed Deck: best structural reference. Problem → Solution → Market → Product → Financials → Team → Ask. Adapt the flow but not the VC-pitch tone.
- Stars+Honey IC Memo: good "investment merits" table format for the financial slides

### Output
- Save Marp source to `deliverables/outputs/decks/ts-vision-deck-YYYY-MM-DD.md`
- The marp-deck skill handles conversion to HTML/PDF

---

## Execution Order

1. **Workstream 1 first** — The financial model outputs feed into both the deal docs and the deck. Don't start writing until the model is validated.
2. **Workstream 2 second** — Deal docs force you to articulate the narrative clearly.
3. **Workstream 3 last** — The deck distills the deal docs into visual form.

## Key Data Sources

| Data | Source | How to Access |
|------|--------|---------------|
| Live order/product/COGS data | Supabase | `supabase` MCP plugin or `scripts/financial_model/baseline.py` |
| Scenario projections | Python model | `python3 scripts/financial_model/run.py` |
| v6 Excel baseline | Local file | `/Users/chrismauze/Documents/Files/Business/tibetan spirit/` |
| Brand rules | Repo rules | `rules/brand-voice.md`, `rules/cultural-sensitivity.md`, `rules/marketing-discipline.md` |
| Growth roadmap context | Repo docs | `docs/ARCHITECTURE.md`, prior commit `36ad441` |
| Reference deal docs | Local PDFs | See paths in Workstream 2 reference materials above |

## Constraints

- NEVER fabricate financial data. All numbers come from Supabase baseline or the scenario model.
- NEVER use prohibited marketing language (see `rules/marketing-discipline.md`): no scarcity, no FOMO, no healing claims, no New Age conflation.
- NEVER commit actual financial data to git — projections and scenario configs only.
- All deliverables go to `deliverables/outputs/` (docs, decks, charts subdirectories).
- Use Supabase MCP for live data queries. Do not hardcode.
- The deal docs are a conversation starter, not a legal document. Do not draft legal terms.
- Respect the brand: practice-first framing, cultural accuracy, authenticity over optimization.

## Do NOT

- Do not create a full LOI or term sheet — that's lawyer work
- Do not use VC/PE jargon in the deal docs — the audience won't understand it
- Do not promise specific returns — show ranges and scenarios
- Do not skip the baseline validation step — garbage in, garbage out
- Do not over-design the deck — clean and minimal beats flashy
- Do not conflate the pitch deck audience (sophisticated, bought-in) with the deal doc audience (unsophisticated, needs comfort)

## Success Criteria

- [ ] Financial model runs end-to-end with validated baseline
- [ ] Baseline metrics match v6 Excel within 5% (or discrepancies documented)
- [ ] Google Sheets sync script works for scenario editing
- [ ] Deal proposal is readable by a non-financial business owner
- [ ] Deal proposal presents conservative + base + optimistic scenarios
- [ ] Vision deck has ~12-15 data-backed slides with no filler
- [ ] Vision deck projections tie directly to financial model output
- [ ] All deliverables saved to `deliverables/outputs/`
- [ ] Chris reviews and approves before any external distribution
