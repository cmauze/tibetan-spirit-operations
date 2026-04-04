# Phase 1 — First Atoms

**Note:** This is a detailed phase card for Phase 1. Phase 1A covers the Tibetan Spirit foundation, heartbeat_runner, Slack bridge, and first routines. Phase 1B covers the email automation system that replaces Shortwave AI filters + Tasklet. Both follow the same specification-first, eval-driven, atoms-before-molecules methodology.

**Depends on:** Phase 0B complete (guides written, vault consolidated, system wiki exists)
**Delivers:** First working routines (Daily Order Summary, Weekly P&L), Slack bridge, heartbeat_runner pattern, email automation pipeline, first agent graduation

---

## Session Prompts

### Phase 1A — TS Foundation + Slack Bridge

> Copy-paste to start a new Claude Code session.

```
Read these files:
1. workspace/plans/REQ-1b/04-phase-1-first-atoms.md (this file — Phase 1A section)
2. workspace/plans/REQ-1b/01-master-spec.md (architecture spec)
3. All guides in code/docs/guides/
4. All specs in code/docs/specs/
5. The system wiki at brain/3-Resources/system-wiki/ (current system state)
6. The EXISTING TS codebase at ~/code/active/tibetan-spirit-ops/ — check
   what's reusable (agents/soul.md files, Supabase schema, scripts, lib/)
   before building anything fresh

Phase 1A builds the first working routines and agents. Before writing
any code, generate a DETAILED implementation task card — like the
Phase 0A card but for Phase 1A. Use the Phase 1A section of this file
as scope, the master spec as architecture authority, and the guides/specs
as pattern references.

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

BUILD THIS WRAPPER EXPLICITLY in Phase 1A. Do not let Paperclip's
claude_local adapter handle it opaquely. I want to see and understand
every line of the integration layer.

Show me the heartbeat_runner.py architecture (what it does, how it
calls routine scripts, how it reports back) BEFORE building any
routines. This is the most important piece to get right because
everything else depends on it.

PAPERCLIP FALLBACK PATH:

If Paperclip isn't ready, stable, or proves problematic — routines
still need to run. Build a cron_runner.py alongside heartbeat_runner.py
that does the same context assembly but is triggered by PM2 cron instead
of Paperclip heartbeats. Same routine scripts, different trigger
mechanism. Test BOTH paths.

EXISTING CODEBASE CHECK:

Before building anything, inventory what already exists in
~/code/active/tibetan-spirit-ops/. Check for:
- agents/ directory with soul files — reusable or needs rewrite?
- Supabase schema or migrations — what tables exist? Do they match the
  three-layer model (registry, runtime, eval) from the DEV-PLAN?
- lib/ or scripts/ — any shared utilities worth keeping?
- Skills or SKILL.md files — still valid?

Present the inventory and your reuse/rebuild recommendations before
starting fresh.

ADDITIONAL REQUIREMENTS:
- Agent-centric directory layout per specs/agents-spec.md
- Write Promptfoo eval YAML BEFORE routine scripts (eval-driven)
- Follow composable patterns from guides/routine-developer/composable-patterns.md
- Use Paperclip terminology consistently (routines, tasks, agents,
  heartbeats, skills — never "workflows")
- Present the task card for my review before executing anything

Generate the task card first. Do not start building until I approve.
```

**Watch for:** The agent skipping the heartbeat_runner wrapper and letting Paperclip's adapter handle invocation opaquely. The agent importing Paperclip modules inside routine scripts (coupling violation). The agent trying to register agents before 7-day graduation. Existing Supabase schema from the DEV-PLAN may need reconciliation — agent should check what exists before creating migrations. Agent defaulting to "workflow" instead of "routine." Agent ignoring the existing codebase and building everything from scratch.

---

### Phase 1B — Email Automation (Shortwave Replacement)

> Copy-paste to start after Phase 1A is running.

