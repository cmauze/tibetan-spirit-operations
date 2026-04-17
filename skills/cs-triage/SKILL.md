---
name: cs-triage
description: Classifies an incoming customer email into one of 7 canonical categories and routes to the correct response workflow or escalation path. Use when a customer email arrives and needs classification before any response is drafted.
allowed-tools: Read, Write
---

<HARD-GATE>
Do NOT draft any customer response before running triage. Spiritual guidance emails escalate immediately to `spiritual-director` — no draft is ever created for this category.
</HARD-GATE>

# CS Email Triage

**Announce at start:** "I'm using the cs-triage skill to classify this customer email."

## Goal

Classify a single incoming customer email into exactly one of 7 canonical categories and determine the correct routing action. Spiritual-guidance is always checked first. Output is a classification record — never a draft response.

## Process

1. **Check spiritual-guidance FIRST** — If the email contains any request about meditation, practice, lineage, blessings, or dharma, classify as `spiritual-guidance` and escalate to `spiritual-director` immediately. Do not draft anything.
2. **Check for complaint signals** — Identify dissatisfaction, demand for refund, or negative experience language. Complaint gets priority handling.
3. **Classify into one of 7 categories** — Apply severity hierarchy for multi-signal emails: `complaint > order-issue > return-request > wholesale-inquiry > product-question > shipping-status`. See `references/classification-matrix.md` for signal words and escalation paths.
4. **Apply cultural sensitivity checks** — Verify no banned terms will appear in downstream response. Check that sacred terms stay untranslated. Products must be framed through practice context.
5. **Write classification record** — Append to `data/cs-drafts-log.json` with: timestamp, category, confidence, reasoning, and `"ai_generated": true`. Log observability entry to `data/agent-runs.json` per `_templates/observability.md`.

## Output

- **Primary:** `data/cs-drafts-log.json` — classification record with category, confidence, reasoning
- **Secondary:** `data/agent-runs.json` — one observability entry per `_templates/observability.md`
- **Terminal:** Category assignment and routing action (e.g., "Classified as `complaint` — priority review by `general-manager`")

**Verification:** Spiritual-guidance check ran first. Category is from the canonical 7 only. Confidence and reasoning recorded. Log entry has `"ai_generated": true`. No draft produced.

## Data Hygiene

- Never log the full email body — persist subject line and first 200 chars of body only.
- Never log the customer's full email address in classification records — use customer ID or order reference if available.
- Strip PII before writing observability entries.

## Common Rationalizations

| Thought | Reality |
|---|---|
| "The question mentions meditation but it's really about the product" | If it touches practice, it is `spiritual-guidance`. When uncertain, escalate. |
| "I'll draft a tentative response and flag it" | For `spiritual-guidance`, do NOT draft. Escalation is the only output. |
| "Complaint is mild — I'll downgrade it" | Classify by content, not tone intensity. |
| "I'm fairly sure this term is appropriate" | Uncertain on cultural terms → flag for `spiritual-director`. Never generate plausible-sounding explanations. |

## Edge Cases

- **Multiple signals present:** Apply severity hierarchy — highest severity wins.
- **Uncertain classification:** Default to `product-question`, set confidence to low, flag for `general-manager` review.
- **Wholesale inquiry >$500:** Classify as `wholesale-inquiry` and flag for `general-manager` escalation.

## Rules

- NEVER draft a response when category is `spiritual-guidance`.
- NEVER use banned terms in any output: exotic, mystical, oriental, ancient secrets, zen vibes, namaste.
- ALWAYS keep sacred terms untranslated: mala, thangka, dharma, sangha, puja, mandala.

## Environment

- **Data files:** `data/cs-drafts-log.json`, `data/agent-runs.json`
- **Reference files:** `references/classification-matrix.md`, `_templates/observability.md`

## Works Well With

- **Followed by:** `order-inquiry` (shipping-status), `cs-drafter` (all other categories)
- **Invoked within:** `cs-workflow` (step 2)
