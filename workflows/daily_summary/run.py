"""
Daily Summary Workflow — 6pm daily cron.

Queries today's orders from Supabase, calculates key metrics, calls Claude (Haiku)
to format a Slack-friendly summary, writes to task_inbox, logs run and cost.

Usage:
    python workflows/daily_summary/run.py
"""

import logging
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Ensure lib/ is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "lib"))

from ts_shared.supabase_client import get_client
from ts_shared.claude_client import (
    call_claude, load_skills, calculate_cost, MODEL_HAIKU,
)
from ts_shared.dashboard_ops import create_task, log_workflow_run, update_workflow_health
from ts_shared.cost_tracker import log_invocation
from ts_shared.notifications import notify

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
logger = logging.getLogger("workflow.daily_summary")

COMPANY_SLUG = "tibetan-spirit"
WORKFLOW_SLUG = "daily_summary"


def query_todays_orders(client) -> list[dict]:
    """Fetch today's orders from Supabase."""
    today_start = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    ).isoformat()

    result = (
        client.table("orders")
        .select("*")
        .gte("created_at", today_start)
        .execute()
    )
    return result.data or []


def query_unfulfilled_old_orders(client) -> list[dict]:
    """Fetch unfulfilled orders older than 24 hours."""
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()

    result = (
        client.table("orders")
        .select("order_number, total_price, created_at")
        .is_("fulfillment_status", "null")
        .lt("created_at", cutoff)
        .execute()
    )
    return result.data or []


def calculate_metrics(orders: list[dict]) -> dict:
    """Calculate daily summary metrics from order data."""
    if not orders:
        return {
            "order_count": 0,
            "revenue": 0.0,
            "aov": 0.0,
            "top_products": [],
            "large_orders": [],
        }

    revenue = sum(float(o.get("total_price", 0) or 0) for o in orders)
    order_count = len(orders)
    aov = revenue / order_count if order_count else 0

    # Top 5 products by revenue
    product_revenue: dict[str, float] = {}
    for order in orders:
        for item in (order.get("line_items") or []):
            title = item.get("title", "Unknown")
            item_rev = float(item.get("price", 0)) * int(item.get("quantity", 1))
            product_revenue[title] = product_revenue.get(title, 0) + item_rev

    top_products = sorted(
        product_revenue.items(), key=lambda x: x[1], reverse=True
    )[:5]

    # Large orders (>$500)
    large_orders = [
        {"order_number": o.get("order_number"), "total": float(o.get("total_price", 0))}
        for o in orders
        if float(o.get("total_price", 0) or 0) > 500
    ]

    return {
        "order_count": order_count,
        "revenue": round(revenue, 2),
        "aov": round(aov, 2),
        "top_products": [{"title": t, "revenue": round(r, 2)} for t, r in top_products],
        "large_orders": large_orders,
    }


def build_user_prompt(metrics: dict, unfulfilled: list[dict]) -> str:
    """Build the user prompt for Claude with today's data."""
    top_products_str = "\n".join(
        f"  {i+1}. {p['title']} — ${p['revenue']:.2f}"
        for i, p in enumerate(metrics["top_products"])
    ) or "  No sales today."

    large_str = "\n".join(
        f"  - Order #{o['order_number']}: ${o['total']:.2f}"
        for o in metrics["large_orders"]
    ) or "  None"

    unfulfilled_str = "\n".join(
        f"  - Order #{o['order_number']}: ${float(o.get('total_price', 0)):.2f} (placed {o.get('created_at', 'unknown')})"
        for o in unfulfilled[:10]
    ) or "  None"

    today = datetime.now(timezone.utc).strftime("%A, %B %d, %Y")

    return f"""Generate a concise daily operations summary for {today}.

DATA:
- Orders today: {metrics['order_count']}
- Revenue: ${metrics['revenue']:.2f}
- Average Order Value: ${metrics['aov']:.2f}

Top 5 products by revenue:
{top_products_str}

Large orders (>$500):
{large_str}

Unfulfilled orders >24 hours old ({len(unfulfilled)} total):
{unfulfilled_str}

FORMAT: Write a brief, Slack-friendly summary (3-5 paragraphs). Include all numbers.
Flag anything requiring attention. End with the decision support block.

The output MUST end with:
STATUS: GREEN/YELLOW/RED
VALUES CHECK: Cultural sensitivity [PASS] | Frequency [N/A]
COST: ${{cost}} (this run)
"""