```
Read these files:
1. workspace/plans/REQ-1b/04-phase-1-first-atoms.md (this file — Phase 1B section)
2. workspace/plans/REQ-1b/01-master-spec.md (architecture spec)
3. workspace/plans/REQ-1b/attachments/email - shortwave-tasklet style automation plan.md
   (full research on Gmail API, classification, open-source landscape)
4. All guides in code/docs/guides/
5. The heartbeat_runner.py and cron_runner.py from Phase 1A (reuse the pattern)
6. code/active/chris-os/ (this is a chris-os capability, NOT tibetan-spirit)

Phase 1B builds a custom email automation system that replaces
Shortwave AI filters ($36/mo) + Tasklet ($35-100/mo) with a
Claude-powered classification pipeline at ~$5-10/mo.

IMPORTANT CONTEXT:
- This is a chris-os routine/agent (Chief of Staff's primary capability),
  NOT a Tibetan Spirit routine
- It uses the same heartbeat_runner pattern established in Phase 1A
- Shortwave remains the reading UI — we only apply Gmail labels, which
  sync bidirectionally to Shortwave
- Shortwave has no API — all automation goes through Gmail API

Before writing any code, generate a DETAILED implementation task card.
Follow the atoms-before-molecules sequence from the research doc:

Atom 1 — Gmail Auth + Label Bootstrap
Atom 2 — Email Fetcher (poll-based, SQLite state tracking)
Atom 3 — Rules Engine (deterministic routing from YAML config)
Atom 4 — Claude Classification (Haiku default, Sonnet fallback)
Atom 5 — Label Applicator (batchModify, retry logic)
Molecule 1 — Processing Pipeline (chains Atoms 2-5)
Molecule 2 — Trigger Registry (YAML rules with approval gates)
Molecule 3 — Monitoring + Feedback (logging, daily summary, corrections)

SPECIFICATION-FIRST APPROACH:
Write README.md and docs/ BEFORE any src/ code. The documentation IS
the specification. Include:
- CLAUDE.md (<100 lines: stack, structure, commands, key pointers)
- docs/SPEC.md (detailed PRD with acceptance criteria)
- docs/ARCHITECTURE.md (system design with Mermaid diagrams)
- docs/CLASSIFICATION.md (label taxonomy, prompt templates, routing)
- config/labels.yaml (label taxonomy definition)
- config/rules.yaml (deterministic routing rules)

KEY ARCHITECTURAL DECISIONS (already made):
- Polling, not push (simplicity over latency — personal inbox, not enterprise)
- SQLite for state tracking (processed message IDs, classification history)
- Tiered classification: rules engine (free) → Haiku ($0.001/email) →
  Sonnet ($0.004/email) → human review label
- Prompt caching for the system prompt (90% cost reduction on cache hits)
- Structured outputs with JSON schema (enum constraints on label names)
- Two-pass hierarchical taxonomy: Pass 1 = ~10 core labels (every email),
  Pass 2 = project-specific labels (actionable emails only)

GRADUATION PATH:
- Standalone script first, triggered by PM2 cron via cron_runner.py
- 7 consecutive days of reliable operation on real email
- Promptfoo eval suite must pass (classification accuracy >85%)
- Then register as Chief of Staff capability via heartbeat_runner
- Chris validates every classification for the first week

BUDGET TARGET:
- Haiku classification at ~$0.001/email
- Rules engine handles 40-60% of email for free
- Total: ~$3-10/month for 50-200 emails/day
- Compare: Shortwave Premier $36/mo + Tasklet $35-100/mo = $71-136/mo

ADDITIONAL REQUIREMENTS:
- Use Paperclip terminology consistently
- Eval-driven: write Promptfoo eval YAML before classification code
- Include dry-run/preview mode for building trust
- Include the flywheel effect: track sender classification history,
  migrate confirmed classifications from LLM to rules engine over time
- Present the task card for my review before executing anything

Generate the task card first. Do not start building until I approve.
```

**Watch for:** Agent building inside tibetan-spirit instead of chris-os. Agent skipping the specification-first step and jumping to code. Agent using push notifications instead of polling (unnecessary complexity). Agent trying to build Shortwave integration (Shortwave has no API — we only touch Gmail). Agent not reusing the heartbeat_runner/cron_runner pattern from Phase 1A.

---

## Phase 1A — Tibetan Spirit Foundation + Infrastructure

### Overview

Create the TS project structure, shared Python library, heartbeat_runner integration layer, Slack bridge, first two routines, and first agent. Everything follows the agent-centric layout from `specs/agents-spec.md`.

### heartbeat_runner.py Architecture

This is the most critical piece in Phase 1. Everything else depends on it.

