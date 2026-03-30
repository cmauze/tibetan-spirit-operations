# Sprint S4: Polish + Wiki Tier 3 + Documentation

**Tools:** Cursor/Gemini (dashboard) + Claude Code (wiki + docs)
**Parallel Group:** PG-4 (solo — final sprint)
**Prerequisites:** S3-W and S3-D both complete
**Complexity:** Moderate

---

## Overview

Three workstreams:
1. **Dashboard eval + settings** — Eval dashboard, settings page, final polish (Cursor/Gemini)
2. **Wiki Tier 3** — Remaining ~39 skills to production quality (Claude Code)
3. **Documentation** — Regenerate CLAUDE.md, .env.example, SYSTEM-STATUS.md, Academy M01-M04 (Claude Code)

---

## Dashboard Dev Prompt (Cursor/Gemini)

```
You are finishing the TS Command Center dashboard (ts-command-center/ repo).
The app has: login, company selector, task inbox, health, costs, home,
workflow registry, agent registry.

=== PROMPT D-5: Eval Dashboard (Autoresearch UI) ===

Build the eval/autoresearch interface for prompt optimization tracking.

Eval Dashboard (/workflows/[id]/eval):
- Eval suite selector dropdown (from eval_suites where workflow_id matches)
- Test cases table: columns = input summary, expected output summary,
  latest score per criterion. Expandable rows for full content.
- Prompt version timeline:
  - Vertical timeline or list showing prompt_versions ordered by created_at
  - Each entry: version number, model, hypothesis text, aggregate pass rate
  - Recharts LineChart: x=version, y=aggregate score (one line per criterion)
- "Run Eval" button:
  - Opens modal: select prompt version + eval suite
  - Triggers POST to a Supabase Edge Function or creates a task_inbox entry
    requesting an eval run (the Python backend picks it up)
- Override rate card:
  - 30-day trend chart from workflow_health.override_rate_30d
  - Current rate with color indicator (green <10%, yellow 10-25%, red >25%)
- Handle empty state gracefully: "No eval suites configured yet" message

Prompt Version Detail (/workflows/[id]/eval/versions/[versionId]):
- Full system prompt text (scrollable, syntax highlighted if possible)
- User prompt template
- Config card: model, temperature, max_tokens, few_shot_examples count
- Hypothesis text (editable — updates prompt_versions on save)
- Score breakdown: table of criteria → score with evaluator reasoning
- "Create Variation" button → navigates to create form pre-filled with this version

Eval Run Detail (/workflows/[id]/eval/runs/[runId]):
- Summary card: started_at, status, total_cost_usd, total_tokens, pass/fail
- Results table: one row per test case
  Columns: test case index, pass/fail badge, per-criterion scores,
  evaluator_reasoning (expandable), human_score_override (editable)
- Improvement delta card (if compared_to_version_id exists):
  Show which criteria improved/regressed vs comparison version

Commit: "feat: eval dashboard with autoresearch UI, version comparison"

=== PROMPT D-6: Settings + Final Polish ===

Settings (/settings):
- Company Management section (Chris-only, admin role check):
  - List companies with edit/add buttons
  - Inline edit: name, status, config JSONB
  - Add company form: slug, name
- Notification Preferences:
  - Per-user toggle: Slack DM (on/off), Push notifications (on/off)
  - Save to user_metadata in Supabase Auth
- Override Rate Thresholds:
  - Global default: 25% (editable)
  - Per-workflow-type overrides table:
    financial=10%, operational=15%, content=25%, cultural=always_review
- Environment Status:
  - Cards for each integration: Supabase, Shopify, Anthropic, Intercom,
    Slack, Notion, Klaviyo, Meta, Google
  - Each shows: "Configured" (green badge) or "Not configured" (gray)
  - Values masked (show last 4 chars only)
  - Read from a /api/env-status endpoint that checks server-side env vars

Final Polish:
- 404 page: friendly message + link back to home
- Loading states: skeleton loaders on all data-fetching pages
- Error boundaries: catch React errors, show "Something went wrong" + retry button
- PWA offline support:
  - Cache task_inbox data in service worker
  - When offline: show cached inbox (read-only, no approve/reject)
  - Banner: "You're offline — showing cached data"
  - Queue offline actions for sync when connection returns

Commit: "feat: settings page, error handling, offline support"
```

