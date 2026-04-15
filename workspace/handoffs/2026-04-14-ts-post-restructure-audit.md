# Post-Restructure Audit + Skills Gap Analysis
**Date:** 2026-04-14
**Branch:** refactor/align-repo-conventions (merge to main first, then fresh branch for audit work)
**For:** Fresh Claude Code session

---

## Context

The `refactor/align-repo-conventions` branch completed a major repo restructure to align tibetan-spirit-ops with OB2 project-scaffold conventions. Changes included:

- Workspace scaffolded at `workspace/` (research/, results/, handoffs/, archive/)
- Legacy docs consolidated: `DEV-PLAN.md` → `workspace/plans/`, `ORG.md` → `.claude/rules/org-roles.md`
- `docs/ARCHITECTURE.md` and `docs/CHANGELOG.md` created
- 4 missing agent definitions created in `.claude/agents/` (fulfillment-manager, inventory-analyst, marketing-strategist, catalog-curator)
- 6 new domain rules files created in `.claude/rules/` (brand-voice, cultural-sensitivity, org-roles, shopify-api, cs-judgment, finance-judgment, marketing-discipline, operations-protocols, ecommerce-judgment, category-judgment)
- Legacy `agents/` directory archived to `_archive/agents-legacy/`
- Python scripts in `workflows/` moved to `scripts/`, configs archived to `_archive/workflows-legacy/`
- `CLAUDE.md` refreshed, `.env.example` created, `.gitignore` updated
- `.claude/settings.json` updated to auto-allow `.claude/**` operations

This audit exists because a major restructure done in a single long session may have produced inconsistencies: stale path references, CLAUDE.md claims that don't match actual file structure, agent definitions that don't meet quality standards, and skills/workflows that haven't been rewritten yet.

---

## Phase A: Structural Audit (read-only first pass)

Start by reading `CLAUDE.md`, `docs/ARCHITECTURE.md`, and `workspace/plans/DEV-PLAN.md` (first 100 lines) to establish the expected structure. Then verify each item below.

### Checklist

**Repo structure**
- [ ] `workspace/` exists with subdirs: `plans/`, `research/`, `results/`, `handoffs/`, `archive/`
- [ ] `docs/` contains: `ARCHITECTURE.md`, `CHANGELOG.md` (check for `OPERATIONS-REFERENCE.md` — if missing, note it as a gap)
- [ ] `scripts/` contains workflow Python scripts (daily_summary.py, weekly_pnl.py at minimum)
- [ ] `_archive/` contains: `agents-legacy/`, `workflows-legacy/` (legacy content safely stored)
- [ ] `lib/ts_shared/` exists as the shared library path (DEV-PLAN calls for flattened path from `lib/shared/src/ts_shared/`)

**CLAUDE.md accuracy**
- [ ] All file paths referenced in CLAUDE.md actually exist on disk (spot-check: `.claude/agents/`, `.claude/rules/`, `workspace/plans/DEV-PLAN.md`, `docs/ARCHITECTURE.md`)
- [ ] Agent roster in CLAUDE.md matches files in `.claude/agents/` (should be 6: cs-drafter, finance-analyst, fulfillment-manager, inventory-analyst, marketing-strategist, catalog-curator)
- [ ] Rules list in CLAUDE.md matches files in `.claude/rules/` (should be 10: brand-voice, cultural-sensitivity, org-roles, shopify-api, cs-judgment, finance-judgment, marketing-discipline, operations-protocols, ecommerce-judgment, category-judgment)

**.claude/ contents**
- [ ] `.claude/agents/` has exactly 6 .md files — no extras, no missing
- [ ] `.claude/skills/` has: `cs-triage/SKILL.md`, `shopify-query/SKILL.md` — verify `act-on-approved/SKILL.md` exists or note as missing
- [ ] `.claude/rules/` has exactly 10 .md files
- [ ] `.claude/settings.json` is valid JSON: `python3 -c "import json; json.load(open('.claude/settings.json'))"`
- [ ] `.claude/hooks/` exists with `budget-check.sh` and `log-activity.sh` (referenced in ARCHITECTURE.md) — if missing, note as gap

**References and paths**
- [ ] `.env.example` exists at repo root with placeholder values only (no real secrets)
- [ ] `.gitignore` covers: `.env*`, `*.local.*`, `data/`, `__pycache__/`, `*.pyc`, `.DS_Store`, `workspace/scratch/`
- [ ] No stale references to `brain/` (should be `wiki/` per 2026-04-05 migration) in any .claude/ files
- [ ] No stale references to `agents/` root-level directory (legacy — should be `.claude/agents/` now)
- [ ] No stale references to `workflows/` directory in scripts or configs (moved to `scripts/`)

