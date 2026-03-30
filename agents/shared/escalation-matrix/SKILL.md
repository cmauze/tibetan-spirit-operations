---
name: escalation-matrix
description: Decision tree for routing issues to the right human. Load this skill whenever a task requires human approval, when you are unsure how to proceed, when a customer issue exceeds your authority, or when a decision involves money above threshold amounts. Every agent should reference this skill for escalation decisions.
version: "0.1.0"
category: shared
tags: [escalation, routing, approval]
author: operations-team
model: haiku
cacheable: true
estimated_tokens: 900
phase: 1
depends_on: [shared/brand-guidelines]
external_apis: []
cost_budget_usd: 0.05
---

# Tibetan Spirit Escalation Matrix

## Core Principle

Phase 1 skills always propose actions for human approval. This matrix determines *which* human approves *what*. When in doubt, escalate to ceo.

## Decision Tree by Domain

### Customer Service Escalations

| Situation | Route To | Method | SLA |
|-----------|----------|--------|-----|
| Simple shipping/tracking question | AUTO_RESPOND | Direct via Re:amaze | Immediate |
| Product question (materials, sizing) | AUTO_RESPOND | Direct via Re:amaze | Immediate |
| Buddhist practice question | spiritual-director | Email | 48 hours |
| Refund request ≤$50 | operations-manager | Dashboard/WhatsApp | 24 hours |
| Refund request >$50 | ceo | Dashboard | 24 hours |
| Complaint about product quality | operations-manager | Dashboard/WhatsApp (Bahasa Indonesia) | 12 hours |
| Complaint about shipping damage | warehouse-manager | Dashboard | 24 hours |
| Legal threat or chargeback | ceo | Dashboard + email alert | 4 hours |
| Cultural sensitivity concern | spiritual-director + ceo | Email | 24 hours |

### Operations Escalations

| Situation | Route To | Method | SLA |
|-----------|----------|--------|-----|
| Standard domestic order | warehouse-manager | Dashboard pick list | Same day |
| Mexico/Latin America order | mexico-fulfillment | Email | 24 hours |
| Nepal supplier reorder needed | operations-manager | WhatsApp (Bahasa Indonesia) | 24 hours |
| Inventory below reorder point | operations-manager | WhatsApp (Bahasa Indonesia) | 12 hours |
| Inventory at zero (stockout) | ceo + operations-manager | Dashboard + WhatsApp | 4 hours |
| Shipping exception (wrong address, damage) | warehouse-manager | Dashboard | Same day |
| Nepal shipment customs issue | operations-manager + ceo | WhatsApp + Dashboard | 12 hours |
| FBA replenishment needed | ceo | Dashboard | 48 hours |

### Pricing and Category Escalations

| Situation | Route To | Method | SLA |
|-----------|----------|--------|-----|
| Price change recommendation | ceo | Dashboard approval queue | 48 hours |
| New product addition | operations-manager (sourcing) → ceo (approval) | Dashboard | 1 week |
| Competitor undercut >20% | ceo | Dashboard + alert | 24 hours |
| Promotion/discount creation | ceo | Dashboard approval queue | 48 hours |

### Marketing Escalations

| Situation | Route To | Method | SLA |
|-----------|----------|--------|-----|
| Ad budget increase >10% | ceo | Dashboard approval queue | 24 hours |
| ROAS drop >15% from 30-day avg | ceo | Dashboard + auto-pause ads | 4 hours |
| New ad creative needed | ceo | Dashboard | 48 hours |
| Email campaign send (>500 recipients) | ceo | Dashboard approval queue | 24 hours |

### Finance Escalations

| Situation | Route To | Method | SLA |
|-----------|----------|--------|-----|
| Reconciliation discrepancy <$50 | Log only | Supabase | N/A |
| Reconciliation discrepancy $50-$500 | ceo | Dashboard | 48 hours |
| Reconciliation discrepancy >$500 | ceo | Dashboard + email alert | 24 hours |
| Nepal supplier payment due | operations-manager → ceo | WhatsApp → Dashboard | 1 week |
| Debt service payment reminder | ceo | Dashboard | 1 week |

## Contact Methods

| Role | Dashboard | WhatsApp | Email | Language |
|------|-----------|----------|-------|----------|
| ceo | Yes | No | chris@tibetanspirit.com | English |
| operations-manager | Yes (mobile) | Yes (primary) | jhoti@tibetanspirit.com | **Bahasa Indonesia** (formal register) |
| warehouse-manager | Yes | No | fiona@tibetanspirit.com | English |
| spiritual-director | No | No | hunlye@foresthermitage.org | English |
| mexico-fulfillment | No | No | omar@espiritutibetano.mx | English/Spanish |

## Bahasa Indonesia Communication Rules for operations-manager

When communicating with operations-manager, always use formal Bahasa Indonesia:
- Use **"Anda"** (formal you), never "kamu" (informal)
- Frame instructions as suggestions: **"Mungkin bisa..."** (Perhaps you could...)
- Use passive voice for softer tone
- Never cause loss of face — frame problems as situations to resolve together
- Mark urgent items with **"MENDESAK"** label
- Buddhist terminology stays untranslated: mala, thangka, dharma
