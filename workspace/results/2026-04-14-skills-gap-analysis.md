# Skills + Workflows Gap Analysis
**Date:** 2026-04-14
**Branch:** main
**Auditor:** Claude Code supervisor session (5 parallel Phase B subagents)

---

## Structural Audit Summary

Phase A passed with 28/30 checks green. Two gaps found: (1) `act-on-approved` skill is missing — called a critical gap in the handoff and confirmed absent; (2) `docs/ARCHITECTURE.md` and `docs/OPERATIONS-REFERENCE.md` structure diagrams still show `workflows/` as containing operational scripts, but scripts are in `scripts/` (documentation-only, no functional impact). **Major surprise:** the handoff's "Known Gaps" list for `lib/ts_shared/` is outdated — all 7 listed modules exist and are fully implemented, as are `tests/` with 10+ test files and `scripts/validate_skill.py`. The repo is significantly more built-out than the handoff expected.

---

## Asset Quality Ratings

### Agents

| Agent | Rating | Issues Found | Action |
|-------|--------|--------------|--------|
| cs-drafter | minor-updates | Missing `budget_usd` in frontmatter; CCPA/data-deletion protocol lives only in skill, not agent | Add frontmatter field; copy CCPA protocol summary to agent |
| finance-analyst | **rewrite** | COGS confidence labeling missing from report format; escalation criteria undefined (no pathway to Chris on anomalies); Dharma Giving not mentioned; word count 374 (target 500-700); no rule citations | Rewrite before first live run |
| fulfillment-manager | solid | Omar/Mexico not mentioned (may be intentional); could add operations-protocols.md citation | Ship as-is; note Omar gap for review |
| inventory-analyst | minor-updates | No rule citations; Shopify API not mentioned in data sources; PO draft workflow structure undefined | Add citations + Shopify API reference + PO JSON schema |
| marketing-strategist | solid | Doesn't explicitly cite marketing-discipline.md by name (content matches) | Ship as-is |
| catalog-curator | solid | Doesn't explicitly cite ecommerce-judgment.md by name (content matches) | Ship as-is |

### Skills

| Skill | Rating | Issues Found | Action |
|-------|--------|--------------|--------|
| cs-triage | minor-updates | Frontmatter missing: version, category, tags, model, estimated_tokens, depends_on; no example input/output | Update frontmatter; add 1 example |
| shopify-query | minor-updates | Frontmatter missing same fields; skill wraps REST API but shopify-api.md mandates GraphQL 2026-01 — inconsistency needs note | Update frontmatter; clarify REST vs GraphQL |
| act-on-approved | **MISSING** | Does not exist anywhere | Priority 1 build (see below) |

### Rules

| Rule | Lines | Role ID Compliance | Rating | Issues Found |
|------|-------|-------------------|--------|--------------|
| brand-voice | 33 | Clean | solid | None |
| cultural-sensitivity | 36 | **Violations**: "Chris", "Jothi", "Dr. Hun Lye" | minor-updates | Replace with `ceo`, `operations-manager`, `spiritual-director` |
| org-roles | 60 | Acceptable (person names canonical here) | solid | None |
| shopify-api | 31 | Minor: "Chris" → `ceo` | solid | 2 name instances on approval lines |
| cs-judgment | 41 | **Violations**: "Chris", "Jothi", "Fiona", "Dr. Hun Lye" + duplicates org-roles | minor-updates | Replace names with role IDs; replace team comm section with reference to org-roles.md |
| finance-judgment | 33 | Clean | solid | None |
| marketing-discipline | 56 | Clean | solid | Line 40: "escalate to Tier 3" unclear — should name role IDs |
| operations-protocols | 63 | **Violations**: "Chris", "Jothi", "Fiona", "Omar" + ~28 lines duplicate org-roles | minor-updates | Remove duplicated org-roles content; replace names with role IDs |
| ecommerce-judgment | 45 | Clean | solid | None |
| category-judgment | 47 | Minor: "Chris" → `ceo` | solid | 1 instance |

### Scripts

| Script | Rating | Issues Found | Action |
|--------|--------|--------------|--------|
| scripts/daily_summary.py | solid | None. Clean lib imports, Supabase write, Slack notify, cost logging, no secrets | Ship |
| scripts/weekly_pnl.py | solid | None. Pull→aggregate→format pattern, COGS confidence tracking, CEO review required | Ship |
| scripts/validate_skill.py | solid (bonus find) | Exists and is functional — checks frontmatter, sections, cultural anti-patterns, model routing | Extend to validate new required frontmatter fields |

---

## Gap Analysis: Missing Assets

### Priority 1 — Blocking (needed before any workflow runs end-to-end)

**1. `skills/act-on-approved/SKILL.md` + symlink**
- Why: Every approval-gated workflow (CS drafts, inventory POs, campaign briefs) needs a downstream execution skill. Without it, approved items sit in `task_inbox` with no execution path.
- Spec: Only executes when task status is `approved`; checks task_inbox before acting; never acts on `needs_review` or `auto_logged`; maps task_type to appropriate tool (Shopify API, Slack send, Gmail draft)
- Blocking: cs_email_drafts.py, inventory_alerts.py cannot complete their workflows without it

**2. `finance-analyst.md` rewrite**
- Why: Current version missing COGS confidence labeling (core requirement per finance-judgment.md), escalation criteria, Dharma Giving accounting, and is 40% below target word count
- Blocking: Running finance-analyst on live data without confidence labeling would produce reports that violate the project's own standards

