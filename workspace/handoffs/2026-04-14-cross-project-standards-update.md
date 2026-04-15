# Cross-Project Standards Update — cpg-agents-2.0, dharma-writer, laurina-partners
**Date:** 2026-04-14
**For:** Fresh Claude Code session (run from any project, or ~/code/active/)
**Prerequisite:** Standards already applied to chris-os and tibetan-spirit-ops

---

## Context

chris-os and tibetan-spirit-ops were updated to OB2+superpowers standards (best-practices-v2 plan). Three other active projects need the same treatment. This prompt defines the evaluation and update for each.

### The Standards (Reference)

These standards are documented in:
- `/Users/chrismauze/code/chris-os/workspace/research/claude-code-best-practices.md`
- `/Users/chrismauze/code/active/tibetan-spirit-ops/workspace/handoffs/2026-04-14-ts-post-merge-audit.md` (example of applied standards)

**Summary of what "compliant" means:**

| Component | Standard |
|-----------|----------|
| **CLAUDE.md** | At root level (not .claude/). <=300 lines project, <=60 lines global. Every line earns its tokens. |
| **Skill SKILL.md** | YAML frontmatter with `name`, `description` (CSO: starts "Use when..."). Body <500 words. Heavy content in `references/`. |
| **Skill metadata.json** | Exists alongside every SKILL.md. Fields: name, description, domain, triggers, model, category, approval_tier, cost_budget_usd, version. |
| **Agent .md** | YAML frontmatter: name, model, description (CSO), effort, memory. Tool scoping via `tools:` list. Word count 300-700 (role-dependent). Prohibitions section. Escalation criteria with role IDs. |
| **Rules** | <=200 lines each. Use role IDs, not person names. No duplication of content across rules files. |
| **Settings.json** | Deny list comprehensive. No blanket Bash allow without deny filter. Valid JSON. |
| **Hooks** | set -euo pipefail. JSON protocol on stdout. Explicit timeout. Exit 2 for blocks, not exit 1. |
| **Symlinks** | Skills at root `skills/` or `workflows/`, symlinked to `.claude/skills/` for runtime. Exception: small projects with <=4 skills can keep them directly in `.claude/skills/`. |
| **Progressive disclosure** | SKILL.md is the concise entry point. references/ holds rubrics, templates, SQL, examples. |
| **CSO rule** | `description` = triggering conditions ONLY. Starts with "Use when...". Never summarizes the workflow. This is the single biggest quality lever. |

---

## Project 1: cpg-agents-2.0

**Path:** `/Users/chrismauze/code/active/cpg-agents-2.0`
**Current state:** Design approved, scaffold built. 9 skills, 3 workflows, 0 agents, 3 rules. CLAUDE.md at `.claude/CLAUDE.md` (wrong — should be root). Skills already have `references/` dirs. No metadata.json files. Inconsistent frontmatter across skills (some use `skill:` key, some use `name:`, one has no frontmatter at all).

### Tasks

#### 1A. Move CLAUDE.md to root
```
mv .claude/CLAUDE.md ./CLAUDE.md
```
Verify `.claude/` still has settings.json, rules/, skills/ README.

#### 1B. Standardize all 9 skill SKILL.md frontmatter

Current state by skill:

| Skill | Has frontmatter? | Uses `name:`? | CSO description? | metadata.json? |
|-------|-----------------|---------------|------------------|----------------|
| connectors/syndicated | NO | — | — | No |
| foundation/data-qa | Yes (`skill:`) | No | No | No |
| foundation/metrics-engine | Yes (`skill:`) | No | No | No |
| foundation/data-catalog | Yes (`skill:`) | No | No | No |
| foundation/segment-builder | Yes (`skill:`) | No | No | No |
| analysis/competitive-grid | Yes (`skill:`) | No | No | No |
| analysis/story-miner | Yes (`skill:`) | No | No | No |
| output/chart-gen | Yes (`name:`) | Yes | No (verb phrase) | No |
| output/deck-builder | Yes (`skill:`) | No | No | No |

