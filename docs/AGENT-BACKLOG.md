# Tibetan Spirit Ops — Agent Implementation Backlog

Status as of 2026-04-01. Ordered by implementation priority.

## Implemented

### CS Drafter (DONE)
- File: `.claude/agents/cs-drafter.md`
- Skill: `.claude/skills/cs-triage/SKILL.md`
- Tools: Gmail MCP (search, read, create draft)
- Approval: Decision Needed (all drafts reviewed by Chris)

### Finance Analyst (DONE)
- File: `.claude/agents/finance-analyst.md`
- Tools: Read, Bash (data queries)
- Approval: Auto-logged (weekly P&L is informational)

---

## Not Yet Implemented

### Fulfillment Manager — Priority: HIGH
**Role**: Order tracking, shipping status, supplier coordination with Jothi
**Tools needed**: Shopify MCP (orders, fulfillments), Gmail MCP (Jothi communications)
**Rules**: shopify-api.md (read-only order access)
**Complexity**: Medium — needs Shopify MCP integration
**Dependencies**: Shopify MCP server configured and tested
**Key workflows**:
- Daily order status scan → flag unfulfilled orders >48h
- Shipping delay detection → notify Chris
- Jothi coordination drafts (Bahasa Indonesia translation consideration)

### Inventory Analyst — Priority: HIGH
**Role**: Stock monitoring, restock alerts, demand forecasting
**Tools needed**: Shopify MCP (inventory levels), data files for historical trends
**Rules**: shopify-api.md
**Complexity**: Medium — needs inventory threshold rules defined
**Dependencies**: Shopify MCP, product catalog in data/
**Key workflows**:
- Daily inventory scan → flag items below reorder point
- Weekly demand forecast based on trailing 4-week sales velocity
- Seasonal adjustment (holiday spikes for incense, prayer flags)

### Marketing Strategist — Priority: LOW
**Role**: Campaign briefs, content calendar, targeting
**Tools needed**: Gmail MCP, data files (customer segments, campaign history)
**Rules**: brand-voice.md, cultural-sensitivity.md
**Complexity**: High — brand voice is nuanced, cultural sensitivity critical
**Dependencies**: CS Drafter proven first (similar brand voice needs), customer segmentation data
**Key workflows**:
- Monthly content calendar proposal
- Campaign brief drafts (seasonal: Losar, Saga Dawa, holiday season)
- RFM segment targeting suggestions (CCPA: must include opt-out mechanism)

### Catalog Curator — Priority: LOW
**Role**: Product descriptions via evaluator-optimizer loop
**Tools needed**: Shopify MCP (product data), Write
**Rules**: brand-voice.md, cultural-sensitivity.md
**Complexity**: High — highest budget ($5/invocation), needs eval loop
**Dependencies**: Brand voice rules proven via CS Drafter, product photography workflow
**Key workflows**:
- New product description generation (practice context, not decor)
- Existing description audit and improvement
- SEO optimization within brand voice constraints

---

## Hooks Backlog

| Hook | Type | Matcher | Status | Notes |
|------|------|---------|--------|-------|
| budget-check.sh | PreToolUse | mcp__shopify__.*\|Bash | DONE | Per-agent daily caps |
| log-activity.sh | PostToolUse | Bash\|Write\|Edit\|mcp__.* | DONE | Async activity log |
| brand-voice-lint.sh | PostToolUse | Write\|Edit | TODO | Scan output for banned terms, flag violations |
| load-ts-state.sh | SessionStart | * | TODO | Load last run state, check data freshness |
| stop-verification.sh | Stop | * | TODO | Write session summary, verify no PII in output |
| slack-notify.sh | Notification | * | TODO | Route to #ts-operations channel |

## Rules Backlog

| Rule | Status | Notes |
|------|--------|-------|
| brand-voice.md | DONE | Comprehensive brand voice guidelines |
| cultural-sensitivity.md | DONE | Sacred terms, prohibited language, escalation |
| shopify-api.md | DONE | API version, rate limits, read-only patterns |
| supabase.md | TODO | Query patterns, RLS rules, table schemas |
| ccpa-compliance.md | TODO | Customer data handling, opt-out, disclosure |
| supplier-comms.md | TODO | Jothi/Fiona communication protocols, language |

## Skills Backlog

| Skill | Agent | Status | Notes |
|-------|-------|--------|-------|
| cs-triage | CS Drafter | DONE | Email classification + response templates |
| order-lookup | Fulfillment Manager | TODO | Shopify order query + status formatting |
| inventory-scan | Inventory Analyst | TODO | Stock level check + reorder alerting |
| campaign-brief | Marketing Strategist | TODO | Campaign template + targeting rules |
| product-description | Catalog Curator | TODO | Evaluator-optimizer description loop |
| weekly-pnl | Finance Analyst | TODO | P&L calculation + anomaly detection |

## Implementation Order

1. **Now**: CS Drafter + Finance Analyst (done)
2. **Next sprint**: Fulfillment Manager + Inventory Analyst (need Shopify MCP)
3. **After that**: Marketing Strategist (needs brand voice proven)
4. **Last**: Catalog Curator (highest complexity, needs eval loop)
