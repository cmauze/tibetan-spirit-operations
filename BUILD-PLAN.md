# Tibetan Spirit AI Ops — Build Plan

## Current State (March 2026)

**Completed in this session:**
- Full folder structure for all 6 agents (~45 skill directories)
- CLAUDE.md project prompt (guides any Claude session working in this repo)
- Shared knowledge layer: brand-guidelines, product-knowledge, channel-config, escalation-matrix, supabase-ops-db
- Priority skills fully drafted: ticket-triage, order-inquiry, fulfillment-domestic, inventory-management, cogs-tracking, reconciliation
- Server scaffolding: server.py (FastAPI + webhook handlers), Dockerfile, requirements.txt, .env.example
- This build plan

**Not yet done:**
- ~35 remaining skills need content (currently empty directories)
- Supabase database not provisioned (schema.sql needs writing + deploying)
- Shopify Custom App not created (API credentials needed)
- No MCP server connections configured
- Dashboard (React PWA) not started
- No tests or evals written

---

## Phase 1: Foundation (Weeks 1-2)

### Week 1: Infrastructure Setup

**Blockers to clear first — these gate everything else:**

| Task | Owner | Time | Dependency |
|------|-------|------|------------|
| Create Shopify Custom App | Chris | 30 min | Shopify admin access |
| Provision Supabase project | Chris | 15 min | Supabase account |
| Deploy schema.sql to Supabase | Chris + Claude | 1 hour | Supabase project |
| Get Anthropic API key (production) | Chris | 5 min | Anthropic console |
| Deploy server.py to Railway | Chris + Claude | 1 hour | Railway account |
| Configure Shopify webhooks → Railway URL | Chris | 30 min | Shopify app + Railway URL |

**Write the Supabase schema:**
```
Prompt for Claude Code:
"Read CLAUDE.md and skills/shared/supabase-ops-db/SKILL.md, then write
schema.sql with full DDL for: products, inventory_extended, orders,
competitive_intel, supplier_payments, marketing_performance,
skill_invocations. Include the materialized views and pg_cron schedules."
```

**Write the shared Python library:**
```
Prompt:
"Create lib/shared/src/ts_shared/supabase_client.py with async Supabase
client wrapper, and logging_utils.py with skill_invocations logging.
Reference the schema in supabase-ops-db/schema.sql."
```

### Week 2: First Skills Go Live

**Target: Get ticket-triage and order-inquiry processing real customer emails.**

| Task | Details |
|------|---------|
| Connect Re:amaze webhook to server.py | New endpoint: `/webhooks/reamaze/ticket` |
| Test ticket-triage on 20 historical emails | Use Claude Code locally with `claude -p` |
| Test order-inquiry with real Shopify orders | Verify order lookup works end-to-end |
| Set up Shopify inventory webhook | Wire to inventory-management skill |
| Run first daily pick list generation | Test fulfillment-domestic cron |
| Record first batch of COGS data | Jhoti provides Nepal invoice data |

**Eval framework setup:**
```
Prompt for skill-creator:
"Create evals for the ticket-triage skill. Test cases:
1. Simple shipping question (should AUTO_RESPOND)
2. Refund request for $30 item (should ESCALATE_JHOTI)
3. Buddhist practice question (should ESCALATE to Dr. Hun Lye)
4. Angry customer threatening chargeback (should be URGENT)
Run with and without the skill, generate the eval viewer."
```

---

## Phase 2: Operations Maturity (Weeks 3-4)

### Skills to Draft

| Skill | Priority | Notes |
|-------|----------|-------|
| `operations/supplier-communication` | High | Jhoti needs this for Nepal supplier coordination |
| `operations/fulfillment-nepal` | High | Nepal shipment tracking, customs, HS codes |
| `operations/fulfillment-mexico` | Medium | Omar's workflow, simpler than domestic |
| `finance/margin-reporting` | High | Weekly margin report for Chris |
| `finance/nepal-payments` | High | NPR payment tracking, exchange rates |
| `customer-service/return-request` | Medium | Returns policy enforcement |
| `customer-service/product-guidance` | Medium | Loads product-knowledge skill |

### Operational Targets

- [ ] 50+ orders processed through fulfillment-domestic without errors
- [ ] Daily reconciliation running automatically with zero false positives
- [ ] Jhoti receiving Bahasa Indonesia alerts via WhatsApp
- [ ] Fiona using dashboard for daily pick lists
- [ ] COGS confirmed for top 20 SKUs (by revenue)

---

## Phase 3: Ecommerce Expansion (Weeks 5-6)

### Etsy Launch