**For each skill:**
1. Add/fix YAML frontmatter: `name` (kebab-case), `description` (CSO — "Use when..."), `version: 1.0.0`
2. Remove non-standard keys (`skill:`, `produces:`, `consumes:`, `invoked_by:`, `reads:`) — these belong in metadata.json
3. Create `metadata.json` alongside each SKILL.md with: name, description, domain, triggers, model, category, approval_tier, cost_budget_usd, version
4. Verify body is <500 words (move excess to references/ if needed — most already have references/)

**CSO descriptions to write:**

| Skill | CSO Description |
|-------|----------------|
| connectors/syndicated | Use when a raw CSV export from Nielsen, SPINS, or Circana needs to be detected, column-mapped to the standard schema, and loaded into DuckDB. |
| foundation/data-qa | Use when a newly loaded dataset needs validation — checking for missing time periods, null values, column type mismatches, or data anomalies before analysis. |
| foundation/metrics-engine | Use when the DuckDB fact table is loaded and the 12 metric views (velocity, distribution, share, pricing, promotion, growth, fair share, summary) need to be built or rebuilt. |
| foundation/data-catalog | Use when a human-readable data dictionary needs generating from the current DuckDB schema — after metrics-engine runs, or on-demand for a new dataset. |
| foundation/segment-builder | Use when defining the focus brand, competitor set, market scope, and time periods for a competitive analysis or sales story run. |
| analysis/competitive-grid | Use when a 7-dimension competitive analysis is needed — comparing a focus brand against competitors on share, velocity, distribution, pricing, promotion, and growth. |
| analysis/story-miner | Use when data-driven talking points are needed for a sales meeting — ranking insights across three scenarios (category growth, competitive threat, distribution opportunity). |
| output/chart-gen | Use when analysis JSON needs to become matplotlib/seaborn charts — share trends, velocity bars, distribution maps, growth matrices, price ladders, or waterfalls. |
| output/deck-builder | Use when analysis and charts need to be assembled into a branded MARP slide deck with executive summary, source citations, and metric definitions. |

#### 1C. Standardize 3 workflow SKILL.md files

Same pattern: add CSO frontmatter + metadata.json to each workflow in `workflows/`.

| Workflow | CSO Description |
|----------|----------------|
| data-foundation | Use when raw data needs end-to-end preparation — connector, QA validation, metrics engine, and data catalog in sequence with a human gate after QA. |
| category-review | Use when a full competitive analysis deck is needed — segment definition through 12-slide branded deck with charts and commentary. |
| sales-stories | Use when a sales-focused story deck is needed — segment definition through 6-8 slide deck with ranked talking points and supporting charts. |

#### 1D. Update settings.json deny list

Current deny list is empty (`"deny": []`). Add:
```json
"deny": [
  "Bash(rm -rf *)",
  "Bash(* --force*)",
  "Bash(git push*)",
  "Edit(.env*)",
  "Write(.env*)",
  "Edit(data/raw/**)",
  "Write(data/raw/**)"
]
```

#### 1E. Verify CLAUDE.md counts match disk

After all changes, verify the skill/workflow/rule counts in CLAUDE.md match actual directories.

**Commit plan:** One commit per logical change (1A, 1B, 1C, 1D, 1E). Feature branch `feat/standards-update`.

---

## Project 2: dharma-writer

