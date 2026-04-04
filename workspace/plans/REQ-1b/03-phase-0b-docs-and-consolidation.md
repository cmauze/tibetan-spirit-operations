# Phase 0B — Docs, Guides, and Legacy Consolidation

**Depends on:** Phase 0A complete
**Produces:** Foundational guides/specs + clean consolidated vault + system wiki + vault maintenance skill

---

## Context

Phase 0A created the empty container. Phase 0B fills it with two things: documentation that teaches how the system works (Track A), and consolidated knowledge from scattered legacy notes and external platforms (Track B). A third track (Track C) then documents the resulting system as a wiki and creates a maintenance skill to keep it healthy. Tracks A and B run in parallel. Track C overlaps with the tail end of Track B and completes after both A and B.

**Critical principle for Track A:** These guides are the medium through which Chris learns the system. Every guide follows: explain concept → concrete examples from Chris's projects → proposed convention → checkpoint → finalize. If Chris cannot explain it back, the guide is not done.

**Critical principle for Track B:** Discovery first, then classification with Chris's explicit approval, then migration. No files move without approval for that specific batch. "I don't want things captured unnecessarily — you should be asking me along the way, per the instructions for that sprint phase." EVERY batch of content must be presented to Chris for classification before any moves. Strong bias toward discarding outdated tech notes. Keep decisions, principles, unique insights, personal reflections, dharma/Buddhism content.

**Critical principle for Track C:** Document the ACTUAL system as built, not the aspirational plan. The wiki and maintenance skill must be simple enough to actually use — the master spec explicitly calls out over-engineering the meta-system as an anti-pattern.

---

## Session Management Notes

Phase 0B spans multiple sessions across three tracks. Context management is critical for quality output.

**Session sizing:**
- **Track A guides:** 1 guide per session (fresh context each time). Context degrades after the first guide. Start a new session for each.
- **Track A specs:** Can batch 2 specs per session if they are short and closely related.
- **Track B batches:** Small enough to review meaningfully. One source/section at a time. Chris must be able to actually read and classify each batch.
- **Track C:** Can overlap with the tail end of Track B. The system wiki benefits from seeing the consolidated vault state.

**Context budget rules:**
- <50% context: continue working freely
- 50-60%: use `/compact <focus area>` to summarize
- 60-80%: finish current step, then start fresh session
- >80%: STOP. Do NOT continue. Quality degrades. `/clear` or new session.

**Model routing (cost efficiency):**
- Coordinator/planning: Opus (reasoning quality matters)
- Implementation/execution: Sonnet (good enough, 3-4x cheaper)
- File discovery/search: Haiku via Explore subagent (fast, cheap)
- Set `CLAUDE_CODE_SUBAGENT_MODEL` for automatic routing

---

## Session Prompts

> Phase 0B has multiple tracks that run as separate sessions. Each prompt below is self-contained — copy-paste directly into a Claude Code terminal session.

### Track A — Docs and Guides

**Prerequisites:** Phase 0A complete. `03-phase-0b-docs-and-consolidation.md` and `01-master-spec.md` accessible.

```
Read these files:
1. 03-phase-0b-docs-and-consolidation.md (Track A: docs buildout)
2. 01-master-spec.md (architecture spec)
3. ~/code/docs/TABLE_OF_CONTENTS.md (what needs writing)
4. workspace/plans/REQ-1b/attachments/prompt to get started.md (pre-research on Agent Teams, subagents, Notion migration)

You are helping me build the foundational documentation for chris-os.
This is a LEARNING process, not just writing. I need to deeply
understand every concept before implementation.

Start with Step A1 (Research Phase). IMPORTANT: The file "prompt to
get started.md" already contains extensive pre-research on Agent Teams,
subagent patterns, Notion migration, and Claude Code coordination. Use
this as a STARTING REFERENCE — your job is to VALIDATE and UPDATE this
pre-research against current sources, not start from scratch. Search
the web for the sources listed in the phase card:
- Anthropic official Claude Code docs (skills, hooks, subagents)
- Paperclip docs (heartbeat protocol, task workflow, companies-spec)
- Community repos (shanraisshan/claude-code-best-practice, etc.)
- Skill ecosystem (SkillsMP, agentskills.io)

NOTE ON PAPERCLIP: Research Paperclip's current status and
documentation quality carefully. It may be very early-stage. Do NOT
over-commit to Paperclip-specific patterns if the docs are thin or
the project is immature. Our system must work without it.

Produce structured reference notes in code/docs/reference/. Then
present findings at the checkpoint before writing guides.

CRITICAL REQUIREMENTS:
- Guide structure: What → Why → How → In Our System → Convention → Common Mistakes → Related Guides
- Read workspace/plans/REQ-1b/attachments/files/guide-documentation-standards.md for the CANONICAL guide format — follow it exactly
- After each guide, STOP and ask me to explain the concept back
- Each guide gets its OWN Claude Code session (fresh context = better quality)
- Research ACTUAL current state of each feature — don't rely on training data
- Use Paperclip terminology: routines (not workflows), tasks, agents, heartbeats
- Concrete examples from my projects, not abstract theory
```

