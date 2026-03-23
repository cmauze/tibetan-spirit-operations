---
name: ticket-triage
description: Classify and route incoming customer service tickets from Re:amaze. Use this skill whenever a new customer inquiry arrives, whether via email, chat, or social media. Handles classification into response tiers, drafts responses for simple queries, and prepares escalation briefs for complex ones. Supports bilingual output (English customer response + Bahasa Indonesia internal notes for Jhoti).
---

# Customer Service Ticket Triage

## Purpose

You receive a customer inquiry and must do three things:
1. **Classify** it into a response tier
2. **Draft a response** (or escalation brief)
3. **Log the decision** with confidence score

## Classification Tiers

### Tier 1: AUTO_RESPOND
Simple factual questions with clear answers. You generate and post the response directly.

**Examples:**
- "Where is my order?" → Look up order status in Shopify, provide tracking
- "What are your shipping rates?" → Reference standard shipping policy
- "Do you ship to [country]?" → Check shipping zones
- "What's the return policy?" → Reference return policy
- "When will [item] be back in stock?" → Check `inventory_extended` table

**Response guidelines:**
- Warm, helpful tone (read `skills/shared/brand-guidelines/SKILL.md`)
- Include specific details (tracking number, dates, policy details)
- Maximum 3 paragraphs
- Always end with "Is there anything else I can help you with?"

### Tier 2: ESCALATE_JHOTI
Operational issues requiring human judgment or authority beyond auto-response.

**Examples:**
- Refund or exchange requests
- Product quality complaints
- Shipping damage reports
- Order modifications after placement
- Questions about product sourcing or authenticity requiring specifics we don't have

**Output (three documents):**
1. **Bahasa Indonesia briefing for Jhoti** — Summary of the issue, recommended action, customer history if available. Use formal register ("Anda", "Mungkin bisa..."). Include the customer's original message translated to Bahasa Indonesia.
2. **English draft response** — A proposed customer reply for Jhoti to review, edit, and send
3. **Bilingual internal notes** — Context for the `skill_invocations` log

### Tier 3: ESCALATE_SPECIALIST
Questions requiring specific expertise.

| Route To | When |
|----------|------|
| Dr. Hun Lye | Buddhist practice questions, meditation guidance, cultural/spiritual significance |
| Chris | Pricing disputes, legal threats, partnership inquiries, wholesale requests |
| Fiona | Shipping logistics questions, warehouse-specific issues |

**Output:** Email draft to the specialist with full context + the customer's message.

### Tier 4: URGENT
Time-sensitive issues requiring immediate attention. Same as Tier 2 but flagged "MENDESAK" (urgent) in Jhoti's WhatsApp notification.

**Triggers:**
- Customer mentions legal action, BBB, or chargeback
- Order value >$200 with a complaint
- Product safety concern
- Social media complaint with public visibility

## Classification Logic

Work through this decision tree:

```
1. Is this spam or not a real customer inquiry?
   → Yes: Tag as spam, no response needed
   → No: Continue

2. Is this urgent? (legal threat, safety concern, high-value complaint)
   → Yes: URGENT (Tier 4)
   → No: Continue

3. Can I answer this with information I have access to?
   (order status, shipping policy, product specs, return policy)
   → Yes: AUTO_RESPOND (Tier 1)
   → No: Continue

4. Does this require Buddhist/spiritual expertise?
   → Yes: ESCALATE_SPECIALIST → Dr. Hun Lye (Tier 3)
   → No: Continue

5. Does this require operational authority?
   (refunds, exchanges, special accommodations)
   → Yes: ESCALATE_JHOTI (Tier 2)
   → No: ESCALATE_SPECIALIST → Chris (Tier 3)
```

## Response Templates

Read `skills/customer-service/ticket-triage/response-templates.md` for pre-approved response templates by category.

## Model Routing

- **Classification step**: Use Haiku 4.5 (fast, cheap — just categorizing)
- **Response drafting**: Use Sonnet 4.6 (needs nuance for customer tone)
- **Bahasa Indonesia translation**: Use Sonnet 4.6 (quality matters for Jhoti's trust)

## Output Format

Every triage produces a structured result:

```json
{
  "tier": "AUTO_RESPOND | ESCALATE_JHOTI | ESCALATE_SPECIALIST | URGENT",
  "category": "shipping | product | practice | refund | complaint | other",
  "confidence": 0.0-1.0,
  "customer_response_draft": "...",
  "internal_notes_en": "...",
  "internal_notes_id": "...",
  "escalation_target": "jhoti | dr_hun_lye | chris | fiona | null",
  "order_id": "if applicable",
  "suggested_tags": ["shipping", "tracking"]
}
```
