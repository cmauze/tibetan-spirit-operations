# Financial Scenario Model — Build Sprint
**Date:** 2026-04-14
**Branch:** feat/financial-scenario-model (create fresh from main)
**For:** Fresh Claude Code session
**Repo:** ~/code/active/tibetan-spirit-ops/

---

## Context

Tibetan Spirit needs a decision tool for line extension analysis — not accounting software.
Chris wants to see what happens to revenue, margin, and required investment when playing
with different product categories, pricing, and volume assumptions.

Current Supabase data: 19,403 orders, 559 products. COGS fields were unpopulated as of
March 2026 — verify current state before building baseline.

## What to Build

Python-based scenario analysis tool at `scripts/financial_model/`:

```
scripts/financial_model/
├── __init__.py
├── baseline.py          # Pull actual data from Supabase, build baseline
├── scenarios.py         # Scenario definition + projection engine  
├── analysis.py          # Comparison, sensitivity, breakeven calculations
├── output.py            # Markdown + JSON output formatters
└── config/
    └── scenarios.yaml   # Editable scenario definitions (Chris edits this)
```

## Baseline Requirements

Pull from Supabase tables: `ts_orders`, `ts_products`, `ts_cogs`
- Period: 2025-01-01 to 2026-04-01 (historical baseline)
- Current product lines, AOV, order volume, margins
- Validate COGS data quality before building projections — flag if unpopulated

Use Supabase MCP to query. NEVER hardcode financial numbers.

## Scenario Engine Requirements

Each scenario in scenarios.yaml defines:
- name, category
- asp (average selling price)  
- cogs_pct (COGS as % of ASP)
- ramp: month_1, month_6, month_12, month_24 (orders/month, linear interpolation)
- upfront_investment: inventory, photography, marketing_launch (or equivalent)
- ongoing_monthly: storage, marketing

## Analysis Requirements

For each scenario, calculate:
- Monthly + annual revenue projections (24 months)
- Blended margin impact on total business
- Breakeven timeline (months to recover upfront investment)
- Total capital required (upfront + working capital)
- Side-by-side comparison table of all scenarios
- Sensitivity: run each at 50%, 75%, 100%, 125%, 150% volume

## Output Format

- `deliverables/docs/financial-model-YYYY-MM-DD.md` — Markdown summary with tables
- `deliverables/charts/` — Charts via chart-gen skill
- `data/financial-model/` — Raw scenario JSON (gitignored)

Deliverables must be scannable by a non-accountant. Use plain language labels.

## Seed Scenarios (populate in scenarios.yaml)

Include 3-5 realistic scenarios for Chris's initial review:
1. Meditation Cushions — physical, ~$85 ASP, 45% COGS
2. Online Dharma Courses — digital, ~$49 ASP, 5% COGS  
3. Incense Gift Sets — bundle extension of existing line, ~$45 ASP, 40% COGS
4. Ritual Supplies Subscription — recurring, ~$35/mo, 35% COGS
5. (Optional) Wholesale to Dharma Centers — B2B, ~$25 AOV, 55% COGS

## Development Approach (TDD)

1. Write tests for projection math first (breakeven, margin blending, sensitivity)
2. Build baseline data pull — validate against known numbers before proceeding
3. Build scenario engine
4. Build comparison + sensitivity output
5. Populate scenarios.yaml and run end-to-end

## Commit Strategy

Branch: `feat/financial-scenario-model`

1. `feat(finance): add baseline data pull from Supabase`
2. `feat(finance): add scenario projection engine`  
3. `feat(finance): add comparison and sensitivity analysis`
4. `feat(finance): add output formatters (markdown + charts + JSON)`
5. `feat(finance): add seed scenarios and documentation`

## Constraints

- Use Supabase MCP for all data queries — NO hardcoded numbers
- All monetary values USD
- Ramp curves interpolate linearly between defined points
- NEVER commit actual financial data — only projections and scenario configs
- NEVER store customer PII in output files
- Run tests after each commit
- Use superpowers:test-driven-development for all new code
- Use superpowers:verification-before-completion before claiming done

## Success Criteria

- `python scripts/financial_model/baseline.py` runs without error
- Baseline numbers match known order history (spot-check against Supabase)
- Scenario projections are mathematically correct (verified by tests)
- Sensitivity analysis produces 5 rows (50%-150%) per scenario
- Markdown output is readable without technical knowledge
- Chris can edit scenarios.yaml and re-run to see updated projections