**Branch cleanliness**
- [ ] `git status` is clean (no uncommitted changes)
- [ ] `git log --oneline -5` shows meaningful commit messages, not leftover WIP commits

### Pass Criteria

Phase A passes when all checklist items are either confirmed or documented as known gaps with an issue note. Do NOT fix gaps during Phase A — document them. Write findings to `workspace/results/2026-04-14-structural-audit.md` before moving to Phase B.

---

## Phase B: Agent/Skill Quality Audit + Gap Analysis

Before auditing, run these two skills to load the evaluation framework:
- `/n-agentic-harnesses` — understand harness design patterns and quality criteria
- `/code-best-practices` — understand Claude Code configuration best practices

Then read `workspace/plans/DEV-PLAN.md` sections: "Workflow Patterns", "Three-Tier Skill Loading", "Extended SKILL.md Frontmatter", and the full Sprint 1-4 structure.

### Existing Assets to Evaluate

For each asset, assess: (1) quality vs. n-agentic-harnesses standards, (2) completeness of frontmatter/config, (3) consistency with CLAUDE.md rules, (4) whether it needs full rewrite, minor updates, or is already solid.

**Agent definitions** (`.claude/agents/`)

| File | What to look for |
|------|-----------------|
| `cs-drafter.md` | HITL compliance (NEVER auto-sends), triage→enrich→draft pipeline structure, escalation paths to spiritual-director, brand-voice integration, CCPA disclosure |
| `finance-analyst.md` | Read-only posture enforced, COGS confidence labeling, no financial decisions, Dharma Giving as accounting line |
| `fulfillment-manager.md` | Multilingual comms (Jothi=Bahasa Indonesia, Fiona=Mandarin, Omar=Spanish), supplier relationship tone, conservative routing default |
| `inventory-analyst.md` | Proactive alerting logic, Shopify inventory API awareness, PO draft workflow |
| `marketing-strategist.md` | Hard caps enforced (2 emails/month, no FOMO/scarcity tactics), Tier 1-4 content framework, seasonal sensitivity |
| `catalog-curator.md` | Evaluator-optimizer loop structure, practice-first framing gate, cultural review before publish, cross-channel consistency |

**Skills** (`.claude/skills/`)

| File | What to look for |
|------|-----------------|
| `cs-triage/SKILL.md` | Frontmatter complete (name, description, version, category, tags, model, estimated_tokens, depends_on), triage logic covers escalation to spiritual-director, does NOT auto-draft |
| `shopify-query/SKILL.md` | Read-only enforcement, rate limit awareness, correct API version (2026-01), GraphQL patterns |
| `act-on-approved/SKILL.md` | If missing: document as critical gap. If present: verify it only executes post-human-approval, checks task_inbox status before acting |

**Rules files** (`.claude/rules/`)

Verify each file is self-contained, cites the correct role IDs (not person names), and doesn't contradict CLAUDE.md. Flag any file that still contains hardcoded person names ("Jothi", "Chris", "Fiona", "Dr. Hun Lye") instead of role IDs.

**Python scripts** (`scripts/`)

| File | What to look for |
|------|-----------------|
| `scripts/daily_summary.py` | Uses `lib/ts_shared/` imports (not legacy path), writes to Supabase `task_inbox`, sends Slack alert, logs cost, no hardcoded secrets |
| `scripts/weekly_pnl.py` | Prompt chain pattern (pull → aggregate → format), uses COGS data, approval_tier=2 (CEO review), cost logging |

### Known Gaps (from DEV-PLAN.md)

These are called for in the plan but do not currently exist:

**Missing shared library modules** (`lib/ts_shared/`)
- `claude_client.py` — SkillMetadata Pydantic model, three-tier skill loader, prompt caching, cost calculator (Prompt 1A)
- `org.py` — ORG.md parser, role resolver (Prompt 1C)
- `notifications.py` — Slack Web API wrapper with role-based routing (Prompt 1C)
- `cost_tracker.py` — Supabase + Notion cost logging (Prompt 1C)
- `views.py` — Materialized view refresher (Prompt 1C)
- `notion_ops.py` — Academy writes and cost log archive (Prompt 1B)

