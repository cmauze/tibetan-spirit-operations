# Tibetan Spirit AI Ops — Development Plan

**Date:** March 29, 2026
**Owner:** Chris Mauzé
**Status:** Approved — ready for execution
**Last Updated:** 2026-03-29

---
!!!
## NOTE: SEE WORKSPACE FOR THE OFFICIAL SPRINT / PLANNING DOCUMENTS !!!!
!!!
---
## Architecture Summary

**What we're building:** An autonomous operations platform where Claude-powered workflows handle daily business operations (order summaries, P&L reports, CS email drafts, inventory alerts, campaign briefs). A React PWA dashboard ("Command Center") is the human control plane for approvals, health monitoring, cost tracking, and workflow management. Supabase is the shared coordination bus — agents write to it, the dashboard reads from it, humans approve through it.

**Execution model:** Standalone Python workflow scripts triggered by Railway cron jobs. Each workflow loads relevant SKILL.md files into Claude's system prompt, queries Supabase for business data, calls the Anthropic API, writes results to Supabase `task_inbox` for human review via the dashboard, and logs costs.

**Three layers:**
1. **Registry Layer** — what exists (companies, agents, workflows, steps, skills)
2. **Runtime Layer** — what happened (task inbox, workflow runs, spend, health)
3. **Eval Layer** — how good is it (eval suites, prompt versions, autoresearch runs)

```
┌─────────────────────────────────────────────────────┐
│                    HUMAN LAYER                       │
│  React PWA (Vercel)     Slack (internal alerts)     │
│  ┌─────────┐ ┌────────┐ ┌────────┐ ┌─────────────┐ │
│  │Approval │ │Health  │ │Cost    │ │Workflow     │ │
│  │Queue    │ │Monitor │ │Tracker │ │Registry     │ │
│  └────┬────┘ └───┬────┘ └───┬────┘ └──────┬──────┘ │
└───────┼──────────┼──────────┼──────────────┼────────┘
        │          │          │              │
   ┌────▼──────────▼──────────▼──────────────▼────────┐
   │              SUPABASE POSTGRESQL                  │
   │  Registry │ Runtime │ Eval │ Auth │ Realtime     │
   └────▲──────────▲──────────▲──────────────▲────────┘
        │          │          │              │
┌───────┼──────────┼──────────┼──────────────┼────────┐
│       │     AGENT LAYER (Railway)          │        │
│  ┌────┴────┐ ┌────┴────┐ ┌────┴────┐ ┌────┴─────┐  │
│  │Cron     │ │Webhook  │ │On-demand│ │Eval      │  │
│  │Triggers │ │Triggers │ │(manual) │ │Runner    │  │
│  └─────────┘ └─────────┘ └─────────┘ └──────────┘  │
│            Python workflows + SKILL.md files        │
└─────────────────────────────────────────────────────┘
```

