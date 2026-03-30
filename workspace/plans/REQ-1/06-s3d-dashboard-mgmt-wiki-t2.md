# Sprint S3-D: Dashboard Management + Wiki Tier 2

**Tools:** Cursor/Gemini (dashboard pages) + Claude Code (wiki deepening)
**Parallel Group:** PG-3 (runs in parallel with S3-W)
**Prerequisites:** S2-D complete (dashboard deployed), S2-K complete (Tier 1 skills done)
**Complexity:** Moderate

---

## Overview

Two parallel workstreams that touch completely different files:
1. **Dashboard:** Add workflow registry and agent registry management views (Cursor/Gemini)
2. **Wiki:** Deepen 10 Tier 2 skills to production quality (Claude Code)

---

## Dashboard Dev Prompt (Cursor/Gemini)

```
You are extending the TS Command Center dashboard (ts-command-center/ repo).
The app already has: login, company selector, task inbox, health, costs, home.

=== PROMPT D-4: Workflow & Agent Registry ===

Build management views that let Chris browse and inspect the system's
configuration — what agents exist, what workflows they run, what steps
each workflow has, and their execution history.

Workflow Registry (/workflows):
- Table/list of all workflows
- Columns: name, company, trigger type (cron/webhook/manual), status badge,
  approval tier (1/2/3), last run time, total runs
- Filter by: company (from selector), status
- Sort by: name, last run
- Click row → /workflows/[id]

Workflow Detail (/workflows/[id]):
- Header section: name, description, trigger config (show cron expression),
  approval tier, default assignee, monthly budget
- Steps table: ordered list from workflow_steps
  Columns: order, name, step_type, model, temperature
  Color-code step_type:
    gate = gray
    reasoning = blue
    template = green
    eval = purple
    tool-call = orange
- Run History section: last 20 workflow_runs
  Columns: started_at, status (badge), total_cost_usd, duration_ms, error_message
  Failed runs highlighted in red background
- Placeholder link: "View Eval Dashboard" → /workflows/[id]/eval (built in S4)

Agent Registry (/agents):
- Table/list of all agents
- Columns: name, company, status badge, skill count (from agent_skills join),
  recent activity (last workflow_run involving this agent)
- Filter by: company, status
- Click row → /agents/[id]

Agent Detail (/agents/[id]):
- Header: name, description, status, company
- Skills table: list from agent_skills join
  Columns: skill name, skill category, skill status
- Recent Runs: last 10 workflow_runs with this agent_id
  Same columns as workflow detail run history
- Cost Summary card: total cost last 30 days (sum from workflow_runs)

All views respect company selector filter.
Add "Workflows" and "Agents" to sidebar/nav.

Commit: "feat: workflow registry, agent registry, management views"
```

---

## Wiki Dev Prompt (Claude Code)

```
Read CLAUDE.md, ORG.md, SYSTEM-STATUS.md.
Read 2-3 Tier 1 skills (from Sprint S2-K) as quality reference.
Follow the exact same production quality standard.

Deepen these 10 Tier 2 skills to v1.0.0. Same requirements as Tier 1:
- Full frontmatter with graduation_criteria, escalation_rules, max_tokens
- Decision Logic with specific thresholds
- 3-5 complete response templates
- Anti-patterns with examples
- Under 500 lines each

=== 10 SKILLS ===

1. customer-service/order-inquiry — order status lookup, tracking info,
   delivery estimates, Shopify order API references

2. customer-service/product-guidance — product recommendations based on
   practice type, experience level, budget. Category cross-references.

3. customer-service/return-request — return policy (30 days, original condition),
   refund thresholds (<$25 auto-approve, $25-100 operations-manager, >$100 ceo),
   restocking considerations, RMA process

4. customer-service/practice-inquiry — Buddhist practice questions, ALWAYS
   escalate to spiritual-director for lineage/teaching questions,
   safe to answer: basic meditation, singing bowl technique, mala counting

5. customer-service/review-solicitation — post-purchase review request timing
   (7 days after delivery), personalized by product category,
   never for orders with complaints

6. marketing/meta-ads — Meta Ads Manager API reference, campaign structure
   (CBO vs ABO), audience targeting for Buddhist/wellness niche,
   creative best practices, pixel/CAPI setup

7. marketing/google-ads — Google Ads API reference, Shopping campaigns,
   search term management, negative keyword strategy,
   Performance Max considerations

8. marketing/performance-reporting — cross-channel performance aggregation,
   ROAS calculation, attribution models, weekly report format,
   budget allocation recommendations

9. operations/fulfillment-domestic — US domestic shipping (USPS/UPS/FedEx),
   Shippo API reference, label generation, Fiona's pick-pack-ship workflow
   (Chinese language dashboard), tracking updates

10. operations/supplier-communication — Nepal supplier relationship management,
    WhatsApp communication protocol, PO format, payment tracking (NPR/USD),
    quality inspection checklist, lead time expectations

Commit: "feat: deepen 10 Tier 2 skills to production quality (v1.0.0)"
```

---

## Dashboard Test Prompt

```
=== WORKFLOW REGISTRY ===
1. /workflows loads: shows all seeded workflows
2. Each row has correct trigger type and approval tier from Supabase
3. Click a workflow → /workflows/[id] loads
4. Steps table renders with color-coded step types
5. Run history shows entries from S1/S2 workflow runs (or empty state)
6. Company filter: switch to "Personal" → shows only personal workflows (or empty)

=== AGENT REGISTRY ===
7. /agents loads: shows 4 Tibetan Spirit agents
8. Skill count is correct (matches agent_skills join count)
9. Click an agent → /agents/[id] loads
10. Skills table shows assigned skills
11. Cost summary card shows 30-day total (may be $0 for unused agents)
12. Company filter works

=== NAV ===
13. "Workflows" and "Agents" appear in sidebar/nav
14. Mobile: accessible from "More" menu in bottom nav
```

---

## Wiki Test Prompt

```
=== VALIDATION ===
1. python scripts/validate_skill.py for all 10 skills → all PASS
2. All have version: "1.0.0" in frontmatter
3. All have graduation_criteria, escalation_rules, max_tokens populated
4. All under 500 lines: wc -l each SKILL.md

=== CONTENT QUALITY ===
5. No hardcoded names: grep -r "Jothi\|Jhoti\|Fiona" in these 10 skills → 0
6. No forbidden words: grep -ri "exotic\|mystical\|oriental" → 0
7. Decision trees have dollar thresholds (return-request has $25/$100 tiers)
8. 3+ response templates per skill
9. practice-inquiry explicitly escalates to spiritual-director for lineage questions
10. supplier-communication references WhatsApp + NPR/USD exchange rates
11. fulfillment-domestic references Fiona's role as warehouse-manager (not by name)

=== CROSS-REFERENCES ===
12. python scripts/validate_cross_refs.py → zero violations
```
