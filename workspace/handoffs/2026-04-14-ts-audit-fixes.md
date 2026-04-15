# Audit Fix Sprint — tibetan-spirit-ops
**Date:** 2026-04-14
**Branch:** Create `fix/post-merge-audit-fixes` from main
**For:** Fresh Claude Code session
**Repo:** ~/code/active/tibetan-spirit-ops/
**Prerequisite:** Read `workspace/results/2026-04-14-post-merge-audit.md` for full audit context

---

## Context

The post-merge audit (`ddc3b86`) found systemic issues beyond what the audit session could fix in-scope. The audit session fixed:
- 3 rules files (person names -> role IDs) — committed `87a44e4`
- org.py DEFAULT_ORG_PATH, evals conftest, test_ticket_triage paths, cs-pipeline symlink — committed `1040f2a`
- test_ticket_triage.py structural tests updated for progressive disclosure (linter-amended after commit)

**Current test state:** 135 pass, 11 fail, 2 collection errors. This sprint targets 0 failures.

---

## Fix 1: Agent Person Names → Role IDs (all 6 agents)

**Priority: HIGH.** Every agent in `.claude/agents/` uses person names instead of role IDs. The role ID convention is defined in `.claude/rules/org-roles.md`.

**Replacements (apply across all 6 agents):**

| Find | Replace With |
|------|-------------|
| Chris | `ceo` |
| Jothi | `operations-manager` |
| Fiona | `warehouse-manager` |
| Dr. Hun Lye | `spiritual-director` |
| Omar | `mexico-fulfillment` |

**Context-sensitive replacements** — don't blindly find/replace. Examples:
- "escalate to Chris" → "escalate to `ceo`"
- "Chris's review" → "`ceo` review"
- "Jothi (Operations Manager)" → "`operations-manager`"
- "route to Dr. Hun Lye before invoking" → "route to `spiritual-director` before invoking"
- In possessive forms: "Chris's approval" → "`ceo` approval"

**Per-agent occurrence counts (from audit):**
- `cs-drafter.md`: ~4 occurrences (Chris, Dr. Hun Lye)
- `finance-analyst.md`: ~2 occurrences (CEO reference — check if already compliant)
- `fulfillment-manager.md`: ~12 occurrences (Chris, Jothi, Fiona) — heaviest
- `inventory-analyst.md`: ~4 occurrences (Chris, Jothi, Fiona)
- `marketing-strategist.md`: ~2 occurrences (Chris)
- `catalog-curator.md`: ~1 occurrence (Dr. Hun Lye)

**Verification:** After all edits, grep all agent files:
```bash
grep -rn '\b\(Chris\|Jothi\|Fiona\|Omar\|Dr\. Hun Lye\)\b' .claude/agents/
```
Expected: zero results.

**Commit:** `fix(agents): replace person names with role IDs in all 6 agents`

---

## Fix 2: Add Mexico Fulfillment to fulfillment-manager

**Priority: HIGH.** The fulfillment-manager agent has zero coverage for Omar / Mexico fulfillment / Espíritu Tibetano / Latin American orders. Per `.claude/rules/org-roles.md`:

- Role ID: `mexico-fulfillment`
- Language: Spanish
- Channel: Email only
- Scope: Latin American order fulfillment exclusively

**Changes needed in `fulfillment-manager.md`:**

1. **Decision table** (the section that routes exceptions): Add a row for Latin American / Mexico fulfillment routing to `mexico-fulfillment` via email in Spanish.

2. **Communication protocols**: Add a `mexico-fulfillment` entry with language (Spanish), channel (email only), and register (formal).

3. **Verification checklist**: Add a check for Mexico/LatAm routing when applicable.

Read `.claude/rules/org-roles.md` and `.claude/rules/operations-protocols.md` for the authoritative communication protocols before writing. Match the style and structure of the existing Jothi/Fiona entries.

**Keep word count within 500-700.** Current is 554 — budget for ~100 words of additions, trim elsewhere if needed.

**Commit:** `feat(agents): add mexico-fulfillment coverage to fulfillment-manager`

---

## Fix 3: Add Rule File Citations to 2 Agents

**Priority: MEDIUM.**

- **`marketing-strategist.md`**: Add a line citing `.claude/rules/marketing-discipline.md` as the authoritative source for frequency caps and tier framework. The agent duplicates this content inline without attribution.

