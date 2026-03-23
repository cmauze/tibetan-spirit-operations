# Tibetan Spirit AI Ops — Handoff 002

> **Session date**: March 23, 2026
> **Session scope**: Tier 0-3 implementation — schema, skills, shared library, server wiring, Railway deploy
> **Status**: In progress (Tier 2 complete, Tier 3 starting)

---

## What Was Completed This Session

### Tier 0: Foundation
- [x] `scripts/validate_skill.py` — structural linter for SKILL.md files
- [x] `pyproject.toml` — project metadata + pytest config
- [x] `tests/conftest.py` — shared pytest fixtures
- [x] Credential scrub: all plaintext tokens in HANDOFF.md, BUILD-PLAN.md, shopify_token_capture.py redacted to `${ENV_VAR}` references
- [x] `.gitignore` updated: added `.claude/settings.local.json`, `.mcp.json`, `validation-report.json`
- [x] `git init` + pushed to `cmauze/tibetan-spirit-operations`

### Tier 1: Three Parallel Branches (all merged)
- [x] **Branch A: `feat/schema`** — `schema.sql` (505 lines, 7 tables, 4 mat views, 20 indexes, 7 triggers), deployed to Supabase via MCP, 4 pre-built queries, `validate_schema.py`, `validate_cross_refs.py`
- [x] **Branch B: `feat/skills-phase2`** — 7 SKILL.md files rewritten to production quality, eval scaffolding (`tests/evals/`) with 18 passing assertions
- [x] **Branch C: `feat/skills-content`** — 6 product knowledge reference files (all marked DRAFT pending Dr. Hun Lye), 3 SKILL.md rewrites (tibetan-calendar, etsy-content-optimization, cross-channel-parity)
- [x] Cross-reference validation gate: PASS (66 files scanned, 12 SQL refs found, 0 errors)

### Tier 2: Shared Library Activation (merged)
- [x] **Branch D: `feat/shared-lib`** — `supabase_client.py` activated (sb_secret_ key format works with supabase-py 2.28.3), `logging_utils.py` Supabase insert activated, `__init__.py` exports added, 4 unit tests passing

### Tier 3: Server Wiring + Deploy (in progress)
- [ ] **Branch E: `feat/server-wiring`** — Agent SDK integration in server.py
- [ ] **Branch F: `feat/railway-deploy`** — Railway deployment + Shopify webhook config

---

## What Needs to Happen After This Session

### Immediate (before processing real orders)

1. **Railway deployment verification**
   - Confirm `/health` returns 200 at the Railway URL
   - Ensure all env vars are set in Railway dashboard
   - Fix Dockerfile Root Directory setting (clear it — Dockerfile expects repo root as build context, set Dockerfile Path to `server/Dockerfile`)

2. **Shopify webhook configuration**
   - `orders/create` → `https://<railway-url>/webhooks/shopify/orders/create`
   - `inventory_levels/update` → `https://<railway-url>/webhooks/shopify/inventory/update`
   - Send test webhook from Shopify admin to verify HMAC + processing

3. **Agent SDK wiring verification**
   - Confirm `execute_skill()` works end-to-end with a real Agent SDK call
   - Verify `skill_invocations` table receives audit records
   - Test with `/api/run-skill` endpoint using the API key

4. **Rotate Shopify token** (recommended)
   - The original `shpat_...` token was in plaintext in HANDOFF.md before redaction
   - While never committed to git, it was visible in the Cowork session
   - Rotate via Shopify Dev Dashboard → TS AI Operations → API credentials

### Short-term (Phase 2, Weeks 3-4 per BUILD-PLAN.md)

5. **Dr. Hun Lye product knowledge review**
   - 6 files in `skills/shared/product-knowledge/` are marked `<!-- DRAFT: Pending Dr. Hun Lye review -->`
   - These are LLM-drafted and should NOT be treated as authoritative until reviewed
   - Files: `singing-bowls.md`, `thangkas.md`, `incense.md`, `malas.md`, `statues.md`, `prayer-flags.md`

6. **Business logic review in new skills**
   - Return thresholds: auto-approve <$30, Jhoti $30-100, Chris >$100 — confirm these match actual policy
   - Nepal FX thresholds: 3% advisory, 5% hold — confirm these match risk tolerance
   - Channel fee rates in materialized views: Shopify 2.5%+$0.30, Etsy 10%, Amazon 30% — these are approximations (actual Etsy = ~6.5% tx + ~3.25% payment + $0.20 listing)

7. **Re:amaze webhook endpoint**
   - `server.py` has no Re:amaze endpoint yet
   - Need: `POST /webhooks/reamaze/ticket` that triggers Customer Service Agent
   - Requires: Re:amaze API credentials (currently blank in `.env`)

8. **Ticket-triage live testing**
   - Run eval framework against 20 historical customer emails
   - Compare AUTO_RESPOND/ESCALATE classifications against what a human would do
   - Target: >90% agreement before going live

### Medium-term (Phase 3-4, Weeks 5-8)

