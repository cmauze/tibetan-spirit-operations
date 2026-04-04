# Phase 0A — Core Structure

**Depends on:** Nothing (starting point)
**Produces:** Directories, Git repos, `.claude/` config, Paperclip shell, server baseline, legacy inventory, Google Drive consolidation plan, Notion workspace inventory

---

## Session Prompt

> Copy-paste this into a new Claude Code session to begin Phase 0A.

```
Read these two files carefully before doing anything:
1. workspace/plans/REQ-1b/02-phase-0a-core-structure.md (this file — step-by-step implementation plan)
2. workspace/plans/REQ-1b/01-master-spec.md (architecture spec — source of truth for all decisions)

You are helping me build the foundational structure for chris-os — my
personal and professional operating system. I'm Chris Mauzé, a
semi-technical entrepreneur who vibe-codes with AI tools.

CURRENT STATE (important — this is NOT a greenfield setup):
- I have an existing workspace at ~/cm/ with brain/ vault, .claude/
  config (CLAUDE.md, rules/, skills/, agents/), and project files.
- I have an existing repo at ~/code/active/tibetan-spirit-ops/ with
  agents/, scripts/, tests/, workspace/, etc.
- I have existing ~/.claude/CLAUDE.md and ~/.claude/rules/ with
  extensive content (anti-patterns, file-budget, parallelization,
  self-monitoring, etc.).
- I have Google Drive content across two accounts (chrismauze@gmail.com
  personal + TS shared drives: "Tibetan Spirit", "NORBU", "TS
  Management Team").
- I have iCloud Documents and Desktop with scattered files.
- I have a Notion workspace ("Chris's Brain" + TS operational pages).

The ~/brain/ vault will be REBUILT FROM SCRATCH with the new PARA
structure. Current brain/ content is treated as a legacy source to be
inventoried and selectively migrated in Phase 0B (with my approval per
batch). Same for ~/cm/ and other legacy locations.

Phase 0A creates the new container structure. Phase 0B fills it by
consolidating content from all legacy sources with interactive approval.

CRITICAL REQUIREMENTS:
- Execute steps in order. Do NOT skip ahead.
- At every "Checkpoint," STOP and present your work. Explain what you
  built and why. Ask me to confirm understanding before continuing.
- ~/.claude/CLAUDE.md must be UNDER 60 LINES. Claude Code loads this
  every session and ignores content it deems irrelevant. Every line
  must prevent a specific mistake.
- Project-level CLAUDE.md files: UNDER 150 LINES.
- ~/brain/CLAUDE.md: UNDER 30 LINES.
- Use Paperclip terminology: routines (recurring), tasks (one-off),
  agents (role definitions with soul files), heartbeats (scheduled
  wake cycles), skills (SKILL.md capability files).
- DO NOT MOVE any legacy files — Step 7 is inventory only. Phase 0B
  executes migrations after Chris classifies each source.
- DO NOT MOVE any Google Drive content — Step 7a produces a
  consolidation PLAN only.
- DO NOT MODIFY Notion content — Step 7b is inventory only.

After reading both files, start with Step 0. Explain what you're about
to do and why before making any filesystem changes.
```

**Watch for:** CLAUDE.md exceeding line limits. Agent skipping checkpoints. Agent moving legacy files before classification. Agent modifying Google Drive or Notion content instead of inventorying. Paperclip onboarding may require interactive decisions. Agent ignoring existing ~/.claude/rules/ content during Step 4 reconciliation.

---

## Context

You are setting up the foundational structure for chris-os — Chris Mauze's personal and professional operating system. Chris is a semi-technical entrepreneur (CPO-level systems thinking, vibe-codes with AI tools). He has a 2024 MacBook Pro (workbench), a 2021 Intel MacBook Pro (always-on server), and a ROK-BOX (GPU lab).

Read the master spec at `workspace/plans/REQ-1b/01-master-spec.md` for full context. This phase card is self-contained but the master spec wins any conflicts.

**Important — how Claude Code loads context natively:** Claude Code automatically reads `~/.claude/CLAUDE.md` and `./CLAUDE.md` at every session start. It wraps this content with a system note saying it may or may not be relevant, so Claude will ignore content it deems irrelevant to the current task. Keep these files lean. Skills in `.claude/skills/` load only when their description matches the task — this is the progressive disclosure mechanism. Hooks in `.claude/settings.json` fire with 100% determinism on every tool use, regardless of context.

**Additional native capabilities referenced in the master spec:**
- **Subagents** (`.claude/agents/`): Custom agent definitions with YAML frontmatter. Run in separate context windows, report back summaries.
- **Agent Teams**: Independent Claude Code sessions with 1M-token context each. File-based coordination.
- **/batch**: Codebase-wide transformations across worktree-isolated agents.
- **/compact** and **/clear**: Context management. Compact at ~50% usage. Clear between unrelated tasks.

---

## Step 0: Current State Reconciliation (NEW)

Before creating any new directories or files, audit what already exists. This prevents destructive overwrites and informs what needs migration vs. creation.

### 0a. Audit ~/cm/ (current workspace)

```bash
# Top-level structure
ls -la ~/cm/
ls -la ~/cm/brain/ 2>/dev/null
ls -la ~/cm/.claude/ 2>/dev/null

# What's in the brain vault?
find ~/cm/brain/ -maxdepth 2 -type d 2>/dev/null | head -50
find ~/cm/brain/ -name "*.md" | wc -l

# What's in .claude config?
ls -la ~/cm/.claude/ 2>/dev/null
cat ~/cm/.claude/CLAUDE.md 2>/dev/null
ls -la ~/cm/.claude/rules/ 2>/dev/null
ls -la ~/cm/.claude/skills/ 2>/dev/null
ls -la ~/cm/.claude/agents/ 2>/dev/null
```