```
                    ┌─────────────────┐
                    │   Paperclip     │
                    │   Heartbeat     │
                    │   Trigger       │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ heartbeat_      │     ┌─────────────────┐
                    │ runner.py       │     │  cron_runner.py  │
                    │                 │     │  (PM2 fallback)  │
                    │ 1. Read task    │     │                  │
                    │    from API     │     │ 1. Read config   │
                    │ 2. Load soul +  │     │ 2. Load soul +   │
                    │    skills       │     │    skills         │
                    │ 3. Assemble     │     │ 3. Assemble      │
                    │    context      │     │    context        │
                    │ 4. Call routine │     │ 4. Call routine   │
                    │ 5. Capture JSON │     │ 5. Capture JSON   │
                    │ 6. Report to    │     │ 6. Write to       │
                    │    Paperclip    │     │    output/         │
                    │ 7. Log cost     │     │ 7. Log cost        │
                    │ 8. Ping health  │     │ 8. Ping health     │
                    │    checks       │     │    checks          │
                    └────────┬────────┘     └────────┬──────────┘
                             │                       │
                    ┌────────▼───────────────────────▼─┐
                    │     Routine Script               │
                    │     (e.g., daily_summary/run.py)  │
                    │                                   │
                    │  - Takes inputs as args/stdin     │
                    │  - Queries Supabase               │
                    │  - Calls Anthropic API            │
                    │  - Loads skills from filesystem   │
                    │  - Returns Pydantic JSON          │
                    │  - ZERO Paperclip imports         │
                    └───────────────────────────────────┘
```

**The key insight:** heartbeat_runner.py and cron_runner.py are interchangeable wrappers. The routine script is the same either way. If Paperclip disappears, you swap the 20-line wrapper, not the 200-line routine.

**Build heartbeat_runner.py and cron_runner.py FIRST**, before any routine. Verify both can invoke a trivial test routine (echo input → structured JSON output) before building real routines.

### Paperclip Fallback Path

If Paperclip is not ready, unstable, or proves problematic:

1. **cron_runner.py** replaces heartbeat_runner.py as the trigger mechanism
2. PM2 manages the cron schedule (already a server dependency)
3. Routine output writes to `output/` directory as JSON files
4. A separate PM2-triggered Slack notifier posts results as Block Kit messages
5. Slack button approvals trigger a webhook that processes downstream actions
6. Budget tracking falls back to local cost_tracker.py logs

Same routines, same evals, same graduation process. Different plumbing.

### Existing Codebase Inventory

Before building anything in Phase 1A, check what already exists at `~/code/active/tibetan-spirit-ops/`:

