# Sprint S1: Foundation

**Tool:** Claude Code (Opus)
**Parallel Group:** PG-1 (solo — everything else depends on this)
**Prerequisites:** None
**Complexity:** Complex

---

## Overview

Build the complete shared Python library, expand all skill frontmatter, create the three-layer Supabase schema, and deliver the first two working workflows. This sprint is sequential — each phase builds on the previous.

## Phase Order

1. **0A** — ORG.md + lib path flatten + skill frontmatter + name replacement
2. **0C** — Seed COGS data for 559 products
3. **1A** — Claude client + skill loader + model constants
4. **1B** — Notion client (wiki/Academy scope only)
5. **1C** — Org resolver + notifications + cost tracker + views
6. **1D** — Three-layer Supabase schema + dashboard_ops.py
7. **2A** — Daily summary workflow
8. **2B** — Weekly P&L workflow

---

## Dev Prompt

```
Read CLAUDE.md completely. Read SYSTEM-STATUS.md for database schemas.
Read DEV-PLAN.md for full prompt specifications (Prompts 0A through 2B).

Execute the following 8 prompts in order. Each builds on the previous.
Commit after each prompt with the specified commit message.
Stop and report after each commit so I can verify.

=== PROMPT 0A: ORG.md + Skill Role Refactor + Lib Path Flatten ===

0. FLATTEN the shared library path:
   - Move all files from lib/shared/src/ts_shared/ → lib/ts_shared/
   - Remove the empty lib/shared/ directory tree
   - Update pyproject.toml package paths
   - Update all imports in existing Python files (server/server.py, tests/*, scripts/*)

1. CREATE `ORG.md` in repo root with role-based org chart:
   - ceo: Chris Mauzé, Denver CO, Slack/Dashboard/Email, English.
     Approves: pricing, budget, strategy, ad creative, financial reports.
   - operations-manager: Jothi, Jakarta Indonesia, Slack/Dashboard (Bahasa Indonesia).
     Language: Bahasa Indonesia (formal — "Anda" not "kamu", suggestions: "Mungkin bisa...").
     Approves: orders, inventory POs, CS drafts, supplier comms.
   - customer-service-lead: TBD (Asheville hire), Dashboard/Email, English.
     Handles: CS review/escalations, website technical, Shopify admin.
   - warehouse-manager: Fiona, Asheville NC, Dashboard, Chinese (Mandarin).
     Handles: pick/pack/ship domestic, inventory counts, shipping exceptions.
   - spiritual-director: Dr. Hun Lye, Email only, English.
     Handles: Buddhist practice questions, cultural sensitivity, product authenticity.
   - mexico-fulfillment: Omar (Espíritu Tibetano), Mexico, Email only, Spanish.
     Handles: Latin American fulfillment.

2. SCAN all 56+ SKILL.md files. Replace hardcoded person names with role references:
   "Jhoti" or "Jothi" → "operations-manager"
   "Chris" → "ceo"
   "Fiona" → "warehouse-manager"
   "Dr. Hun Lye" → "spiritual-director"
   "Omar" → "mexico-fulfillment"

3. EXPAND FRONTMATTER on all SKILL.md files. Current format is just `name` + `description`.
   Add fields per the CLAUDE.md "SKILL.md Frontmatter Schema":
   - version: "0.1.0"
   - category: (from folder path)
   - tags: (3-5 relevant tags)
   - author: operations-team
   - model: (haiku for triage, sonnet for analysis/drafting)
   - cacheable: true
   - estimated_tokens: (approximate from file length)
   - phase: 1
   - depends_on: (shared skills referenced)
   - external_apis: (supabase, shopify, etc.)
   - cost_budget_usd: (0.05 haiku, 0.15 sonnet, 0.50 opus)
   Use subagents to process skills in parallel (5 batches by folder).

4. UPDATE .gitignore: add data/*.csv, data/*.numbers, .~lock.*, __pycache__/, *.pyc, temp/

Commit: "refactor: create ORG.md, expand skill frontmatter, replace hardcoded names across 56 skills"

=== PROMPT 0C: Seed COGS Data ===

Read skills/finance/cogs-tracking/SKILL.md and skills/shared/supabase-ops-db/SKILL.md.

Create `scripts/seed_cogs_from_model.py`:
1. Query all 559 products from Supabase
2. Apply category-level COGS estimates by title/handle matching:
   - Incense: 24%, Singing Bowls: 30%, Malas/Prayer Beads: 20%
   - Statues/Ritual Objects: 35%, Thangkas: 40%, Prayer Flags: 15%
   - Books/Texts: 10%, Altar Supplies: 25%, Default: 25%
3. Set freight_per_unit: <$20→$2.50, $20-50→$4, $50-100→$6, >$100→$8
4. Set duty_rate = 0.05, cogs_confidence = 'estimated'
5. Print summary: count by category, total estimated COGS, blended margin %
6. REFRESH MATERIALIZED VIEW for channel_profitability_monthly and product_margin_detail

Use existing Supabase client from lib/ts_shared/supabase_client.py.

Commit: "feat: seed COGS estimates for 559 products"

=== PROMPT 1A: Claude Client + Model Constants ===

Read lib/ts_shared/supabase_client.py for existing pattern.

Create `lib/ts_shared/claude_client.py`:

1. Model constants:
   MODEL_HAIKU = "claude-haiku-4-5-20251001"
   MODEL_SONNET = "claude-sonnet-4-6"
   MODEL_OPUS = "claude-opus-4-6"

2. `SkillMetadata` Pydantic model — parse YAML frontmatter fields:
   name, description, version, category, tags, author, model, cacheable,
   estimated_tokens, phase, depends_on, external_apis, cost_budget_usd

3. `load_skill(skill_path: str) -> tuple[SkillMetadata, str]`
4. `load_skills(skill_paths: list[str]) -> tuple[list[SkillMetadata], str]`
   Auto-resolve depends_on (co-load dependencies).
5. `get_skill_index() -> list[SkillMetadata]`
   Tier 1 load: frontmatter only, ~50 tokens/skill.
6. `call_claude(system_parts, user_message, model=MODEL_SONNET, max_tokens=2000) -> Message`
   Use prompt caching: cache_control={"type": "ephemeral"} on system blocks.
7. `calculate_cost(usage, model) -> float`
   Haiku: $1/$5/MTok, Sonnet: $3/$15, Opus: $15/$75. Cache read 90% discount.

Add anthropic, pyyaml to pyproject.toml.
Write tests in tests/test_claude_client.py (mock the API).

Commit: "feat: add claude_client with skill loading, frontmatter parsing, prompt caching, cost calculation"

=== PROMPT 1B: Notion Client (Wiki Scope Only) ===

Read lib/ts_shared/notion_config.py.

Create `lib/ts_shared/notion_ops.py` — NARROWED SCOPE: Academy writes + cost log archive.
Dashboard handles all operational data. Public wiki goes to Intercom Help Center.

1. Refactor notion_config.py: read from env vars with hardcoded defaults.
   Only keep academy_modules and cost_log databases.

2. `create_academy_page(module_id, title, content, language="id") -> str`
3. `log_cost_to_notion(workflow, model, input_tokens, output_tokens, cached_tokens, cost_usd)`

Use notion-sdk-py. Add to pyproject.toml. Retry logic (3 retries, exp backoff). 3 req/sec limit.

Commit: "feat: add notion_ops.py for wiki/Academy writes"

=== PROMPT 1C: Org Resolver + Notifications + Cost Tracker ===

Read ORG.md.

Create three modules in lib/ts_shared/:

1. `org.py`:
   - `load_org(org_path="ORG.md") -> dict[str, OrgRole]`
   - `resolve_role(role_id: str) -> OrgRole`
   - OrgRole Pydantic model: person, location, contact_methods, language, approves, handles

2. `notifications.py`:
   - `send_slack(channel, text, blocks=None) -> bool` (SLACK_BOT_TOKEN from env)
   - `send_slack_dm(user_id, text) -> bool`
   - `notify(role_id, message) -> bool` (auto-select Slack, graceful degradation)

3. `cost_tracker.py`:
   - `log_invocation(workflow, skill_name, model, usage, latency_ms, trigger_source="cron", confidence=None, error=None) -> str`
     Dual-write: Supabase skill_invocations (primary) + Notion cost log (archive).
     Return invocation_id.

4. `views.py`:
   - `refresh_views(view_names: list[str])` — refresh materialized views.

Add pydantic, slack-sdk to pyproject.toml. Write tests for all.

Commit: "feat: add org resolver, notifications, cost tracker, view refresher"

=== PROMPT 1D: Full Supabase Schema Migration (Three-Layer) ===

Read DEV-PLAN.md for full schema specification.
Read temp/planning/ts-ops-dashboard-build-spec.md for complete DDL.

Create a Supabase migration with the three-layer schema:

REGISTRY LAYER: companies, agents, skills, agent_skills, workflows, workflow_steps
RUNTIME LAYER: task_inbox, workflow_runs, workflow_health, spend_records
EVAL LAYER: eval_suites, prompt_versions, eval_runs, eval_results

Include:
- RLS policies (admin sees all, team sees own company)
- Realtime publication on task_inbox, workflow_health, workflow_runs
- Indexes on hot query paths
- Seed data: 2 companies (tibetan-spirit, personal), 4 placeholder agents

Create `lib/ts_shared/dashboard_ops.py`:
- create_task(company_slug, workflow_slug, title, output, output_rendered,
  assignee, priority="P2", wake_reason="scheduled", cost_usd=0) -> str
- update_task_status(task_id, status, feedback=None, feedback_by=None)
- log_workflow_run(...) -> str
- update_workflow_health(workflow_slug, status, last_result, cost=None, duration_ms=None)
- log_spend(period, period_type, company_slug, workflow_slug, run_count, success_count,
  failure_count, total_cost_usd)

Write tests for dashboard_ops.py.

Commit: "feat: three-layer Supabase schema with registry, runtime, eval + dashboard_ops.py"

=== PROMPT 2A: Daily Summary Workflow ===

Read skills/shared/brand-guidelines/SKILL.md, skills/shared/channel-config/SKILL.md.
Read all lib/ts_shared/ modules.

Create `workflows/daily_summary/`:

1. `config.yaml`:
   name: daily_summary
   schedule: "0 18 * * *"
   model: claude-haiku-4-5-20251001
   skills: [shared/brand-guidelines, shared/channel-config]
   requires_approval: false
   notify: [ceo]

2. `run.py`:
   - Query today's orders from Supabase
   - Calculate: order count, revenue, AOV, top 5 products
   - Flag: unfulfilled >24h, orders >$500
   - Call Claude (Haiku) with loaded skills
   - Write to task_inbox via dashboard_ops.create_task() with status=auto_logged
   - Log workflow_run, send Slack to ceo, log cost

3. Write test in tests/evals/test_daily_summary.py.

Commit: "feat: add daily_summary workflow — first end-to-end workflow"

=== PROMPT 2B: Weekly P&L Workflow ===

Read skills/finance/cogs-tracking/SKILL.md, skills/finance/margin-reporting/SKILL.md.

Create `workflows/weekly_pnl/`:

1. `config.yaml`:
   name: weekly_pnl
   schedule: "0 6 * * 1"
   model: claude-sonnet-4-6
   requires_approval: true
   assignee: ceo

2. `run.py` — Three-step:
   Step 1 (Python): Query 7-day orders, join products for COGS, calculate revenue/margin/fees/AOV.
   Step 2 (Sonnet): Format CEO-ready P&L report with trends, top products, concerns, actions.
   Step 3: Write to task_inbox (needs_review, assignee=chris, priority=P2). Log run + cost.

3. Write test in tests/evals/test_pnl_accuracy.py.

Commit: "feat: add weekly_pnl workflow with prompt chain and accuracy eval"
```

