# d2c-operations-lead Plugin Extraction Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extract generalized D2C operations skills from tibetan-spirit-ops into a `plugin/d2c-operations-lead/` directory within the project, then symlink into `~/code/public-plugins/` for distribution.

**Architecture:** Plugin lives IN the source project (`tibetan-spirit-ops/plugin/d2c-operations-lead/`). Source of truth stays with the project. `public-plugins/d2c-operations-lead` is a symlink for distribution. Original skills in `skills/` are NEVER modified — the plugin contains independently-authored generalized versions.

**Tech Stack:** Claude Code plugins (skill SKILL.md format), markdown, JSON metadata

---

## File Structure

```
tibetan-spirit-ops/
├── skills/                    # UNCHANGED — branded originals stay here
└── plugin/
    └── d2c-operations-lead/
        ├── .claude-plugin/plugin.json
        ├── README.md
        └── skills/
            ├── cs-triage/
            │   ├── SKILL.md
            │   ├── metadata.json
            │   └── references/classification-matrix.md
            ├── cs-pipeline/
            │   ├── SKILL.md
            │   └── metadata.json
            ├── shopify-query/
            │   ├── SKILL.md
            │   ├── metadata.json
            │   └── references/query-patterns.md
            ├── order-inquiry/
            │   ├── SKILL.md
            │   ├── metadata.json
            │   └── references/status-mapping.md
            ├── fulfillment-flag/
            │   ├── SKILL.md
            │   ├── metadata.json
            │   └── references/decision-table.md
            ├── margin-reporting/
            │   ├── SKILL.md
            │   ├── metadata.json
            │   └── references/queries.md
            ├── campaign-brief/
            │   ├── SKILL.md
            │   ├── metadata.json
            │   └── references/brief-template.md
            ├── restock-calc/
            │   ├── SKILL.md
            │   ├── metadata.json
            │   └── references/formulas.md
            └── description-optimizer/
                ├── SKILL.md
                ├── metadata.json
                └── references/rubric.md
```

Symlink: `~/code/public-plugins/d2c-operations-lead` → `~/code/active/tibetan-spirit-ops/plugin/d2c-operations-lead`

---

## Generalization Principles

These apply to every skill:

1. **No brand names.** Replace "Tibetan Spirit" with generic D2C language. Replace "tibetanspirit.com" with "your store".
2. **No team names.** Replace "Jothi", "Fiona", "Dr. Hun Lye", "Omar", "Chris" with role IDs (`operations-manager`, `warehouse-manager`, `brand-specialist`, `regional-fulfillment`, `general-manager`).
3. **No cultural specifics.** Replace "dharma", "Buddhist", "Nepal artisan" with generic terms ("brand-specialist topics", "cultural/brand-sensitive content", "international sourcing region"). The TS originals keep these.
4. **No specific languages.** Replace "Bahasa Indonesia formal", "Mandarin", "Spanish" with "team member's configured language and channel".
5. **No specific products.** Replace "singing bowls", "thangkas", "malas" with generic product type references.
6. **No specific data paths.** Replace `ts_orders`, `data/finance-reports.json` with generic table/path references.
7. **Keep the methodology.** The workflow structure, decision frameworks, verification checklists, and common rationalizations are the VALUE — they stay.
8. **CCPA stays.** Compliance requirements are generic D2C obligations, not brand-specific.

---

### Task 1: Scaffold Plugin Directory + Manifest

**Files:**
- Create: `plugin/d2c-operations-lead/.claude-plugin/plugin.json`
- Create: `plugin/d2c-operations-lead/README.md`

- [ ] **Step 1: Create plugin directory structure**

```bash
mkdir -p ~/code/active/tibetan-spirit-ops/plugin/d2c-operations-lead/.claude-plugin
mkdir -p ~/code/active/tibetan-spirit-ops/plugin/d2c-operations-lead/skills
```

- [ ] **Step 2: Create plugin.json manifest**

Write to `plugin/d2c-operations-lead/.claude-plugin/plugin.json`:

```json
{
  "name": "d2c-operations-lead",
  "description": "D2C operations workflows — CS triage, inventory monitoring, fulfillment routing, marketing discipline, catalog optimization, and margin reporting for Shopify-based brands",
  "version": "0.1.0",
  "author": {"name": "Chris Mauzé", "url": "https://chrismauze.com"},
  "license": "UNLICENSED",
  "keywords": ["d2c", "ecommerce", "shopify", "operations", "cs-triage", "inventory", "fulfillment", "marketing", "catalog"]
}
```

- [ ] **Step 3: Create README.md**

Write to `plugin/d2c-operations-lead/README.md`:

```markdown
# d2c-operations-lead

D2C operations plugin for Claude Code. Encodes operational workflows for Shopify-based direct-to-consumer brands: customer service triage and drafting, fulfillment exception handling, inventory restocking, margin reporting, marketing discipline, and catalog description optimization.

## Skills

| Skill | Domain | Description |
|-------|--------|-------------|
| cs-triage | Customer Service | Email classification → 7 categories with escalation routing |
| cs-pipeline | Customer Service | End-to-end: triage → enrichment → draft → approval queue |
| shopify-query | Data Access | Real-time Shopify GraphQL lookups (orders, products, inventory) |
| order-inquiry | Customer Service | Order status → customer-facing language with special case handling |
| fulfillment-flag | Operations | Exception flagging and routing for fulfillment anomalies |
| margin-reporting | Finance | Weekly P&L with SKU-level margins, channel comparison, below-floor alerts |
| campaign-brief | Marketing | Structured briefs with tier classification and frequency cap enforcement |
| restock-calc | Inventory | Reorder point, safety stock, and restock quantity recommendations |
| description-optimizer | Catalog | Evaluator-optimizer loop with 5-dimension quality rubric |

## Prerequisites

- Shopify store with GraphQL Admin API access
- Database (Supabase recommended) with order, product, inventory, and COGS tables
- Gmail integration (for CS pipeline)
- Team notification channel (Slack recommended)

## Installation

```
/plugins install d2c-operations-lead
```

## Configuration

Each skill references generic role IDs. Configure your team's role mapping:

| Role ID | Responsibility |
|---------|---------------|
| `general-manager` | Final approvals, strategy, pricing |
| `operations-manager` | Orders, inventory POs, supplier comms |
| `warehouse-manager` | Pick/pack/ship, inventory counts |
| `brand-specialist` | Brand-sensitive content review, cultural accuracy |
| `regional-fulfillment` | Regional/international fulfillment |

Configure in your project's CLAUDE.md or org-roles rule file.
```

- [ ] **Step 4: Commit scaffold**

```bash
cd ~/code/active/tibetan-spirit-ops
git add plugin/d2c-operations-lead/.claude-plugin/plugin.json plugin/d2c-operations-lead/README.md
git commit -m "feat(d2c-operations-lead): scaffold plugin directory and manifest"
```

---

### Task 2: Generalize cs-triage

**Files:**
- Create: `plugin/d2c-operations-lead/skills/cs-triage/SKILL.md`
- Create: `plugin/d2c-operations-lead/skills/cs-triage/metadata.json`
- Create: `plugin/d2c-operations-lead/skills/cs-triage/references/classification-matrix.md`

- [ ] **Step 1: Create SKILL.md**

Write to `plugin/d2c-operations-lead/skills/cs-triage/SKILL.md`:

```markdown
---
name: cs-triage
description: Use when a customer email arrives and needs classification and routing before any response is drafted.
---

<HARD-GATE>
Brand-sensitive emails MUST be checked FIRST before any other classification. If the email contains questions about brand values, cultural significance, or product authenticity that require specialist knowledge, it escalates immediately to `brand-specialist` — no draft is created, no automated response is attempted.
</HARD-GATE>

# CS Email Triage

## Overview

Classifies incoming customer emails into 7 canonical categories and routes to the appropriate response workflow or escalation path. Brand-sensitive topics are always checked first.

## When to Use

- Incoming customer email needs classification before drafting
- CS drafter needs a category assignment for routing
- **Do NOT use for:** already-classified emails, internal team communications

## Workflow

1. Check for brand-sensitive content FIRST — if detected, escalate to `brand-specialist` immediately, do NOT draft
2. Check for complaint signals — priority handling
3. Multi-category: use highest severity (`complaint > order-issue > return-request > wholesale-inquiry > product-question > shipping-status`)
4. If uncertain: classify as `product-question`, flag for `general-manager` review
5. Apply brand voice checks (see Verification)
6. Log classification with `"ai_generated": true` for compliance

See `references/classification-matrix.md` for category signal words, response templates, and escalation paths.

## Common Rationalizations

| Rationalization | Reality |
|----------------|---------|
| "The question mentions the brand but it's really about the product" | If it touches brand values or cultural sensitivity, it is `brand-sensitive`. When uncertain, escalate. |
| "I'll draft a tentative response and flag it" | For `brand-sensitive`, do NOT draft. Escalation is the only output. |
| "Complaint is mild, I'll downgrade it" | Classify by content, not intensity. |

## Red Flags

- Drafting a response when category is `brand-sensitive`
- Downgrading complaint severity based on tone mildness
- Skipping brand voice checks
- Missing `"ai_generated": true` in log

## Verification

- [ ] Brand-sensitive check run FIRST
- [ ] Category assigned from canonical 7 categories only
- [ ] No brand-prohibited vocabulary used
- [ ] Products framed per brand guidelines
- [ ] No claims beyond product specifications
- [ ] Compliance log entry includes `"ai_generated": true`
```

- [ ] **Step 2: Create metadata.json**

Write to `plugin/d2c-operations-lead/skills/cs-triage/metadata.json`:

```json
{
  "name": "cs-triage",
  "description": "Customer email classification and routing for CS workflow.",
  "domain": "customer-service",
  "triggers": ["triage customer email", "CS triage", "classify inquiry"],
  "model": "inherit",
  "category": "skill",
  "version": "1.0.0"
}
```

- [ ] **Step 3: Create references/classification-matrix.md**

Write to `plugin/d2c-operations-lead/skills/cs-triage/references/classification-matrix.md`:

```markdown
# CS Triage — Classification Matrix

## Category Signals

| Category | Signal Words/Patterns | Response Action | Escalation |
|----------|----------------------|-----------------|------------|
| shipping-status | "where is my order", "tracking", "when will it arrive", "shipping update" | Tracking lookup + ETA | None |
| order-issue | "wrong item", "damaged", "broken", "missing", "incorrect" | Apology + resolution options | `general-manager` reviews |
| product-question | "what is", "how to use", "difference between", "recommend" | Product knowledge response | None |
| return-request | "return", "refund", "exchange", "send back" | Acknowledge + return policy | `general-manager` reviews |
| wholesale-inquiry | "wholesale", "bulk order", "reseller", "B2B", amount >$500 | Acknowledge + escalate | `general-manager` directly |
| brand-sensitive | Brand-specific signal words configured per store | DO NOT DRAFT | `brand-specialist` |
| complaint | negative tone, "disappointed", "unacceptable", "terrible" | Empathetic + priority flag | `general-manager` priority |

## Response Templates

### Greeting
Dear [First Name],

Thank you for reaching out.

### Shipping Status
We've looked into your order #[ORDER] and here's the latest:
[tracking info / ETA]

If you have any other questions, we're here to help.

### Order Issue
We're sorry to hear about this experience with your order. We take great care in preparing each item, and we want to make this right.

[Specific response based on issue type]

We'll follow up within [timeframe] with next steps.

### Return Request
We understand. Our return policy allows returns within [N] days of delivery for items in original condition.

To start the process:
1. [return steps]
2. [shipping instructions]

We'll process your [refund/exchange] within [timeframe] of receiving the item.

### Product Question
Great question! [Product name] is [description per brand guidelines].

[Specific answer]

If you'd like more guidance on choosing the right [product type], we're happy to help.

### Wholesale Inquiry
Thank you for your interest in carrying our products. We'd love to explore this with you.

Our team will be in touch within [timeframe] to discuss your needs.
```

- [ ] **Step 4: Commit**

```bash
cd ~/code/active/tibetan-spirit-ops
git add plugin/d2c-operations-lead/skills/cs-triage/
git commit -m "feat(d2c-operations-lead): add generalized cs-triage skill"
```

---

### Task 3: Generalize cs-pipeline

**Files:**
- Create: `plugin/d2c-operations-lead/skills/cs-pipeline/SKILL.md`
- Create: `plugin/d2c-operations-lead/skills/cs-pipeline/metadata.json`

- [ ] **Step 1: Create SKILL.md**

Write to `plugin/d2c-operations-lead/skills/cs-pipeline/SKILL.md`:

```markdown
---
name: cs-pipeline
description: Use when customer service emails need end-to-end processing — triage, enrichment, drafting, and approval queuing in sequence.
---

<HARD-GATE>
Every email MUST pass through triage classification before any draft is created. Brand-sensitive emails are escalated at triage — they never reach the drafting stage. Skipping triage produces unclassified drafts that bypass the escalation and compliance gates.
</HARD-GATE>

# CS Email Pipeline

## Overview

Orchestrates the full customer service email workflow: triage → enrichment → draft → approval queue. Each stage has its own gate — an email only advances when the prior stage passes.

## When to Use

**Invoke when:**
- A batch of unread customer emails needs processing
- `general-manager` says "run CS pipeline" or "process customer emails"
- CS drafter needs upstream triage and enrichment before drafting

**Do NOT use for:**
- A single already-classified email (use cs-drafter directly)
- Internal team communications
- Emails already in the approval queue

## Workflow

1. **Scan** — Query email for unread external customer emails. Exclude internal domains. Build the processing queue.
2. **Triage** — For each email, invoke `cs-triage` skill. Classify into one of 7 categories. Brand-sensitive emails stop here and escalate to `brand-specialist`. Complaints get priority ordering.
3. **Enrich** — For emails that passed triage, query the database for order/product context. Check email for prior threads with the same customer. Attach enrichment data to the email record.
4. **Draft** — For each enriched email, create a draft response. Apply brand voice rules. Log with `"ai_generated": true`.
5. **Queue** — Present the batch summary to `general-manager` for approval. Each draft shows: category, customer, subject, enrichment data used, and the draft itself.

**Stage gates:**

| Gate | Condition to advance | Failure action |
|------|---------------------|----------------|
| Triage → Enrich | Category assigned, not `brand-sensitive` | Escalate to `brand-specialist` |
| Enrich → Draft | Enrichment data attached (even if empty) | Flag for manual review |
| Draft → Queue | Draft passes Verification checklist | Hold for revision |

## Common Rationalizations

| Rationalization | Reality |
|----------------|---------|
| "I know the category already, I'll skip triage" | Triage catches brand-sensitive escalations. Skipping it is a compliance gap. |
| "No enrichment data found, so I'll draft without it" | Attach the empty enrichment record — the drafter needs to know the lookup happened. |
| "Customer is waiting, I'll send this one directly" | Every draft goes through the queue. Compliance requires human approval. |

## Red Flags

- Drafting before triage completes
- Brand-sensitive emails reaching the draft stage
- Sending any email without human approval
- Skipping enrichment because "the email is straightforward"
- Processing internal team emails through the pipeline

## Verification

- [ ] All emails triaged before any drafting begins
- [ ] Brand-sensitive emails escalated, not drafted
- [ ] Enrichment data attached to every email record (even if no data found)
- [ ] All drafts have `"ai_generated": true` in log
- [ ] Batch summary presented for `general-manager` review
- [ ] No emails sent — drafts only, queued for approval
```

