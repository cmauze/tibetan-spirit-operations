# Future Backlog — System Walkthrough and Sprint Ideas

**Purpose:** Part 1 walks through every phase so you can understand the complete system before any code runs. Part 2 catalogs future ideas worth tracking but not building yet.

Read this after absorbing the master spec and before executing any phase cards.

---

## Part 1: The Complete Walkthrough

### After Phase 0A

Your filesystem is clean. Two directories at `~/`: `brain/` (Obsidian vault) and `code/` (everything else). Legacy directories (cm/, health-wellness-protocols/, temp/) are inventoried but not yet migrated.

On the server, Paperclip is running with two empty companies (chris-os, tibetan-spirit) and a Board user. The dashboard is accessible from your workbench and from your iPhone via Tailscale PWA. Healthchecks.io pings every 5 minutes.

Your `~/.claude/CLAUDE.md` (under 60 lines) loads at every Claude Code session, giving every agent your identity and values. A safety hook blocks writing secrets to files. The `code/docs/TABLE_OF_CONTENTS.md` shows 30+ planned guides, all unchecked.

**The experience:** Clean PARA vault with empty folders. Paperclip dashboard with two companies and no agents. Claude Code sessions inherit your global identity. Nothing is automated yet — this is the container.

### After Phase 0B

The foundational guides are written: how agents work, how to write a skill, hook fundamentals, composable patterns, soul files, heartbeat protocol, graduation model. You wrote them by reading source material, asking questions, and iterating. You understand these concepts well enough to explain them.

Legacy notes are consolidated. Old vaults migrated to brain/. Standalone folders absorbed or archived. Dropbox uninstalled. Google Drive has a clean archive. Your knowledge is in one searchable vault.

**The experience:** Consolidated knowledge, documented understanding of every system concept, clean filesystem. Ready to write code.

### After Phase 1

Three things run on the server. Two Tibetan Spirit routines: Daily Order Summary (Haiku, 6pm, auto-logged) and Weekly P&L (Sonnet, Monday 6am, Board approval). Both query Supabase, call Anthropic, write to Paperclip tickets, and ping Healthchecks. Both have Promptfoo evals validated against real data.

The Chief of Staff agent (chris-os company) runs 3x daily, triaging email via Gmail API. Classifies, summarizes, posts to Paperclip. After a week of Chris validating classifications, the soul file has been rewritten based on actual error patterns.

The Slack bridge polls Paperclip and posts Block Kit messages. Approve in Slack → bridge updates Paperclip. Link in message → opens dashboard for deeper review.

Graduated routines show in Paperclip as registered agents with budgets and run history.

**The experience:** Morning: Slack shows email triage — scan, approve classifications, handle 3-5 items. Monday: P&L in Slack — tap link, review in dashboard, approve. Evening: daily summary arrives. 30-45 minutes/day replaces 2-3 hours.

### After Phase 2

TS operational suite is comprehensive. CS drafts flow through Intercom → triage → draft → Paperclip → Slack → back to Intercom. Inventory alerts surface POs for review. Campaign briefs generate bi-weekly. Product descriptions run evaluator-optimizer loops.

Langfuse traces every LLM call with cost and latency data.

**The experience:** TS operations largely automated with human oversight. Phone-based approvals during the day. Structured handoffs to Jothi.

### After Phase 3

Personal agents operational. Fitness Coach posts daily workouts and weekly reviews. Research Analyst runs on-demand tasks and Friday digests. Cross-company patterns established. Subagent evaluator scores highest-value routines and alerts on degradation.

### After Phase 4

PDF deck tells the builder story. Portfolio website is live with project deep-dives and contact form. Positions for both employment and advisory conversations.

### After Phase 5

Skills at production quality. Autoresearch improving descriptions overnight. Financial Controller generating weekly snapshots. Content pipeline scoped for dharma teaching material.

---

## Part 2: Future Sprint Ideas

### Centralized Cross-System File Index

A script that scans brain/, Documents/, Google Drive, and code/ to maintain a searchable index (filename, path, location, type, modified date). Query via Claude Code skill. **Consider after Phase 2.**

### Obsidian AI-Assisted Weekly Review

Sunday evening agent scans vault: unprocessed inbox items, stale projects, archival candidates. Generates structured review document for Board approval. **Consider after Phase 0B when vault has enough content.**

### Multi-Language Agent Communication

Extend org resolver with language preferences. Translation step in notifications to non-English team members (Jothi: formal Bahasa, Fiona: Mandarin, Omar: Spanish). **Consider in Phase 2 when routines route to team members.**

### Claude Code Agent Teams for Parallel Development

Use experimental `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` for 3-5 parallel instances sharing a task list. Could accelerate Phase 2 significantly. **Consider after Phase 1 when multiple independent routines exist.**

### Automated Prompt Optimization (Autoresearch)

Full Karpathy loop: define metrics → run → score → analyze failures → improve prompt → repeat. Nightly Promptfoo runs, threshold-triggered optimization cycles. **Consider Phase 5+ with 90+ days of scoring data.**

### WhatsApp for Supplier Communications

Twilio WhatsApp Business API for template-based supplier messages (PO confirmations, shipping updates). NOT conversational. **Consider only if volume justifies; manual WhatsApp may suffice indefinitely.**

### Dharma Video Transcription Pipeline

Whisper on ROK-BOX GPU for 875+ YouTube videos. Custom Drikung Kagyu terminology glossary. LLM post-processing. Supabase + pgvector for semantic search. **Phase 5+ as standalone project.**

### Compliance Automation (CCPA ADMT + EU AI Act)

Audit all automated routines for compliance. Implement disclosures, opt-out mechanisms. Build compliance checklist skill. **BEFORE any automated customer-facing communications (Phase 2 prerequisite).**

### New Venture Scoping

When a new venture becomes active, create a Paperclip company shell with mission statement and import the relevant repo-example as a starting template. No pre-planning needed — the architecture supports any number of companies.

---

## Part 3: Readiness Checklist

Before executing Phase 0A, confirm you can answer:

- [ ] I understand the three-machine architecture and what runs where
- [ ] I understand where each type of content lives (brain vs Documents vs Google Drive vs code)
- [ ] I understand the Paperclip terminology (routine vs task, agent vs routine, skill vs hook)
- [ ] I understand what Claude Code loads natively (CLAUDE.md, skills, hooks) vs what Paperclip adds
- [ ] I understand the values cascade (constitution → company → agent → skill)
- [ ] I understand the HITL flow (routine → Paperclip ticket → Slack bridge → approve → back to Paperclip)
- [ ] I understand graduation (standalone script → 7 days → eval passes → register as Paperclip agent)
- [ ] I understand why CLAUDE.md must be lean (Claude ignores content it deems irrelevant)
- [ ] I understand the teaching checkpoint pattern (explain → STOP → build → review → document)
