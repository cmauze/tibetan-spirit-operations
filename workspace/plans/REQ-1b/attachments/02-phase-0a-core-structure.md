# Phase 0A — Core Structure

**Depends on:** Nothing (starting point)
**Produces:** Directories, Git repos, `.claude/` config, Paperclip shell, server baseline

---

## Context

You are setting up the foundational structure for chris-os — Chris Mauzé's personal and professional operating system. Chris is a semi-technical entrepreneur (CPO-level systems thinking, vibe-codes with AI tools). He has a 2024 MacBook Pro (workbench), a 2021 Intel MacBook Pro (always-on server), and a ROK-BOX (GPU lab).

Read the master spec at `code/docs/architecture/stack-overview.md` for full context. This phase card is self-contained but the master spec wins any conflicts.

**Important — how Claude Code loads context natively:** Claude Code automatically reads `~/.claude/CLAUDE.md` and `./CLAUDE.md` at every session start. It wraps this content with a system note saying it may or may not be relevant, so Claude will ignore content it deems irrelevant to the current task. Keep these files lean. Skills in `.claude/skills/` load only when their description matches the task — this is the progressive disclosure mechanism. Hooks in `.claude/settings.json` fire with 100% determinism on every tool use, regardless of context.

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

```bash
mkdir -p ~/brain/{1-Projects,2-Areas,3-Resources,4-Archive,_inbox}
mkdir -p ~/brain/2-Areas/{tibetan-buddhism,ai-engineering,fitness,finance,music-production,home-and-family}
mkdir -p ~/brain/3-Resources/{ai-engineering,cpg-analytics,dharma-teachings,productivity-systems}
mkdir -p ~/brain/.claude
cd ~/brain && git init
```

Create `~/brain/CLAUDE.md` (vault-level — loaded when Claude Code runs inside this directory):

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

**Checkpoint:** Walk through PARA structure. Ask Chris to explain the difference between Projects (has a deadline) and Areas (ongoing, no deadline). Confirm the 2-Areas categories cover his life. Ask if anything is missing.

---

## Step 3: Code Meta-Project

```bash
mkdir -p ~/code/{active,archive,docs}
mkdir -p ~/code/docs/{guides,specs,architecture,reference,repo-examples}
mkdir -p ~/code/docs/guides/{agent-developer,skill-developer,hook-developer,routine-developer,system-admin}
mkdir -p ~/code/docs/reference/{anthropic,paperclip,community}
mkdir -p ~/code/docs/architecture/diagrams
mkdir -p ~/code/active/{chris-os,tibetan-spirit}
mkdir -p ~/code/active/chris-os/{agents,infrastructure,skills,routines}
mkdir -p ~/code/active/chris-os/infrastructure/{paperclip,slack-bridge,server,monitoring}
mkdir -p ~/code/active/tibetan-spirit/{agents,routines,evals,scripts}
mkdir -p ~/code/.claude
cd ~/code && git init
```

Create `~/code/.claude/CLAUDE.md` (project-level, <150 lines):

```markdown
# chris-os System

Root of Chris Mauzé's development system. Contains docs, active projects, and archives.

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

**Checkpoint:** Walk through code/ structure. Explain: docs/ is system-level documentation, active/ holds project repos, each project has its own CLAUDE.md + COMPANY.md. Show how the guide categories (agent-developer, skill-developer, hook-developer, routine-developer, system-admin) map to the concepts Chris needs to learn. Ask if categories make sense.

---

## Step 4: User-Level Claude Code Configuration

This is the most important file in the system. It loads at EVERY Claude Code session. It must be under 60 lines. Every line must prevent a mistake Claude would otherwise make.

Create `~/.claude/CLAUDE.md`:

```markdown
# Chris Mauzé

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

Create `~/.claude/settings.json` with a PreToolUse safety hook that blocks writing secrets to files (same as before but with clear comments explaining the hook pattern).

**Checkpoint:** Count the lines in CLAUDE.md. Must be under 60. Walk Chris through what loads at session start (CLAUDE.md) vs what loads on demand (skills) vs what fires deterministically (hooks). Ask Chris to predict: "If I start a Claude Code session in ~/code/active/tibetan-spirit/, which CLAUDE.md files load?" (Answer: ~/.claude/CLAUDE.md + ~/code/.claude/CLAUDE.md + ~/code/active/tibetan-spirit/CLAUDE.md — the hierarchy cascades.)

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

Create Board user: Chris Mauzé.

Start via PM2: `cd ~/paperclip && pm2 start npm --name "paperclip" -- start && pm2 save`

**Checkpoint:** Access Paperclip dashboard at `http://<server-tailscale-ip>:3100` from workbench. Walk through: company selector, empty org chart, budget settings. On iPhone: install Tailscale, open same URL in Safari, "Add to Home Screen" for PWA. Confirm mobile experience works.

---

## Step 6: Monitoring

Healthchecks.io free account. Create checks: `paperclip-heartbeat` (5min), `server-alive` (10min). Add Slack webhook. Create PM2 healthcheck ping script.

**Checkpoint:** Stop the healthcheck, confirm Slack alert fires. Explain dead man's switch pattern.

---

## Step 7: Legacy Inventory (Discovery Only)

Scan ALL legacy locations and produce `~/brain/_inbox/legacy-inventory.md`:
- `~/cm/brain/` (main old vault) and `~/cm/brain/vault-v0/` (older vault)
- `~/health-wellness-protocols/`, `~/music/`, `~/temp/`
- Google Drive: brain/, cm/, repos/, vault-v0/, daasity-ai, dharma-book-agents, etc.
- Dropbox (Personal), Red Fox Analytics Dropbox

For each: folder count, file count, notable content, last modified date range, recommended action (migrate to brain / migrate to Documents / archive to Google Drive / delete).

**DO NOT MOVE ANYTHING.** This is inventory only. Phase 0B executes the migration after Chris classifies each source.

**Checkpoint:** Present inventory. Ask Chris to classify each source. This classification drives Phase 0B Track B.

---

## Step 8: Table of Contents

Create `~/code/docs/TABLE_OF_CONTENTS.md` listing every planned guide, spec, and architecture doc with checkboxes tracking completion. Create `~/brain/TABLE_OF_CONTENTS.md` for the vault.

**Checkpoint:** Show both TOCs. Ask if any guides/specs are missing.

---

## Step 9: Git Push

Commit and push both repos (brain + code) to private GitHub repos. Verify .gitignore works.

**Checkpoint:** Confirm both visible on GitHub. Verify no .obsidian/workspace.json or .env files.

---

## Verification

- [ ] Dotfiles visible in Finder
- [ ] brain/ exists with PARA, CLAUDE.md (<30 lines), .gitignore
- [ ] code/ exists with docs/, active/, .claude/CLAUDE.md (<150 lines)
- [ ] ~/.claude/CLAUDE.md exists (<60 lines)
- [ ] ~/.claude/settings.json has safety hook
- [ ] Server: pmset, PM2, Tailscale, Paperclip running
- [ ] Paperclip dashboard accessible from workbench + iPhone PWA
- [ ] Healthchecks.io active with Slack alerts
- [ ] Legacy inventory complete, Chris has classified each source
- [ ] Both TOCs created
- [ ] Both repos on GitHub
