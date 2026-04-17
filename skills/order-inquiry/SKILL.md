---
name: order-inquiry
description: Resolves customer questions about order status, tracking, and delivery by querying live order data and drafting a response. Use when a customer asks where their order is, requests a tracking number, questions a delivery estimate, or expresses concern about a delay.
allowed-tools: Read, Write, mcp__plugin_supabase_supabase__execute_sql
---

# CS Order Inquiry

**Announce at start:** "I'm using the order-inquiry skill to look up this order and draft a response."

## Goal

Look up the customer's order, translate internal fulfillment state into customer-friendly language, handle special cases (Nepal-sourced, FBA, delayed, not found), draft a warm response, and queue it for human approval. No response is sent without human review.

## Process

1. **Identify the order** — Locate via order number (preferred), confirmation email, or name + purchase date. If multiple matches exist, confirm with customer before proceeding. Never say "we have no record" before exhausting all lookup options.
2. **Query order status** — Pull from Supabase `ts_orders` first; fall back to Shopify GraphQL API for real-time state. Map internal status to customer-facing language per `references/status-mapping.md`.
3. **Handle special cases** — Check for: Nepal-sourced items (2–4 week lead times), FBA orders (tracking from Amazon, not Shopify), delayed orders (>7 business days domestic, >21 international), or order not found. Apply rules from `references/status-mapping.md` for each.
4. **Draft the response** — Apply brand voice: warm, informative, practice-aware. Acknowledge any delay directly before offering next steps. Never use urgency language. Never guess a delivery date when carrier data is unavailable. Subject: `Re: [original subject]`. Closing: "With warm regards, / The Tibetan Spirit Team".
5. **Queue for review** — Append draft to `data/cs-drafts-log.json` with `"ai_generated": true`. Log observability entry to `data/agent-runs.json` per `_templates/observability.md`.

**HUMAN GATE: Draft goes to the CS queue — human sends. Never call `gmail_create_draft` or send directly.**

## Output

- **Primary:** `data/cs-drafts-log.json` — draft record with order status and `"ai_generated": true`
- **Secondary:** `data/agent-runs.json` — one observability entry per `_templates/observability.md`
- **Terminal:** Order status found / special case type / draft queued confirmation

**Verification:** Order located via at least one identifier. Status pulled from `ts_orders` or Shopify fallback. Customer-facing status uses mapped language, not internal enum. Special case rules applied if applicable. Response acknowledges delay before offering resolution. No guessed delivery dates. Draft queued — not sent.

## Data Hygiene

- Store customer first name only in draft log — never full name + email combination.
- Persist order ID and status in the log record — not the customer's full shipping address.
- Never expose SHOPIFY_ACCESS_TOKEN or Supabase credentials in any output or log.
- Strip PII from observability entries written to `data/agent-runs.json`.

## Common Rationalizations

| Thought | Reality |
|---|---|
| "I'll estimate delivery from the ship date" | Never guess. Pull actual carrier data or state it's unavailable. |
| "The delay is minor, I won't mention it" | Acknowledge delays directly. Customers who discover it themselves lose trust. |
| "We have no record of this order" | Never say this. Ask the customer to check their confirmation email first. |
| "FBA orders work the same way" | They don't. FBA tracking data comes from Amazon, not Shopify. |

## Edge Cases

- **Order not found:** Do not say "no record exists." Ask customer to provide confirmation email. Escalate to `general-manager` if still unresolvable.
- **FBA order:** Note that tracking data comes from Amazon. Include the Amazon order link or tracking number if available in `ts_orders`.
- **Nepal-sourced item:** Proactively mention 2–4 week lead times and explain the sourcing story warmly.
- **Delay >7 days domestic / >21 international:** Acknowledge the delay in the first sentence of the response body before any explanation.

## Rules

- NEVER send any response — queue only, human approves.
- NEVER guess a delivery date when carrier data is unavailable.
- ALWAYS acknowledge delays before offering next steps.

## Environment

- **MCP server:** Supabase (`execute_sql`)
- **Data files:** `data/cs-drafts-log.json`, `data/agent-runs.json`
- **Reference files:** `references/status-mapping.md`, `_templates/observability.md`
- **Rules:** `.claude/rules/brand-voice.md`

## Works Well With

- **Preceded by:** `cs-triage` (shipping-status classification)
- **Invoked by:** `cs-drafter` agent
