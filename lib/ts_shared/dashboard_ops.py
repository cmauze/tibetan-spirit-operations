"""
Dashboard operations — write to Supabase runtime tables (task_inbox, workflow_runs,
workflow_health, spend_records).

These are the primary write functions used by workflow scripts to record results,
update health status, and track spend.

Usage:
    from ts_shared.dashboard_ops import create_task, log_workflow_run

    task_id = create_task(
        company_slug="tibetan-spirit",
        workflow_slug="daily_summary",
        title="Daily Summary — 2026-03-30",
        output={"revenue": 1234.56, "orders": 8},
        output_rendered="Revenue: $1,234.56 | Orders: 8",
        assignee="ceo",
    )
"""

import logging
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)


def _get_client():
    """Lazy import to avoid circular imports and allow mocking."""
    from ts_shared.supabase_client import get_client
    return get_client()


def _resolve_id(table: str, slug_column: str, slug_value: str) -> Optional[str]:
    """Look up a UUID by slug. Returns None if not found."""
    result = (
        _get_client()
        .table(table)
        .select("id")
        .eq(slug_column, slug_value)
        .limit(1)
        .execute()
    )
    if result.data:
        return result.data[0]["id"]
    return None


def create_task(
    company_slug: str,
    workflow_slug: str,
    title: str,
    output: dict,
    output_rendered: str,
    assignee: str,
    priority: str = "P2",
    wake_reason: str = "scheduled",
    cost_usd: float = 0,
    status: str = "needs_review",
    run_id: Optional[str] = None,
) -> str:
    """Insert a task into task_inbox. Returns the task ID.

    Args:
        company_slug: Company slug (e.g. "tibetan-spirit").
        workflow_slug: Workflow slug (e.g. "daily_summary").
        title: Human-readable task title.
        output: Structured output data (JSONB).
        output_rendered: Formatted text for display.
        assignee: Role ID of the person responsible (e.g. "ceo").
        priority: Priority level (P0-P3). Default P2.
        wake_reason: Why this task was created. Default "scheduled".
        cost_usd: Cost of generating this task. Default 0.
        status: Initial task status. Default "needs_review".
        run_id: Optional workflow_run ID to link.

    Returns:
        UUID string of the created task.
    """
    company_id = _resolve_id("companies", "slug", company_slug)
    if not company_id:
        raise ValueError(f"Company not found: {company_slug}")

    workflow_id = _resolve_id("workflows", "slug", workflow_slug)

    row = {
        "company_id": company_id,
        "workflow_id": workflow_id,
        "title": title,
        "status": status,
        "priority": priority,
        "assignee": assignee,
        "output": output,
        "output_rendered": output_rendered,
        "wake_reason": wake_reason,
        "cost_usd": cost_usd,
    }
    if run_id:
        row["run_id"] = run_id

    result = _get_client().table("task_inbox").insert(row).execute()
    task_id = result.data[0]["id"]
    logger.info("Created task %s: %s", task_id, title)
    return task_id


def update_task_status(
    task_id: str,
    status: str,
    feedback: Optional[str] = None,
    feedback_by: Optional[str] = None,
) -> None:
    """Update a task's status and optional feedback.

    Args:
        task_id: UUID of the task.
        status: New status (needs_review, in_progress, approved, rejected, auto_logged).
        feedback: Optional feedback text.
        feedback_by: Optional role ID of who gave feedback.
    """
    update = {"status": status}
    if feedback is not None:
        update["feedback"] = feedback
        update["feedback_at"] = datetime.now(timezone.utc).isoformat()
    if feedback_by is not None:
        update["feedback_by"] = feedback_by

    _get_client().table("task_inbox").update(update).eq("id", task_id).execute()
    logger.info("Updated task %s -> %s", task_id, status)


def log_workflow_run(
    company_slug: str,
    workflow_slug: str,
    status: str,
    wake_reason: str,
    steps_completed: int,
    steps_total: int,
    step_results: list[dict],
    input_tokens: int,
    output_tokens: int,
    total_cost_usd: float,
    model_used: str,
    error_message: Optional[str] = None,
    error_step: Optional[str] = None,
    started_at: Optional[datetime] = None,
    duration_ms: Optional[int] = None,
) -> str:
    """Log a workflow execution to workflow_runs. Returns the run ID.

    Args:
        company_slug: Company slug.
        workflow_slug: Workflow slug.
        status: Run status (pending, running, completed, failed, cancelled).
        wake_reason: Why this run was triggered.
        steps_completed: Number of steps completed.
        steps_total: Total steps in the workflow.
        step_results: List of per-step result dicts.
        input_tokens: Total input tokens consumed.
        output_tokens: Total output tokens produced.
        total_cost_usd: Total cost of this run.
        model_used: Primary model used.
        error_message: Error message if failed.
        error_step: Which step failed.
        started_at: When the run started. Defaults to now.
        duration_ms: Total duration in milliseconds.

    Returns:
        UUID string of the created run.
    """
    company_id = _resolve_id("companies", "slug", company_slug)
    if not company_id:
        raise ValueError(f"Company not found: {company_slug}")

    workflow_id = _resolve_id("workflows", "slug", workflow_slug)

    now = datetime.now(timezone.utc)
    run_started = started_at or now

    row = {
        "company_id": company_id,
        "workflow_id": workflow_id,
        "status": status,
        "wake_reason": wake_reason,
        "steps_completed": steps_completed,
        "steps_total": steps_total,
        "step_results": step_results,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_cost_usd": total_cost_usd,
        "model_used": model_used,
        "started_at": run_started.isoformat(),
        "completed_at": now.isoformat() if status in ("completed", "failed") else None,
        "duration_ms": duration_ms,
    }
    if error_message:
        row["error_message"] = error_message
    if error_step:
        row["error_step"] = error_step

    # Resolve agent_id from workflow if possible
    if workflow_id:
        wf = (
            _get_client()
            .table("workflows")
            .select("agent_id")
            .eq("id", workflow_id)
            .limit(1)
            .execute()
        )
        if wf.data and wf.data[0].get("agent_id"):
            row["agent_id"] = wf.data[0]["agent_id"]

    result = _get_client().table("workflow_runs").insert(row).execute()
    run_id = result.data[0]["id"]
    logger.info("Logged workflow run %s: %s (%s)", run_id, workflow_slug, status)
    return run_id


