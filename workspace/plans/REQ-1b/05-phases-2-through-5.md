# Phases 2-5 — Scope Outlines

## Important Note

These are scope outlines, not full task cards. Detailed implementation prompts for each phase should be generated AFTER the prior phase completes, because each phase builds on patterns and infrastructure established by its predecessor. Generate each phase's detailed card only when the prior phase is complete.

---

## Session Prompts

### Phase 2 — TS Operations Core

> Copy-paste to start a new Claude Code session after Phase 1 is complete.

```
Read:
1. workspace/plans/REQ-1b/05-phases-2-through-5.md (Phase 2 scope)
2. workspace/plans/REQ-1b/01-master-spec.md (architecture spec)
3. All guides and specs in code/docs/
4. code/active/tibetan-spirit-ops/ (existing from Phase 1)
5. brain/3-Resources/system-wiki/ (current system documentation)

Generate a detailed Phase 2 task card. Phase 2 adds: CS email drafts
(Intercom), inventory alerts (Shopify sync), campaign briefs, product
descriptions (evaluator-optimizer), customer profiles, Langfuse, and
reliability pass.

Before generating: review what exists in TS from Phase 1. New routines
build on the shared library, heartbeat_runner pattern, and eval
patterns established there.

AGENT TEAMS FOR PARALLEL ROUTINES:

Phase 2 has 5 independent routines (CS Email Drafts, Inventory Alerts,
Campaign Brief Generator, Product Description Optimizer, Customer
Profiles). After the shared library extensions are complete, consider
using Agent Teams to develop independent routines in parallel:
- Each teammate owns one routine's directory completely
- No file overlap between teammates
- Lead reviews heartbeat_runner integration for each routine
- 5-6 tasks per teammate, clear file ownership
- Run lead on Opus for planning, teammates on Sonnet for execution

Only parallelize after confirming the shared library and Supabase
schema extensions are stable. Sequential is safer if unsure.

NOTION MCP INTEGRATION:

Some routines (Campaign Briefs, Product Descriptions) may benefit from
reading Notion content — TS brand guidelines, product catalogs, and
SOPs live in the Notion workspace. Consider adding Notion MCP as a
data source for routines that need team-facing operational content.
This is additive, not required — Supabase + Git are the primary
data sources.

CRITICAL: Include a compliance checkpoint before any automated
customer-facing communications go live (CCPA ADMT). Also include
a step to update the system wiki with the new routines and agents.

Generate task card for review. Do not build until approved.
```

**Watch for:** Agent skipping the compliance checkpoint for customer-facing communications. Agent not reusing the heartbeat_runner pattern from Phase 1. Agent creating new shared utilities instead of extending the existing lib/. Agent defaulting to "workflow" instead of "routine." Agent Teams teammates touching shared library files (race condition risk — those must be completed by the lead first).

---

### Phase 3 — Personal Agents

> Copy-paste to start a new Claude Code session after Phase 2 is complete.