- **agents/ directory** — Are there soul files? Are they still valid for the current architecture?
- **Supabase schema** — Do migrations or schema files exist? Do they match the three-layer model (registry, runtime, eval) from the DEV-PLAN? Reconcile before creating new migrations.
- **lib/ or scripts/** — Any shared utilities (claude_client, notifications, cost tracking) that can be extended rather than rebuilt?
- **Skills or SKILL.md files** — Still aligned with the Agent Skills standard?
- **workspace/ or docs/** — Any specs, plans, or research that inform implementation?

Present the full inventory with reuse/rebuild recommendations at the first checkpoint.

### Shared Python Library

Build the shared library in `lib/`:

- **claude_client.py** — Skill loading from filesystem, prompt caching, cost calculation per invocation, model routing (Haiku/Sonnet/Opus)
- **org.py** — Role resolution from ORG.md, company context loading
- **notifications.py** — Slack message formatting (Block Kit), channel routing by company and priority
- **cost_tracker.py** — Invocation logging to Supabase (model, tokens, cost, routine name, timestamp)

### Supabase Schema

Expand the schema with the three-layer model (minus dashboard-specific tables since Paperclip's dashboard replaces the custom PWA):

- **Registry layer:** agents, routines, skills, companies (definitions and configurations)
- **Runtime layer:** invocations, costs, outputs, approvals (operational state)
- **Eval layer:** eval_runs, eval_scores, graduation_status (quality tracking)

Check what exists in Supabase before creating migrations. Reconcile conflicts.

### First Two Routines

Build as standalone scripts first. Graduate into Paperclip agents after 7 days.

**Daily Order Summary**
- Model: Haiku (cost-efficient for structured data extraction)
- Schedule: 6pm Denver daily
- Auto-logged, no approval required
- Queries Supabase for day's orders, formats summary, posts to Slack

**Weekly P&L**
- Model: Sonnet (needs deeper reasoning for financial analysis)
- Schedule: Monday 6am Denver
- Board approval required before distribution
- Queries Supabase for weekly financials, generates analysis, routes to Board

Each routine:
1. Write Promptfoo eval YAML first (defines "good output")
2. Build the routine script (produces the output)
3. Test standalone: `python routines/daily_summary/run.py --date 2026-04-01`
4. Test via cron_runner: `python cron_runner.py --routine daily_summary --date 2026-04-01`
5. Test via heartbeat_runner (if Paperclip is ready)
6. Run for 7 consecutive days on real data
7. Graduate if all evals pass and override rate is acceptable

### chris-os Chief of Staff (Initial)

Build the first personal agent: email triage via Gmail API. (Note: the full email automation system is Phase 1B. Phase 1A establishes the basic triage capability.)

- Classifies emails: Action Required, FYI, Delegate, Archive
- Drafts one-line summaries for Action Required items
- Posts batches to Paperclip (or Slack if no Paperclip)
- Runs 3x daily via heartbeat
- First week: Chris validates every classification
- Rewrite the soul file based on observed error patterns after the first week

### Slack Bridge

Build the Slack Bolt Python bridge connecting Paperclip's ticket system to Slack channels.

- Polls Paperclip API every 30 seconds
- Formats tickets as Block Kit messages with approve/reject buttons
- Routes to channels by company and priority
- Handles button-click approvals back to Paperclip
- Deploy on server via PM2

**Fallback:** If Paperclip is not available, the bridge reads from the `output/` directory instead of the Paperclip API. Same Slack UX, different data source.

### Community Skill Sourcing

Search skill marketplaces (SkillsMP, SkillHub, Anthropic official) for infrastructure/utility skills. Evaluate against quality criteria from `specs/skills-spec.md`. Fork and adapt top 5-10. Write custom skills for business-specific needs (brand-guidelines, product-knowledge, escalation-matrix).

### Graduation Checklist

After 7 days of reliable operation, each routine must pass:

- [ ] Ran successfully for 7 consecutive days on real data
- [ ] Promptfoo eval suite passes consistently
- [ ] Override rate is acceptable (Tier 3: human reviews every output)
- [ ] Cost per invocation is within budget
- [ ] Standalone execution works: `python routines/{name}/run.py`
- [ ] cron_runner execution works: `python cron_runner.py --routine {name}`
- [ ] heartbeat_runner execution works (if Paperclip available)
- [ ] Soul file written based on observed behavior patterns
- [ ] Skills loaded correctly from filesystem
- [ ] Output format matches Pydantic model specification

On graduation: register as Paperclip agent with soul file, heartbeat schedule, and budget cap. Appears in dashboard with run history and budget utilization.

### Agent Teams Consideration

Independent routines (Daily Order Summary, Weekly P&L) could theoretically be developed in parallel by separate Agent Teams teammates. However:

- Only parallelize AFTER the shared library and heartbeat_runner are established by the lead
- Each teammate would own one routine's directory completely (no file overlap)
- The lead must review and approve the heartbeat_runner integration for each routine
- Practical recommendation: build sequentially for Phase 1A (only 2 routines), consider parallelization in Phase 2 when there are 5+ independent routines

---

## Phase 1B — Email Automation System

### Context

Replaces Shortwave AI filters ($36/mo on Premier tier, limited to 10 filters) and Tasklet ($35-100/mo, non-deterministic, redundant with Claude Code) with a custom email classification pipeline at ~$5-10/mo. This is a **chris-os** capability — the Chief of Staff agent's primary function — not a Tibetan Spirit routine.

Shortwave remains the email reading UI. The system applies Gmail labels via the API, which sync bidirectionally to Shortwave instantly. Shortwave has no public API, so all automation goes through Gmail.

### Specification-First Methodology

Follow README-Driven Development. Write all documentation before any code.

**Project structure:**

```
code/active/chris-os/routines/email-automation/
├── README.md                    # Vision, features, architecture, quick start
├── CLAUDE.md                    # <100 lines: stack, structure, commands
├── docs/
│   ├── SPEC.md                  # Detailed PRD with acceptance criteria
│   ├── ARCHITECTURE.md          # System design with Mermaid diagrams
│   ├── CLASSIFICATION.md        # Label taxonomy, prompt templates, routing
│   ├── GMAIL-API.md             # API integration: auth, rate limits, patterns
│   ├── TRIGGERS.md              # Trigger registry format, approval gates
│   ├── DEPLOYMENT.md            # PM2 setup, server config, monitoring
│   └── adr/                     # Architecture Decision Records
│       ├── 001-use-haiku-for-classification.md
│       ├── 002-polling-vs-push-notifications.md
│       └── 003-sqlite-for-state-tracking.md
├── src/                         # Implementation (after docs are approved)
├── tests/                       # Pytest suite
├── evals/                       # Promptfoo YAML + test fixtures
└── config/
    ├── labels.yaml              # Label taxonomy definition
    ├── rules.yaml               # Deterministic routing rules
    └── prompts/                 # Classification prompt templates
```

### Key Architectural Decisions

These are already decided based on the research. Document as ADRs:

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Notification model | Polling (not push) | Personal inbox, sub-second latency unnecessary. Polling via `history.list` (2 quota units/call) every 1-5 minutes is simpler than Pub/Sub setup, watch renewal every 7 days, and Cloud project dependency. |
| State tracking | SQLite | Processed message IDs, classification history, sender profiles. Local, zero-dependency, perfect for single-user system. |
| Classification tier 1 | Rules engine (free) | Header checks (`List-Unsubscribe` -> newsletter), domain patterns (`@github.com` -> dev notifications), known sender maps. Handles 40-60% of email without any API call. |
| Classification tier 2 | Haiku 4.5 (~$0.001/email) | Near-frontier accuracy for classification. Cached system prompt reduces cost by 90% on hits. Structured output with JSON schema + enum constraints. |
| Classification tier 3 | Sonnet 4.5 (~$0.004/email) | Re-classification with chain-of-thought for low-confidence cases (<0.7-0.85 threshold) and VIP senders. ~5% of remaining emails. |
| Classification tier 4 | Human review | Dedicated "Needs Review" Gmail label for cases where even Sonnet is uncertain. |
| Label taxonomy | Two-pass hierarchical | Pass 1: ~10 core labels (every email). Pass 2: project-specific labels (actionable emails only). Reduces label space per call, improves accuracy. |
| Reading UI | Shortwave (unchanged) | Bidirectional Gmail label sync means every label we apply appears in Shortwave instantly. No Shortwave API needed. |

### Implementation Sequence (Atoms Before Molecules)

**Atom 1 — Gmail Auth + Label Bootstrap**
- OAuth2 flow with persistent refresh token storage
- CRITICAL: Publish app to production status (testing tokens expire in 7 days)
- Label CRUD operations
- Script reads `config/labels.yaml`, ensures all labels exist in Gmail with correct colors and nesting
- Verification: labels appear correctly in Shortwave

**Atom 2 — Email Fetcher**
- Poll-based fetcher using `messages.list` with configurable query parameters
- `history.list` for incremental sync (2 quota units per call)
- SQLite database tracks processed message IDs with timestamps
- Configurable polling interval (default: every 2 minutes)
- Verification: fetches new unread emails since last run, never re-processes

**Atom 3 — Rules Engine**
- Deterministic routing from `config/rules.yaml`
- Sender patterns, domain maps, header checks (`List-Unsubscribe`)
- Returns label assignments or "needs LLM classification"
- Verification: correctly labels newsletters, known-sender emails, automated notifications without any API calls

**Atom 4 — Claude Classification**
- Cached system prompt: classifier persona + category definitions + distinguishing criteria + 2-5 few-shot examples for commonly confused categories
- User message: only the email to classify
- Structured output with JSON schema: `primary_label` (enum), `confidence` (0.0-1.0), `priority` (urgent/normal/low), optional `project_labels` array, `reasoning` string
- Haiku 4.5 default, Sonnet fallback for low-confidence results
- Prompt caching: ~1,000-token system prompt, 80%+ cache hit rate expected
- Verification: classifies test emails into correct labels with >85% accuracy

**Atom 5 — Label Applicator**
- Takes classification results, applies Gmail labels via `batchModify`
- Batch chunking (max 1,000 message IDs per call)
- Retry logic with exponential backoff
- Idempotent state updates in SQLite
- Verification: labels appear in Gmail and sync to Shortwave

**Molecule 1 — Processing Pipeline**
- Chains Atoms 2-5 into a single processing run
- Scheduler trigger: PM2 cron via cron_runner.py (same pattern as Phase 1A)
- Fetch → rules engine → Claude (if needed) → apply labels → update state
- End-to-end processing with dry-run mode for building trust
- Verification: end-to-end processing of new emails with correct labeling

**Molecule 2 — Trigger Registry**
- YAML/Markdown document defining all active automation rules
- New rules proposed by Claude require explicit user approval before activation
- Change history tracked in Git
- Verification: adding a new rule results in correct behavior on next processing cycle

**Molecule 3 — Monitoring + Feedback**
- Classification logging: every decision with reasoning, stored in SQLite
- Daily summary report: emails processed, rule vs. LLM ratio, confidence distribution, cost
- Misclassification correction: moving an email to a different label triggers a feedback event
- Prompt refinement based on accumulated corrections
- The flywheel: track sender classification history, migrate confirmed senders from LLM to rules engine over time (system gets cheaper and faster)

### Graduation Path

1. **Standalone script** — triggered by PM2 cron via cron_runner.py
2. **7 consecutive days** of reliable operation on real email
3. **Promptfoo eval suite** passes (classification accuracy >85%)
4. **Chris validates every classification** for the first week
5. **Soul file rewrite** based on observed error patterns
6. **Register as Chief of Staff capability** via heartbeat_runner
7. **Progressive trust:** Tier 3 (review every output) → Tier 2 (review exceptions) → Tier 1 (auto-execute, weekly digest)

### Cost Budget

| Component | Unit Cost | Monthly Estimate (100 emails/day) |
|-----------|-----------|-----------------------------------|
| Rules engine (40-60% of email) | Free | $0 |
| Haiku classification (remaining) | ~$0.001/email | $1.50-3.00 |
| Sonnet escalation (~5% of LLM calls) | ~$0.004/email | $0.30-0.60 |
| Prompt caching savings | -90% on hits | Net: ~$0.50-1.00 saved |
| **Total** | | **~$3-5/month** |

Compare: Shortwave Premier $36/mo + Tasklet $35-100/mo = **$71-136/mo**

### Integration with Phase 1A

- Reuses heartbeat_runner.py and cron_runner.py from Phase 1A
- Reuses shared library: claude_client.py (for Haiku/Sonnet calls), cost_tracker.py (for budget logging), notifications.py (for Slack alerts)
- Lives in `code/active/chris-os/routines/email-automation/` — NOT in tibetan-spirit
- Chief of Staff email triage (Phase 1A basic version) evolves into the full pipeline here
- Same graduation process: standalone → 7 days → eval passes → register

---

## Verification & Testing

### Phase 1A Verification Checklist

- [ ] **heartbeat_runner.py** invokes a trivial test routine and reports structured JSON
- [ ] **cron_runner.py** invokes the same test routine identically
- [ ] **Shared library** imports resolve: claude_client, org, notifications, cost_tracker
- [ ] **Supabase schema** deployed: registry, runtime, eval layers
- [ ] **Daily Order Summary** runs standalone: `python routines/daily_summary/run.py --date 2026-04-01`
- [ ] **Daily Order Summary** Promptfoo eval passes
- [ ] **Weekly P&L** runs standalone: `python routines/weekly_pnl/run.py --week 2026-W14`
- [ ] **Weekly P&L** Promptfoo eval passes
- [ ] **Slack bridge** polls and formats tickets as Block Kit messages
- [ ] **Slack bridge** handles button-click approvals back to Paperclip (or writes approval to output/)
- [ ] **Chief of Staff** classifies test emails correctly
- [ ] **7-day graduation** checklist passed for each routine
- [ ] **All routine scripts** have zero Paperclip imports
- [ ] **Cost tracking** logs every invocation to Supabase

### Phase 1B Verification Checklist

- [ ] **Gmail OAuth2** token persists and auto-refreshes (production status, not testing)
- [ ] **Label bootstrap** creates all labels from `config/labels.yaml` in Gmail
- [ ] **Labels** appear correctly in Shortwave with proper nesting
- [ ] **Email fetcher** retrieves new emails since last run, never re-processes
- [ ] **SQLite state** tracks processed message IDs correctly
- [ ] **Rules engine** classifies known patterns without API calls
- [ ] **Haiku classification** returns valid structured JSON with enum-constrained labels
- [ ] **Sonnet fallback** triggers for low-confidence results
- [ ] **Label applicator** applies labels via batchModify, labels visible in Shortwave
- [ ] **Dry-run mode** shows proposed labels without applying them
- [ ] **Promptfoo eval** passes with >85% classification accuracy
- [ ] **End-to-end pipeline** processes new emails correctly when triggered by PM2 cron
- [ ] **Daily summary report** shows processing stats, costs, confidence distribution
- [ ] **7-day graduation** passed on real email
- [ ] **Cost per day** is within $0.10-0.30 budget
- [ ] **Flywheel** track in SQLite shows sender classification history accumulating
