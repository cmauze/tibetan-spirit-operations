# chris-os — Architecture Specification v3

**Version:** 3.0 | **Owner:** Chris Mauzé | **Status:** Draft — pending review
**Supersedes:** v2.0 | **Changes from v2:** Paperclip-agnostic fallback architecture, Claude Code native capabilities (Agent Teams, subagents, /batch), Notion workspace integration, enhanced CLAUDE.md cascade, session management strategy, Google Drive consolidation

---

## 1. Purpose

Single source of truth for how Chris Mauzé's portfolio of AI-automated businesses and personal systems are structured, built, and operated. In case of conflict with any other document, this spec wins.

The system uses the **Paperclip Agent Companies Specification** as the organizational framework — but every component is designed to function independently of Paperclip. Markdown files are canonical. Git repos are package containers. The filesystem is the source of truth. If Paperclip disappears tomorrow, the system degrades gracefully: routines still run via PM2 cron, approvals shift to Slack-only, and budget tracking falls back to local logs.

---

## 2. Terminology

These terms follow Paperclip's nomenclature. Using them consistently prevents confusion across all docs, guides, and session prompts.

| Term | Definition | Example |
|------|-----------|---------|
| **Company** | Isolated organizational unit with its own agents, budgets, tasks, and audit trails | chris-os, tibetan-spirit |
| **Agent** | Entity that does work. Has a soul file, skills, and heartbeat schedule. Reserved for genuine dynamic decision-making — most work is better served by routines | Chief of Staff, Finance Analyst |
| **Task** | One-off unit of work assigned to an agent | "Research top 5 incense subscription competitors" |
| **Routine** | Recurring scheduled task. `recurring: true` in TASK.md, cron in `.paperclip.yaml`. The workhorse of the system | Daily Order Summary (6pm), Weekly P&L (Mon 6am) |
| **Skill** | SKILL.md file teaching an agent how to do something. Follows the Agent Skills open standard (agentskills.io) | brand-guidelines, ticket-triage |
| **Heartbeat** | Scheduled wake cycle: load context → check assignments → execute → report → sleep | Every 2hrs during business hours |
| **Soul file** | SOUL.md — agent's character, values, judgment framework, behavioral boundaries. Character, not procedures | "Ruthlessly filter. Chris should see 10-15 emails, not 80." |
| **Board** | Human oversight layer. Approves, overrides, sets budgets. Currently: Chris only | Chris |
| **Routine script** | Standalone Python/shell code that fulfills a routine. Zero framework dependencies. Implementation detail, not a Paperclip concept | `routines/daily_summary/run.py` |

### What Claude Code handles natively (no Paperclip needed)

Claude Code provides three progressive disclosure layers:

**Layer 1 — CLAUDE.md (loaded every session, ~80% adherence):**
- `~/.claude/CLAUDE.md` — user-level identity, values, navigation (<60 lines)
- `./CLAUDE.md` — project-level context (<150 lines per project)
- Hierarchy cascades: user → parent project → project. All three load when opening a nested project.
- Anthropic wraps content with: *"this context may or may not be relevant."* Claude actively ignores content it deems irrelevant. Therefore: every line must prevent a specific mistake. If removing a line wouldn't change behavior, cut it.

**Layer 2 — Skills (loaded on demand via semantic matching, ~95% when matched):**
- `.claude/skills/` directories with SKILL.md files
- Claude matches the `description` frontmatter field against the current task
- Supporting files: `examples/`, `references/`, `templates/`, `tests/`
- This is where detailed instructions, conventions, and domain knowledge live

**Layer 3 — Hooks (deterministic, 100% enforcement):**
- `.claude/settings.json` hook definitions
- Events: `PreToolUse`, `PostToolUse`, `Notification`, `Stop`
- Handler: shell command receives JSON on stdin, exit code controls behavior
- Exit 0 = allow, exit 2 = block with feedback message
- Safety-critical constraints MUST go in hooks, not CLAUDE.md or skills

