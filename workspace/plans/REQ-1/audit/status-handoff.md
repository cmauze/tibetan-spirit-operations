# REQ-1 Status Handoff

## Session: 2026-03-29 — Initial Planning

**What was done:**
- Comprehensive codebase exploration (lib, scripts, server, skills, tests, pyproject.toml)
- Intercom Essentials API research (capabilities, pricing, integration pattern)
- Multi-sprint execution plan designed (7 sprints, 4 parallel groups)
- REQ-1 folder created with self-contained sprint prompts (01-07)
- Intercom research archived in attachments/
- Memory saved: user profile, architecture decisions, agent pairing pattern

## Session: 2026-03-30 — Paperclip Integration + Values Framework

**What was done:**
- Deep research on Paperclip open source project (39.4K stars, 27 days old, TypeScript/React)
- Integration analysis: adopted concepts, deferred software
- Values-driven agent design research (soul files, frequency caps, content tiers, CEO decision support)
- Created `agents/` directory structure plan (Paperclip-inspired)
- Created soul file templates for 6 agents
- Created values guardrails framework (constitutional values, frequency caps, content tiers)
- Created CEO decision support checklist
- Updated CLAUDE.md with ** markers for incomplete features
- Updated DEV-PLAN.md file organization section
- Created structural changes addendum (00A-structural-changes.md)
- Filed attachments: paperclip-integration-plan.md, values-guardrails-framework.md, intercom-research.md

**Decisions locked:**
- Intercom Essentials (not Zendesk)
- Separate dashboard repo (ts-command-center/)
- Supabase already Pro tier
- Slack workspace ready
- Cursor/Gemini for dashboard, Claude Code for Python backend
- Dev + testing agent pairing for each sprint
- **NEW:** Paperclip concepts adopted, software deferred to post-MVP
- **NEW:** `skills/` → `agents/` restructure (agent-centric with embedded skills)
- **NEW:** Soul files for all 6 agents
- **NEW:** Values guardrails framework (constitutional values, frequency caps, content tiers)
- **NEW:** CEO structured decision support format in all workflow outputs

**Technical Lead Pushback (recorded for transparency):**
1. Paperclip is 27 days old — adopting software now is high-risk. Concepts yes, runtime no.
2. Running Paperclip server duplicates our dashboard + schema + cost tracker — not worth the redundancy.
3. Heartbeat scheduling burns tokens on idle wake-ups — Railway cron is better for 5.5 orders/day.
4. funnel-decomposition skill has no data source (Meta/Google APIs unconnected) — define it, don't build the workflow yet.
5. Moving skills into agent subfolders requires updating every `depends_on` path in 57 SKILL.md files — non-trivial migration in Sprint S1 Prompt 0A.

**What's next:**
- Begin Sprint S1 execution (foundation)
- Each sprint gets a dev agent + testing agent pair
- Supervisor reviews after each parallel group completes

**Blockers:**
- Intercom Essentials account (Chris task, before Sprint S2-W)
- Supabase auth users: chris, jothi, fiona (Chris task, before Sprint S2-D)

**Sprint readiness:**
- S1: READY — no external dependencies
- S2-W: Needs Intercom credentials (or falls back to test mode)
- S2-D: Needs Supabase auth users
- S2-K: READY after S1 Prompt 0A

**Files updated this session:**
- CLAUDE.md — full rewrite with ** markers, agents/ structure, values guardrails
- DEV-PLAN.md — file organization section updated (skills/ → agents/)
- workspace/plans/REQ-1/00-overview.md — added structural changes references
- workspace/plans/REQ-1/00A-structural-changes.md — NEW: path migration + new artifacts
- workspace/plans/REQ-1/attachments/paperclip-integration-plan.md — NEW
- workspace/plans/REQ-1/attachments/values-guardrails-framework.md — NEW
