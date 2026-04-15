---
name: practice-inquiry
description: Handle Buddhist practice questions from customers and escalate to spiritual-director for specialized guidance
version: "0.1.0"
category: customer-service
tags: [dharma, practice, escalation]
author: operations-team
model: sonnet
cacheable: true
estimated_tokens: 450
phase: 1
depends_on: [shared/brand-guidelines, shared/product-knowledge]
external_apis: []
cost_budget_usd: 0.15
---

# Practice Inquiry Routing Skill

## Overview
Respond to customer inquiries about Buddhist practice, meditation techniques, and spiritual questions, with clear escalation path to spiritual-director for specialized guidance.

## Key Sections

### Inquiry Classification
- Identify practice category (meditation, ritual, daily practice, philosophy, etc.)
- Assess complexity level (general information vs. specialized guidance)
- Note if customer is experienced practitioner or beginner

### Initial Response Options
- Provide general educational information for straightforward questions
- Share relevant passages or context from Buddhist teachings
- Reference product benefits aligned with practice

### Escalation to spiritual-director
- Recognize when question requires specialized expertise
- Document inquiry details and context
- Prepare escalation summary with customer contact
- Set expectations for response timeline

### Follow-up Communication
- Confirm escalation with customer
- Provide interim guidance if appropriate
- Close loop once spiritual-director provides guidance

## Scope Boundaries
- Can address general practice questions and product recommendations
- Escalate: medical claims, personal spiritual guidance, advanced teachings

## Dependencies
- Escalates to: spiritual-director (via escalation-matrix)
- References: product-knowledge for practice context

## Success Metrics
- Customer receives helpful response or successful escalation
- spiritual-director has complete context for specialized inquiry
