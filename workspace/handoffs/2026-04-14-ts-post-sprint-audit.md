# Post-Sprint Audit — Sessions B + C Verification
**Date:** 2026-04-14
**Branch:** main (read both feature branches before merging)
**For:** Fresh Claude Code session (supervisor mode, subagents for each check)
**Repo:** ~/code/active/tibetan-spirit-ops/

---

## Context

Two parallel sessions ran against this repo:

| Session | Branch | Scope |
|---------|--------|-------|
| **B** (financial-model) | `feat/financial-scenario-model` | Python financial scenario engine at `scripts/financial_model/`, Supabase baseline, 5 seed scenarios, sensitivity analysis, markdown output |
| **C** (agent-skill-rewrite) | `feat/agent-skill-rewrite` | Rewrote all 6 agents + 2 skills to n-agentic-harnesses standards, built new skills (at minimum act-on-approved), defined CS pipeline workflow |

A prior Phase 4 audit session produced two result files:
- `workspace/results/2026-04-14-structural-audit.md` — structural pass (28/30)
- `workspace/results/2026-04-14-skills-gap-analysis.md` — quality ratings + prioritized build list

This session's job: verify both branches' work, fix uncovered gaps, then produce a merge-readiness verdict.

---

## Step 0: Load Frameworks

Before any evaluation:
- `/n-agentic-harnesses` — agent/skill quality criteria
- `/code-best-practices` — Claude Code configuration standards

---

## Phase 1: Session C Verification (agent-skill-rewrite)

**Switch to branch:** `git checkout feat/agent-skill-rewrite`

### 1A. Agent Rewrites — Quality Gate

For each of the 6 agents in `.claude/agents/`, verify ALL of:

**Structural checks (code-best-practices):**
- [ ] Frontmatter includes: `effort`, `memory`, `model: claude-opus-4-6` (per TS agent frontmatter standards)
- [ ] cs-drafter has `criticalSystemReminder_EXPERIMENTAL` field for CCPA/HITL compliance
- [ ] fulfillment-manager has `max-turns: 15`
- [ ] Tool scoping in frontmatter (`tools:` list) — appropriate for role
- [ ] "What You Don't Do" / prohibitions section exists
- [ ] Escalation criteria are specific (role ID, not person name, with channel)
- [ ] Word count in specialist range (500–700 words)

**Content checks (from gap analysis — these were the specific issues):**

| Agent | Must Fix (from audit) | Verify |
|-------|----------------------|--------|
| cs-drafter | CCPA protocol in agent body (was only in skill); budget field | HITL compliance, triage→enrich→draft pipeline, spiritual-director escalation |
| finance-analyst | **Was rated REWRITE**: COGS confidence labeling, escalation criteria, Dharma Giving as accounting, word count | All four deficits resolved |
| fulfillment-manager | Omar/Mexico fulfillment gap | Multilingual comms (Jothi=Bahasa, Fiona=Mandarin), conservative routing |
| inventory-analyst | Rule citations, Shopify API in data sources, PO draft schema | Proactive alerting logic, 14-day threshold |
| marketing-strategist | marketing-discipline.md citation | Hard caps (2 emails/month), Tier 1-4 framework, seasonal |
| catalog-curator | ecommerce-judgment.md citation | Evaluator-optimizer loop, practice-first gate, cultural review |

