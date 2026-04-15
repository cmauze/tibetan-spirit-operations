# ACT NOW — tibetan-spirit-ops Restructure Complete

**Date:** 2026-04-14
**Source:** tibetan-spirit-ops restructure session (refactor/align-repo-conventions branch)
**Context:** `/Users/chrismauze/code/active/tibetan-spirit-ops/`

---

## ACT NOW 1: Merge refactor/align-repo-conventions to main

**Why it matters:** 11 commits ready on a clean branch — structural alignment, workspace scaffold, 4 new agent definitions, 6 rules files, legacy agents archived, CLAUDE.md refreshed. Waiting to merge blocks all downstream work.

**Next actions:**
1. `cd ~/code/active/tibetan-spirit-ops && git checkout main && git merge refactor/align-repo-conventions`
2. Verify `ls` at root looks clean (no legacy files, workspace/ has all subdirs)
3. Push to origin if remote exists

---

## ACT NOW 2: Run post-restructure audit

**Why it matters:** 15-item structural checklist + skills gap analysis. Will produce a prioritized build list for Phase 5.

**Next actions:**
1. Open fresh session: `cd ~/code/active/tibetan-spirit-ops && claude`
2. Read and execute handoff: `/Users/chrismauze/code/active/tibetan-spirit-ops/workspace/handoffs/2026-04-14-ts-post-restructure-audit.md`
3. Output goes to `workspace/results/YYYY-MM-DD-skills-gap-analysis.md`

---

## ACT NOW 3: Phase 5 — Rewrite all agents/skills/workflows

**Why it matters:** All 6 agents, 3 skills, 2 Python scripts are currently migrated from legacy architecture. Chris explicitly decided they should be rewritten to n-agentic-harnesses + code-best-practices standards. Nothing legacy retained unless it helps reach the optimized version.

**Next actions:**
1. Complete audit (ACT NOW 2) first — gap analysis will drive the priority order
2. Invoke `/n-agentic-harnesses` and `/code-best-practices` skills at start of sprint
3. Rewrite in order: highest-use agents first (CS Drafter, Finance Analyst, then the 4 new ones)

---

## ACT NOW 4: Phase 3 — Financial scenario model

**Why it matters:** Separate sprint on `feat/financial-scenario-model`. Config-driven Python tool pulling from Supabase (ts_orders, ts_products, ts_cogs). Outputs markdown/charts/JSON for scenario analysis.

**Next actions:**
1. New session, new branch: `git checkout -b feat/financial-scenario-model`
2. Spec at: `/Users/chrismauze/code/chris-os/workspace/handoffs/2026-04-14-ts-repo-restructure.md` (Phase 3 section)
3. Start with baseline data pull from Supabase before building scenario engine

---

## Decisions Made (flag for ADR)

1. **All agents/skills/workflows → rewrite to best practices** — Nothing legacy retained for its own sake. Use n-agentic-harnesses + code-best-practices as evaluation framework.

2. **ORG.md → .claude/rules/org-roles.md** — Tibetan Spirit is a multi-person operation (Jothi/Fiona/Omar); role-based communication protocols are operationally necessary, not a Paperclip-era artifact.

3. **.claude/** auto-allowed in permissions** — Added `Read/Edit/Write(.claude/**)` to project settings.json; hooks still protected by deny rule.
