# Replacing Shortwave AI + Tasklet with Claude Code and Gmail API

**A custom email automation system using Claude for classification and Gmail API for label management can replicate and significantly exceed what Shortwave's paid AI features and Tasklet provide — at a fraction of the cost.** The combination of Gmail's generous API limits (10,000 labels, 1,000 filters, 300,000 label modifications per minute), Claude Haiku's near-frontier classification accuracy at ~$0.001/email, and Shortwave's bidirectional label sync means Chris can build a system that classifies into unlimited labels (vs. Shortwave's 10-filter Premier limit), runs 24/7 on a MacBook via PM2, and keeps Shortwave as the beautiful reading UI. Open-source projects like Inbox Zero (10K GitHub stars) and gmail-llm-labeler prove this architecture works in production. This report covers every research dimension needed to write the specification.

---

## What Shortwave actually gives you (and where it falls short)

Shortwave, built by ex-Google Inbox engineers including Firebase founder Andrew Lee, runs exclusively on Gmail and currently uses **Anthropic's Claude models** across its tiers: Haiku 4.5 for free users, Sonnet 4.6 for Business ($24/month), and Opus 4.6 for Max ($100/month). The product's core AI features — filters, smart labels, splits, bundles, delivery schedules — work together to triage email, but several hard limits constrain power users.

**AI Filters** are Shortwave's most relevant feature for replication. Users define filter logic in natural language (e.g., "Include emails about billing issues or payment problems"), and Shortwave's AI reads each incoming email to apply actions: labeling, archiving, starring, or deleting. The constraint is strict: **Business gets 3 filters, Premier gets 10, Max gets 50**. The Premier tier's 10-filter limit is the ceiling Chris is hitting. Filters support combining natural language descriptions with traditional Gmail search queries, and include pre-built templates for common patterns (cold outreach, needs action, FYI, travel, finance, purchases).

**Smart Labels** work by sender memory: when you apply a label to a thread, Shortwave remembers that sender and auto-applies the label to future emails from them. This is purely sender-based, not content-based — which means it can be over-eager and mislabels when a sender's emails span multiple topics. Gmail labels sync bidirectionally: label changes in Shortwave propagate to Gmail instantly, while Gmail-side name/color edits sync to Shortwave daily (force-syncable via Settings > Support > Refresh Gmail data). Nested labels created in Gmail import into Shortwave via the standard `/` separator convention.

**Splits** divide the inbox into tabbed mini-inboxes defined by importance, labels, senders, or search queries. **Bundles** collapse related threads into a single line item. **Delivery Schedules** hold emails matching certain criteria and release them at configured times (e.g., newsletters only on Saturday mornings). The **Todo system** converts emails to tasks with grouping, notes, reordering, and cross-split visibility. All of these features layer on top of Gmail labels — meaning a custom system that applies the right labels can trigger much of this behavior.

**Shortwave has no public API.** Multiple sources confirm it offers no developer API for external access. However, Shortwave *is* an MCP client — it connects to external MCP servers (Slack, Notion, Asana, HubSpot, Linear, GitHub, Zapier, and custom servers) via HTTP/SSE or stdio. This is limited to tool calls only (no resources, prompts, or sampling), with a max of **40 tools** across all connected MCP servers. This means the custom system cannot push data *into* Shortwave programmatically — but it doesn't need to, because Gmail labels applied via the API appear in Shortwave automatically.

Shortwave's underlying AI architecture is a RAG pipeline: full inbox download, vector embeddings, full-text search, cross-encoding re-ranking, and multi-step reasoning. The Ghostwriter writing personalization system learns the user's voice from sent emails. These are the hardest features to replicate and are largely outside scope for the email classification project.

---

## Tasklet is powerful but expensive and non-deterministic

Tasklet launched October 8, 2025 as Shortwave's sister product — a separate automation engine that runs 24/7 without user interaction. Where Shortwave handles interactive email, Tasklet handles autonomous background automation. Direct Shortwave integration landed January 6, 2026, enabling Tasklet to create drafts in Shortwave, manage todos, and add thread comments.

Tasklet's defining feature is **natural-language automation definition** — no workflow builder, no node graphs, no code. You describe what you want in plain English, and the AI figures out which tools to connect and how to handle edge cases. It uses a two-tier agent architecture: a persistent high-level agent maintains instructions and memories, while ephemeral sub-agents handle individual task runs with results stored in a SQL database for cross-run context.

Tasklet supports three trigger types: **scheduled** (daily, weekly, every 15 minutes), **email** (new arrivals, label applications), and **webhook** (external events). It integrates with thousands of apps via Pipedream, can call arbitrary HTTP APIs with provided credentials, connects to MCP servers, and has a unique computer-use fallback — a persistent Ubuntu VM in Google Cloud where it navigates web UIs via computer vision when no API exists.

The limitations are significant for Chris's use case. **Pricing starts at $35/month** (Starter) and reaches $250/month (Business), on top of Shortwave's subscription — and CEO Andrew Lee openly acknowledges it's "way more expensive than Zapier." The system is **non-deterministic** by nature; agentic reasoning can misinterpret nuanced instructions. Enterprise features (logging, audit trails, cost management) are still "on the roadmap." Most critically, Tasklet's value proposition — the natural-language-to-automation pipeline — is precisely what Claude Code already provides, making Tasklet redundant for a developer-capable user.

---

## Gmail API provides everything the automation layer needs

The Gmail API through `google-api-python-client` offers generous limits well-suited for a personal automation system. The key numbers that matter:

**Rate limits** operate on a quota-unit system: **15,000 units per user per minute** (per-project limit is 1,200,000 units/minute). A `messages.batchModify` call costs 50 units and handles up to **1,000 message IDs** per request — meaning a single user can perform 300 batch modifications per minute, touching **300,000 messages per minute**. Individual `messages.get` or `messages.modify` cost 5 units each, allowing 3,000 individual operations per minute. For a personal inbox processing perhaps 50-200 emails per day, quota is a non-issue.

**Label management** supports up to **10,000 labels per account**, with Google recommending ≤500 for performance. For a taxonomy of 10 core labels + 30-40 project labels, this is well within safe range. Labels are created via `labels.create` with support for nested hierarchy using `/` separators in names (e.g., `Projects/Alpha` appears as "Alpha" nested under "Projects" in Gmail's UI). The parent label must exist before creating children. Label colors are constrained to ~98 predefined hex values — arbitrary colors are not supported. Labels support visibility settings (`labelShow`, `labelShowIfUnread`, `labelHide`) to manage clutter.

**Gmail Filters API** (`users.settings.filters`) supports up to **1,000 filters per account** with full CRUD operations except update (must delete and recreate). Filters match on sender, recipient, subject, arbitrary Gmail search queries, attachment presence, and message size. Actions include adding/removing labels and forwarding. Critically, API-created filters only apply to **future incoming messages** — retroactive labeling requires `messages.list` with query parameters followed by `batchModify`.

**OAuth2 for always-on scripts** requires obtaining a refresh token during initial interactive authorization (`access_type='offline'`, `prompt='consent'`). Access tokens expire after 1 hour but auto-refresh using the refresh token. For apps published to production status, **refresh tokens do not expire** (apps in "Testing" status get only 7-day tokens — publishing to production is essential). Service accounts cannot access personal @gmail.com accounts, only Google Workspace with domain-wide delegation.

**Push notifications** via `users.watch()` + Google Cloud Pub/Sub deliver near-real-time alerts when the mailbox changes. The watch expires after **7 days maximum** and must be renewed (recommended: daily). Notifications contain only `emailAddress` and `historyId` — you must call `history.list` to get actual changes. Maximum notification rate is 1 event per second per user. Setup requires a Cloud Pub/Sub topic with publish permissions granted to `gmail-api-push@system.gserviceaccount.com`. For a simpler alternative, **polling with `history.list`** (2 quota units per call) every 1-5 minutes works well for personal automation where sub-second latency isn't needed.

For the recommended processing pipeline: use `messages.list` with Gmail search query (`q` parameter supporting `from:`, `label:`, `is:unread`, `newer_than:`, boolean operators, and more) to find target messages, paginate results (max 500 per page), collect IDs, chunk into groups of 1,000, then call `batchModify` for each chunk.

---

## The open-source landscape proves this architecture works

A rich ecosystem of open-source projects from 2024-2026 demonstrates that LLM-powered email classification via Gmail API is a solved problem at the architectural level.

**Inbox Zero** (github.com/elie222/inbox-zero) is the most mature project with ~10,000 GitHub stars, 50+ contributors, and SOC 2 Type II certification. Built with TypeScript/Next.js, it supports multiple LLM providers (OpenAI, Anthropic, Google Gemini, Groq), uses Google PubSub for real-time processing, and lets users define AI rules in plain English. Its core insight: "natural language rule definitions are the UX pattern that works best for email automation." It's a full SaaS platform, heavier than what Chris needs, but its architecture validates the approach.

**gmail-llm-labeler** (github.com/ColeMurray/gmail-llm-labeler) is the canonical minimal implementation — a Python CLI with clean ETL pipeline architecture: Extract (fetch via Gmail API since last run) → Transform (classify with LLM) → Load (apply Gmail labels). Uses SQLite to track processed emails, supports dry-run mode, and logs all LLM interactions in JSONL format. The blog post walkthrough notes that **GPT-4o-mini with `max_tokens=10, temperature=0.3` is sufficient for classification**, and emphasizes always including an "Other" fallback category.

**MailSentinel** demonstrates enterprise-grade patterns in email classification: **YAML-based classification profiles** with model selection, system prompts, and few-shot examples per profile. Profiles support inheritance and dependency resolution. The project uses circuit breaker patterns for resilience and cryptographic audit trails. It was built in a 4-hour human-AI pair programming session — evidence that Claude Code can build these systems rapidly.

**Exo** (exo.email) is the most sophisticated Claude-specific project — a full desktop email client using Claude exclusively for classification. Key innovation: **persistent AI memories scoped per-sender and per-topic**, and learning from classification overrides to improve accuracy over time. It processes email via Gmail History API every 30 seconds.

The **MCP server pattern** is emerging as the 2025-2026 standard for Claude-Gmail integration. A "thin MCP proxy" exposes Gmail as tools to Claude, with all reasoning happening in the LLM. Rules are stored as plain, inspectable local files. The server handles auth and API complexity while remaining stateless.

Five dominant architecture patterns emerge across all projects:

- **ETL Pipeline** (most common): fetch → classify → label, with SQLite tracking processed IDs
- **Agent-with-Tools**: LLM orchestrates Gmail operations through defined tool interfaces
- **MCP Proxy**: thin server exposes Gmail capabilities, Claude handles all reasoning
- **Event-Driven**: Pub/Sub webhooks trigger classification on new email arrival
- **Workflow Automation**: n8n/Make.com chains for no-code approaches

The key cross-cutting lessons: track processed emails to ensure idempotency, include dry-run/preview mode for building trust, use rules for deterministic patterns and LLM only for ambiguous cases (hybrid approach handles 40-60% of emails for free), and always include human-in-the-loop feedback mechanisms.

---

## Haiku handles classification at $0.001 per email

Email classification is one of the tasks where Claude's smaller models shine. **Travelers Insurance achieved 91% accuracy across 13 categories using prompt engineering alone** — no fine-tuning — with Claude Instant (Haiku-equivalent) reaching 90%, just 1 percentage point behind the full model. For Chris's system, Haiku 4.5 at **$1.00 per million input tokens / $5.00 per million output tokens** is the optimal default.

The recommended prompt architecture uses a **cached system prompt** containing the classifier persona, all category definitions with distinguishing criteria, and 2-5 few-shot examples for commonly confused categories. The user message contains only the email to classify. Prompt caching reduces input costs by **90%** on cache hits (0.1x base price), and the cache persists for 5 minutes standard or 1 hour with extended TTL. With a ~1,000-token system prompt cached at 80% hit rate, effective throughput increases 5-10x since cached tokens don't count toward rate limits.

**Structured outputs** (GA since late 2025) guarantee valid JSON conforming to a defined schema. Using `enum` constraints on the `primary_label` field ensures Claude returns only valid label names — no parsing failures. The classification schema should include `primary_label`, `confidence` (0.0-1.0), `priority` (urgent/normal/low), optional `project_labels` array, and a `reasoning` field that dramatically improves classification quality and enables debugging.

The **tiered routing architecture** optimizes both cost and accuracy:

1. **Rules engine** (free, instant): Header checks (`List-Unsubscribe` → newsletter), domain patterns (`@github.com` → dev notifications), known sender maps. Handles 40-60% of email.
2. **Haiku 4.5** (~$0.001/email): Standard classification for ~95% of remaining emails. Confidence threshold at 0.7-0.85.
3. **Sonnet 4.5** (~$0.004/email): Re-classification with chain-of-thought for low-confidence cases and VIP senders. ~5% of remaining emails.
4. **Human review queue**: Dedicated "Needs Review" label for cases where even Sonnet is uncertain.

For Chris's likely volume of 50-200 emails/day, estimated costs with this approach: **$3-10/month** total, compared to Shortwave Premier at $36/month + Tasklet at $35-100/month. The **Batch API** offers an additional 50% discount for non-urgent processing (daily backlog runs), and combines with prompt caching for 50-85% total savings.

The taxonomy should use a **two-pass hierarchical approach**: Pass 1 classifies into ~10 core labels (high accuracy, every email), Pass 2 conditionally classifies into project-specific labels (only for actionable emails). This reduces the label space per call and improves accuracy versus attempting to classify into 40+ labels simultaneously. Research on hierarchical multi-label classification confirms that trying to classify into hundreds of labels simultaneously degrades LLM accuracy.

For the cold-start problem with new senders: rely on content-first classification (email body analysis), domain-based heuristics, and email header signals. Track sender classification history over time in a local database, and after N confirmed classifications, apply rule-based routing as the default with LLM as override. This creates a **flywheel effect** where the system gets cheaper and faster over time as more senders move from LLM classification to rules.

---

## Specification-first development with CLAUDE.md at the center

The project should follow README-Driven Development as articulated by GitHub co-founder Tom Preston-Werner: "Write your README first. As in, before you write any code or tests or behaviors or ANYTHING." The README serves as both specification and north star, preventing the common failure mode of building "a perfect implementation of the wrong specification."

The modern evolution of this approach, formalized by GitHub's Spec Kit (September 2025), follows a four-phase workflow: **Specify → Plan → Tasks → Implement**. Addy Osmani's January 2026 analysis of 2,500+ AI agent configuration files identified six core areas every spec should cover: Commands, Testing, Project Structure, Code Style, Git Workflow, and Boundaries.

For a Claude Code-driven project, the **CLAUDE.md file** is the highest-leverage artifact. It's read automatically at the start of every Claude Code session and should be kept under **100-150 lines** — research shows that as instructions increase, compliance drops uniformly across all instructions. Use the WHAT/WHY/HOW framework: tech stack and structure (WHAT), project purpose and component roles (WHY), and build/test/deploy commands (HOW). Keep domain-specific details in separate docs files and reference them from CLAUDE.md: "When working on classification, first read docs/CLASSIFICATION.md."

The recommended documentation structure for this project:

```
email-automation/
├── README.md                    # Vision, features, architecture overview, quick start
├── CLAUDE.md                    # <100 lines: stack, structure, commands, key pointers
├── docs/
│   ├── SPEC.md                  # Detailed PRD with user stories and acceptance criteria
│   ├── ARCHITECTURE.md          # System design with Mermaid diagrams
│   ├── CLASSIFICATION.md        # Label taxonomy, prompt templates, routing logic
│   ├── GMAIL-API.md             # API integration patterns, auth, rate limits
│   ├── TRIGGERS.md              # Trigger registry format, approval gates
│   ├── DEPLOYMENT.md            # PM2 setup, MacBook server config, monitoring
│   ├── adr/
│   │   ├── 001-use-haiku-for-classification.md
│   │   ├── 002-polling-vs-push-notifications.md
│   │   ├── 003-sqlite-for-state-tracking.md
│   │   └── template.md
│   └── diagrams/                # Exported Mermaid diagrams if needed
├── src/
├── tests/
└── config/
    ├── labels.yaml              # Label taxonomy definition
    ├── rules.yaml               # Deterministic routing rules
    └── prompts/                 # Classification prompt templates
```

**Architecture Decision Records** (ADRs) should capture every significant technical choice using the Nygard template: Title, Status (Proposed/Accepted/Deprecated), Context (forces at play), Decision ("We will..."), and Consequences (positive, negative, neutral). Store them in version control alongside code, and review each one month after acceptance.

The Amazon "Working Backwards" PR/FAQ format is valuable for the initial README: write it as if the system already exists and works. "This system processes incoming Gmail using Claude AI to classify emails into a human-defined taxonomy of labels, visible in Shortwave within seconds of arrival. It handles 200+ emails daily at under $5/month, replaces $71+/month in Shortwave Premier + Tasklet subscriptions, and gives the user unlimited classification rules instead of Shortwave's 10-filter cap."

---

## Six Mermaid diagrams tell the complete architecture story

Mermaid.js diagrams render natively in GitHub README files, VS Code, GitLab, and Obsidian. For this project, six diagrams provide comprehensive architectural documentation. Each should stay under **15-20 nodes** for readability, using the "sandwich" pattern: contextual text → diagram → key takeaways.

**Diagram 1 — System Context (C4)** shows the four participants: User, Email Automation System, Gmail API, Claude API, and Shortwave. This belongs in README.md to give readers immediate architectural orientation.

**Diagram 2 — Container Architecture (Flowchart with subgraphs)** zooms into the system showing: Local Server (orchestrator), Classification Engine (Claude client), Rules Engine (deterministic routing), Config Store (YAML), Email Cache (SQLite), and the external APIs. This goes in ARCHITECTURE.md.

**Diagram 3 — Processing Pipeline (Flowchart, top-down)** shows the step-by-step flow: Scheduler triggers → Fetch new emails → Check processed cache → Extract content → Apply rules engine → Send to Claude if needed → Apply labels via Gmail API → Update cache. Include decision diamonds for rules-vs-LLM routing and confidence thresholds.

**Diagram 4 — API Interaction Sequence** uses a sequence diagram to show temporal API call flows between Scheduler, Local Server, Gmail API, Claude API, and SQLite Cache. Include the loop for processing each email and the alt/else for confidence-based model escalation.

**Diagram 5 — Email State Machine** models the lifecycle: New → Fetched → Rules-Matched or Classifying → Classified → Labeled → (Archived or In-Inbox). Include error states with retry logic and a Manual Review terminal state.

**Diagram 6 — Classification Decision Tree** shows the tiered routing: Known sender list check → Header-based rules → Domain heuristics → Haiku classification → Confidence check → (Apply labels or escalate to Sonnet or flag for review).

Best practices for maintainability: use descriptive node IDs (`GMAIL_API[Gmail API]` not `A[Gmail API]`), declare nodes before connections, use `%%` comments to annotate sections, limit subgraph nesting to 2 levels, and test all diagrams in mermaid.live before committing. The ELK layout engine (`%%{init: {"flowchart": {"defaultRenderer": "elk"}}}%%`) handles larger diagrams better than the default renderer.

---

## Building atoms before molecules: the implementation sequence

Chris's "build atoms before molecules" principle maps perfectly to a phased implementation where each phase produces a working, testable unit before the next phase begins.

**Atom 1 — Gmail Auth + Label Bootstrap**: OAuth2 flow with persistent refresh token storage, label CRUD operations, and a script that reads `config/labels.yaml` and ensures all defined labels exist in Gmail with correct colors and nesting. This is the foundation everything else depends on. Verify: labels appear correctly in Shortwave.

**Atom 2 — Email Fetcher**: Poll-based fetcher using `messages.list` with configurable query parameters and `history.list` for incremental sync. SQLite database tracks processed message IDs with timestamps. Verify: fetches new unread emails since last run, never re-processes.

**Atom 3 — Rules Engine**: Deterministic routing from `config/rules.yaml` — sender patterns, domain maps, header checks. Returns label assignments or "needs LLM classification." Verify: correctly labels newsletters, known-sender emails, automated notifications without any API calls.

**Atom 4 — Claude Classification**: System prompt + category definitions + few-shot examples, cached. Structured output with JSON schema. Haiku 4.5 as default, Sonnet fallback for low-confidence results. Verify: classifies test emails into correct labels with >85% accuracy.

**Atom 5 — Label Applicator**: Takes classification results and applies Gmail labels via `batchModify`. Handles batch chunking (max 1,000 per call), retry logic with exponential backoff, and idempotent state updates. Verify: labels appear in Gmail and sync to Shortwave.

**Molecule 1 — Processing Pipeline**: Chains Atoms 2-5 into a single processing run. Scheduler triggers (cron via PM2), fetches new emails, routes through rules engine, sends remainder to Claude, applies labels, updates state. Verify: end-to-end processing of new emails with correct labeling.

**Molecule 2 — Trigger Registry**: A YAML/Markdown document defining all active automation rules with human approval gates. New rules proposed by Claude require explicit user approval before activation. Change history tracked in git. Verify: adding a new rule to the registry results in correct behavior on next processing cycle.

**Molecule 3 — Monitoring + Feedback**: Classification logging (every decision with reasoning), daily summary report, misclassification correction interface (moving an email to a different label triggers a feedback event), and prompt refinement based on accumulated corrections.

---

## Conclusion

The technical foundation for this system is sound, well-proven, and surprisingly straightforward. Gmail's API provides **orders of magnitude more capacity** than a personal inbox needs — 10,000 labels vs. 50 needed, 300,000 label modifications per minute vs. hundreds per day, 1,000 filters vs. dozens. Claude Haiku 4.5 achieves classification accuracy within 1-2% of frontier models at **1/3 the cost**, and prompt caching plus tiered routing keep monthly costs under $10 for typical entrepreneur email volume. The bidirectional label sync between Gmail and Shortwave means every classification decision appears in Chris's email client instantly, without Shortwave needing an API.

The most valuable insight from the open-source landscape: **start with deterministic rules, use LLM only for what rules can't handle.** The gmail-llm-labeler and MailSentinel projects prove that a clean ETL pipeline with SQLite state tracking, YAML-configurable rules, and a thin LLM classification layer is both simple to build and reliable in production. The MCP proxy pattern offers a future evolution path where Claude Code itself becomes the orchestrator, but the initial system should be a straightforward Python pipeline managed by PM2 — atoms first, molecules after they're proven.

The specification-first approach, anchored by a CLAUDE.md under 100 lines and a docs/ folder with focused documents for each concern, ensures Claude Code can build each atom with full context while keeping the overall system comprehensible to someone encountering it for the first time. Six Mermaid diagrams — context, containers, pipeline, sequence, state machine, and classification tree — provide the visual architecture documentation that makes the system legible at any zoom level.