```
Read:
1. workspace/plans/REQ-1b/05-phases-2-through-5.md (Phase 3 scope)
2. workspace/plans/REQ-1b/01-master-spec.md (architecture spec)
3. All guides and specs
4. code/active/chris-os/ (infrastructure + Chief of Staff from Phase 1)

Generate a detailed Phase 3 task card. Adds: Fitness Coach, Research
Analyst, cross-company patterns. Chief of Staff already running —
these follow the same graduation pattern and heartbeat_runner
integration.

IMPORTANT — CHIEF OF STAFF EMAIL TRIAGE:

The Chief of Staff's email triage capability is already running from
Phase 1B. The full email automation pipeline (Gmail Auth, fetcher,
rules engine, Claude classification, label applicator) is operational.
Phase 3 does NOT rebuild email triage — it extends the Chief of Staff
with additional capabilities and builds new agents that follow the
same pattern.

SUBAGENT EVALUATOR:

Deploy for highest-value routines. The evaluator pattern:
- Haiku scores routine outputs against rubrics defined in SKILL.md files
- Scores log to Supabase eval layer (eval_runs, eval_scores tables)
- Weekly aggregation alerts on degradation (score trending down)
- Rubric dimensions: accuracy, completeness, tone, actionability
- Custom rubric per routine type (financial analysis rubric differs
  from email classification rubric)
- The evaluator is itself a routine with its own eval suite (meta!)

Use the subagent pattern from .claude/agents/ — define a reviewer.md
or evaluator.md subagent that runs in a separate context window.
Haiku model for cost efficiency. Read-only tools only (Read, Grep,
Glob). Reports back scores and flagged issues.

The Fitness Coach needs to understand my training philosophy (science-
based, periodized, three modalities: strength, running, mobility).
The Research Analyst serves ALL ventures. Cross-company patterns
define how chris-os agents support tibetan-spirit.

Include a step to update the system wiki with new agents and patterns.

Generate task card for review. Do not build until approved.
```

**Watch for:** Agent rebuilding email triage instead of extending the existing Chief of Staff from Phase 1B. Agent creating the subagent evaluator without its own eval suite (the evaluator must evaluate itself). Agent not defining clear cross-company boundaries (chris-os agents serve TS operations through the Board, not through direct coupling). Agent defaulting to "workflow" instead of "routine."

---

### Phase 4 — Portfolio and Positioning

> Copy-paste to start a new Claude Code session. Can overlap with Phases 2-3.

```
Read:
1. workspace/plans/REQ-1b/05-phases-2-through-5.md (Phase 4 scope)
2. workspace/plans/REQ-1b/01-master-spec.md (architecture spec)

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

## Phase 2 — Tibetan Spirit Operations Core

**Depends on:** Phase 1 complete (routines running, Slack bridge operational)
**Delivers:** Complete TS operational routine suite

### CS Email Drafts

Three-step chain — Haiku triage -> Supabase customer enrichment -> Sonnet draft. Intercom integration for ingestion and reply. Every draft requires Board approval before sending.

### Inventory Alerts

Shopify API sync to Supabase. Compare against reorder thresholds. Sonnet generates priority-sorted alerts with suggested POs. Routes to operations-manager.

### Campaign Brief Generator

Top products by revenue + seasonal context + inventory data -> campaign theme, target segment, subject lines, product selection. Board approval.

**Notion MCP integration note:** Campaign briefs may benefit from reading TS brand guidelines and product catalogs from Notion. The Notion workspace at `Chris's Brain` and `Tibetan Spirit` shared drive contain team-facing brand documentation. Consider adding Notion MCP as an optional data source for this routine. This is additive — the routine must work without Notion access, using Git-based brand-guidelines skill as the primary source.

### Product Description Optimizer

Evaluator-optimizer loop: Sonnet generates -> Haiku evaluates against rubric (SEO, brand voice, accuracy, cultural sensitivity) -> regenerate if below threshold -> max 3 iterations.

### Customer Profiles

RFM scoring from order history. Heuristic segmentation. Enriches CS drafts and campaign targeting.

### Langfuse Deployment

Self-host via Docker on server. Wrap Agent SDK calls with `@observe()`. Cost tracking, latency monitoring, prompt versioning.

### Reliability Pass

All imports resolve, all Supabase queries valid, all eval suites pass.

### Compliance Check

Audit routines for CCPA ADMT before any automated customer-facing communications go live. This is a hard gate — nothing customer-facing publishes without Board review AND compliance verification.

### Agent Teams for Parallel Routine Development

Phase 2 has 5 independent routines that can be developed in parallel once the shared infrastructure is stable:

| Routine | Owner (Teammate) | Directory | Dependencies |
|---------|-------------------|-----------|--------------|
| CS Email Drafts | teammate-1 | routines/cs_email_drafts/ | Intercom API, shared lib |
| Inventory Alerts | teammate-2 | routines/inventory_alerts/ | Shopify API, shared lib |
| Campaign Briefs | teammate-3 | routines/campaign_briefs/ | shared lib, brand-guidelines skill |
| Product Descriptions | teammate-4 | routines/product_descriptions/ | shared lib, eval rubrics |
| Customer Profiles | teammate-5 | routines/customer_profiles/ | Supabase, shared lib |

**Prerequisite for parallelization:** The lead must complete shared library extensions (Intercom client, Shopify client, any new Supabase tables) before spawning teammates. Teammates only touch their own routine directory — never shared library files.

**Recommended approach:** Lead completes shared infrastructure (Langfuse, API clients, schema extensions), then spawns 3-5 teammates for parallel routine development, then lead handles the reliability pass and compliance check after all routines are complete.

---

## Phase 3 — Personal Agents

**Depends on:** Phase 2 complete
**Delivers:** Personal agents, cross-company patterns, subagent evaluator

### Fitness Coach Agent

Daily workout posts matching Chris's training template. Progressive overload calculations. Weekly programming reviews. Periodization and deload management.

Training philosophy: science-based, periodized, three modalities (strength, running, mobility). The soul file must encode these principles, not just exercise lists.

### Research Analyst Agent

On-demand tasks assigned through Paperclip. Multi-source synthesis with confidence levels. Friday digest of developments relevant to Chris's portfolio.

Serves ALL ventures — not scoped to a single company. Cross-company routing through the Board.

### Cross-Company Patterns

Define how agents in chris-os serve TS operations:
- Chief of Staff routes TS emails (already running from Phase 1B)
- Research Analyst does TS competitive research
- The Board is the bridge between companies
- chris-os agents never have direct Paperclip imports for tibetan-spirit — they route through the Board's approval/assignment mechanism

### Subagent Evaluator

Deploy for highest-value routines. Pattern:

1. **Define rubrics** per routine type in SKILL.md files
   - Financial analysis rubric: accuracy, completeness, insight quality, actionability
   - Email classification rubric: label accuracy, confidence calibration, reasoning quality
   - Content generation rubric: brand voice, SEO, cultural sensitivity, factual accuracy
2. **Haiku scores** routine outputs against rubrics
   - Runs as a `.claude/agents/evaluator.md` subagent (separate context window)
   - Read-only tools: Read, Grep, Glob (never modifies routine output)
   - Returns structured scores per dimension + overall pass/fail
3. **Scores log to Supabase** eval layer (eval_runs, eval_scores tables from Phase 1A schema)
4. **Weekly aggregation** alerts on degradation
   - Score trending down over 7-day window triggers Slack alert
   - Identifies which dimension is degrading (e.g., "brand voice scores dropped 15%")
5. **The evaluator evaluates itself** — it has its own Promptfoo eval suite
   - Test cases with known-good and known-bad routine outputs
   - Expected scores for each test case
   - The evaluator must score known-bad outputs low and known-good outputs high

### Chief of Staff Extension

The Chief of Staff's email triage pipeline is already running from Phase 1B. Phase 3 extends the agent with additional capabilities — it does NOT rebuild email automation. Potential extensions:
- Calendar awareness (meeting prep, scheduling conflicts)
- Cross-venture priority routing (TS emails, personal emails, advisory emails)
- Weekly attention report: what consumed Chris's time, what was filtered

---

## Phase 4 — Portfolio and Positioning

**Depends on:** Phase 1 minimum (need working projects to showcase)
**Delivers:** Professional positioning materials

Can start partially in parallel with Phases 2-3 since it is primarily content work.

### PDF Deck

Builder narrative: who you are -> what you've built -> how you think -> what you're looking for. Hybrid audience: employment at AI companies + advisory/operator roles.

