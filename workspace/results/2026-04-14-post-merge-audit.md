# Post-Merge Audit Results — tibetan-spirit-ops
**Date:** 2026-04-14
**Commit:** `ddc3b86` (feat/agent-skill-rewrite merged to main)
**Auditor:** Claude Code (lead dev session)

---

## Section 1: Agent Quality Gate — 6 agents

### Universal Passes (all 6 agents)
- Frontmatter: effort, memory, model: claude-opus-4-6
- CSO description: starts with "Use when..."
- Tool scoping: appropriate tools, no Bash
- Word count: 543-663 (within 500-700 specialist range)
- Common Rationalizations: 3+ entries each
- Red Flags section: present
- Verification section: present

### Cross-Cutting Issue: Person Names (HIGH)
**All 6 agents use person names instead of role IDs.** 20+ occurrences total. "Chris" should be `ceo`, "Jothi" should be `operations-manager`, "Fiona" should be `warehouse-manager`, "Dr. Hun Lye" should be `spiritual-director`.

### Per-Agent Issues

| Agent | Status | Issues |
|-------|--------|--------|
| cs-drafter | PASS (with issues) | "Dr. Hun Lye" and "Chris" used instead of role IDs |
| finance-analyst | PASS (with issues) | Prohibitions section is informal (inline bullet, not structured block); no explicit escalation thresholds |
| fulfillment-manager | FAIL | Omar/Mexico fulfillment completely absent; person names throughout (12+ occurrences) |
| inventory-analyst | PASS (with issues) | No Shopify API as data source; no PO draft schema; person names |
| marketing-strategist | PASS (with issues) | No `.claude/rules/marketing-discipline.md` citation; person names |
| catalog-curator | PASS (with issues) | No `.claude/rules/ecommerce-judgment.md` citation; "Dr. Hun Lye" used |

### Deferred Fixes (need Chris's decision on scope)
1. Replace person names with role IDs across all 6 agents (~20+ edits)
2. Add Mexico fulfillment coverage to fulfillment-manager
3. Add rule file citations to marketing-strategist and catalog-curator
4. Add Shopify API to inventory-analyst data sources
5. Add PO draft schema to inventory-analyst
6. Restructure finance-analyst prohibitions into formal block

---

## Section 2: Skill Quality Gate — 8 skills

### Results

| Skill | CSO | metadata.json | references/ | Body (words) | Symlink |
|-------|-----|---------------|-------------|--------------|---------|
| cs-triage | PASS | PASS | PASS | PASS (389) | PASS |
| shopify-query | PASS | PASS | PASS | PASS (327) | PASS |
| order-inquiry | PASS | PASS | PASS | PASS (462) | PASS |
| fulfillment-flag | PASS | PASS | **FAIL** | **FAIL** (579) | PASS |
| margin-reporting | PASS | PASS | PASS | PASS (475) | PASS |
| campaign-brief | PASS | PASS | NOTE | **FAIL** (522) | PASS |
| restock-calc | PASS | PASS | NOTE | **FAIL** (517) | PASS |
| description-optimizer | PASS | PASS | PASS | **FAIL** (542) | PASS |

### Issues
- **fulfillment-flag**: 579 words + no references/ directory. Decision table and carrier rules should be extracted.
- **campaign-brief**: 522 words (22 over). Brief template could move to references/.
- **restock-calc**: 517 words (17 over). Formulas/tiers could move to references/.
- **description-optimizer**: 542 words (42 over). Workflow prose needs tightening.

---

## Section 3: Workflow Quality Gate — cs-pipeline

| Check | Result |
|-------|--------|
| SKILL.md exists | PASS |
| metadata.json exists | PASS |
| README.md exists | PASS |
| HARD-GATE for spiritual guidance | PASS |
| Stage gates table | PASS |
| Symlink .claude/skills/cs-pipeline | **FIXED** (was missing, created during audit) |

---

## Section 4: Rules Cleanup — DONE

**Committed fix:** Replaced person names with role IDs in 3 rules files.

| File | Changes |
|------|---------|
| cultural-sensitivity.md | "Chris" -> `ceo`, "Dr. Hun Lye" -> `spiritual-director`, "Jothi" -> `operations-manager` |
| cs-judgment.md | "Chris" -> `ceo`; Team Communication section collapsed to org-roles.md reference |
| operations-protocols.md | Multilingual Team Communication table + subsections collapsed to org-roles.md reference |

**Additional findings:** `shopify-api.md` and `category-judgment.md` also contain "Chris" — not in handoff scope but should be fixed in a follow-up.

---

## Section 5: Missing Skill — act-on-approved