- [ ] **Step 2: Create metadata.json**

Write to `plugin/d2c-operations-lead/skills/cs-pipeline/metadata.json`:

```json
{
  "name": "cs-pipeline",
  "description": "End-to-end customer service email pipeline: triage → enrichment → draft → approval queue.",
  "domain": "customer-service",
  "triggers": ["run CS pipeline", "process customer emails", "CS email batch", "triage and draft"],
  "model": "inherit",
  "category": "workflow",
  "version": "1.0.0"
}
```

- [ ] **Step 3: Commit**

```bash
cd ~/code/active/tibetan-spirit-ops
git add plugin/d2c-operations-lead/skills/cs-pipeline/
git commit -m "feat(d2c-operations-lead): add generalized cs-pipeline workflow"
```

---

### Task 4: Generalize shopify-query

**Files:**
- Create: `plugin/d2c-operations-lead/skills/shopify-query/SKILL.md`
- Create: `plugin/d2c-operations-lead/skills/shopify-query/metadata.json`
- Create: `plugin/d2c-operations-lead/skills/shopify-query/references/query-patterns.md`

- [ ] **Step 1: Create SKILL.md**

Write to `plugin/d2c-operations-lead/skills/shopify-query/SKILL.md`:

```markdown
---
name: shopify-query
description: Use when an agent needs real-time Shopify data not yet synced to the database, or a specific lookup by order number, SKU, or customer email.
---

# Shopify Query

## Overview

Queries your Shopify store for real-time data when agents need fresh data not yet synced to the database.

## When to Use

- Specific order lookup for CS enrichment (freshest data)
- Product search by SKU/name against live catalog
- Real-time low stock check
- Customer info for CS enrichment
- **Do NOT use for:** aggregate reports (use database), bulk data sync (use backfill scripts), write operations (not supported)

## Workflow

1. Determine query type (order, product, inventory, recent-orders, customer)
2. Run the appropriate query from `references/query-patterns.md`
3. Parse JSON response; handle `{"error": "..."}` if present
4. Log any customer data access with purpose (compliance)

| Need | Use |
|------|-----|
| Aggregate reports, P&L, margins | Database (orders, products tables) |
| Specific order lookup (CS) | This skill — freshest data |
| Product search by SKU/name | This skill for live catalog |
| Real-time low stock | This skill |
| Customer info (CS enrichment) | This skill |
| Bulk data (full catalog) | Backfill script → database |

## Common Rationalizations

| Rationalization | Reality |
|----------------|---------|
| "The database has this data, I'll use that for CS" | Database may lag 24h. For CS enrichment, use this skill. |
| "I'll query all orders to be thorough" | Always use date filters. Bulk queries belong in backfill script. |

## Red Flags

- Exposing API credentials in any output
- Bulk operations without date filters
- Using this for aggregate reporting (use database)
- Storing customer PII outside draft/log context

## Verification

- [ ] Credentials not logged or exposed
- [ ] Date filter applied for order queries
- [ ] Customer data access logged with purpose (compliance)
- [ ] Output is JSON; error field handled before proceeding
```

- [ ] **Step 2: Create metadata.json**

Write to `plugin/d2c-operations-lead/skills/shopify-query/metadata.json`:

```json
{
  "name": "shopify-query",
  "description": "Real-time Shopify data queries for agent workflows.",
  "domain": "operations",
  "triggers": ["look up order", "check inventory", "shopify query", "find product", "customer lookup"],
  "model": "inherit",
  "category": "skill",
  "version": "1.0.0"
}
```

- [ ] **Step 3: Create references/query-patterns.md**

Write to `plugin/d2c-operations-lead/skills/shopify-query/references/query-patterns.md`:

```markdown
# Shopify Query — Command Reference

All queries use the Shopify GraphQL Admin API. Configure your store URL and access token in environment variables.

## Query Types

### Order Lookup
Look up a specific order by order number. Returns: order details, line items, shipping address, fulfillment + tracking info, customer email.

### Product Search
Search active products by SKU (exact) or title (substring). Returns matches with price, stock, type.

### Inventory Check
List products sorted by stock level. Optionally filter to items below a threshold.

### Recent Orders
Returns orders from last N days with revenue total and per-order summary. Always use date filters.

### Customer Lookup
Look up customer by email. Returns: name, order count, total spent, tags, address. For CS enrichment only — never export PII.

## Constraints
- **Read-only.** NEVER modifies Shopify data.
- **Rate limits:** Respect Shopify's GraphQL cost-based rate limits (1,000-point bucket, 50 points/sec refill). Keep queries under 100 points — limit page sizes to 50 items, max 2 nesting levels.
- **Credentials:** Read from environment variables. Never expose in output.
```

- [ ] **Step 4: Commit**

```bash
cd ~/code/active/tibetan-spirit-ops
git add plugin/d2c-operations-lead/skills/shopify-query/
git commit -m "feat(d2c-operations-lead): add generalized shopify-query skill"
```

---

### Task 5: Generalize order-inquiry

**Files:**
- Create: `plugin/d2c-operations-lead/skills/order-inquiry/SKILL.md`
- Create: `plugin/d2c-operations-lead/skills/order-inquiry/metadata.json`
- Create: `plugin/d2c-operations-lead/skills/order-inquiry/references/status-mapping.md`

- [ ] **Step 1: Create SKILL.md**

Write to `plugin/d2c-operations-lead/skills/order-inquiry/SKILL.md`:

```markdown
---
name: order-inquiry
description: Use when a customer asks about order status, tracking, delivery timeline, or has concerns about a delayed shipment.
---

# CS Order Inquiry

## Overview

Resolves customer questions about order status, tracking, and delivery by querying live order data and translating internal fulfillment states into customer-friendly language.

## When to Use

- **Invoke when:** Customer asks where their order is, requests a tracking number, questions a delivery estimate, or expresses concern about a delay
- **Do NOT use for:** Returns, cancellations, product questions, or complaints unrelated to shipment status — route those through cs-triage first

## Workflow

1. **Identify the order** — Locate via order number (preferred), confirmation email, or name + purchase date. If multiple matches exist, confirm with customer before proceeding.

2. **Query order status** — Pull from database first; fall back to Shopify GraphQL API for real-time state. Map internal status to customer-facing language per `references/status-mapping.md`.

3. **Handle special cases** — Long-lead-time items (international sourcing), marketplace-fulfilled orders (e.g., FBA), delayed orders (>7 biz days domestic, >21 international), or order not found. See `references/status-mapping.md`.

4. **Draft the response** — Apply brand voice: warm, informative, authentic. Acknowledge any delay directly before offering next steps. Never use urgency language.

5. **Queue for human review** — All drafts go to the CS queue. Compliance requires human approval before sending. Log with `"ai_generated": true`.

## Common Rationalizations

| Rationalization | Reality |
|----------------|---------|
| "I'll estimate delivery from the ship date" | Never guess. Pull actual carrier data or state it's unavailable. |
| "The delay is minor, I won't mention it" | Acknowledge delays directly. Customers who discover it themselves lose trust. |
| "We have no record of this order" | Never say this. Ask the customer to check their confirmation email first. |
| "Marketplace-fulfilled orders work the same way" | They don't. Marketplace fulfillment and tracking data comes from the marketplace, not Shopify. |

## Red Flags

- Sending any response without human review (compliance violation)
- Guessing a delivery date when carrier data is unavailable
- Using "we have no record" language before exhausting lookup options
- Skipping the sourcing context explanation when it's relevant
- Missing `"ai_generated": true` in the log entry

## Verification

- [ ] Order located via at least one identifier (order number, email, name+date)
- [ ] Status pulled from database or Shopify fallback
- [ ] Customer-facing status uses mapped language (not internal enum)
- [ ] Special case rules applied if long-lead, marketplace-fulfilled, delayed, or not found
- [ ] Response acknowledges delay before offering resolution (if applicable)
- [ ] No urgency language, no guessed delivery dates
- [ ] Draft queued in CS queue, not sent
- [ ] Log entry includes `"ai_generated": true`
```