**Watch for:** Agent writing all guides in one session (context degrades — start fresh sessions per guide). Agent defaulting to "workflow" instead of "routine." Agent over-indexing on Paperclip patterns when Paperclip docs may be thin. Agent inventing features that don't exist yet.

---

### Track B — Legacy Consolidation

**Prerequisites:** Phase 0A complete. Legacy inventory at `~/brain/_inbox/legacy-inventory.md`.

```
Read these files:
1. 03-phase-0b-docs-and-consolidation.md (Track B: consolidation — all three sub-tracks)
2. ~/brain/_inbox/legacy-inventory.md (inventory from Phase 0A)

You are consolidating knowledge from multiple sources into my Obsidian
vault at ~/brain/. This covers THREE domains: local legacy files,
Google Drive, and Notion.

CRITICAL REQUIREMENT — READ THIS CAREFULLY:
"I don't want things captured unnecessarily — you should be asking me
along the way." Process ONE source/section at a time. Present contents
and recommended classification for EACH batch. I must explicitly
approve each batch before you move any files or content.

CLASSIFICATION RULES:
- DISCARD: outdated technical notes (LangGraph, LangChain, pre-2026
  AI architecture, framework comparisons no longer relevant).
- KEEP: decisions, principles, unique insights, personal reflections,
  Buddhism/dharma content, fitness programming notes.
- ARCHIVE (don't delete): anything uncertain → Google Drive archive.
- Strong bias toward discarding. When in doubt, ask me.

FOR LOCAL FILES (B1a):
- Sources: ~/cm/, ~/health-wellness-protocols/, ~/temp/
- Add consistent YAML frontmatter to every migrated markdown file.
- Rename to lowercase-with-hyphens.md convention.
- Start with ~/cm/brain/ (the largest source). Show top-level structure
  and sample files before proposing classifications.

FOR GOOGLE DRIVE (B1b):
- Present the three TS shared drives for consolidation approval.
- Move personal archive from My Drive to Google Drive archive.
- Clean up inbox/ and cmdb_drive/.
- Present current state and proposed actions. Do NOT move anything
  without my explicit approval.

FOR NOTION (B1c):
- Use the Notion MCP tools to inventory Chris's Brain workspace.
- Classify each page/database: keep in Notion (team-facing), migrate
  to brain/ (Chris-only knowledge), archive (outdated).
- Process ONE section at a time. I approve each batch.
- Team-facing content (SOPs, brand guidelines, academy) stays in Notion.
- Chris-only knowledge migrates to brain/.
- Outdated content gets archived.
```

**Watch for:** Agent moving files before getting explicit approval. Agent capturing content Chris doesn't want. Agent trying to process too much in one batch. Notion inventory should be interactive, not automated.

---

### Track C — System Wiki and Vault Maintenance

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
│   ├── the-stack.md                  ← Every tool, why it's there, what it does
│   └── the-email-automation-system.md ← Email automation architecture (planned for Phase 1B)
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
The "the-email-automation-system.md" page should be clearly marked as
planned for Phase 1B — include the architectural concept but note it
is not yet built.

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

