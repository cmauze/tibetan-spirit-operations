# Sprint S2-W: Workflow Track (CS + Customers + Inventory)

**Tool:** Claude Code (Opus)
**Parallel Group:** PG-2 (runs in parallel with S2-D and S2-K)
**Prerequisites:** Sprint S1 complete
**Complexity:** Complex

---

## Overview

Build three workflows (CS email drafts, customer profiles, inventory alerts) and the Intercom Essentials REST client. This sprint creates the CS pipeline that ingests customer messages, triages with AI, drafts responses, and queues them for human approval.

---

## Dev Prompt

```
Read CLAUDE.md, ORG.md, SYSTEM-STATUS.md, DEV-PLAN.md.
Read all lib/ts_shared/ modules to understand the shared library pattern.

Execute the following 3 prompts in order. Commit after each.
Stop and report after each commit.

=== PROMPT 2C: CS Email Drafts Workflow + Intercom Client ===

Read skills/customer-service/ticket-triage/SKILL.md,
skills/shared/brand-guidelines/SKILL.md, skills/shared/product-knowledge/SKILL.md,
skills/shared/escalation-matrix/SKILL.md.

1. Create `lib/ts_shared/intercom_client.py` — thin REST client using httpx:

   class IntercomClient:
       BASE_URL = "https://api.intercom.io"
       API_VERSION = "2.11"

   Functions:
   - __init__(access_token: str): set up httpx.Client with auth + version headers
   - fetch_new_conversations(since: datetime) -> list[dict]: GET /conversations with updated_after filter
   - get_conversation(conversation_id: str) -> dict: GET /conversations/{id} with full parts
   - post_internal_note(conversation_id: str, admin_id: str, body: str) -> dict:
     POST /conversations/{id}/parts with message_type="note"
   - send_reply(conversation_id: str, admin_id: str, body: str) -> dict:
     POST /conversations/{id}/reply with message_type="comment", type="admin"
   - search_contacts(email: str) -> list[dict]: POST /contacts/search
   - verify_webhook(payload: bytes, signature: str, secret: str) -> bool: HMAC-SHA256

   Auth: Bearer token via INTERCOM_ACCESS_TOKEN env var.
   Graceful degradation: if token missing, log warning, all methods return None/empty.
   Add httpx to pyproject.toml if not already there.

2. Create `workflows/cs_email_drafts/`:

   config.yaml:
     name: cs_email_drafts
     schedule: "*/30 8-18 * * *"
     model_triage: claude-haiku-4-5-20251001
     model_draft: claude-sonnet-4-6
     requires_approval: true
     assignee: customer-service-lead  # falls back to operations-manager until hire

   run.py — Three-step chain:
     Step 1 TRIAGE (Haiku): Classify each new ticket.
       Return {category, priority, route_to_role, summary}.
     Step 2 ENRICH: Look up customer in Supabase (order history from orders table,
       profile from customer_profiles if exists). Load relevant domain skill.
     Step 3 DRAFT (Sonnet): Generate response following brand guidelines.
       Output: {subject, body, internal_notes, suggested_actions}.
     Step 4 OUTPUT: Write to task_inbox via dashboard_ops.create_task().
       Send Slack alert. If Intercom configured, post AI draft as internal note
       on the conversation so CS can see it in Intercom UI.

   Email ingestion logic:
     Check HELPDESK_PLATFORM env var:
     - "intercom": use intercom_client to fetch_new_conversations()
     - Not set: fall back to Supabase `cs_inbox` table (test mode)

   For output on approval:
     If Intercom configured: send_reply() through Intercom API
     Otherwise: log to task_inbox as "approved, manual send required"

3. Create `scripts/import_test_emails.py`:
   Insert 10 sample emails into Supabase cs_inbox table covering:
   order_status, product_question, return_request, practice_inquiry, complaint,
   shipping_delay, wholesale_inquiry, product_recommendation, damaged_item, gratitude.

   First create the cs_inbox table if it doesn't exist:
   CREATE TABLE cs_inbox (
     id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
     source TEXT DEFAULT 'manual',
     from_email TEXT NOT NULL,
     from_name TEXT,
     subject TEXT NOT NULL,
     body TEXT NOT NULL,
     conversation_id TEXT,  -- Intercom conversation ID if applicable
     processed BOOLEAN DEFAULT false,
     created_at TIMESTAMPTZ DEFAULT now()
   );

4. Write eval: tests/evals/test_cs_drafts.py
   - Verify triage accuracy on 10 test emails
   - Check brand compliance (no forbidden words)
   - Verify escalation routing matches ORG.md

Commit: "feat: add cs_email_drafts workflow with Intercom client and triage chain"

=== PROMPT 2.5A: Customer Profiles + RFM Scoring ===

Create Supabase migration for `customer_profiles`:
  email TEXT UNIQUE NOT NULL,
  first_name TEXT, last_name TEXT,
  first_order_date TIMESTAMPTZ, last_order_date TIMESTAMPTZ,
  order_count INTEGER DEFAULT 0,
  lifetime_value NUMERIC DEFAULT 0,
  avg_order_value NUMERIC DEFAULT 0,
  top_categories JSONB DEFAULT '[]',
  segment TEXT DEFAULT 'unknown',
  rfm_score TEXT,
  rfm_recency INTEGER, rfm_frequency INTEGER, rfm_monetary INTEGER,
  ticket_count INTEGER DEFAULT 0,
  sentiment_score NUMERIC,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()

Create `scripts/build_customer_profiles.py`:
1. Query all orders grouped by email
2. Calculate RFM quintiles (1-5 each dimension)
3. Assign heuristic segments: practicing_buddhist, wellness_seeker, gift_buyer, unknown
   (based on product categories: malas+texts→practicing, singing_bowls+incense→wellness,
    holiday_timing+gift_wrap→gift_buyer)
4. Upsert all profiles, print summary

Commit: "feat: build customer_profiles with RFM scoring from 19K orders"

=== PROMPT 3B: Inventory Alerts Workflow ===

Read skills/operations/inventory-management/SKILL.md, skills/shared/channel-config/SKILL.md.

1. Create `scripts/sync_shopify_inventory.py`:
   - Query Shopify API for inventory levels across all locations
   - Upsert into inventory_extended table (create migration if needed for any missing columns)
   - Print summary: total SKUs synced, stockouts, low stock

2. Create `workflows/inventory_alerts/`:

   config.yaml:
     name: inventory_alerts
     schedule: "0 9 * * *"
     model: claude-sonnet-4-6
     requires_approval: true
     assignee: operations-manager

   run.py:
     Step 1: Run sync_shopify_inventory (or call its logic directly)
     Step 2: Compare each SKU against reorder_trigger_qty. Flag stockouts, critical, reorder.
     Step 3 (Sonnet): Generate priority-sorted alert list with PO suggestions.
       Include: SKU, title, current stock, avg daily sales (from inventory_health view),
       days of supply, suggested reorder qty.
     Step 4: Write to task_inbox. Send Slack. If stockouts, also alert ceo.

   Refresh materialized view: inventory_health after sync.

Commit: "feat: add inventory_alerts workflow with Shopify sync and reorder generation"
```