| Skill | Priority | Dependency |
|-------|----------|------------|
| `ecommerce/etsy-content-optimization` | Critical | Etsy shop created |
| `ecommerce/cross-channel-parity` | Critical | Both Shopify + Etsy live |
| `operations/etsy-sync-monitoring` | High | CedCommerce configured |
| `category-management/pricing-strategy` | High | COGS confirmed for listed items |

### Amazon FBA Prep

| Skill | Priority | Dependency |
|-------|----------|------------|
| `operations/amazon-fba-replenishment` | High | Amazon Seller Central account |
| `ecommerce/amazon-listing-optimization` | Medium | Product catalog on Amazon |
| `finance/amazon-fee-analysis` | Medium | First Amazon sales data |

---

## Phase 4: Marketing & Category Intelligence (Weeks 7-8)

### Skills to Draft

| Skill | Priority | API Dependency |
|-------|----------|----------------|
| `marketing/meta-ads` | High | Meta Ads API access |
| `marketing/google-ads` | High | Google Ads API access |
| `marketing/performance-reporting` | High | Ad platform data flowing |
| `marketing/email-sms` | Medium | Klaviyo API access |
| `marketing/drift-detection` | Medium | 30+ days of performance data |
| `marketing/inventory-aware-advertising` | High | Inventory skill + ad skills |
| `category-management/competitive-research` | Medium | DataForSEO or similar |
| `category-management/category-portfolio` | Low | 3+ months of sales data |

### MCP Server Inventory

| Service | MCP Availability | Fallback |
|---------|-----------------|----------|
| Shopify | `@anthropic/shopify-mcp` (community) | Direct REST API via `@tool` |
| Klaviyo | Unknown — check registry | REST API wrapper |
| QuickBooks | Unknown — check registry | REST API wrapper via OAuth2 |
| Shippo | Unknown — check registry | REST API wrapper |
| Meta Ads | Unknown — unlikely | REST API wrapper |
| Google Ads | Unknown — unlikely | REST API wrapper |
| Re:amaze | Unknown | REST API wrapper |

**Action item**: For each service without a maintained MCP server, write a thin Python wrapper exposed as an in-process MCP tool via the Agent SDK's `@tool` decorator. These live in `lib/shared/src/ts_shared/tools/`.

---

## Phase 5: Polish & Graduation (Weeks 9-10)

- Run Phase 1 → Phase 2 evaluation for mature skills
- Write remaining ~15 lower-priority skills
- Set up Langfuse observability (Tier 2)
- Build drift detection canary prompts
- Begin Phase 2 autonomous operation for proven skills

---

## Key Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Shopify API rate limits during batch operations | Skill failures | Implement rate-aware queuing in shared lib |
| Nepal supplier invoice data inconsistent | Bad COGS, wrong margins | Phase 1 requires human validation of every COGS entry |
| Claude API outage during order processing | Orders queue up | Simple retry + orders preserved in Shopify (source of truth) |
| Etsy content optimization undertested | Poor Etsy SEO | Use skill-creator evals extensively before launch |
| QuickBooks API complexity (OAuth2 flow) | Delayed finance integration | Start with manual QuickBooks data export, automate later |
| Solo operator bandwidth | Can't build everything at once | Strict phase ordering — don't start Phase 3 before Phase 2 targets met |

---

## Claude Code Prompts for Next Skills

These are ready-to-use prompts for drafting the remaining skills with Claude Code:

### Supplier Communication
```
"Read CLAUDE.md, then read skills/shared/escalation-matrix/SKILL.md and
skills/shared/brand-guidelines/cultural-sensitivity.md. Write
skills/operations/supplier-communication/SKILL.md for drafting
correspondence with Nepal suppliers. Must support Bahasa Indonesia
output for Jhoti's review. Include purchase order drafting, shipment
status inquiries, and quality issue escalation."
```

### Margin Reporting
```
"Read CLAUDE.md and skills/finance/cogs-tracking/SKILL.md and
skills/shared/supabase-ops-db/SKILL.md. Write
skills/finance/margin-reporting/SKILL.md for weekly margin reports.
Should query the product_margin_detail materialized view and generate
a report showing margin by SKU, category, and channel with trend
arrows vs. previous period."
```

### Pricing Strategy
```
"Read CLAUDE.md, skills/shared/channel-config/SKILL.md, and
skills/finance/cogs-tracking/SKILL.md. Write
skills/category-management/pricing-strategy/SKILL.md. Must account
for channel-specific fee structures, margin floors by category,
competitive positioning, and the Dharma Giving allocation."
```

### Competitive Research
```
"Read CLAUDE.md and skills/shared/product-knowledge/SKILL.md. Write
skills/category-management/competitive-research/SKILL.md and
competitor-set.md. Include methodology for weekly competitive scans,
price comparison by category, and a Python script
(scrape-competitors.py) that pulls competitor prices from their
public storefronts."
```