CRITICAL: The skill should make the vault EASIER to maintain over
time, not harder. If it creates bureaucratic overhead (tagging
taxonomies nobody follows, elaborate filing systems), it's failed.
The best maintenance system is one that's so simple it actually gets
used. The master spec anti-pattern #5 applies here: "Over-engineering
the meta-system. The documentation/organization system must be simple
enough to actually maintain. If updating docs is harder than writing
code, the docs will rot."

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
```

**Watch for:** The agent writing an aspirational wiki that documents unbuilt features as if they exist. The agent designing an over-engineered vault maintenance system (elaborate tag hierarchies, complex review workflows). The best vault system is the one simple enough to actually use. The wiki should be accurate to the CURRENT state of the system — mark future phases clearly.

**Timing:** This prompt should run AFTER Phase 0B Track A (docs/guides exist to reference) and Track B (vault is consolidated, so the agent can see the real content patterns). It can overlap with the tail end of Track B.

---

## Track A: Docs and Guides

### A1: Research Phase

Before writing guides, research current best practices across Claude Code, Paperclip, and the community. Produce structured reference notes in `code/docs/reference/`.

**Pre-research available:** The file `workspace/plans/REQ-1b/attachments/prompt to get started.md` already contains extensive pre-research on Agent Teams (file-based swarms, seven coordination primitives, hard limitations), subagent patterns (complete frontmatter reference, three production-proven coordinator patterns, Anthropic's own code review pattern), and Notion-to-Obsidian migration (MCP server landscape, four migration tools, eight pitfalls, PARA mapping). This should be used as a starting reference. The research phase should VALIDATE and UPDATE this pre-research rather than starting from scratch.

**Specific validation tasks:**
1. Confirm Agent Teams limitations are still current (the pre-research lists 10 constraints as of March 2026)
2. Verify subagent frontmatter fields haven't changed
3. Check if `/batch` command capabilities have expanded
4. Confirm Notion MCP server recommendations are still accurate
5. Research Paperclip's current status and documentation quality — it may be very early-stage. The plan should not over-commit to Paperclip-specific patterns if the docs are thin or the project is immature.

**Sources to research:**
1. Anthropic official docs — skills, hooks, subagents, agent teams, headless mode, sessions, settings cascade
2. Paperclip docs — heartbeat protocol, task workflow, writing a skill, handling approvals, cost reporting, companies-spec
3. Community repos — shanraisshan/claude-code-best-practice, ChrisWiles/claude-code-showcase, hesreallyhim/awesome-claude-code, Anthropic's plugin-dev hook-development SKILL.md
4. Skill ecosystem — SkillsMP, SkillHub, agentskills.io, Antigravity Awesome Skills

For each source, produce a reference note with: key takeaways for our system, patterns to adopt, patterns to avoid, notable examples worth adapting.

**Checkpoint:** Present top 5-7 patterns that should shape our guides. Identify community skills worth forking (infrastructure/utility only). Flag Paperclip maturity level (early-stage/stable/production-ready) and recommend how heavily to lean on Paperclip-specific patterns. Get alignment before writing guides.

### A2: Write Foundational Guides

Each guide follows this structure: What This Is → Why It Matters → How It Works → In Our System (concrete examples) → Convention → Common Mistakes → Related Guides. **Read `workspace/plans/REQ-1b/attachments/files/guide-documentation-standards.md` for the canonical format** — every guide must match this template.

**Session management:** Each guide should be written in its own Claude Code session to prevent context degradation. Start a fresh session, read this phase card and the relevant reference notes, write one guide, checkpoint, done. Do not batch multiple guides.

Write in this order (each builds on previous):

1. **`guides/agent-developer/how-agents-work.md`** — Agent vs routine. Lifecycle (wake → context → assignments → execute → report → sleep). Heartbeat system. "Memento Man" metaphor. In our system: Daily Summary is a routine, Chief of Staff is an agent.

2. **`guides/skill-developer/writing-a-skill.md`** — SKILL.md anatomy. Frontmatter fields. Supporting files (examples/, references/, templates/, tests/). Semantic matching on description. Agent Skills open standard. Complete example: brand-guidelines skill with full directory.

3. **`guides/hook-developer/hook-fundamentals.md`** — What hooks are (event-driven, not instructions). Events, handler types, JSON stdin, exit codes. How hooks differ from skills (OS vs apps). The safety hook from Phase 0A as worked example.

4. **`guides/routine-developer/composable-patterns.md`** — Anthropic's six patterns (single call, prompt chain, routing, parallelization, orchestrator-workers, evaluator-optimizer). When to use each. How our routines map. March of Nines reliability math.

5. **`guides/agent-developer/writing-a-soul-file.md`** — Soul file purpose (character/judgment, NOT procedures). Paperclip's file system (AGENTS.md, SOUL.md, HEARTBEAT.md, TOOLS.md). Start with 20 lines, add rules only when agents misbehave.

6. **`guides/agent-developer/heartbeat-protocol.md`** — How heartbeats work. The checklist (confirm identity → wake context → plans → assignments → checkout → execute → extract facts → exit). Context compiled fresh each cycle. How PM2 cron maps to heartbeats.

7. **`guides/routine-developer/graduation-model.md`** — Standalone script → graduated agent. Graduation checklist. Override rate as master metric. Tier 3 → 2 → 1 progression.

8. **`guides/system-admin/session-management.md`** — How to manage Claude Code sessions effectively. Context budgets (<50% continue, 50-60% compact, 60-80% finish and compact, >80% stop). `/compact` usage with focus guidance. `/clear` for task switches. Document-and-clear pattern for knowledge transfer across sessions. Subagent offloading to keep parent context clean. Agent Teams for parallel independent work. Model routing strategy (Opus for planning, Sonnet for execution, Haiku for discovery). When to start a new session vs continue. Named sessions with `/rename`. The "agent dumb zone" and how to avoid it. Practical examples from our system: one-guide-per-session pattern, research-then-write pattern, batch review pattern.

**Checkpoint after each guide:** Chris explains the concept back. If gaps, revise. Only proceed when confirmed.

### A3: Write Foundational Specs

1. **`specs/skills-spec.md`** — Our SKILL.md standard extending agentskills.io. Frontmatter fields, supporting file convention, complete example directory.

2. **`specs/agents-spec.md`** — Agent definition standard. What goes in SOUL.md vs AGENTS.md vs .paperclip.yaml. Agent-centric directory layout.

3. **`specs/values-guardrails-spec.md`** — Values cascade (constitution → company → agent → skill). Frequency caps, content tiers, product framing. CEO decision support format.

4. **`specs/companies-spec.md`** — Vendor the Paperclip companies-spec into our docs.

5. **`specs/routine-portability-spec.md`** — The contract for how routine scripts must be framework-independent. This is the most important architectural constraint and deserves its own spec. Contents: Zero Paperclip imports in routine scripts. Standalone CLI execution (`python routines/daily_summary/run.py --date 2026-04-01` must work). Pydantic structured output (every routine returns a Pydantic model, serialized to JSON). Input contract (arguments or stdin, never framework-specific context objects). The `heartbeat_runner.py` wrapper pattern (thin integration layer, ~20 lines, swappable). Testing contract (routine testable without any framework running). The "if Paperclip disappears" litmus test: replacing the 20-line wrapper, not the 200-line routine.

**Checkpoint:** Present each spec. Confirm it accurately represents the conventions to enforce.

### A4: Repo Examples

Minimal but complete clonable archetypes in `docs/repo-examples/`:
- `python-routine-project/` — Routine-based project (TS-style)
- `agent-company/` — Paperclip company package
- `web-project/` — Web/portfolio project

**Checkpoint:** Walk through each. Every file explained.

---

## Track B: Legacy Consolidation

Track B covers THREE consolidation domains. Process them in order (B1a → B1b → B1c), though batches within each domain proceed one at a time with Chris's explicit approval.

**Critical note from Chris:** "I don't want things captured unnecessarily — you should be asking me along the way, per the instructions for that sprint phase." EVERY batch of content must be presented to Chris for classification before any moves. Strong bias toward discarding outdated tech notes. Keep decisions, principles, unique insights, personal reflections, dharma/Buddhism content.

### B1a: Local Legacy Files

**Sources:** `~/cm/`, `~/health-wellness-protocols/`, `~/temp/`

Present Phase 0A inventory to Chris in batches. For each source: what's in it, recommended classification, overlaps with new vault. One source at a time.

**Classification guidance:**
- DISCARD: outdated technical notes (LangGraph, LangChain, pre-2026 AI architecture, framework comparisons no longer relevant)
- KEEP: decisions, principles, unique insights, personal reflections, Buddhism/dharma content, fitness programming notes
- ARCHIVE: anything uncertain → Google Drive

**Migration per approved batch:** copy to destination, add consistent YAML frontmatter, rename to lowercase-with-hyphens.md convention, verify file counts, stage originals in `_migrated/`.

### B1b: Google Drive Consolidation

Present the current state of Google Drive for Chris's review and approval:

1. **Three TS shared drives** — Present current structure and propose consolidation plan. These may include NORBU, TS, and TS Mgmt Team drives referenced in the master spec.
2. **Personal archive from My Drive** — Propose moving to Google Drive archive location.
3. **inbox/ and cmdb_drive/ cleanup** — Inventory contents, propose classification.

Present proposed actions for each area. Do NOT move anything without explicit approval.

### B1c: Notion Workspace

Interactive inventory of Chris's Brain workspace in Notion. Use the Notion MCP tools.

**Process:**
1. Use `notion-search` to inventory the workspace — list all top-level pages and databases.
2. Present the inventory to Chris with recommended classification for each:
   - **Keep in Notion** — team-facing content (SOPs, brand guidelines, product catalogs, academy modules, anything Jothi/vendors/collaborators use)
   - **Migrate to brain/** — Chris-only knowledge (personal decisions, system architecture notes, technical thinking, dharma content)
   - **Archive** — outdated content (old project plans, stale meeting notes, obsolete processes)
3. Process ONE section at a time. Chris must approve each batch before proceeding.
4. For content migrating to brain/: use `notion-fetch` to get page content, convert to clean markdown, add YAML frontmatter, place in appropriate PARA location.
5. For archived content: mark in Notion or move to an archive section.

**Notion go-forward role (from master spec):** Notion remains the team-facing operational wiki for Tibetan Spirit. Content that is team-facing stays in Notion. Content that is Chris-only migrates to brain/. Content that serves both gets Notion as primary (team access) with brain/ getting a reference link.

### B2: Migration Execution

Per approved batch across all three domains: copy to destination, add consistent frontmatter, rename to convention, verify file counts, stage originals in `_migrated/`.

### B3: Clean Up

Move `_migrated/` to Google Drive archive. Delete empty directories. Uninstall Dropbox if approved. Update TABLE_OF_CONTENTS.md. Final scan for orphans. Commit to Git.

**Checkpoint:** Walk through final vault state. Confirm nothing important lost.

---

## Track C: System Wiki and Vault Maintenance

### C1: System Wiki

Create a section in `~/brain/3-Resources/system-wiki/` that explains how chris-os works. Three audiences: Chris (primary reference), Garrett (technical collaborator), Ashley (non-technical collaborator).

**Wiki structure:**

```
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
│   ├── the-stack.md                  ← Every tool, why it's there, what it does
│   └── the-email-automation-system.md ← Email automation architecture (planned for Phase 1B)
└── reference/
    ├── glossary.md                   ← Every term defined (Paperclip terminology + ours)
    ├── people-and-roles.md           ← Who does what (Chris, Jothi, Fiona, etc.)
    └── troubleshooting.md            ← Common problems and how to fix them
