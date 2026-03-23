"""
Skill invocation logging for the audit trail.

Every skill execution is logged to the `skill_invocations` table in Supabase.
This provides a complete audit trail, cost tracking, and the data needed for
Phase 1 → Phase 2 graduation decisions.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

logger = logging.getLogger("ts-ops.logging")


async def log_skill_invocation(
    agent_name: str,
    skill_name: str,
    prompt: str,
    result: dict[str, Any],
    cost_usd: float = 0.0,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    model_used: str = "sonnet-4.6",
    input_tokens: int = 0,
    output_tokens: int = 0,
    cached_tokens: int = 0,
    confidence_score: Optional[float] = None,
    trigger_source: str = "manual",
    phase: int = 1,
    human_approved: Optional[bool] = None,
    status: str = "success",
    error: Optional[str] = None,
    invocation_id: Optional[str] = None,
) -> str:
    """
    Log a skill invocation to the skill_invocations table.

    Returns the invocation ID for reference.
    """
    if invocation_id is None:
        invocation_id = str(uuid4())

    if start_time is None:
        start_time = datetime.now(timezone.utc)
    if end_time is None:
        end_time = datetime.now(timezone.utc)

    latency_ms = int((end_time - start_time).total_seconds() * 1000)

    record = {
        "id": invocation_id,
        "timestamp": start_time.isoformat(),
        "agent_name": agent_name,
        "skill_name": skill_name,
        "trigger_source": trigger_source,
        "raw_input": json.dumps({"prompt": prompt}),
        "raw_output": json.dumps(result),
        "model_used": model_used,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cached_tokens": cached_tokens,
        "cost_usd": cost_usd,
        "latency_ms": latency_ms,
        "confidence_score": confidence_score,
        "phase": phase,
        "human_approved": human_approved,
        "status": status,
        "error": error,
    }

    try:
        # TODO: Uncomment when Supabase is configured
        # from ts_shared.supabase_client import get_client
        # client = get_client()
        # client.table("skill_invocations").insert(record).execute()
        logger.info(
            f"Skill invocation logged: {skill_name} ({status}) "
            f"cost=${cost_usd:.4f} latency={latency_ms}ms"
        )
    except Exception as e:
        # Logging should never crash the skill — log locally and continue
        logger.error(f"Failed to log skill invocation to Supabase: {e}")
        logger.info(f"Fallback log: {json.dumps(record)}")

    return invocation_id