**Additional native capabilities:**
- **Subagents** (`.claude/agents/`): Custom agent definitions with YAML frontmatter (name, description, tools, model, permissionMode, maxTurns, skills, hooks). Run in separate context windows, report back summaries. Built-in types: `general-purpose`, `Explore` (Haiku, read-only), `Plan` (read-only), `claude-code-guide`.
- **Agent Teams** (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`): Independent Claude Code sessions with 1M-token context each. File-based coordination via tasks and mailboxes. Seven primitives: TeamCreate, Task, TaskCreate, TaskList, TaskUpdate, SendMessage, TeamDelete. Practical limit: ~5 teammates before diminishing returns.
- **/batch**: Codebase-wide transformations. Fans out to worktree-isolated agents. Useful for migrations and large refactors.
- **/compact** and **/clear**: Context management. Compact at ~50% usage. Clear between unrelated tasks. Document-and-clear pattern for knowledge transfer across sessions.

### What Paperclip adds (and what we'd lose without it)

| Capability | Paperclip | Fallback without Paperclip |
|-----------|-----------|---------------------------|
| Org structure (companies, teams) | Dashboard + API | Markdown files in Git (already canonical) |
| Budget enforcement (auto-pause at 100%) | Built-in | Local cost_tracker.py logs + manual alerts |
| Heartbeat scheduling | Cron via Paperclip | PM2 cron (already a dependency) |
| Board governance gates | Ticket → approve/reject | Slack-only approval flow |
| Multi-company data isolation | Built-in | Directory isolation (already enforced) |
| Dashboard monitoring | Web UI via Tailscale | Healthchecks.io + Slack alerts |
| Atomic task checkout | API-based | File-locking (Agent Teams pattern) |

**Design implication:** Every routine script has ZERO Paperclip imports. The integration layer (`heartbeat_runner.py`) is a thin wrapper (~20 lines) that can be swapped for a PM2 cron wrapper with identical behavior. Test both paths.

### Paperclip maturity assessment (as of March 2026)

Paperclip is **4 weeks old** (created 2026-03-02), MIT-licensed, 42.7k stars, 1,451 open issues, switched from semver to calver within 3 weeks. The concepts (companies, heartbeats, atomic task checkout, budget enforcement, soul files) are strong and worth adopting as **patterns**. The framework itself is too immature to take as a hard dependency.

**What to adopt from Paperclip (conceptually):**
- Heartbeat protocol pattern (wake → check identity → claim task → work → report)
- Soul file separation (SOUL.md for identity, HEARTBEAT.md for execution, TOOLS.md for capabilities)
- Atomic task checkout (409 Conflict on concurrent claims)
- Goal ancestry (every task traces back to company mission)
- Budget enforcement at the orchestration layer

**What NOT to do:**
- Do not adopt Paperclip as a framework dependency at this stage
- Do not build against Paperclip APIs that may change weekly
- Do not assume Paperclip's dashboard replaces the need for your own monitoring
- DO build Paperclip-compatible markdown files so adoption is easy later if it matures

**The practical path:** Build routine scripts that are standalone. Build a thin heartbeat_runner.py that assembles context and calls them. If/when Paperclip matures, the heartbeat_runner becomes a Paperclip adapter. Until then, PM2 cron is the scheduler.

### Agent Skills standard — adopt immediately

The Agent Skills open standard (agentskills.io) is **production-ready** with 30+ tool support (Claude Code, Codex, Cursor, Gemini CLI, VS Code Copilot, etc.). 14.7k stars on the spec repo, 107k stars on anthropics/skills.

**SKILL.md format:** YAML frontmatter (`name`, `description`, optional `license`, `compatibility`, `metadata`, `allowed-tools`) plus markdown instructions. Progressive disclosure: ~100 tokens for discovery, <5000 for activation, on-demand for deep reference.

**Promptfoo** (18.9k stars, MIT, acquired by OpenAI March 2026) is the standard eval framework. YAML-first, 40+ assertion types, native Anthropic support. Use deterministic assertions first (`contains`, `is-json`, `javascript`), `llm-rubric` only for subjective qualities.

**Skill marketplaces:** Antigravity Awesome Skills (1,340+, best curation) > SkillHub (7k+) > SkillsMP (87k+, least curated). Fork infrastructure skills, don't depend on external repos at runtime.

---

## 3. Design Principles

**Markdown is canonical.** Every definition lives as a markdown file in Git. Databases are derived runtime state. If it's not in Git, it doesn't exist.

**Build atoms before molecules.** No orchestration until standalone scripts run reliably for 7 consecutive days on real data. This is non-negotiable.

**Routines over agents.** Most operational tasks are routines (deterministic, fixed control flow). The "agent" label is reserved for genuine dynamic decision-making where the entity must reason about what to do, not just how to do it.

**Eval-driven development.** Write the Promptfoo eval before the routine script. No eval = not ready to build. The eval defines "good output" — the routine is just the code that produces it.

**Progressive trust.** Every agent starts at maximum supervision (Tier 3). Override rate is the master metric. Graduation: Tier 3 (human reviews every output) → Tier 2 (human reviews exceptions) → Tier 1 (auto-execute, human reviews weekly digest).

**CLAUDE.md is advisory (~80%). Hooks are deterministic (100%).** Safety-critical constraints go in hooks. Behavioral guidance goes in skills. Identity and navigation go in CLAUDE.md.

**CLAUDE.md must be lean.** User-level: under 60 lines. Project-level: under 150 lines. Test: "If I remove this line, will Claude make mistakes?" If no, cut it.

**Mission cascade.** Every task traces through goal → project → company mission. No connection = should not exist.

**Decouple from all frameworks.** Every routine script runs without Paperclip. Every skill follows the Agent Skills standard (not a Paperclip-specific format). Every definition lives in plain Git markdown. Framework lock-in is a design bug.

**Specification first.** Write the README and docs before the code. The documentation IS the specification. A vague README produces vague code.

**Context engineering.** (From Tasklet philosophy.) Plumb the right data into the model at the right time. The user should have the illusion of total recall without actually loading everything. Our progressive disclosure stack achieves this: lean CLAUDE.md (~100 tokens) → skills on demand (<5000 tokens) → reference files on demand (unlimited). Each layer loads only when needed. Heartbeat_runner assembles tailored context per routine run. Sub-agents receive only what they need, not the full conversation history.

**Routine-to-agent promotion.** Start with deterministic routines (predictable, auditable, cheap). When override rate stays >25% despite soul file rewrites, the task may need genuine agentic reasoning. Promote to a full agent with dynamic decision-making only when routines prove too rigid. This bridges the "routines over agents" principle with the reality that some tasks genuinely need model agency.

**Soul file evolution is a graduation step.** After the 7-day graduation period, the soul file gets rewritten based on observed error patterns, override history, and accumulated run data. This is a standard step for every agent, not an ad-hoc process.

**Structured execution logs from day one.** Every routine run produces a structured log (inputs, decisions with reasoning, actions taken, cost, latency). Store in Supabase. This feeds the eval system, enables Chris to review agent behavior, and provides the data for soul file evolution. Langfuse (Phase 2) enhances this, but a simpler version ships in Phase 1.

**The iterative recommendation principle.** Agents don't just execute — they observe patterns and recommend system improvements (new labels, new skills, new routines, new triggers). The pattern: observe → recommend → Board approves → system updates. Agents never make organizational changes autonomously.

---

## 4. Hardware

Three machines, Tailscale mesh VPN.

**2024 MacBook Pro** (Apple Silicon) — **workbench**. Development, Obsidian, interactive Claude Code sessions. This is where you sit.

**2021 MacBook Pro** (Intel, 128GB, 2TB) — **server**. Always-on headless. Paperclip, PM2, Docker, Slack bridge, all automated routines. `pmset -a sleep 0 disksleep 0 displaysleep 0 autorestart 1`.

**ROK-BOX** (RTX 3080, 128GB) — **GPU lab**. Whisper transcription, local LLM testing. Used on-demand only. Not part of the critical path.

---

## 5. File System (Workbench)

```
/Users/chrismauze/
├── .claude/                                ← USER-LEVEL (every session, <60 lines)
│   ├── CLAUDE.md                           ← Identity, values, navigation pointers
│   ├── settings.json                       ← Global safety hooks (deterministic)
│   ├── skills/                             ← Skills available in every project
│   │   └── vault-maintenance/              ← Obsidian vault upkeep (Phase 0B)
│   └── agents/                             ← Custom subagent definitions
│       ├── researcher.md                   ← Multi-source research specialist
│       └── reviewer.md                     ← Code/content review specialist
│
├── brain/                                  ← Obsidian vault (LOCAL + Git, NOT iCloud)
│   ├── CLAUDE.md                           ← Vault schema, PARA rules (<30 lines)
│   ├── .claude/                            ← Vault-specific skills/agents
│   ├── 1-Projects/                         ← Active deliverables with deadlines
│   ├── 2-Areas/                            ← Ongoing responsibilities, no end date
│   ├── 3-Resources/                        ← Reference material by topic
│   │   └── system-wiki/                    ← How chris-os works (Phase 0B Track C)
│   ├── 4-Archive/                          ← Completed/inactive, searchable
│   ├── _inbox/                             ← Unsorted captures, process during weekly review
│   └── TABLE_OF_CONTENTS.md
│
├── code/                                   ← Git repo: chris-os system
│   ├── .claude/CLAUDE.md                   ← Meta-project navigation (<150 lines)
│   ├── docs/
│   │   ├── guides/                         ← Teaching docs (how + why)
│   │   │   ├── agent-developer/            ← Agents, soul files, heartbeats
│   │   │   ├── skill-developer/            ← Writing and structuring skills
│   │   │   ├── hook-developer/             ← Deterministic safety gates
│   │   │   ├── routine-developer/          ← Composable patterns, graduation
│   │   │   └── system-admin/               ← Server, PM2, Tailscale, monitoring
│   │   ├── specs/                          ← Contracts (what must be true)
│   │   ├── architecture/                   ← System docs (this spec lives here)
│   │   ├── reference/                      ← External material (Anthropic, Paperclip, community)
│   │   └── repo-examples/                  ← Clonable project archetypes
│   ├── active/
│   │   ├── chris-os/                       ← Infrastructure + personal agents
│   │   │   ├── COMPANY.md                  ← Paperclip company definition
│   │   │   ├── CLAUDE.md                   ← Project-level context
│   │   │   ├── agents/                     ← Agent definitions (chief-of-staff, etc.)
│   │   │   ├── infrastructure/             ← Paperclip, Slack bridge, server, monitoring
│   │   │   ├── skills/                     ← Shared personal agent skills
│   │   │   └── routines/                   ← Routine scripts (standalone Python)
│   │   └── tibetan-spirit/                 ← E-commerce operations
│   │       ├── COMPANY.md
│   │       ├── CLAUDE.md
│   │       ├── agents/                     ← (shared, customer-service, operations, finance)
│   │       ├── routines/                   ← Routine scripts
│   │       ├── evals/                      ← Promptfoo YAML + test fixtures
│   │       ├── scripts/                    ← Utility scripts
│   │       └── lib/                        ← Shared Python library
│   ├── archive/
│   └── README.md
│
├── Documents/                              ← iCloud — personal reference files ONLY
├── Music/                                  ← LOCAL — Ableton projects (never in cloud)
└── Google Drive/                           ← Shared files + archive
    └── Shared drives/
        └── Tibetan Spirit/                 ← Consolidated from NORBU + TS + TS Mgmt Team
```

### Cloud rules

| Location | Purpose | What belongs here |
|----------|---------|-------------------|
| **GitHub** | All code + brain vault | Everything under version control |
| **iCloud (Documents)** | Personal files only Chris needs | PDFs, personal reference, music software docs |
| **Google Drive (Personal)** | Shared with others + archive | TS financial models, legal docs, historical archive |
| **Google Drive (Shared: Tibetan Spirit)** | TS team collaboration | Product lines, marketing, vendor docs, shipping |
| **Notion** | TS operational wiki + team onboarding | Company Home, Brand Guidelines, Academy, SOPs |

**Hard rule:** No Git repos on iCloud or Google Drive. No .env files in any cloud storage.

### Notion workspace role (go-forward)

Notion remains the **team-facing operational wiki** for Tibetan Spirit. It's where Jothi, vendors, and collaborators interact with TS documentation. Content that is:
- **Team-facing** (SOPs, brand guidelines, product catalogs, academy modules) → stays in Notion
- **Chris-only** (system architecture, technical decisions, personal knowledge) → lives in brain/ or code/
- **Both** (org chart, company overview) → Notion is primary (team access), brain/ gets a reference link

The Notion workspace at `Chris's Brain` (personal) will be inventoried during Phase 0B and content classified interactively with Chris's approval per batch.

### Current state (as of 2026-03-31 audit)

The filesystem has **already partially migrated** to the target architecture. This is NOT a greenfield build.

| Location | Status | Size | Action Needed |
|----------|--------|------|---------------|
| `~/.claude/` | Active — 40-line CLAUDE.md, 18 skills, 1,078 todos | 380M | Update settings.json (still references ~/cm/ paths) |
| `~/brain/` | Active Obsidian vault, PARA structure, git-synced | 575M | Minor: numeric prefixes (00/01/99) vs text labels |
| `~/code/` | Production-ready — 4 active projects incl. tibetan-spirit-ops | 134G | Add docs/guides/specs/ structure |
| `~/cm/` | **LEGACY** — dormant, unmigrated | 5.6G | Consolidate: archive valuable, delete temp (104K files/5.5G) |
| Google Drive | Two accounts mounted, three TS shared drives | — | Consolidate TS drives into single "Tibetan Spirit" |
| Dropbox | Still installed, active sync | — | Evaluate for removal during Phase 0B |
| Notion | Active TS workspace (last edited 2026-03-30) | — | Inventory and classify interactively in Phase 0B |

**Implication for Phase 0A:** The core filesystem (`~/brain/`, `~/code/`, `~/.claude/`) already exists but needs to be **rebuilt from scratch** following the new architecture. The existing `~/brain/` content, `~/cm/`, Google Drive, Notion, and other legacy sources will be inventoried in Phase 0A and selectively migrated during Phase 0B with interactive approval per batch. The `~/.claude/settings.json` still references `~/cm/` paths and needs updating. The `~/code/.claude/CLAUDE.md` is 257 lines (over the 150-line budget).

**The core filesystem going forward:**
```
~/
├── brain/          ← NEW from scratch (PARA). Current brain/ content treated as legacy source.
├── code/           ← Existing structure, enhanced with docs/guides/specs/
├── cm/             ← Archive after consolidation
├── Desktop/        ← macOS default
├── Documents/      ← iCloud
├── GoogleDrive-chrismauze@gmail.com/
└── (other standard macOS folders)
```

---

## 6. Companies

### chris-os

The operating system. Contains ALL infrastructure (Paperclip server, Slack bridge, monitoring) AND all personal agents (Chief of Staff, Fitness Coach, Research Analyst, and any future personal agents). This is the company that makes Chris's life work.

### tibetan-spirit

The primary active e-commerce operation. Contains TS-specific agents and routines. Content skills (dharma teaching material, Buddhist terminology preservation, product photography standards) live here as shared agent skills since they serve TS operations.

### Future companies

Created as empty Paperclip shells on demand when a new venture becomes active. Not pre-planned. Clone from `docs/repo-examples/agent-company/` as starting template.

---

## 7. Values Cascade

Each level inherits from above. Cannot override, only extend.

| Level | Source | Content | Example |
|-------|--------|---------|---------|
| 0 — Constitution | `~/.claude/CLAUDE.md` | Health > Ethics > Sustainability > Growth > Efficiency | "Nothing customer-facing publishes without human review" |
| 1 — Company | `COMPANY.md` | Company-specific values | chris-os: attention protection. TS: cultural authenticity, right livelihood |
| 2 — Agent | `SOUL.md` | Per-agent judgment framework, decision authority | "Ruthlessly filter. Chris should see 10-15 emails, not 80." |
| 3 — Skill | `SKILL.md` | Per-task constraints, frequency caps, escalation triggers | "Max 3 regeneration iterations for product descriptions" |

---

## 8. HITL: Slack + Paperclip Dashboard

**Slack** = fast lane (notifications, quick approvals, lock screen). **Dashboard** = deep lane (full review, editing, budgets, org chart, via Tailscale PWA on phone).

```
Routine executes
  → Paperclip ticket (structured output)
    → Slack bridge polls (30s)
      → Block Kit message with approve/reject buttons
        → Chris approves in Slack
          → Bridge updates Paperclip
            → Downstream action (send email, create PO, etc.)
```

**Fallback path (no Paperclip):** Routine executes → writes JSON to `output/` → PM2-triggered Slack notifier posts Block Kit message → Chris approves → webhook triggers downstream action. Same UX, different plumbing.

---

## 9. Session Management Strategy

Claude Code sessions are the primary development interface. Managing context effectively is critical.

**Context budget rules:**
- <50% context: continue working freely
- 50-60%: use `/compact <focus area>` to summarize
- 60-80%: finish current step, then `/compact` or start fresh session
- >80%: `/clear` or new session. Do NOT continue — quality degrades

**Session patterns:**
- **Single-guide sessions:** One guide per session for Phase 0B Track A. Fresh context = better quality.
- **Document-and-clear:** Have Claude dump plan/progress to a markdown file, `/clear`, start new session reading that file. Full knowledge transfer, fresh context.
- **Subagent offloading:** Use subagents for research-heavy tasks. They run in separate context windows and report back summaries, keeping the parent context clean.
- **Agent Teams for parallel tracks:** When working on independent deliverables (e.g., Track A guides + Track B consolidation), use Agent Teams with clear file ownership per teammate.

**Model routing for cost efficiency:**
- Coordinator/planning: Opus (reasoning quality matters)
- Implementation/execution: Sonnet (good enough, 3-4x cheaper)
- File discovery/search: Haiku via Explore subagent (fast, cheap)
- Set `CLAUDE_CODE_SUBAGENT_MODEL` for automatic routing

---

## 10. Phases (no timelines)

**0A:** Core structure — directories, Git, `.claude/` config, Paperclip shell, server, legacy inventory, Google Drive consolidation plan, Notion inventory.
**0B:** Three parallel tracks — A: docs/guides/specs, B: legacy + Notion consolidation (interactive), C: system wiki + vault maintenance skill.
**1:** First atoms — TS routines (Daily Summary, Weekly P&L), Chief of Staff, Slack bridge, heartbeat_runner, evals, graduation.
**2:** TS core — CS drafts (Intercom), inventory (Shopify), campaigns, product descriptions, customer profiles, Langfuse, compliance check.
**3:** Personal agents — Fitness Coach, Research Analyst, cross-company patterns, subagent evaluator.
**4:** Portfolio — PDF deck, then website. Can overlap with Phases 2-3.
**5:** Deepening — skill quality, autoresearch loops, Financial Controller, content pipeline scoping.

---

## 11. Anti-Patterns (things this system explicitly avoids)

1. **Framework lock-in.** Every component works without Paperclip. Skills follow the open Agent Skills standard. No proprietary formats.
2. **Premature orchestration.** No multi-agent coordination until single agents prove themselves. Build atoms before molecules.
3. **Documentation after code.** Docs come first. If the docs are wrong, the implementation will be wrong.
4. **Aspirational documentation.** Docs describe what IS, not what you wish existed. Mark planned features clearly.
5. **Over-engineering the meta-system.** The documentation/organization system must be simple enough to actually maintain. If updating docs is harder than writing code, the docs will rot.
6. **Autonomous customer-facing actions.** Nothing customer-facing publishes without Board review. This is a hard limit, not a guideline.
7. **Bloated CLAUDE.md.** If a line doesn't prevent a specific mistake, it doesn't belong in CLAUDE.md. Details go in skills.