**Missing skills** (DEV-PLAN calls for 56 total; only 2 exist in `.claude/skills/`)
- `act-on-approved` — Execute downstream actions post-approval (check if missing)
- All shared skills referenced in ARCHITECTURE.md: `brand-guidelines`, `product-knowledge`, `escalation-matrix`, `channel-config`, `supabase-ops-db`, `tibetan-calendar`
- Domain skills for each workflow: `cs-triage` (exists), `cogs-tracking`, `margin-reporting`, `inventory-management`, `ticket-triage`, campaign/marketing skills

**Missing scripts**
- `scripts/cs_email_drafts.py` — CS triage → enrich → draft workflow (Sprint 2)
- `scripts/inventory_alerts.py` — Stock monitoring with PO draft (Sprint 2)
- `scripts/campaign_brief.py` — Campaign brief generation (Sprint 3)
- `scripts/product_descriptions.py` — Evaluator-optimizer loop (Sprint 3)
- `scripts/validate_skill.py` — Skill frontmatter validator (referenced in DEV-PLAN Prompt 0A verify step — check if exists)

**Missing infrastructure**
- `.claude/hooks/` — `budget-check.sh` and `log-activity.sh` referenced in ARCHITECTURE.md
- `lib/ts_shared/supabase_client.py` — confirm it exists and uses flattened path
- Supabase three-layer schema migration (Registry + Runtime + Eval layers, Prompt 1D)
- `config.yaml` files for each workflow script

**Missing tests**
- `tests/` directory — confirm it exists and has any tests at all
- `tests/test_claude_client.py`, `tests/test_org.py`, `tests/test_notifications.py` (Prompts 1A-1C)

### Output: Produce `workspace/results/2026-04-14-skills-gap-analysis.md`

Write this file at the end of Phase B. Use this structure:

```markdown
# Skills + Workflows Gap Analysis
**Date:** 2026-04-14
**Branch:** [current branch]

## Structural Audit Summary
[1-paragraph summary from Phase A — what passed, what gaps were found]

## Asset Quality Ratings

### Agents
| Agent | Rating | Issues Found | Action |
|-------|--------|--------------|--------|
| cs-drafter | [solid/minor/rewrite] | [brief notes] | [keep/update/rewrite] |
...

### Skills
| Skill | Rating | Issues Found | Action |
|-------|--------|--------------|--------|
...

### Rules
| Rule | Rating | Issues Found | Action |
...

### Scripts
| Script | Rating | Issues Found | Action |
...

## Gap Analysis: Missing Assets

### Priority 1 — Blocking (needed before any workflow runs end-to-end)
[List with justification]

### Priority 2 — Sprint 2 (needed for CS and inventory workflows)
[List]

### Priority 3 — Sprint 3+ (campaign, product descriptions, eval)
[List]

## Recommended Build Order
[Numbered sequence — what to build first and why]

## Do NOT Build Yet
[Things DEV-PLAN mentions that should stay deferred: Dashboard, Railway deployment, full eval layer, etc.]
```

---

## Constraints

- Do NOT modify any code files during this audit — read-only until gap analysis is written
- Do NOT start building missing assets during this session — audit first, build list second
- Do NOT read `.env` or any file containing secrets
- Do NOT run scripts against production Supabase without confirming with Chris first
- Do NOT merge to main until Phase A structural audit passes cleanly
- If you find a critical blocker (broken import, missing required file, settings.json invalid), stop and report before continuing

---

## Success Criteria

**Phase A done when:**
- All 15 checklist items confirmed or documented
- `workspace/results/2026-04-14-structural-audit.md` written to disk
- No merge to main with known structural errors

**Phase B done when:**
- All 6 agents, 3 skills, 10 rules, and 2 scripts rated
- All gaps from DEV-PLAN.md catalogued and prioritized
- `workspace/results/2026-04-14-skills-gap-analysis.md` written to disk with prioritized build list
- Chris has reviewed and approved the build list before any implementation begins

---

## Update: Skills/Workflows Structure Added (2026-04-14)

After the original handoff was written, the following structural change was made:

- Root `skills/` directory added (canonical), with `.claude/skills/` as symlinks
- Root `workflows/` directory scaffolded (empty, for future Claude workflows)
- CLAUDE.md updated with full asset structure table

**Phase A audit checklist additions:**
- [ ] `ls skills/` shows `cs-triage/` and `shopify-query/` with SKILL.md in each
- [ ] `.claude/skills/cs-triage` and `.claude/skills/shopify-query` are symlinks (not directories)
- [ ] `workflows/` directory exists at root
- [ ] CLAUDE.md Asset Structure table present with 5-row table