- **`catalog-curator.md`**: Add a line citing `.claude/rules/ecommerce-judgment.md` as the authoritative source for ecommerce content judgment. The agent embeds these principles without attribution.

Add citations near the relevant content sections — don't restructure. One line each, e.g.:
```
Source: `.claude/rules/marketing-discipline.md`
```

**Commit:** `fix(agents): add rule file citations to marketing-strategist and catalog-curator`

---

## Fix 4: Remaining Person Names in 2 Rules Files

**Priority: MEDIUM.** The audit session fixed 3 rules files. Two more have "Chris":

- **`.claude/rules/shopify-api.md`**: ~2 occurrences ("Chris runs manually", "executed by Chris after review") → replace with `ceo`
- **`.claude/rules/category-judgment.md`**: 1 occurrence ("belongs to Chris, not to an optimization model") → replace with `ceo`

**Commit:** `fix(rules): replace remaining person names in shopify-api and category-judgment`

---

## Fix 5: Refactor Skill Loading in Production Code

**Priority: HIGH (blocks 7 test failures).** Two modules still reference the old `agents/` directory structure:

### 5A. `server/server.py`

Current state:
- Line 35: `AGENTS_DIR = os.path.join(os.path.dirname(__file__), "..", "agents")`
- Line 46-56: `load_skill()` constructs paths like `agents/{domain}/skills/{name}/SKILL.md`
- Lines 59-114: `AGENT_CONFIGS` dict maps agent domains to old skill paths

**Required changes:**

1. Rename `AGENTS_DIR` → `SKILLS_DIR`, point to `../skills`:
   ```python
   SKILLS_DIR = os.path.join(os.path.dirname(__file__), "..", "skills")
   ```

2. Simplify `load_skill()` — flat structure, no domain nesting:
   ```python
   def load_skill(skill_name: str) -> str:
       """Load a SKILL.md file from the skills directory."""
       full_path = os.path.join(SKILLS_DIR, skill_name, "SKILL.md")
       if not os.path.exists(full_path):
           raise FileNotFoundError(f"Skill not found: {full_path}")
       with open(full_path, "r") as f:
           return f.read()
   ```

