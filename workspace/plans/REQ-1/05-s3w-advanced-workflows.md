# Sprint S3-W: Advanced Workflows + Reliability

**Tool:** Claude Code (Opus)
**Parallel Group:** PG-3 (runs in parallel with S3-D)
**Prerequisites:** S2-W complete (all Sprint 2 workflows working), S2-K complete (Tier 1 skills at v1.0.0)
**Complexity:** Moderate

---

## Overview

Build the campaign brief generator and product description optimizer (the most sophisticated workflow — evaluator-optimizer loop). Then run a reliability pass across all 6 workflows to ensure they're production-ready.

---

## Dev Prompt

```
Read CLAUDE.md, ORG.md, DEV-PLAN.md.
Read all lib/ts_shared/ modules.
Read workflows/daily_summary/run.py and workflows/weekly_pnl/run.py for established patterns.

Execute 3 prompts. Commit after each.

=== PROMPT 4A: Campaign Brief Generator ===

Read skills/shared/brand-guidelines/SKILL.md, skills/shared/tibetan-calendar/SKILL.md.

Create `workflows/campaign_brief/`:

config.yaml:
  name: campaign_brief
  schedule: "0 8 * * 1"  # Monday 8am Denver
  model: claude-sonnet-4-6
  skills: [shared/brand-guidelines, shared/tibetan-calendar, shared/channel-config]
  requires_approval: true
  assignee: ceo
  priority: P2

run.py:
  Step 1 (Python): Query top 20 products by revenue (30 days) from orders + products.
  Pull seasonal context from tibetan-calendar skill (upcoming Buddhist dates).
  Check inventory_extended for surplus items (available_to_sell > 2x avg monthly sales).
  Step 2 (Sonnet): Generate campaign brief:
    - Campaign theme (tied to seasonal context or product story)
    - Target segment (from customer_profiles segments)
    - 3 email subject line options
    - Body outline (3-5 key points)
    - Product selection (5-8 SKUs with reasoning)
    - Recommended send date/time
  Step 3: Write to task_inbox (needs_review, assignee=ceo).
  Log workflow_run and cost. Send Slack to ceo.

Write test: tests/evals/test_campaign_brief.py
- Verify output JSONB has required fields (theme, target_segment, subject_lines, products)
- Verify products referenced exist in Supabase products table
- Verify no cultural anti-patterns in theme/subject lines

Commit: "feat: add campaign_brief workflow"

=== PROMPT 4B: Product Description Optimizer (Evaluator-Optimizer) ===

Read skills/shared/brand-guidelines/SKILL.md, skills/shared/product-knowledge/SKILL.md.

Create `workflows/product_descriptions/`:

config.yaml:
  name: product_descriptions
  schedule: manual  # Triggered on demand
  model: claude-sonnet-4-6
  skills: [shared/brand-guidelines, shared/product-knowledge]
  requires_approval: true
  assignee: ceo
  priority: P2
  pattern: evaluator_optimizer

run.py:
  Accept --product-ids argument (comma-separated Shopify IDs or "all" for batch).

  For each product:
    Step 1 GENERATE (Sonnet): Create product description.
      Input: title, SKU, price, category (inferred from title/handle),
      current Shopify description (if available via API).
      Output: {title, description, meta_description, key_features, care_instructions}

    Step 2 EVALUATE (Sonnet as evaluator): Score on 5 dimensions (1-10 each):
      - SEO: keywords, meta description, title optimization
      - Conversion: benefit-focused, clear CTA, addresses objections
      - Brand Voice: matches Tibetan Spirit tone, warm, knowledgeable
      - Accuracy: product details correct, materials/dimensions plausible
      - Readability: clear structure, scannable, appropriate length

    Step 3 ITERATE: If any dimension <7, feed evaluation back to generator.
      Include: which dimensions failed, evaluator reasoning, specific suggestions.
      Max 3 iterations. Log iteration count and scores per iteration.

    Step 4 OUTPUT: Write final description + all scores to task_inbox.
      Include iteration history in output JSONB.

  For batch mode (--product-ids all):
    Use sequential processing (not parallel) to stay within budget.
    Create one task_inbox entry per product.

Write test: tests/evals/test_product_descriptions.py
- Test on 3 products with known categories
- Verify eval scores are present in output
- Verify no cultural anti-patterns
- Verify Buddhist terms preserved

Commit: "feat: add product_descriptions evaluator-optimizer workflow"

=== PROMPT 4C: Reliability Pass ===

Run reliability audit across ALL 6 workflows:

1. Create `scripts/run_all_workflows.py`:
   - Accept --dry-run flag
   - In dry-run mode: import each workflow's run module, load config,
     verify imports resolve, verify Supabase queries reference valid tables
   - In live mode: run each workflow sequentially, capture results
   - Print summary: workflow name, status, cost, duration

2. Verify all imports resolve:
   python -c "import workflows.daily_summary.run"
   python -c "import workflows.weekly_pnl.run"
   python -c "import workflows.cs_email_drafts.run"
   python -c "import workflows.inventory_alerts.run"
   python -c "import workflows.campaign_brief.run"
   python -c "import workflows.product_descriptions.run"

3. Run python scripts/validate_cross_refs.py → zero violations

4. Run all eval suites: pytest tests/evals/ -v

5. Update workflow_health entries for all 6 workflows.
   For each: set status='healthy', last_run_at=now(), last_result='passed_reliability'.

6. Verify config.yaml files are consistent:
   - All have required fields: name, schedule, model, requires_approval
   - All assignee values are valid ORG.md role IDs
   - All skill references resolve to existing SKILL.md files

Commit: "feat: reliability audit — all workflows validated and healthy"
```

---

## Test Prompt

```
=== CAMPAIGN BRIEF ===
1. python workflows/campaign_brief/run.py → creates task_inbox entry
2. Inspect output JSONB:
   - Has fields: theme, target_segment, subject_lines (array), products (array)
   - products array has SKU and title fields
3. Verify products exist: for each SKU in output, query products table → all found
4. Cost check: total_cost_usd < $0.15
5. No "exotic"/"mystical" in theme or subject lines
6. pytest tests/evals/test_campaign_brief.py → passes

=== PRODUCT DESCRIPTIONS ===
7. Pick 3 product IDs from: SELECT shopify_id FROM products WHERE price > 20 LIMIT 3
8. python workflows/product_descriptions/run.py --product-ids X,Y,Z
   → creates 3 task_inbox entries
9. Inspect one output JSONB:
   - Has: title, description, meta_description, key_features, care_instructions
   - Has: eval_scores with 5 dimensions, iteration_count
   - All eval scores ≥ 7 (or iteration_count = 3 if still below)
10. No "exotic"/"mystical" in any description
11. Buddhist terms (mala, thangka, etc.) preserved if relevant to product
12. pytest tests/evals/test_product_descriptions.py → passes

=== RELIABILITY PASS ===
13. python scripts/run_all_workflows.py --dry-run → all 6 workflows pass
14. python scripts/validate_cross_refs.py → zero violations
15. pytest tests/evals/ → all suites pass
16. SELECT slug, status FROM workflow_health → all 6 show 'healthy'

=== FULL SUITE ===
17. pytest tests/ → ALL tests pass (existing + new)
```
