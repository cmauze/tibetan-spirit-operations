# Handoff Prompts — Copy-Paste for Claude Code Sessions

Each prompt below is designed to be pasted directly into a Claude Code terminal session. They reference phase card files which should be accessible in the working directory or provided as context.

**How to use:**
1. Download the phase card files into your working directory
2. Start a Claude Code session
3. Copy-paste the relevant prompt
4. The agent reads the phase card and executes with teaching checkpoints

---

## Phase 0A — Core Structure

**Prerequisites:** `02-phase-0a-core-structure.md` and `01-master-spec.md` accessible.

```
Read these two files carefully before doing anything:
1. 02-phase-0a-core-structure.md (step-by-step implementation plan)
2. 01-master-spec.md (architecture spec — source of truth)

You are helping me build the foundational structure for chris-os — my
personal and professional operating system. I'm Chris Mauzé, a
semi-technical entrepreneur who vibe-codes with AI tools.

CRITICAL REQUIREMENTS:
- Execute steps in order. Do NOT skip ahead.
- At every "Checkpoint," STOP and present your work. Explain what you
  built and why. Ask me to confirm understanding before continuing.
- ~/.claude/CLAUDE.md must be UNDER 60 LINES. Claude Code loads this
  every session and ignores content it deems irrelevant. Every line
  must prevent a specific mistake.
- Project-level CLAUDE.md files: UNDER 150 LINES.
- Use Paperclip terminology: routines (recurring), tasks (one-off),
  agents (role definitions with soul files), heartbeats (scheduled
  wake cycles), skills (SKILL.md capability files).

After reading both files, start with Step 1. Explain what you're about
to do and why before making any filesystem changes.
```

**Watch for:** CLAUDE.md exceeding line limits. Agent skipping checkpoints. Agent moving legacy files before classification. Paperclip onboarding may require interactive decisions.

---

## Phase 0B Track A — Docs and Guides

**Prerequisites:** Phase 0A complete. `03-phase-0b-docs-and-consolidation.md` and `01-master-spec.md` accessible.

```
Read these files:
1. 03-phase-0b-docs-and-consolidation.md (Track A: docs buildout)
2. 01-master-spec.md (architecture spec)
3. ~/code/docs/TABLE_OF_CONTENTS.md (what needs writing)

You are helping me build the foundational documentation for chris-os.
This is a LEARNING process, not just writing. I need to deeply
understand every concept before implementation.

Start with Step A1 (Research Phase). Search the web for the sources
listed in the phase card:
- Anthropic official Claude Code docs (skills, hooks, subagents)
- Paperclip docs (heartbeat protocol, task workflow, companies-spec)
- Community repos (shanraisshan/claude-code-best-practice, etc.)
- Skill ecosystem (SkillsMP, agentskills.io)

Produce structured reference notes in code/docs/reference/. Then
present findings at the checkpoint before writing guides.

CRITICAL REQUIREMENTS:
- Guide structure: What → Why → How → In Our System → Convention → Common Mistakes
- After each guide, STOP and ask me to explain the concept back
- Research ACTUAL current state of each feature — don't rely on training data
- Use Paperclip terminology: routines (not workflows), tasks, agents, heartbeats
- Concrete examples from my projects, not abstract theory
```

**Watch for:** Agent writing all 7 guides in one session (context degrades — start fresh sessions per guide). Agent defaulting to "workflow" instead of "routine."

---

## Phase 0B Track B — Legacy Consolidation

**Prerequisites:** Phase 0A complete. Legacy inventory at `~/brain/_inbox/legacy-inventory.md`.

```
Read these files:
1. 03-phase-0b-docs-and-consolidation.md (Track B: consolidation)
2. ~/brain/_inbox/legacy-inventory.md (inventory from Phase 0A)

You are consolidating notes from multiple legacy sources into my
Obsidian vault at ~/brain/.

CRITICAL REQUIREMENTS:
- Process ONE source at a time. Present contents and recommended
  classification for each batch.
- I must explicitly approve each batch before you move any files.
- DISCARD: outdated technical notes (LangGraph, LangChain, pre-2026
  AI architecture, framework comparisons no longer relevant).
- KEEP: decisions, principles, unique insights, personal reflections,
  Buddhism/dharma content, fitness programming notes.
- ARCHIVE (don't delete): anything uncertain → Google Drive.
- Add consistent YAML frontmatter to every migrated markdown file.
- Rename to lowercase-with-hyphens.md convention.

Start with ~/cm/brain/ (the largest source). Show top-level structure
and sample files before proposing classifications.
```

---

## Phase 0B Track C — System Wiki and Vault Maintenance