3. Update `AGENT_CONFIGS` skill references to new names:
   ```
   "customer-service/ticket-triage" → "cs-triage"
   "shared/brand-guidelines" → removed or mapped to a rule
   "shared/product-knowledge" → removed or mapped to a rule
   "shared/escalation-matrix" → removed or mapped to a rule
   "shared/channel-config" → removed or mapped to a rule
   "shared/supabase-ops-db" → removed or mapped to a rule
   "operations/fulfillment-domestic" → "fulfillment-flag"
   "operations/inventory-management" → "restock-calc"
   "ecommerce/etsy-content-optimization" → "description-optimizer"
   "ecommerce/cross-channel-parity" → (check if skill exists or remove)
   "category-management/pricing-strategy" → "margin-reporting"
   "category-management/competitive-research" → (check if skill exists or remove)
   "marketing/meta-ads" → "campaign-brief" or remove
   "marketing/google-ads" → remove if no skill exists
   "marketing/performance-reporting" → remove if no skill exists
   ```
   
   **IMPORTANT:** Some old skills don't have direct equivalents. For those, either:
   - Remove from AGENT_CONFIGS (if the server doesn't actively call them)
   - Or leave as TODO comments for the next sprint

4. Read the full server.py to understand what `AGENT_CONFIGS` is used for before changing — it may affect webhook routing logic.

### 5B. `lib/ts_shared/claude_client.py`

This module exports `AGENTS_DIR`, `load_skill()`, `load_skills()`, `_resolve_skill_path()`, and `get_skill_index()`. All use the old path structure.

**Required changes:**

1. Rename `AGENTS_DIR` → `SKILLS_DIR`, point to `skills/`:
   ```python
   SKILLS_DIR = REPO_ROOT / "skills"
   ```

2. Simplify `_resolve_skill_path()` — flat lookup:
   ```python
   def _resolve_skill_path(skill_name: str) -> Path:
       return SKILLS_DIR / skill_name / "SKILL.md"
   ```

3. Update `get_skill_index()` to walk `skills/` directory instead of `agents/`

4. Update `load_skills()` dependency resolution if it relies on old paths

5. **Export name change:** `AGENTS_DIR` → `SKILLS_DIR`. Update all imports in test files.

### 5C. Update `tests/test_claude_client.py`

After fixing claude_client.py:
- Update import: `AGENTS_DIR` → `SKILLS_DIR`
- Update path assertions in `test_resolve_shared_skill_path` and `test_resolve_agent_skill_path`
- Update `test_load_skill_brand_guidelines` — this skill may not exist in the new structure. Map to an actual skill.
- Update `test_load_skill_ticket_triage` → use `cs-triage`
- Update `test_load_skills_brand_guidelines_always_first` — dependency resolution may have changed
- Update `test_get_skill_index_returns_all` — adjust expected count and names

### 5D. Update `tests/test_server.py`

Fix skill path references in test expectations to match the refactored server.py.

**Commit:** `refactor(server): update skill loading for flat skills/ directory structure`

---

## Fix 6: Clean Up Stale Test Files

**Priority: LOW.**

- `tests/evals/test_daily_summary.py` — imports `workflows.daily_summary.run` which doesn't exist
- `tests/evals/test_pnl_accuracy.py` — imports `workflows.weekly_pnl.run` which doesn't exist

These reference old Python-based workflows that were never migrated. Options:
1. **Delete** both files (simplest — the workflows they test don't exist)
2. **Skip** with `pytest.mark.skip(reason="workflow not yet migrated")` at module level

Recommend option 1 — delete. They produce import errors and test nothing.

**Commit:** `chore(tests): remove stale eval tests for non-existent workflows`

---

## Fix 7: Skill Word Count Trimming (4 skills)

**Priority: LOW.** Four skills exceed the 500-word SKILL.md budget:

| Skill | Words | Over | Fix |
|-------|-------|------|-----|
| fulfillment-flag | 579 | 79 | Extract decision table + carrier rules to `references/decision-table.md` |
| description-optimizer | 542 | 42 | Tighten inline workflow prose |
| campaign-brief | 522 | 22 | Extract brief template to `references/brief-template.md` |
| restock-calc | 517 | 17 | Extract lead-time tiers to `references/formulas.md` |

For each:
1. Create `references/` dir if missing
2. Move the heaviest content block to a reference file
3. Add a one-line pointer in SKILL.md: `See references/{file}.md for {what}.`
4. Verify body is now <500 words

**Commit:** `refactor(skills): extract heavy content to references/, bring 4 skills under 500-word budget`

---

## Fix 8: Branch Cleanup

After all fixes are committed and merged:

```bash
git branch -d feat/agent-skill-rewrite
git branch -d refactor/align-repo-conventions
```

For `chore/skill-metadata-standardization` (unmerged, 5 commits):
- It contains an `act-on-approved` skill. Before deleting, check if this skill should be cherry-picked to main.
- The metadata.json standardization work in that branch is superseded by this sprint.
- **Do not delete without Chris's explicit approval.**

---

## Execution Order

1. Fix 1 (agent person names) — highest impact, self-contained
2. Fix 2 (Mexico fulfillment) — builds on Fix 1
3. Fix 3 (rule citations) — quick, self-contained
4. Fix 4 (remaining rules person names) — quick, self-contained
5. Fix 5 (skill loading refactor) — most complex, blocks test fixes
6. Fix 6 (stale tests) — quick cleanup
7. Fix 7 (word count) — editorial, lowest priority
8. Fix 8 (branches) — after everything else is merged

Fixes 1-4 can be parallelized (no file overlaps). Fix 5 is sequential (server.py → claude_client.py → test updates). Fixes 6-7 are independent.

---

## Verification

After all fixes, run:
```bash
python3 -m pytest tests/ -v           # Target: 0 failures, 0 errors
python3 -c "import json; json.load(open('.claude/settings.json'))"  # Valid JSON
ls -la .claude/skills/                 # 9 symlinks (8 skills + 1 workflow)
grep -rn '\b\(Chris\|Jothi\|Fiona\|Omar\|Dr\. Hun Lye\)\b' .claude/agents/ .claude/rules/  # Only in org-roles.md
wc -w skills/*/SKILL.md workflows/*/SKILL.md  # All <500 words
```

---

## Do NOT

- Modify `.env` or read secrets
- Run scripts against production Supabase
- Change the skill directory structure (skills stay at root `skills/`, symlinked to `.claude/skills/`)
- Delete the `chore/skill-metadata-standardization` branch without Chris's approval
- Add new skills or agents beyond what's specified
- Restructure AGENT_CONFIGS routing logic — just update paths. If an old skill has no equivalent, leave a TODO comment.
- Push to remote without Chris's approval
