# Sprint S2-K: Wiki Deepening — Tier 1

**Tool:** Claude Code (Opus)
**Parallel Group:** PG-2 (runs in parallel with S2-W and S2-D)
**Prerequisites:** Sprint S1 Prompt 0A complete (expanded frontmatter schema)
**Complexity:** Moderate

---

## Overview

Deepen the 8 most critical SKILL.md files from ~35% stub depth to 100% production quality. These skills block active workflows — they are loaded into Claude's system prompt when workflows run. Quality here directly determines AI output quality.

**Zero file overlap with other PG-2 agents.** This sprint only modifies `skills/*/SKILL.md` files. No Python code, no Supabase, no dashboard.

---

## Dev Prompt

```
Read CLAUDE.md completely — especially the "Skills = Agent Knowledge Base" section
and the "SKILL.md Frontmatter Schema" specification.
Read ORG.md for role definitions and contact methods.
Read SYSTEM-STATUS.md for database schemas (table names, column names, data types).

Your job: deepen 8 SKILL.md files to production quality. Each file must have:

1. YAML frontmatter with ALL fields populated:
   - version: "1.0.0" (upgrade from 0.1.0 — these are now production)
   - All fields from Sprint S1 0A expansion PLUS:
   - graduation_criteria: {min_invocations: 200, max_error_rate: 0.02, min_days: 30}
   - escalation_rules: (specific conditions → role mappings)
   - max_tokens: (appropriate for this skill's expected output length)

2. Markdown body with these sections:
   - ## Purpose (2-3 sentences: what this skill does, when Claude should use it)
   - ## Decision Logic (decision tree with SPECIFIC thresholds — dollar amounts,
     time limits, quantities — NOT vague "large" or "significant")
   - ## Output Format (JSON schema or structured format with field descriptions)
   - ## Response Templates (3-5 COMPLETE examples — full text, not outlines)
   - ## Escalation Rules (when to bypass normal flow, mapped to ORG.md roles)
   - ## Anti-Patterns (things to NEVER do, with concrete bad examples)
   - ## Cultural Notes (if applicable — Buddhist terminology, sensitivity rules)
   - ## Supabase References (table.column names used by this skill — must be valid)

3. Constraints:
   - Under 500 lines per skill
   - All role references use ORG.md IDs (ceo, operations-manager, etc.)
   - All table/column references match SYSTEM-STATUS.md schemas
   - Response templates are IN CHARACTER — they sound like Tibetan Spirit, not generic AI
   - Buddhist terms stay untranslated: mala, thangka, dharma, sangha, puja, mandala
   - Never use: exotic, mystical, oriental, trinket, cheap, primitive, hippie

Process these 8 skills. Commit after completing all 8:

=== SKILL 1: shared/brand-guidelines ===
Voice: knowledgeable, respectful, warm, transparent
Define: tone by context (product descriptions, CS, marketing, internal)
Include: word choice guide (preferred vs forbidden), sentence structure patterns,
Buddhist terminology preservation rules, 5% Dharma Giving framing

=== SKILL 2: shared/product-knowledge ===
Product taxonomy with categories, authenticity markers per category,
care instructions per product type, sourcing narrative (Nepal, Tibet, India),
price range expectations by category, common customer questions per product type

=== SKILL 3: shared/escalation-matrix ===
Full routing table: condition → role → contact method → SLA
Include: dollar thresholds (refund >$100 → ceo), topic routing
(practice questions → spiritual-director), language routing
(Bahasa messages → operations-manager), severity levels

=== SKILL 4: shared/channel-config ===
Shopify Growth plan: $79/mo, 2.5%+$0.30 transaction fees, 10 inventory locations
Future channels: Etsy (10% fee), Amazon (30% referral), Wholesale (0%)
Store URLs, API versions, webhook endpoints
Fee calculation formulas for each channel

=== SKILL 5: customer-service/ticket-triage ===
4-tier classification: AUTO_RESPOND, ESCALATE_OPERATIONS, ESCALATE_SPECIALIST, URGENT
Decision tree with specific triggers (chargeback→URGENT, practice question→SPECIALIST)
Reference Intercom as the helpdesk platform (not Re:amaze)
Bilingual output: English customer response + Bahasa Indonesia internal notes
Include sample classifications for 10+ email types

=== SKILL 6: finance/cogs-tracking ===
COGS confidence levels: confirmed (supplier invoice), estimated (category %), unknown
Category-level fallback estimates (from seed_cogs_from_model.py values)
Monthly review workflow for refining estimates
Exchange rate handling (NPR/USD, flag >5% monthly change)
Supabase references: products.cogs_confirmed, products.cogs_estimated,
products.cogs_confidence, products.freight_per_unit, products.duty_rate

=== SKILL 7: finance/margin-reporting ===
P&L structure: revenue - COGS - channel fees = gross profit
Margin calculation by product, category, and channel
Materialized view references: channel_profitability_monthly, product_margin_detail
Week-over-week and month-over-month trend analysis
Red flags: margin below 30%, negative margin products, fee ratio anomalies

=== SKILL 8: operations/inventory-management ===
Stock status tiers: stockout (0), critical (<safety_stock), reorder (<reorder_trigger_qty), healthy
Reorder point calculation: avg_daily_sales × lead_time_days + safety_stock
PO template format with supplier, quantities, unit costs
Shopify inventory locations API reference
Supabase references: inventory_extended.*, inventory_health view

Commit: "feat: deepen 8 Tier 1 skills to production quality (v1.0.0)"
```

