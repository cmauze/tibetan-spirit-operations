# Agent & Skill Rewrite Sprint — Part 2 (Standards Confirmation + Remaining Work)
**Date:** 2026-04-14
**Branch:** feat/agent-skill-rewrite (DO NOT create new branch — continue on this one)
**For:** Fresh Claude Code session
**Repo:** ~/code/active/tibetan-spirit-ops/
**Depends on:** Chris confirming the formatting standards below before any new work proceeds

---

## Context

Part 1 of the rewrite sprint (this session) rewrote all 6 agents and 2 existing skills to OB2 + superpowers/agent-skills standards. 12 commits on `feat/agent-skill-rewrite`. The branch has NOT been merged to main.

Three tasks remain: building Priority 1 new skills, defining the CS pipeline workflow, and updating all project documentation. But Chris wants to **confirm the final formatting standard** before proceeding — and any confirmed changes may require retroactive updates to the 6 agents and 2 skills already written.

---

## Step 0: WAIT FOR CHRIS — Standards Confirmation

**Do NOT proceed to Step 1 until Chris explicitly confirms the formatting standards.**

Present Chris with the current standards being used and ask if anything needs to change. The standards applied in Part 1 are:

### Agent Frontmatter (currently applied)
```yaml
---
name: agent-name
model: claude-opus-4-6
effort: high
memory: project
description: |
  Use when [triggering conditions only — never summarize workflow].
tools:
  - [scoped tool list — no Bash unless justified]
---
```
Additional fields used on specific agents:
- `max-turns: 15` on fulfillment-manager (bounded workflow)
- `criticalSystemReminder_EXPERIMENTAL: "..."` on cs-drafter (CCPA compliance gate)
- `schedule: "0 7 * * 1"` on finance-analyst (cron)

### Agent Body Structure (currently applied)
```markdown
# Agent Name

## Overview
1-2 sentences. Core purpose + key constraint.

## When to Use
**Invoke when:** [bullet list]
**Do NOT invoke when:** [bullet list with routing guidance]

## Workflow
Numbered steps with bold step names. Decision tables inline if <50 lines.

## Common Rationalizations
| Rationalization | Reality |
|---|---|
| ... | ... |

## Red Flags
- Bullet list of behavioral anti-patterns

## Verification
- [ ] Checkbox list run before final output
```

### Skill Frontmatter (currently applied)
```yaml
---
name: skill-name
description: Use when [triggering conditions only]
---
```

### Skill Body Structure (currently applied)
Same section order as agents: Overview → When to Use → Workflow → Common Rationalizations → Red Flags → Verification

### Skill File Layout (currently applied)
```
skills/{name}/
  SKILL.md            Main file, <500 words body
  metadata.json       Name, description, domain, triggers, model, category, version
  references/         Heavy content (>100 lines) extracted here
```

### CSO Rule (critical, applied everywhere)
`description` field = triggering conditions ONLY, starts with "Use when...". Never summarizes workflow. This is the single biggest quality lever — Claude follows the description shortcut instead of reading the full skill body when descriptions contain process detail.

### metadata.json Schema (currently applied)
```json
{
  "name": "component-name",
  "description": "Brief description.",
  "domain": "customer-service|finance|fulfillment|inventory|marketing|catalog|operations",
  "triggers": ["trigger phrase 1", "trigger phrase 2"],
  "model": "claude-opus-4-6|inherit",
  "category": "agent|skill|workflow",
  "approval_tier": "auto-logged|review-required|decision-needed",
  "cost_budget_usd": 2.00,
  "version": "2.0.0",
  "created": "2026-04-14",
  "updated": "2026-04-14"
}
```
Additional optional fields: `schedule` (cron), `max-turns` (integer).

---

## Step 1: Retroactive Updates (if standards change)

If Chris confirms changes to the standards above, apply them retroactively to ALL already-written files:
- 6 agents in `.claude/agents/`
- 6 agent metadata files in `.claude/agents/`
- 2 skills in `skills/`
- 2 skill metadata files in `skills/`
- 2 reference directories in `skills/`

Commit: `fix(agents,skills): retroactive standards alignment`