### 0b. Audit ~/.claude/ (user-level config)

```bash
ls -la ~/.claude/
cat ~/.claude/CLAUDE.md 2>/dev/null
ls -la ~/.claude/rules/ 2>/dev/null
ls -la ~/.claude/skills/ 2>/dev/null
ls -la ~/.claude/agents/ 2>/dev/null
cat ~/.claude/settings.json 2>/dev/null
```

### 0c. Audit ~/code/active/tibetan-spirit-ops/ (existing TS repo)

```bash
ls -la ~/code/active/tibetan-spirit-ops/
find ~/code/active/tibetan-spirit-ops/ -maxdepth 2 -type d | head -50
cat ~/code/active/tibetan-spirit-ops/CLAUDE.md 2>/dev/null
cat ~/code/active/tibetan-spirit-ops/.claude/CLAUDE.md 2>/dev/null
```

### 0d. Audit other key locations

```bash
# iCloud Documents
ls ~/Documents/ 2>/dev/null | head -30

# Desktop
ls ~/Desktop/ 2>/dev/null | head -30

# Google Drive mount points
ls ~/Library/CloudStorage/ 2>/dev/null
ls ~/Library/CloudStorage/GoogleDrive-chrismauze@gmail.com/ 2>/dev/null | head -20
```

### 0e. Produce reconciliation document

