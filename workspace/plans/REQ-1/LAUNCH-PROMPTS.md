# Sprint S1 — Launch Prompts

Copy-paste each prompt into a fresh Claude Code session. Wait for the supervisor review between chunks.

---

## Execution Plan

| Chunk | Phases | What It Does | After: You Need To |
|-------|--------|-------------|---------------------|
| **Chunk A** | 0A + 0C | Restructure repo (skills→agents), create ORG.md, soul files, seed COGS | Verify: ORG.md looks right, spot-check 2-3 soul files, confirm COGS seeding output |
| **Chunk B** | 1A + 1B + 1C | Build shared Python library (6 modules) | Verify: `pytest tests/` passes, Slack test message works |
| **Chunk C** | 1D + 2A + 2B | Schema migration + first 2 workflows | Verify: check task_inbox has entries, review daily summary + P&L output quality |

After all 3 chunks pass, **PG-2 starts** (3 agents in parallel: workflows, dashboard, wiki).

---

## Chunk A Prompt (Restructure + COGS)

```
Read CLAUDE.md completely. Read SYSTEM-STATUS.md for database schemas.
Read workspace/plans/REQ-1/00A-structural-changes.md for the file structure migration spec.
Read workspace/plans/REQ-1/attachments/values-guardrails-framework.md for values framework.

You are executing Sprint S1 Phases 0A + 0C. Commit after each phase. Stop and report after each commit.

=== PHASE 0A: Restructure skills→agents + ORG.md + Lib Path Flatten ===

0. FLATTEN the shared library path:
   - Move all files from lib/shared/src/ts_shared/ → lib/ts_shared/
   - Remove the empty lib/shared/ directory tree
   - Update pyproject.toml package paths
   - Update all imports in existing Python files (server/server.py, tests/*, scripts/*)

1. RESTRUCTURE skills/ → agents/:
   - Create agents/ directory at repo root
   - Move skills/shared/ → agents/shared/
   - For each of these 6 agents: customer-service, operations, finance, marketing, ecommerce, category-management:
     a) Create agents/{agent}/ directory
     b) Create agents/{agent}/soul.md (see below for content)
     c) Create agents/{agent}/config.yaml (see below for format)
     d) Move skills/{agent}/ → agents/{agent}/skills/
   - Remove the now-empty skills/ directory
   - Update all depends_on paths in every SKILL.md frontmatter:
     Old: "shared/brand-guidelines" stays the same (it's relative)
     Old: "customer-service/ticket-triage" → stays the same (loader resolves)
   - Update server/server.py AGENT_CONFIGS skill paths
   - Update scripts/validate_skill.py to scan agents/ instead of skills/
   - Update scripts/validate_cross_refs.py to scan agents/

2. CREATE ORG.md in repo root with role-based org chart:
   - ceo: Chris Mauzé, Denver CO, Slack/Dashboard/Email, English. Approves: pricing, budget, strategy, ad creative, financial reports.
   - operations-manager: Jothi, Jakarta Indonesia, Slack/Dashboard (Bahasa Indonesia). Formal: "Anda" not "kamu", suggestions: "Mungkin bisa...". Approves: orders, inventory POs, CS drafts, supplier comms.
   - customer-service-lead: TBD (Asheville hire), Dashboard/Email, English. Handles: CS review/escalations, website technical, Shopify admin.
   - warehouse-manager: Fiona, Asheville NC, Dashboard, Chinese (Mandarin). Handles: pick/pack/ship domestic, inventory counts, shipping exceptions.
   - spiritual-director: Dr. Hun Lye, Email only, English. Handles: Buddhist practice questions, cultural sensitivity, product authenticity.
   - mexico-fulfillment: Omar (Espíritu Tibetano), Mexico, Email only, Spanish. Handles: Latin American fulfillment.

3. SCAN all SKILL.md files (now under agents/). Replace hardcoded person names with role references:
   "Jhoti" or "Jothi" → "operations-manager"
   "Chris" → "ceo"
   "Fiona" → "warehouse-manager"
   "Dr. Hun Lye" → "spiritual-director"
   "Omar" → "mexico-fulfillment"

4. EXPAND FRONTMATTER on all SKILL.md files. Current format is just name + description.
   Add these fields (read CLAUDE.md "SKILL.md Frontmatter Schema" for full spec):
   - version: "0.1.0"
   - category: (from agent folder name)
   - tags: (3-5 relevant tags)
   - author: operations-team
   - model: (haiku for triage, sonnet for analysis/drafting)
   - cacheable: true
   - estimated_tokens: (approximate from file length)
   - phase: 1
   - depends_on: (shared skills referenced — always include shared/brand-guidelines)
   - external_apis: (supabase, shopify, intercom, etc.)
   - cost_budget_usd: (0.05 haiku, 0.15 sonnet, 0.50 opus)
   Use subagents to process skills in parallel (batch by agent folder).

5. CREATE SOUL FILES for each agent. Each soul.md should be 30-80 lines:

   agents/customer-service/soul.md:
   "I am the voice of Tibetan Spirit to our customers. I prioritize warmth and accuracy over speed. I never guess on questions of dharma, spiritual practice, or product authenticity — I escalate to spiritual-director. I never send a response without human approval. I serve both English-speaking and Chinese-speaking team members."

   agents/operations/soul.md:
   "I keep the daily machinery of Tibetan Spirit running smoothly. I watch for problems before they become crises. When inventory is low, I act. When orders are unusual, I flag. I respect Jothi's communication preferences (formal Bahasa Indonesia) and Fiona's (Chinese/Mandarin via dashboard)."

   agents/finance/soul.md:
   "I am the financial conscience of Tibetan Spirit. I prioritize accuracy over speed and flag anomalies rather than hiding them. When numbers don't add up, I surface the problem immediately. I never make financial decisions — I inform the decisions the ceo makes. Dharma Giving is an accounting line item, never a marketing angle."

   agents/marketing/soul.md:
   "I help Tibetan Spirit maintain meaningful connection with customers through marketing. I understand our audience values authenticity over sales pressure. I enforce frequency caps (2 promotional emails/month, 3 ad impressions/week/user). I never sacrifice brand voice for keyword density. Restraint is our competitive advantage. I never use urgency/scarcity tactics for sacred goods."

   agents/ecommerce/soul.md:
   "I improve how Tibetan Spirit's products are presented online. I balance SEO effectiveness with cultural authenticity. I never sacrifice brand voice for keyword density. Every optimization must pass cultural review. Products are described through their practice context first."

   agents/category-management/soul.md:
   "I think strategically about Tibetan Spirit's product portfolio. I balance margin awareness with ethical sourcing. I consider long-term category health over short-term revenue. I respect the sacred significance of every product category."

6. CREATE CONFIG.YAML for each agent using this format:
   name: {agent-slug}
   description: "{one-line from soul.md}"
   model: {claude-sonnet-4-6 or claude-haiku-4-5-20251001}
   max_turns: {10-20}
   budget_usd: {per-invocation cap}
   skills:
     - shared/brand-guidelines  # Always first
     - shared/{other relevant shared skills}
     - {agent-specific skills}
   Match the skill lists to the existing AGENT_CONFIGS in server/server.py.

7. UPDATE agents/shared/brand-guidelines/SKILL.md:
   Add a "Constitutional Values" section at the TOP of the markdown body (after frontmatter).
   Content from workspace/plans/REQ-1/attachments/values-guardrails-framework.md:
   - Override priority: ABSOLUTE
   - Prohibited words list
   - Sacred terminology preservation list
   - Product framing rules table
   - Frequency caps (email, ads, social)
   - Content tier classification
   - Dharma Giving integrity rules
   - CEO decision support output format

8. UPDATE .gitignore: add data/*.csv, data/*.numbers, .~lock.*, __pycache__/, *.pyc, temp/, workspace/scratch/

Commit: "refactor: restructure skills→agents, create ORG.md, soul files, values guardrails, expand frontmatter"

=== PHASE 0C: Seed COGS Data ===

Read agents/finance/skills/cogs-tracking/SKILL.md and agents/shared/supabase-ops-db/SKILL.md.

Create scripts/seed_cogs_from_model.py:
1. Query all 559 products from Supabase
2. Apply category-level COGS estimates by title/handle matching:
   Incense: 24%, Singing Bowls: 30%, Malas/Prayer Beads: 20%,
   Statues/Ritual Objects: 35%, Thangkas: 40%, Prayer Flags: 15%,
   Books/Texts: 10%, Altar Supplies: 25%, Default: 25%
3. Set freight_per_unit: <$20→$2.50, $20-50→$4, $50-100→$6, >$100→$8
4. Set duty_rate = 0.05, cogs_confidence = 'estimated'
5. Print summary: count by category, total estimated COGS, blended margin %
6. REFRESH MATERIALIZED VIEW for channel_profitability_monthly and product_margin_detail

Use existing Supabase client from lib/ts_shared/supabase_client.py.

Commit: "feat: seed COGS estimates for 559 products"
```