def load_soul_file() -> str:
    """Load the operations agent soul file."""
    soul_path = Path(__file__).resolve().parent.parent.parent / "agents" / "operations" / "soul.md"
    if soul_path.exists():
        return soul_path.read_text(encoding="utf-8")
    return ""


def run() -> str:
    """Execute the daily summary workflow. Returns the task ID."""
    start = time.monotonic()
    started_at = datetime.now(timezone.utc)

    logger.info("Starting daily summary workflow")

    # 1. Load agent soul + skills
    soul = load_soul_file()
    _skill_metas, skills_body = load_skills(["shared/brand-guidelines", "shared/channel-config"])

    system_parts = []
    if soul:
        system_parts.append(soul)
    system_parts.append(skills_body)

    # 2. Query data
    client = get_client()
    orders = query_todays_orders(client)
    unfulfilled = query_unfulfilled_old_orders(client)

    # 3. Calculate metrics
    metrics = calculate_metrics(orders)

    # 4. Call Claude (Haiku)
    user_prompt = build_user_prompt(metrics, unfulfilled)
    response = call_claude(
        system_parts=system_parts,
        user_message=user_prompt,
        model=MODEL_HAIKU,
        max_tokens=1500,
    )

    output_text = response.content[0].text
    cost_usd = calculate_cost(response.usage, MODEL_HAIKU)

    duration_ms = int((time.monotonic() - start) * 1000)

    # 5. Write to task_inbox
    output_data = {
        **metrics,
        "unfulfilled_count": len(unfulfilled),
        "cost_usd": cost_usd,
    }

    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    run_id = log_workflow_run(
        company_slug=COMPANY_SLUG,
        workflow_slug=WORKFLOW_SLUG,
        status="completed",
        wake_reason="cron",
        steps_completed=1,
        steps_total=1,
        step_results=[{"step": "summarize", "status": "completed"}],
        input_tokens=response.usage.input_tokens,
        output_tokens=response.usage.output_tokens,
        total_cost_usd=cost_usd,
        model_used=MODEL_HAIKU,
        started_at=started_at,
        duration_ms=duration_ms,
    )

    task_id = create_task(
        company_slug=COMPANY_SLUG,
        workflow_slug=WORKFLOW_SLUG,
        title=f"Daily Summary — {today_str}",
        output=output_data,
        output_rendered=output_text,
        assignee="ceo",
        status="auto_logged",
        wake_reason="scheduled",
        cost_usd=cost_usd,
        run_id=run_id,
    )

    # 6. Update workflow health
    update_workflow_health(
        workflow_slug=WORKFLOW_SLUG,
        status="healthy",
        last_result="completed",
        cost=cost_usd,
        duration_ms=duration_ms,
    )

    # 7. Log cost
    log_invocation(
        workflow=WORKFLOW_SLUG,
        skill_name="daily-summary",
        model=MODEL_HAIKU,
        usage=response.usage,
        latency_ms=duration_ms,
    )

    # 8. Notify CEO via Slack
    slack_msg = (
        f"*Daily Summary — {today_str}*\n"
        f"Orders: {metrics['order_count']} | "
        f"Revenue: ${metrics['revenue']:.2f} | "
        f"AOV: ${metrics['aov']:.2f}\n"
        f"Cost: ${cost_usd:.4f}"
    )
    notify("ceo", slack_msg)

    logger.info(
        "Daily summary complete: %d orders, $%.2f revenue, cost $%.4f",
        metrics["order_count"], metrics["revenue"], cost_usd,
    )

    return task_id


if __name__ == "__main__":
    task_id = run()
    print(f"Task created: {task_id}")
