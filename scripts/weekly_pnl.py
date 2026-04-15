"""
Weekly P&L Workflow — Monday 6am cron.

Three-step prompt chain:
  Step 1 (Python): Query 7-day orders, join with products for COGS, calculate
    revenue, COGS, gross margin, fees, AOV. Compare to prior week.
  Step 2 (Sonnet): Format as CEO-ready P&L report with trends, top products,
    concerns, recommended actions. Includes decision support format.
  Step 3: Write to task_inbox (needs_review, assignee=ceo, priority=P2).
    Log workflow_run and cost.

Usage:
    python workflows/weekly_pnl/run.py
"""

import json
import logging
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "lib"))

from ts_shared.supabase_client import get_client
from ts_shared.claude_client import (
    call_claude, load_skills, calculate_cost, MODEL_SONNET,
)
from ts_shared.dashboard_ops import create_task, log_workflow_run, update_workflow_health
from ts_shared.cost_tracker import log_invocation
from ts_shared.notifications import notify

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
logger = logging.getLogger("workflow.weekly_pnl")

COMPANY_SLUG = "tibetan-spirit"
WORKFLOW_SLUG = "weekly_pnl"

# Shopify fee constants
SHOPIFY_PCT_FEE = 0.025
SHOPIFY_FLAT_FEE = 0.30


# ============================================================================
# Step 1: Data gathering and calculations (pure Python)
# ============================================================================


def query_week_orders(client, start: datetime, end: datetime) -> list[dict]:
    """Fetch orders for a date range."""
    result = (
        client.table("orders")
        .select("*")
        .gte("created_at", start.isoformat())
        .lt("created_at", end.isoformat())
        .execute()
    )
    return result.data or []


def query_products(client) -> dict[str, dict]:
    """Load all products keyed by SKU."""
    result = (
        client.table("products")
        .select("sku, title, price, cogs_confirmed, cogs_estimated, cogs_confidence, freight_per_unit, duty_rate")
        .eq("status", "active")
        .execute()
    )
    return {p["sku"]: p for p in (result.data or []) if p.get("sku")}


def get_cogs(product: dict) -> float:
    """Get COGS for a product, preferring confirmed over estimated."""
    cogs = product.get("cogs_confirmed")
    if cogs is not None:
        return float(cogs)
    cogs = product.get("cogs_estimated")
    if cogs is not None:
        return float(cogs)
    return 0.0


def get_landed_cost(product: dict) -> float:
    """Calculate full landed cost: COGS + freight + duty."""
    cogs = get_cogs(product)
    freight = float(product.get("freight_per_unit") or 0)
    duty_rate = float(product.get("duty_rate") or 0)
    return cogs + freight + (cogs * duty_rate)