9. **Remaining ~39 stub skills**
   - Prioritize by phase per BUILD-PLAN.md
   - Phase 3: etsy-sync-monitoring, amazon-fba-replenishment, amazon-listing-optimization
   - Phase 4: meta-ads, google-ads, performance-reporting, drift-detection, email-sms

10. **MCP server inventory**
    - Evaluate community MCP servers for: Shopify, Klaviyo, QuickBooks
    - For services without maintained MCPs, write thin Python wrappers as in-process MCP tools via `@tool` decorator
    - These go in `lib/shared/src/ts_shared/tools/`

11. **Dashboard (React PWA)**
    - Fiona needs daily pick lists
    - Jhoti needs order approval interface (Bahasa Indonesia)
    - Chris needs margin/inventory overview
    - Not started — `dashboard/` directory doesn't exist yet

12. **Langfuse/OTEL integration (Phase 2 observability)**
    - Currently logging to `skill_invocations` table only
    - Add Langfuse for production tracing when volume justifies it (200+ invocations)
    - Requires: Langfuse account, `LANGFUSE_PUBLIC_KEY` and `LANGFUSE_SECRET_KEY` env vars

### Long-term

13. **Phase 1 → Phase 2 graduation**
    - Skills start requiring human approval (Phase 1)
    - After 30-90 days, 200+ invocations, <2% error rate → graduate to Phase 2 (autonomous with reporting)
    - Auto-demote to Phase 1 if drift detection flags anomalies
    - Query: `SELECT skill_name, COUNT(*), AVG(CASE WHEN error IS NULL THEN 1 ELSE 0 END) as success_rate FROM skill_invocations GROUP BY skill_name`

14. **Etsy + Amazon channel launches**
    - Etsy shop creation (if not done)
    - Amazon Seller Central account setup
    - CedCommerce integration for Etsy sync
    - These gate Phase 3 skills

---

## Key Files Changed This Session

| File | Change |
|------|--------|
| `skills/shared/supabase-ops-db/schema.sql` | NEW — full DDL, deployed to Supabase |
| `skills/shared/supabase-ops-db/queries/*.sql` | NEW — 4 pre-built query files |
| `skills/shared/product-knowledge/*.md` | NEW — 6 product knowledge drafts |
| `skills/operations/supplier-communication/SKILL.md` | Rewritten from stub |
| `skills/operations/fulfillment-nepal/SKILL.md` | Rewritten from stub |
| `skills/operations/fulfillment-mexico/SKILL.md` | Rewritten from stub |
| `skills/finance/nepal-payments/SKILL.md` | Rewritten from stub |
| `skills/finance/margin-reporting/SKILL.md` | Rewritten from stub |
| `skills/customer-service/return-request/SKILL.md` | Rewritten from stub |
| `skills/customer-service/product-guidance/SKILL.md` | Rewritten from stub |
| `skills/shared/tibetan-calendar/SKILL.md` | Rewritten from stub |
| `skills/ecommerce/etsy-content-optimization/SKILL.md` | Rewritten from stub |
| `skills/ecommerce/cross-channel-parity/SKILL.md` | Rewritten from stub |
| `lib/shared/src/ts_shared/supabase_client.py` | Activated (was NotImplementedError) |
| `lib/shared/src/ts_shared/logging_utils.py` | Activated Supabase insert |
| `scripts/validate_skill.py` | NEW — structural linter |
| `scripts/validate_schema.py` | NEW — schema consistency checker |
| `scripts/validate_cross_refs.py` | NEW — cross-branch validator |
| `tests/conftest.py` | NEW — shared fixtures |
| `tests/test_supabase_client.py` | NEW — client tests |
| `tests/test_logging_utils.py` | NEW — logging tests |
| `tests/evals/conftest.py` | NEW — eval fixtures |
| `tests/evals/test_ticket_triage.py` | NEW — classification eval |
| `pyproject.toml` | NEW — project config |
| `HANDOFF.md` | Credentials redacted |
| `BUILD-PLAN.md` | No credential changes needed |
| `.gitignore` | Added Claude/MCP/validation entries |
| `server/server.py` | TBD — Tier 3 (Agent SDK wiring) |

---

## Database State

- **Supabase project**: `tibetan-spirit-ops` on us-east-1
- **Schema**: 7 tables, 4 materialized views, 5 enum types, 23 indexes, 7 update triggers
- **Data**: All tables empty — awaiting first Shopify sync
- **pg_cron**: Schedules documented as comments in schema.sql (extension availability not confirmed)

## Validation State

| Validator | Result |
|-----------|--------|
| `validate_skill.py` (all 57 skills) | 14 pass, 43 fail (stubs expected) |
| `validate_skill.py` (10 new skills) | 10 pass, 0 fail |
| `validate_schema.py` | PASS (7 tables, 4 views, 4 queries valid) |
| `validate_cross_refs.py` | PASS (66 files, 12 SQL refs, 0 errors) |
| `pytest` (shared lib) | 4/4 pass |
| `pytest` (evals) | 18/18 pass |