---

## Test Prompt

```
Verify all 8 Tier 1 skills meet production quality standards.

=== VALIDATION SCRIPT ===
1. python scripts/validate_skill.py skills/shared/brand-guidelines/SKILL.md → PASS
2. python scripts/validate_skill.py skills/shared/product-knowledge/SKILL.md → PASS
3. python scripts/validate_skill.py skills/shared/escalation-matrix/SKILL.md → PASS
4. python scripts/validate_skill.py skills/shared/channel-config/SKILL.md → PASS
5. python scripts/validate_skill.py skills/customer-service/ticket-triage/SKILL.md → PASS
6. python scripts/validate_skill.py skills/finance/cogs-tracking/SKILL.md → PASS
7. python scripts/validate_skill.py skills/finance/margin-reporting/SKILL.md → PASS
8. python scripts/validate_skill.py skills/operations/inventory-management/SKILL.md → PASS

=== VERSION CHECK ===
9. grep "version:" skills/shared/brand-guidelines/SKILL.md → "1.0.0"
   (repeat for all 8 skills)

=== CONTENT QUALITY ===
10. Each skill has Decision Logic section with dollar/quantity thresholds
    grep -c "\\$[0-9]" each SKILL.md → at least 1 match per relevant skill
11. Each skill has 3+ response templates
    grep -c "### Template" or "### Example" each SKILL.md → ≥3
12. No hardcoded names: grep -r "Jothi\|Jhoti\|Fiona\|Dr. Hun Lye\|Omar" skills/ → 0 matches
13. No forbidden words: grep -ri "exotic\|mystical\|oriental\|trinket" skills/ → 0 matches
14. Cultural terms preserved: grep -c "mala\|thangka\|dharma\|sangha" relevant skills → >0

=== LINE COUNT ===
15. wc -l skills/shared/brand-guidelines/SKILL.md → <500 lines
    (repeat for all 8)

=== CROSS-REFERENCE VALIDITY ===
16. python scripts/validate_cross_refs.py → zero violations
    (ensures table.column references match actual Supabase schema)

=== STRUCTURAL CHECK ===
17. Each skill has these sections (grep for ## headers):
    - Purpose, Decision Logic, Output Format, Response Templates,
      Escalation Rules, Anti-Patterns

=== INTERCOM REFERENCE ===
18. grep -i "intercom" skills/customer-service/ticket-triage/SKILL.md → matches found
    grep -i "re:amaze\|reamaze" skills/ → 0 matches (old platform removed)

=== FRONTMATTER COMPLETENESS ===
19. For each skill, verify frontmatter has:
    graduation_criteria, escalation_rules, max_tokens
    (these were deferred in S1 0A, should now be populated)
```