If Chris confirms no changes, skip this step.

---

## Step 2: Build Priority 1 New Skills

Reference: `workspace/plans/GROWTH-ROADMAP.md` for future roadmap. The current sprint builds operational skills, not growth skills.

Priority 1 skills per agent (highest operational value from legacy archive):

| Agent | Skill to Build | Why |
|-------|---------------|-----|
| CS | `order-inquiry` | ~40% of all tickets per legacy SKILL.md |
| Finance | `margin-reporting` | Core weekly P&L output — the agent's primary skill |
| Fulfillment | `fulfillment-flag` | Core flag/exception logic |
| Inventory | `restock-calc` | Threshold calculation + recommendation logic |
| Marketing | `campaign-brief` | Core brief generator output |
| Catalog | `description-optimizer` | The evaluator-optimizer loop is complex enough to warrant standalone |

For each new skill:
1. Create `skills/{name}/SKILL.md` using confirmed standards
2. Create `skills/{name}/metadata.json`
3. Create `skills/{name}/references/` if methodology >100 lines
4. Symlink: `ln -s ../../skills/{name} .claude/skills/{name}`
5. Commit: `feat(skills): add {name} skill`

Legacy reference material is in `_archive/agents-legacy/agents/{department}/skills/` — read for context, never copy verbatim.

---

## Step 3: Define CS Pipeline Workflow

Create `workflows/cs-pipeline/`:
- `SKILL.md` — coordinator prompt for: triage → enrichment → draft → approval
- `metadata.json`
- `README.md` — chains and purpose

This is a Claude workflow (SKILL.md), NOT a Python script. Python scripts stay in `scripts/`.

Commit: `feat(workflows): add cs-pipeline workflow definition`

---

## Step 4: Update All Documentation

After all new skills and workflows are built:

1. **CLAUDE.md** — Update the Skills section (currently shows 2 skills), Workflows section (currently 0), and any agent roster changes
2. **docs/ARCHITECTURE.md** — Update references to skills/workflows if they exist
3. **docs/CHANGELOG.md** — Add single `[Unreleased]` entry summarizing the entire sprint:
   - 6 agents rewritten to OB2+superpowers standards
   - 2 skills rewritten with references/ extraction
   - N new Priority 1 skills built
   - CS pipeline workflow defined
   - New frontmatter fields: effort, memory, max-turns, criticalSystemReminder_EXPERIMENTAL
4. **Stale workflow refs** — `docs/ARCHITECTURE.md:113` and `docs/OPERATIONS-REFERENCE.md:186` still show `workflows/` as containing cron scripts (they're actually in `scripts/`). Fix these.

Commit: `docs: update all documentation for agent/skill rewrite sprint`

---

## Constraints

- NEVER modify `.claude/hooks/` or `.claude/settings.json`
- NEVER read `.env`
- Git history is the changelog for `.claude` changes — no separate changelog needed
- Use `superpowers:subagent-driven-development` for the new skill builds (Step 2)
- Reference projects for pattern verification:
  - `/Users/chrismauze/code/reference/superpowers-main/skills/` — superpowers skill patterns
  - `/Users/chrismauze/code/reference/agent-skills-main/` — agent-skills patterns (agents/, skills/, references/)
  - `/Users/chrismauze/code/reference/natebjones-projects/OB1` — OB1 metadata.json schema

---

## Success Criteria

- Chris has confirmed the formatting standards
- Any retroactive changes applied if standards changed
- At least 6 Priority 1 skills built (one per agent)
- CS pipeline workflow definition exists in `workflows/`
- All symlinks in `.claude/skills/` resolve correctly
- CLAUDE.md, docs/ARCHITECTURE.md, docs/CHANGELOG.md all updated
- Branch ready for Chris review before merge to main

---

## What NOT to Do

- Do NOT merge to main — Chris reviews the full branch first
- Do NOT start building new skills before Chris confirms standards
- Do NOT copy legacy skills verbatim — read for context, write from scratch
- Do NOT build growth-phase skills (subscription-manager, etsy-sync) — those are next sprint per GROWTH-ROADMAP.md
- Do NOT modify hooks or settings.json