---

## Chunk B Prompt (Shared Library)

```
Read CLAUDE.md completely. Read ORG.md. Read SYSTEM-STATUS.md.
Read lib/ts_shared/supabase_client.py for the existing singleton pattern.

You are executing Sprint S1 Phases 1A + 1B + 1C. Commit after each phase.

=== PHASE 1A: Claude Client + Skill Loader ===

Create lib/ts_shared/claude_client.py:

1. Model constants:
   MODEL_HAIKU = "claude-haiku-4-5-20251001"
   MODEL_SONNET = "claude-sonnet-4-6"
   MODEL_OPUS = "claude-opus-4-6"

2. SkillMetadata Pydantic model — parse YAML frontmatter into structured object:
   name, description, version, category, tags, author, model, cacheable,
   estimated_tokens, phase, depends_on, external_apis, cost_budget_usd

3. load_skill(skill_path: str) -> tuple[SkillMetadata, str]:
   Read SKILL.md from agents/ tree. Skill paths like "shared/brand-guidelines"
   resolve to agents/shared/brand-guidelines/SKILL.md. Paths like
   "customer-service/ticket-triage" resolve to
   agents/customer-service/skills/ticket-triage/SKILL.md.
   Parse YAML frontmatter into SkillMetadata, return (metadata, markdown_body).

4. load_skills(skill_paths: list[str]) -> tuple[list[SkillMetadata], str]:
   Load multiple skills. Auto-resolve depends_on (co-load dependencies).
   ALWAYS load shared/brand-guidelines FIRST regardless of order requested.
   Concatenate bodies with section headers. Deduplicate dependencies.

5. get_skill_index() -> list[SkillMetadata]:
   Scan agents/*/skills/*/ and agents/shared/*/. Parse frontmatter only.
   Tier 1 startup load (~50 tokens/skill).

6. call_claude(system_parts, user_message, model=MODEL_SONNET, max_tokens=2000) -> Message:
   Use prompt caching: cache_control={"type": "ephemeral"} on system blocks.

7. calculate_cost(usage, model) -> float:
   Haiku: $1/$5/MTok. Sonnet: $3/$15. Opus: $15/$75. Cache read 90% discount.

Add anthropic, pyyaml to pyproject.toml.
Write tests in tests/test_claude_client.py (mock the API).

Commit: "feat: claude_client with skill loading from agents/ tree, prompt caching, cost calc"

=== PHASE 1B: Notion Client (Wiki Scope Only) ===

Read lib/ts_shared/notion_config.py.

Create lib/ts_shared/notion_ops.py — NARROWED SCOPE: Academy + cost log archive.

1. Refactor notion_config.py: read from env vars with hardcoded defaults.
   Only keep academy_modules and cost_log databases.
2. create_academy_page(module_id, title, content, language="id") -> str
3. log_cost_to_notion(workflow, model, input_tokens, output_tokens, cached_tokens, cost_usd)

Use notion-sdk-py. Add to pyproject.toml. Retry logic (3 retries, exp backoff). 3 req/sec.
Write tests (mock Notion API).

Commit: "feat: notion_ops.py for wiki/Academy writes"

=== PHASE 1C: Org Resolver + Notifications + Cost Tracker ===

Read ORG.md.

Create three modules in lib/ts_shared/:

1. org.py:
   - load_org(org_path="ORG.md") -> dict[str, OrgRole]
   - resolve_role(role_id: str) -> OrgRole
   - OrgRole Pydantic model: person, location, contact_methods, language, approves, handles

2. notifications.py:
   - send_slack(channel, text, blocks=None) -> bool (SLACK_BOT_TOKEN from env)
   - send_slack_dm(user_id, text) -> bool
   - notify(role_id, message) -> bool (auto-select Slack, graceful degradation if no token)

3. cost_tracker.py:
   - log_invocation(workflow, skill_name, model, usage, latency_ms, trigger_source="cron") -> str
     Dual-write: Supabase skill_invocations (primary) + Notion cost log (archive).

4. views.py:
   - refresh_views(view_names: list[str]) — REFRESH MATERIALIZED VIEW calls.

Add pydantic, slack-sdk to pyproject.toml. Write tests for all modules.

Commit: "feat: org resolver, notifications, cost tracker, view refresher"
```

