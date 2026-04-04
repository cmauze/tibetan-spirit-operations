# REQ-1b — chris-os System Build

## Overview
Chris Mauze's personal and professional operating system. AI-automated businesses (Tibetan Spirit e-commerce, personal productivity agents) built on the Paperclip Agent Companies framework with Claude Code as the primary development interface.

## Scope
- Phase 0A: Core filesystem structure, Git repos, .claude/ config, Paperclip shell, server baseline, legacy inventory
- Phase 0B: Foundational documentation (7 guides, 4 specs), legacy consolidation (local + Google Drive + Notion), system wiki
- Phase 1A: First TS routines (Daily Summary, Weekly P&L), Slack bridge, heartbeat_runner, evals, graduation
- Phase 1B: Email automation (replaces Shortwave AI + Tasklet), Chief of Staff agent
- Phase 2: TS operations core (CS drafts, inventory, campaigns, product descriptions, Langfuse)
- Phase 3: Personal agents (Fitness Coach, Research Analyst, cross-company patterns)
- Phase 4: Portfolio and positioning (PDF deck, website)
- Phase 5: Deepening (skill quality, autoresearch, Financial Controller, content pipeline)

## How to Use These Files
Each phase file is self-contained. To execute a phase:
1. Open a new Claude Code session
2. Say: "Read [path to phase file] and start. This is the spec."
3. The agent reads the file, finds the Session Prompt section, and executes with teaching checkpoints
4. At the end, start a NEW session: "Read [same file] — run the Verification & Testing section at the bottom"

## File Index
| File | Purpose |
|------|---------|
| 00-overview.md | This file — epic overview and navigation |
| 01-master-spec.md | Architecture specification (source of truth for conflicts) |
| 02-phase-0a-core-structure.md | Phase 0A: filesystem, Git, config, server, inventory |
| 03-phase-0b-docs-and-consolidation.md | Phase 0B: guides, specs, legacy/Notion/Drive consolidation, wiki |
| 04-phase-1-first-atoms.md | Phase 1: TS routines, email automation, Slack bridge |
| 05-phases-2-through-5.md | Phases 2-5: scope outlines (detailed cards generated per phase) |
| 06-future-backlog.md | System walkthrough + future sprint ideas |

## Acceptance Criteria
- [ ] Clean filesystem: ~/brain/ (Obsidian, PARA) + ~/code/ (system) + no competing locations
- [ ] All 7 guides and 4 specs written, reviewed, understood
- [ ] Two TS routines running reliably for 7+ days with passing evals
- [ ] Email automation classifying into Gmail labels, visible in Shortwave
- [ ] Slack bridge operational (approve/reject via Block Kit messages)
- [ ] Paperclip dashboard accessible (or PM2 fallback operational)
- [ ] Chris can explain: how agents work, how to write a skill, how hooks enforce safety, how graduation works

## Key Principles
1. Specification first — docs before code
2. Build atoms before molecules — no orchestration until standalone scripts prove themselves
3. Eval-driven — write the eval before the routine
4. Progressive trust — every agent starts supervised
5. Decouple from frameworks — everything runs without Paperclip
6. CLAUDE.md lean — user <60 lines, project <150 lines
7. Nothing customer-facing publishes without human review

## Draft READMEs
The attachments/files/ directory contains draft README files for the three main directories:
- brain-README.md -> ~/brain/README.md
- code-README.md -> ~/code/README.md
- chris-os-README.md -> ~/code/active/chris-os/README.md
These are first drafts to be refined during Phase 0A implementation.