```

**Writing guidelines:**
- Every page starts with a one-sentence summary of what this page covers
- concepts/ pages explain ideas without assuming technical knowledge
- how-to/ pages are procedural: numbered steps, expected outcomes, what can go wrong
- architecture/ pages are technical but explain WHY, not just WHAT
- Use Mermaid diagrams where visual explanation helps (render as preview-only)
- Cross-link between wiki pages with [[wikilinks]]
- Include YAML frontmatter on every page (type: reference, status: active, tags: [system-wiki])
- Write for someone reading this for the first time, not someone who sat through our planning sessions
- Keep each page under 200 lines. If longer, split into sub-pages.

**Critical:** This wiki documents the ACTUAL system as built, not the aspirational plan. If something hasn't been implemented yet, don't document it as if it exists. Say "planned for Phase X" or leave it out. The `the-email-automation-system.md` page should be clearly marked as planned for Phase 1B — include the architectural concept but note it is not yet built.

**Checkpoint:** Present index.md and 2-3 example pages for review. Confirm tone, depth, and structure before writing the full wiki.

### C2: Vault Maintenance Skill

After completing the wiki AND after Track B consolidation is complete (you've seen the full state of the vault), create a Claude Code skill at `~/.claude/skills/vault-maintenance/SKILL.md`.

Design the skill based on what you've learned about the vault's actual state during consolidation, not based on a generic template.

**Before writing the skill, present your assessment:**
- What patterns did you observe during consolidation?
- What kinds of notes tend to accumulate without organization?
- What are the most common sources of new content going forward? (Claude artifacts from phone, meeting notes, research, project updates, email-worthy ideas captured quickly)
- What maintenance cadence makes sense (daily? weekly? ad-hoc)?
- What should the skill CHECK vs what should it DO autonomously vs what should it PROPOSE for human review?

**Checkpoint:** Present assessment and proposed scope. Chris approves before writing.

**Skill directory:**

```
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
```

**SKILL.md frontmatter:**
```yaml
---
name: vault-maintenance
description: Organize, clean, and maintain the Obsidian vault. Use when
  asked to "clean up notes," "organize inbox," "review vault health,"
  "process captures," or during scheduled vault maintenance sessions.
  Also use when adding new notes to ensure consistent formatting.
