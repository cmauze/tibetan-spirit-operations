# Open Brain MCP — Global Connector Restore
**Date:** 2026-04-14
**For:** Fresh Claude Code session
**Repo:** ~/code/chris-os/ (for verification), then ~/.claude/ (for global config)

---

## Problem

The Open Brain MCP server (`capture_thought`, `search_thoughts`, `list_thoughts`, `thought_stats`, `log_audit_event`) is deployed as a Supabase Edge Function but only registered in the chris-os project's `.claude/mcp-settings.json`. Skills like `session-auto-capture` that run in other project directories (e.g., tibetan-spirit-ops) can't reach it.

## What Already Exists (DO NOT REBUILD)

| Component | Location | Status |
|-----------|----------|--------|
| **Edge Function** | `~/code/chris-os/supabase/functions/open-brain-mcp/` (856 lines, 8 files) | Deployed to Supabase |
| **Schema** | `thoughts` table with pgvector embeddings, `match_thoughts` RPC, `upsert_thought` RPC | Migrated |
| **Project MCP config** | `~/code/chris-os/.claude/mcp-settings.json` | Working |
| **Capture pipeline** | `~/code/chris-os/orchestrator/capture.py` + `supabase_client.py` + `git_writer.py` | Built, needs live testing |
| **Handoff doc** | `~/code/chris-os/workspace/handoffs/2026-04-14-capture-pipeline-handoff.md` | Full implementation notes |

## What Needs to Happen

### Step 1: Verify the Edge Function is live
```bash
# Test from the existing chris-os config — the URL and key are in:
# ~/code/chris-os/.claude/mcp-settings.json
# The .env file at ~/code/chris-os/supabase/ or ~/code/chris-os/orchestrator/.env
# has SUPABASE_URL, SUPABASE_SERVICE_KEY

# Quick health check (replace URL/key from the mcp-settings.json):
curl -X POST "https://yglkbxcozxmgvhyxaiyw.supabase.co/functions/v1/open-brain-mcp" \
  -H "Content-Type: application/json" \
  -d '{"method": "tools/list"}'
```

If the edge function is down, redeploy:
```bash
cd ~/code/chris-os
supabase functions deploy open-brain-mcp
```

### Step 2: Register Open Brain MCP globally

Create `~/.claude/mcp-settings.json` with the open-brain server. The URL with embedded key is already in `~/code/chris-os/.claude/mcp-settings.json`:

```json
{
  "mcpServers": {
    "open-brain": {
      "url": "https://yglkbxcozxmgvhyxaiyw.supabase.co/functions/v1/open-brain-mcp?key=<KEY_FROM_CHRIS_OS_MCP_SETTINGS>"
    }
  }
}
```

**IMPORTANT:** The key in the URL is an edge function invocation key (NOT the Supabase service role key). Read it from the existing chris-os config — do NOT hardcode a new one.

**ALSO IMPORTANT:** If `~/.claude/mcp-settings.json` already exists when you run, MERGE the open-brain entry rather than overwriting. Other projects may have added their own MCP servers.

### Step 3: Verify from a non-chris-os directory

Start a fresh Claude Code session in ~/code/ or ~/code/active/tibetan-spirit-ops/ and verify these tools are available:
- `search_thoughts`
- `capture_thought`
- `list_thoughts`
- `thought_stats`

### Step 4: Test capture round-trip

```
# In the fresh session, test:
capture_thought("Test capture from tibetan-spirit-ops session — verifying global MCP connector")

# Then verify it landed:
search_thoughts("test capture tibetan-spirit-ops")
```

### Step 5: Verify session-auto-capture works

End a session and confirm the skill can call `capture_thought` to save ACT NOW items.

## Architecture Context

The Open Brain MCP server exposes 5 tools:

| Tool | Purpose | Auth |
|------|---------|------|
| `capture_thought(content)` | Save thought with auto-embedding + LLM metadata extraction | x-brain-key header (embedded in URL) |
| `search_thoughts(query, limit, threshold)` | Semantic vector search via pgvector | Same |
| `list_thoughts(limit, type?, topic?, person?, days?)` | Browse recent thoughts with filters | Same |
| `thought_stats()` | Aggregate stats: counts, types, top topics | Same |
| `log_audit_event(actor, action, target, ...)` | Immutable audit log | Same |

The `thoughts` table schema (from `20260405000000_sprint_a_foundation.sql`):
- `id` UUID, `content` TEXT, `embedding` vector, `metadata` JSONB
- `status` (raw/triaged/needs_review/processed), `context_id`, `destination` (wiki/task/memory/reflection/panning)
- Content fingerprint dedup via SHA-256
- RLS: service_role only

## Session Notes to Capture (once connector works)

These are the ACT NOW items from the tibetan-spirit-ops financial model session that couldn't be captured:

1. **Google Sheets integration for TS scenario model** — Chris wants spreadsheet editability for scenario parameters. YAML→Google Sheets is a one-function swap in `scenarios.py`. Next: create Sheet with scenario columns, add Sheets API read, optionally write projections back to output tabs.

2. **Baseline actuals vs. v6 projections** — Supabase shows ~$20K/mo Shopify run rate, ahead of v6 model's Y1 assumption ($11.6K/mo). Validate: does the 2025 baseline include pre-acquisition orders? If truly $20K/mo organic, v6 "moderate upside" targets may be conservative.

## Constraints

- NEVER commit the edge function key or Supabase service role key to any file that gets committed to git
- The MCP config file at `~/.claude/mcp-settings.json` is NOT committed (it's in the user home dir)
- Do NOT rebuild the edge function or schema — they already exist and work
- Do NOT modify the chris-os project-level mcp-settings.json — it should keep working independently