---

## Chunk C Prompt (Schema + Workflows)

```
Read CLAUDE.md, ORG.md, SYSTEM-STATUS.md.
Read DEV-PLAN.md for full schema specification (Prompt 1D section).
Read workspace/plans/REQ-1/attachments/values-guardrails-framework.md.
Read all lib/ts_shared/ modules to understand the library you're building on.

You are executing Sprint S1 Phases 1D + 2A + 2B. Commit after each phase.

=== PHASE 1D: Three-Layer Supabase Schema + dashboard_ops.py ===

Create a Supabase migration establishing the three-layer schema:

REGISTRY LAYER: companies, agents, skills, agent_skills, workflows, workflow_steps
RUNTIME LAYER: task_inbox, workflow_runs, workflow_health, spend_records
EVAL LAYER: eval_suites, prompt_versions, eval_runs, eval_results

Include:
- RLS policies (admin sees all, team sees own company)
- Realtime publication on task_inbox, workflow_health, workflow_runs
- Indexes on hot query paths (task_inbox by status+assignee, workflow_runs by workflow+date)
- Seed data: 2 companies (tibetan-spirit, personal), 6 agents for tibetan-spirit
  matching the agents/ directory (customer-service, operations, finance, marketing, ecommerce, category-management)

Create lib/ts_shared/dashboard_ops.py:
- create_task(company_slug, workflow_slug, title, output, output_rendered,
  assignee, priority="P2", wake_reason="scheduled", cost_usd=0) -> str
- update_task_status(task_id, status, feedback=None, feedback_by=None)
- log_workflow_run(...) -> str
- update_workflow_health(workflow_slug, status, last_result, cost=None, duration_ms=None)
- log_spend(period, period_type, company_slug, workflow_slug, run_count, ..., total_cost_usd)

Write tests for dashboard_ops.py (mock Supabase).

Commit: "feat: three-layer Supabase schema + dashboard_ops.py"

=== PHASE 2A: Daily Summary Workflow ===

Read agents/shared/brand-guidelines/SKILL.md, agents/shared/channel-config/SKILL.md.
Read agents/operations/soul.md for agent identity.

Create workflows/daily_summary/:

1. config.yaml:
   name: daily_summary
   schedule: "0 18 * * *"
   model: claude-haiku-4-5-20251001
   agent: operations
   skills: [shared/brand-guidelines, shared/channel-config]
   requires_approval: false
   notify: [ceo]

2. run.py:
   - Load agent soul file + skills via claude_client.load_skills()
   - Query today's orders from Supabase
   - Calculate: order count, revenue, AOV, top 5 products by revenue
   - Flag: unfulfilled >24h, orders >$500
   - Call Claude (Haiku) with soul + skills as system prompt
   - Output MUST end with structured decision support:
     STATUS: GREEN/YELLOW/RED
     VALUES CHECK: Cultural sensitivity [PASS] | Frequency [N/A]
     COST: $X.XX
   - Write to task_inbox via dashboard_ops.create_task() with status=auto_logged
   - Log workflow_run, send Slack to ceo, log cost

3. Write test in tests/evals/test_daily_summary.py with mock data.

Commit: "feat: daily_summary workflow — first end-to-end workflow"

=== PHASE 2B: Weekly P&L Workflow ===

Read agents/finance/skills/cogs-tracking/SKILL.md, agents/finance/skills/margin-reporting/SKILL.md.
Read agents/finance/soul.md for agent identity.

Create workflows/weekly_pnl/:

1. config.yaml:
   name: weekly_pnl
   schedule: "0 6 * * 1"
   model: claude-sonnet-4-6
   agent: finance
   requires_approval: true
   assignee: ceo

2. run.py — Three-step:
   Step 1 (Python): Query 7-day orders, join with products for COGS, calculate
   revenue, COGS, gross margin, fees, AOV. Compare to prior week.
   Step 2 (Sonnet): Format CEO-ready P&L report with trends, top products,
   concerns, recommended actions. Include decision support format.
   Step 3: Write to task_inbox (needs_review, assignee=chris, priority=P2).
   Log workflow_run and cost.

3. Write test in tests/evals/test_pnl_accuracy.py.

Commit: "feat: weekly_pnl workflow with prompt chain and accuracy eval"
```

