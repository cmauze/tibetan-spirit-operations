---
name: cs-pipeline
description: Orchestrates the full customer service email workflow — triage, enrichment, draft, and approval queue in sequence. Use when a batch of unread customer emails needs processing, or when cs-drafter needs upstream triage and enrichment before drafting.
allowed-tools: Read, Write, mcp__claude_ai_Gmail__gmail_search_messages, mcp__claude_ai_Gmail__gmail_read_message, mcp__plugin_supabase_supabase__execute_sql
---

<HARD-GATE>
Do NOT draft any customer email without running triage classification first. Spiritual guidance emails escalate at triage and never reach the drafting stage. Skipping triage produces unclassified drafts that bypass escalation gates.
</HARD-GATE>

# CS Email Pipeline

**Announce at start:** "I'm using the cs-pipeline skill to process the customer email batch."

## Goal

Orchestrate the full customer service email workflow from inbox to approval queue: triage → enrichment → draft → queue. Each stage gates the next — an email only advances when the prior stage passes. No email is sent; all drafts require human approval before sending.

## Process

1. **Scan** — Query Gmail for unread external customer emails. Exclude `@tibetanspirit.com` and `@cgai.dev`. Build the processing queue.
2. **Triage** — For each email, invoke the `cs-triage` skill. Classify into one of 7 categories. Spiritual-guidance emails stop here and escalate to `spiritual-director` — do not draft. Complaints get priority ordering.
3. **Enrich** — For emails that passed triage, query Supabase `ts_orders` / `ts_products` for order and product context. Check Gmail for prior threads with the same customer. Attach enrichment data to the email record — even if the lookup returns nothing, the empty record must be attached.
4. **Draft** — For each enriched email, invoke the `cs-drafter` agent. Apply brand voice (`.claude/rules/brand-voice.md`) and cultural sensitivity rules (`.claude/rules/cultural-sensitivity.md`). Log each draft with `"ai_generated": true`.
5. **Queue** — Present batch summary to `general-manager` for approval. Each draft shows: category, customer first name only, subject, enrichment data used, and the draft text. Log observability entry to `data/agent-runs.json` per `_templates/observability.md`.

**HUMAN GATE 1: No email is sent. All drafts require `general-manager` approval before any response is sent.**

## Output

- **Primary:** `data/cs-drafts-log.json` — all draft records with category, enrichment, and `"ai_generated": true`
- **Secondary:** `data/agent-runs.json` — one observability entry per `_templates/observability.md`
- **Terminal:** Batch summary table: total processed, by category, escalations, drafts queued

**Verification:** All emails triaged before any draft created. Spiritual-guidance emails escalated with no draft produced. Enrichment record attached to every email (even empty). All drafts carry `"ai_generated": true`. No emails sent — drafts only, in queue.

## Data Hygiene

- Log customer first name only in batch summary — never full name or email address in terminal output.
- Persist first 200 chars of email body in enrichment records — keeps log files small and limits exposure.
- Never write full customer email addresses to `data/cs-drafts-log.json` — use customer ID or order number as the reference key.
- Strip PII before writing observability entries to `data/agent-runs.json`.

## Common Rationalizations

| Thought | Reality |
|---|---|
| "I know the category already, I'll skip triage" | Triage catches spiritual-guidance escalations. Skipping it bypasses a hard gate. |
| "No enrichment data found, so I'll draft without it" | Attach the empty enrichment record — the drafter needs to know the lookup happened. |
| "Customer is waiting, I'll send this one directly" | Every draft goes through the queue. Human approval is required before sending. |

## Edge Cases

- **Spiritual-guidance email reaches draft stage:** Block immediately. This means triage was skipped or misclassified. Log the error and do not produce a draft.
- **Enrichment lookup fails (Supabase down):** Attach an empty enrichment record with `"source": "unavailable"`. Continue to drafting.
- **Batch is empty:** Log to `data/agent-runs.json` with `"inputs_summary": {"emails_found": 0}`. Report zero-item batch to terminal.

## Rules

- NEVER send any customer email — draft only, `general-manager` sends.
- NEVER skip triage for any email in the batch, regardless of apparent simplicity.
- NEVER advance a spiritual-guidance email to the drafting stage.

## Environment

- **MCP servers:** Gmail (`gmail_search_messages`, `gmail_read_message`), Supabase (`execute_sql`)
- **Sub-skills:** `cs-triage`, `cs-drafter`
- **Data files:** `data/cs-drafts-log.json`, `data/agent-runs.json`
- **Reference files:** `.claude/rules/brand-voice.md`, `.claude/rules/cultural-sensitivity.md`, `_templates/observability.md`

## Works Well With

- **Sub-skills:** `cs-triage` (step 2), `cs-drafter` (step 4)
- **Invoked by:** `cs-drafter` agent on batch runs