Create `~/brain/_inbox/current-state-audit.md` (or equivalent location if brain/ doesn't exist yet — use a temp location and move later):

```markdown
# Current State Audit — Phase 0A Reconciliation
Date: [today]

## ~/cm/ Workspace
- [inventory summary]
- Brain vault: [file count, structure summary]
- .claude/ config: [what exists — CLAUDE.md, rules/, skills/, agents/]
- Projects: [what exists]

## ~/.claude/ (User-Level)
- CLAUDE.md: [line count, key content summary]
- rules/: [list of rule files]
- skills/: [list of skill directories]
- agents/: [list of agent files]
- settings.json: [hooks summary]

## ~/code/active/tibetan-spirit-ops/
- Structure: [directory summary]
- Key files: [CLAUDE.md, agents/, scripts/, etc.]
- Git status: [branch, last commit]

## iCloud Documents
- [summary]

## Desktop
- [summary]

## Google Drive
- [mount points found]

## Migration Plan
For each existing item, classify as:
- KEEP IN PLACE — already in correct location
- MIGRATE — needs to move to new structure (specify destination)
- RECONCILE — content overlaps with new structure (specify how to merge)
- ARCHIVE — move to archive location
- DEFER — handle in Phase 0B

| Source | Classification | Destination | Notes |
|--------|---------------|-------------|-------|
| ~/.claude/CLAUDE.md | RECONCILE | ~/.claude/CLAUDE.md (rewrite) | Merge useful content into new <60 line version |
| ~/.claude/rules/* | RECONCILE | ~/.claude/rules/ or skills/ | Evaluate which rules are still needed |
| ~/cm/brain/ | MIGRATE | ~/brain/ | Inventory content first |
| ~/code/active/tibetan-spirit-ops/ | RECONCILE | ~/code/active/tibetan-spirit/ | Map existing structure to new layout |
| ... | ... | ... | ... |
```

**Checkpoint:** STOP. Present the full audit results and migration plan. Walk Chris through every line of the migration table. This is the most important checkpoint in Phase 0A — every subsequent step depends on getting reconciliation right. Confirm each classification before proceeding. Ask: "Is there anything I missed? Any files or locations I didn't check?"

---

## Step 1: Finder Configuration

Make dotfiles visible so Chris can see `.claude/` directories:

```bash
defaults write com.apple.finder AppleShowAllFiles -bool true
killall Finder
```

**Checkpoint:** Confirm dotfiles visible. Show where `.claude/` directories will exist.

---

## Step 2: Brain Vault (Obsidian)

**IMPORTANT:** If `~/brain/` already exists with content, rename it to `~/brain-legacy/` first. The existing content is treated as a legacy source — it will be inventoried in Step 7 and selectively migrated during Phase 0B with Chris's interactive approval. We are building the new vault from scratch.

### If ~/brain/ does not exist (or is empty):

```bash
mkdir -p ~/brain/{1-Projects,2-Areas,3-Resources,4-Archive,_inbox}
mkdir -p ~/brain/2-Areas/{tibetan-buddhism,ai-engineering,fitness,finance,music-production,home-and-family}
mkdir -p ~/brain/3-Resources/{ai-engineering,cpg-analytics,dharma-teachings,productivity-systems}
mkdir -p ~/brain/.claude
cd ~/brain && git init
```

### If ~/cm/brain/ exists with content:

```bash
# DO NOT copy or move yet — just document what's there
echo "=== ~/cm/brain/ contents ==="
find ~/cm/brain/ -maxdepth 2 -type d
find ~/cm/brain/ -name "*.md" | wc -l
echo "=== Sample files ==="
find ~/cm/brain/ -name "*.md" -maxdepth 2 | head -20

# Create the new structure alongside (Phase 0B Track B will handle migration)
mkdir -p ~/brain/{1-Projects,2-Areas,3-Resources,4-Archive,_inbox}
mkdir -p ~/brain/2-Areas/{tibetan-buddhism,ai-engineering,fitness,finance,music-production,home-and-family}
mkdir -p ~/brain/3-Resources/{ai-engineering,cpg-analytics,dharma-teachings,productivity-systems}
mkdir -p ~/brain/.claude
cd ~/brain && git init
```

Create `~/brain/CLAUDE.md` (vault-level — loaded when Claude Code runs inside this directory). **Must be under 30 lines:**

```markdown
# Brain Vault

Obsidian vault, PARA methodology. Markdown files on disk.

## Structure
- `1-Projects/` — Active deliverables with deadlines
- `2-Areas/` — Ongoing responsibilities, no end date
- `3-Resources/` — Reference material by topic
- `4-Archive/` — Completed/inactive, searchable
- `_inbox/` — Unsorted captures, process during weekly review

## Frontmatter
Every note: `type`, `status`, `tags`, `created` in YAML frontmatter.

## Conventions
- One idea per note. Link with [[wikilinks]]. Lowercase-with-hyphens filenames.
- Under 500 lines per note. Date-prefix time-sensitive notes.
```

Create `~/brain/.gitignore`: exclude `.obsidian/workspace.json`, `.obsidian/workspace-mobile.json`, `.trash/`, `.DS_Store`.

**Checkpoint:** Walk through PARA structure. Ask Chris to explain the difference between Projects (has a deadline) and Areas (ongoing, no deadline). Confirm the 2-Areas categories cover his life. Ask if anything is missing. If ~/cm/brain/ existed with content, present the inventory and confirm that Phase 0B Track B will handle migration — nothing moves now. Verify CLAUDE.md is under 30 lines (count them).

---

## Step 3: Code Meta-Project

**IMPORTANT:** The existing repo at `~/code/active/tibetan-spirit-ops/` needs to map into the new structure. The master spec defines the target as `~/code/active/tibetan-spirit/`. This step creates the meta-project structure and plans the TS repo reconciliation — it does NOT move or rename the existing TS repo yet.

### Create meta-project structure:

```bash
mkdir -p ~/code/{active,archive,docs}
mkdir -p ~/code/docs/{guides,specs,architecture,reference,repo-examples}
mkdir -p ~/code/docs/guides/{agent-developer,skill-developer,hook-developer,routine-developer,system-admin}
mkdir -p ~/code/docs/reference/{anthropic,paperclip,community}
mkdir -p ~/code/docs/architecture/diagrams
mkdir -p ~/code/active/chris-os/{agents,infrastructure,skills,routines}
mkdir -p ~/code/active/chris-os/infrastructure/{paperclip,slack-bridge,server,monitoring}
mkdir -p ~/code/.claude
cd ~/code && git init
```

### Plan tibetan-spirit directory reconciliation:

The master spec target structure for tibetan-spirit is:
```
~/code/active/tibetan-spirit/
├── COMPANY.md
├── CLAUDE.md
├── agents/          (shared, customer-service, operations, finance)
├── routines/        (routine scripts)
├── evals/           (Promptfoo YAML + test fixtures)
├── scripts/         (utility scripts)
└── lib/             (shared Python library)
```

The existing repo at `~/code/active/tibetan-spirit-ops/` has its own structure (documented in Step 0 audit). Create a reconciliation plan:

```bash
# Document what exists in the current TS repo
echo "=== tibetan-spirit-ops structure ==="
find ~/code/active/tibetan-spirit-ops/ -maxdepth 3 -type d | grep -v __pycache__ | grep -v .git | grep -v node_modules
echo "=== Key config files ==="
cat ~/code/active/tibetan-spirit-ops/CLAUDE.md 2>/dev/null | head -20
cat ~/code/active/tibetan-spirit-ops/pyproject.toml 2>/dev/null | head -20
```

Write reconciliation plan to `~/brain/_inbox/ts-repo-reconciliation.md`:

```markdown
# Tibetan Spirit Repo Reconciliation Plan

## Current: ~/code/active/tibetan-spirit-ops/
[document current structure from audit]

## Target: ~/code/active/tibetan-spirit/
[target structure from master spec]

## Mapping
| Current Location | Target Location | Action | Notes |
|-----------------|-----------------|--------|-------|
| tibetan-spirit-ops/agents/ | tibetan-spirit/agents/ | Migrate | Review agent definitions for format updates |
| tibetan-spirit-ops/scripts/ | tibetan-spirit/scripts/ | Migrate | Verify scripts still needed |
| tibetan-spirit-ops/tests/ | tibetan-spirit/evals/ | Reconcile | Tests may become eval YAML |
| tibetan-spirit-ops/workspace/ | tibetan-spirit/workspace/ | Migrate | Planning docs carry forward |
| ... | ... | ... | ... |

## Decision Required
- Rename tibetan-spirit-ops → tibetan-spirit? Or create fresh and migrate content?
- What to do with existing Git history?
- Which existing agents/scripts are still relevant to the new architecture?
```

**Do NOT create `~/code/active/tibetan-spirit/` yet.** The reconciliation plan needs Chris's approval first. The directory will be created after classification.

Create `~/code/.claude/CLAUDE.md` (project-level, <150 lines):

```markdown
# chris-os System

Root of Chris Mauze's development system. Contains docs, active projects, and archives.

## Navigation
- `docs/guides/` — Teaching docs (how + why)
- `docs/specs/` — Contracts (what must be true)
- `docs/architecture/` — System architecture (master spec lives here)
- `active/chris-os/` — Infrastructure + personal agents
- `active/tibetan-spirit/` — TS e-commerce operations

## Conventions
- All projects follow Paperclip Agent Companies spec
- Each project has COMPANY.md (Paperclip) and CLAUDE.md (Claude Code)
- Guides explain "why" before "how" with concrete examples
- Present work at checkpoints for review before continuing

## Terminology
Routines = recurring scheduled tasks. Tasks = one-off work.
Skills = SKILL.md capability files. Agents = entities with soul files.
See docs/architecture/stack-overview.md for full glossary.
```

Create `~/code/README.md` with system overview, active projects table, and pointer to `docs/TABLE_OF_CONTENTS.md`.

**Checkpoint:** Walk through code/ structure. Explain: docs/ is system-level documentation, active/ holds project repos, each project has its own CLAUDE.md + COMPANY.md. Show how the guide categories (agent-developer, skill-developer, hook-developer, routine-developer, system-admin) map to the concepts Chris needs to learn. Ask if categories make sense. Present the TS repo reconciliation plan and get explicit approval on the migration strategy before proceeding.

---

## Step 4: User-Level Claude Code Configuration

This is the most important file in the system. It loads at EVERY Claude Code session. It must be under 60 lines. Every line must prevent a mistake Claude would otherwise make.

**IMPORTANT:** Chris already has `~/.claude/CLAUDE.md` and `~/.claude/rules/` with extensive content. This step must RECONCILE, not replace. The existing rules/ files contain valuable constraints (anti-patterns, file-budget, parallelization, self-monitoring). Evaluate each:

### 4a. Audit and classify existing ~/.claude/ content:

```bash
# Read existing user-level CLAUDE.md
cat ~/.claude/CLAUDE.md

# Read each rule file
for f in ~/.claude/rules/*.md; do echo "=== $f ==="; cat "$f"; echo; done

# Check existing skills and agents
ls -la ~/.claude/skills/ 2>/dev/null
ls -la ~/.claude/agents/ 2>/dev/null

# Check settings.json
cat ~/.claude/settings.json 2>/dev/null
```

For each existing file, classify:
- **KEEP** — still valid, incorporate into new structure
- **MERGE INTO CLAUDE.md** — essential content that belongs in the <60 line file
- **CONVERT TO SKILL** — detailed content better served as a skill (loaded on demand)
- **ARCHIVE** — outdated or redundant

Present the classification to Chris before making changes.

### 4b. Write new ~/.claude/CLAUDE.md:

```markdown
# Chris Mauze

Solo entrepreneur, AI-automated businesses. Semi-technical (CPO-level + vibe-coding).

## Communication
- Explain "why" before "how." Challenge assumptions, don't agree quickly.
- Direct, technical, evidence-based. No filler.
- Teaching checkpoints: explain plan → STOP for alignment → build → review together.

## Values (highest wins conflicts)
1. Health  2. Ethics  3. Sustainability  4. Growth  5. Efficiency

## Hard Limits
- Nothing customer-facing publishes without human review
- Never misrepresent Tibetan product origins or cultural significance
- Morning meditation and workouts are protected time

## Navigation
- Knowledge: ~/brain/ (Obsidian, PARA)
- Code: ~/code/ (docs, active projects, archives)
- System docs: ~/code/docs/ (guides, specs, architecture)
- Personal files: ~/Documents/ (iCloud)
- Shared files: Google Drive

## VIP Contacts (always surface)
Ashley, Jothi, Dr. Hun Lye, Garrett
```

### 4c. Reconcile ~/.claude/rules/:

Evaluate each existing rule file against the new system. The existing rules (anti-patterns, file-budget, parallelization, self-monitoring) are likely still valuable. Decision matrix:

| Existing Rule File | Recommendation | Rationale |
|---|---|---|
| `anti-patterns.md` | KEEP | Prevents bloat — universally useful |
| `file-budget.md` | KEEP | Enforces file discipline |
| `parallelization.md` | KEEP | Prevents race conditions |
| `self-monitoring.md` | KEEP | Context management is critical |
| [any others found] | EVALUATE | Present to Chris |

Present the classification. Chris decides what stays, what's archived, what's converted.

### 4d. Scaffold ~/.claude/agents/ (subagent definitions):

The master spec defines two subagents at the user level. Check if `~/.claude/agents/` exists and what's already there. Create or update:

`~/.claude/agents/researcher.md`:
```markdown
---
name: researcher
description: Multi-source research specialist. Use when gathering information from docs, web, APIs, or codebases. Reports structured summaries back to the parent session.
tools:
  - Read
  - Glob
  - Grep
  - WebSearch
  - WebFetch
model: claude-sonnet-4-20250514
permissionMode: default
maxTurns: 15
---

# Researcher

You are a research specialist. Your job is to gather, synthesize, and report information.

## Workflow
1. Understand the research question precisely
2. Search available sources (files, web, APIs)
3. Synthesize findings into a structured summary
4. Flag gaps, contradictions, or low-confidence findings
5. Return a concise report — not raw data dumps

## Output Format
Always return:
- **Summary** (3-5 sentences)
- **Key Findings** (bulleted, with sources)
- **Gaps / Uncertainties** (what you couldn't confirm)
- **Recommended Next Steps** (if applicable)
```

`~/.claude/agents/reviewer.md`:
```markdown
---
name: reviewer
description: Code and content review specialist. Use when reviewing PRs, documentation drafts, or implementation quality. Provides structured feedback with severity levels.
tools:
  - Read
  - Glob
  - Grep
model: claude-sonnet-4-20250514
permissionMode: default
maxTurns: 10
---

# Reviewer

You are a review specialist. Your job is to evaluate code or content for quality, correctness, and adherence to standards.

## Workflow
1. Read the target material thoroughly
2. Check against relevant standards (CLAUDE.md, specs, conventions)
3. Identify issues with severity: CRITICAL / MAJOR / MINOR / NIT
4. Provide actionable fix suggestions, not just complaints
5. Note what's done well — reviews should be balanced

## Output Format
Always return:
- **Verdict**: APPROVE / REQUEST CHANGES / NEEDS DISCUSSION
- **Issues** (sorted by severity, with file:line references)
- **Strengths** (what's done well)
- **Suggestions** (improvements that aren't blocking)
```

### 4e. Create/update ~/.claude/settings.json:

Create settings.json with a PreToolUse safety hook that blocks writing secrets to files. If settings.json already exists, merge the safety hook into existing config — do NOT overwrite other settings.

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit",
        "hook": {
          "type": "command",
          "command": "python3 -c \"import sys,json; d=json.load(sys.stdin); c=d.get('input',{}).get('content','') or d.get('input',{}).get('new_string',''); [sys.exit(2) if s in c.lower() else None for s in ['api_key','secret_key','password=','token=','private_key']]; sys.exit(0)\""
        }
      }
    ]
  }
}
```

**Checkpoint:** Count the lines in CLAUDE.md. Must be under 60. Walk Chris through what loads at session start (CLAUDE.md) vs what loads on demand (skills) vs what fires deterministically (hooks). Present the rules/ reconciliation classification and get approval. Present the subagent definitions and explain when each would be used. Ask Chris to predict: "If I start a Claude Code session in ~/code/active/tibetan-spirit/, which CLAUDE.md files load?" (Answer: ~/.claude/CLAUDE.md + ~/code/.claude/CLAUDE.md + ~/code/active/tibetan-spirit/CLAUDE.md — the hierarchy cascades.)

---

## Step 5: Server Setup (2021 MBP)

SSH in via Tailscale. Configure for always-on:

```bash
sudo pmset -a sleep 0 disksleep 0 displaysleep 0 autorestart 1
# Install: Homebrew, Node.js, Git, Python3, PM2, uv, Tailscale
pm2 startup  # Follow output instructions
mkdir -p ~/paperclip ~/deployments ~/docker/{langfuse,grafana}
```

Install Paperclip: `npx paperclipai onboard --yes`

During onboard, create two companies:
- **chris-os**: "Personal operating system — infrastructure, productivity, wellness, creative life"
- **tibetan-spirit**: "Himalayan artisan goods e-commerce"

Create Board user: Chris Mauze.

Start via PM2: `cd ~/paperclip && pm2 start npm --name "paperclip" -- start && pm2 save`

**Checkpoint:** Access Paperclip dashboard at `http://<server-tailscale-ip>:3100` from workbench. Walk through: company selector, empty org chart, budget settings. On iPhone: install Tailscale, open same URL in Safari, "Add to Home Screen" for PWA. Confirm mobile experience works.

