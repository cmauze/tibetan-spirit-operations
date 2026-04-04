# Phases 1-5 — Scope Outlines

**Note:** These are scope outlines, not full task cards. Detailed implementation prompts for Phases 1-5 should be generated AFTER Phase 0B completes, because the guides written in 0B inform the specific implementation patterns. Generate each phase's detailed card only when the prior phase is complete.

---

## Phase 1 — First Atoms

**Depends on:** Phase 0B complete (guides written, vault consolidated)
**Delivers:** First working routines, first agent, Slack bridge

### Tibetan Spirit Foundation

Create the TS project structure following the agent-centric layout from `specs/agents-spec.md`. Implement the shared Python library: claude_client.py (skill loading, prompt caching, cost calculation), org.py (role resolution from ORG.md), notifications.py (Slack), cost_tracker.py (invocation logging to Supabase). Expand Supabase schema with the three-layer model (registry, runtime, eval) from the existing DEV-PLAN — minus dashboard-specific tables since Paperclip's dashboard replaces the custom PWA.

Build two routines as standalone scripts first, then graduate them into Paperclip agents. Daily Order Summary (Haiku, auto-logged, 6pm Denver) and Weekly P&L (Sonnet, Board approval required, Monday 6am). Each routine loads relevant skills, queries Supabase, calls Anthropic API, writes results to Paperclip's ticket system, logs costs. Write Promptfoo eval suites for both. Run both for 7 consecutive days on real data before graduation.

### chris-os Chief of Staff

Build the first personal agent: email triage via Gmail API. The agent classifies emails (Action Required, FYI, Delegate, Archive), drafts one-line summaries for Action Required items, posts batches to Paperclip. Runs 3x daily via heartbeat. First week: Chris validates every classification. Rewrite the soul file based on observed error patterns after the first week.

### Slack Bridge

Build the Slack Bolt Python bridge connecting Paperclip's ticket system to Slack channels. Polls Paperclip API every 30 seconds. Formats tickets as Block Kit messages with approve/reject buttons. Routes to channels by company and priority. Handles button-click approvals back to Paperclip. Deploy on server via PM2.

### Community Skill Sourcing

Search skill marketplaces (SkillsMP, SkillHub, Anthropic official) for infrastructure/utility skills. Evaluate against quality criteria from `specs/skills-spec.md`. Fork and adapt top 5-10. Write custom skills for business-specific needs (brand-guidelines, product-knowledge, escalation-matrix).

### Graduation

After 7 days of reliable operation, routines that pass the graduation checklist get registered as Paperclip agents with soul files, heartbeat schedules, and budget caps. They appear in the Paperclip dashboard with run history and budget utilization.

---

## Phase 2 — Tibetan Spirit Operations Core

**Depends on:** Phase 1 complete (routines running, Slack bridge operational)
**Delivers:** Complete TS operational routine suite

**CS Email Drafts:** Three-step chain — Haiku triage → Supabase customer enrichment → Sonnet draft. Intercom integration for ingestion and reply. Every draft requires Board approval before sending.

**Inventory Alerts:** Shopify API sync to Supabase. Compare against reorder thresholds. Sonnet generates priority-sorted alerts with suggested POs. Routes to operations-manager.

**Campaign Brief Generator:** Top products by revenue + seasonal context + inventory data → campaign theme, target segment, subject lines, product selection. Board approval.

**Product Description Optimizer:** Evaluator-optimizer loop: Sonnet generates → Haiku evaluates against rubric (SEO, brand voice, accuracy, cultural sensitivity) → regenerate if below threshold → max 3 iterations.

**Customer Profiles:** RFM scoring from order history. Heuristic segmentation. Enriches CS drafts and campaign targeting.

**Langfuse Deployment:** Self-host via Docker on server. Wrap Agent SDK calls with `@observe()`. Cost tracking, latency monitoring, prompt versioning.

**Reliability Pass:** All imports resolve, all Supabase queries valid, all eval suites pass.

**Compliance Check:** Audit routines for CCPA ADMT before any automated customer-facing communications go live.

---

## Phase 3 — Personal Agents

**Depends on:** Phase 2 complete
**Delivers:** Personal agents, cross-company patterns

**Fitness Coach Agent:** Daily workout posts matching Chris's training template. Progressive overload calculations. Weekly programming reviews. Periodization and deload management.

**Research Analyst Agent:** On-demand tasks assigned through Paperclip. Multi-source synthesis with confidence levels. Friday digest of developments relevant to Chris's portfolio.

**Cross-Company Patterns:** Define how agents in chris-os serve TS operations (Chief of Staff routes TS emails, Research Analyst does TS competitive research). The Board is the bridge between companies.

**Subagent Evaluator:** Deploy for highest-value routines. Haiku scores against rubrics. Scores log to Supabase. Weekly aggregation alerts on degradation.

---

## Phase 4 — Portfolio and Positioning

**Depends on:** Phase 1 minimum (need working projects to showcase)
**Delivers:** Professional positioning materials

Can start partially in parallel with Phases 2-3 since it is primarily content work.

**PDF Deck:** Builder narrative: who you are → what you've built → how you think → what you're looking for. Hybrid audience: employment at AI companies + advisory/operator roles.

**Portfolio Website:** Framework TBD. Project deep-dives with architecture diagrams. Contact form. Deploy free.

---

## Phase 5 — Deepening and Scale

**Depends on:** Phase 3 complete
**Delivers:** Production-quality skills, autoresearch, expanded agents

**Skill Deepening:** Bring stubs to production quality. Decision trees with thresholds, response templates, Supabase query references, escalation rules, anti-patterns. Priority: shared skills first, then active agent skills.

**Autoresearch Loops:** For eligible domains (agent prompts, product descriptions, email subject lines): Promptfoo eval suites, nightly scoring, automated prompt variant generation.

**Financial Controller Agent:** Weekly financial snapshots. Cash flow forecasting.

**Content Pipeline Scoping:** Evaluate YouTube transcription feasibility for dharma teaching content that serves TS product descriptions, educational material, and knowledge base articles. Pilot on ROK-BOX GPU.
