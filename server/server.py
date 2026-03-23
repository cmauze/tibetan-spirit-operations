"""
Tibetan Spirit AI Operations Server
FastAPI webhook receiver + cron scheduler + Agent SDK worker

Deployment: Railway (long-running session pattern)
Runtime: Python 3.12+ with Node.js 18+ (Agent SDK requirement)
"""

import os
import asyncio
import hashlib
import hmac
import json
import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, HTTPException, Request, Header, BackgroundTasks
from pydantic import BaseModel

# Claude Agent SDK imports
# from claude_agent_sdk import (
#     query, ClaudeAgentOptions, AssistantMessage, TextBlock, ResultMessage
# )

# Shared library imports
# from ts_shared.supabase_client import get_supabase_client
# from ts_shared.logging_utils import log_skill_invocation

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ts-ops")

app = FastAPI(title="Tibetan Spirit AI Operations", version="0.1.0")

# ─── Configuration ────────────────────────────────────────────────────────────

SHOPIFY_WEBHOOK_SECRET = os.environ.get("SHOPIFY_WEBHOOK_SECRET", "")
API_KEY = os.environ.get("API_KEY", "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# ─── Skill Registry ──────────────────────────────────────────────────────────

SKILLS_DIR = os.path.join(os.path.dirname(__file__), "..", "skills")


def load_skill(skill_path: str) -> str:
    """Load a SKILL.md file from the skills directory."""
    full_path = os.path.join(SKILLS_DIR, skill_path, "SKILL.md")
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Skill not found: {full_path}")
    with open(full_path, "r") as f:
        return f.read()


# Agent configurations — maps agent name to its default skill set and options
AGENT_CONFIGS = {
    "customer-service": {
        "skills": [
            "shared/brand-guidelines",
            "shared/product-knowledge",
            "shared/escalation-matrix",
            "customer-service/ticket-triage",
        ],
        "model": "haiku",  # Triage with Haiku, escalate to Sonnet for evaluating and writing all responses which aren't clearly answered by existing template
        "max_turns": 10,
        "max_budget_usd": 0.25,
    },
    "operations": {
        "skills": [
            "shared/channel-config",
            "shared/supabase-ops-db",
            "operations/fulfillment-domestic",
            "operations/inventory-management",
        ],
        "model": "sonnet",
        "max_turns": 15,
        "max_budget_usd": 0.50,
    },
    "finance": {
        "skills": [
            "shared/channel-config",
            "shared/supabase-ops-db",
            "finance/cogs-tracking",
            "finance/reconciliation",
        ],
        "model": "sonnet",
        "max_turns": 20,
        "max_budget_usd": 1.00,
    },
}


# ─── Webhook Security ────────────────────────────────────────────────────────


def verify_shopify_webhook(body: bytes, hmac_header: str) -> bool:
    """Validate Shopify webhook HMAC-SHA256 signature."""
    if not SHOPIFY_WEBHOOK_SECRET:
        logger.warning("SHOPIFY_WEBHOOK_SECRET not set — skipping validation")
        return True
    digest = hmac.new(
        SHOPIFY_WEBHOOK_SECRET.encode("utf-8"),
        body,
        hashlib.sha256,
    ).digest()
    import base64
    computed = base64.b64encode(digest).decode("utf-8")
    return hmac.compare_digest(computed, hmac_header)


# ─── Health Check ────────────────────────────────────────────────────────────


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "0.1.0",
    }


# ─── Shopify Webhooks ────────────────────────────────────────────────────────


@app.post("/webhooks/shopify/orders/create")
async def shopify_order_created(
    request: Request,
    background_tasks: BackgroundTasks,
    x_shopify_hmac_sha256: str = Header(None),
):
    """Handle new Shopify order — triggers Operations Agent."""
    body = await request.body()

    if x_shopify_hmac_sha256 and not verify_shopify_webhook(body, x_shopify_hmac_sha256):
        raise HTTPException(status_code=401, detail="Invalid HMAC signature")

    payload = json.loads(body)
    order_id = payload.get("id")
    order_number = payload.get("order_number")

    logger.info(f"New order received: #{order_number} (ID: {order_id})")

    # Respond 200 immediately — process asynchronously
    background_tasks.add_task(process_order, payload)
    return {"status": "accepted", "order_id": order_id}