---

## Wiki Dev Prompt (Claude Code)

```
Read CLAUDE.md, ORG.md, SYSTEM-STATUS.md.
Read 2-3 Tier 1 or Tier 2 skills as quality reference.

Deepen ALL remaining SKILL.md files to v1.0.0. Same production quality standard.
These are Tier 3 — lower priority skills for future channel expansion and advanced features.

Process in batches by category. Commit after each batch.

=== BATCH 1: customer-service (2 remaining) ===
- customer-service/practice-inquiry (if not already done in Tier 2)
- customer-service/review-solicitation (if not already done in Tier 2)
Commit: "feat: deepen remaining customer-service skills to v1.0.0"

=== BATCH 2: operations (5 remaining) ===
- operations/fulfillment-mexico
- operations/fulfillment-nepal
- operations/amazon-fba-replenishment
- operations/travel-coordination
- operations/etsy-sync-monitoring
- operations/warehouse-management (if exists)
Commit: "feat: deepen remaining operations skills to v1.0.0"

=== BATCH 3: ecommerce (6-8 remaining) ===
- ecommerce/site-health
- ecommerce/content-performance
- ecommerce/amazon-listing-optimization
- ecommerce/agentic-discovery
- ecommerce/collection-management
- ecommerce/product-photography-standards
Commit: "feat: deepen ecommerce skills to v1.0.0"

=== BATCH 4: category-management (8 skills) ===
- category-management/competitive-research
- category-management/pricing-strategy
- category-management/category-portfolio
- category-management/assortment-planning
- category-management/promotion-strategy
- category-management/subscription-curation
- category-management/wholesale-strategy
- category-management/marketplace-expansion
Commit: "feat: deepen category-management skills to v1.0.0"

=== BATCH 5: marketing (11 remaining) ===
- marketing/campaign-architecture
- marketing/creative-library
- marketing/amazon-ppc
- marketing/etsy-ads
- marketing/pinterest-ads
- marketing/ab-testing
- marketing/email-sms
- marketing/seo
- marketing/social-content
- marketing/drift-detection
- marketing/inventory-aware-advertising
Commit: "feat: deepen remaining marketing skills to v1.0.0"

=== BATCH 6: finance (remaining) ===
- finance/debt-service
- finance/amazon-fee-analysis
- finance/channel-profitability
- finance/nepal-payments
- finance/reconciliation (if not already at v1.0.0)
Commit: "feat: deepen remaining finance skills to v1.0.0"

=== BATCH 7: shared (remaining) ===
- shared/supabase-ops-db
- shared/tibetan-calendar
Commit: "feat: deepen remaining shared skills to v1.0.0"
```

---

## Documentation Dev Prompt (Claude Code)

