# Intercom Essentials — API Research Summary

**Researched:** 2026-03-29
**Decision:** Intercom Essentials is the locked helpdesk platform for Tibetan Spirit.

---

## Pricing

- **$29/seat/month** (billed annually) or $39/month monthly
- Minimum 1 seat
- Verify current pricing at intercom.com/pricing before purchase

## What's Included in Essentials

- Shared Inbox, Basic Messenger (chat widget), Help Center (knowledge base)
- Ticketing, Macros/Saved Replies, Conversation routing
- Basic reporting, REST API access, Webhooks, Shopify integration

## What's NOT Included

- **Fin AI Agent**: add-on at $0.99/resolution — we skip this, use our own AI pipeline
- Advanced Workflows, Custom objects, SLA management, HIPAA compliance
- Advanced reporting / custom reports

## API Capabilities (All Paid Plans)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `GET /conversations` | List | With filters (updated_after, etc.) |
| `GET /conversations/{id}` | Get | Full conversation with parts |
| `POST /conversations/{id}/reply` | Reply | Send as admin to customer |
| `POST /conversations/{id}/parts` | Note | Internal note (AI draft) |
| `POST /contacts/search` | Search | Find by email, external_id |
| `GET/POST/PUT /articles` | CRUD | Help center articles |

**Auth:** Bearer token, `Intercom-Version: 2.11` header
**Rate limit:** ~1,000 requests/minute
**Webhook signing:** HMAC-SHA256 via `X-Hub-Signature` header

## Key Webhook Topics

| Topic | Fires When |
|-------|-----------|
| `conversation.user.created` | New customer message |
| `conversation.user.replied` | Customer follow-up |
| `conversation.admin.replied` | Agent/admin reply |
| `conversation.admin.closed` | Conversation closed |

**Webhook setup is dashboard-only** (no API for managing subscriptions).

## No Native Draft State

Intercom API has no "draft" message type. Our workflow:
1. Webhook fires → Python backend receives
2. AI triages + drafts response
3. Draft stored in Supabase `task_inbox`
4. Optionally posted as **internal note** on the conversation (visible to CS in Intercom UI)
5. On human approval → `send_reply()` sends to customer

## No Official Python SDK

Use direct REST with `httpx`. Community `python-intercom` library is outdated.

## Required Scopes

`read.conversations`, `write.conversations`, `read.contacts`, `write.contacts`,
`read.articles`, `write.articles`, `read.admins`

## Shopify Integration

Native app in Intercom marketplace. Automatically:
- Adds Messenger widget to storefront
- Syncs customer data into Intercom contacts
- Shows order history in conversation sidebar

## Help Center

- Included in Essentials
- Articles API for programmatic creation
- Multi-language support
- Custom domain: **unconfirmed on Essentials** — verify with Intercom sales

## Env Vars Needed

```
HELPDESK_PLATFORM=intercom
INTERCOM_ACCESS_TOKEN=...
INTERCOM_ADMIN_ID=...
INTERCOM_WEBHOOK_SECRET=...
```

## Architecture Fit

```
Customer → Intercom Messenger → conversation.user.created webhook
→ Railway/Python → triage (Haiku) → draft (Sonnet) → Supabase task_inbox
→ Dashboard approval → Intercom send_reply() → Customer
```
