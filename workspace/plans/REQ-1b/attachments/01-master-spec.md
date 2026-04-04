# chris-os — Architecture Specification v2

**Version:** 2.0 | **Owner:** Chris Mauzé | **Status:** Approved

---

## 1. Purpose

Single source of truth for how Chris Mauzé's portfolio of AI-automated businesses and personal systems are structured, built, and operated. In case of conflict with any other document, this spec wins. The system follows the Paperclip Agent Companies Specification — markdown files are canonical, Git repos are package containers, the filesystem is the source of truth.

---

## 2. Terminology

These terms follow Paperclip's nomenclature exactly. Using them consistently prevents confusion.

| Term | Definition | Example |
|------|-----------|---------|
| **Company** | Isolated organizational unit with its own agents, budgets, tasks, and audit trails | chris-os, tibetan-spirit |
| **Agent** | Entity that does work. Has a soul file, skills, and heartbeat schedule | Chief of Staff, Finance Analyst |
| **Task** | One-off unit of work assigned to an agent | "Research top 5 incense subscription competitors" |
| **Routine** | Recurring scheduled task. `recurring: true` in TASK.md, cron in `.paperclip.yaml` | Daily Order Summary (6pm), Weekly P&L (Mon 6am) |
| **Skill** | SKILL.md file teaching an agent how to do something. Agent Skills open standard | brand-guidelines, ticket-triage |
| **Heartbeat** | Scheduled wake cycle: load context → check assignments → execute → report → sleep | Every 2hrs during business hours |
| **Soul file** | SOUL.md — agent's character, values, judgment framework, behavioral boundaries | "Ruthlessly filter. Chris should see 10-15 emails, not 80." |
| **Board** | Human oversight. Approves hires, overrides strategy, sets budgets | Chris |
| **Routine script** | The Python/shell code an agent executes to fulfill a routine. Implementation detail, not a Paperclip concept | `routines/daily_summary/run.py` |

### What Claude Code handles natively (no Paperclip needed)

Claude Code automatically loads `~/.claude/CLAUDE.md` (user-level) and `./CLAUDE.md` (project-level) at every session start. However, Anthropic wraps this content with a system reminder: *"this context may or may not be relevant — you should not respond unless it is highly relevant to your task."* This means Claude actively ignores CLAUDE.md content it deems irrelevant. Therefore: keep CLAUDE.md lean, put details in skills.

