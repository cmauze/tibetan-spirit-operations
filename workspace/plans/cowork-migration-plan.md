# Cowork Migration Plan — Tibetan Spirit Scheduled Tasks

**Date:** 2026-04-16
**Status:** Plan (not yet executed)
**Prerequisite:** Cowork scheduling API access

---

## Goal

Migrate `daily_summary.py` and `weekly_pnl.py` from PM2 cron to Cowork scheduled tasks. Keep the Shopify webhook receiver on Railway (Cowork cannot receive external webhooks).

## Current State

| Script | Schedule | Model | Output | LOC |
|--------|----------|-------|--------|-----|
| `scripts/daily_summary.py` | PM2 daily 6pm MT | Haiku | Slack #ts-operations | 274 |
| `scripts/weekly_pnl.py` | PM2 Monday 6am MT | Sonnet | Supabase task_inbox (needs_review) | 401 |

Both import from `lib/ts_shared/` (Supabase client, Claude client, cost tracker, notifications, dashboard ops).

## Migration Strategy

### Phase 1: daily_summary.py → Cowork

**What it does:** Queries today's orders from Supabase, calculates revenue/orders/AOV, calls Haiku to format a Slack summary, logs run + cost.

**Cowork configuration:**
- **Schedule:** `0 18 * * *` (daily 6pm MT)
- **Model:** Haiku (cost-sensitive, formatting only)
- **Environment:** Needs `SUPABASE_URL`, `SUPABASE_KEY`, `SLACK_WEBHOOK_URL`, `ANTHROPIC_API_KEY`
- **Working directory:** `~/code/active/tibetan-spirit-ops/`
- **Command:** `python scripts/daily_summary.py`

**Migration steps:**
1. Verify daily_summary.py runs standalone (no PM2 dependencies)
2. Register as Cowork scheduled task with env vars
3. Run once manually to verify output
4. Disable PM2 cron entry
5. Monitor for 3 days, then remove PM2 config

### Phase 2: weekly_pnl.py → Cowork

**What it does:** Three-step chain: (1) Python queries 7-day orders + COGS, (2) Sonnet formats CEO P&L report, (3) writes to task_inbox for review.

**Cowork configuration:**
- **Schedule:** `0 6 * * 1` (Monday 6am MT)
- **Model:** Sonnet (analysis + formatting)
- **Environment:** Same as daily_summary + needs `ANTHROPIC_API_KEY` with Sonnet access
- **Working directory:** `~/code/active/tibetan-spirit-ops/`
- **Command:** `python scripts/weekly_pnl.py`

**Migration steps:**
1. Verify weekly_pnl.py runs standalone
2. Register as Cowork scheduled task
3. Wait for next Monday to verify in production
4. Disable PM2 cron entry
5. Monitor for 2 weeks, then remove PM2 config

## Future Phases (Not This Sprint)

| Phase | Component | Notes |
|-------|-----------|-------|
| 3 | Agent invocations → Cowork fork | Already fork-based, minimal changes |
| 4 | task_inbox polling → Cowork tasks | Replace Supabase polling loop |
| 5 | Cost tracking → Cowork dashboard | Currently logs to spend_records |

## What Stays on Railway

- **Shopify webhook receiver** (`server/server.py`): HTTP endpoint for order/inventory events with HMAC validation. Cowork cannot receive external webhooks.
- **All 4 hooks**: Must fire at Claude Code tool-invocation time (not schedulable).

## Risks

| Risk | Mitigation |
|------|-----------|
| Cowork env var handling differs | Test with dry run before disabling PM2 |
| Timezone mismatch | Explicitly set MT in Cowork cron config |
| lib/ts_shared import path | Scripts use relative path insertion; verify Cowork working directory |
| Slack webhook rate limits | daily_summary is once/day — well within limits |

## Rollback

If Cowork fails, re-enable PM2 cron entries. Both scripts are stateless — no data migration needed.