### Priority 2 — Sprint 2 (needed for CS and inventory workflows)

**Scripts:**
- `scripts/cs_email_drafts.py` — CS triage → enrich → draft pipeline (references cs-drafter agent)
- `scripts/inventory_alerts.py` — Proactive stock monitoring with PO draft (references inventory-analyst agent)

**Skill updates (not blocking, but needed before Sprint 2 runs):**
- cs-triage/SKILL.md frontmatter: add version, category, tags, model, estimated_tokens, depends_on + 1 example
- shopify-query/SKILL.md frontmatter: same; plus clarify REST vs GraphQL discrepancy

**Agent updates:**
- cs-drafter.md: add budget_usd to frontmatter; add CCPA protocol summary
- inventory-analyst.md: add rule citations; add Shopify API data source; define PO draft JSON schema

**Rules cleanup (person names → role IDs):**
- cultural-sensitivity.md: 3 instances
- cs-judgment.md: 4 instances + remove team-comm duplication
- operations-protocols.md: 4 instances + remove org-roles duplication

**Docs fix:**
- docs/ARCHITECTURE.md line 113: update structure diagram — `workflows/` → empty placeholder, `scripts/` → operational Python scripts
- docs/OPERATIONS-REFERENCE.md line 186: same fix

### Priority 3 — Sprint 3+ (campaign, product descriptions, eval)

**Scripts:**
- `scripts/campaign_brief.py` — Campaign brief generation (references marketing-strategist agent)
- `scripts/product_descriptions.py` — Evaluator-optimizer loop (references catalog-curator agent)

**Shared skills (currently none exist — referenced in ARCHITECTURE.md):**
- `skills/brand-guidelines/SKILL.md` — Shared by cs-drafter, marketing-strategist, catalog-curator
- `skills/product-knowledge/SKILL.md` — Shared by cs-drafter, catalog-curator
- `skills/escalation-matrix/SKILL.md` — Shared by all agents
- `skills/tibetan-calendar/SKILL.md` — Seasonal sensitivity (Losar, Saga Dawa, Vesak)
- `skills/supabase-ops-db/SKILL.md` — Shared DB query patterns

**Infrastructure:**
- Supabase three-layer schema migration (Registry + Runtime + Eval layers per DEV-PLAN Prompt 1D)
- `config.yaml` files for each workflow script
- Expand `scripts/validate_skill.py` to check new required frontmatter fields (version, category, tags, estimated_tokens)

---

## Recommended Build Order

1. **Rewrite finance-analyst.md** — highest risk to run as-is; no code required, just agent definition
2. **Build `skills/act-on-approved/`** — unblocks every approval-gated workflow
3. **Update skill frontmatter** (cs-triage, shopify-query) — quick, unblocks validate_skill.py checks
4. **Fix rules person-name violations** (cultural-sensitivity, cs-judgment, operations-protocols) — consistency + compliance
5. **Fix docs structure diagrams** (workflows/ → scripts/) — low effort, removes confusion
6. **Add agent minor-updates** (cs-drafter budget field, inventory-analyst citations + PO schema) — low risk
7. **Build scripts/cs_email_drafts.py** — first end-to-end workflow test
8. **Build scripts/inventory_alerts.py** — second workflow
9. **Build shared skills** (brand-guidelines, product-knowledge, escalation-matrix) — after Sprint 2 scripts proven
10. **Supabase schema migration** — when eval layer needed for Sprint 3

---

## Do NOT Build Yet

- **Dashboard** (Paperclip-inspired PWA) — no live workflows to monitor yet
- **Railway deployment** — local execution sufficient until Sprint 2 complete
- **Full eval layer** (Langfuse + evals/ expansion) — basic evals exist; defer until workflows proven
- **56 total skills** — DEV-PLAN lists this as long-term target, not Sprint 1-2 scope
- **All shared skills** — wait until at least 2 agent workflows are stable; shared surfaces should emerge from real usage, not be specced in advance
- **Notion integration** (notion_ops.py, notion_config.py exist but unused) — defer until cost dashboard is prioritized
- **campaign_brief.py / product_descriptions.py** — Sprint 3; blocks on Sprint 2 proving out the pattern

---

## Bonus: What the Handoff Got Wrong (Good News)

The handoff's "Known Gaps" section listed these as missing. All exist and are solid:

| Item | Handoff Said | Reality |
|------|-------------|---------|
| lib/ts_shared/claude_client.py | Missing | Present — SkillMetadata Pydantic model, three-tier loader, prompt caching, cost calculator |
| lib/ts_shared/org.py | Missing | Present — ORG.md parser, role resolver, caching |
| lib/ts_shared/notifications.py | Missing | Present |
| lib/ts_shared/cost_tracker.py | Missing | Present |
| lib/ts_shared/views.py | Missing | Present |
| lib/ts_shared/notion_ops.py | Missing | Present |
| lib/ts_shared/supabase_client.py | Unconfirmed | Present — env-var based, no secrets |
| tests/ directory | Missing | Present — 10+ test files + evals/ subdirectory |
| scripts/validate_skill.py | Unconfirmed | Present and functional |

**The shared library is complete. The test suite exists. Sprint 1 was already largely built before this audit.**

---

## Status: Awaiting Chris Review

Build list is ordered and ready. No implementation should begin until Chris reviews this document and approves the priority sequence.
