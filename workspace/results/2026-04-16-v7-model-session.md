# Session Capture: v7 Financial Model & Deal Docs Sprint
**Date:** 2026-04-16
**Scope:** tibetan-spirit-ops

## What Happened

Executed 6-task implementation plan for the v7 financial model and deal document refresh. All tasks completed and merged to main.

### Deliverables Produced
1. **v7 YAML config** (`scripts/financial_model/config/model_v7.yaml`) — all assumptions in one file
2. **Python model engine** (`scripts/financial_model/model.py`) — 36-month P&L with channel projections, 32 tests passing
3. **7-tab xlsx workbook** (`deliverables/outputs/docs/ts-financial-model-v7-2026-04-16.xlsx`) — ready for Google Sheets upload
4. **Deal proposal v2** (`deliverables/outputs/docs/ts-deal-proposal-v2-2026-04-16.md`) — secured note, UCC-1, monk ordination framing
5. **Tax/legal checklist** (`deliverables/outputs/docs/ts-tax-legal-checklist-2026-04-16.md`) — 8 items, 3 tiers, 7 docs from attorney
6. **Review plan** (`workspace/plans/review-plan-2026-04-16.md`) — Chris's review checklist for all deliverables

### Key Finding: COGS Validated
Cross-referenced `~/Downloads/TS Product Lines.xlsx` against tibetanspirit.com live listings. The sheet's "65%" column was **gross margin**, not COGS. Actual blended product COGS is ~31%. The model's 30% is confirmed as slightly conservative. Memory saved at `project_ts_cogs_validated.md`.

### v7 vs v6 Key Changes
- COGS: 30% (was 24.8%)
- Starting D2C: $7,500/mo (was $8,500)
- D2C AOV: ~$75 (was $134)
- Y3 EBITDA: -$57K conservative (was +$76K in v6)
- D2C and TS Travels fully separated

### Incident: Lost Worktree Commits
All work was committed on a branch inside a worktree that was cleaned up, deleting the branch. Recovered 6 commits from git reflog and fast-forward merged into main.

## ACT NOW Items

1. **Chris: Review all 4 deliverables** — follow review plan at `workspace/plans/review-plan-2026-04-16.md`
2. **Vision deck needs v7 update** — still uses v6 numbers, update after Chris's review
3. **Due diligence research agent** — benchmark v7 assumptions against market data (future session)
4. **Key decision pending**: whether to present conservative case alongside a moderate scenario, or adjust assumptions for Y3 positive