---

## Step 6: Monitoring

Healthchecks.io free account. Create checks: `paperclip-heartbeat` (5min), `server-alive` (10min). Add Slack webhook. Create PM2 healthcheck ping script.

**Checkpoint:** Stop the healthcheck, confirm Slack alert fires. Explain dead man's switch pattern.

---

## Step 7: Legacy Inventory (Discovery Only)

Scan ALL legacy locations and produce `~/brain/_inbox/legacy-inventory.md`.

### 7.1 Local filesystem sources:

- `~/cm/brain/` (main old vault) and `~/cm/brain/vault-v0/` (older vault)
- `~/health-wellness-protocols/`, `~/music/`, `~/temp/`
- `~/cm/` workspace root (projects, scripts, configs outside brain/)
- Any other directories identified in Step 0 audit

### 7.2 Google Drive (chrismauze@gmail.com — Personal):

Access via Google Drive desktop client mount or MCP tools. Inventory:

- **My Drive:**
  - `cm/` — workspace mirror or backup
  - `archive/` — historical archive
  - `cmdb_drive/` — database-related files
  - `inbox/` — unprocessed files
  - TS-related files at root level (financial models, legal docs, etc.)
  - Any other top-level directories

- **Shared Drives:**
  - **Tibetan Spirit** — TS team collaboration drive
  - **NORBU** — NORBU-branded TS content (legacy brand name?)
  - **TS Management Team** — TS management/operational docs