**Role ID compliance (all agents):**
- [ ] No hardcoded person names ("Chris", "Jothi", "Fiona", "Dr. Hun Lye") — use `ceo`, `operations-manager`, `warehouse-manager`, `spiritual-director`
- [ ] Exception: `org-roles.md` may use person names (it's the canonical mapping)

### 1B. Skill Rewrites — Quality Gate

For each skill in `skills/`:

**Frontmatter checks:**
- [ ] `description` field starts with "Use when..." followed by triggering conditions ONLY (CSO rule — do NOT summarize the workflow)
- [ ] Required fields present: name, description, version, category, tags, model, estimated_tokens, depends_on
- [ ] `metadata.json` exists alongside SKILL.md
- [ ] `references/` directory exists if methodology is complex

**Specific skill checks:**

| Skill | Verify |
|-------|--------|
| cs-triage | Spiritual-director escalation; does NOT auto-draft; has example input/output |
| shopify-query | Read-only enforcement; rate limit awareness; REST vs GraphQL clarified |
| act-on-approved | **Was MISSING — must now exist.** Only executes on status=approved; checks task_inbox; maps task_type to tool |

**Any new skills built (from Priority 1 gap list):** Verify they follow the same frontmatter + progressive disclosure pattern.

### 1C. Workflow Definitions

- [ ] `workflows/` contains at least CS pipeline workflow definition
- [ ] Workflow has SKILL.md + metadata.json + README.md (per workflow README convention)
- [ ] Workflow chains reference correct skill names

### 1D. Symlinks

- [ ] Every `skills/{name}/` has a corresponding symlink at `.claude/skills/{name}`
- [ ] `ls -la .claude/skills/` — all entries are symlinks, not directories

### 1E. CLAUDE.md Consistency

- [ ] Agent roster in CLAUDE.md matches files in `.claude/agents/` (count and names)
- [ ] Skills count in CLAUDE.md matches actual `skills/` directories
- [ ] Workflows count updated if any were added
- [ ] Hooks count still accurate

### 1F. Tests

- [ ] Run `python -m pytest tests/ -v` — all existing tests still pass
- [ ] If Session C added new skills with eval criteria, check that evals exist in `tests/evals/`

---

## Phase 2: Session B Verification (financial-model)

**Switch to branch:** `git checkout feat/financial-scenario-model`

### 2A. Structure

- [ ] `scripts/financial_model/` exists with: `__init__.py`, `baseline.py`, `scenarios.py`, `analysis.py`, `output.py`, `config/scenarios.yaml`
- [ ] No hardcoded financial numbers in Python files (all pulled from Supabase or config)
- [ ] No secrets, API keys, or connection strings in any file
- [ ] `.gitignore` covers `data/financial-model/` (raw scenario JSON)

### 2B. Code Quality

- [ ] `baseline.py` uses Supabase MCP or `lib/ts_shared/supabase_client.py` for data access
- [ ] `scenarios.yaml` has 3-5 seed scenarios with realistic parameters
- [ ] Sensitivity analysis produces 5 rows (50%-150% volume) per scenario
- [ ] Output includes breakeven timeline calculation
- [ ] Tests exist in `tests/` for projection math (breakeven, margin blending, sensitivity)

### 2C. Test Run

- [ ] `python -m pytest tests/ -v` passes (including any new financial model tests)
- [ ] `python scripts/financial_model/baseline.py --help` or equivalent runs without import errors (do NOT run against production Supabase without Chris's approval)

### 2D. Output

- [ ] `deliverables/docs/` directory exists or is defined in output config
- [ ] Markdown output template is scannable by a non-accountant

---

## Phase 3: Uncovered Gap Cleanup

These items were identified in the Phase 4 audit but NOT assigned to either parallel session. Fix them on main (or on a small `fix/audit-cleanup` branch) before merging feature branches.

### 3A. Rules — Person Names → Role IDs

Three files need edits:

**`.claude/rules/cultural-sensitivity.md`** — replace:
- "Chris" → `ceo`
- "Jothi" → `operations-manager`
- "Dr. Hun Lye" → `spiritual-director`

**`.claude/rules/cs-judgment.md`** — replace:
- "Chris" → `ceo`
- "Jothi" → `operations-manager`
- "Fiona" → `warehouse-manager`
- "Dr. Hun Lye" → `spiritual-director`
- Remove or replace the "Team Communication" section (lines ~32-40) with a one-line reference: `Reference: .claude/rules/org-roles.md`

**`.claude/rules/operations-protocols.md`** — replace:
- "Chris" → `ceo`
- "Jothi" → `operations-manager`
- "Fiona" → `warehouse-manager`
- "Omar" → `mexico-fulfillment`
- Remove the ~28 lines of duplicated org-roles content (Multilingual Team Communication table + protocols). Replace with: `For team communication protocols, see .claude/rules/org-roles.md.`

Commit: `fix(rules): replace person names with role IDs in 3 rules files`

### 3B. Docs — Structure Diagram Fix

Two files need the same edit:

**`docs/ARCHITECTURE.md`** (~line 113) and **`docs/OPERATIONS-REFERENCE.md`** (~line 186):
- Update structure tree to show `scripts/` contains operational Python scripts
- Update `workflows/` description to "Claude workflow definitions (empty — future)" or similar

Commit: `fix(docs): correct structure diagram (scripts/ not workflows/ for operational scripts)`

---

## Phase 4: Merge Readiness

After all checks pass:

### Merge Order

1. **main ← fix/audit-cleanup** (if Phase 3 created a branch) — rules + docs only, no conflicts expected
2. **main ← feat/financial-scenario-model** — Session B; touches only `scripts/financial_model/`, `deliverables/`, `tests/`, `config/` — no overlap with Session C
3. **main ← feat/agent-skill-rewrite** — Session C; touches `.claude/agents/`, `skills/`, `workflows/`, `.claude/skills/` — merge last since it's the largest changeset

### Post-Merge Checks

- [ ] `git status` clean on main after all merges
- [ ] `python -m pytest tests/ -v` passes on main
- [ ] `.claude/settings.json` is valid JSON
- [ ] All `.claude/skills/` symlinks resolve correctly
- [ ] `scripts/validate_skill.py` passes on all skills (run: `python scripts/validate_skill.py skills/`)
- [ ] CLAUDE.md counts still match disk (agents, skills, workflows, rules, hooks)

### Output

Write `workspace/results/2026-04-14-post-sprint-audit.md` with:
- Per-phase pass/fail summary
- Any issues found and how they were resolved
- Final merge status
- Remaining gaps deferred to next sprint

---

## Constraints

- Do NOT merge branches without all Phase 1-3 checks passing
- Do NOT run scripts against production Supabase without Chris approval
- Do NOT modify `.claude/hooks/` or `.claude/settings.json`
- Do NOT read `.env`
- Rules edits in Phase 3 are small and safe — proceed without approval gate
- Docs edits in Phase 3 are informational — proceed without approval gate
- If a Phase 1 or Phase 2 check reveals a critical defect (broken import, missing required file, test failure), STOP and report to Chris before attempting to fix — the defect belongs to the session that produced it

---

## Success Criteria

- All Phase 1 checks pass (or defects documented and assigned back to Session C)
- All Phase 2 checks pass (or defects documented and assigned back to Session B)
- Phase 3 cleanup committed
- All three branches merged to main in order
- Post-merge test suite passes
- `workspace/results/2026-04-14-post-sprint-audit.md` written
