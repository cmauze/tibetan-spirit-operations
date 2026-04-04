# Phase 0B — Docs, Guides, and Legacy Consolidation

**Depends on:** Phase 0A complete
**Produces:** Foundational guides/specs + clean consolidated vault

---

## Context

Phase 0A created the empty container. Phase 0B fills it with two things: documentation that teaches how the system works (Track A), and consolidated knowledge from scattered legacy notes (Track B). Both tracks run in parallel and complete before Phase 1.

**Critical principle for Track A:** These guides are the medium through which Chris learns the system. Every guide follows: explain concept → concrete examples from Chris's projects → proposed convention → checkpoint → finalize. If Chris cannot explain it back, the guide is not done.

**Critical principle for Track B:** Discovery first, then classification with Chris's explicit approval, then migration. No files move without approval for that specific batch.

---

## Track A: Docs and Guides

### A1: Research Phase

Before writing guides, research current best practices across Claude Code, Paperclip, and the community. Produce structured reference notes in `code/docs/reference/`.

**Sources to research:**
1. Anthropic official docs — skills, hooks, subagents, agent teams, headless mode, sessions, settings cascade
2. Paperclip docs — heartbeat protocol, task workflow, writing a skill, handling approvals, cost reporting, companies-spec
3. Community repos — shanraisshan/claude-code-best-practice, ChrisWiles/claude-code-showcase, hesreallyhim/awesome-claude-code, Anthropic's plugin-dev hook-development SKILL.md
4. Skill ecosystem — SkillsMP, SkillHub, agentskills.io, Antigravity Awesome Skills

For each source, produce a reference note with: key takeaways for our system, patterns to adopt, patterns to avoid, notable examples worth adapting.

**Checkpoint:** Present top 5-7 patterns that should shape our guides. Identify community skills worth forking (infrastructure/utility only). Get alignment before writing guides.

### A2: Write Foundational Guides

Each guide follows this structure: What This Is → Why It Matters → How It Works → In Our System (concrete examples) → Convention → Common Mistakes → Related Guides.

Write in this order (each builds on previous):

1. **`guides/agent-developer/how-agents-work.md`** — Agent vs routine. Lifecycle (wake → context → assignments → execute → report → sleep). Heartbeat system. "Memento Man" metaphor. In our system: Daily Summary is a routine, Chief of Staff is an agent.

2. **`guides/skill-developer/writing-a-skill.md`** — SKILL.md anatomy. Frontmatter fields. Supporting files (examples/, references/, templates/, tests/). Semantic matching on description. Agent Skills open standard. Complete example: brand-guidelines skill with full directory.

3. **`guides/hook-developer/hook-fundamentals.md`** — What hooks are (event-driven, not instructions). Events, handler types, JSON stdin, exit codes. How hooks differ from skills (OS vs apps). The safety hook from Phase 0A as worked example.

4. **`guides/routine-developer/composable-patterns.md`** — Anthropic's six patterns (single call, prompt chain, routing, parallelization, orchestrator-workers, evaluator-optimizer). When to use each. How our routines map. March of Nines reliability math.

5. **`guides/agent-developer/writing-a-soul-file.md`** — Soul file purpose (character/judgment, NOT procedures). Paperclip's file system (AGENTS.md, SOUL.md, HEARTBEAT.md, TOOLS.md). Start with 20 lines, add rules only when agents misbehave.

6. **`guides/agent-developer/heartbeat-protocol.md`** — How heartbeats work. The checklist (confirm identity → wake context → plans → assignments → checkout → execute → extract facts → exit). Context compiled fresh each cycle. How PM2 cron maps to heartbeats.

7. **`guides/routine-developer/graduation-model.md`** — Standalone script → graduated agent. Graduation checklist. Override rate as master metric. Tier 3 → 2 → 1 progression.

**Checkpoint after each guide:** Chris explains the concept back. If gaps, revise. Only proceed when confirmed.

### A3: Write Foundational Specs

1. **`specs/skills-spec.md`** — Our SKILL.md standard extending agentskills.io. Frontmatter fields, supporting file convention, complete example directory.

2. **`specs/agents-spec.md`** — Agent definition standard. What goes in SOUL.md vs AGENTS.md vs .paperclip.yaml. Agent-centric directory layout.

3. **`specs/values-guardrails-spec.md`** — Values cascade (constitution → company → agent → skill). Frequency caps, content tiers, product framing. CEO decision support format.

4. **`specs/companies-spec.md`** — Vendor the Paperclip companies-spec into our docs.

**Checkpoint:** Present each spec. Confirm it accurately represents the conventions to enforce.

### A4: Repo Examples

Minimal but complete clonable archetypes in `docs/repo-examples/`:
- `python-routine-project/` — Routine-based project (TS-style)
- `agent-company/` — Paperclip company package
- `web-project/` — Web/portfolio project

**Checkpoint:** Walk through each. Every file explained.

---

## Track B: Legacy Consolidation

### B1: Classification

Present Phase 0A inventory to Chris in batches. For each source: what's in it, recommended classification, overlaps with new vault. One source at a time. Strong bias toward discarding outdated technical notes (LangGraph, pre-2026 AI architecture) and keeping decisions, principles, and unique insights.

### B2: Migration

Per approved batch: copy to destination, add consistent frontmatter, rename to convention, verify file counts, stage originals in `_migrated/`.

### B3: Clean Up

Move `_migrated/` to Google Drive archive. Delete empty directories. Uninstall Dropbox if approved. Update TABLE_OF_CONTENTS.md. Final scan for orphans. Commit to Git.

**Checkpoint:** Walk through final vault state. Confirm nothing important lost.

---

## Verification

**Track A:** Research notes complete. 7 guides written and reviewed. 4 specs written and reviewed. Repo examples created. TABLE_OF_CONTENTS updated.

**Track B:** All sources classified by Chris. Migrations executed. Old directories removed. Vault TOC reflects new content. All changes on GitHub.

**Integration:** Chris can explain how agents work, how to write a skill, how hooks enforce safety, what the composable patterns are, how graduation works. One vault, one docs system, no competing locations.
