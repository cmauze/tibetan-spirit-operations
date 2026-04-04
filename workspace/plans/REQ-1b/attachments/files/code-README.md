# chris-os — The Operating System

This repository is the root of Chris Mauzé's personal and professional operating system. It contains system documentation, active project repositories, and shared infrastructure for running a portfolio of AI-automated businesses and personal productivity agents.

---

## The Development Philosophy

Every project in this system follows a single development pattern:

```
SPECIFICATION → DOCUMENTATION → PLAN → IMPLEMENTATION → TEST
       ↑                                                   │
       └───────────── feedback loop ───────────────────────┘
```

**Specification first.** Before any code exists, write the README and docs that describe what the system will do, who it serves, and how it works. This is the Amazon "Working Backwards" method — the documentation IS the specification.

**Documentation as source of truth.** Claude Code agents read the docs, generate implementation plans, and build from them. If the docs are wrong, the implementation will be wrong. Getting docs right is the highest-leverage activity in the system. Every project has a README that a new collaborator can read and understand without needing to read the code.

**Plan before executing.** Claude Code generates a detailed plan (Braingrid-style task decomposition) from the documentation. Chris reviews and approves the plan. Only then does implementation begin. Each implementation step includes tests that verify the feature works as specified.

**Iterative improvement.** After implementation, test results and real-world usage feed back into the specification. Documentation is updated. The cycle repeats. The system gets better over time because the docs get better over time.

---

## What's Here

```
code/
├── docs/                       System documentation (you are here)
│   ├── guides/                 Teaching docs — explain how and why
│   │   ├── agent-developer/    How agents, soul files, heartbeats work
│   │   ├── skill-developer/    How to write and structure skills
│   │   ├── hook-developer/     How deterministic safety gates work
│   │   ├── routine-developer/  How to build recurring automated tasks
│   │   └── system-admin/       Server, PM2, Tailscale, monitoring
│   ├── specs/                  Contracts — what must be true
│   ├── architecture/           System architecture and diagrams
│   ├── reference/              External material (Anthropic, Paperclip, community)
│   └── repo-examples/          Clonable starting templates for new projects
│
├── active/                     Active projects
│   ├── chris-os/               Infrastructure + personal agents
│   └── tibetan-spirit/         E-commerce operations
│
├── archive/                    Completed or deprecated projects
│
├── .claude/CLAUDE.md           Navigation context for Claude Code sessions
└── this README
```

---

## Active Projects

| Project | Company | Purpose | Status |
|---------|---------|---------|--------|
| **chris-os** | chris-os | Infrastructure (Paperclip, Slack bridge, monitoring) + personal agents (Chief of Staff, Fitness Coach, Research Analyst) | Phase 0 |
| **tibetan-spirit** | tibetan-spirit | E-commerce operations — automated routines for order summaries, P&L, CS drafts, inventory, campaigns | Phase 0 |

New projects are created on demand when a venture becomes active. Clone from `docs/repo-examples/` as a starting template.

---

## How Projects Are Structured

Every project follows the [Paperclip Agent Companies Specification](docs/specs/companies-spec.md). The key files:

```
project-name/
├── COMPANY.md              Who we are, what we're trying to achieve (Paperclip)
├── CLAUDE.md               Navigation context for Claude Code (loaded at session start)
├── .paperclip.yaml         Paperclip runtime config (adapter, env, schedules)
├── agents/
│   ├── shared/             Skills used by ALL agents in this company
│   │   └── skills/
│   │       └── brand-guidelines/
│   │           ├── SKILL.md
│   │           ├── examples/
│   │           ├── references/
│   │           └── templates/
│   └── agent-name/
│       ├── AGENTS.md       Role definition (Paperclip)
│       ├── SOUL.md         Values, judgment, behavioral boundaries
│       └── skills/         Agent-specific capabilities
├── routines/               Recurring task scripts (standalone, portable)
│   └── routine-name/
│       ├── config.yaml     Schedule, model, approval tier, budget
│       └── run.py          The actual script (zero Paperclip dependencies)
├── evals/                  Promptfoo YAML + test fixtures
├── scripts/                Utility scripts (data sync, seeding, etc.)
├── lib/                    Shared Python library for this project
└── README.md               What this project does (specification-first)
```

### The critical rule: routine scripts are portable

Every `run.py` must work standalone: `python routines/daily_summary/run.py --date 2026-04-01`. The script knows nothing about Paperclip. It takes inputs, queries data, calls the Anthropic API, returns structured output.

Paperclip triggers routines via a thin `heartbeat_runner.py` wrapper that assembles context and reports results. If Paperclip disappears, you replace the 20-line wrapper, not the 200-line routine.

---

## How Routines Get Built (The Full Lifecycle)

This diagram shows how a new routine goes from idea to production:

```
┌─────────────────────────────────────────────────────────┐
│  1. SPECIFY                                             │
│  Write the routine's README: what it does, inputs,      │
│  outputs, approval rules, success criteria.             │
│  This is the spec. Do not write code yet.               │
└──────────────────────┬──────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────┐
│  2. EVAL FIRST                                          │
│  Write Promptfoo YAML defining what "good output" looks │
│  like. Test cases with expected results. If you can't   │
│  define good output, the routine isn't ready to build.  │
└──────────────────────┬──────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────┐
│  3. BUILD                                               │
│  Claude Code reads the spec and eval, generates a plan, │
│  Chris approves, Claude implements. Routine script is   │
│  standalone Python with zero Paperclip dependencies.    │
└──────────────────────┬──────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────┐
│  4. PROVE (7 days)                                      │
│  Run on real data for 7 consecutive days via PM2 cron.  │
│  Eval suite passes. HITL gates documented. Chris        │
│  validates outputs daily.                               │
└──────────────────────┬──────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────┐
│  5. GRADUATE                                            │
│  Write soul file. Register as Paperclip agent. Set      │
│  heartbeat schedule and budget. Routine now runs via    │
│  Paperclip heartbeats with Board oversight.             │
└──────────────────────┬──────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────┐
│  6. IMPROVE                                             │
│  Override rate tracked. Eval scores monitored. When     │
│  quality degrades, update spec → update eval → update   │
│  routine. The cycle repeats.                            │
└─────────────────────────────────────────────────────────┘
```

---

## Automated Systems (Current and Planned)

### Running Now
*(None yet — Phase 0 in progress)*

### Phase 1 (Next)
| Routine | Company | Schedule | Model | Approval |
|---------|---------|----------|-------|----------|
| Daily Order Summary | tibetan-spirit | Daily 6pm | Haiku | Auto-logged |
| Weekly P&L | tibetan-spirit | Mon 6am | Sonnet | Board approval |
| Email Triage | chris-os | 3x daily | Sonnet | Board reviews batch |

### Phase 2 (Planned)
| Routine | Company | Schedule | Model | Approval |
|---------|---------|----------|-------|----------|
| CS Email Drafts | tibetan-spirit | Every 30min (business hrs) | Haiku→Sonnet | CS review |
| Inventory Alerts | tibetan-spirit | Daily | Sonnet | Ops manager |
| Campaign Briefs | tibetan-spirit | Bi-weekly | Sonnet | Board approval |
| Product Descriptions | tibetan-spirit | On-demand | Sonnet | Board + ops |
| Email Automation | chris-os | Continuous | Haiku→Sonnet | Adaptive |

### Phase 3 (Planned)
| Routine | Company | Schedule | Model | Approval |
|---------|---------|----------|-------|----------|
| Daily Workout | chris-os | Daily 6am | Sonnet | Board reviews |
| Weekly Training Review | chris-os | Sunday evening | Sonnet | Board approves |
| Research Tasks | chris-os | On-demand | Sonnet | Board reviews |
| Weekly Intelligence Digest | chris-os | Friday afternoon | Sonnet | Auto-logged |

---

## Key Principles

These principles govern everything in the system. They're documented fully in `docs/architecture/stack-overview.md` and `brain/3-Resources/system-wiki/values-and-guardrails.md`.

1. **Specification first.** Write the docs before the code. The documentation is the spec.
2. **Build atoms before molecules.** No orchestration until standalone scripts prove themselves.
3. **Eval-driven development.** Write the eval before the routine. No eval = not ready to build.
4. **Progressive trust.** Every agent starts supervised. Override rate is the master metric.
5. **Portable by default.** Every routine runs without Paperclip. Every skill follows the Agent Skills standard. Every definition lives in Git markdown.
6. **Lean CLAUDE.md.** User-level under 60 lines. Project-level under 150 lines. Details go in skills, not CLAUDE.md.
7. **Cultural sensitivity is non-negotiable.** Nothing customer-facing for Tibetan Spirit publishes without human review.
8. **Iterative recommendation.** Agents don't just execute — they observe patterns and recommend system improvements (new labels, new skills, new routines) for Board approval.

---

## The Three Machines

| Machine | Role | What Runs |
|---------|------|-----------|
| 2024 MacBook Pro | Workbench | Claude Code, Cursor, Obsidian, development |
| 2021 MacBook Pro | Server | Paperclip, PM2, Docker, Slack bridge, all automated routines |
| ROK-BOX | GPU Lab | Whisper transcription, local LLM testing (on-demand only) |

Connected via Tailscale mesh VPN. Development happens on the workbench, deployment happens on the server, heavy compute happens on the ROK-BOX.

---

## For New Collaborators

1. Start with `brain/3-Resources/system-wiki/index.md` — the system wiki explains everything at the right level for your role.
2. Read this README for the development philosophy and project structure.
3. Read the `docs/guides/` relevant to what you'll be doing.
4. Every project has its own README — read that before looking at code.

If something is unclear, that's a documentation bug. Flag it and we'll fix the docs.