Content arc:
1. **Who I am** — CPG analytics -> product leader -> AI entrepreneur
2. **What I've built** — Production NL2SQL agent at Daasity, multi-agent TS ops, personal OS with Paperclip
3. **How I think** — Principles, architecture philosophy, "March of Nines" operational rigor, atoms-before-molecules, eval-driven development
4. **What I'm looking for** — AI company roles (product, engineering leadership), advisory/operator positions

### Portfolio Website

Framework TBD. Project deep-dives with architecture diagrams. Contact form. Deploy free.

---

## Phase 5 — Deepening and Scale

**Depends on:** Phase 3 complete
**Delivers:** Production-quality skills, autoresearch, expanded agents

### Skill Deepening

Bring stubs to production quality. Decision trees with thresholds, response templates, Supabase query references, escalation rules, anti-patterns. Priority: shared skills first, then active agent skills.

**`/batch` for codebase-wide skill quality improvements:** Use Claude Code's `/batch` command to fan out quality improvements across all skill files simultaneously. The workflow:

1. Define the quality rubric (decision trees, thresholds, examples, anti-patterns)
2. Run `/batch improve all SKILL.md files to meet the quality rubric in docs/specs/skills-spec.md`
3. `/batch` enters plan mode, launches Explore agents to inventory all skill files
4. Decomposes into units: one unit per skill file (or skill directory)
5. Spawns worktree-isolated agents to improve each skill independently
6. Each agent: reads the quality rubric, reads the current skill, rewrites to meet rubric, runs skill-specific tests
7. Results: PRs per skill, review and merge

This is the ideal `/batch` use case — independent files, clear rubric, no shared state between improvements.

### Autoresearch Loops

For eligible domains (agent prompts, product descriptions, email subject lines):

1. **Promptfoo eval suites** define the quality bar
2. **Nightly scoring** runs the eval suite against current prompt/template
3. **Automated prompt variant generation** proposes improvements
4. **A/B scoring** compares variants against the current version
5. **Board approval** for any variant that scores higher
6. **Rollback** if production scores degrade after deployment

**Autoresearch loop architecture:**

```
┌─────────────────────────┐
│  Nightly cron trigger   │
└────────────┬────────────┘
             │
┌────────────▼────────────┐
│  Run Promptfoo eval on  │
│  current prompt version │
└────────────┬────────────┘
             │
     ┌───────▼───────┐
     │ Score above    │──── Yes ──→ Log scores, done
     │ threshold?     │
     └───────┬───────┘
             │ No (or "try to improve")
     ┌───────▼───────────────┐
     │ Generate 3-5 prompt   │
     │ variants (Sonnet)     │
     └───────┬───────────────┘
             │
     ┌───────▼───────────────┐
     │ Score all variants    │
     │ against eval suite    │
     └───────┬───────────────┘
             │
     ┌───────▼───────┐
     │ Best variant   │──── No ──→ Log, flag for human review
     │ beats current? │
     └───────┬───────┘
             │ Yes
     ┌───────▼───────────────┐
     │ Propose to Board      │
     │ (Slack + Paperclip)   │
     └───────┬───────────────┘
             │
     ┌───────▼───────┐
     │ Board approves │──── No ──→ Keep current, log rationale
     └───────┬───────┘
             │ Yes
     ┌───────▼───────────────┐
     │ Deploy new version    │
     │ Monitor for 48hrs     │
     │ Auto-rollback if      │
     │ scores degrade        │
     └───────────────────────┘
```

Eligible domains for Phase 5:
- **Email classification prompts** — the Chief of Staff's classification accuracy can improve over time
- **Product description templates** — SEO and conversion optimization
- **Email subject lines** — open rate optimization (requires Shopify/Klaviyo integration)
- **Agent prompts** — soul file refinement based on override patterns

### Financial Controller Agent

Weekly financial snapshots. Cash flow forecasting. Builds on the Weekly P&L routine from Phase 1A but with deeper analysis:
- Cash runway projections (3, 6, 12 month)
- Revenue trend analysis with seasonality detection
- Expense categorization and anomaly flagging
- Board-ready financial summary

