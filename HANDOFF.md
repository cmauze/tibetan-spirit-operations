# Tibetan Spirit AI Ops — Agent Handoff Prompt

> **Purpose**: This document is a complete handoff for the next Claude agent (Claude Code CLI or Cowork session) continuing implementation of the Tibetan Spirit autonomous operations platform. Copy-paste this entire document as the opening prompt for a new session.

---

## INSTRUCTIONS FOR NEXT AGENT

You are continuing implementation of an autonomous AI operations platform for Tibetan Spirit, a Tibetan Buddhist goods e-commerce business. Read `CLAUDE.md` first — it is the master context document for this project. Then read `BUILD-PLAN.md` for the phased implementation plan.

**Your environment**: You are working in the `tibetan-spirit-ops` repo. If you have access to a Supabase MCP, use it for database operations. If you have access to the Shopify API, use it to validate the connection. All credentials are in `.env`.

---

## CURRENT STATE (as of March 23, 2026)

### What's DONE

**Infrastructure credentials (all in `.env`):**
- Anthropic API key — configured
- Shopify Admin API — `${SHOPIFY_ACCESS_TOKEN}` (offline token, permanent)
  - Store: `tibetanspirits.myshopify.com`
  - App: "TS AI Operations" (Dev Dashboard, version 006, legacy install flow, non-embedded)
  - Client ID: `${SHOPIFY_CLIENT_ID}`
  - Scopes: read/write orders, products, inventory, fulfillments, shipping + read customers, locations, analytics
  - Webhook secret: `${SHOPIFY_WEBHOOK_SECRET}`
- Supabase project — `tibetan-spirit-ops` on us-east-1 (Micro compute)
  - URL: `${SUPABASE_URL}`
  - Using new key types: `${SUPABASE_ANON_KEY}` (anon) and `${SUPABASE_SERVICE_KEY}` (service)
  - **Database is empty — schema.sql has NOT been deployed yet**

**Project structure (57 SKILL.md files):**
- `CLAUDE.md` — master project prompt (comprehensive)
- `BUILD-PLAN.md` — 10-week phased implementation plan
- `.env` — all credentials for Shopify + Supabase + Anthropic (other services blank)
- `.gitignore` — properly configured

**Fully drafted skills (11):**
1. `skills/shared/brand-guidelines/SKILL.md` + `cultural-sensitivity.md`
2. `skills/shared/product-knowledge/SKILL.md`
3. `skills/shared/channel-config/SKILL.md`
4. `skills/shared/escalation-matrix/SKILL.md`
5. `skills/shared/supabase-ops-db/SKILL.md`
6. `skills/customer-service/ticket-triage/SKILL.md` + `response-templates.md`
7. `skills/customer-service/order-inquiry/SKILL.md`
8. `skills/operations/fulfillment-domestic/SKILL.md` + `carrier-rules.md`
9. `skills/operations/inventory-management/SKILL.md`
10. `skills/finance/cogs-tracking/SKILL.md`
11. `skills/finance/reconciliation/SKILL.md`

**Stub skills (46):** All remaining skill directories have SKILL.md files with proper YAML frontmatter, section outlines, dependencies, and success metrics — but lack full implementation instructions. They are meaningful scaffolds, not empty placeholders.

**Server code:**
- `server/server.py` — FastAPI with Shopify webhook HMAC validation, background tasks, agent config stubs
- `server/Dockerfile` — Python 3.12-slim + Node.js 20
- `server/requirements.txt` — fastapi, uvicorn, claude-agent-sdk>=0.1.48, supabase, python-dotenv, httpx
- `server/.env.example` — template with placeholder values

**Shared library:**
- `lib/shared/src/ts_shared/supabase_client.py` — singleton client (currently raises NotImplementedError)
- `lib/shared/src/ts_shared/logging_utils.py` — skill invocation audit logging

**Utility scripts:**
- `scripts/shopify_token_capture.py` — one-time OAuth token capture (already used, can be deleted)

### What's NOT done — prioritized

**CRITICAL PATH (do these first):**

1. **Validate connections** — Run these tests before anything else:
   ```bash
   # Shopify test
   curl -s "https://tibetanspirits.myshopify.com/admin/api/2026-01/shop.json" \
     -H "X-Shopify-Access-Token: ${SHOPIFY_ACCESS_TOKEN}" | python3 -m json.tool

   # Supabase test
   curl -s "${SUPABASE_URL}/rest/v1/" \
     -H "apikey: ${SUPABASE_SERVICE_KEY}" \
     -H "Authorization: Bearer ${SUPABASE_SERVICE_KEY}"
   ```
   If either fails, debug the credential before proceeding. If Supabase MCP is available, use it to verify the connection instead.