---

## What the Supervisor (me) Checks After Each Chunk

### After Chunk A:
- [ ] `ls agents/` shows: shared/, customer-service/, operations/, finance/, marketing/, ecommerce/, category-management/
- [ ] Each agent folder has: soul.md, config.yaml, skills/ with SKILL.md files
- [ ] `ls skills/` → directory no longer exists
- [ ] `cat ORG.md | head -20` → roles defined
- [ ] `grep -r "Jothi\|Jhoti\|Fiona" agents/` → zero matches
- [ ] `python scripts/validate_skill.py` → all pass (scans agents/ tree)
- [ ] `python scripts/seed_cogs_from_model.py` → prints category breakdown
- [ ] `pytest tests/` → existing tests pass with new import paths
- [ ] Spot-check: read 1 soul file, 1 config.yaml — look right?
- [ ] Spot-check: brand-guidelines has constitutional values section?

### After Chunk B:
- [ ] `pytest tests/` → all tests pass (including new test_claude_client, test_org, etc.)
- [ ] `python -c "from ts_shared.claude_client import load_skill; m,b = load_skill('shared/brand-guidelines'); print(m.name, len(b))"` → works
- [ ] `python -c "from ts_shared.org import resolve_role; print(resolve_role('ceo').language)"` → "English"
- [ ] Notifications degrade gracefully if SLACK_BOT_TOKEN missing

### After Chunk C:
- [ ] Schema migration applied — `SELECT * FROM companies` → 2 rows
- [ ] `python workflows/daily_summary/run.py` → executes, task_inbox row created
- [ ] `python workflows/weekly_pnl/run.py` → executes, needs_review task created
- [ ] Output includes STATUS/VALUES CHECK/COST decision support section
- [ ] `pytest tests/` → ALL tests pass
- [ ] Cost check: daily_summary < $0.02, weekly_pnl < $0.10

### From Chris (before PG-2 starts):
- [ ] Supabase auth users created (chris, jothi, fiona)
- [ ] Intercom Essentials account created + Shopify connected
- [ ] Verify Slack channels exist (#ts-ops, #ts-customer-service, #ts-alerts)