For each location: folder count, file count, notable content categories, last modified date range, recommended action.

### 7.3 iCloud Documents and Desktop:

```bash
# iCloud Documents
find ~/Documents/ -maxdepth 2 -type f | wc -l
find ~/Documents/ -maxdepth 2 -type d
ls -la ~/Documents/

# iCloud Desktop
find ~/Desktop/ -maxdepth 2 -type f | wc -l
ls -la ~/Desktop/
```

For each: file count, notable content, recommended action.

### 7.4 Existing codebase — ~/code/active/tibetan-spirit-ops/:

This was partially inventoried in Step 0, but now produce a detailed breakdown:

```bash
# Full structure
find ~/code/active/tibetan-spirit-ops/ -maxdepth 3 -type f -name "*.py" -o -name "*.md" -o -name "*.yaml" -o -name "*.json" | grep -v __pycache__ | grep -v .git | grep -v node_modules

# Git log (recent activity)
cd ~/code/active/tibetan-spirit-ops/ && git log --oneline -20

# Agent definitions
ls ~/code/active/tibetan-spirit-ops/agents/ 2>/dev/null
cat ~/code/active/tibetan-spirit-ops/agents/*.md 2>/dev/null | head -100
```

### 7.5 Produce the inventory document:

`~/brain/_inbox/legacy-inventory.md`:

```markdown
# Legacy Inventory — Phase 0A Discovery
Date: [today]

## Classification Legend
- MIGRATE TO BRAIN — Content belongs in ~/brain/ (personal knowledge)
- MIGRATE TO DOCUMENTS — Content belongs in ~/Documents/ (iCloud personal files)
- ARCHIVE TO GOOGLE DRIVE — Historical, keep accessible but not active
- KEEP IN PLACE — Already in correct location
- RECONCILE — Overlaps with new structure, needs merge plan
- DELETE — Truly obsolete (build artifacts, caches, duplicates)
- DEFER TO 0B — Needs interactive classification with Chris

## Local Sources

### ~/cm/brain/ (main old vault)
- File count: [n]
- Structure: [summary]
- Notable content: [key categories]
- Last modified: [date range]
- **Recommended:** DEFER TO 0B (Track B — interactive vault consolidation)

### ~/cm/ (workspace, excluding brain/)
- [inventory]
- **Recommended:** [classification]

### ~/health-wellness-protocols/
- [inventory]
- **Recommended:** [classification]

### ~/music/
- [inventory]
- **Recommended:** [classification]

### ~/temp/
- [inventory]
- **Recommended:** [classification]

## Google Drive (Personal — chrismauze@gmail.com)

### My Drive/cm/
- [inventory]
- **Recommended:** [classification]

### My Drive/archive/
- [inventory]
- **Recommended:** [classification]

### My Drive/cmdb_drive/
- [inventory]
- **Recommended:** [classification]

### My Drive/inbox/
- [inventory]
- **Recommended:** [classification]

### My Drive/ (TS files at root)
- [inventory]
- **Recommended:** [classification]

### Shared Drives/Tibetan Spirit
- [inventory — folder count, key content areas]
- **Recommended:** KEEP (consolidation target — see Step 7a)

### Shared Drives/NORBU
- [inventory]
- **Recommended:** CONSOLIDATE into Tibetan Spirit drive (see Step 7a)

### Shared Drives/TS Management Team
- [inventory]
- **Recommended:** CONSOLIDATE into Tibetan Spirit drive (see Step 7a)

## iCloud

### Documents/
- File count: [n]
- Notable content: [categories]
- **Recommended:** [classification]

### Desktop/
- File count: [n]
- Notable content: [categories]
- **Recommended:** [classification]

## Existing Codebase

### ~/code/active/tibetan-spirit-ops/
- Structure: [detailed directory tree]
- Key files: [list with descriptions]
- Git history: [recent activity summary]
- Active agents: [list]
- Active scripts: [list]
- **Recommended:** RECONCILE (see ts-repo-reconciliation.md from Step 3)

## Notion Workspace
See Step 7b for detailed Notion inventory.

## Summary Statistics
| Source | Files | Recommended Action |
|--------|-------|-------------------|
| ~/cm/brain/ | [n] | Defer to 0B |
| Google Drive (Personal) | [n] | Mixed — see details |
| Google Drive (Shared × 3) | [n] | Consolidate → 1 drive |
| iCloud | [n] | Classify |
| tibetan-spirit-ops | [n] | Reconcile |
| Notion | [n pages] | See Step 7b |
```

**DO NOT MOVE ANYTHING.** This is inventory only. Phase 0B executes the migration after Chris classifies each source.

**Checkpoint:** Present inventory. Walk through each source and recommended classification. Ask Chris to confirm or override each recommendation. This classification drives Phase 0B Track B.

---

## Step 7a: Google Drive Consolidation Plan (Discovery + Plan Only)

Chris currently has three TS-related shared drives:
1. **Tibetan Spirit** — primary TS collaboration drive
2. **NORBU** — legacy brand name, likely overlapping content
3. **TS Management Team** — management/operational subset

The master spec target is a single **Tibetan Spirit** shared drive.

### Produce the consolidation plan:

Inventory each drive's top-level folder structure, file counts by folder, and last-modified dates. Then produce `~/brain/_inbox/google-drive-consolidation-plan.md`:

```markdown
# Google Drive Consolidation Plan — TS Shared Drives
Date: [today]
Status: PLAN ONLY — awaiting Chris's approval before any moves

## Current State

### Shared Drive: Tibetan Spirit
[folder tree with file counts and date ranges]

### Shared Drive: NORBU
[folder tree with file counts and date ranges]

### Shared Drive: TS Management Team
[folder tree with file counts and date ranges]

## Overlap Analysis
[Identify duplicate or overlapping content across the three drives]

## Proposed Consolidated Structure

Tibetan Spirit/ (single shared drive)
├── [proposed folder structure]
├── ...
└── _archive/           ← Content from decommissioned drives

## Migration Plan

### Phase 1: Merge NORBU → Tibetan Spirit
| Source (NORBU) | Destination (TS) | Action | Notes |
|----------------|-------------------|--------|-------|
| [folder] | [folder] | Move / Merge / Archive | [notes] |

### Phase 2: Merge TS Management Team → Tibetan Spirit
| Source (TS Mgmt) | Destination (TS) | Action | Notes |
|------------------|-------------------|--------|-------|
| [folder] | [folder] | Move / Merge / Archive | [notes] |

### Phase 3: Decommission empty drives
- Remove NORBU shared drive (after confirming empty)
- Remove TS Management Team shared drive (after confirming empty)

## Sharing/Permissions
[Note any permission changes needed — who currently has access to each drive?]

## Risks
- [List risks: broken links, shared file references, team members losing access, etc.]
- [Mitigation for each]

## Decision Required
Chris: Please review and either approve this plan, request modifications,
or flag specific items that need discussion. Nothing moves until you say go.
```

