# Agent & Skill Rewrite Sprint — Best Practices Alignment
**Date:** 2026-04-14
**Branch:** feat/agent-skill-rewrite (create fresh from main)
**For:** Fresh Claude Code session
**Repo:** ~/code/active/tibetan-spirit-ops/
**Depends on:** Phase 4 audit must be complete (workspace/results/ should have gap analysis)

---

## Context

All 6 agents and 2 skills in this repo were migrated from a legacy architecture during the April 2026 restructure. They are functional but were carried over from pre-best-practices designs — they were not written to OB2 standards. Chris's decision: every agent and skill must be rewritten from scratch using the n-agentic-harnesses and code-best-practices frameworks as the evaluation lens. Legacy content in `_archive/agents-legacy/` (54 skills across 6 departments) is reference material only — never copy verbatim.

The goal of this sprint is a fully standards-compliant agent + skill layer: precise system prompts, properly scoped tools, progressive disclosure format (SKILL.md + references/), metadata.json on every component, and at least the Priority 1 skills from the gap analysis built as proper Claude skills.

---

## Step 0: Load Best Practices Framework

Before writing a single line, invoke both skills:
- `/n-agentic-harnesses` — understand optimal agent architecture patterns
- `/code-best-practices` — understand code quality standards

Use the output of these two skills as your evaluation and rewrite framework. Everything you write must pass these frameworks.

---

## Step 1: Audit Existing Assets

Read every existing `.claude/agents/` and `skills/` file. For each, answer:
- Does it follow n-agentic-harnesses patterns?
- Is the system prompt specific enough for reliable execution?
- Are tools properly scoped?
- Is the progressive disclosure pattern used (SKILL.md + references/)?
- Does it have metadata.json?

Produce a brief assessment table before writing any rewrites.

---

## Step 2: Agent Rewrite Priority Order

Rewrite agents in this order (highest operational value first):
1. CS Drafter — already working, needs quality verification
2. Finance Analyst — already working, needs quality verification
3. Fulfillment Manager — migrated from legacy, likely needs rewrite
4. Inventory Analyst — migrated from legacy, likely needs rewrite
5. Marketing Strategist — migrated from legacy, likely needs rewrite
6. Catalog Curator — migrated from legacy, evaluator-optimizer loop is complex

For EACH agent rewrite:
- Read the current `.claude/agents/{name}.md`
- Read the corresponding legacy `soul.md` from `_archive/agents-legacy/` for operational context
- Read all relevant `.claude/rules/` files the agent references
- Write the rewritten agent definition
- Have spec reviewer + code quality reviewer subagents review it
- Commit: `refactor(agents): rewrite {name} to n-agentic-harnesses standards`

---

## Step 3: Skill Rewrite

For each skill in `skills/`:
- `cs-triage/` — assess and rewrite if needed
- `shopify-query/` — assess and rewrite if needed

Skill format requirements:
- `SKILL.md` — concise, actionable (progressive disclosure)
- `references/` — detailed methodology, examples (loaded on-demand)
- `metadata.json` — name, description, triggers, domain

---

## Step 4: New Skills to Build (from Gap Analysis)

Read `workspace/results/` for the gap analysis from Phase 4 audit. Build Priority 1 skills first. Expected gaps based on `workspace/plans/DEV-PLAN.md`:
- Each agent needs 5–9 operational skills (currently 0 exist as proper Claude skills)
- Skills go in `skills/{name}/` canonical, symlinked to `.claude/skills/{name}/`

For each new skill:
1. Write test/eval criteria first
2. Write `SKILL.md`
3. Write `metadata.json`
4. Write `references/` if methodology is complex
5. Symlink: `ln -s ../../skills/{name} .claude/skills/{name}`

---

## Step 5: Workflows

After skills are built, identify which multi-skill compositions need a workflow:
- CS pipeline (triage → enrichment → draft → approval)
- Daily ops summary
- Weekly P&L

Workflow format (in `workflows/{name}/`):
- `SKILL.md` — coordinator prompt
- `metadata.json`
- `README.md` — chains and purpose

Python scripts in `scripts/` are NOT Claude workflows — they remain as-is.

---

## Commit Strategy

Branch: `feat/agent-skill-rewrite`
One commit per agent or logical group of skills.

---

## Constraints

- Run `/n-agentic-harnesses` and `/code-best-practices` BEFORE writing anything
- Read legacy `soul.md` and skills from `_archive/` for context — never copy verbatim
- Use `superpowers:subagent-driven-development` — one subagent per agent/skill rewrite
- Two-stage review after each: spec compliance then code quality
- NEVER modify `.claude/hooks/` or `.claude/settings.json`
- NEVER read `.env`
- Run full audit of each file before claiming it's rewritten

---

## Success Criteria

- Every agent passes n-agentic-harnesses framework check
- Every skill has `SKILL.md` + `metadata.json` + `references/` (if complex)
- All symlinks in `.claude/skills/` resolve correctly
- At least Priority 1 skills from gap analysis are built
- CS pipeline workflow definition exists in `workflows/`