---
```

**Critical:** The skill should make the vault EASIER to maintain over time, not harder. If it creates bureaucratic overhead (tagging taxonomies nobody follows, elaborate filing systems), it's failed. The best maintenance system is one that's so simple it actually gets used. Master spec anti-pattern #5: "Over-engineering the meta-system."

---

## Verification & Testing

### Track A Verification

**Research (A1):**
- [ ] Reference notes in `code/docs/reference/` for each source
- [ ] Pre-research from "prompt to get started.md" validated and updated
- [ ] Paperclip maturity level assessed and documented
- [ ] Top 5-7 patterns identified and approved by Chris
- [ ] Community skills worth forking identified (infrastructure/utility only)

**Guides (A2):**
- [ ] 8 guides written and reviewed (7 original + session-management)
- [ ] Each guide follows canonical format from `guide-documentation-standards.md`
- [ ] Chris can explain each concept back (teaching checkpoints passed)
- [ ] Each guide written in its own session (no context degradation)
- [ ] TABLE_OF_CONTENTS.md updated

**Specs (A3):**
- [ ] 5 specs written and reviewed (4 original + routine-portability-spec)
- [ ] `routine-portability-spec.md` clearly defines the framework-independence contract
- [ ] Each spec accurately represents conventions to enforce
- [ ] Chris has confirmed each spec

**Repo Examples (A4):**
- [ ] 3 repo examples created
- [ ] Every file in each example explained

### Track B Verification

**Local files (B1a):**
- [ ] All sources classified by Chris (one batch at a time)
- [ ] Migrations executed per approved batches
- [ ] YAML frontmatter added to all migrated markdown
- [ ] Files renamed to lowercase-with-hyphens.md

**Google Drive (B1b):**
- [ ] Three TS shared drives reviewed and consolidation approved
- [ ] Personal archive relocated
- [ ] inbox/ and cmdb_drive/ cleaned

**Notion (B1c):**
- [ ] Chris's Brain workspace fully inventoried
- [ ] Each page/database classified (keep/migrate/archive)
- [ ] Chris-only knowledge migrated to brain/ with frontmatter
- [ ] Team-facing content confirmed in Notion
- [ ] Outdated content archived

**Cleanup (B2-B3):**
- [ ] `_migrated/` moved to Google Drive archive
- [ ] Empty directories removed
- [ ] TABLE_OF_CONTENTS.md reflects new content
- [ ] Orphan scan completed
- [ ] All changes committed to Git

### Track C Verification

**Wiki (C1):**
- [ ] System wiki created at `brain/3-Resources/system-wiki/`
- [ ] Index page and all concept/how-to/architecture/reference pages written
- [ ] `the-email-automation-system.md` clearly marked as planned (Phase 1B)
- [ ] Wiki documents ACTUAL system state, not aspirations
- [ ] Three audiences served (Chris, Garrett, Ashley)
- [ ] All pages under 200 lines with proper frontmatter

**Vault Maintenance Skill (C2):**
- [ ] Assessment of vault patterns presented and approved
- [ ] Skill created at `~/.claude/skills/vault-maintenance/`
- [ ] Simple enough to actually use (anti-pattern #5 test)
- [ ] References, templates, and examples included

### Integration Verification

- [ ] Chris can explain how agents work, how to write a skill, how hooks enforce safety, what the composable patterns are, how graduation works, how to manage sessions effectively
- [ ] One vault, one docs system, no competing locations
- [ ] No important content lost from legacy sources, Google Drive, or Notion
- [ ] Notion workspace role clarified: team-facing stays, Chris-only migrated, outdated archived
- [ ] All changes on GitHub
