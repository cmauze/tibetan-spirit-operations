# Post-Merge Audit & Next Steps — tibetan-spirit-ops
**Date:** 2026-04-14
**Branch:** main (all work on main — feature branch merged)
**For:** Fresh Claude Code session
**Repo:** ~/code/active/tibetan-spirit-ops/

---

## Context

The `feat/agent-skill-rewrite` branch was merged to main (`ddc3b86`). This sprint delivered:

- 6 agents rewritten to OB2+superpowers standards (CSO descriptions, effort/memory/model frontmatter, scoped tools, Common Rationalizations + Red Flags + Verification sections)
- 2 existing skills rewritten with references/ extraction (cs-triage, shopify-query)
- 6 new Priority 1 skills (order-inquiry, margin-reporting, fulfillment-flag, restock-calc, campaign-brief, description-optimizer)
- 1 workflow defined (cs-pipeline: triage -> enrichment -> draft -> approval)
- CCPA enforcement hook (ccpa-gate.sh) blocking direct email sending
- HARD-GATE on cs-triage for spiritual guidance escalation
- Agent metadata consolidated from .metadata.json into frontmatter comments

**Standards applied** (from `~/code/chris-os/workspace/plans/2026-04-14-best-practices-v2.md`):
- CSO rule: `description` field = triggering conditions only, starts with "Use when..."
- Frontmatter: effort, memory, model (claude-opus-4-6), tools (scoped)
- Progressive disclosure: SKILL.md body <500 words, heavy content in references/
- HARD-GATE XML tags for discipline-enforcing skills
- Metadata consolidation: custom fields as comment lines (budget, approval, domain)

---

## Audit Required

This session needs to verify the merged work against audit standards. Load `/n-agentic-harnesses` and `/code-best-practices` before starting.

### 1. Agent Quality Gate (6 agents in `.claude/agents/`)

For each agent, verify:

| Check | Standard | How to verify |
|-------|----------|---------------|
| Frontmatter fields | effort, memory, model: claude-opus-4-6 | Read each agent file |
| CSO description | Starts with "Use when..." + triggering conditions only | Read description field |
| Tool scoping | tools: list present, no Bash unless justified | Check frontmatter |
| Word count | 500-700 words (specialist range) | wc -w |
| Prohibitions section | "What You Don't Do" or equivalent exists | Search for section |
| Escalation criteria | Uses role IDs (ceo, operations-manager), not person names | Grep for person names |
| Common Rationalizations | Section exists with 3+ entries | Read each file |
| Red Flags | Section exists | Read each file |
| Verification section | Section exists | Read each file |

**Agent-specific checks from gap analysis:**

| Agent | Must verify |
|-------|------------|
| cs-drafter | CCPA protocol in body (not just skill); criticalSystemReminder_EXPERIMENTAL field; triage->enrich->draft pipeline |
| finance-analyst | Was rated REWRITE — verify all deficits resolved: COGS confidence labeling, escalation criteria, Dharma Giving as accounting |
| fulfillment-manager | Omar/Mexico fulfillment coverage; max-turns: 15; multilingual comms |
| inventory-analyst | Shopify API in data sources; PO draft schema; 14-day threshold |
| marketing-strategist | marketing-discipline.md citation; hard caps (2 emails/month); Tier 1-4 framework |
| catalog-curator | ecommerce-judgment.md citation; evaluator-optimizer loop; practice-first gate |

### 2. Skill Quality Gate (8 skills in `skills/`)

For each skill, verify:

| Check | Standard |
|-------|----------|
| CSO description | Starts with "Use when..." |
| metadata.json exists | Alongside SKILL.md |
| references/ | Exists if methodology is complex (>100 lines extracted) |
| Body length | <500 words in SKILL.md |
| Symlink | `.claude/skills/{name}` -> `../../skills/{name}` |

### 3. Workflow Quality Gate (1 workflow in `workflows/`)

- [ ] cs-pipeline has SKILL.md + metadata.json + README.md
- [ ] HARD-GATE present for spiritual guidance escalation
- [ ] Stage gates table defines pass/fail criteria per step

### 4. Rules Cleanup (NOT YET DONE)

Three rules files still have person names instead of role IDs. Fix these:

**`.claude/rules/cultural-sensitivity.md`:**
- "Chris" -> `ceo`, "Jothi" -> `operations-manager`, "Dr. Hun Lye" -> `spiritual-director`

**`.claude/rules/cs-judgment.md`:**
- "Chris" -> `ceo`, "Jothi" -> `operations-manager`, "Fiona" -> `warehouse-manager`, "Dr. Hun Lye" -> `spiritual-director`
- Replace Team Communication section (~lines 32-40) with: `Reference: .claude/rules/org-roles.md`

**`.claude/rules/operations-protocols.md`:**
- "Chris" -> `ceo`, "Jothi" -> `operations-manager`, "Fiona" -> `warehouse-manager`, "Omar" -> `mexico-fulfillment`
- Remove ~28 lines of duplicated org-roles content; replace with: `For team communication protocols, see .claude/rules/org-roles.md.`

Commit: `fix(rules): replace person names with role IDs in 3 rules files`

### 5. Missing Skill: act-on-approved

The gap analysis flagged `act-on-approved` as a critical missing skill. It was NOT built in this sprint (Priority 1 list focused on CS/ops skills). Scope:
- Executes only on task_inbox items with status=approved
- Checks task_inbox via Supabase MCP
- Maps task_type to the appropriate tool/action
- Logs execution result back to task_inbox

**Decision needed from Chris:** Build now or defer to next sprint?

### 6. Stale Branch Cleanup

These branches are fully merged to main and can be deleted:
- `feat/agent-skill-rewrite`
- `refactor/align-repo-conventions`

One unmerged branch exists:
- `chore/skill-metadata-standardization` (4 commits) — check if superseded by this sprint's work before deleting

### 7. CLAUDE.md Consistency Check

After all fixes:
- [ ] Agent count in CLAUDE.md matches `.claude/agents/` (expect 6)
- [ ] Skills count matches `skills/` directories (expect 8)
- [ ] Workflows count matches `workflows/` directories (expect 1)
- [ ] Hooks count matches `.claude/hooks/` (expect 4)
- [ ] Rules count matches `.claude/rules/` (expect 10)

### 8. Test Suite

- [ ] `python -m pytest tests/ -v` — all tests pass on main
- [ ] `.claude/settings.json` is valid JSON
- [ ] All `.claude/skills/` symlinks resolve correctly

---

## Do NOT

- Modify `.env` or read secrets
- Run scripts against production Supabase without Chris's approval
- Merge the `chore/skill-metadata-standardization` branch without checking for conflicts/supersession
- Skip the rules cleanup — role ID compliance is a standards requirement
- Create new skills beyond act-on-approved without Chris's approval

---

## Output

Write `workspace/results/2026-04-14-post-merge-audit.md` with:
- Per-section pass/fail
- Issues found and resolutions
- Remaining gaps deferred
- Final state summary