def calculate_pnl(orders: list[dict], products: dict[str, dict]) -> dict:
    """Calculate P&L metrics from orders and products.

    Returns:
        Dict with revenue, cogs, fees, gross_profit, margin_pct, aov,
        order_count, top_products, cogs_confidence_breakdown.
    """
    if not orders:
        return {
            "revenue": 0.0, "cogs": 0.0, "fees": 0.0, "gross_profit": 0.0,
            "margin_pct": 0.0, "aov": 0.0, "order_count": 0,
            "top_products": [], "cogs_unknown_count": 0,
            "cogs_estimated_count": 0, "cogs_confirmed_count": 0,
        }

    revenue = sum(float(o.get("total_price", 0) or 0) for o in orders)
    order_count = len(orders)
    aov = revenue / order_count if order_count else 0

    # Calculate COGS from line items
    total_cogs = 0.0
    product_metrics: dict[str, dict] = {}
    cogs_confidence_counts = {"confirmed": 0, "estimated": 0, "unknown": 0}
    seen_skus = set()

    for order in orders:
        for item in (order.get("line_items") or []):
            sku = item.get("sku", "")
            title = item.get("title", "Unknown")
            qty = int(item.get("quantity", 1))
            item_price = float(item.get("price", 0))
            item_revenue = item_price * qty

            product = products.get(sku, {})
            item_cogs = get_landed_cost(product) * qty
            total_cogs += item_cogs

            if sku and sku not in seen_skus:
                seen_skus.add(sku)
                confidence = product.get("cogs_confidence", "unknown")
                cogs_confidence_counts[confidence] = cogs_confidence_counts.get(confidence, 0) + 1

            if title not in product_metrics:
                product_metrics[title] = {"revenue": 0, "cogs": 0, "units": 0}
            product_metrics[title]["revenue"] += item_revenue
            product_metrics[title]["cogs"] += item_cogs
            product_metrics[title]["units"] += qty

    # Shopify fees
    fees = sum(
        float(o.get("total_price", 0) or 0) * SHOPIFY_PCT_FEE + SHOPIFY_FLAT_FEE
        for o in orders
    )

    gross_profit = revenue - total_cogs - fees
    margin_pct = (gross_profit / revenue * 100) if revenue else 0

    # Top products by revenue
    top_products = sorted(
        [
            {
                "title": title,
                "revenue": round(m["revenue"], 2),
                "cogs": round(m["cogs"], 2),
                "units": m["units"],
                "margin_pct": round(
                    ((m["revenue"] - m["cogs"]) / m["revenue"] * 100)
                    if m["revenue"] else 0, 1
                ),
            }
            for title, m in product_metrics.items()
        ],
        key=lambda x: x["revenue"],
        reverse=True,
    )[:10]

    return {
        "revenue": round(revenue, 2),
        "cogs": round(total_cogs, 2),
        "fees": round(fees, 2),
        "gross_profit": round(gross_profit, 2),
        "margin_pct": round(margin_pct, 1),
        "aov": round(aov, 2),
        "order_count": order_count,
        "top_products": top_products,
        "cogs_confirmed_count": cogs_confidence_counts.get("confirmed", 0),
        "cogs_estimated_count": cogs_confidence_counts.get("estimated", 0),
        "cogs_unknown_count": cogs_confidence_counts.get("unknown", 0),
    }


def calculate_wow_change(current: dict, prior: dict) -> dict:
    """Calculate week-over-week changes."""
    changes = {}
    for key in ("revenue", "gross_profit", "order_count", "aov", "margin_pct"):
        curr = current.get(key, 0)
        prev = prior.get(key, 0)
        if prev:
            pct = ((curr - prev) / abs(prev)) * 100
        elif curr:
            pct = 100.0
        else:
            pct = 0.0
        changes[key] = {
            "current": curr,
            "prior": prev,
            "change_pct": round(pct, 1),
            "direction": "up" if pct > 2 else ("down" if pct < -2 else "flat"),
        }
    return changes


# ============================================================================
# Step 2: Claude formats the report (Sonnet)
# ============================================================================


def build_pnl_prompt(
    current_pnl: dict,
    prior_pnl: dict,
    wow: dict,
    week_start: str,
    week_end: str,
) -> str:
    """Build the user prompt for Sonnet to format the P&L report."""
    top_products_str = "\n".join(
        f"  {i+1}. {p['title']} — ${p['revenue']:.2f} revenue, "
        f"${p['cogs']:.2f} COGS, {p['margin_pct']}% margin, {p['units']} units"
        for i, p in enumerate(current_pnl["top_products"])
    ) or "  No product data."

    wow_str = "\n".join(
        f"  {key}: {v['current']} (was {v['prior']}, {v['change_pct']:+.1f}% {v['direction']})"
        for key, v in wow.items()
    )

    return f"""Generate a CEO-ready Weekly P&L Report for the week of {week_start} to {week_end}.

FINANCIAL DATA:
- Revenue: ${current_pnl['revenue']:.2f}
- COGS: ${current_pnl['cogs']:.2f}
- Shopify Fees: ${current_pnl['fees']:.2f}
- Gross Profit: ${current_pnl['gross_profit']:.2f}
- Gross Margin: {current_pnl['margin_pct']}%
- Orders: {current_pnl['order_count']}
- AOV: ${current_pnl['aov']:.2f}

COGS DATA QUALITY:
- Confirmed: {current_pnl['cogs_confirmed_count']} SKUs
- Estimated: {current_pnl['cogs_estimated_count']} SKUs
- Unknown: {current_pnl['cogs_unknown_count']} SKUs

WEEK-OVER-WEEK:
{wow_str}

TOP PRODUCTS:
{top_products_str}

FORMAT: Write a structured P&L report suitable for a CEO reviewing on mobile.
Include:
1. Executive summary (3 lines max)
2. Key metrics table
3. Week-over-week comparison with trend arrows (▲/▼/─)
4. Top products by revenue
5. Concerns and recommended actions
6. COGS data quality note if unknowns > 0

End with the decision support block:
STATUS: GREEN/YELLOW/RED
DECISIONS NEEDED: [specific decisions if any]
VALUES CHECK: Cultural sensitivity [PASS] | Frequency [N/A]
COST: ${{cost}} (this run)
"""