### Content Pipeline Scoping

Evaluate YouTube transcription feasibility for dharma teaching content that serves TS product descriptions, educational material, and knowledge base articles. Pilot on ROK-BOX GPU.

- Whisper transcription on ROK-BOX (RTX 3080, local processing)
- Content extraction: teachings -> product context, educational material, FAQ answers
- Integration: extracted content feeds into product description optimizer (Phase 2) and campaign brief generator (Phase 2) as additional context
- This is a scoping exercise first — evaluate feasibility before committing to a full pipeline

---

## Verification & Testing

### Phase 2 Verification Checklist

- [ ] CS Email Drafts: Haiku triage -> enrichment -> Sonnet draft pipeline works end-to-end
- [ ] CS Email Drafts: Board approval gate blocks sending without approval
- [ ] Inventory Alerts: Shopify API sync populates Supabase correctly
- [ ] Inventory Alerts: Reorder threshold comparison generates accurate alerts
- [ ] Campaign Brief Generator: Produces coherent briefs from revenue + seasonal + inventory data
- [ ] Product Description Optimizer: Evaluator-optimizer loop runs max 3 iterations
- [ ] Product Description Optimizer: Cultural sensitivity rubric catches inappropriate content
- [ ] Customer Profiles: RFM scoring matches manual calculations
- [ ] Langfuse: `@observe()` decorators capture cost, latency, prompt versions
- [ ] Reliability Pass: All imports resolve, all Supabase queries valid
- [ ] All eval suites pass for every new routine
- [ ] CCPA ADMT compliance checkpoint completed before customer-facing routines go live
- [ ] System wiki updated with new routines and operational documentation
- [ ] All routine scripts have zero Paperclip imports

### Phase 3 Verification Checklist

- [ ] Fitness Coach: Daily workout matches training template and periodization schedule
- [ ] Fitness Coach: Progressive overload calculations are mathematically correct
- [ ] Fitness Coach: Deload detection triggers appropriately
- [ ] Research Analyst: Multi-source synthesis includes confidence levels
- [ ] Research Analyst: Friday digest covers all ventures, not just TS
- [ ] Cross-Company Patterns: chris-os agents route to TS through Board, not direct coupling
- [ ] Subagent Evaluator: Scores known-good outputs high, known-bad outputs low
- [ ] Subagent Evaluator: Weekly degradation alerts fire when scores trend down
- [ ] Subagent Evaluator: Has its own Promptfoo eval suite that passes
- [ ] Chief of Staff extension capabilities work without breaking existing email triage
- [ ] System wiki updated with new agents and cross-company patterns

### Phase 4 Verification Checklist

- [ ] PDF Deck: Narrative arc covers all four sections (who/built/think/looking for)
- [ ] PDF Deck: Reviewed by Chris for accuracy and tone
- [ ] Portfolio Website: Project deep-dives include architecture diagrams
- [ ] Portfolio Website: Deploys successfully to free hosting
- [ ] Portfolio Website: Contact form works

### Phase 5 Verification Checklist

- [ ] Skill Deepening: All priority skills meet the quality rubric in specs/skills-spec.md
- [ ] Skill Deepening: `/batch` successfully processes skill files without conflicts
- [ ] Autoresearch Loops: Nightly scoring runs reliably via PM2 cron
- [ ] Autoresearch Loops: Variant generation produces meaningfully different prompts
- [ ] Autoresearch Loops: Board approval gate works (no automatic deployment without approval)
- [ ] Autoresearch Loops: Auto-rollback triggers on score degradation
- [ ] Financial Controller: Cash runway projections match manual calculations
- [ ] Financial Controller: Anomaly flagging identifies known test anomalies
- [ ] Content Pipeline: Whisper transcription produces usable text from test audio on ROK-BOX
- [ ] Content Pipeline: Feasibility assessment delivered with clear go/no-go recommendation
