---
name: campaign-brief
description: Generates a structured campaign brief with content tier classification and frequency cap enforcement. Use when a marketing initiative, seasonal event, or content calendar entry needs a formal brief for CEO review.
allowed-tools: Read, Write
---

# Campaign Brief

**Announce at start:** "I'm using the campaign-brief skill to draft a structured marketing brief."

## Goal

Produce a structured campaign brief for Tibetan Spirit marketing initiatives. Applies the Content Tier Framework and enforces frequency caps before anything reaches `general-manager` for approval. Output is always queued — never scheduled or published directly.

## Process

1. **Classify tier** — Apply the Content Tier Framework from `.claude/rules/marketing-discipline.md`. If uncertain, escalate to Tier 3. Tier 4 is blocked — stop immediately and explain why.
2. **Check frequency caps** — Verify promotional email count (≤2/month) and ad impression caps (≤3/user/week). If at limit, do not draft — flag to `general-manager`.
3. **Check seasonal context** — For Losar, Saga Dawa, Vesak, or Q4: approach with reverence. Flag if the brief risks commercial momentum overriding spiritual significance.
4. **Draft the brief** — Use the format in `references/brief-template.md`. Include a substantive "What This Campaign Does NOT Do" section — not boilerplate.
5. **Verify** — Run the Verification checklist before outputting.
6. **Queue output** — Write to `data/marketing-briefs-queue.json`. Log observability entry to `data/agent-runs.json` per `_templates/observability.md`.

## Output

- **Primary:** `data/marketing-briefs-queue.json` — queued brief with tier classification
- **Secondary:** `data/agent-runs.json` — one observability entry per `_templates/observability.md`
- **Terminal:** Brief summary with tier, approval path, and any flags

**Verification:** Brief has correct tier classification. Frequency caps verified. "What This Campaign Does NOT Do" is substantive. No prohibited tactics present. Tier 3 content flagged for Spiritual Director review. Output written to queue with no live publishing.

## Common Rationalizations

| Thought | Reality |
|---|---|
| "This is educational content, not promotional" | If it drives traffic to a product, it is Tier 2 minimum. Classify honestly. |
| "Dharma Giving makes this mission-driven, not marketing" | Dharma Giving is an accounting line, never a campaign angle. |
| "We're just one email over the cap — it's a soft limit" | The cap is hard. Not sending is sometimes the correct decision. |
| "This seasonal event creates urgency" | Urgency language is Tier 4. Seasonal reverence is Tier 2/3. |

## Edge Cases

- **Tier 4 detected:** Block immediately. Write explanation to terminal. Do not queue anything.
- **Frequency cap at limit:** Do not draft. Flag to `general-manager` with cap status and next available window.
- **Tier 3 content:** Flag for Spiritual Director review before CEO — include this note explicitly in the queued brief.
- **Uncertain tier:** Default to Tier 3 and flag.

## Rules

- NEVER produce urgency, scarcity, or countdown language in any draft.
- NEVER include Dharma Giving as a campaign angle in customer-facing copy.
- NEVER queue without verifying frequency caps first.
- ALWAYS flag Tier 3 content for Spiritual Director review before CEO.

## Environment

- **Data files:** `data/marketing-briefs-queue.json`, `data/agent-runs.json`
- **Reference files:** `references/brief-template.md`, `.claude/rules/marketing-discipline.md`, `_templates/observability.md`

## Works Well With

- **Invoked by:** `marketing-strategist` agent
- **Followed by:** `general-manager` review queue