Claude Code discovers skills in `.claude/skills/` and loads them on demand via semantic matching against the description field. Hooks in `.claude/settings.json` fire deterministically (100% enforcement, unlike CLAUDE.md's ~80%). Subagent definitions in `.claude/agents/` are available for spawning.

### What Paperclip adds

Organizational structure (companies, org charts, teams). Budget enforcement with auto-pause at 100%. Heartbeat scheduling. Board governance gates. Multi-company data isolation. Dashboard for monitoring. Atomic task checkout.

---

## 3. Design Principles

**Markdown is canonical.** Every definition lives as a markdown file in Git. Databases are derived runtime state.

**Build atoms before molecules.** No orchestration until standalone scripts run reliably for 7 consecutive days on real data.

**Routines over agents.** Most operational tasks are routines (deterministic, fixed control flow). The "agent" label is reserved for genuine dynamic decision-making.

**Eval-driven development.** Write the eval before the skill. No eval = not ready to build.

**Progressive trust.** Every agent starts at maximum supervision. Override rate is the master metric.

**CLAUDE.md is advisory (~80%). Hooks are deterministic (100%).** Safety-critical constraints go in hooks. Guidance goes in skills.

**CLAUDE.md must be lean.** User-level: under 60 lines. Project-level: under 150 lines. "If I remove this line, will Claude make mistakes?" If no, cut it. Details belong in skills (loaded on demand), not CLAUDE.md (loaded every session).

**Mission cascade.** Every task traces through goal → project → company mission. No connection = should not exist.

**Decouple from Paperclip.** Every routine script must run without Paperclip. If Paperclip breaks, routines still work via PM2 cron.

---

## 4. Hardware

Three machines, Tailscale mesh VPN.

**2024 MacBook Pro** (Apple Silicon) — **workbench**. Development, Obsidian, interactive Claude Code.

**2021 MacBook Pro** (Intel, 128GB, 2TB) — **server**. Always-on headless. Paperclip, PM2, Docker, Slack bridge. `pmset -a sleep 0 disksleep 0 displaysleep 0 autorestart 1`.

**ROK-BOX** (RTX 3080, 128GB) — **GPU lab**. Whisper transcription, local LLM testing. Used on-demand only.

---

## 5. File System (Workbench)

```
/Users/chrismauze/
├── .claude/                                ← USER-LEVEL (every session, <60 lines)
│   ├── CLAUDE.md                           ← Identity, values, navigation pointers
│   ├── settings.json                       ← Global safety hooks
│   └── skills/                             ← Skills available everywhere
│
├── brain/                                  ← Obsidian vault (LOCAL + Git, NOT iCloud)
│   ├── CLAUDE.md                           ← Vault schema, quality standards
│   ├── 1-Projects/ 2-Areas/ 3-Resources/ 4-Archive/ _inbox/
│   └── TABLE_OF_CONTENTS.md
│
├── code/                                   ← Git repo: chris-os system
│   ├── .claude/CLAUDE.md                   ← Meta-project navigation (<150 lines)
│   ├── docs/
│   │   ├── guides/                         ← Teaching docs (how + why)
│   │   ├── specs/                          ← Contracts (what must be true)
│   │   ├── architecture/                   ← System docs (this file lives here)
│   │   ├── reference/                      ← External material
│   │   └── repo-examples/                  ← Clonable project archetypes
│   ├── active/
│   │   ├── chris-os/                       ← Infrastructure + personal agents
│   │   │   ├── COMPANY.md
│   │   │   ├── agents/ (chief-of-staff, fitness-coach, research-analyst)
│   │   │   ├── infrastructure/ (paperclip, slack-bridge, server, monitoring)
│   │   │   ├── skills/                     ← Shared personal agent skills
│   │   │   └── routines/                   ← Routine scripts
│   │   └── tibetan-spirit/                 ← E-commerce operations
│   │       ├── COMPANY.md
│   │       ├── agents/ (shared, customer-service, operations, finance)
│   │       ├── routines/                   ← Routine scripts
│   │       ├── evals/ scripts/ lib/
│   │       └── (content/dharma skills live in agents/shared/)
│   ├── archive/
│   └── README.md
│
├── Documents/                              ← iCloud — personal reference files
├── Music/                                  ← LOCAL — Ableton projects
└── Google Drive/                           ← Organization files + archive
```

**Cloud rules:** iCloud = personal files only you need. Google Drive = shared with others + archive. GitHub = all code + brain vault. No Git repos on iCloud or Google Drive.

---

## 6. Companies

### chris-os

The operating system. Contains ALL infrastructure (Paperclip server, Slack bridge, monitoring) AND all personal agents (Chief of Staff, Fitness Coach, Research Analyst, and any future personal agents). This is the company that makes Chris's life work.

### tibetan-spirit

The primary active e-commerce operation. Contains TS-specific agents and routines. Content skills (including dharma teaching material, Buddhist terminology preservation, product photography standards) live here as shared agent skills since they serve TS operations.

### Future companies

Created as empty Paperclip shells on demand when a new venture becomes active. Not pre-planned.

---

## 7. Values Cascade

Each level inherits from above. Cannot override, only extend.

**Level 0 — Constitution** (`~/.claude/CLAUDE.md`): Health > Ethics > Sustainability > Growth > Efficiency.
**Level 1 — Company** (COMPANY.md): chris-os adds attention protection. TS adds cultural authenticity, right livelihood.
**Level 2 — Agent** (SOUL.md): Per-agent judgment framework and decision authority.
**Level 3 — Skill** (SKILL.md): Per-task constraints, frequency caps, escalation triggers.

---

## 8. HITL: Slack + Paperclip Dashboard

**Slack** = fast lane (notifications, quick approvals, lock screen). **Dashboard** = deep lane (full review, editing, budgets, org chart, via Tailscale PWA on phone).

Routine executes → Paperclip ticket → Slack bridge (polls 30s) → Block Kit message → Chris approves in Slack → bridge updates Paperclip → downstream action.

---

## 9. Phases (no timelines)

**0A:** Core structure (directories, Git, Paperclip shell, server).
**0B:** Parallel: docs/guides + legacy consolidation.
**1:** First atoms (TS routines, Chief of Staff, Slack bridge, evals).
**2:** TS core (CS drafts, inventory, campaigns, descriptions, Langfuse).
**3:** Personal agents (Fitness Coach, Research Analyst, cross-company).
**4:** Portfolio (PDF deck, then website).
**5:** Deepening (skill quality, autoresearch, expanded agents).