- [ ] **Step 2: Create metadata.json**

Write to `plugin/d2c-operations-lead/skills/order-inquiry/metadata.json`:

```json
{
  "name": "order-inquiry",
  "description": "Handles order status, tracking, and delivery questions — the most common CS inquiry type (~40% of tickets).",
  "domain": "customer-service",
  "triggers": ["where is my order", "order status", "tracking number", "delivery estimate", "delayed shipment"],
  "model": "inherit",
  "category": "skill",
  "version": "1.0.0"
}
```

- [ ] **Step 3: Create references/status-mapping.md**

Write to `plugin/d2c-operations-lead/skills/order-inquiry/references/status-mapping.md`:

```markdown
# Order Status Mapping

Reference for Steps 2 and 3 of the order-inquiry workflow.

## Internal → Customer-Facing Status

| Internal Status | Customer-Facing Language | Notes |
|----------------|--------------------------|-------|
| `unfulfilled` | "Being Prepared" | Order received, not yet picked/packed |
| `partially_fulfilled` | "Partially Shipped" | Some items shipped, remainder still processing |
| `fulfilled` (no tracking) | "Shipped" | Fulfillment confirmed but carrier scan not yet available |
| `fulfilled` + tracking URL | "On Its Way" | Include tracking link in response |
| `fulfilled` + delivered event | "Delivered" | Confirm delivery date from carrier |

## Special Cases

### Long-Lead-Time Items (International Sourcing)
Items sourced from international artisan partners may carry extended lead times before fulfillment. When a customer inquires:
- Explain the sourcing context positively — these items are crafted by skilled artisans
- Provide the expected fulfillment window (not a delivery date)
- Do not apologize for the lead time; frame it as part of the item's provenance

### Marketplace-Fulfilled Orders (e.g., FBA)
Orders fulfilled through marketplaces (Amazon FBA, etc.) are tracked through the marketplace, not Shopify. Shopify fulfillment status will not reflect the true state.
- Do not use Shopify tracking data for marketplace-fulfilled orders
- Direct the customer to their marketplace order confirmation for tracking
- If the customer purchased on your site but the order routes to marketplace fulfillment, explain this clearly

### Delayed Orders
A shipment is considered delayed when:
- **Domestic:** No delivery scan within 7 business days of ship date
- **International:** No delivery scan within 21 business days of ship date

When a delay is confirmed:
1. Acknowledge the delay directly in the first sentence — do not bury it
2. State what is known (last carrier scan, current location if available)
3. Offer a concrete next step: carrier investigation request, replacement, or refund
4. Escalate to `operations-manager` if a carrier claim needs to be filed

### Order Not Found
When no order matches the customer's provided information:
- **Never say** "we have no record of that order"
- Ask the customer to locate their original confirmation email
- Try alternate lookups: different email address, guest vs. account order, potential typo in order number
- If still unresolved after two attempts, escalate for manual investigation
```

- [ ] **Step 4: Commit**

```bash
cd ~/code/active/tibetan-spirit-ops
git add plugin/d2c-operations-lead/skills/order-inquiry/
git commit -m "feat(d2c-operations-lead): add generalized order-inquiry skill"
```

---

### Task 6: Generalize fulfillment-flag

**Files:**
- Create: `plugin/d2c-operations-lead/skills/fulfillment-flag/SKILL.md`
- Create: `plugin/d2c-operations-lead/skills/fulfillment-flag/metadata.json`
- Create: `plugin/d2c-operations-lead/skills/fulfillment-flag/references/decision-table.md`

- [ ] **Step 1: Create SKILL.md**

Write to `plugin/d2c-operations-lead/skills/fulfillment-flag/SKILL.md`:

```markdown
---
name: fulfillment-flag
description: Use when orders need exception flagging, fulfillment routing review, or shipping anomalies require team coordination.
---

# Fulfillment Flag

## Overview

Identifies fulfillment exceptions and routes them to the correct team member before a problem compounds. A delayed shipment is always better than a mis-routed one.

## When to Use

- **Invoke when:** An order is unfulfilled beyond threshold, tracking is missing after ship date, address validation fails, routing is ambiguous, or inventory counts conflict
- **Do NOT use for:** Standard order flow, routine fulfillment updates, or Shopify order modification (write operations require human approval)

## Workflow

1. **Evaluate the trigger** — Identify the exception type from the decision table in `references/decision-table.md`
2. **Investigate before escalating** — Check the order in Shopify and warehouse systems; international supplier delays often have infrastructure causes, not neglect
3. **Draft the flag** — Write the exception summary with order ID, trigger condition, and recommended action
4. **Route to the correct person** — Use the decision table to select the role and channel; use the team member's configured language and register
5. **Queue to comms file** — Append to the fulfillment communications queue with `"ai_generated": true`; never send directly

See `references/decision-table.md` for exception routing table and carrier rules.

## Common Rationalizations

| Rationalization | Reality |
|----------------|---------|
| "I'll auto-route the mixed domestic/international order to save time" | NEVER auto-route mixed orders — flag for manual review every time |
| "The international supplier is just a few days late, I'll wait" | Surface to `general-manager` before the deadline passes; investigate first, but don't absorb the delay silently |
| "Shopify says we have stock, so we're fine" | Trust the physical count when it conflicts; Shopify can be stale |
| "I'll send the flag directly to the team" | Queue to the communications file; never send directly |

## Red Flags

- Routing an order without flagging when routing is ambiguous
- Auto-routing an order with both domestic and international components
- Escalating a supplier delay without first investigating infrastructure causes
- Using incorrect language or register for team communications
- Writing to the comms queue without `"ai_generated": true`
- Flagging with Shopify inventory data when physical count is available and conflicts

## Verification

- [ ] Exception type identified from decision table
- [ ] Investigation completed before escalation (no assumption of negligence)
- [ ] Correct role, channel, and language used per decision table
- [ ] Mixed domestic/international orders flagged for manual review — not auto-routed
- [ ] Flag queued to communications file, not sent
- [ ] `"ai_generated": true` included in queue entry
- [ ] Carrier and packaging rules checked for relevant orders
```

- [ ] **Step 2: Create metadata.json**

Write to `plugin/d2c-operations-lead/skills/fulfillment-flag/metadata.json`:

```json
{
  "name": "fulfillment-flag",
  "description": "Exception flagging and routing review for fulfillment pipeline — surfaces problems before they become crises.",
  "domain": "fulfillment",
  "triggers": ["fulfillment exception", "shipping anomaly", "order routing", "delayed shipment", "address issue"],
  "model": "inherit",
  "category": "skill",
  "version": "1.0.0"
}
```

- [ ] **Step 3: Create references/decision-table.md**

Write to `plugin/d2c-operations-lead/skills/fulfillment-flag/references/decision-table.md`:

```markdown
# Fulfillment Decision Table

## Exception Routing

| Condition | Route To | Channel | Notes |
|-----------|----------|---------|-------|
| Unfulfilled >24h | `operations-manager` | Dashboard/chat | Standard ops escalation |
| Missing tracking after ship date | `warehouse-manager` | Dashboard | Warehouse investigation |
| Domestic + international components | Manual review flag | Dashboard | NEVER auto-route |
| International supplier deadline <7 days | `general-manager` | Chat/Slack | Strategic decision |
| Address validation failure | `operations-manager` (hold order) | Dashboard | Hold until resolved |
| Inventory conflict (Shopify vs warehouse) | `warehouse-manager` (trust physical count) | Dashboard | Physical count wins |
| Regional/international shipping address | `regional-fulfillment` | Email | Regional team handles |

## Carrier Rules (flag when violated)

Configure per your shipping setup. Common patterns:

- Light packages (<1 lb): economy carrier (e.g., USPS)
- Heavy or fragile items: premium carrier with handling (e.g., UPS)
- International: international carrier (e.g., DHL)
- Fragile/high-value items: custom packaging + insurance required
- Oversized items: special shipping method required

Document your product-specific carrier rules in this file when configuring the plugin.
```