**Decision needed from Chris.** Not built in this sprint. However, an `act-on-approved` skill exists on the `chore/skill-metadata-standardization` branch (unmerged). May be cherry-pickable.

---

## Section 6: Stale Branch Cleanup

| Branch | Status | Action |
|--------|--------|--------|
| feat/agent-skill-rewrite | Merged | Safe to delete |
| refactor/align-repo-conventions | Merged | Safe to delete |
| chore/skill-metadata-standardization | Unmerged (5 commits) | Contains act-on-approved skill + metadata.json standardization. Metadata work is superseded by this sprint. act-on-approved may be worth cherry-picking. **Do not delete until Chris reviews.** |

---

## Section 7: CLAUDE.md Consistency — PASS

| Asset | CLAUDE.md | Actual | Match |
|-------|-----------|--------|-------|
| Agents | 6 | 6 | PASS |
| Skills | 8 | 8 | PASS |
| Workflows | 1 | 1 | PASS |
| Hooks | 4 | 4 | PASS |
| Rules | 10 | 10 | PASS |

---

## Section 8: Test Suite

### Final State: 135 passed, 11 failed, 2 collection errors

### Fixed During Audit
1. **`lib/ts_shared/org.py`**: Updated `DEFAULT_ORG_PATH` from `ORG.md` to `.claude/rules/org-roles.md` (ORG.md was moved during earlier restructuring but path wasn't updated). Fixed 9 test_org.py failures.
2. **`tests/evals/conftest.py`**: Updated `SKILLS_DIR` from `agents/` to `skills/` and simplified path resolution for flat skill structure. Fixed 18 test_ticket_triage errors.
3. **`tests/evals/test_ticket_triage.py`**: Updated skill path from `customer-service/ticket-triage` to `cs-triage` and frontmatter name assertion.

### Remaining Failures (need refactoring — deferred)

**Production code with stale paths (7 failures):**
- `server/server.py`: `AGENTS_DIR`, `load_skill()`, and `AGENT_CONFIGS` all reference old `agents/` directory tree. Affects `test_server.py` (2 fails) and `test_claude_client.py` (5 fails).
- `lib/ts_shared/claude_client.py`: `AGENTS_DIR`, `_resolve_skill_path()`, `get_skill_index()` all use old path structure.

**Structural test expectations (4 failures):**
- `test_ticket_triage.py::TestSkillStructure`: Tests expect classification tiers, JSON format, and model routing in SKILL.md body. The rewritten cs-triage uses progressive disclosure — this content is in `references/classification-matrix.md`. Tests need rewriting.
- `test_no_cultural_anti_patterns`: False positive — the word "exotic" appears in the verification checklist as a banned term ("No banned terms: exotic, mystical..."). The substring check is too broad.

**Stale test files (2 collection errors):**
- `tests/evals/test_daily_summary.py`: Imports from `workflows.daily_summary.run` which doesn't exist
- `tests/evals/test_pnl_accuracy.py`: Imports from `workflows.weekly_pnl.run` which doesn't exist

---

## Summary

| Section | Status |
|---------|--------|
| 1. Agent Quality Gate | PASS with issues (person names, missing Mexico fulfillment) |
| 2. Skill Quality Gate | PASS with issues (4 skills over word budget) |
| 3. Workflow Quality Gate | PASS (symlink fixed during audit) |
| 4. Rules Cleanup | DONE |
| 5. act-on-approved | Deferred — decision needed |
| 6. Branch Cleanup | Assessed — 2 safe to delete, 1 needs review |
| 7. CLAUDE.md Consistency | PASS |
| 8. Test Suite | PARTIAL — 135/148 pass, 11 fail + 2 stale |

### Changes Made This Session
- Fixed 3 rules files (person names -> role IDs)
- Created cs-pipeline symlink
- Fixed org.py DEFAULT_ORG_PATH
- Fixed evals conftest.py skill path resolution
- Fixed test_ticket_triage.py path and name assertion

### Deferred Work (Next Sprint)
1. Replace person names with role IDs in all 6 agents
2. Add Mexico fulfillment to fulfillment-manager agent
3. Refactor `server/server.py` and `lib/ts_shared/claude_client.py` skill loading for new `skills/` directory structure
4. Rewrite structural tests for progressive disclosure
5. Remove or rewrite stale test files (daily_summary, pnl_accuracy)
6. Extract fulfillment-flag content to references/ (579 words -> <500)
7. Trim campaign-brief, restock-calc, description-optimizer to <500 words
8. Add rule file citations to marketing-strategist and catalog-curator agents
9. Fix "Chris" in shopify-api.md and category-judgment.md