---

## Test Prompt

```
Run the following verification suite for Sprint S1. Report pass/fail for each check.

=== PROMPT 0A VERIFICATION ===
1. python -c "from ts_shared.supabase_client import get_client; print('OK')"
2. Test old path is gone: python -c "from lib.shared.src.ts_shared.supabase_client import get_client" (should FAIL)
3. ls lib/shared/ (should not exist)
4. python scripts/validate_skill.py (all skills pass)
5. grep -r "Jothi\|Jhoti\|Fiona\|Dr. Hun Lye\|Omar" skills/ (zero matches)
6. cat ORG.md | head -20 (exists, has role definitions)
7. pytest tests/ (all existing tests pass with new import paths)

=== PROMPT 0C VERIFICATION ===
8. python scripts/seed_cogs_from_model.py (runs without error, prints summary)
9. Run SQL: SELECT cogs_confidence, count(*) FROM products GROUP BY 1
   → all rows 'estimated', zero 'unknown'
10. Run SQL: SELECT * FROM product_margin_detail LIMIT 5
    → margin_pct values non-null, reasonable (40-75%)
11. Run SQL: SELECT * FROM channel_profitability_monthly ORDER BY month DESC LIMIT 3
    → total_cogs > 0

=== PROMPT 1A VERIFICATION ===
12. pytest tests/test_claude_client.py (all pass)
13. python -c "from ts_shared.claude_client import load_skill, call_claude, SkillMetadata, MODEL_HAIKU; print('OK')"
14. python -c "from ts_shared.claude_client import load_skill; m, body = load_skill('shared/brand-guidelines'); print(m.name, m.model, len(body))"
    → prints name, model hint, body length > 0
15. python -c "from ts_shared.claude_client import get_skill_index; idx = get_skill_index(); print(f'{len(idx)} skills indexed')"
    → prints "56 skills indexed" (or 57)

=== PROMPT 1B VERIFICATION ===
16. pytest tests/test_notion_ops.py (all pass, mocked)
17. python -c "from ts_shared.notion_ops import create_academy_page, log_cost_to_notion; print('OK')"

=== PROMPT 1C VERIFICATION ===
18. pytest tests/test_org.py tests/test_notifications.py tests/test_cost_tracker.py (all pass)
19. python -c "from ts_shared.org import resolve_role; r = resolve_role('ceo'); print(r.language)"
    → "English"
20. python -c "from ts_shared.org import resolve_role; r = resolve_role('operations-manager'); print(r.language)"
    → "Bahasa Indonesia"
21. Confirm notifications degrade gracefully: unset SLACK_BOT_TOKEN, call notify() → returns False, no crash

=== PROMPT 1D VERIFICATION ===
22. Supabase migration applies cleanly
23. Run SQL: SELECT * FROM companies → 2 rows (tibetan-spirit, personal)
24. Run SQL: SELECT * FROM agents WHERE company_id = (SELECT id FROM companies WHERE slug = 'tibetan-spirit') → 4 agents
25. Run SQL: SELECT * FROM pg_publication_tables WHERE pubname = 'supabase_realtime'
    → includes task_inbox, workflow_health, workflow_runs
26. pytest tests/test_dashboard_ops.py (all pass)

=== PROMPT 2A VERIFICATION ===
27. python workflows/daily_summary/run.py (executes against real data, no errors)
28. Run SQL: SELECT * FROM task_inbox ORDER BY created_at DESC LIMIT 1
    → row exists, status='auto_logged', output JSONB non-empty
29. Run SQL: SELECT * FROM workflow_runs ORDER BY started_at DESC LIMIT 1
    → status='completed', total_cost_usd > 0
30. pytest tests/evals/test_daily_summary.py (passes)
31. Cost check: total_cost_usd < $0.02

=== PROMPT 2B VERIFICATION ===
32. python workflows/weekly_pnl/run.py (executes against real data)
33. Run SQL: SELECT * FROM task_inbox WHERE status = 'needs_review' ORDER BY created_at DESC LIMIT 1
    → P&L task exists, output JSONB has revenue/cogs/gross_margin/margin_pct/aov fields
34. pytest tests/evals/test_pnl_accuracy.py (passes)
35. Cost check: total_cost_usd < $0.10

=== FULL SUITE ===
36. pytest tests/ (ALL tests pass — existing + new)
37. python scripts/validate_cross_refs.py (zero violations)
```
