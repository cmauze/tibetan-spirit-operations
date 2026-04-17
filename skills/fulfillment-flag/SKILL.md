---
name: fulfillment-flag
description: Identifies fulfillment exceptions and routes them to the correct team member before a problem compounds. Use when orders need exception flagging, fulfillment routing review, or shipping anomalies require team coordination.
allowed-tools: Read, Write, mcp__plugin_supabase_supabase__execute_sql
---

# Fulfillment Flag

**Announce at start:** "I'm using the fulfillment-flag skill to identify and route fulfillment exceptions."

## Goal

Detect fulfillment exceptions from the order pipeline, investigate each before escalating, draft the correct communication for the responsible team member in their language and channel, and queue everything to `data/fulfillment-comms-queue.json` for human approval. A delayed shipment is always better than a mis-routed one.

## Process

1. **Evaluate the trigger** — Identify the exception type using the decision table in `references/decision-table.md`. Match exception type to responsible role, channel, and language.
2. **Investigate before escalating** — Check the order in Shopify and the warehouse dashboard. For Nepal supplier delays, investigate infrastructure causes before assuming negligence. Never escalate blindly.
3. **Draft the flag** — Write the exception summary: order ID, exception type, investigation findings, and recommended action. Use the correct language and formal register per `.claude/rules/org-roles.md`.
4. **Route to the correct person** — Apply decision table to select role, channel, and language. `operations-manager`: Bahasa Indonesia formal, use "Anda". `warehouse-manager`: Mandarin, Dashboard only. `general-manager`: English, Slack or Dashboard.
5. **Queue to comms file** — Append to `data/fulfillment-comms-queue.json` with `"ai_generated": true`. Log observability entry to `data/agent-runs.json` per `_templates/observability.md`. Never send directly.

## Output

- **Primary:** `data/fulfillment-comms-queue.json` — queued exception flags with routing metadata
- **Secondary:** `data/agent-runs.json` — one observability entry per `_templates/observability.md`
- **Terminal:** List of exceptions flagged with exception type, order ID, and assigned role

**Verification:** Exception type identified from decision table. Investigation completed before escalation. Correct role, channel, and language assigned per decision table. Mixed domestic/international orders flagged for manual review — not auto-routed. All flags in queue — nothing sent. `"ai_generated": true` in every queue entry.

## Data Hygiene

- Include order ID and exception type in flags — not customer name or email address.
- Never log customer shipping addresses in `data/fulfillment-comms-queue.json` — reference order ID only.
- Strip customer PII from observability entries in `data/agent-runs.json`.

## Common Rationalizations

| Thought | Reality |
|---|---|
| "I'll auto-route the mixed domestic/international order to save time" | NEVER auto-route mixed orders — flag for manual review every time. |
| "The Nepal supplier is just a few days late, I'll wait" | Surface to `general-manager` before the deadline passes — investigate first, but don't absorb delays silently. |
| "Shopify says we have stock, so we're fine" | Trust the physical count when it conflicts — Shopify can be stale. |
| "I'll send the flag directly to `operations-manager` over Slack" | Queue to `data/fulfillment-comms-queue.json` — never send directly. |

## Edge Cases

- **Mixed domestic/international components:** Always flag for manual review — never auto-route regardless of apparent simplicity.
- **Nepal supplier delay:** Investigate infrastructure causes first. Escalate to `general-manager` after investigation, not before.
- **Address validation failure:** Hold order. Flag for CS team — do not attempt address correction.
- **Inventory conflict (Shopify vs. warehouse):** Trust physical count. Flag discrepancy to `operations-manager`.

## Rules

- NEVER send any communication directly — queue only, human approves.
- NEVER auto-route orders with both domestic and international components.
- ALWAYS use "Anda" (not "kamu") in all Bahasa Indonesia communications.
- ALWAYS investigate Nepal delays before escalating — assume infrastructure, not negligence.

## Environment

- **MCP server:** Supabase (`execute_sql`)
- **Data files:** `data/fulfillment-comms-queue.json`, `data/agent-runs.json`
- **Reference files:** `references/decision-table.md`, `.claude/rules/org-roles.md`, `_templates/observability.md`

## Works Well With

- **Invoked by:** `fulfillment-manager` agent
- **Preceded by:** `shopify-query` (for order status lookup)