**DO NOT MOVE ANY FILES.** This is a plan document only. The actual consolidation happens after Chris reviews and approves, potentially during Phase 0B or as a standalone task.

**Checkpoint:** STOP. Present the consolidation plan. Walk Chris through the overlap analysis. Ask: "Are there any folders or files in these drives that are sensitive, shared with external partners, or have specific permission requirements I should know about?" Get explicit approval or revision requests.

---

## Step 7b: Notion Workspace Inventory (Discovery Only)

Use Notion MCP tools to inventory Chris's Notion workspace. The goal is to classify every page/database for its go-forward home.

### Inventory scope:

1. **Chris's Brain** (personal workspace):
   - Top-level pages and databases
   - Nested content (sample to reasonable depth, not exhaustive)
   - Last edited dates where available

2. **TS Dashboard / TS operational pages:**
   - Company Home, Brand Guidelines, Academy, SOPs
   - Product catalogs, vendor docs
   - Any databases (inventory trackers, order logs, etc.)

3. **Inbox and unorganized content:**
   - Pages in default/unsorted locations

### Use Notion MCP tools:

```
notion-search: Search for top-level pages and databases
notion-fetch: Read specific pages for content classification
```

### Produce classification document:

`~/brain/_inbox/notion-inventory.md`:

```markdown
# Notion Workspace Inventory
Date: [today]
Status: INVENTORY ONLY — interactive classification with Chris in Phase 0B

## Classification Legend
- KEEP IN NOTION — Team-facing content (SOPs, brand guidelines, product catalogs, academy)
- MIGRATE TO BRAIN — Chris-only knowledge (personal notes, system architecture, decisions)
- ARCHIVE — Outdated content, keep in Notion but move to archive section
- LINK ONLY — Keep in Notion, add reference link in brain/ (content serves both audiences)

## Chris's Brain (Personal Workspace)

| Page/Database | Type | Last Edited | Content Summary | Classification |
|---------------|------|-------------|-----------------|----------------|
| [page name] | [page/db] | [date] | [summary] | [recommendation] |
| ... | ... | ... | ... | ... |

## Tibetan Spirit Pages

### Team-Facing (recommend: KEEP IN NOTION)
| Page/Database | Type | Last Edited | Content Summary | Notes |
|---------------|------|-------------|-----------------|-------|
| Company Home | Page | [date] | [summary] | Primary TS landing page |
| Brand Guidelines | Page | [date] | [summary] | Referenced by team + vendors |
| Academy | Database | [date] | [summary] | Training modules |
| SOPs | Page/DB | [date] | [summary] | Operational procedures |
| ... | ... | ... | ... | ... |

### Chris-Only (recommend: MIGRATE TO BRAIN or CODE)
| Page/Database | Type | Last Edited | Content Summary | Target |
|---------------|------|-------------|-----------------|--------|
| [page] | [type] | [date] | [summary] | brain/2-Areas/... or code/... |
| ... | ... | ... | ... | ... |

### Uncertain (recommend: DISCUSS WITH CHRIS)
| Page/Database | Type | Last Edited | Content Summary | Options |
|---------------|------|-------------|-----------------|---------|
| [page] | [type] | [date] | [summary] | [option A / option B] |
| ... | ... | ... | ... | ... |

## Summary
- Total pages inventoried: [n]
- Keep in Notion: [n]
- Migrate to brain/: [n]
- Migrate to code/: [n]
- Archive: [n]
- Needs discussion: [n]

## Next Steps
Interactive classification happens in Phase 0B. Chris reviews each batch
and approves/overrides recommendations before any content is moved or modified.
```

**DO NOT MODIFY any Notion content.** Read-only inventory. Phase 0B handles migration with interactive Chris approval per batch.

**Checkpoint:** STOP. Present the Notion inventory. Walk through the classification recommendations. Highlight any "uncertain" items that need Chris's input. Ask: "Are there any Notion pages shared with team members (Jothi, vendors) that I might have missed? Any databases with active integrations (Zapier, etc.) that we need to be careful about?"

---

## Step 8: Table of Contents

Create `~/code/docs/TABLE_OF_CONTENTS.md` listing every planned guide, spec, and architecture doc with checkboxes tracking completion. Create `~/brain/TABLE_OF_CONTENTS.md` for the vault.

**Checkpoint:** Show both TOCs. Ask if any guides/specs are missing.

---

## Step 9: Git Push

Commit and push both repos (brain + code) to private GitHub repos. Verify .gitignore works.

**Checkpoint:** Confirm both visible on GitHub. Verify no .obsidian/workspace.json or .env files.

---

## Verification & Testing

> Start a new session: "Read `/Users/chrismauze/code/active/tibetan-spirit-ops/workspace/plans/REQ-1b/02-phase-0a-core-structure.md` — you're responsible for running the verification checklist at the bottom."

