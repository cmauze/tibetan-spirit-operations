---
name: cs-pipeline
description: Use when customer service emails need end-to-end processing — triage, enrichment, drafting, and approval queuing in sequence.
---

<HARD-GATE>
Every email MUST pass through triage classification before any draft is created. Spiritual guidance emails are escalated at triage — they never reach the drafting stage. Skipping triage produces unclassified drafts that bypass the escalation and compliance gates.
</HARD-GATE>

# CS Email Pipeline

## Overview

Orchestrates the full customer service email workflow: triage → enrichment → draft → approval queue. Each stage has its own gate — an email only advances when the prior stage passes.

## When to Use

**Invoke when:**
- A batch of unread customer emails needs processing
- `general-manager` says "run CS pipeline" or "process customer emails"
- cs-drafter needs upstream triage and enrichment before drafting

**Do NOT use for:**
- A single already-classified email (use cs-drafter directly)
- Internal team communications
- Emails already in the approval queue

## Workflow

1. **Scan** — Query Gmail for unread external customer emails. Exclude `@tibetanspirit.com` and `@cgai.dev`. Build the processing queue.
2. **Triage** — For each email, invoke `cs-triage` skill. Classify into one of 7 categories. Spiritual-guidance emails stop here and escalate to `spiritual-director`. Complaints get priority ordering.
3. **Enrich** — For emails that passed triage, query Supabase for order/product context. Check Gmail for prior threads with the same customer. Attach enrichment data to the email record.
4. **Draft** — For each enriched email, invoke `cs-drafter` agent to create a Gmail draft. Apply brand voice and cultural sensitivity rules. Log with `"ai_generated": true`.
5. **Queue** — Present the batch summary to `general-manager` for approval. Each draft shows: category, customer, subject, enrichment data used, and the draft itself.

**Stage gates:**

| Gate | Condition to advance | Failure action |
|------|---------------------|----------------|
| Triage → Enrich | Category assigned, not `spiritual-guidance` | Escalate to `spiritual-director` |
| Enrich → Draft | Enrichment data attached (even if empty) | Flag for manual review |
| Draft → Queue | Draft passes Verification checklist | Hold for revision |

## Common Rationalizations

| Rationalization | Reality |
|----------------|---------|
| "I know the category already, I'll skip triage" | Triage catches spiritual-guidance escalations. Skipping it is a compliance gap. |
| "No enrichment data found, so I'll draft without it" | Attach the empty enrichment record — the drafter needs to know the lookup happened. |
| "Customer is waiting, I'll send this one directly" | Every draft goes through the queue. CCPA requires human approval. |

## Red Flags

- Drafting before triage completes
- Spiritual-guidance emails reaching the draft stage
- Sending any email without human approval
- Skipping enrichment because "the email is straightforward"
- Processing internal team emails through the pipeline

## Verification

- [ ] All emails triaged before any drafting begins
- [ ] Spiritual-guidance emails escalated, not drafted
- [ ] Enrichment data attached to every email record (even if no data found)
- [ ] All drafts have `"ai_generated": true` in log
- [ ] Batch summary presented for `general-manager` review
- [ ] No emails sent — drafts only, queued for approval