2. **Write and deploy `schema.sql`** — Read `skills/shared/supabase-ops-db/SKILL.md` for the schema design. Create `skills/shared/supabase-ops-db/schema.sql` with full DDL for:
   - `products` (Shopify product data + COGS fields)
   - `inventory_extended` (cross-channel stock levels)
   - `orders` (order tracking)
   - `competitive_intel` (competitor prices)
   - `supplier_payments` (Nepal supplier payments in NPR/USD)
   - `marketing_performance` (ad spend/revenue by channel)
   - `skill_invocations` (audit trail — every skill run logged)
   - Materialized views: `channel_profitability_monthly`, `product_margin_detail`, `inventory_health`, `marketing_roas_trailing`
   - pg_cron refresh schedules for materialized views

   Deploy via Supabase MCP if available, otherwise output the SQL for the user to paste into the Supabase SQL Editor.

3. **Fix `supabase_client.py`** — Replace the `NotImplementedError` with a working async Supabase client using the credentials from `.env`. Test that it can query the database after schema deployment.

4. **Wire up `server.py`** — The Agent SDK calls are stubbed with TODO comments. Replace them with actual `claude_agent_sdk` invocations. Reference the CLAUDE.md section on model routing (Haiku for triage, Sonnet for execution).

**IMPORTANT (but not blocking):**

5. **Deploy to Railway** — Push to GitHub, connect to Railway, set environment variables. The Dockerfile is ready. After deploy, configure Shopify webhooks to point at `https://<railway-url>/webhooks/shopify/orders/create` and `/webhooks/shopify/inventory/update`.

6. **Write product-knowledge reference files** — `skills/shared/product-knowledge/` needs per-category detail files: `singing-bowls.md`, `thangkas.md`, `incense.md`, `malas.md`, `statues.md`, `prayer-flags.md`. These feed the product-guidance and category management skills.

7. **Write pre-built SQL queries** — `skills/shared/supabase-ops-db/queries/` directory with common query patterns referenced by multiple skills.

8. **Draft remaining ~35 stub skills** — Use the Claude Code prompts in `BUILD-PLAN.md` section "Claude Code Prompts for Next Skills" as starting points. Prioritize by phase: operations → finance → ecommerce → marketing → category management.

---

## ARCHITECTURE QUICK REFERENCE

- **Runtime**: Claude Agent SDK (Python) on Railway
- **Database**: Supabase PostgreSQL (coordination layer between all skills)
- **Models**: Haiku 4.5 ($1/$5) for triage → Sonnet 4.6 ($3/$15) for execution → Opus 4.6 ($5/$25) for complex analysis
- **6 Agents**: Customer Service, Operations, Ecommerce Manager, Category Manager, Marketing Manager, Finance
- **Trigger mechanisms**: Shopify webhooks, Re:amaze webhooks, daily/weekly crons, manual invocation
- **Phase system**: Phase 1 = human approval required, Phase 2 = autonomous with reporting

## KEY PEOPLE

- **Chris Mauzé** — CEO. Approves pricing, budget, strategy. Uses Claude Code + dashboard.
- **Jhoti** — Ops Manager, Indonesia. ALL communications in formal Bahasa Indonesia ("Anda" not "kamu").
- **Fiona** — Warehouse manager, Asheville NC. Handles domestic pick/pack/ship.
- **Dr. Hun Lye** — Spiritual director. Escalation target for Buddhist practice questions.
- **Omar** — Mexico fulfillment partner (Espíritu Tibetano).

## CULTURAL RULES (non-negotiable)

- Never use "exotic" or "mystical" — frame products through practice context
- Buddhist terminology stays untranslated: mala, thangka, dharma, sangha
- Products have spiritual significance — singing bowls are meditation instruments, not "home decor"
- 5% Dharma Giving is a genuine commitment, not a marketing angle
- When in doubt about cultural sensitivity, escalate to Dr. Hun Lye

---

## AGENT STRATEGY

**Should this agent see the rest of the project through, or hand off?**

This project has two distinct workstreams:

1. **Infrastructure + Wiring** (schema deployment, server.py wiring, Railway deploy, webhook config) — This is a focused 2-3 hour session. One agent should do all of this in sequence because each step depends on the previous one.

2. **Skill authoring** (~35 remaining skills) — This is parallelizable and can be done across multiple sessions. Each skill is independent. Use the Claude Code prompts in BUILD-PLAN.md.

**Recommended approach**: The next agent handles workstream 1 completely (validate connections → deploy schema → fix supabase_client → wire server.py → deploy to Railway). Then hand off to subsequent sessions for skill authoring, which can be done incrementally over days/weeks as Chris has time.

---

## FILES TO READ FIRST

1. `CLAUDE.md` — master context (read fully)
2. `BUILD-PLAN.md` — phased plan (skim for current phase)
3. `.env` — verify all credentials present
4. `skills/shared/supabase-ops-db/SKILL.md` — schema design for #2 above
5. `server/server.py` — understand the webhook + agent invocation flow
6. `lib/shared/src/ts_shared/supabase_client.py` — needs to be fixed (#3 above)