- [ ] **Step 4: Commit**

```bash
cd ~/code/active/tibetan-spirit-ops
git add plugin/d2c-operations-lead/skills/fulfillment-flag/
git commit -m "feat(d2c-operations-lead): add generalized fulfillment-flag skill"
```

---

### Task 7: Generalize margin-reporting

**Files:**
- Create: `plugin/d2c-operations-lead/skills/margin-reporting/SKILL.md`
- Create: `plugin/d2c-operations-lead/skills/margin-reporting/metadata.json`
- Create: `plugin/d2c-operations-lead/skills/margin-reporting/references/queries.md`

- [ ] **Step 1: Create SKILL.md**

Write to `plugin/d2c-operations-lead/skills/margin-reporting/SKILL.md`:

```markdown
---
name: margin-reporting
description: Use when the weekly margin report is due, an ad-hoc margin review is requested, or below-floor alerts need investigation.
---

# Margin Reporting

## Overview

Generates weekly and ad-hoc margin reports with SKU-level profitability, channel comparisons, trend indicators, and below-floor alerts. Read-only — never modifies financial records.

## When to Use

- **Invoke when:** weekly P&L is due, `general-manager` requests a margin review, a below-floor alert needs investigation, or channel profitability needs comparison
- **Do NOT use for:** modifying COGS records, updating pricing, or any write operation on financial data

## Workflow

1. **Query SKU margins** — run SKU-level margin query; label COGS confidence on every row (confirmed vs. estimated)
2. **Query channel rollup** — run channel profitability query; compute trend arrows per channel (▲ ≥+2pp, ▼ ≥−2pp, ─ <2pp)
3. **Run category rollup** — aggregate SKU margins by category; flag any category average below floor
4. **Identify below-floor alerts** — flag all SKUs where `margin < channel_floor`; mark negative-margin rows as URGENT
5. **Check charitable/mission allocations** — if the brand has a charitable allocation (e.g., % of revenue to a cause), confirm it appears as an accounting expense, not a marketing line
6. **Assemble report sections** — Executive Summary → By Category → By Channel → Below-Floor Alerts → Action Items (see `references/queries.md` for full template)
7. **Write output** — save to the finance reports file; log run with `"ai_generated": true`

See `references/queries.md` for SQL query patterns and the full report template.

## Common Rationalizations

| Rationalization | Reality |
|----------------|---------|
| "COGS is probably close enough to skip the label" | Every estimate must be labeled. Unlabeled numbers imply confirmed data. |
| "The variance is small, I'll smooth it over" | Surface all anomalies. A $50 gap today can be $5,000 next quarter. |
| "The charitable allocation lowers apparent margin, I'll exclude it" | It is a real expense. Include it with its accounting label — never omit. |
| "This channel is below floor but volume is tiny" | Floor violations are flagged regardless of volume. `general-manager` decides what to do. |

## Red Flags

- Any COGS row presented without a confidence label (confirmed / estimated)
- Negative-margin SKU not marked URGENT
- Charitable allocation appearing in a marketing or promotion line
- Log entry missing `"ai_generated": true`
- Financial data modified (this skill is read-only)

## Verification

- [ ] All COGS rows labeled: confirmed or estimated
- [ ] Trend arrows applied to all channel rows (▲ / ▼ / ─)
- [ ] Every SKU with margin < channel floor appears in Below-Floor Alerts
- [ ] Negative-margin SKUs marked URGENT
- [ ] Charitable/mission allocation is an accounting expense line, not marketing
- [ ] Run logged with `"ai_generated": true`
- [ ] No financial records modified
```

- [ ] **Step 2: Create metadata.json**

Write to `plugin/d2c-operations-lead/skills/margin-reporting/metadata.json`:

```json
{
  "name": "margin-reporting",
  "description": "Weekly margin report with SKU-level profitability, channel comparison, trend indicators, and below-floor alerts.",
  "domain": "finance",
  "triggers": ["margin report", "weekly P&L", "profitability analysis", "below-floor alert", "channel margins"],
  "model": "inherit",
  "category": "skill",
  "version": "1.0.0"
}
```

- [ ] **Step 3: Create references/queries.md**

Write to `plugin/d2c-operations-lead/skills/margin-reporting/references/queries.md`:

```markdown
# Margin Reporting — Query Patterns & Report Template

## SQL Query Patterns

Adapt these to your database schema. The queries assume materialized views for SKU margins and channel profitability.

### 1. SKU-Level Margins

```sql
SELECT
  sku,
  product_title,
  category,
  channel,
  revenue_net,
  cogs_total,
  gross_margin_pct,
  cogs_confidence,          -- 'confirmed' | 'estimated'
  margin_floor_pct,
  (gross_margin_pct < margin_floor_pct) AS below_floor,
  (gross_margin_pct < 0)                AS negative_margin
FROM product_margin_detail
WHERE period_start = date_trunc('week', current_date - interval '7 days')
ORDER BY gross_margin_pct ASC;
```

### 2. Channel Profitability Rollup

```sql
SELECT
  channel,
  period_month,
  total_revenue_net,
  total_cogs,
  gross_margin_pct,
  LAG(gross_margin_pct) OVER (PARTITION BY channel ORDER BY period_month) AS prior_margin_pct,
  (gross_margin_pct - LAG(gross_margin_pct) OVER (PARTITION BY channel ORDER BY period_month)) AS margin_delta_pp
FROM channel_profitability_monthly
WHERE period_month >= date_trunc('month', current_date - interval '3 months')
ORDER BY channel, period_month;
```

### 3. Category Rollup

```sql
SELECT
  category,
  COUNT(DISTINCT sku) AS sku_count,
  SUM(revenue_net) AS category_revenue,
  SUM(cogs_total) AS category_cogs,
  ROUND(
    (SUM(revenue_net) - SUM(cogs_total)) / NULLIF(SUM(revenue_net), 0) * 100, 1
  ) AS category_margin_pct,
  BOOL_OR(cogs_confidence = 'estimated') AS has_estimated_cogs,
  COUNT(*) FILTER (WHERE gross_margin_pct < margin_floor_pct) AS below_floor_count
FROM product_margin_detail
WHERE period_start = date_trunc('week', current_date - interval '7 days')
GROUP BY category
ORDER BY category_margin_pct ASC;
```

### 4. Below-Floor Alert Query

```sql
SELECT
  sku, product_title, category, channel,
  gross_margin_pct, margin_floor_pct,
  (gross_margin_pct - margin_floor_pct) AS gap_pp,
  cogs_confidence,
  CASE
    WHEN gross_margin_pct < 0 THEN 'URGENT — negative margin'
    ELSE 'ALERT — below floor'
  END AS alert_level
FROM product_margin_detail
WHERE period_start = date_trunc('week', current_date - interval '7 days')
  AND gross_margin_pct < margin_floor_pct
ORDER BY gross_margin_pct ASC;
```

---

## Trend Arrow Logic

| Condition | Arrow |
|-----------|-------|
| `margin_delta_pp >= 2.0` | ▲ |
| `margin_delta_pp <= -2.0` | ▼ |
| `-2.0 < margin_delta_pp < 2.0` | ─ |

---

## Report Template

```
{BRAND_NAME} — WEEKLY MARGIN REPORT
Week ending: {YYYY-MM-DD}
Generated: {timestamp} | ai_generated: true