**Multi-company support:** Schema supports multiple companies from day 1. Dashboard has a company selector (top-left) for switching between workspaces. Initial companies: `tibetan-spirit` (primary focus) and `personal` (Chris's personal agent monitoring). Additional companies (`cgai`, `norbu`) added when ready.

**Helpdesk: Intercom or Zendesk** (decision narrowed, setup pending). Chris will set up one of these before Sprint 2. The CS email drafts workflow ingests from helpdesk API if configured, otherwise falls back to a Supabase `cs_inbox` table for test mode. The helpdesk's built-in knowledge base / help center replaces the need for a Notion public wiki — product guides, FAQ, shipping policy, and Buddhist practice guides will live in the helpdesk's article system instead.

---

## Guiding Principles

1. **~2,000 orders/year (~5.5/day).** Every system must justify itself against this volume. If a human can do it in 30 minutes, don't automate it unless the automation is trivially simple or the learning compounds.
2. **Build atoms before molecules.** No orchestration layer until standalone scripts produce real outputs from real data. Find the simplest solution possible, increase complexity only when needed.
3. **Cultural sensitivity is non-negotiable.** Nothing customer-facing publishes without human approval. The Buddhist audience is small, discerning, and will notice AI slop. Zero exceptions.
4. **The onboarding IS the company.** Every training module Jothi completes becomes a permanent wiki page. We're not just onboarding one person — we're building the knowledge base that future hires, agents, and brand extensions will use.

---

## Architecture Decisions (Locked)

### Dashboard as Control Plane (Not Notion)

The React PWA dashboard replaces Notion for all operational workflows. Supabase `task_inbox` is the HITL state machine — workflows write drafts to it, humans approve/reject through the dashboard, downstream actions execute on approval.

**Why dashboard over Notion for ops:**
- Direct Supabase writes (no Notion→Supabase polling needed)
- Realtime updates via Supabase subscriptions
- Mobile-first approval queue (phone-sized tap targets)
- Multi-company filtering with workspace selector
- Override rate tracking and workflow graduation built in
- Bilingual support (English, Bahasa Indonesia, Chinese)

**What stays in Notion:**
- Academy modules (Jothi's training — 37 modules, Bahasa Indonesia)
- Internal playbooks (brand voice, supplier directory)

**What moves to helpdesk (Intercom/Zendesk):**
- Public-facing knowledge base (product guides, FAQ, shipping policy, Buddhist practice guides)
- The helpdesk's built-in help center / articles system replaces Notion's "Share to web" pages

### Why Hybrid (Supabase + Dashboard + Cron Scripts)

**Keep:** Supabase as data layer (19K orders, 559 products, 7 tables, 4 materialized views).

**Replace:** Always-on Railway FastAPI server → cron-triggered standalone Python workflows. The server stays in `server/` for future webhook/chatbot endpoint.

**Add:** React PWA dashboard on Vercel as the human-facing operational layer. Supabase is the coordination bus between agents and humans.

### HITL Pattern: Supabase as State Machine

Workflows write drafts to Supabase `task_inbox`. Dashboard shows them for human review. When human approves/rejects, the dashboard writes status directly back to Supabase. Next workflow run checks Supabase. No polling, no sync layer, no Notion in the operational loop.

**Quality gate on approved content:** Before executing downstream actions, check that output doesn't contain automation artifacts (markdown formatting, JSON, skill references). Fall back to manual action if rendering fails.

### Org Chart as Single Source of Truth

A single `ORG.md` that all skills reference by role, not by name. The `lib/org.py` utility loads ORG.md and resolves role → contact method → language.

### Railway Deployment Model

All scheduled workflows run on Railway as Cron Services. Each workflow gets its own cron service — a container that spins up on schedule, runs the script, and stops. All cron services share the same Docker image and environment variables.

```dockerfile
# Workflows run as: docker run ts-ops python -m workflows.daily_summary.run
# Server runs as: docker run ts-ops uvicorn server.server:app
```

Each workflow's `config.yaml` schedule translates directly to a Railway cron expression. The existing `server/server.py` runs as a separate Railway Web Service when webhook reception or chatbot endpoint is needed.

**Shopify Plan:** Growth ($79/mo) confirmed. Inventory API available with "all data" access and 10 inventory locations, which unblocks `sync_shopify_inventory.py` and `inventory_alerts` workflow.

### Slack for Internal Comms

Channels for workflow-specific feeds (#ts-ops, #ts-inventory, #ts-cs-drafts). WhatsApp reserved for Nepal supplier communications and Jothi's mobile alerts.

### Role Responsibilities

| Role | Responsibilities |
|------|-----------------|
| `ceo` | Strategy, approvals, brand voice, architecture, financial oversight |
| `operations-manager` (Jothi) | Supply chain/sourcing, creative content, daily ops |
| `customer-service-lead` (TBD — Asheville hire) | CS review/escalations, website technical, Shopify admin |
| `warehouse-manager` (Fiona) | Pick/pack/ship domestic, inventory counts, shipping exceptions |
| `spiritual-director` (Dr. Hun Lye) | Buddhist practice questions, cultural sensitivity, product authenticity |
| `mexico-fulfillment` (Omar) | Latin American order fulfillment |

### Workflow Patterns (Anthropic Composable Patterns)

Each workflow maps to one of Anthropic's composable agentic patterns:

| Workflow | Pattern | Skills Loaded | Model | HITL Gate |
|---|---|---|---|---|
| `daily_summary` | Single LLM call with retrieval | shared/brand-guidelines, shared/channel-config | Haiku | Auto-logged (no approval) |
| `weekly_pnl` | Prompt chain (pull → aggregate → format) | finance/cogs-tracking, finance/margin-reporting | Sonnet | CEO reviews for accuracy |
| `cs_email_drafts` | Prompt chain (triage → enrich → draft) | customer-service/ticket-triage, shared/brand-guidelines, shared/product-knowledge | Haiku→Sonnet | CS lead reviews every draft |
| `inventory_alerts` | Prompt chain with conditional logic | operations/inventory-management, shared/channel-config | Sonnet | Ops manager reviews PO draft |
| `campaign_brief` | Prompt chain (pull → analyze → generate) | shared/brand-guidelines, marketing skills | Sonnet | CEO approves brief |
| `product_descriptions` | Evaluator-optimizer loop (autoresearch) | shared/brand-guidelines, shared/product-knowledge | Sonnet | CEO + ops manager review |

### Autoresearch Suitability

Not all domains benefit from automated prompt optimization. Use autoresearch where feedback loops are fast and scoring is tractable:

| Domain | Autoresearch? | Why |
|--------|:---:|---|
| Agent prompts / system prompts | Yes | Fast eval, binary scoring, compounds overnight |
| Product descriptions / SEO copy | Yes | Rubric-scorable, low deployment risk |
| Email subject lines | Yes | 24-hour feedback loop via Klaviyo |
| Shopify theme / page speed | Yes | Lighthouse scores as metric |
| Paid ad creative | No | 5-7 week feedback loops at ~5.5 orders/day |
| Brand positioning | No | Qualitative, high-stakes |
| Supplier negotiations | No | Relationship-based, months-long cycle |

### Three-Tier Skill Loading (from cross-framework research)

A convergent pattern across Anthropic, Microsoft, and LangChain for resource-efficient skill loading. The `claude_client.py` skill loader must implement this:

1. **Tier 1 (Startup):** Only name + description loaded into system prompt for all 56 skills (~50 tokens/skill = ~3K tokens total). Claude uses these to decide which skills are relevant.
2. **Tier 2 (On-Trigger):** Full SKILL.md content loads when Claude identifies a skill as relevant (~1.2-2K tokens per skill). Keep under 500 lines / 5K tokens.
3. **Tier 3 (At-Invocation):** Dependencies (`depends_on` skills) + shared resources resolve at execution time (~500-1K tokens).

This means `load_skill()` must parse YAML frontmatter into a structured `SkillMetadata` object (not just return raw text), so the loader can read `estimated_tokens`, `depends_on`, and `model` hints before deciding what to load and which model to route to.

### Extended SKILL.md Frontmatter (Phased Rollout)

The full frontmatter schema is defined in CLAUDE.md. Based on cross-framework research (`temp/research/SKILL_METADATA_RESEARCH.md`), frontmatter fields roll out in phases:

**Sprint 1 (Prompt 0A) — all 56 skills get these:**
- `name`, `description` (with "Use when:" + "Do NOT use for:"), `version`, `category`, `tags`, `author`, `model`, `cacheable`, `estimated_tokens`, `phase`, `depends_on`, `external_apis`, `cost_budget_usd`

**Sprint 4 (Wiki Deepening) — add when deepening each skill:**
- `graduation_criteria` (min_invocations, max_error_rate, min_days)
- `escalation_rules` (condition → role mappings)
- `max_tokens`

**Post-MVP — add when observability matures:**
- `inputs`/`outputs` with Pydantic-style validation constraints (min_length, max_length, pattern, ge/le)
- `cache_optimization` (cache_ttl_seconds, estimated_cache_savings, cache_breakpoints)
- `context_budget` (full_skill_tokens, shared_resources_tokens, total_loaded_tokens, recommended_model, fallback_model)
- `observability` (log_level, trace_context_fields, drift_detection with anomaly_threshold)
- `performance` (typical_runtime_seconds, p99_runtime_seconds, idempotent, output_format)
- `references` (runbook path, examples path, related_skills list)

Fields unique to Tibetan Spirit (not found in any major framework):
- `escalation_rules` — map conditions to team roles (spiritual-director, ceo, operations-manager)
- `cultural_notes` — Buddhist terminology, product context sensitivity
- `phase` + `graduation_criteria` — Phase 1 HITL → Phase 2 autonomous progression

### config.yaml Standard Format

Every workflow has a `config.yaml` defining its operational parameters:

```yaml
name: weekly_pnl
description: "Weekly P&L summary from Shopify orders + COGS estimates"
pattern: prompt_chain       # single_call | prompt_chain | evaluator_optimizer
schedule: "0 6 * * 1"       # Railway cron expression
skills: [shared/brand-guidelines, finance/cogs-tracking, finance/margin-reporting]
model: claude-sonnet-4-6
requires_approval: true
approval_tier: 2             # 1=auto-execute, 2=draft+4hr-timeout, 3=explicit
assignee: ceo
priority: P2
budget:
  max_tokens: 4000
  max_cost_usd: 0.30
eval:
  suite: tests/evals/test_pnl_accuracy.py
```

### Principle: Don't Rebuild What's Working

Do not rewrite anything that's working. Build new things alongside existing assets.

---

## What Exists Today

| Asset | Status | Detail |
|-------|--------|--------|
| Supabase schema | ✅ Live | 7 tables, 4 materialized views, 19.4K orders, 559 products |
| Shopify API | ✅ Connected | OAuth token active, backfill scripts tested |
| Anthropic API | ✅ Key configured | Not yet invoked in production |
| Notion databases | ✅ Created | IDs in `notion_config.py` (narrowed to wiki/Academy use only) |
| Railway | ✅ Connected | GitHub linked, env vars configured |
| 56 SKILL.md files | 🟡 Stubs | Frontmatter + purpose + outline. ~35% content depth. |
| FastAPI server | 🟡 Built | 326 lines, not deployed. Future webhook/chatbot endpoint. |
| Lib path | 🟡 Wrong path | Currently `lib/shared/src/ts_shared/` — needs flattening to `lib/ts_shared/` |
| Slack | 🟡 Webhooks active | `#ts-alerts` + `#ts-customer-service` webhooks live (2026-04-05). Bot token + Socket Mode needed for HITL buttons. |
| ORG.md | 🔴 Missing | Referenced in CLAUDE.md but file doesn't exist |
| workflows/ | 🔴 Missing | Directory doesn't exist yet |
| Dashboard | 🔴 Not started | Separate repo `ts-command-center/` on Vercel |

---

## Priority Order & Sprint Structure

Development runs on two parallel tracks after Sprint 1 foundation completes. The **workflow track** (Python, Railway) and the **dashboard track** (Next.js, Vercel) share Supabase as the coordination bus.

### Sprint 1: Foundation
**Goal:** Shared library complete. Supabase schema expanded with registry/runtime/eval layers. First two workflows running and writing to `task_inbox`.

### Sprint 2: Dashboard Core + CS Pipeline
**Goal:** Dashboard deployed — Chris can approve/reject from phone. CS email drafts with HITL. Inventory alerts.

### Sprint 3: More Workflows + Dashboard Management
**Goal:** Campaign briefs, product descriptions, reliability pass. Dashboard shows workflow registry and agent details.

### Sprint 4: Wiki Deepening + Eval
**Goal:** Deepen SKILL.md files to production quality. Eval dashboard operational. System documentation.

---

## Sprint 1: Foundation

All prompts are sequential — each builds on the previous.

### Prompt 0A: ORG.md + Skill Role Refactor + Lib Path Flatten

```
Read CLAUDE.md, then read skills/shared/escalation-matrix/SKILL.md.

0. FLATTEN the shared library path:
   - Move all files from lib/shared/src/ts_shared/ → lib/ts_shared/
   - Remove the empty lib/shared/ directory tree
   - Update pyproject.toml package paths
   - Update all imports in existing Python files (server/server.py, tests/*, scripts/*)

1. CREATE `ORG.md` in repo root with role-based org chart:
   - ceo: Chris Mauzé, Denver CO, Slack/Dashboard/Email, English. Approves: pricing, budget, strategy, ad creative, financial reports.
   - operations-manager: Jothi, Jakarta Indonesia, Slack/Dashboard (Bahasa Indonesia), Bahasa Indonesia (formal — "Anda" not "kamu", suggestions with "Mungkin bisa..."). Approves: orders, inventory POs, CS drafts, supplier comms. WhatsApp for supplier/Nepal comms only.
   - customer-service-lead: TBD (Asheville hire), Asheville NC, Dashboard/Email, English. Handles: CS review/escalations, website technical, Shopify admin.
   - warehouse-manager: Fiona, Asheville NC, Dashboard, Chinese (Mandarin). Handles: pick/pack/ship domestic, inventory counts, shipping exceptions.
   - spiritual-director: Dr. Hun Lye, Email only, English. Handles: Buddhist practice questions, cultural sensitivity, product authenticity.
   - mexico-fulfillment: Omar (Espíritu Tibetano), Mexico, Email only, Spanish. Handles: Latin American fulfillment.

2. SCAN all 56 SKILL.md files. Replace hardcoded person names with role references:
   "Jhoti" or "Jothi" → "operations-manager"
   "Chris" → "ceo"
   "Fiona" → "warehouse-manager"
   "Dr. Hun Lye" → "spiritual-director"
   "Omar" → "mexico-fulfillment"

3. EXPAND FRONTMATTER on all 56 SKILL.md files. The current format is just `name` + `description`.
   Add these fields to every skill (read CLAUDE.md "SKILL.md Frontmatter Schema" for the full spec):

   For each skill, add the fields you can confidently infer:
   - version: "0.1.0" (all skills are stubs, not yet 1.0)
   - category: (derive from folder path — shared, customer-service, operations, etc.)
   - tags: (3-5 relevant tags based on the skill's content)
   - author: operations-team (default for now)
   - model: (haiku for classification/triage skills, sonnet for analysis/drafting skills)
   - cacheable: true (for all skills)
   - estimated_tokens: (approximate from file length)
   - phase: 1 (all skills start in Phase 1)
   - depends_on: (list shared skills that this skill references)
   - external_apis: (supabase, shopify, etc. — infer from content)
   - cost_budget_usd: (0.05 for haiku skills, 0.15 for sonnet, 0.50 for opus)

   Leave empty if you can't confidently infer: graduation_criteria, escalation_rules, max_tokens.

   Use subagents to process skills in parallel (5 batches by folder).

4. UPDATE .gitignore: add data/*.csv, data/*.numbers, .~lock.*, __pycache__/, *.pyc, temp/

Commit: "refactor: create ORG.md, expand skill frontmatter, replace hardcoded names across 56 skills"
```

**Verify:**
- `python -c "from ts_shared.supabase_client import get_client; print('OK')"` — import works at new path
- `python scripts/validate_skill.py` — all 56 skills pass frontmatter validation
- `grep -r "Jothi\|Jhoti\|Fiona\|Dr. Hun Lye\|Omar" skills/` — no hardcoded names remain
- All existing tests pass: `pytest tests/`

---

### Prompt 0C: Seed COGS Data

```
Read skills/finance/cogs-tracking/SKILL.md and skills/shared/supabase-ops-db/SKILL.md.

Create `scripts/seed_cogs_from_model.py`:
1. Query all 559 products from Supabase
2. Apply category-level COGS estimates by title/handle matching:
   - Incense: 24% of retail price
   - Singing Bowls: 30%
   - Malas/Prayer Beads: 20%
   - Statues/Ritual Objects: 35%
   - Thangkas: 40%
   - Prayer Flags: 15%
   - Books/Texts: 10%
   - Altar Supplies: 25%
   - Default: 25%
3. Set freight_per_unit: <$20→$2.50, $20-50→$4, $50-100→$6, >$100→$8
4. Set duty_rate = 0.05, cogs_confidence = 'estimated'
5. Print summary: count by category, total estimated COGS, blended margin %
6. REFRESH MATERIALIZED VIEW for channel_profitability_monthly and product_margin_detail

Use existing Supabase client from lib/ts_shared/supabase_client.py.

Commit: "feat: seed COGS estimates for 559 products"
```

**Verify:**
- Run the script, confirm 559 products updated
- `SELECT cogs_confidence, count(*) FROM products GROUP BY 1` → all rows `estimated`, zero `unknown`
- `SELECT * FROM product_margin_detail LIMIT 5` → margin_pct values non-null and reasonable (40-75%)
- `SELECT * FROM channel_profitability_monthly ORDER BY month DESC LIMIT 3` → total_cogs > 0

---

### Prompt 1A: Shared Library — Claude Client + Model Constants

```
Read CLAUDE.md and lib/ts_shared/supabase_client.py for the existing pattern.

Create `lib/ts_shared/claude_client.py`:

1. Model constants:
   MODEL_HAIKU = "claude-haiku-4-5-20251001"
   MODEL_SONNET = "claude-sonnet-4-6"
   MODEL_OPUS = "claude-opus-4-6"

2. `SkillMetadata` Pydantic model — parse YAML frontmatter into structured object:
   - name, description, version, category, tags, author
   - model (routing hint: haiku/sonnet/opus)
   - cacheable, estimated_tokens
   - phase (1=HITL, 2=autonomous)
   - depends_on (list of skill paths for co-loading)
   - external_apis (list of required services)
   - cost_budget_usd (max cost per invocation)

3. `load_skill(skill_path: str) -> tuple[SkillMetadata, str]`: Read SKILL.md from
   skills/{skill_path}/. Parse YAML frontmatter into SkillMetadata, return both
   metadata and markdown body. Support nested paths like "shared/brand-guidelines".

4. `load_skills(skill_paths: list[str]) -> tuple[list[SkillMetadata], str]`:
   Load multiple skills, auto-resolve depends_on (co-load dependencies),
   concatenate bodies with section headers. Return metadata list + combined content.

5. `get_skill_index() -> list[SkillMetadata]`: Scan all skills/ directories,
   parse only YAML frontmatter (not full body), return list of metadata.
   This is the Tier 1 startup load (~50 tokens/skill = ~3K tokens total).

6. `call_claude(system_parts: list[dict], user_message: str, model: str = MODEL_SONNET, max_tokens: int = 2000) -> anthropic.types.Message`:
   - Use prompt caching: mark system content blocks with cache_control={"type": "ephemeral"}
   - Return full Message object

7. `calculate_cost(usage: anthropic.types.Usage, model: str) -> float`:
   - Haiku: $1/$5 per MTok (input/output), cache read 90% discount
   - Sonnet: $3/$15 per MTok, cache read 90% discount
   - Opus: $15/$75 per MTok, cache read 90% discount

Add `anthropic`, `pyyaml` to pyproject.toml dependencies.

Write tests in tests/test_claude_client.py (mock the API).

Commit: "feat: add claude_client with skill loading, frontmatter parsing, prompt caching, cost calculation"
```

**Verify:**
- `pytest tests/test_claude_client.py` — all tests pass
- Skill loading: `load_skill("shared/brand-guidelines")` returns (SkillMetadata, str) tuple
- SkillMetadata: `metadata.name == "brand-guidelines"`, `metadata.model == "sonnet"` (or whatever the skill specifies)
- `get_skill_index()` returns list of 56 SkillMetadata objects with name+description only (no full body loaded)
- Dependency resolution: loading a skill with `depends_on: [shared/brand-guidelines]` also loads that dependency
- Cost calculation: `calculate_cost(Usage(input_tokens=1000, output_tokens=500), MODEL_HAIKU)` returns correct USD value
- No real API calls in tests (all mocked)

---

### Prompt 1B: Shared Library — Notion Client (Wiki Scope Only)

```
Read CLAUDE.md and lib/ts_shared/notion_config.py (contains all database IDs).

Create `lib/ts_shared/notion_ops.py` — NARROWED SCOPE: Academy writes and cost log archive only.
The dashboard handles all operational data (task inbox, cost tracking, workflow status).
Public-facing wiki content lives in the helpdesk knowledge base (Intercom/Zendesk), not Notion.

1. Refactor notion_config.py to read from env vars with hardcoded defaults:
   NOTION_DB = {
       "academy_modules": os.getenv("NOTION_ACADEMY_DB", "b460c0381565404ab05534370a0aa990"),
       "cost_log": os.getenv("NOTION_COST_LOG_DB", "ab437dd8b622419a8907e5fe590d9ae5"),
   }

2. `create_academy_page(module_id, title, content, language="id") -> str`: Create page in Academy database.

3. `log_cost_to_notion(workflow, model, input_tokens, output_tokens, cached_tokens, cost_usd) -> None`:
   Archive copy of cost data to Notion Cost Log (Supabase is primary).

Use notion-sdk-py. Add to pyproject.toml.
Include retry logic (3 retries, exponential backoff). Rate limit: max 3 req/sec.

Commit: "feat: add notion_ops.py for wiki/Academy writes (operational HITL via dashboard)"
```

**Verify:**
- `pytest tests/test_notion_ops.py` — all tests pass (mock Notion API)
- Confirm notion_config.py reads from env vars with fallback defaults
- Confirm no task inbox or workflow registry functions exist (those go through dashboard)

---

### Prompt 1C: Shared Library — Org Resolver + Notifications + Cost Tracker

```
Read ORG.md and CLAUDE.md.

Create three modules in lib/ts_shared/:

1. `org.py`:
   - `load_org(org_path="ORG.md") -> dict[str, OrgRole]`: Parse ORG.md into Pydantic models
   - `resolve_role(role_id: str) -> OrgRole`: Get person, contact, language
   - OrgRole: person, location, contact_methods, language, approves, handles

2. `notifications.py`:
   - `send_slack(channel: str, text: str, blocks: list | None = None) -> bool`: Slack Web API. Read SLACK_BOT_TOKEN from env.
   - `send_slack_dm(user_id: str, text: str) -> bool`
   - `notify(role_id: str, message: str) -> bool`: Auto-select Slack for internal. Graceful degradation if token missing.

3. `cost_tracker.py`:
   - `log_invocation(workflow, skill_name, model, usage, latency_ms, trigger_source="cron", confidence=None, error=None) -> str`:
     Write to Supabase skill_invocations (primary) AND Notion Cost Log (archive copy).
     Calculate cost via claude_client.calculate_cost().
     Return invocation_id.

4. `views.py`:
   - `refresh_views(view_names: list[str])`: Refresh specified materialized views after data writes.

Add pydantic, slack-sdk to pyproject.toml.
Write tests for all modules.

Commit: "feat: add org resolver, notifications, cost tracker, view refresher"
```

**Verify:**
- `pytest tests/test_org.py tests/test_notifications.py tests/test_cost_tracker.py` — all pass
- `resolve_role("ceo")` returns OrgRole with language="English"
- `resolve_role("operations-manager")` returns OrgRole with language="Bahasa Indonesia"
- Notifications degrade gracefully when SLACK_BOT_TOKEN is missing (log warning, return False)

---

### Prompt 1D: Full Supabase Schema Migration (Three-Layer)

This is the critical merge point. It replaces the simple `pending_approvals` table with the full three-layer schema that the dashboard reads from and agents write to.

```
Read CLAUDE.md, ORG.md, and DEV-PLAN.md (this file — the schema definitions below).

Create a Supabase migration that establishes the three-layer schema:

REGISTRY LAYER (system metadata — what exists):
- companies (slug, name, status, config)
- agents (company_id, slug, name, status, definition file paths)
- skills (company_id, slug, name, skill_md_path, pattern, version, status)
- agent_skills (agent_id, skill_id, config_overrides)
- workflows (company_id, skill_id, slug, trigger_type, trigger_config, approval_required,
  approval_tier, default_assignee, default_priority, max_cost_per_run, monthly_budget, status)
- workflow_steps (workflow_id, step_order, slug, step_type, model, temperature,
  max_tokens, config, eval_criteria)

RUNTIME LAYER (execution data — what happened):
- task_inbox (company_id, workflow_id, agent_id, title, status, priority, assignee,
  output JSONB, output_rendered, feedback, feedback_by, feedback_at, wake_reason,
  cost_usd, run_id, due_at)
  Status values: 'needs_review', 'in_progress', 'approved', 'rejected', 'auto_logged'
- workflow_runs (workflow_id, agent_id, company_id, status, wake_reason,
  steps_completed, steps_total, current_step, step_results JSONB,
  input_tokens, output_tokens, total_cost_usd, model_used, error_message,
  error_step, started_at, completed_at, duration_ms)
- workflow_health (workflow_id, company_id, status, last_run_at, last_result,
  failures_7d, avg_cost_per_run, avg_duration_ms, success_rate_7d,
  override_rate_30d, notes)
- spend_records (period, period_type, company_id, workflow_id,
  run_count, success_count, failure_count, total_input_tokens,
  total_output_tokens, total_cost_usd, budget_usd, models_used)

EVAL LAYER (autoresearch — how good is it):
- eval_suites (workflow_id, skill_id, slug, name, test_cases JSONB,
  scoring_criteria JSONB, pass_thresholds JSONB, status)
- prompt_versions (workflow_id, workflow_step_id, version, system_prompt,
  user_prompt_template, model, temperature, max_tokens, few_shot_examples JSONB,
  hypothesis, parent_version_id, is_current)
- eval_runs (eval_suite_id, prompt_version_id, status, aggregate_scores JSONB,
  pass, total_cost_usd, total_tokens, compared_to_version_id, improvement_delta JSONB)
- eval_results (eval_run_id, test_case_index, input JSONB, expected_output JSONB,
  actual_output JSONB, scores JSONB, pass, evaluator_model, evaluator_reasoning,
  human_score_override JSONB, human_notes)

Include:
- Row Level Security policies (admin sees all companies, team sees own company)
- Realtime publication on task_inbox, workflow_health, workflow_runs
- Indexes on hot query paths:
  - task_inbox: status WHERE 'needs_review', (assignee, status), (company_id, status)
  - workflow_runs: status WHERE 'running', (workflow_id, started_at DESC)
  - spend_records: (period, company_id)
  - eval_runs: (eval_suite_id, started_at DESC)

Seed data:
- companies: tibetan-spirit (active), personal (active)
- Placeholder agents for tibetan-spirit: operations-manager, finance, marketing, customer-service

Also create `lib/ts_shared/dashboard_ops.py`:
- create_task(company_slug, workflow_slug, title, output, output_rendered,
  assignee, priority="P2", wake_reason="scheduled", cost_usd=0) -> str:
  Insert into task_inbox. Return task ID.
- update_task_status(task_id, status, feedback=None, feedback_by=None) -> None
- log_workflow_run(company_slug, workflow_slug, status, wake_reason,
  steps_completed, steps_total, step_results, input_tokens, output_tokens,
  total_cost_usd, model_used, error_message=None) -> str: Return run ID.
- update_workflow_health(workflow_slug, status, last_result,
  cost=None, duration_ms=None) -> None
- log_spend(period, period_type, company_slug, workflow_slug,
  run_count, success_count, failure_count, total_cost_usd) -> None

Write tests for dashboard_ops.py (mock Supabase).

Commit: "feat: three-layer Supabase schema with registry, runtime, eval + dashboard_ops.py"
```

**Verify:**
- Migration applies cleanly against Supabase
- `SELECT * FROM companies` → 2 rows (tibetan-spirit, personal)
- `SELECT * FROM agents WHERE company_id = (SELECT id FROM companies WHERE slug = 'tibetan-spirit')` → 4 agents
- Realtime enabled: `SELECT * FROM pg_publication_tables WHERE pubname = 'supabase_realtime'` includes task_inbox, workflow_health, workflow_runs
- `pytest tests/test_dashboard_ops.py` — all pass
- RLS: verify a non-admin auth token can only see rows matching their company_id

---

### Prompt 2A: Daily Summary Workflow

```
Read CLAUDE.md, ORG.md, skills/shared/brand-guidelines/SKILL.md, skills/shared/channel-config/SKILL.md.
Read lib/ts_shared/claude_client.py, dashboard_ops.py, cost_tracker.py, notifications.py.

Create `workflows/daily_summary/`:

1. `config.yaml`:
   name: daily_summary
   schedule: "0 18 * * *"  # 6pm Denver
   model: claude-haiku-4-5-20251001
   skills: [shared/brand-guidelines, shared/channel-config]
   requires_approval: false
   notify: [ceo]

2. `run.py`:
   - Query Supabase for today's orders (created_at >= today 00:00 UTC)
   - Calculate: order count, revenue, AOV, top 5 products by revenue
   - Flag: unfulfilled orders >24h old, unusually large orders (>$500)
   - Call Claude (Haiku) with loaded skills to format a Slack-friendly summary
   - Write to Supabase task_inbox via dashboard_ops.create_task() with status auto_logged
   - Write workflow_run via dashboard_ops.log_workflow_run()
   - Send Slack notification to ceo
   - Log cost via cost_tracker

3. Write test in tests/evals/test_daily_summary.py with mock data.

Commit: "feat: add daily_summary workflow — first end-to-end workflow"
```

**Verify:**
- `python workflows/daily_summary/run.py` executes against real Supabase data without errors
- `SELECT * FROM task_inbox ORDER BY created_at DESC LIMIT 1` → row exists with status='auto_logged', output JSONB non-empty
- `SELECT * FROM workflow_runs ORDER BY started_at DESC LIMIT 1` → status='completed', total_cost_usd > 0
- `pytest tests/evals/test_daily_summary.py` — passes with mock data
- Cost is reasonable: < $0.02 for a Haiku summary

---

### Prompt 2B: Weekly P&L Workflow

```
Read CLAUDE.md, skills/finance/cogs-tracking/SKILL.md, skills/finance/margin-reporting/SKILL.md.
Read all lib/ts_shared/ modules.

Create `workflows/weekly_pnl/`:

1. `config.yaml`:
   name: weekly_pnl
   schedule: "0 6 * * 1"  # Monday 6am Denver
   model: claude-sonnet-4-6
   requires_approval: true
   assignee: ceo

2. `run.py` — Three-step:
   Step 1 (pure Python): Query orders for past 7 days. Join with products for COGS.
   Query channel_profitability_monthly view. Calculate revenue, COGS, gross margin,
   fees, AOV. Compare to prior week.
   Step 2 (Sonnet): Format as CEO-ready P&L report with trends, top products,
   concerns, recommended actions.
   Step 3: Write to Supabase task_inbox via dashboard_ops.create_task()
   with status='needs_review', assignee='chris', priority='P2'.
   Log workflow_run and cost.

3. Write test in tests/evals/test_pnl_accuracy.py with fixture data.
   Test must verify: revenue sums match, margin calculations correct,
   week-over-week comparison logic handles edge cases (zero revenue week, etc.).

Commit: "feat: add weekly_pnl workflow with prompt chain and accuracy eval"
```

**Verify:**
- `python workflows/weekly_pnl/run.py` executes against real Supabase data
- `SELECT * FROM task_inbox WHERE status = 'needs_review' ORDER BY created_at DESC LIMIT 1` → P&L task exists
- Output JSONB contains: revenue, cogs, gross_margin, margin_pct, aov, week_over_week fields
- `pytest tests/evals/test_pnl_accuracy.py` — passes, especially numerical accuracy checks
- Cost: < $0.10 for a Sonnet analysis

---

### Chris Tasks (Sprint 1 — parallel with Claude Code)

1. **Create Slack workspace** — Install Slack app with Bot Token scopes: `chat:write`, `im:write`, `users:read`, `channels:read`. Create channels: `#ts-ops`, `#ts-customer-service`, `#ts-alerts`. Get `SLACK_BOT_TOKEN` → add to `.env` and Railway.

2. **Verify Railway deployment** — After Prompt 2A is committed, trigger a Railway deploy. Verify the build succeeds.

3. **Rotate Shopify token** — Go to Shopify Dev Dashboard → rotate client secret → re-run OAuth flow → update `.env` and Railway.

4. **Create Supabase auth users** — chris (admin role), jothi (member, company=tibetan-spirit), fiona (member, company=tibetan-spirit).

---

## Sprint 2: Dashboard Core + CS Pipeline

Two parallel tracks. Dashboard must be usable by end of sprint — Chris can approve/reject from phone.

### Dashboard Track

#### Prompt D-1: Next.js Scaffold + Supabase Connection

```
Initialize a new Next.js 15 project in a separate repo (ts-command-center/):

npx create-next-app@latest ts-command-center --typescript --tailwind --eslint --app --src-dir

Install: @supabase/ssr, @supabase/supabase-js, recharts, @radix-ui/themes,
next-intl, zod, date-fns

Set up:
1. Supabase client (server + client components)
2. Auth with Supabase Auth (email/password — 3 users: chris, jothi, fiona)
3. Middleware for auth protection
4. Layout with company selector in header (reads from companies table).
   Chris sees all companies. Team members see only their company.
   Selector persists selection to localStorage and filters all views.
5. PWA manifest.json + service worker registration (offline task queue viewing)
6. next-intl with English (default), Chinese, Bahasa Indonesia locale files

Deploy to Vercel. Verify Supabase Realtime connection works.

Commit: "feat: Next.js scaffold with Supabase auth, i18n, PWA"
```

**Verify:**
- App deploys to Vercel without errors
- Login works for chris, jothi, fiona
- Company selector shows: Tibetan Spirit, Personal
- Chris can switch between companies; Jothi sees only Tibetan Spirit
- Realtime test: insert a row into task_inbox via SQL, verify it appears in browser console subscription

---

#### Prompt D-2: Task Inbox (Priority 1 — HITL Approval Queue)

```
Build the Task Inbox — this is the most critical view. Phone-first approval
queue that Chris checks multiple times daily.

Pages:
  /inbox — List view
  /inbox/[id] — Detail view with approve/reject

List view (/inbox):
- Card view on mobile, table on desktop
- Filters: status (Needs Review default), company, assignee, priority, workflow
- Sort: priority (P0 first) → created_at (newest)
- Realtime: subscribe to task_inbox inserts/updates via Supabase Realtime
- Badge count in nav showing "Needs Review" count
- Quick-action buttons: Approve / Reject without opening detail

Detail view (/inbox/[id]):
- Rendered output (output_rendered field, or formatted JSONB)
- Properties sidebar: status, priority, assignee, workflow, cost, created_at
- Approve button → sets status='approved', feedback_by=current_user, feedback_at=now()
- Reject button → opens feedback textarea, then sets status='rejected'
- Edit button → opens inline editor for output modifications before approval
  (if modified, save edited version to feedback field)
- Metadata: wake_reason, cost_usd, link to workflow run

Mobile optimization:
- Large tap targets (48px minimum)
- Swipe gestures if feasible (right=approve, left=reject)
- Bottom nav bar (Inbox, Health, Costs, More)

Company selector in header filters inbox to selected company.

Commit: "feat: task inbox with approve/reject, realtime, mobile-first"
```

**Verify:**
- Insert a test task via SQL: `INSERT INTO task_inbox (company_id, title, status, priority, assignee, output, output_rendered) VALUES (...)` → appears in dashboard within 2 seconds (Realtime)
- Approve flow: click Approve → status changes to 'approved' in Supabase, page updates
- Reject flow: click Reject → feedback modal appears → submit → status 'rejected' with feedback text in Supabase
- Mobile: load on phone-sized viewport, all buttons tappable, layout readable
- Company filter: switch to "Personal" → inbox shows only personal company tasks
- Badge count: matches `SELECT count(*) FROM task_inbox WHERE status = 'needs_review' AND company_id = ...`

---

#### Prompt D-3: System Health + Cost Tracker + Home

```
Three more dashboard views:

System Health (/health):
- Grid of workflow cards, one per active workflow
- Card shows: name, status badge (green/yellow/red), last run time, 7d success rate
- Click → detailed view with recent runs and error messages
- Auto-refresh via Supabase Realtime on workflow_health changes
- "Degraded" = ran but with warnings; "Down" = last run failed

Cost Tracker (/costs):
- Recharts AreaChart: daily cost over past 30 days, stacked by company
- Budget progress bars per workflow (spend_records.total_cost_usd / budget_usd)
- Toggle: this week / this month / last 30 days
- Table: top workflows by cost, sortable

Dashboard Home (/):
- Four-quadrant layout:
  1. Needs Attention (task_inbox count by priority)
  2. System Status (workflow_health traffic lights)
  3. Weekly Spend (cost summary + budget %)
  4. Recent Activity (latest workflow_runs)
- Company selector filters all quadrants

Commit: "feat: health dashboard, cost tracker, home overview"
```

**Verify:**
- Health page: workflow cards render for seeded workflows. Click one → shows run history (empty initially, populated after workflows run)
- Cost page: chart renders (may be empty initially). Budget bars show 0% progress with correct budget ceilings from workflow config
- Home page: all four quadrants render. Switching company in selector filters data in all quadrants
- Realtime: update workflow_health via SQL → card color changes without page refresh

---

### Workflow Track (parallel with dashboard)

#### Prompt 2C: CS Email Drafts Workflow

```
Read CLAUDE.md, ORG.md, skills/customer-service/ticket-triage/SKILL.md,
skills/shared/brand-guidelines/SKILL.md, skills/shared/product-knowledge/SKILL.md,
skills/shared/escalation-matrix/SKILL.md.

Create `workflows/cs_email_drafts/`:

1. `config.yaml`:
   name: cs_email_drafts
   schedule: "*/30 8-18 * * *"  # Every 30 min during business hours
   model_triage: claude-haiku-4-5-20251001
   model_draft: claude-sonnet-4-6
   requires_approval: true
   assignee: customer-service-lead  # Falls back to operations-manager until hire

2. `run.py` — Three-step chain:
   Step 1 TRIAGE (Haiku): Classify each new ticket.
   Return {category, priority, route_to_role, summary}.
   Step 2 ENRICH: Look up customer order history in Supabase. Load relevant domain skill.
   Step 3 DRAFT (Sonnet): Generate response following brand guidelines.
   Warm, respectful, knowledgeable.
   Step 4 OUTPUT: Write to task_inbox via dashboard_ops. Send Slack alert.

3. For email ingestion: First confirm with Chris which helpdesk was chosen
   (Intercom or Zendesk) and get the API credentials. Then check HELPDESK_PLATFORM env var.
   If 'intercom': use Intercom API to fetch new conversations.
   If 'zendesk': use Zendesk API to fetch new tickets.
   If not set: fall back to Supabase `cs_inbox` table (test mode).
   For output: post approved draft as internal note on the helpdesk conversation.
   CS lead reviews and sends from helpdesk UI.

4. Create `scripts/import_test_emails.py` with 10 sample emails across categories:
   order status, product question, return request, practice inquiry, complaint,
   shipping delay, wholesale inquiry, product recommendation, damaged item, gratitude.

5. Write eval: tests/evals/test_cs_drafts.py — verify triage accuracy, brand compliance.

Commit: "feat: add cs_email_drafts workflow with triage→enrich→draft chain"
```

**Verify:**
- Run `scripts/import_test_emails.py` → 10 test emails in cs_inbox table
- `python workflows/cs_email_drafts/run.py` → processes test emails, creates task_inbox entries
- Triage accuracy: at least 8/10 test emails classified to correct category
- Draft quality: spot-check 3 drafts for brand voice (no "exotic", no "mystical", Buddhist terms untranslated)
- Escalation: practice inquiry routes to spiritual-director, refund >$100 routes to ceo
- `pytest tests/evals/test_cs_drafts.py` — passes

---

#### Prompt 2.5A: Customer Profiles + RFM Scoring

```
Read CLAUDE.md and the orders table schema.

Create `scripts/build_customer_profiles.py`:

1. Add Supabase migration for `customer_profiles`:
   email (unique), first/last_order_date, order_count, lifetime_value, avg_order_value,
   top_categories (jsonb), segment (text), rfm_score (text),
   rfm_recency/frequency/monetary (int 1-5),
   ticket_count (int, default 0), sentiment_score (numeric)

2. Query all orders grouped by email. Calculate RFM quintiles.
3. Heuristic segments: practicing_buddhist, wellness_seeker, gift_buyer, unknown.
4. Upsert all profiles. Print summary.

Commit: "feat: build customer_profiles with RFM scoring from 19K orders"
```

**Verify:**
- `SELECT count(*) FROM customer_profiles` → thousands of profiles (one per unique email)
- `SELECT segment, count(*) FROM customer_profiles GROUP BY 1` → reasonable distribution across segments
- `SELECT * FROM customer_profiles ORDER BY lifetime_value DESC LIMIT 5` → top customers have high LTV, high frequency
- RFM scores: `SELECT rfm_score, count(*) FROM customer_profiles GROUP BY 1 ORDER BY 1` → scores like "555", "111" etc with distribution

---

#### Prompt 3B: Inventory Alerts Workflow

```
Read CLAUDE.md, skills/operations/inventory-management/SKILL.md, skills/shared/channel-config/SKILL.md.

Create `workflows/inventory_alerts/`:

1. `run.py`:
   Step 1: Query Shopify API for current inventory levels → sync to Supabase inventory_extended.
   Step 2: Compare each SKU against reorder_trigger_qty. Flag stockouts, critical, reorder-needed.
   Step 3 (Sonnet): Generate priority-sorted alert list with suggested POs.
   Step 4: Write to task_inbox (assignee=operations-manager, priority based on severity).
   Send Slack alert. If stockouts, also alert ceo.

2. Create `scripts/sync_shopify_inventory.py` as a reusable sync utility.

Commit: "feat: add inventory_alerts workflow with Shopify sync and reorder generation"
```

**Verify:**
- `python scripts/sync_shopify_inventory.py` → populates inventory_extended table
- `SELECT count(*) FROM inventory_extended` → matches Shopify product count
- `SELECT * FROM inventory_health WHERE stock_status IN ('stockout', 'critical') LIMIT 10` → materialized view returns meaningful data
- `python workflows/inventory_alerts/run.py` → creates task_inbox entries for low-stock items
- Task assignee is 'operations-manager' (not hardcoded name)

---

### Chris Tasks (Sprint 2)

1. **Test dashboard end-to-end** — Open the Vercel deployment on phone. Approve a daily_summary task. Reject a P&L task with feedback. Verify status changes propagate.
2. **Review COGS estimates** — Spot-check seeded COGS data against real supplier invoices.
3. **Set up helpdesk** — Create Intercom or Zendesk account, connect Shopify store, get API credentials → add to `.env`.

---

## Sprint 3: More Workflows + Dashboard Management

### Workflow Track

#### Prompt 4A: Campaign Brief Generator

```
Create `workflows/campaign_brief/`:
- Weekly schedule. Sonnet model. CEO approval.
- Pull top 20 products by revenue (30 days), seasonal context from tibetan-calendar skill,
  inventory surplus from inventory_extended.
- Generate: campaign theme, target segment, subject lines, body outline,
  product selection, send date.
- Write to task_inbox via dashboard_ops.

Commit: "feat: add campaign_brief workflow"
```

**Verify:**
- `python workflows/campaign_brief/run.py` → creates task_inbox entry with status='needs_review'
- Output JSONB contains: theme, target_segment, subject_lines (array), products (array with SKUs)
- Products referenced actually exist in Supabase products table
- Cost: < $0.15 for a Sonnet generation

---

#### Prompt 4B: Product Description Optimizer (Evaluator-Optimizer)

```
Create `workflows/product_descriptions/`:
- Manual trigger. Sonnet model. CEO + operations-manager approval.
- Evaluator-optimizer loop:
  Generator → Evaluator (rubric: SEO, conversion, brand voice, accuracy, readability)
  → if any dimension <7, feed back and regenerate → max 3 iterations.
- Batch mode via Anthropic Batch API for overnight processing.

Commit: "feat: add product_descriptions evaluator-optimizer workflow"
```

**Verify:**
- Run on 3 test products: `python workflows/product_descriptions/run.py --product-ids X,Y,Z`
- Each product gets a task_inbox entry with the final description
- Eval scores visible in output JSONB (per-dimension scores, iteration count)
- No description uses "exotic" or "mystical" (brand voice check)
- Buddhist terms (mala, thangka, dharma, sangha) remain untranslated

---

#### Prompt 4C: Reliability Pass

```
Run reliability audit across all workflows:
1. Verify all imports resolve.
2. Verify Supabase queries reference valid tables/columns (use validate_cross_refs.py).
3. Run all eval suites.
4. Create scripts/run_all_workflows.py orchestrator that runs each workflow's run.py
   with --dry-run flag (loads data, skips API calls, validates pipeline).
5. Update workflow_health entries for all workflows.

Commit: "feat: reliability audit — all workflows tested"
```

**Verify:**
- `python scripts/run_all_workflows.py --dry-run` → all workflows complete without import errors
- `python scripts/validate_cross_refs.py` → zero violations
- `pytest tests/evals/` → all eval suites pass
- `SELECT slug, status FROM workflow_health` → all active workflows show 'healthy'

---

### Dashboard Track

#### Prompt D-4: Workflow & Agent Registry

```
Build the management views:

Workflow Registry (/workflows):
- List all workflows with: name, company, trigger type, status, approval tier, last run
- Filter by company, status
- Click → workflow detail

Workflow Detail (/workflows/[id]):
- Header: name, description, trigger config, approval settings
- Steps table: ordered list of workflow_steps showing step_type, model, temperature
  Color-code by step type (gate=gray, reasoning=blue, template=green, eval=purple, tool-call=orange)
- Run History: last 20 workflow_runs with status, cost, duration
- Link to eval dashboard (placeholder for Sprint 4)

Agent Registry (/agents):
- List all agents with: name, company, status, skill count
- Click → agent detail

Agent Detail (/agents/[id]):
- Description, status, company
- Assigned skills list (from agent_skills join)
- Recent workflow_runs involving this agent
- Cost summary (30-day)

Commit: "feat: workflow registry, agent registry, management views"
```

**Verify:**
- /workflows shows all seeded workflows with correct trigger types and approval tiers
- Click a workflow → steps table renders with color-coded step types
- /agents shows 4 TS agents with correct skill counts
- Company filter works: selecting "Personal" shows only personal agents/workflows
- Run history table populates after workflows have run (may be empty on first load)

---

### Chris Tasks (Sprint 3)

1. **Review campaign brief output** — Approve or reject in dashboard. Provide feedback.
2. **Review product descriptions** — Compare AI vs current. Flag cultural sensitivity issues.
3. **Railway cron setup** — Configure cron services for all ready workflows.

---

## Sprint 4: Wiki Deepening + Eval Dashboard

**This sprint has two tracks that can be done by separate agent teams.**

### Track A: Wiki Deepening (Separate Agent Team)

The 56 SKILL.md files are currently at ~35% depth. Deepen them to production quality.

**Priority order by workflow dependency:**

**Tier 1 — Blocks active workflows (deepen first):**
- `shared/brand-guidelines`, `shared/product-knowledge`, `shared/escalation-matrix`, `shared/channel-config`
- `customer-service/ticket-triage`
- `finance/cogs-tracking`, `finance/margin-reporting`
- `operations/inventory-management`

**Tier 2 — Enables next wave:**
- `customer-service/order-inquiry`, `product-guidance`, `return-request`, `practice-inquiry`
- `marketing/meta-ads`, `google-ads`, `performance-reporting`
- `operations/fulfillment-domestic`, `supplier-communication`

**Tier 3 — Future channel expansion:**
- `ecommerce/*`, `category-management/*`, remaining `finance/*`

**Production quality means:** decision trees with thresholds, 3-5 response templates, Supabase query references, escalation rules matching ORG.md, anti-patterns with examples, cultural sensitivity rules. Keep under 500 lines per skill.

**Verify per skill:**
- `python scripts/validate_skill.py skills/{category}/{skill-name}/SKILL.md` → passes
- Frontmatter version bumped to "1.0.0"
- Decision trees have specific dollar/time thresholds (not vague)
- Response templates are complete examples, not outlines

---

### Track B: Eval Dashboard

#### Prompt D-5: Eval Dashboard (Autoresearch UI)

```
Build the eval/autoresearch interface:

Eval Dashboard (/workflows/[id]/eval):
- Eval suite selector (if multiple suites exist for this workflow)
- Test cases table: input, expected output, latest score per criterion
- Prompt version history: timeline of versions with aggregate scores
  Recharts LineChart showing score trends over versions
- "Run Eval" button: triggers eval run against current prompt version
- Override rate chart: 30-day trend of human modifications to workflow outputs

Prompt Version Detail (/workflows/[id]/eval/versions/[versionId]):
- Full prompt text (system + user template)
- Configuration: model, temperature, max_tokens, few-shot examples
- Score breakdown per criterion with evaluator reasoning

Eval Run Detail (/workflows/[id]/eval/runs/[runId]):
- Per-test-case results table
- Scores with evaluator reasoning
- Human override column
- Cost summary

Commit: "feat: eval dashboard with autoresearch UI, version comparison"
```

**Verify:**
- Page loads without errors even with empty eval tables
- If eval_suites exist: test case table renders, scores display
- Override rate chart: `SELECT * FROM workflow_health WHERE override_rate_30d IS NOT NULL` → chart renders
- Version history: LineChart renders with at least 2 data points if prompt_versions exist

---

#### Prompt D-6: Settings + Final Polish

```
Settings (/settings):
- Company management (add/edit companies — Chris only)
- Notification preferences per user (Slack, push)
- Override rate threshold configuration (global + per-workflow-type)
- Environment status: show which API keys are configured (masked values with "configured" badge)

Final polish:
- 404 page for invalid routes
- Loading states on all data fetches
- Error boundaries with user-friendly messages
- PWA offline support: cache task_inbox for offline viewing

Commit: "feat: settings page, error handling, offline support"
```

**Verify:**
- /settings loads, shows company list
- Adding a new company inserts into Supabase companies table
- Environment status shows configured/unconfigured for each integration
- Offline: enable airplane mode → cached inbox still viewable
- Navigate to /nonexistent → 404 page renders

---

### Final Documentation (After Sprint 4)

```
Read the entire codebase. Generate the following:

1. REGENERATE `CLAUDE.md` as the definitive codebase navigation document:
   - Actual file tree with one-line descriptions
   - How to run each workflow (exact commands)
   - Complete env var list
   - Architecture as-built (dashboard + agents + Supabase)
   - Database schema summary (all three layers)
   - Dashboard pages and what they show
   - Skill loading pattern
   - Model routing
   - Cultural context (keep the Buddhist sensitivity section)
   - Team & ORG.md
   Keep under 300 lines.

2. CREATE `.env.example` at repo root with all env vars documented.

3. UPDATE `SYSTEM-STATUS.md` to reflect post-implementation state.

Commit: "docs: regenerate CLAUDE.md, create .env.example, update system status"
```

---

## Post-Sprint 4: Chatbot + On-Site Experience

Deferred to post-MVP. Requires Railway web service deployment (always-on, $5-10/month).

The spec is in `temp/planning/` for reference. Key elements:
- Stateless chat handler in `workflows/chatbot/run.py`
- API endpoint: POST /api/chat in `server/server.py`
- Tools: order_lookup, product_search, faq_lookup
- Escalation: confidence < 0.7, refund/complaint → CS, practice question → spiritual-director
- Shopify Liquid widget snippet

---

## Academy Module Generation (Sprint 4 scope — M01-M04 only)

The full Academy has 37 modules (M01-M37) across 8 sections: Foundation (M01-M04), Operations (M05-M10), Digital Marketing Fundamentals (M11-M14), Channels: Meta (M15-M21), Channels: Google (M22-M26), Channels: Email/Klaviyo (M27-M31), AI-Assisted Operations (M32-M34), Photography & Creative (M35-M37). Full TOC with module descriptions is in `temp/planning/ts-ops-action-plan-v2-renameacademytowiki.md`.

**For MVP, build only M01-M04 (Foundation).** Jothi learns faster by doing supervised real work. Defer M05-M37 to post-launch.

```
Create `scripts/generate_academy_module.py`:
- Takes module ID (e.g., "M01") and generates content using Claude + real Supabase data
- Output: Notion page content (pushed via Notion API through notion_ops.py)

Generate M01-M04 (Foundation):
- M01: The Business of Tibetan Spirit
- M02: Our Products & Their Significance
- M03: How Orders Flow
- M04: The AI Operations System (what the workflows do, how to review in dashboard)

Commit: "feat: add Academy module generator, create M01-M04 Foundation modules"
```

---

## Override Rate: The Master Metric

Override rate measures how often a human modifies or rejects an AI workflow's output before it goes live.

```
override_rate = (rejected + modified) / total_reviewed × 100
```

**Starting threshold: 25% flat** for all workflows. Intentionally generous — no historical data to calibrate against. Buddhist content sensitivity means some "overrides" are refinements, not failures.

**Future per-category thresholds (after 90+ days of data):**
- Financial workflows: 5-10%
- Operational workflows: 10-15%
- Content/Creative workflows: 20-30%
- Cultural/Spiritual content: Human review always (non-negotiable)

**Workflow graduation:**
- Tier 3 (explicit approval): All new workflows start here
- Tier 2 (draft + 4hr auto-approve): Graduate when override rate < 25% for 30+ days
- Tier 1 (auto-execute, log only): Graduate when override rate near-zero for extended period

Computed automatically from task_inbox status transitions. Stored in `workflow_health.override_rate_30d`.

---

## Dependency Graph

```
Sprint 1 (Foundation — all sequential)
├── 0A: ORG.md + skill refactor + lib path flatten
├── 0C: Seed COGS data
├── 1A: Claude client + model constants
├── 1B: Notion client (wiki/Academy scope only)
├── 1C: Org resolver + notifications + cost tracker
├── 1D: Full 3-layer Supabase schema + dashboard_ops.py ← CRITICAL MERGE POINT
├── 2A: Daily summary workflow (first end-to-end)
└── 2B: Weekly P&L workflow (first approval-required workflow)

Sprint 2 (Two parallel tracks — requires Sprint 1 complete)
  DASHBOARD TRACK:              WORKFLOW TRACK:
  ├── D-1: Next.js scaffold     ├── 2C: CS email drafts
  ├── D-2: Task Inbox            ├── 2.5A: Customer profiles
  └── D-3: Health + Costs        └── 3B: Inventory alerts
         + Home page

Sprint 3 (Two parallel tracks — requires Sprint 2 complete)
  DASHBOARD TRACK:              WORKFLOW TRACK:
  └── D-4: Workflow + Agent      ├── 4A: Campaign brief
       Registry                  ├── 4B: Product descriptions
                                 └── 4C: Reliability pass

Sprint 4 (Two parallel tracks — can start after Sprint 1 for wiki)
  DASHBOARD TRACK:              WIKI DEEPENING TRACK:
  ├── D-5: Eval dashboard       ├── Tier 1 skills (8 skills)
  └── D-6: Settings + polish    ├── Tier 2 skills (10 skills)
                                └── Tier 3 skills (remaining)
```

---

## Environment Variables

The `.env` file already contains `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `ANTHROPIC_API_KEY`, `SHOPIFY_API_TOKEN`, and `SHOPIFY_WEBHOOK_SECRET`. Do not recreate these.

```bash
# ALREADY IN .env — do not duplicate:
# SUPABASE_URL, SUPABASE_SERVICE_KEY, ANTHROPIC_API_KEY, SHOPIFY_API_TOKEN, SHOPIFY_WEBHOOK_SECRET

# ADD for Sprint 1 — Notion (wiki/Academy only)
NOTION_API_KEY=...

# ADD for Sprint 1 — internal notifications
SLACK_BOT_TOKEN=...
SLACK_CHANNEL_OPS=#ts-ops
SLACK_CHANNEL_CS=#ts-customer-service
SLACK_CHANNEL_ALERTS=#ts-alerts

# ADD for Sprint 2 — dashboard (separate repo env)
NEXT_PUBLIC_SUPABASE_URL=...
NEXT_PUBLIC_SUPABASE_ANON_KEY=...
SUPABASE_SERVICE_ROLE_KEY=...

# ADD for Sprint 2 — helpdesk (Intercom or Zendesk — Chris to set up)
HELPDESK_PLATFORM=intercom  # or 'zendesk'
HELPDESK_API_KEY=...
HELPDESK_API_SECRET=...

# ADD later — graceful degradation if missing
KLAVIYO_API_KEY=...
META_ADS_ACCESS_TOKEN=...
GOOGLE_ADS_DEVELOPER_TOKEN=...
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
```

---

## File Organization (Target State)

```
tibetan-spirit-ops/                    ← This repo (Python workflows + skills)
├── CLAUDE.md                          ← Project instructions (regenerated after Sprint 4)
├── ORG.md                             ← Role-based org chart
├── SYSTEM-STATUS.md                   ← Live technical reference
├── DEV-PLAN.md                        ← This file
├── pyproject.toml
├── .env                               ← Credentials (never committed)
├── .gitignore
│
├── lib/ts_shared/                     ← Shared Python library
│   ├── __init__.py
│   ├── supabase_client.py             ← Singleton Supabase connection (exists)
│   ├── claude_client.py               ← Skill loading + Anthropic API + caching
│   ├── dashboard_ops.py               ← Write to Supabase runtime tables (task_inbox, workflow_runs, etc.)
│   ├── notion_config.py               ← Database IDs for wiki/Academy (exists, narrowed)
│   ├── notion_ops.py                  ← Wiki/Academy writes only
│   ├── org.py                         ← ORG.md parser + role resolver
│   ├── notifications.py               ← Slack + graceful degradation
│   ├── cost_tracker.py                ← Supabase (primary) + Notion (archive)
│   ├── logging_utils.py               ← Audit trail logging (exists)
│   └── views.py                       ← Materialized view refresh helper
│
├── workflows/                         ← Each workflow = standalone cron job
│   ├── daily_summary/config.yaml + run.py
│   ├── weekly_pnl/
│   ├── cs_email_drafts/
│   ├── inventory_alerts/
│   ├── campaign_brief/
│   └── product_descriptions/
│
├── agents/                            ← AI team (Paperclip-inspired structure)
│   ├── shared/                        ← Cross-agent skills: brand, products, escalation, channels, DB, calendar
│   ├── customer-service/              ← soul.md + config.yaml + skills/ (6 skills)
│   ├── operations/                    ← soul.md + config.yaml + skills/ (8 skills)
│   ├── finance/                       ← soul.md + config.yaml + skills/ (7 skills)
│   ├── marketing/                     ← soul.md + config.yaml + skills/ (15 skills)
│   ├── ecommerce/                     ← soul.md + config.yaml + skills/ (8 skills)
│   └── category-management/           ← soul.md + config.yaml + skills/ (8 skills)
│
├── scripts/                           ← Utility scripts
│   ├── backfill_shopify.py            ← (exists, tested)
│   ├── import_orders_csv.py           ← (exists, tested)
│   ├── seed_cogs_from_model.py
│   ├── build_customer_profiles.py
│   ├── sync_shopify_inventory.py
│   ├── validate_*.py                  ← (exist, tested)
│   └── run_all_workflows.py
│
├── server/                            ← FastAPI (future webhook/chatbot endpoint)
│   ├── server.py                      ← 326 lines, not deployed yet
│   ├── Dockerfile
│   └── requirements.txt
│
├── tests/
│   ├── test_*.py                      ← Unit tests
│   ├── evals/                         ← Workflow evaluation suites
│   └── fixtures/                      ← Test data
│
├── data/                              ← Local data assets (gitignored)
└── temp/                              ← Historical planning docs (gitignored)

ts-command-center/                     ← Separate repo (Next.js dashboard on Vercel)
├── src/app/                           ← App Router pages
│   ├── page.tsx                       ← Dashboard home (4-quadrant overview)
│   ├── inbox/                         ← Task Inbox (approve/reject)
│   ├── health/                        ← Workflow Health (traffic lights)
│   ├── costs/                         ← Spend Tracker (charts)
│   ├── workflows/                     ← Workflow Registry + Detail + Eval
│   ├── agents/                        ← Agent Registry + Detail
│   └── settings/                      ← Company management, notification prefs
├── src/lib/                           ← Supabase client, utils
├── public/                            ← PWA manifest, icons
└── messages/                          ← i18n locale files (en, zh, id)
```

---

## Open Decisions (Chris to resolve)

1. **Helpdesk platform** — Narrowed to **Intercom or Zendesk**. Chris to set up account, connect Shopify store, and get API credentials before Sprint 2. Both have strong APIs, Shopify integrations, chat widgets, and built-in knowledge bases that replace the Notion public wiki. The agent building Prompt 2C should confirm with Chris which platform was chosen before writing the integration. Env vars: `HELPDESK_PLATFORM` (intercom/zendesk), `HELPDESK_API_KEY`, `HELPDESK_API_SECRET`.
2. **CS hire timeline** — Until hire, CS approvals route to operations-manager.
3. **Chatbot scope** — Deferred to post-Sprint 4. Confirm acceptable.
4. **Supabase plan** — Free tier has 2 Realtime connections. Dashboard needs Realtime for task_inbox, workflow_health, workflow_runs. Pro ($25/mo) recommended from day 1.
5. **Vercel plan** — Hobby (free) works for dev. Pro ($20/mo) needed when Jothi/Fiona need access.
6. **Slack workspace** — Does it exist yet? Bot token available? Needed for Sprint 1.
7. **Financial model precision** — Keep category-level COGS estimates until volume justifies per-product refinement from supplier invoices?

---

## Key Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Shopify API rate limits during batch operations | Workflow failures | Rate-aware queuing in shared lib; batch requests |
| Nepal supplier invoice data inconsistent | Bad COGS, wrong margins | Phase 1 COGS are estimates; human validation of confirmed COGS entries |
| Claude API outage during order processing | Orders queue up | Retry logic; orders preserved in Shopify (source of truth) |
| Solo operator bandwidth | Can't build everything at once | Strict sprint ordering — don't start Sprint 3 before Sprint 2 targets met |
| Supabase free tier Realtime limits (2 connections) | Dashboard can't subscribe to multiple tables | Upgrade to Pro ($25/mo) before dashboard goes live |
| Creative fatigue on ad campaigns | Declining ROAS | See performance marketing playbook; 10-15 active ads, refresh 2-4/week |

---

## Future Integrations (Not in MVP, Graceful Degradation)

These integrations are scaffolded with env var checks. If credentials are missing, workflows log a warning and continue without them.

| Integration | Env Var | When Needed | Purpose |
|---|---|---|---|
| **Klaviyo** | `KLAVIYO_API_KEY` | Post-Sprint 4 (email marketing) | Campaign triggers, abandoned cart flows, segment sync from customer_profiles |
| **Meta Marketing API** | `META_ADS_ACCESS_TOKEN` | Performance marketing phase | Ad performance data, creative fatigue monitoring |
| **Google Ads API** | `GOOGLE_ADS_DEVELOPER_TOKEN` | Performance marketing phase | Shopping campaign management, search term audits |
| **Twilio (WhatsApp)** | `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN` | When Nepal supplier comms workflow is built | WhatsApp messages to suppliers only |
| **Langfuse** | `LANGFUSE_PUBLIC_KEY` | Phase 2 observability | Trace visualization, prompt versioning, cost tracking |

---

## Reference Documents (in `temp/planning/`)

These historical planning docs are archived but remain useful references:

| File | Contains |
|------|----------|
| `ts-ops-dashboard-build-spec.md` | Full three-layer Supabase schema DDL (Parts 1A-1E), scoring criteria reference, agent definition convention, autoresearch system spec |
| `ts-performance-marketing-playbook.md` | Complete beginner's guide to performance marketing: Meta Ads, Google Ads, Pinterest, Etsy, Klaviyo flows, subscription economics, budget allocation, testing frameworks, metrics glossary |
| `ts-ops-action-plan-v2-renameacademytowiki.md` | Full Academy TOC (37 modules M01-M37), Jothi onboarding schedule, daily rhythm, supplier names, HITL gate reference |
| `TS-OPS-REFINED-PLAN.md` | Original Claude Code prompts, QA checkpoints, execution strategy |
| `TS-OPS-PLAN-ADDENDUM.md` | Locked decisions: Railway consolidated, Re:amaze recommendation, Slack over WhatsApp, CS role, Shopify Growth plan |
| `HANDOFF-AGENT-PROMPT.md` | Agent handoff context, critical feedback overrides, helpdesk architecture options |
| `temp/research/SKILL_METADATA_RESEARCH.md` | Cross-framework research (Anthropic, LangChain, CrewAI, Semantic Kernel, OpenAI, Dust.tt, Relevance AI): three-tier loading, extended frontmatter, cost/cache/observability metadata, input/output schemas |
| `temp/research/SKILL_METADATA_IMPLEMENTATION.md` | Phased implementation guide: minimum viable schema, per-category guidance, validation patterns, common mistakes |
| `temp/research/SKILL_METADATA_MATRIX.md` | Comparison matrix of metadata fields across 7 frameworks, field prioritization tiers |

The full DDL for the three-layer schema (registry, runtime, eval) referenced by Prompt 1D is in `temp/planning/ts-ops-dashboard-build-spec.md` (Parts 1A through 1E).
