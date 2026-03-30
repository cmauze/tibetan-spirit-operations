"""
Cost tracker — dual-write to Supabase (primary) and Notion (archive).

Usage:
    from ts_shared.cost_tracker import log_invocation

    invocation_id = log_invocation(
        workflow="daily_summary",
        skill_name="channel-config",
        model="claude-haiku-4-5-20251001",
        usage=response.usage,
        latency_ms=1200,
    )
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from ts_shared.claude_client import calculate_cost

logger = logging.getLogger(__name__)


def log_invocation(
    workflow: str,
    skill_name: str,
    model: str,
    usage,
    latency_ms: int,
    trigger_source: str = "cron",
    confidence: Optional[float] = None,
    error: Optional[str] = None,
) -> str:
    """Log a skill invocation to Supabase (primary) + Notion (archive).

    Args:
        workflow: Workflow name (e.g. "daily_summary").
        skill_name: Skill that was invoked.
        model: Model ID used.
        usage: anthropic.types.Usage object (or mock with input_tokens, output_tokens, etc.)
        latency_ms: End-to-end latency in milliseconds.
        trigger_source: "cron", "webhook", or "manual".
        confidence: Optional confidence score (0-1).
        error: Optional error message if the invocation failed.

    Returns:
        Invocation UUID string.
    """
    cost_usd = calculate_cost(usage, model)
    input_tokens = getattr(usage, "input_tokens", 0) or 0
    output_tokens = getattr(usage, "output_tokens", 0) or 0
    cached_tokens = getattr(usage, "cache_read_input_tokens", 0) or 0

    invocation_id = str(uuid.uuid4())

    # Primary write: Supabase skill_invocations
    _write_supabase(
        invocation_id=invocation_id,
        workflow=workflow,
        skill_name=skill_name,
        model=model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cached_tokens=cached_tokens,
        cost_usd=cost_usd,
        latency_ms=latency_ms,
        trigger_source=trigger_source,
        confidence=confidence,
        error=error,
    )

    # Archive write: Notion cost log (best-effort)
    _write_notion(
        workflow=workflow,
        model=model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cached_tokens=cached_tokens,
        cost_usd=cost_usd,
    )

    return invocation_id


def _write_supabase(
    invocation_id: str,
    workflow: str,
    skill_name: str,
    model: str,
    input_tokens: int,
    output_tokens: int,
    cached_tokens: int,
    cost_usd: float,
    latency_ms: int,
    trigger_source: str,
    confidence: Optional[float],
    error: Optional[str],
) -> None:
    """Insert into Supabase skill_invocations table."""
    try:
        from ts_shared.supabase_client import get_client

        client = get_client()
        now = datetime.now(timezone.utc).isoformat()
        row = {
            "id": invocation_id,
            "timestamp": now,
            "agent_name": workflow,
            "skill_name": skill_name,
            "trigger_source": trigger_source,
            "model_used": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cached_tokens": cached_tokens,
            "cost_usd": cost_usd,
            "latency_ms": latency_ms,
        }
        if confidence is not None:
            row["confidence_score"] = confidence
        if error:
            row["error"] = error
        client.table("skill_invocations").insert(row).execute()
        logger.info("Logged invocation %s to Supabase ($%.4f)", invocation_id, cost_usd)
    except Exception as e:
        logger.error("Failed to log invocation to Supabase: %s", e)


def _write_notion(
    workflow: str,
    model: str,
    input_tokens: int,
    output_tokens: int,
    cached_tokens: int,
    cost_usd: float,
) -> None:
    """Archive to Notion cost log (best-effort, never raises)."""
    try:
        from ts_shared.notion_ops import log_cost_to_notion

        log_cost_to_notion(
            workflow=workflow,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cached_tokens=cached_tokens,
            cost_usd=cost_usd,
        )
    except Exception as e:
        logger.warning("Notion cost log write failed (non-fatal): %s", e)