---

## Test Prompt

```
Run the following verification suite for Sprint S2-W.

=== INTERCOM CLIENT ===
1. python -c "from ts_shared.intercom_client import IntercomClient; print('OK')"
2. Verify graceful degradation: unset INTERCOM_ACCESS_TOKEN, instantiate client → no crash
3. pytest tests/test_intercom_client.py (if exists, all pass with mocked API)

=== CS EMAIL DRAFTS ===
4. python scripts/import_test_emails.py → 10 emails in cs_inbox table
5. Run SQL: SELECT count(*) FROM cs_inbox → 10
6. python workflows/cs_email_drafts/run.py → processes test emails, no errors
7. Run SQL: SELECT count(*) FROM task_inbox WHERE status = 'needs_review'
   ORDER BY created_at DESC → new entries exist
8. Triage accuracy: inspect output JSONB for each task — at least 8/10 correct categories
9. Spot-check 3 drafts: no "exotic", no "mystical", Buddhist terms untranslated
10. Verify: practice inquiry → routes to spiritual-director
11. Verify: complaint with refund >$100 → routes to ceo
12. pytest tests/evals/test_cs_drafts.py → passes

=== CUSTOMER PROFILES ===
13. python scripts/build_customer_profiles.py → runs, prints summary
14. Run SQL: SELECT count(*) FROM customer_profiles → thousands of profiles
15. Run SQL: SELECT segment, count(*) FROM customer_profiles GROUP BY 1 → multi-segment distribution
16. Run SQL: SELECT * FROM customer_profiles ORDER BY lifetime_value DESC LIMIT 5
    → top customers have high LTV
17. Run SQL: SELECT rfm_score, count(*) FROM customer_profiles GROUP BY 1 ORDER BY 1
    → varied scores (111 through 555)

=== INVENTORY ALERTS ===
18. python scripts/sync_shopify_inventory.py → inventory_extended populated
19. Run SQL: SELECT count(*) FROM inventory_extended → matches product count (or close)
20. Run SQL: SELECT * FROM inventory_health WHERE stock_status IN ('stockout', 'critical') LIMIT 10
    → materialized view returns data
21. python workflows/inventory_alerts/run.py → creates task_inbox entries
22. Verify task assignee is 'operations-manager' (not hardcoded name)

=== FULL SUITE ===
23. pytest tests/ → ALL tests pass
24. python scripts/validate_cross_refs.py → zero violations
```