**Path:** `/Users/chrismauze/code/active/dharma-writer`
**Current state:** 4 skills (in .claude/skills/, not root), 1 agent, 2 rules, 0 hooks, 0 workflows. CLAUDE.md at `.claude/CLAUDE.md` (wrong — should be root). Skills have metadata.json. Agent has basic frontmatter. Skills have partial CSO compliance (some start with "Use when", some don't).

### Tasks

#### 2A. Move CLAUDE.md to root
```
mv .claude/CLAUDE.md ./CLAUDE.md
```

#### 2B. Fix skill CSO descriptions

| Skill | Current Description | CSO Compliant? | Fix |
|-------|-------------------|----------------|-----|
| keyword-index | "Build or update the Buddhist terminology index..." | Partial — has "Use when" in second sentence | Rewrite: "Use when onboarding new transcripts, expanding the glossary, or preparing for transcript improvement — builds the Buddhist terminology index from raw corpus and existing glossaries." |
| hun-lye-writing | "Unified writing skill that produces dharma articles..." | No — verb phrase | Rewrite: "Use when an article, book outline, or book chapter needs to be written in Dr. Hun Lye's voice — two-phase workflow requiring human approval between research/plan and write phases." |
| transcript-improve | "Improve raw ASR transcripts..." | Partial — has "Use after" clause | Rewrite: "Use when raw ASR transcripts need terminology correction, proper name fixes, and structural cleanup — requires keyword-index to have been run on the corpus first." |
| youtube-extract | "Extract YouTube transcripts..." | No — verb phrase | Rewrite: "Use when YouTube transcripts need extraction from individual videos, playlists, or entire channels for ingestion into the raw transcript corpus." |

#### 2C. Update agent frontmatter

`research-writing.md` has basic frontmatter (name, description, model) but is missing:
- `effort: high`
- `memory: session`
- CSO description (currently verb phrase — rewrite to "Use when...")
- Prohibitions/"What You Don't Do" section
- Word count check (target 300-500 for a focused research agent)

Rewrite description: "Use when the hun-lye-writing skill's research phase needs a structured brief — searches source transcripts, loads voice profile and reference works, and produces a writing plan for human approval."

#### 2D. Add metadata.json to any skills missing it

Check existing metadata.json files for completeness — add missing fields (domain, triggers, category, approval_tier, cost_budget_usd).

#### 2E. Consider HARD-GATE on hun-lye-writing

This skill has a mandatory human approval gate between Phase 1 (research/plan) and Phase 2 (write). Add:

```markdown
<HARD-GATE>
Do NOT proceed to Phase 2 (writing) without explicit human approval of the Phase 1 research brief and writing plan. Skipping this gate produces content that hasn't been validated against source material and voice profile.
</HARD-GATE>
```

#### 2F. Update settings.json deny list

Current deny list only covers raw data and voice profiles. Add:
```json
"deny": [
  "Edit(data/01_raw/**)",
  "Write(data/01_raw/**)",
  "Edit(config/voice-profiles/**)",
  "Bash(rm -rf*)",
  "Bash(* --force*)",
  "Bash(git push*)",
  "Edit(.env*)",
  "Write(.env*)"
]
```

#### 2G. Verify CLAUDE.md accuracy

After all changes, verify skill count, agent count, and rule count match disk.

**Commit plan:** Feature branch `feat/standards-update`. One commit per logical change.

---

## Project 3: laurina-partners

**Path:** `/Users/chrismauze/code/active/laurina-partners`
**Current state:** 8 skills (in .claude/skills/), 1 agent, 2 rules, 1 hook, 1 workflow (lp-diligence). CLAUDE.md at root (correct). Agent has good frontmatter (model, skills list, memory, isolation, maxTurns). Skills have `description:` fields but none follow CSO rule — they all use verb phrases or summaries.

### Tasks

#### 3A. Fix ALL 8 skill CSO descriptions

Every LP skill description currently starts with a summary ("Laurina Partners competitive analysis..."). Rewrite each to start with "Use when...":

| Skill | CSO Description |
|-------|----------------|
| lp-comp-analysis | Use when a deal needs competitive landscape mapping — market sizing, moat assessment, and pricing power validation from an investor perspective. |
| lp-research | Use when deal research sources need synthesis into an investment-grade brief with LP evidence standards and brand voice. |
| lp-brand-review | Use when a Laurina Partners deliverable needs brand compliance checking — visual identity, voice, typography, source citation, and document structure. |
| lp-deal-qa | Use when investment analysis needs a skeptical second opinion — fact-checking numbers, stress-testing assumptions, challenging the thesis, and verifying brand compliance. |
| lp-meeting-notes | Use when an investment call needs synthesis — extracting deal risks, management credibility signals, and diligence gaps from meeting transcripts. |
| lp-docx | Use when a Laurina Partners Word document needs generating — LOIs, investor memos, diligence request lists with the Quiet Authority brand system applied. |
| lp-model-review | Use when a financial model needs investor-grade review — COGS decomposition, growth stacking, labor cost treatment, and revenue timing skepticism. |
| lp-deal-memo | Use when a deal memo or IC memo needs drafting with LP brand voice, source citation requirements, and financial skepticism defaults. |

#### 3B. Add metadata.json to all skills

Only lp-diligence workflow has metadata.json. Add to all 8 skills.

#### 3C. Update agent frontmatter

`lp-analyst.md` has good structure but is missing:
- `effort: high`
- CSO description (currently verb phrase)
- Prohibitions section (NEVER auto-execute trades, NEVER commit financial data, etc. — pull from rules)

Rewrite description: "Use when investment work is needed — deal sourcing, screening, research, diligence, financial modeling, IC prep, QA, document generation, or portfolio monitoring."

#### 3D. Verify workflow has SKILL.md + metadata.json

Check `workflows/lp-diligence/` — does it have SKILL.md? metadata.json already exists. Add README.md if missing.

#### 3E. Update settings.json deny list

Current deny list is basic. Add financial safety patterns:
```json
"deny": [
  "Bash(rm -rf *)",
  "Bash(sudo *)",
  "Bash(chmod 777 *)",
  "Bash(ssh *)",
  "Bash(* > /dev/*)",
  "Bash(* --force*)",
  "Bash(git push*)",
  "Edit(.env*)",
  "Write(.env*)",
  "Write(data/**/*.csv)",
  "Edit(data/**/*.csv)"
]
```

#### 3F. Verify CLAUDE.md accuracy

After all changes, verify counts match disk. CLAUDE.md is already at root and well-structured.

**Commit plan:** Feature branch `feat/standards-update`. One commit per logical change.

---

## Execution Approach

### Option A: Sequential (one project per session)
Three sessions, one project each. Cleanest context. Recommended for cpg-agents-2.0 (most work) and dharma-writer (cultural sensitivity). Laurina-partners is the lightest.

### Option B: Parallel (subagent per project)
Use `superpowers:subagent-driven-development` with three worktree-isolated subagents. Faster but harder to review. Only use if time-constrained.

### Recommended order
1. **laurina-partners** (lightest — 8 CSO fixes, metadata.json, minor agent update)
2. **dharma-writer** (medium — 4 CSO fixes, HARD-GATE, CLAUDE.md move, agent update)
3. **cpg-agents-2.0** (heaviest — 9 skills + 3 workflows need full frontmatter rewrite, metadata.json, CLAUDE.md move)

### Per-project checklist (run after each)
- [ ] All SKILL.md descriptions start with "Use when..."
- [ ] metadata.json exists alongside every SKILL.md
- [ ] Agent frontmatter has: name, model, description (CSO), effort, memory
- [ ] Agent has prohibitions section
- [ ] settings.json deny list is comprehensive
- [ ] CLAUDE.md is at project root
- [ ] CLAUDE.md counts match disk
- [ ] `python3 -c "import json; json.load(open('.claude/settings.json'))"` passes
- [ ] All tests pass (if tests exist)
- [ ] Changes committed on feature branch, not main

---

## Constraints

- Do NOT modify chris-os or tibetan-spirit-ops (already done)
- Do NOT modify `~/.claude/` global config (user-level hooks are managed separately)
- Do NOT merge feature branches — leave for Chris's review
- Do NOT read .env files
- Do NOT install dependencies
- Do NOT restructure project directories beyond what's specified (e.g., don't move LP skills from .claude/skills/ to root skills/ — that's a larger decision)
- When writing CSO descriptions, preserve the domain-specific trigger phrases already in the description fields — just restructure to lead with "Use when..."