def load_soul_file() -> str:
    """Load the finance agent soul file."""
    soul_path = Path(__file__).resolve().parent.parent.parent / "agents" / "finance" / "soul.md"
    if soul_path.exists():
        return soul_path.read_text(encoding="utf-8")
    return ""


# ============================================================================
# Step 3: Write results and notify
# ============================================================================


def run() -> str:
    """Execute the weekly P&L workflow. Returns the task ID."""
    start = time.monotonic()
    started_at = datetime.now(timezone.utc)

    logger.info("Starting weekly P&L workflow")

    # Date ranges
    now = datetime.now(timezone.utc)
    week_end = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = week_end - timedelta(days=7)
    prior_start = week_start - timedelta(days=7)

    # Step 1: Data gathering
    client = get_client()
    products = query_products(client)

    current_orders = query_week_orders(client, week_start, week_end)
    prior_orders = query_week_orders(client, prior_start, week_start)

    current_pnl = calculate_pnl(current_orders, products)
    prior_pnl = calculate_pnl(prior_orders, products)
    wow = calculate_wow_change(current_pnl, prior_pnl)

    # Step 2: Format via Sonnet
    soul = load_soul_file()
    _skill_metas, skills_body = load_skills([
        "shared/brand-guidelines",
        "finance/cogs-tracking",
        "finance/margin-reporting",
    ])

    system_parts = []
    if soul:
        system_parts.append(soul)
    system_parts.append(skills_body)

    week_start_str = week_start.strftime("%Y-%m-%d")
    week_end_str = week_end.strftime("%Y-%m-%d")

    user_prompt = build_pnl_prompt(current_pnl, prior_pnl, wow, week_start_str, week_end_str)
    response = call_claude(
        system_parts=system_parts,
        user_message=user_prompt,
        model=MODEL_SONNET,
        max_tokens=2500,
    )

    output_text = response.content[0].text
    cost_usd = calculate_cost(response.usage, MODEL_SONNET)
    duration_ms = int((time.monotonic() - start) * 1000)

    # Step 3: Write to task_inbox and log
    output_data = {
        **current_pnl,
        "week_start": week_start_str,
        "week_end": week_end_str,
        "week_over_week": wow,
        "cost_usd": cost_usd,
    }

    run_id = log_workflow_run(
        company_slug=COMPANY_SLUG,
        workflow_slug=WORKFLOW_SLUG,
        status="completed",
        wake_reason="cron",
        steps_completed=2,
        steps_total=2,
        step_results=[
            {"step": "data_gathering", "status": "completed"},
            {"step": "format_report", "status": "completed"},
        ],
        input_tokens=response.usage.input_tokens,
        output_tokens=response.usage.output_tokens,
        total_cost_usd=cost_usd,
        model_used=MODEL_SONNET,
        started_at=started_at,
        duration_ms=duration_ms,
    )

    task_id = create_task(
        company_slug=COMPANY_SLUG,
        workflow_slug=WORKFLOW_SLUG,
        title=f"Weekly P&L — {week_start_str} to {week_end_str}",
        output=output_data,
        output_rendered=output_text,
        assignee="ceo",
        priority="P2",
        status="needs_review",
        wake_reason="scheduled",
        cost_usd=cost_usd,
        run_id=run_id,
    )

    update_workflow_health(
        workflow_slug=WORKFLOW_SLUG,
        status="healthy",
        last_result="completed",
        cost=cost_usd,
        duration_ms=duration_ms,
    )

    log_invocation(
        workflow=WORKFLOW_SLUG,
        skill_name="weekly-pnl",
        model=MODEL_SONNET,
        usage=response.usage,
        latency_ms=duration_ms,
    )

    notify("ceo", f"*Weekly P&L ready for review* — {week_start_str} to {week_end_str}")

    logger.info(
        "Weekly P&L complete: $%.2f revenue, %.1f%% margin, cost $%.4f",
        current_pnl["revenue"], current_pnl["margin_pct"], cost_usd,
    )

    return task_id


if __name__ == "__main__":
    task_id = run()
    print(f"Task created: {task_id}")