def update_workflow_health(
    workflow_slug: str,
    status: str,
    last_result: str,
    cost: Optional[float] = None,
    duration_ms: Optional[int] = None,
) -> None:
    """Update or insert a workflow's health record.

    Args:
        workflow_slug: Workflow slug.
        status: Health status (healthy, degraded, failing, disabled).
        last_result: Description of last result (e.g. "completed", "failed: timeout").
        cost: Cost of the last run (updates avg_cost_per_run).
        duration_ms: Duration of the last run (updates avg_duration_ms).
    """
    workflow_id = _resolve_id("workflows", "slug", workflow_slug)
    if not workflow_id:
        logger.warning("Workflow not found for health update: %s", workflow_slug)
        return

    # Look up company_id from workflow
    wf = (
        _get_client()
        .table("workflows")
        .select("company_id")
        .eq("id", workflow_id)
        .limit(1)
        .execute()
    )
    company_id = wf.data[0]["company_id"] if wf.data else None

    now = datetime.now(timezone.utc).isoformat()

    update = {
        "status": status,
        "last_run_at": now,
        "last_result": last_result,
    }
    if cost is not None:
        update["avg_cost_per_run"] = cost
    if duration_ms is not None:
        update["avg_duration_ms"] = duration_ms

    # Try upsert: update if exists, insert if not
    existing = (
        _get_client()
        .table("workflow_health")
        .select("id")
        .eq("workflow_id", workflow_id)
        .limit(1)
        .execute()
    )

    if existing.data:
        _get_client().table("workflow_health").update(update).eq(
            "workflow_id", workflow_id
        ).execute()
    else:
        update["workflow_id"] = workflow_id
        update["company_id"] = company_id
        _get_client().table("workflow_health").insert(update).execute()

    logger.info("Updated workflow health: %s -> %s", workflow_slug, status)


def log_spend(
    period: str,
    period_type: str,
    company_slug: str,
    workflow_slug: str,
    run_count: int,
    success_count: int,
    failure_count: int,
    total_input_tokens: int = 0,
    total_output_tokens: int = 0,
    total_cost_usd: float = 0,
    budget_usd: Optional[float] = None,
    models_used: Optional[list[str]] = None,
) -> None:
    """Log or update a spend record for a period.

    Uses upsert on (period, period_type, company_slug, workflow_slug).

    Args:
        period: Date string (YYYY-MM-DD) for the period start.
        period_type: "daily", "weekly", or "monthly".
        company_slug: Company slug.
        workflow_slug: Workflow slug.
        run_count: Number of runs in this period.
        success_count: Successful runs.
        failure_count: Failed runs.
        total_input_tokens: Total input tokens.
        total_output_tokens: Total output tokens.
        total_cost_usd: Total cost.
        budget_usd: Budget for this period (optional).
        models_used: List of model IDs used.
    """
    company_id = _resolve_id("companies", "slug", company_slug)
    if not company_id:
        raise ValueError(f"Company not found: {company_slug}")

    workflow_id = _resolve_id("workflows", "slug", workflow_slug)

    row = {
        "period": period,
        "period_type": period_type,
        "company_id": company_id,
        "workflow_id": workflow_id,
        "run_count": run_count,
        "success_count": success_count,
        "failure_count": failure_count,
        "total_input_tokens": total_input_tokens,
        "total_output_tokens": total_output_tokens,
        "total_cost_usd": total_cost_usd,
    }
    if budget_usd is not None:
        row["budget_usd"] = budget_usd
    if models_used is not None:
        row["models_used"] = models_used

    _get_client().table("spend_records").upsert(
        row,
        on_conflict="period,period_type,company_id,workflow_id",
    ).execute()
    logger.info(
        "Logged spend: %s %s %s/$%.4f",
        workflow_slug, period_type, period, total_cost_usd,
    )
