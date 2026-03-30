"""
Notion database configuration for Tibetan Spirit AI Ops.

Narrowed scope: Academy modules + cost log archive only.
Dashboard operational data lives in Supabase. Public wiki goes to Intercom Help Center.

Usage:
    from ts_shared.notion_config import NOTION_DB, ACADEMY_PROPS, COST_LOG_PROPS
"""

import os

# Parent page for all TS Ops databases
TS_DASHBOARD_PAGE_ID = os.environ.get(
    "NOTION_DASHBOARD_PAGE_ID", "3328604de46680648cacf383420869b3"
)

# Database IDs — env var overrides, hardcoded defaults from initial Notion MCP setup
NOTION_DB = {
    "academy_modules": os.environ.get(
        "NOTION_DB_ACADEMY", "b460c0381565404ab05534370a0aa990"
    ),
    "cost_log": os.environ.get(
        "NOTION_DB_COST_LOG", "ab437dd8b622419a8907e5fe590d9ae5"
    ),
}

# Property name constants (match Notion database schema)
COST_LOG_PROPS = {
    "title": "Run",
    "workflow": "Workflow",
    "run_date": "Run Date",
    "model": "Model",
    "input_tokens": "Input Tokens",
    "output_tokens": "Output Tokens",
    "cached_tokens": "Cached Tokens",
    "cost": "Cost USD",
}

ACADEMY_PROPS = {
    "title": "Module",
    "section": "Section",
    "status": "Status",
    "assignee": "Assignee",
    "module_number": "Module Number",
}
