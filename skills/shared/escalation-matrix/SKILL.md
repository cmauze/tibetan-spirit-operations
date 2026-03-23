---
name: escalation-matrix
description: Decision tree for routing issues to the right human. Load this skill whenever a task requires human approval, when you are unsure how to proceed, when a customer issue exceeds your authority, or when a decision involves money above threshold amounts. Every agent should reference this skill for escalation decisions.
---

# Tibetan Spirit Escalation Matrix

## Core Principle

Phase 1 skills always propose actions for human approval. This matrix determines *which* human approves *what*. When in doubt, escalate to Chris.

## Decision Tree by Domain

### Customer Service Escalations

| Situation | Route To | Method | SLA |
|-----------|----------|--------|-----|
| Simple shipping/tracking question | AUTO_RESPOND | Direct via Re:amaze | Immediate |
| Product question (materials, sizing) | AUTO_RESPOND | Direct via Re:amaze | Immediate |
| Buddhist practice question | Dr. Hun Lye | Email | 48 hours |
| Refund request ≤$50 | Jhoti | Dashboard/WhatsApp | 24 hours |
| Refund request >$50 | Chris | Dashboard | 24 hours |
| Complaint about product quality | Jhoti | Dashboard/WhatsApp (Bahasa Indonesia) | 12 hours |
| Complaint about shipping damage | Fiona | Dashboard | 24 hours |
| Legal threat or chargeback | Chris | Dashboard + email alert | 4 hours |
| Cultural sensitivity concern | Dr. Hun Lye + Chris | Email | 24 hours |

### Operations Escalations

| Situation | Route To | Method | SLA |
|-----------|----------|--------|-----|
| Standard domestic order | Fiona | Dashboard pick list | Same day |
| Mexico/Latin America order | Omar | Email | 24 hours |
| Nepal supplier reorder needed | Jhoti | WhatsApp (Bahasa Indonesia) | 24 hours |
| Inventory below reorder point | Jhoti | WhatsApp (Bahasa Indonesia) | 12 hours |
| Inventory at zero (stockout) | Chris + Jhoti | Dashboard + WhatsApp | 4 hours |
| Shipping exception (wrong address, damage) | Fiona | Dashboard | Same day |
| Nepal shipment customs issue | Jhoti + Chris | WhatsApp + Dashboard | 12 hours |
| FBA replenishment needed | Chris | Dashboard | 48 hours |

### Pricing and Category Escalations

| Situation | Route To | Method | SLA |
|-----------|----------|--------|-----|
| Price change recommendation | Chris | Dashboard approval queue | 48 hours |
| New product addition | Jhoti (sourcing) → Chris (approval) | Dashboard | 1 week |
| Competitor undercut >20% | Chris | Dashboard + alert | 24 hours |
| Promotion/discount creation | Chris | Dashboard approval queue | 48 hours |

### Marketing Escalations

| Situation | Route To | Method | SLA |
|-----------|----------|--------|-----|
| Ad budget increase >10% | Chris | Dashboard approval queue | 24 hours |
| ROAS drop >15% from 30-day avg | Chris | Dashboard + auto-pause ads | 4 hours |
| New ad creative needed | Chris | Dashboard | 48 hours |
| Email campaign send (>500 recipients) | Chris | Dashboard approval queue | 24 hours |

### Finance Escalations

| Situation | Route To | Method | SLA |
|-----------|----------|--------|-----|
| Reconciliation discrepancy <$50 | Log only | Supabase | N/A |
| Reconciliation discrepancy $50-$500 | Chris | Dashboard | 48 hours |
| Reconciliation discrepancy >$500 | Chris | Dashboard + email alert | 24 hours |
| Nepal supplier payment due | Jhoti → Chris | WhatsApp → Dashboard | 1 week |
| Debt service payment reminder | Chris | Dashboard | 1 week |

## Contact Methods

| Person | Dashboard | WhatsApp | Email | Language |
|--------|-----------|----------|-------|----------|
| Chris | Yes | No | chris@tibetanspirit.com | English |
| Jhoti | Yes (mobile) | Yes (primary) | jhoti@tibetanspirit.com | **Bahasa Indonesia** (formal register) |
| Fiona | Yes | No | fiona@tibetanspirit.com | English |
| Dr. Hun Lye | No | No | hunlye@foresthermitage.org | English |
| Omar | No | No | omar@espiritutibetano.mx | English/Spanish |

## Bahasa Indonesia Communication Rules for Jhoti

When communicating with Jhoti, always use formal Bahasa Indonesia:
- Use **"Anda"** (formal you), never "kamu" (informal)
- Frame instructions as suggestions: **"Mungkin bisa..."** (Perhaps you could...)
- Use passive voice for softer tone
- Never cause loss of face — frame problems as situations to resolve together
- Mark urgent items with **"MENDESAK"** label
- Buddhist terminology stays untranslated: mala, thangka, dharma
