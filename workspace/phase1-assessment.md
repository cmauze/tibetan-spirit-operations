# Phase 1 Assessment — tibetan-spirit-ops Restructure
**Date:** 2026-04-14  
**Status:** Complete inventory and gap analysis  
**Next Action:** Chris's approval on recommendations before Phase 2 execution

---

## 1. Legacy agents/ Directory (6 departments + shared)

### Inventory

| Department | Skills Count | Soul.md Present | Recommendation |
|---|---|---|---|
| **customer-service** | 6 skills | Yes (4.1 KB) | PARTIALLY MIGRATE — soul.md contains operationally critical principles not in .claude/rules/ |
| **finance** | 8 skills | Yes (1.5 KB) | PARTIALLY MIGRATE — soul.md contains decision-support philosophy + dharma-giving principles unique to this agent |
| **marketing** | 10 skills | Yes (1.6 KB) | PARTIALLY MIGRATE — soul.md contains brand restraint + authenticity-first principles critical to Tibetan Spirit positioning |
| **operations** | 7 skills | Yes (1.5 KB) | PARTIALLY MIGRATE — soul.md contains supplier relationship + communication protocols unique to cross-regional ops |
| **ecommerce** | 7 skills | Yes (1.6 KB) | PARTIALLY MIGRATE — soul.md contains practice-context-first framing + cross-channel consistency rules |
| **category-management** | 8 skills | Yes (1.4 KB) | PARTIALLY MIGRATE — soul.md contains long-term category health + artisan protection philosophy |
| **shared/** | 6 resource folders | No | ARCHIVE — content already covered by .claude/rules/ (brand-voice, cultural-sensitivity) or Supabase config |

### Soul.md Assessment

**Critical Finding:** Each agent's `soul.md` contains unique philosophical grounding that is NOT currently reflected in `.claude/rules/` files:

- **finance/soul.md**: "Accuracy Over Speed" + "Surface Anomalies Immediately" + Dharma Giving framing as accounting (not marketing)
- **operations/soul.md**: Multilingual team communication protocols (Bahasa Indonesia formality rules, Chinese notation style, Spanish email protocols) + supplier relationship philosophy
- **customer-service/soul.md**: "Never Guess on Sacred Matters" escalation decision tree + multilingual internal communication rules
- **marketing/soul.md**: Frequency discipline rules (2 promos/month, 3 ad impressions/week, NO SMS) + "No Urgency Tactics for Sacred Goods" positioning
- **ecommerce/soul.md**: "Practice Context First" framing (meditation instrument before material composition) + cross-channel consistency enforcement
- **category-management/soul.md**: "Sacred Significance of Every Category" + supplier margin protection philosophy + anti-commoditization stance

**Status:** `.claude/rules/` currently has only brand-voice.md and cultural-sensitivity.md. Missing domain-specific judgment frameworks for each agent's decision logic.

### Skills Assessment

**Sample check (customer-service/skills/order-inquiry):** SKILL.md has well-structured metadata (version, category, tags, cost_budget, phase, depends_on, external_apis) and detailed workflow. This is valuable IP that extends beyond soul.md.

**Finding:** Legacy skills have richer contextual metadata (cost budgets, token estimates, dependencies, phase indicators) than any current .claude/ skills. Validation report shows systematic errors: missing "output format" and "decision logic" sections across many legacy skills.

---

## 2. .claude/ Native Structure

### Actual Contents

| Directory | Contents | Status |
|---|---|---|
| **.claude/agents/** | cs-drafter.md, finance-analyst.md | **INCOMPLETE** — Only 2 of 6 agents from CLAUDE.md roster have definitions |
| **.claude/skills/** | act-on-approved/, cs-triage/, shopify-query/ | **SPARSE** — Only 3 skills; no comprehensive domain skills from legacy agents |
| **.claude/rules/** | brand-voice.md, cultural-sensitivity.md, shopify-api.md | **FOUNDATIONAL** — Missing: domain-specific judgment frameworks (finance, ops, marketing, etc.) |
| **.claude/hooks/** | log-activity.sh, session-context.sh, slack-notify.sh | **ACTIVE** — 3 hooks; _archive/ subfolder suggests old hooks were retired |
| **.claude/evals/** | Empty | **UNUSED** |
| **.claude/settings.json** | Present | **CONFIGURED** |

### Agent Roster vs. Definition Gap

**CLAUDE.md lists 6 agents:**
1. Fulfillment Manager (Opus) — **NO .md file**
2. Inventory Analyst (Opus) — **NO .md file**
3. CS Drafter (Opus) — ✓ cs-drafter.md exists
4. Marketing Strategist (Opus) — **NO .md file**
5. Catalog Curator (Opus) — **NO .md file**
6. Finance Analyst (Opus) — ✓ finance-analyst.md exists

**Gap:** 4 of 6 agents lack definition files in .claude/agents/. This blocks anyone trying to restore agent execution using CLAUDE.md as a guide.

---

## 3. Root-Level Files Assessment

### DEV-PLAN.md (1,424 lines)

**Summary:**  
Comprehensive development plan dated 2026-03-29. Covers:
- Three-layer architecture (Registry, Runtime, Eval)
- HITL pattern with Supabase as state machine
- Dashboard as control plane (Vercel PWA)
- Six agent team with $2.00/agent budget + $0.50/finance
- Multi-company support (tibetan-spirit, personal, cgai, norbu)
- Sprint breakdown: MVP (S1-S3), post-MVP (S4+)
- Playbook references in temp/planning/ subdirectory
- Risk mitigations and future integrations table

**Freshness Assessment:**
- **ACTIVE & CURRENT** — Last updated 2026-03-29 (15 days ago)
- References concrete March 29 decisions (Shopify API 2026-01, Railway consolidation, Intercom/Zendesk helpdesk decision narrowed)
- TODO items present but not stale (Slack workspace token, Supabase Pro upgrade before dashboard goes live, financial model precision)
- **No signs of abandonment** — Contains approval status, owner (Chris), locked decisions with rationales

**Assessment:** This is the operational north star. It's being actively referenced (workspace/plans/REQ-1 and REQ-1b follow this structure). Recommend keeping at root, with a reference added to CLAUDE.md and ARCHITECTURE.md (when created).

### ORG.md (56 lines)

**Summary:**  
Role directory with 6 roles, each with language/channel/approval mappings:
- ceo (Chris) — Slack/Dashboard, English
- operations-manager (Jothi) — Slack/Dashboard, Bahasa Indonesia (formal)
- customer-service-lead — TBD (Asheville hire)
- warehouse-manager (Fiona) — Dashboard only, Chinese (Mandarin)
- spiritual-director (Dr. Hun Lye) — Email only, English
- mexico-fulfillment (Omar) — Email only, Spanish

**Assessment:**
- **ACTIONABLE & REFERENCED** — Agents/skills use this for role resolution
- **Incomplete:** customer-service-lead is "TBD" (though cs-drafter.md was written assuming this role exists)
- **Recommendation:** Move to `.claude/rules/org-roles.md` (consolidate with other governance rules) OR keep at root if it's used as canonical employee directory

**Status:** This should stay accessible but could migrate to docs/ or .claude/rules/ depending on whether it's API-referenced by agents.

### SYSTEM-STATUS.md (30,655 bytes)

**Summary:**  
Technical reference dated 2026-03-29. Contains:
- Live connections table (Supabase ✓, Shopify ✓, Anthropic key ✓, others placeholder)
- Data in Supabase (19,403 orders, 559 products, COGS fields unpopulated)
- Scripts inventory (3 verified: backfill_shopify.py, import_orders_csv.py, test_shopify_connection.py)
- Schema deep dive (full table definitions, constraints, materialized views)
- API key reference (project IDs, access patterns)

**Assessment:**
- **SEMI-GENERATED** — Started from live state (marked "Generated 2026-03-29 from live Supabase queries and codebase inspection") but hand-maintained content (rationales, notes)
- **Stale Risk:** Last updated 2026-03-29; hasn't been refreshed with live schema state since then. COGS fields are still noted as "unpopulated" — need to verify current state
- **Sensitive Content:** Contains raw project IDs, API versions. Should NOT be committed if live credentials are embedded
- **Recommendation:** Convert to generated/automated output (add to post-commit hook or CI/CD pipeline). Move sensitive bits to .env.example. Keep human-readable portions in docs/TECHNICAL-REFERENCE.md

### validation-report.json (16,081 bytes)

**Assessment:**
- **GENERATED OUTPUT** — JSON validation report from legacy skill scanner
- **Stale:** Dated from when validation tool ran (paths reference `/Users/chrismauze/cm/code/` — note the extra `/cm/` layer that's no longer in current path structure)
- **Current relevance:** Tests for missing SKILL.md sections (output format, decision logic, phase behavior) across 50+ legacy skills. All show failures, indicating legacy skills don't match current validation schema
- **Recommendation:** Delete. This is output, not source. If regenerated, the schema expectations have changed. Include new validation in Phase 2 tooling.

---

## 4. workspace/ Directory Structure

### Current State
- ✓ **plans/** — Contains REQ-1, REQ-1b with detailed planning docs
- ✗ **research/** — MISSING
- ✗ **results/** — MISSING
- ✗ **handoffs/** — MISSING
- ✗ **scratch/** — MISSING (though .gitignore references workspace/scratch/)
- ✗ **archive/** — MISSING (though .gitignore references _archive/ at root)

### Gap Analysis

**Missing from standard PARA-inspired workspace structure:**
| Directory | Purpose | Status |
|---|---|---|
| research/ | Decision support, competitor analysis, market research | MISSING |
| results/ | Outputs (reports, dashboards, scripts) ready for production | MISSING |
| handoffs/ | Agent handoff docs, context transfers, knowledge retention | MISSING |
| scratch/ | Ephemeral work, drafts, experimental output (git-ignored) | MISSING |

**Recommendation:** Create workspace/{research, results, handoffs, scratch} directories as part of Phase 2A. Populate with guidance docs (e.g., workspace/research/README.md: "Save competitive analysis, market research, autoresearch outputs here").

---

## 5. Stale Path References

### Search Results

**Scope of search:** grep across .md, .py, .yaml, .json files for: `brain/`, `~/brain/`, `cmauze/brain`, `/harness/`, `recipe-`

**Findings:**
- ✗ **No stale `/harness/` references** — Clean
- ✗ **No stale `cmauze/brain` references** — Clean
- ✗ **No stale `recipe-` prefix references** — Clean
- ✓ **`~/brain/` references FOUND in workspace/plans/**
  - File: workspace/plans/REQ-1b/00-overview.md (multiple mentions of `~/brain/` rebuild)
  - File: workspace/plans/REQ-1b/02-phase-0a-core-structure.md (extensive references to ~/brain/ PARA structure)
  - **Status:** These are in planning docs, not active code. They reference a FUTURE migration (Chris's personal brain vault), not tibetan-spirit-ops. No action needed — these are archive/planning context.

**Assessment:** Repo is clean of stale infrastructure references. No migration needed for active code.

---

## 6. workflows/ Directory Assessment

### Structure

```
workflows/
├── daily_summary/
│   ├── config.yaml
│   └── run.py (8,074 bytes)
└── weekly_pnl/
    ├── config.yaml
    └── run.py (12,929 bytes)
```

### Type & Implementation

Both are **Python scripts with YAML config** (legacy HardhatPM style), NOT Claude workflow SKILL.md files.

**daily_summary/run.py:**
- Imports: supabase, anthropic, slack, datetime, json
- Logic: Queries Supabase orders from last 24h, calls Anthropic Claude API with system prompt, formats summary, posts to Slack
- **Dependencies:** ANTHROPIC_API_KEY, SUPABASE credentials, SLACK_BOT_TOKEN
- **Functionality:** Appears complete but not deployed (server not running per SYSTEM-STATUS.md)

**weekly_pnl/run.py:**
- Imports: supabase, anthropic, datetime, json, pandas, logging
- Logic: Queries Supabase orders + COGS data, calls Anthropic for P&L analysis, writes to Supabase task_inbox, logs to file
- **Dependencies:** Same as daily_summary + pandas
- **Functionality:** Similar state (not deployed)

### Functional Status

- **Referenced in:** DEV-PLAN.md (Part 1, architecture section) as "standalone Python workflow scripts triggered by Railway cron jobs"
- **Deployment:** Neither is active per SYSTEM-STATUS.md ("server not deployed")
- **Current Role:** These are **draft implementations** awaiting:
  - Railway cron job configuration (DEV-PLAN.md S1 task)
  - Env var setup (.env configuration)
  - Supabase task_inbox table creation (mentioned as deployed but empty)

### Recommendation

| Item | Action | Rationale |
|---|---|---|
| config.yaml (both) | ARCHIVE or DELETE | Deprecated HardhatPM config format; replaced by .claude/ structure |
| run.py (both) | RETAIN in Phase 2E | These are valuable workflow implementations; need to be validated against new agent/skill schema before deployment |

---

## 7. .gitignore Assessment

### Current Exclusions
✓ Standard Python/Node/IDE ignores (good coverage)  
✓ Secrets: .env, *.pem, *.key, credentials.json  
✓ Generated: validation-report.json, /data/  
✓ Temp: temp/, workspace/scratch/, scratch/  
✓ Claude-local: .claude/settings.local.json, .claude/mcp-settings.json

### Gaps

| Pattern | Current | Recommendation |
|---|---|---|
| **_archive/** | Not excluded | Add `_archive/` — this folder exists at root and contains deprecated content |
| **workspace/scratch/** | Included | Good — ephemeral work ignored |
| **deliverables/** | Not excluded | Ambiguous: is this generated (should ignore) or version-controlled (should track)? |
| **.env.example** | Not mentioned | ADD — best practice for credential management |
| **workspace/archive/** | Not excluded | Add when structure created (Phase 2A) |
| **logs/** | Partially (*.log) | Should add `/logs/` directory to be safe |

### Assessment

**Current .gitignore is 70% complete.** Main gaps are root-level _archive/ and clarification on deliverables/.

---

## Summary: Recommended Actions for Chris's Approval

### Tier 1: Block Phase 2 Start (Required decisions)

1. **Agent Definition Files (CRITICAL)**
   - **Issue:** 4 of 6 agents in CLAUDE.md lack .md definitions in .claude/agents/
   - **Decision needed:** Migrate Fulfillment Manager, Inventory Analyst, Marketing Strategist, Catalog Curator from legacy agents/ to .claude/agents/, or formally deactivate them
   - **Impact:** Without this, no one can restore agent execution following CLAUDE.md

2. **Legacy Soul.md Content Preservation**
   - **Issue:** Each soul.md contains unique philosophical/operational principles NOT in .claude/rules/
   - **Decision needed:** Extract soul.md content into new rule files (finance-judgment.md, operations-protocols.md, marketing-discipline.md, etc.) OR retain legacy soul.md files for reference and document that they're canonical
   - **Impact:** Without this, team loses domain-specific decision frameworks

3. **Stale validation-report.json**
   - **Decision needed:** Delete this file; regenerate only if Phase 2E tooling creates new validation schema
   - **Impact:** Currently incorrect (paths wrong, expectations stale)

### Tier 2: Phase 2A/2B Input (Planning clarity)

4. **workspace/ Structure**
   - Create research/, results/, handoffs/, scratch/ subdirectories
   - Add README.md to each explaining purpose and examples
   - **Timing:** Phase 2A

5. **Root-level docs consolidation**
   - Clarify: Does ORG.md stay at root (for employee directory) or migrate to .claude/rules/org-roles.md (for agent access)?
   - **Timing:** Phase 2B

6. **.gitignore update**
   - Add _archive/, workspace/archive/
   - Add .env.example pattern
   - Clarify deliverables/ scope
   - **Timing:** Phase 2G+H

### Tier 3: Post-Phase 2 (Automation/infrastructure)

7. **SYSTEM-STATUS.md → Generated Output**
   - Convert from hand-maintained document to CI/CD output
   - Add post-commit hook or GitHub Actions to refresh live connection status
   - Move sensitive content to .env.example
   - **Timing:** Phase 2B (infrastructure)

8. **workflows/daily_summary and weekly_pnl**
   - Validate against new agent/skill schema
   - Configure Railway cron jobs (defer to S2 if not in S1 scope)
   - **Timing:** Phase 2E (validation); S1/S2 (deployment)

### Tier 4: Information Only (Already good)

- ✓ DEV-PLAN.md is active and current; no action needed
- ✓ CLAUDE.md is accurate for active agents; update after agent migration
- ✓ No stale infrastructure references found (brain/, /harness/, recipe-)
- ✓ Legacy skill structures are richer than current .claude/skills/; valuable for reference during Phase 2D migration

---

## File Locations Referenced in This Report

**Root-level files:**
- `/Users/chrismauze/code/active/tibetan-spirit-ops/CLAUDE.md`
- `/Users/chrismauze/code/active/tibetan-spirit-ops/DEV-PLAN.md`
- `/Users/chrismauze/code/active/tibetan-spirit-ops/ORG.md`
- `/Users/chrismauze/code/active/tibetan-spirit-ops/SYSTEM-STATUS.md`
- `/Users/chrismauze/code/active/tibetan-spirit-ops/.gitignore`

**Legacy structure:**
- `/Users/chrismauze/code/active/tibetan-spirit-ops/agents/` (6 departments + shared/)
- Each department contains: soul.md, config.yaml, skills/

**.claude/ native:**
- `/Users/chrismauze/code/active/tibetan-spirit-ops/.claude/agents/` (cs-drafter.md, finance-analyst.md)
- `/Users/chrismauze/code/active/tibetan-spirit-ops/.claude/skills/` (act-on-approved, cs-triage, shopify-query)
- `/Users/chrismauze/code/active/tibetan-spirit-ops/.claude/rules/` (brand-voice.md, cultural-sensitivity.md, shopify-api.md)

**Workflows:**
- `/Users/chrismauze/code/active/tibetan-spirit-ops/workflows/daily_summary/run.py`
- `/Users/chrismauze/code/active/tibetan-spirit-ops/workflows/weekly_pnl/run.py`

**Workspace:**
- `/Users/chrismauze/code/active/tibetan-spirit-ops/workspace/plans/` (active planning)

---

**End of Assessment**