═══════════════════════════════════════
EXECUTIVE SUMMARY
═══════════════════════════════════════
Overall gross margin:  {X.X}%  {trend arrow}  (prior week: {X.X}%)
Revenue (net):         ${X,XXX}
COGS coverage:         {X} confirmed SKUs / {X} estimated SKUs
Below-floor alerts:    {N} SKUs  ({N} URGENT)
Anomalies flagged:     {N}

═══════════════════════════════════════
BY CATEGORY
═══════════════════════════════════════
{category}             {X.X}%  {trend arrow}  [{confirmed|estimated*}]
  └─ {N} SKUs | Revenue: ${X,XXX} | Below-floor: {N}
...

═══════════════════════════════════════
BY CHANNEL
═══════════════════════════════════════
{channel}              {X.X}%  {trend arrow}
  Revenue: ${X,XXX} | Floor: {X.X}% | Gap to floor: {+/−X.X}pp
...

═══════════════════════════════════════
BELOW-FLOOR ALERTS
═══════════════════════════════════════
[URGENT — negative margin]
  SKU: {sku} | {product_title}
  Channel: {channel} | Category: {category}
  Margin: {X.X}% | Floor: {X.X}% | Gap: {−X.X}pp
  COGS: {confirmed|estimated}

═══════════════════════════════════════
ACTION ITEMS
═══════════════════════════════════════
[ ] {Specific action derived from alerts or anomalies}

═══════════════════════════════════════
DATA QUALITY NOTES
═══════════════════════════════════════
- Estimated COGS rows: {N}
- Anomalies requiring investigation: {descriptions}
- Missing data: {any gaps noted}
```
```

- [ ] **Step 4: Commit**

```bash
cd ~/code/active/tibetan-spirit-ops
git add plugin/d2c-operations-lead/skills/margin-reporting/
git commit -m "feat(d2c-operations-lead): add generalized margin-reporting skill"
```

---

### Task 8: Generalize campaign-brief

**Files:**
- Create: `plugin/d2c-operations-lead/skills/campaign-brief/SKILL.md`
- Create: `plugin/d2c-operations-lead/skills/campaign-brief/metadata.json`
- Create: `plugin/d2c-operations-lead/skills/campaign-brief/references/brief-template.md`

- [ ] **Step 1: Create SKILL.md**

Write to `plugin/d2c-operations-lead/skills/campaign-brief/SKILL.md`:

```markdown
---
name: campaign-brief
description: Use when a marketing campaign needs a structured brief, content calendar entry, or seasonal promotion plan for review.
---

# Campaign Brief

## Overview

Generates a structured campaign brief for D2C marketing initiatives, classifying content by tier and enforcing frequency caps before anything reaches `general-manager` for approval. Output is queued, never scheduled.

## When to Use

- **Invoke when:** a marketing initiative, seasonal event, or content calendar entry needs a formal brief for review
- **Do NOT use for:** transactional emails (order confirmations, shipping notices — these are Tier 1, no brief needed), customer service responses, product descriptions

## Workflow

1. **Classify tier** — Apply the Content Tier Framework below. If uncertain, escalate to Tier 3. Tier 4 is blocked; stop immediately and explain why.
2. **Check frequency caps** — Verify promotional email count and ad impression caps before drafting. If caps are at limit, do not draft — flag to `general-manager`.
3. **Check seasonal context** — For culturally or brand-significant events: approach with appropriate reverence and tone. Flag if the brief risks commercial momentum overriding significance.
4. **Draft the brief** — Use the format in `references/brief-template.md`.
5. **Verify compliance** — Run the Verification checklist before outputting.
6. **Queue output** — Write to the marketing briefs queue with `"ai_generated": true`. Never publish or schedule.

### Content Tier Framework

| Tier | Content Type | Approval Required |
|------|-------------|-------------------|
| Tier 1 | Transactional only (confirmations, shipping) | None — auto-publish |
| Tier 2 | All marketing content | `general-manager` approval |
| Tier 3 | Content touching brand values or cultural significance | `brand-specialist` review, then `general-manager` |
| Tier 4 | Urgency/scarcity tactics, unsubstantiated claims | BLOCKED — never use |

### Default Frequency Caps

| Channel | Cap | Notes |
|---------|-----|-------|
| Promotional emails | Configurable (suggest ≤2/month) | Not sending is sometimes the correct decision |
| Ad impressions | Configurable (suggest ≤3/user/week) | Frequency fatigue degrades brand trust |
| SMS | Not recommended for premium brands | Consider brand positioning before enabling |

## Common Rationalizations

| Rationalization | Reality |
|----------------|---------|
| "This is educational content, not promotional" | If it drives traffic to a product, it is Tier 2 minimum. Classify honestly. |
| "Our charitable mission makes this mission-driven, not marketing" | Charitable allocations are accounting lines, never campaign angles. |
| "We're just one email over the cap — it's a soft limit" | The cap is hard. Not sending is sometimes the correct decision. |
| "This seasonal event creates urgency" | Urgency language is Tier 4. Seasonal significance is Tier 2/3. |

## Red Flags

- Any urgency, scarcity, or countdown language in draft copy (Tier 4 — block)
- Unsubstantiated benefit claims
- Charitable/mission commitments mentioned as a reason to purchase
- Brief produced without checking frequency caps
- Tier 3 content missing `brand-specialist` review note

## Verification

- [ ] Content tier classified correctly (Tier 4 = blocked, not queued)
- [ ] Frequency caps verified before drafting
- [ ] "What This Campaign Does NOT Do" section is substantive, not boilerplate
- [ ] No prohibited tactics (urgency, scarcity, FOMO, unsubstantiated claims)
- [ ] Charitable allocation not present in any customer-facing copy
- [ ] Tier 3 brief flagged for `brand-specialist` review before `general-manager`
- [ ] Output written to marketing briefs queue with `"ai_generated": true`
```

- [ ] **Step 2: Create metadata.json**

Write to `plugin/d2c-operations-lead/skills/campaign-brief/metadata.json`:

```json
{
  "name": "campaign-brief",
  "description": "Structured campaign brief generator with content tier classification and frequency cap enforcement.",
  "domain": "marketing",
  "triggers": ["campaign brief", "marketing plan", "content calendar", "seasonal promotion", "campaign draft"],
  "model": "inherit",
  "category": "skill",
  "version": "1.0.0"
}
```

- [ ] **Step 3: Create references/brief-template.md**

Write to `plugin/d2c-operations-lead/skills/campaign-brief/references/brief-template.md`:

```markdown
# Campaign Brief Template

```
# Campaign Brief: [Name]
**Objective:** [single sentence]
**Timing:** [dates]
**Audience:** [segment]
**Tier:** [2 or 3]
## Core Message
## Channels
## Content Requirements
## What This Campaign Does NOT Do
```

Do not invent fields or omit sections. The "What This Campaign Does NOT Do" section must contain substantive constraints, not boilerplate.
```

- [ ] **Step 4: Commit**

```bash
cd ~/code/active/tibetan-spirit-ops
git add plugin/d2c-operations-lead/skills/campaign-brief/
git commit -m "feat(d2c-operations-lead): add generalized campaign-brief skill"
```

---

### Task 9: Generalize restock-calc

**Files:**
- Create: `plugin/d2c-operations-lead/skills/restock-calc/SKILL.md`
- Create: `plugin/d2c-operations-lead/skills/restock-calc/metadata.json`
- Create: `plugin/d2c-operations-lead/skills/restock-calc/references/formulas.md`

- [ ] **Step 1: Create SKILL.md**

Write to `plugin/d2c-operations-lead/skills/restock-calc/SKILL.md`:

```markdown
---
name: restock-calc
description: Use when inventory levels need threshold calculation, restock quantities need computing, or demand-based reorder recommendations are needed.
---

# Restock Calculator

## Overview

Computes reorder points, restock quantities, and safety stock for each SKU using velocity data, lead times, and seasonal demand signals. Produces recommendations only — never makes purchase commitments.

## When to Use

**Invoke when:**
- Calculating whether a SKU has crossed its reorder point
- Computing a recommended order quantity for domestic or international-sourced items
- Determining safety stock for a SKU ahead of a seasonal event
- Validating that an existing recommendation used the correct lead-time tier

**Do NOT use for:**
- Generating the full inventory report (use inventory analyst agent)
- Modifying inventory records or placing orders
- Reconciling Shopify vs. warehouse counts (inventory analyst owns that)

## Workflow

1. **Identify data source** — Query inventory table via database; fall back to local snapshot file. Label every figure: confirmed or estimated.
2. **Calculate daily velocity** — 30-day avg daily sales from orders table. Adjust for upcoming seasonal events.
3. **Compute reorder point, safety stock, and restock quantity** — Apply formulas from `references/formulas.md`. Flag immediately if a top-20 SKU is below critical alert threshold.
4. **Flag overstock** — Apply overstock threshold from `references/formulas.md`.
5. **Write output** — Append to restock recommendations file with confidence labels and data source.

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "Daily velocity is roughly known, I'll skip the label" | Every figure needs explicit confidence label — confirmed or estimated. |
| "The international lead time is probably shorter this time" | Use conservative lead time estimates. Never assume a faster timeline. |
| "Low-margin SKU, I'll skip the safety stock calc" | If it serves a customer need, compute it regardless of margin. |
| "Marketplace fields aren't in the snapshot, I'll use on-hand only" | Note the missing fields explicitly; do not silently ignore them. |

## Red Flags

- Computing reorder quantity without checking sourcing tier (domestic vs. international)
- Omitting confidence label on any figure
- Using Shopify count when it conflicts with warehouse count
- Implying a purchase commitment in the output
- Skipping safety stock for a SKU because volume is low

## Verification

- [ ] Data source labeled: database (confirmed) or snapshot (estimated)
- [ ] Daily velocity uses 30-day avg from orders table
- [ ] Reorder point = velocity × 14 (velocity × 7 for top-20 SKUs)
- [ ] Safety stock = max(velocity × 6, 2 units)
- [ ] International-sourced items use 90-day quantity with conservative lead time
- [ ] Marketplace-specific fields checked when available
- [ ] Overstock threshold applied: >180 days supply, no active promotion
- [ ] No purchase commitment language in output
```

- [ ] **Step 2: Create metadata.json**

Write to `plugin/d2c-operations-lead/skills/restock-calc/metadata.json`:

```json
{
  "name": "restock-calc",
  "description": "Threshold calculation and restock quantity recommendations based on velocity, lead times, and seasonal demand.",
  "domain": "inventory",
  "triggers": ["restock calculation", "reorder point", "safety stock", "lead time planning", "demand forecast"],
  "model": "inherit",
  "category": "skill",
  "version": "1.0.0"
}
```

- [ ] **Step 3: Create references/formulas.md**

Write to `plugin/d2c-operations-lead/skills/restock-calc/references/formulas.md`:

```markdown
# Restock Formulas & Lead-Time Tiers

## Lead-Time Tiers

| Source | Lead Time | Restock Quantity |
|--------|-----------|-----------------|
| Domestic | 2–4 weeks | velocity × 60 days |
| International-sourced | 8–12 weeks (configure per supplier) | velocity × 90 days |

Use conservative estimate when sourcing tier is uncertain.

## Formulas

- **Reorder point:** velocity × 14 days
- **Critical alert (top-20 SKU):** velocity × 7 days
- **Safety stock:** max(velocity × 6, 2 units)
- **Overstock threshold:** on_hand > velocity × 180 with no active promotion

## Pipeline Adjustments

- Subtract in-transit units from international restock quantity if populated
- Include marketplace-allocated and marketplace-in-transit units in safety stock when present
```

- [ ] **Step 4: Commit**

```bash
cd ~/code/active/tibetan-spirit-ops
git add plugin/d2c-operations-lead/skills/restock-calc/
git commit -m "feat(d2c-operations-lead): add generalized restock-calc skill"
```

---

### Task 10: Generalize description-optimizer

**Files:**
- Create: `plugin/d2c-operations-lead/skills/description-optimizer/SKILL.md`
- Create: `plugin/d2c-operations-lead/skills/description-optimizer/metadata.json`
- Create: `plugin/d2c-operations-lead/skills/description-optimizer/references/rubric.md`

- [ ] **Step 1: Create SKILL.md**

Write to `plugin/d2c-operations-lead/skills/description-optimizer/SKILL.md`:

```markdown
---
name: description-optimizer
description: Use when product descriptions need scoring against the quality rubric, revision through the evaluator-optimizer loop, or cross-channel consistency checking.
---

# Description Optimizer

## Overview

Runs the evaluator-optimizer loop on product descriptions — scoring against the 5-dimension rubric, revising until all dimensions pass, and verifying cross-channel consistency before queuing for review.

## When to Use

**Invoke when:**
- A new product description needs scoring before catalog entry
- An existing description is flagged for quality review
- Cross-channel consistency needs to be verified (Shopify, Etsy, Amazon, etc.)

**Do NOT use for:**
- Descriptions that have already passed review and are live
- Category strategy decisions
- Publishing directly to any channel — output goes to the catalog drafts queue only

## Workflow

1. **Parse structure** — Confirm 6-sentence structure per `references/rubric.md`. Rewrite to spec if missing.
2. **Score all 5 dimensions** — Apply `references/rubric.md`. Record score (1-10) + one-line rationale per dimension.
3. **Gate check** — Any dimension <8 → revise failing dimension(s) only, re-score. Max 3 cycles.
4. **Cross-channel check** — Same brand framing, terminology, and provenance across all sales channels.
5. **Flag uncertain terms** — Brand-specific or cultural terms you're not certain about → flag for `brand-specialist`. Never generate plausible-sounding explanations.
6. **Write to queue** — Append to catalog drafts queue with `"ai_generated": true` and `"rubric_scores"`.

After 3 failed cycles: flag for human review, do not advance.

## Common Rationalizations

| Rationalization | Reality |
|----------------|---------|
| "The score is 7.5 — close enough to advance" | <8 means revise. The threshold is not a suggestion. |
| "Different marketplace shoppers expect different framing" | Cross-channel consistency is non-negotiable. Products tell the same story everywhere. |
| "I'm fairly sure this is the right term" | Uncertainty = flag for `brand-specialist`. Plausible is not accurate. |
| "The SEO keywords will hurt the score but help conversion" | Brand-authentic framing is the SEO strategy. Commercial keywords are a separate failing. |

## Red Flags

- Advancing a description with any dimension score <8
- Using generic commercial keywords instead of brand-authentic terms
- Misrepresenting product category or positioning across channels
- Generating explanations for uncertain terms without verified sourcing
- Writing directly to any sales channel — queue only

## Verification

- [ ] All 5 rubric dimensions scored with numeric score + rationale
- [ ] No dimension below 8
- [ ] 6-sentence structure confirmed (sentence 6 optional)
- [ ] Cross-channel variants use identical brand framing and terminology
- [ ] No brand-prohibited vocabulary
- [ ] Uncertain terms flagged for `brand-specialist` — not explained
- [ ] `"ai_generated": true` in queue entry
- [ ] `"rubric_scores"` object in queue entry
```

- [ ] **Step 2: Create metadata.json**

Write to `plugin/d2c-operations-lead/skills/description-optimizer/metadata.json`:

```json
{
  "name": "description-optimizer",
  "description": "Evaluator-optimizer loop for product descriptions with 5-dimension rubric scoring and cross-channel consistency.",
  "domain": "catalog",
  "triggers": ["description quality", "product copy review", "evaluator-optimizer", "rubric scoring", "cross-channel consistency"],
  "model": "inherit",
  "category": "skill",
  "version": "1.0.0"
}
```

- [ ] **Step 3: Create references/rubric.md**

Write to `plugin/d2c-operations-lead/skills/description-optimizer/references/rubric.md`:

```markdown
# Description Quality Rubric

Reference for the `description-optimizer` skill. All product descriptions must score ≥8/10 on every dimension before advancing to the catalog drafts queue.

---

## Required Structure (150-250 words)

| Sentence | Content |
|----------|---------|
| 1 | What the item IS and what purpose or context it serves (brand-first) |
| 2-3 | Craftsmanship, sourcing, and materials — specific terms required |
| 4-5 | Practical guidance: how to use, care instructions, intended context |
| 6 (optional) | Provenance, artisan story, or sourcing context |

---

## 5-Dimension Rubric

### Dimension 1 — Brand-First Framing
**Criterion:** The description leads with the brand's core value proposition before any material, aesthetic, or commercial detail.

| Score | Meaning |
|-------|---------|
| 10 | Opens with explicit brand context; no generic commercial framing anywhere |
| 8-9 | Opens with brand context; minor commercial language appears later |
| 5-7 | Brand and commercial framing compete; unclear which leads |
| <5 | Description leads with aesthetics, price, or lifestyle framing |

**Test:** Read only the first sentence. Does it tell the customer what makes this product distinctive to your brand? If not, score ≤7.

---

### Dimension 2 — Brand Accuracy
**Criterion:** Brand-specific and category-specific terms are used correctly. No conflation with competitors or generic alternatives.

| Score | Meaning |
|-------|---------|
| 10 | All terms verified; no conflation; brand references are specific and accurate |
| 8-9 | Terms correct; one minor imprecision that does not misrepresent the brand |
| 5-7 | Noticeable conflation or vague brand language |
| <5 | Brand-prohibited vocabulary present, or significant misrepresentation |

**Escalation rule:** When uncertain whether a term is used correctly, flag for `brand-specialist`. Do not generate plausible explanations.

---

### Dimension 3 — SEO Authenticity
**Criterion:** Search terms reflect how your actual customers search — not how generic shoppers search.

| Score | Meaning |
|-------|---------|
| 10 | All search terms are customer-native; no generic commercial keywords |
| 8-9 | Primary terms authentic; one commercial keyword present but not dominant |
| 5-7 | Mixed — commercial and authentic terms compete |
| <5 | Optimized for generic audience, not your customers |

---

### Dimension 4 — Cross-Channel Consistency
**Criterion:** The same product tells the same story on every sales channel. Formatting may differ; meaning and framing must not.

| Score | Meaning |
|-------|---------|
| 10 | Identical brand framing, terminology, and provenance across all channels |
| 8-9 | Consistent framing; minor formatting differences only |
| 5-7 | Channel-specific meaning differences; one channel uses different framing |
| <5 | Product positioned differently across channels |

---

### Dimension 5 — Specificity
**Criterion:** Provenance, maker, and technique are named — not gestured at.

| Score | Meaning |
|-------|---------|
| 10 | Specific maker, region, technique, and material source named and verifiable |
| 8-9 | Specific region or technique named; one element vague but not misleading |
| 5-7 | Generic provenance language without specifics |
| <5 | No provenance; description could apply to any similar product |

---

## Scoring Record Format

Each queue entry must include:

```json
{
  "rubric_scores": {
    "brand_first_framing": 9,
    "brand_accuracy": 8,
    "seo_authenticity": 9,
    "cross_channel_consistency": 10,
    "specificity": 8
  },
  "revision_cycles": 1,
  "flagged_terms": [],
  "ai_generated": true
}
```

If any score is <8, the entry must not appear in the queue. If `flagged_terms` is non-empty, the entry waits for `brand-specialist` review before advancing.
```

- [ ] **Step 4: Commit**

```bash
cd ~/code/active/tibetan-spirit-ops
git add plugin/d2c-operations-lead/skills/description-optimizer/
git commit -m "feat(d2c-operations-lead): add generalized description-optimizer skill"
```

---

### Task 11: Create Symlink + Update public-plugins

**Files:**
- Create: symlink `~/code/public-plugins/d2c-operations-lead` → `~/code/active/tibetan-spirit-ops/plugin/d2c-operations-lead`
- Modify: `~/code/public-plugins/README.md` (already updated in Task 2 rename)

- [ ] **Step 1: Create symlink from public-plugins**

```bash
ln -s /Users/chrismauze/code/active/tibetan-spirit-ops/plugin/d2c-operations-lead /Users/chrismauze/code/public-plugins/d2c-operations-lead
```

- [ ] **Step 2: Verify symlink resolves**

```bash
ls -la /Users/chrismauze/code/public-plugins/d2c-operations-lead
ls /Users/chrismauze/code/public-plugins/d2c-operations-lead/skills/
```

Expected: symlink pointing to tibetan-spirit-ops/plugin/d2c-operations-lead, and 9 skill directories listed.

- [ ] **Step 3: Commit symlink to public-plugins**

```bash
cd ~/code/public-plugins
git add d2c-operations-lead
git commit -m "feat: add d2c-operations-lead symlink to tibetan-spirit-ops/plugin/"
```

- [ ] **Step 4: Commit plugin directory to tibetan-spirit-ops**

```bash
cd ~/code/active/tibetan-spirit-ops
git add plugin/
git commit -m "feat(d2c-operations-lead): complete plugin with 9 generalized D2C skills"
```

---

### Task 12: Validate

- [ ] **Step 1: Verify tibetan-spirit-ops skills/ directory is unchanged**

```bash
cd ~/code/active/tibetan-spirit-ops
git diff HEAD skills/
```

Expected: no output (skills/ was never modified).

- [ ] **Step 2: Verify plugin has all 9 skills**

```bash
ls plugin/d2c-operations-lead/skills/ | sort
```

Expected:
```
campaign-brief
cs-pipeline
cs-triage
description-optimizer
fulfillment-flag
margin-reporting
order-inquiry
restock-calc
shopify-query
```

- [ ] **Step 3: Verify every skill has SKILL.md and metadata.json**

```bash
for skill in campaign-brief cs-pipeline cs-triage description-optimizer fulfillment-flag margin-reporting order-inquiry restock-calc shopify-query; do
  if [ -f plugin/d2c-operations-lead/skills/$skill/SKILL.md ] && [ -f plugin/d2c-operations-lead/skills/$skill/metadata.json ]; then
    echo "OK: $skill"
  else
    echo "MISSING: $skill"
  fi
done
```

Expected: All 9 print "OK".

- [ ] **Step 4: Verify no brand-specific terms leaked into plugin**

```bash
grep -ri "tibetan spirit\|tibetanspirit\|dharma giving\|forest hermitage\|dr\. hun lye\|jothi\|fiona\|omar\|nepal\|bahasa indonesia\|mandarin\|drikung kagyu\|losar\|saga dawa\|vesak\|mala\|thangka\|singing bowl" plugin/d2c-operations-lead/ || echo "CLEAN — no brand-specific terms found"
```

Expected: "CLEAN" — no matches.

- [ ] **Step 5: Verify symlink works from public-plugins**

```bash
ls /Users/chrismauze/code/public-plugins/d2c-operations-lead/skills/ | wc -l
```

Expected: 9

- [ ] **Step 6: Verify plugin.json is valid JSON**

```bash
python3 -c "import json; json.load(open('/Users/chrismauze/code/active/tibetan-spirit-ops/plugin/d2c-operations-lead/.claude-plugin/plugin.json')); print('VALID')"
```

Expected: VALID