```
Read the entire codebase (all lib/, workflows/, scripts/, skills/, tests/, server/).

=== FINAL DOCUMENTATION ===

1. REGENERATE `CLAUDE.md` as the definitive codebase navigation document:
   - File tree with one-line descriptions (actual tree, not aspirational)
   - How to run each workflow (exact python commands)
   - Complete env var list with descriptions
   - Architecture as-built (dashboard + agents + Supabase)
   - Database schema summary (all three layers + original 7 tables)
   - Dashboard pages and their URLs
   - Skill loading pattern (three-tier)
   - Model routing (haiku/sonnet/opus and when)
   - Cultural context (Buddhist sensitivity section — keep this)
   - Team & ORG.md reference
   Keep UNDER 300 lines. This is a navigation doc, not exhaustive reference.

2. CREATE `.env.example` at repo root:
   List every env var used across the codebase with:
   - Variable name
   - Description comment
   - Which sprint/module uses it
   - Whether it's required or optional
   Do NOT include actual values.

3. UPDATE `SYSTEM-STATUS.md`:
   - Update all table row counts from live Supabase
   - Add new tables (registry, runtime, eval layers, customer_profiles, cs_inbox)
   - Update "What's Working" to reflect all 6 workflows
   - Update skill readiness (all at v1.0.0)
   - Update deployment status

4. CREATE `scripts/generate_academy_module.py`:
   - Takes module_id argument (e.g., "M01")
   - Queries real Supabase data relevant to the module topic
   - Generates module content using Claude (Sonnet)
   - Pushes to Notion via notion_ops.create_academy_page()
   - Language: Bahasa Indonesia primary, English section headers

5. Generate M01-M04 (Foundation):
   M01: The Business of Tibetan Spirit — mission, values, 5% Dharma Giving, product categories
   M02: Our Products & Their Significance — taxonomy, sourcing, care, cultural context
   M03: How Orders Flow — Shopify→Supabase→fulfillment routing, order lifecycle
   M04: The AI Operations System — what workflows do, how to review in dashboard,
        override rate, graduation tiers

Commit: "docs: regenerate CLAUDE.md, create .env.example, update system status, Academy M01-M04"
```

---

## Dashboard Test Prompt

```
=== EVAL DASHBOARD (D-5) ===
1. /workflows/[id]/eval loads without errors (even with empty eval tables)
2. Empty state message renders: "No eval suites configured yet"
3. If eval_suites exist: test case table renders, scores display
4. Prompt version timeline renders (may have 0-1 entries initially)
5. Override rate card shows value from workflow_health (or "No data" placeholder)
6. "Run Eval" button opens modal
7. Version detail page (/workflows/[id]/eval/versions/[versionId]) loads
8. Eval run detail page loads with results table

=== SETTINGS (D-6) ===
9. /settings loads for chris (admin)
10. Company list shows: Tibetan Spirit, Personal
11. Add company form: enter "Test Corp" → inserts into companies table
12. Notification preferences: toggle Slack DM → saves to user metadata
13. Override rate thresholds: edit global default → persists
14. Environment status: shows correct configured/unconfigured badges

=== FINAL POLISH ===
15. Navigate to /nonexistent → 404 page renders with home link
16. Loading states visible during initial data fetch on all pages
17. Offline test: enable airplane mode → cached inbox visible, "offline" banner shown
18. Error boundary: introduce a render error → "Something went wrong" message appears
19. No console errors on any page in normal operation

=== RESPONSIVE ===
20. All new pages work on 375px mobile viewport
21. Desktop sidebar shows Workflows, Agents links
22. Mobile "More" menu includes new links
```

---

## Wiki + Docs Test Prompt

```
=== WIKI TIER 3 ===
1. python scripts/validate_skill.py for ALL skills → every single one passes
2. grep "version: .0.1.0" skills/ -r → 0 matches (all upgraded to 1.0.0)
3. wc -l skills/*/SKILL.md and skills/*/*/SKILL.md → all under 500 lines
4. grep -r "Jothi\|Jhoti\|Fiona\|Dr. Hun Lye\|Omar" skills/ → 0 matches
5. grep -ri "exotic\|mystical\|oriental\|trinket" skills/ → 0 matches
6. python scripts/validate_cross_refs.py → zero violations

=== DOCUMENTATION ===
7. wc -l CLAUDE.md → under 300 lines
8. CLAUDE.md has sections: file tree, run commands, env vars, architecture,
   database schema, dashboard pages, skill loading, model routing, cultural context
9. cat .env.example → all env vars listed with descriptions, no actual values
10. SYSTEM-STATUS.md reflects current state (new tables, row counts, workflow status)

=== ACADEMY ===
11. python scripts/generate_academy_module.py M01 → creates Notion page
12. Verify M01-M04 exist in Notion Academy database
13. Content is primarily Bahasa Indonesia with English section headers

=== FINAL FULL SUITE ===
14. pytest tests/ → ALL tests pass
15. python scripts/run_all_workflows.py --dry-run → all 6 pass
16. python scripts/validate_cross_refs.py → zero violations
17. python scripts/validate_skill.py → all skills pass
```