**Prerequisites:** Phase 0A complete. Phase 0B Track A (docs/guides) in progress or complete. Track B (consolidation) complete.

This prompt creates two things: a human-readable wiki in the Obsidian vault that explains how the entire system works (for Chris, collaborators, and future reference), and a maintenance skill that keeps the vault organized going forward.

```
Read these files:
1. 01-master-spec.md (the architecture spec)
2. 02-phase-0a-core-structure.md (what was built in Phase 0A)
3. All guides and specs in ~/code/docs/guides/ and ~/code/docs/specs/
4. The current state of ~/brain/ (the vault you'll be writing into)
5. The current state of ~/code/ (the system you'll be documenting)

You have two jobs.

JOB 1: CREATE A SYSTEM WIKI IN THE BRAIN VAULT

Create a section in ~/brain/3-Resources/system-wiki/ that explains how
chris-os works. This wiki serves three audiences:

AUDIENCE A — Chris (primary): A reference I return to when I forget how
something works, need to modify the system, or want to add a new routine
or agent. Written at CPO-level: I understand systems thinking but need
the specific mechanics explained clearly.

AUDIENCE B — Technical collaborators (Garrett): Someone technically
capable who needs to understand the system well enough to operate within
it, suggest improvements, or build their own version for a different
business. They've never seen Paperclip or this architecture before.

AUDIENCE C — Non-technical collaborators (Ashley): Someone who needs to
understand what the system does and how to interact with it (approving
things, understanding what agents are doing) without needing to
understand the implementation.

THE WIKI STRUCTURE:

brain/3-Resources/system-wiki/
├── index.md                          ← Start here. System overview, audience guide.
├── concepts/
│   ├── what-is-chris-os.md           ← Plain-language explanation of the system
│   ├── companies-and-agents.md       ← What companies are, what agents are, how roles work
│   ├── routines-and-tasks.md         ← What runs automatically vs what's assigned
│   ├── skills-and-knowledge.md       ← How agents learn to do things
│   ├── approvals-and-oversight.md    ← How humans stay in control (Slack + dashboard)
│   ├── the-brain-vault.md            ← How the knowledge system works (this vault)
│   └── values-and-guardrails.md      ← How values flow through the system
├── how-to/
│   ├── add-a-new-routine.md          ← Step-by-step: creating a new recurring task
│   ├── add-a-new-agent.md            ← Step-by-step: creating a new role with soul file
│   ├── add-a-new-skill.md            ← Step-by-step: teaching an agent something new
│   ├── add-a-new-company.md          ← Step-by-step: starting a new venture in the system
│   ├── review-and-approve.md         ← How to use Slack + dashboard for approvals
│   ├── check-system-health.md        ← Where to look when something seems wrong
│   └── add-notes-to-the-vault.md     ← How to capture and organize knowledge
├── architecture/
│   ├── three-machines.md             ← Workbench, server, GPU lab — what runs where
│   ├── file-system-map.md            ← Complete directory structure with annotations
│   ├── data-flow.md                  ← How data moves: Supabase → routine → Paperclip → Slack
│   └── the-stack.md                  ← Every tool, why it's there, what it does
└── reference/
    ├── glossary.md                   ← Every term defined (Paperclip terminology + ours)
    ├── people-and-roles.md           ← Who does what (Chris, Jothi, Fiona, etc.)
    └── troubleshooting.md            ← Common problems and how to fix them

WRITING GUIDELINES:
- Every page starts with a one-sentence summary of what this page covers
- concepts/ pages explain ideas without assuming technical knowledge
- how-to/ pages are procedural: numbered steps, expected outcomes, what can go wrong
- architecture/ pages are technical but explain WHY, not just WHAT
- Use Mermaid diagrams where visual explanation helps (render as preview-only)
- Cross-link between wiki pages with [[wikilinks]]
- Include YAML frontmatter on every page (type: reference, status: active, tags: [system-wiki])
- Write for someone reading this for the first time, not someone who sat through our planning sessions
- Keep each page under 200 lines. If longer, split into sub-pages.

CRITICAL: This wiki documents the ACTUAL system as built, not the
aspirational plan. If something hasn't been implemented yet, don't
document it as if it exists. Say "planned for Phase X" or leave it out.

Present the index.md and 2-3 example pages for my review before
writing the full wiki. I want to confirm the tone, depth, and
structure before you write 20 pages.

---

JOB 2: CREATE A VAULT MAINTENANCE SKILL

After completing the wiki AND after Track B consolidation is complete
(you've seen the full state of the vault), create a Claude Code skill
at ~/.claude/skills/vault-maintenance/SKILL.md.

This skill should be designed for PERIODIC use — invoked manually or
on a schedule — to keep the vault healthy. But you should DESIGN the
skill based on what you've learned about the vault's actual state,
not based on a generic template.

Before writing the skill, present your assessment:
- What patterns did you observe during consolidation?
- What kinds of notes tend to accumulate without organization?
- What are the most common sources of new content going forward?
  (Claude artifacts from phone, meeting notes, research, project
  updates, email-worthy ideas captured quickly)
- What maintenance cadence makes sense (daily? weekly? ad-hoc)?
- What should the skill CHECK vs what should it DO autonomously
  vs what should it PROPOSE for human review?

Based on your assessment, propose the skill's scope. I'll approve
before you write it.

THE SKILL DIRECTORY:

~/.claude/skills/vault-maintenance/
├── SKILL.md                          ← Core instructions
├── references/
│   ├── frontmatter-schema.md         ← Valid types, statuses, tag conventions
│   └── para-decision-tree.md         ← How to classify a note into PARA
├── templates/
│   ├── daily-capture.md              ← Template for quick notes
│   ├── decision-record.md            ← Template for documenting decisions
│   └── meeting-notes.md              ← Template for meetings
└── examples/
    ├── well-organized-note.md        ← What a properly formatted note looks like
    └── needs-cleanup-note.md         ← What a note looks like before maintenance

The SKILL.md frontmatter should include:
---
name: vault-maintenance
description: Organize, clean, and maintain the Obsidian vault. Use when
  asked to "clean up notes," "organize inbox," "review vault health,"
  "process captures," or during scheduled vault maintenance sessions.
  Also use when adding new notes to ensure consistent formatting.
---

CRITICAL: The skill should make the vault EASIER to maintain over
time, not harder. If it creates bureaucratic overhead (tagging
taxonomies nobody follows, elaborate filing systems), it's failed.
The best maintenance system is one that's so simple it actually gets
used.
```

