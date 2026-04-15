# Changelog

All notable changes to tibetan-spirit-ops are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### Added
- 6 agents rewritten to OB2+superpowers standards: CSO descriptions, effort/memory/model frontmatter, scoped tools (Supabase MCP), Common Rationalizations + Red Flags + Verification sections — `680d640`..`fbed06e`
- 2 existing skills (cs-triage, shopify-query) rewritten with references/ extraction — `a0041b4`, `85faaed`
- 6 new Priority 1 skills: order-inquiry, margin-reporting, fulfillment-flag, restock-calc, campaign-brief, description-optimizer — `7cb5cc1`..`e202cda`
- CS pipeline workflow definition (triage → enrichment → draft → approval) — `dbfe50a`
- CCPA enforcement hook (ccpa-gate.sh) blocks direct email sending — `8b903b0`
- HARD-GATE behavioral tag on cs-triage for spiritual guidance escalation — `dd3e4de`
- New frontmatter fields: effort, memory, max-turns, criticalSystemReminder_EXPERIMENTAL
- Growth roadmap ($100-200k → $1-2M) at workspace/plans/GROWTH-ROADMAP.md — `36ad441`

### Changed
- Consolidated agent .metadata.json into YAML frontmatter comment lines — `050198e`, `448f500`
- Updated CLAUDE.md skills/workflows/hooks counts
- Fixed stale workflow references in ARCHITECTURE.md and OPERATIONS-REFERENCE.md
- Scaffolded workspace structure (plans/, results/, handoffs/, archive/) — `b8149d0`
- Consolidated root-level docs (moved DEV-PLAN.md to workspace/plans/, ORG.md to .claude/rules/org-roles.md, archived SYSTEM-STATUS.md, deleted stale validation-report.json) — `9176fff`

### Removed
- Empty workflows/ directory (replaced with cs-pipeline workflow) — `dd3e4de`
- Separate .metadata.json files for agents (consolidated into frontmatter) — `050198e`

---

## [0.5.0] — 2026-04-05

### Added
- Slack notification hook with channel routing (`#ts-operations`, `#system-health`, `#daily-brief`) — `b3f2699`
- Shopify-query skill and CLI tool for agent workflows — `617a9bb`

### Changed
- All 6 agents upgraded to Opus model — `62f2513`
- Hooks centralized to user-level; evals and context injection added to harness — `61300f9`

---

## [0.4.0] — 2026-04-02

### Added
- Claude Code harness layer: agents, hooks, skills, rules, settings — `b1c968c`
- Security hooks, deny rules, and stop verification — `2678665`
- COGS seeding script improvements with better category patterns — `bd926c6`

---

## [0.3.0] — 2026-03-30

### Added
- Three-layer Supabase schema (registry, runtime, eval) + `dashboard_ops.py` — `09b46ab`
- `daily_summary` workflow — first end-to-end workflow — `52771d4`
- `weekly_pnl` workflow with prompt chain and accuracy eval — `3ea817f`
- `claude_client` with skill loading, prompt caching, cost calculation — `8066def`
- Org resolver, notifications, cost tracker, view refresher — `86f231b`
- `notion_ops.py` for wiki/Academy writes and cost log archiving — `feat`
- COGS estimates seeded for 559 products — `9aef8ac`
- Product margins updated from supplier spreadsheet — `e7ab4de`

### Changed
- Restructured skills → agents directory; created ORG.md, soul files, values guardrails, expanded frontmatter — `46aac30`

### Fixed
- `update_updated_at_column()` added to three-layer migration for self-contained replay — `d6e4a8f`
- Resolved name leakage, stale path refs, and test failures from audit — `5177730`

---

## [0.2.0] — 2026-03-24

### Added
- Shopify → Supabase sync and CSV import scripts — `feat(backfill)`

---

## [0.1.0] — 2026-03-23

### Added
- Initial scaffold with credentials redacted — `187f8f7`
- Database DDL, pre-built queries, and validation scripts — `8dbd539`
- 7 Phase 2 skills and eval scaffolding — `59643e1`
- Product knowledge files and ecommerce skills — `aecb760`
- Agent SDK wired, 6 agent configs, server tests — `cbe0fb8`
- Supabase client and audit logging activated — `feat(shared-lib)`
