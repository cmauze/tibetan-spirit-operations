# COMMANDS.md — Skill Quick Reference

How to trigger skills with specific inputs. Each entry shows the skill name, what it does, and example invocations with parameters.

---

## Customer Service

### `/cs-triage` — Classify an incoming customer email and route it

```
Triage this customer email — classify it and tell me where it should go
```

```
Classify the latest unread email from shop@tibetanspirit.com
```

### `/cs-workflow` — Run the full CS email pipeline (triage → enrichment → draft → approval)

```
Process the unread customer emails — run the full CS workflow
```

```
Run CS workflow on the latest 5 emails from shop@tibetanspirit.com
```

### `/order-inquiry` — Look up order status and draft a customer response

```
Customer is asking about order #12345 — where is it?
```

```
Draft a response for a customer asking about tracking for order TS-2026-04-1892
```

---

## Shopify & Inventory

### `/shopify-query` — Query live Shopify data not yet in Supabase

```
How many units of SKU MALA-108-ROSE do we have in stock right now?
```

```
Pull the last 10 orders placed today from Shopify
```

### `/restock-calc` — Compute reorder points, quantities, and safety stock

```
Run restock calculations for all incense SKUs
```

```
What should we reorder for singing bowls given the 6-week lead time from Nepal?
```

### `/fulfillment-flag` — Flag fulfillment exceptions and route to the right team member

```
Review today's orders for any fulfillment exceptions
```

```
Flag the order with mixed domestic/international items for manual routing
```

---

## Finance & Reporting

### `/margin-reporting` — Weekly P&L, SKU-level profitability, margin alerts

```
Generate the weekly margin report
```

```
Show me which SKUs fell below margin floor this month
```

```
Run an ad-hoc margin comparison: Shopify DTC vs Etsy for Q1 2026
```

---

## Marketing & Catalog

### `/campaign-brief` — Generate a campaign brief with content tier classification

```
Draft a campaign brief for the Saga Dawa collection launch in May
```

```
Create a brief for a Losar New Year email — educational content about the holiday
```

### `/description-optimizer` — Evaluator-optimizer loop on product descriptions

```
Optimize the product description for the 7-metal singing bowl
```

```
Run the description optimizer on all thangka listings — score against the rubric and revise
```

---

## Research & Documentation

### `/wiki-research` — Deep research producing wiki articles

```
Research best practices for Shopify international shipping to Southeast Asia
```

```
Research incense sourcing certifications and authenticity standards
```

### `/web-harvest` — Extract web content into wiki raw sources

```
Harvest Shopify's GraphQL Admin API docs for the 2026-01 version
```

### `/wiki-query` — Answer questions from wiki knowledge

```
What do we know about our Nepal supplier lead times?
```

---

## Development

### `/brainstorming` → `/writing-plans` → `/subagent-driven-development`

Standard pipeline for any non-trivial implementation:

```
I want to build an automated daily inventory sync between Shopify and Supabase
```

### `/simplify` — Review and clean up changed code

```
/simplify
```

### `/code-review` — Review a pull request

```
/code-review 15
```

---

## Daily Operations

### `/morning-brief` — Gmail + Calendar daily brief

```
/morning-brief
```

### `/email-inbox` — Full email triage pipeline

```
/email-inbox
```

### `/journal-compose` — End-of-day journal entry

```
/journal-compose
```