**Watch for:** The agent writing an aspirational wiki that documents unbuilt features as if they exist. The agent designing an over-engineered vault maintenance system (elaborate tag hierarchies, complex review workflows). The best vault system is the one simple enough to actually use. The wiki should be accurate to the CURRENT state of the system — mark future phases clearly.

**Timing:** This prompt should run AFTER Phase 0B Track A (docs/guides exist to reference) and Track B (vault is consolidated, so the agent can see the real content patterns). It can overlap with the tail end of Track B.

---

## Phase 1 — First Atoms

**Prerequisites:** Phase 0B complete (all tracks). `04-phases-1-through-5-outlines.md`, `01-master-spec.md`, all guides and specs accessible.

```
Read these files:
1. 04-phases-1-through-5-outlines.md (Phase 1 scope outline)
2. 01-master-spec.md (architecture spec)
3. All guides in code/docs/guides/
4. All specs in code/docs/specs/
5. The system wiki at brain/3-Resources/system-wiki/ (current system state)

Phase 1 builds the first working routines and agents. Before writing
any code, generate a DETAILED Phase 1 task card — like the Phase 0A
card but for Phase 1. Use file #1 as scope, #2 as architecture
authority, #3-4 as pattern references.

The task card must include:
- Step-by-step implementation with teaching checkpoints
- Exact file paths for every artifact created
- Verification commands for every step
- The graduation checklist for each routine
- Promptfoo eval YAML written BEFORE routine scripts (eval-driven)

CRITICAL — THE HEARTBEAT RUNNER PATTERN:

Every routine script must be PORTABLE — it knows nothing about
Paperclip. The integration between Paperclip and your scripts happens
through a thin wrapper called heartbeat_runner.py. This wrapper:

1. Receives the heartbeat trigger from Paperclip
2. Reads the task assignment from Paperclip's API
3. Assembles context (soul file content + relevant skills + task details)
4. Calls the routine script, passing inputs as arguments or stdin
5. Receives structured output (Pydantic model / JSON)
6. Reports the result back to Paperclip's ticket system
7. Logs cost to the budget tracker
8. Pings Healthchecks.io

The routine script itself (e.g., routines/daily_summary/run.py) takes
inputs, queries Supabase, calls Anthropic API with loaded skills,
returns structured output. It has ZERO Paperclip imports or API calls.

This means:
- `python routines/daily_summary/run.py --date 2026-04-01` works standalone
- Paperclip triggers it via heartbeat_runner.py
- PM2 can trigger it via a cron wrapper that does the same context assembly
- If Paperclip disappears, you replace the 20-line wrapper, not the 200-line routine

BUILD THIS WRAPPER EXPLICITLY in Phase 1. Do not let Paperclip's
claude_local adapter handle it opaquely. I want to see and understand
every line of the integration layer.

Show me the heartbeat_runner.py architecture (what it does, how it
calls routine scripts, how it reports back) BEFORE building any
routines. This is the most important piece to get right because
everything else depends on it.

ADDITIONAL REQUIREMENTS:
- Agent-centric directory layout per specs/agents-spec.md
- Write Promptfoo eval YAML BEFORE routine scripts (eval-driven)
- Follow composable patterns from guides/routine-developer/composable-patterns.md
- Use Paperclip terminology consistently
- Present the task card for my review before executing anything

Generate the task card first. Do not start building until I approve.
```

