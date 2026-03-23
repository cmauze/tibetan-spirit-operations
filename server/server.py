from __future__ import annotations

"""
Tibetan Spirit AI Operations Server
FastAPI webhook receiver + cron scheduler + Agent SDK worker

Deployment: Railway (ephemeral session pattern)
Runtime: Python 3.12+ (Agent SDK bundles Claude Code CLI)
"""

import base64
import hashlib
import hmac
import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from fastapi import BackgroundTasks, FastAPI, Header, HTTPException, Request
from pydantic import BaseModel

from claude_agent_sdk import ClaudeAgentOptions, ResultMessage, query
from ts_shared.logging_utils import log_skill_invocation

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ts-ops")

app = FastAPI(title="Tibetan Spirit AI Operations", version="0.2.0")

# ─── Configuration ────────────────────────────────────────────────────────────

SHOPIFY_WEBHOOK_SECRET = os.environ.get("SHOPIFY_WEBHOOK_SECRET", "")
API_KEY = os.environ.get("API_KEY", "")
SKILLS_DIR = os.path.join(os.path.dirname(__file__), "..", "skills")

MODEL_IDS = {
    "haiku": "claude-haiku-4-5-20251001",
    "sonnet": "claude-sonnet-4-6-20250514",
    "opus": "claude-opus-4-6-20250514",
}

# ─── Skill Registry ──────────────────────────────────────────────────────────


def load_skill(skill_path: str) -> str:
    """Load a SKILL.md file from the skills directory."""
    full_path = os.path.join(SKILLS_DIR, skill_path, "SKILL.md")
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Skill not found: {full_path}")
    with open(full_path, "r") as f:
        return f.read()


AGENT_CONFIGS = {
    "customer-service": {
        "skills": [
            "shared/brand-guidelines",
            "shared/product-knowledge",
            "shared/escalation-matrix",
            "customer-service/ticket-triage",
        ],
        "model": "haiku",
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
    "ecommerce": {
        "skills": [
            "shared/channel-config",
            "shared/product-knowledge",
            "ecommerce/etsy-content-optimization",
            "ecommerce/cross-channel-parity",
        ],
        "model": "sonnet",
        "max_turns": 15,
        "max_budget_usd": 0.50,
    },
    "category-management": {
        "skills": [
            "shared/channel-config",
            "shared/product-knowledge",
            "category-management/pricing-strategy",
            "category-management/competitive-research",
        ],
        "model": "sonnet",
        "max_turns": 20,
        "max_budget_usd": 1.00,
    },
    "marketing": {
        "skills": [
            "shared/channel-config",
            "marketing/meta-ads",
            "marketing/google-ads",
            "marketing/performance-reporting",
        ],
        "model": "sonnet",
        "max_turns": 15,
        "max_budget_usd": 0.75,
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
        SHOPIFY_WEBHOOK_SECRET.encode("utf-8"), body, hashlib.sha256
    ).digest()
    computed = base64.b64encode(digest).decode("utf-8")
    return hmac.compare_digest(computed, hmac_header)


# ─── Health Check ────────────────────────────────────────────────────────────


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "0.2.0",
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
    logger.info(f"New order received: #{payload.get('order_number')} (ID: {order_id})")

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
    context: Optional[Dict[str, Any]] = None,
) -> dict[str, Any]:
    """Execute a skill via the Claude Agent SDK. Logs every invocation."""
    start_time = datetime.now(timezone.utc)
    config = AGENT_CONFIGS.get(agent_name, {})
    model_key = config.get("model", "sonnet")
    result_text = ""
    cost_usd = 0.0
    input_tokens = output_tokens = cached_tokens = 0
    status = "success"
    error_msg = None

    try:
        skill_content = load_skill(skill_path)
        full_prompt = f"{skill_content}\n\n---\n\nTask:\n{prompt}"
        if context:
            full_prompt += f"\n\nContext:\n{json.dumps(context, indent=2, default=str)}"

        options = ClaudeAgentOptions(
            system_prompt=skill_content,
            model=MODEL_IDS.get(model_key, MODEL_IDS["sonnet"]),
            max_turns=config.get("max_turns", 10),
            permission_mode="bypassPermissions",
            cwd=os.path.dirname(SKILLS_DIR),
        )

        async for message in query(prompt=full_prompt, options=options):
            if isinstance(message, ResultMessage):
                result_text = message.result or ""
                cost_usd = getattr(message, "total_cost_usd", 0.0) or 0.0
                usage = getattr(message, "usage", {}) or {}
                input_tokens = usage.get("input_tokens", 0)
                output_tokens = usage.get("output_tokens", 0)
                cached_tokens = usage.get("cache_read_input_tokens", 0)

        return {"status": "completed", "result": result_text[:2000]}

    except Exception as e:
        logger.error(f"Skill execution failed: {skill_path} — {e}")
        status = "error"
        error_msg = str(e)
        raise

    finally:
        end_time = datetime.now(timezone.utc)
        try:
            await log_skill_invocation(
                agent_name=agent_name,
                skill_name=skill_path,
                prompt=prompt,
                result={"text": result_text[:500]} if result_text else {"error": error_msg},
                cost_usd=cost_usd,
                start_time=start_time,
                end_time=end_time,
                model_used=MODEL_IDS.get(model_key, "sonnet"),
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cached_tokens=cached_tokens,
                trigger_source="webhook",
                status=status,
                error=error_msg,
            )
        except Exception as log_err:
            logger.error(f"Failed to log invocation: {log_err}")


# ─── Background Task Handlers ────────────────────────────────────────────────


async def process_order(order_payload: dict):
    """Process a new Shopify order through the Operations Agent."""
    order_number = order_payload.get("order_number")
    logger.info(f"Processing order #{order_number}")
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


class SkillRunRequest(BaseModel):
    agent: str
    skill: str
    prompt: str
    context: Optional[Dict[str, Any]] = None


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