### Structure Verification

- [ ] Dotfiles visible in Finder
- [ ] `~/brain/` exists with PARA structure (1-Projects, 2-Areas, 3-Resources, 4-Archive, _inbox)
- [ ] `~/brain/CLAUDE.md` exists and is under 30 lines (count them: `wc -l ~/brain/CLAUDE.md`)
- [ ] `~/brain/.gitignore` excludes .obsidian/workspace.json, .trash/, .DS_Store
- [ ] `~/code/` exists with docs/, active/, .claude/
- [ ] `~/code/.claude/CLAUDE.md` exists and is under 150 lines (count: `wc -l ~/code/.claude/CLAUDE.md`)
- [ ] `~/code/docs/guides/` has all five subdirectories (agent-developer, skill-developer, hook-developer, routine-developer, system-admin)
- [ ] `~/code/docs/reference/` has three subdirectories (anthropic, paperclip, community)
- [ ] `~/code/active/chris-os/` has agents/, infrastructure/, skills/, routines/

### Claude Code Configuration Verification

- [ ] `~/.claude/CLAUDE.md` exists and is under 60 lines (count: `wc -l ~/.claude/CLAUDE.md`)
- [ ] `~/.claude/settings.json` has PreToolUse safety hook for secrets
- [ ] `~/.claude/rules/` — all retained rule files present and unmodified (per Chris's approval)
- [ ] `~/.claude/agents/researcher.md` exists with valid YAML frontmatter
- [ ] `~/.claude/agents/reviewer.md` exists with valid YAML frontmatter
- [ ] CLAUDE.md cascade test: verify `ls ~/.claude/CLAUDE.md ~/code/.claude/CLAUDE.md ~/brain/CLAUDE.md` — all three exist

### Server Verification

- [ ] Server: `pmset` configured (sleep 0, autorestart 1)
- [ ] Server: PM2 running with Paperclip process
- [ ] Server: Tailscale connected to mesh
- [ ] Paperclip dashboard accessible from workbench at `http://<server-ip>:3100`
- [ ] Paperclip dashboard accessible from iPhone as PWA
- [ ] Two companies exist in Paperclip: chris-os, tibetan-spirit
- [ ] Board user created: Chris Mauze

### Monitoring Verification

- [ ] Healthchecks.io account active with paperclip-heartbeat (5min) and server-alive (10min) checks
- [ ] Slack webhook configured and tested
- [ ] Dead man's switch verified: stopped heartcheck, Slack alert received

### Inventory & Reconciliation Verification

- [ ] `~/brain/_inbox/current-state-audit.md` exists with complete audit of existing state
- [ ] `~/brain/_inbox/legacy-inventory.md` exists with all sources inventoried
- [ ] `~/brain/_inbox/ts-repo-reconciliation.md` exists with TS repo mapping plan
- [ ] `~/brain/_inbox/google-drive-consolidation-plan.md` exists with three-drive-to-one plan
- [ ] `~/brain/_inbox/notion-inventory.md` exists with complete Notion workspace inventory
- [ ] Chris has reviewed and classified each legacy source (classifications documented)
- [ ] Chris has reviewed and approved/revised the Google Drive consolidation plan
- [ ] Chris has reviewed the Notion inventory classifications
- [ ] Existing `~/.claude/rules/` files reconciled (kept/archived/converted per Chris's approval)
- [ ] Existing `~/code/active/tibetan-spirit-ops/` reconciliation plan approved

### Documentation Verification

- [ ] `~/code/docs/TABLE_OF_CONTENTS.md` created with complete checklist
- [ ] `~/brain/TABLE_OF_CONTENTS.md` created
- [ ] `~/code/README.md` created with system overview

### Git Verification

- [ ] `~/brain/` — Git initialized, committed, pushed to private GitHub repo
- [ ] `~/code/` — Git initialized, committed, pushed to private GitHub repo
- [ ] No `.obsidian/workspace.json` in Git (check: `git -C ~/brain ls-files | grep workspace`)
- [ ] No `.env` files in Git (check: `git -C ~/code ls-files | grep .env`)
- [ ] No secrets in committed files

### Cascade Test (Manual)

Open a terminal and verify the CLAUDE.md cascade loads correctly:

```bash
# In ~/brain/ — should load: ~/.claude/CLAUDE.md + ~/brain/CLAUDE.md
cd ~/brain && claude --print-system-prompt 2>/dev/null | head -5

# In ~/code/ — should load: ~/.claude/CLAUDE.md + ~/code/.claude/CLAUDE.md
cd ~/code && claude --print-system-prompt 2>/dev/null | head -5

# In ~/code/active/chris-os/ — should load all three levels
cd ~/code/active/chris-os && claude --print-system-prompt 2>/dev/null | head -5
```

### Phase 0A Exit Criteria

All of the above must be checked. If any item fails, fix it before declaring Phase 0A complete. The inventory and reconciliation items (Step 0, Step 7, 7a, 7b) produce PLANS — the actual migrations happen in Phase 0B. Phase 0A is complete when:

1. All directories and config files exist with correct content and line limits
2. Server infrastructure is running and monitored
3. Every legacy source is inventoried with Chris's classification
4. Google Drive consolidation plan is produced and reviewed
5. Notion inventory is produced and reviewed
6. Existing codebase reconciliation plan is produced and reviewed
7. Both repos are on GitHub with clean .gitignore