**Watch for:** The agent skipping the heartbeat_runner wrapper and letting Paperclip's adapter handle invocation opaquely. The agent importing Paperclip modules inside routine scripts (coupling violation). The agent trying to register agents before 7-day graduation. Existing Supabase schema from the DEV-PLAN may need reconciliation — agent should check what exists before creating migrations. Agent defaulting to "workflow" instead of "routine."

---

## Phase 2 — TS Operations Core

**Prerequisites:** Phase 1 complete.

```
Read:
1. 04-phases-1-through-5-outlines.md (Phase 2 scope)
2. 01-master-spec.md
3. All guides and specs in code/docs/
4. code/active/tibetan-spirit/ (existing from Phase 1)
5. brain/3-Resources/system-wiki/ (current system documentation)

Generate a detailed Phase 2 task card. Phase 2 adds: CS email drafts
(Intercom), inventory alerts (Shopify sync), campaign briefs, product
descriptions (evaluator-optimizer), customer profiles, Langfuse, and
reliability pass.

Before generating: review what exists in TS from Phase 1. New routines
build on the shared library, heartbeat_runner pattern, and eval
patterns established there.

CRITICAL: Include a compliance checkpoint before any automated
customer-facing communications go live (CCPA ADMT). Also include
a step to update the system wiki with the new routines and agents.

Generate task card for review. Do not build until approved.
```

---

## Phase 3 — Personal Agents

```
Read:
1. 04-phases-1-through-5-outlines.md (Phase 3 scope)
2. 01-master-spec.md
3. All guides and specs
4. code/active/chris-os/ (infrastructure + Chief of Staff from Phase 1)

Generate a detailed Phase 3 task card. Adds: Fitness Coach, Research
Analyst, cross-company patterns. Chief of Staff already running —
these follow the same graduation pattern and heartbeat_runner
integration.

The Fitness Coach needs to understand my training philosophy (science-
based, periodized, three modalities: strength, running, mobility).
The Research Analyst serves ALL ventures. Cross-company patterns
define how chris-os agents support tibetan-spirit.

Include a step to update the system wiki with new agents and patterns.

Generate task card for review. Do not build until approved.
```

---

## Phase 4 — Portfolio and Positioning

```
Read:
1. 04-phases-1-through-5-outlines.md (Phase 4 scope)
2. 01-master-spec.md

Build my professional positioning materials. Start with a PDF deck.

Audience: hybrid — employment at AI companies + advisory/operator.

Narrative: who I am (CPG analytics → product leader → AI entrepreneur)
→ what I've built (production NL2SQL agent at Daasity, multi-agent TS
ops, personal OS with Paperclip) → how I think (principles, architecture
philosophy, "March of Nines" operational rigor) → what I'm looking for.

Draft the deck structure (slide titles and content bullets) for review.
Do not build until structure is approved.
```

---

## Ongoing — Vault Maintenance Sessions

After the vault-maintenance skill is created in Phase 0B Track C, use this prompt for periodic maintenance sessions:

```
/vault-maintenance

Process my inbox, check for organizational issues, and present a
maintenance report. Don't make changes — show me what you'd do and
let me approve in batches.
```

Or for a quick capture cleanup:

```
/vault-maintenance

I've dumped several files into ~/brain/_inbox/ over the past week.
Classify each one, add frontmatter, rename to convention, and propose
where it should go in the PARA structure. Present for my approval.
```

---

## Notes on Session Management

**Context window:** Claude Code's context fills fast. For Phase 0B Track A (7 guides), start a fresh session for each guide. Use `/compact` when responses degrade.

**Session continuity:** Each phase card is self-contained. Resume mid-phase by telling the agent which step you completed last.

**Teaching checkpoints:** Every "Checkpoint" is a STOP. Agent presents, explains why, waits for confirmation. If you don't understand, say so — agent re-explains from a different angle.

**Paperclip dashboard:** Keep open during Phase 1+. Verify companies, agents, and routines appear correctly when registered.

**Wiki updates:** After each phase, the system wiki in brain/3-Resources/system-wiki/ should be updated to reflect the current state. The Phase 2+ prompts include this as an explicit step.
