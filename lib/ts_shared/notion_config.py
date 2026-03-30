"""
Notion database IDs for the TS Ops system.

All databases live under the TS Dashboard page.
Created via Notion MCP on March 29, 2026.

Usage:
    from ts_shared.notion_config import NOTION_DB
    inbox_id = NOTION_DB["task_inbox"]
"""

import os

# Parent page for all TS Ops databases
TS_DASHBOARD_PAGE_ID = "3328604de46680648cacf383420869b3"

# Database IDs (created via Notion MCP)
NOTION_DB = {
    "task_inbox": "c21af3f0c67a4d638681315aed4c17ea",
    "workflow_registry": "36fd1db454794ad99776427611f90fdb",
    "cost_log": "ab437dd8b622419a8907e5fe590d9ae5",
    "academy_modules": "b460c0381565404ab05534370a0aa990",
}

# Data source IDs (for Notion MCP operations)
NOTION_DATASOURCE = {
    "task_inbox": "6039c11d-9144-4710-9919-bda79bc5a8d4",
    "workflow_registry": "68abec8e-53a9-4681-a81c-27d21fdf659a",
    "cost_log": "1fb70637-10a5-4fd7-9f9b-9a434a75c018",
    "academy_modules": "7deb8745-3174-4a73-9326-24a5064fcc65",
}

# Property name constants (match exactly what Notion MCP created)
TASK_INBOX_PROPS = {
    "title": "Task",
    "review_status": "Review Status",  # Select: To Review, Approved, Rejected, Auto-Logged
    "workflow": "Workflow",       # Select: daily_summary, weekly_pnl, cs_email_drafts, inventory_alerts, campaign_brief, product_descriptions, approval_poller, chatbot
    "assignee": "Assignee",      # Select: ceo, operations-manager, customer-service-lead, warehouse-manager, spiritual-director
    "priority": "Priority",      # Select: P1, P2, P3, P4
    "output": "Output",          # Rich text
    "supabase_id": "Supabase ID",  # Text (links to skill_invocations row)
    "created": "Created",        # Created time (auto)
}

WORKFLOW_REGISTRY_PROPS = {
    "title": "Workflow",
    "status": "Status",          # Select: Healthy, Degraded, Down, In Development
    "schedule": "Schedule",      # Text (cron expression or description)
    "last_run": "Last Run",      # Date
    "last_cost": "Last Cost USD",  # Number (USD format)
    "failure_count": "Failure Count 7d",  # Number
    "notes": "Notes",            # Text
}

COST_LOG_PROPS = {
    "title": "Run",
    "workflow": "Workflow",      # Select
    "run_date": "Run Date",      # Date
    "model": "Model",            # Select: haiku-4.5, sonnet-4.6, opus-4.6
    "input_tokens": "Input Tokens",  # Number
    "output_tokens": "Output Tokens",  # Number
    "cached_tokens": "Cached Tokens",  # Number
    "cost": "Cost USD",          # Number (USD format)
}

ACADEMY_PROPS = {
    "title": "Module",
    "section": "Section",        # Select: Getting Started, Product Knowledge, Customer Service, Operations, Marketing, Finance, Advanced, Reference
    "status": "Status",          # Select: Not Started, Draft, Review, Published
    "assignee": "Assignee",      # Select: ceo, operations-manager, customer-service-lead
    "module_number": "Module Number",  # Number
}