@app.post("/webhooks/shopify/inventory/update")
async def shopify_inventory_updated(
    request: Request,
    background_tasks: BackgroundTasks,
    x_shopify_hmac_sha256: str = Header(None),
):
    """Handle inventory level change — triggers inventory check."""
    body = await request.body()

    if x_shopify_hmac_sha256 and not verify_shopify_webhook(body, x_shopify_hmac_sha256):
        raise HTTPException(status_code=401, detail="Invalid HMAC signature")

    payload = json.loads(body)
    logger.info(f"Inventory update: {payload.get('inventory_item_id')}")

    background_tasks.add_task(process_inventory_update, payload)
    return {"status": "accepted"}


# ─── Skill Execution ─────────────────────────────────────────────────────────


async def execute_skill(
    agent_name: str,
    skill_path: str,
    prompt: str,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Execute a single skill via the Claude Agent SDK.

    This is the core execution function. Every skill invocation flows through here,
    which ensures consistent logging, cost tracking, and error handling.
    """
    invocation_id = f"{agent_name}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    start_time = datetime.now(timezone.utc)

    try:
        skill_content = load_skill(skill_path)
        config = AGENT_CONFIGS.get(agent_name, {})

        # Build the full prompt with skill instructions and context
        full_prompt = f"{skill_content}\n\n---\n\nTask:\n{prompt}"
        if context:
            full_prompt += f"\n\nContext:\n{json.dumps(context, indent=2, default=str)}"

        # TODO: Replace with actual Agent SDK call once credentials are configured
        # options = ClaudeAgentOptions(
        #     system_prompt=skill_content,
        #     max_turns=config.get("max_turns", 10),
        #     max_budget_usd=config.get("max_budget_usd", 0.50),
        #     permission_mode="bypassPermissions",
        # )
        # result = await query(prompt=full_prompt, options=options)

        result = {
            "status": "stub",
            "message": f"Skill {skill_path} would execute here",
            "invocation_id": invocation_id,
        }

        # Log to Supabase skill_invocations table
        # await log_skill_invocation(
        #     invocation_id=invocation_id,
        #     agent_name=agent_name,
        #     skill_name=skill_path,
        #     prompt=prompt,
        #     result=result,
        #     cost_usd=0.0,
        #     start_time=start_time,
        #     end_time=datetime.now(timezone.utc),
        # )

        return result

    except Exception as e:
        logger.error(f"Skill execution failed: {skill_path} — {e}")
        # Log failure
        # await log_skill_invocation(
        #     invocation_id=invocation_id,
        #     agent_name=agent_name,
        #     skill_name=skill_path,
        #     prompt=prompt,
        #     result={"error": str(e)},
        #     cost_usd=0.0,
        #     start_time=start_time,
        #     end_time=datetime.now(timezone.utc),
        #     status="error",
        # )
        raise


# ─── Background Task Handlers ────────────────────────────────────────────────


async def process_order(order_payload: dict):
    """Process a new Shopify order through the Operations Agent pipeline."""
    order_number = order_payload.get("order_number")
    logger.info(f"Processing order #{order_number}")

    # Step 1: Determine fulfillment route
    # (domestic via Fiona, Mexico via Omar, or international via Nepal)
    await execute_skill(
        agent_name="operations",
        skill_path="operations/fulfillment-domestic",
        prompt=f"Route and prepare fulfillment for order #{order_number}",
        context=order_payload,
    )


async def process_inventory_update(inventory_payload: dict):
    """Check if inventory update triggers reorder alerts."""
    await execute_skill(
        agent_name="operations",
        skill_path="operations/inventory-management",
        prompt="Check if this inventory change triggers any reorder alerts",
        context=inventory_payload,
    )


# ─── Cron-Triggered Skills ───────────────────────────────────────────────────
# These are invoked by an external scheduler (Railway cron, GitHub Actions, or crontab)
# via authenticated POST to /api/run-skill


class SkillRunRequest(BaseModel):
    agent: str
    skill: str
    prompt: str
    context: dict[str, Any] | None = None


@app.post("/api/run-skill")
async def run_skill(
    req: SkillRunRequest,
    background_tasks: BackgroundTasks,
    x_api_key: str = Header(None),
):
    """Authenticated endpoint for cron-triggered or manual skill invocation."""
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

    background_tasks.add_task(
        execute_skill,
        agent_name=req.agent,
        skill_path=req.skill,
        prompt=req.prompt,
        context=req.context,
    )
    return {"status": "accepted", "agent": req.agent, "skill": req.skill}


# ─── Entry Point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
