"""
Baseline data pull for Tibetan Spirit financial scenario model.

Pulls historical orders, products, and COGS from Supabase and returns a
structured baseline summary dict. Used as the foundation for all scenario
projections.

Schema reality (differs from task spec table names):
  - Table 'orders' (not ts_orders): id, created_at, total_price, fulfillment_status
  - Table 'products' (not ts_products): id, title, status, price,
      cogs_confirmed, cogs_estimated, cogs_confidence
  - No separate cogs table — COGS embedded in products

Usage (validation mode):
    python3 scripts/financial_model/baseline.py
"""

import logging
import os
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Support running as a script from worktree or main repo root.
# In a git worktree the .env lives in the main repo, not the worktree dir.
# Candidates (first found wins):
#   1. <worktree_root>/.env  (worktree has its own .env)
#   2. <worktree_root>/../../.env  (git worktree: .worktrees/<name>/../../ = main repo)
_worktree_root = Path(__file__).resolve().parent.parent.parent
load_dotenv(_worktree_root / ".env")
if not os.environ.get("SUPABASE_URL"):
    load_dotenv(_worktree_root.parent.parent / ".env")

sys.path.insert(0, str(_worktree_root / "lib"))

logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

PERIOD_START = "2025-01-01"
PERIOD_END = "2026-04-01"
FULFILLED_STATUS = "fulfilled"
COGS_CONFIRMED_THRESHOLD = 0.50
PAGE_SIZE = 1000  # Supabase default max per request

# Product category classification patterns (applied to product title).
# Derived from seed_cogs_from_model.py — kept as a standalone copy to avoid
# import dependency on that script. First match wins.
CATEGORY_PATTERNS: list[tuple[str, str]] = [
    (r"incense|dhoop|nado|rope\s*incense|cone\s*incense|\bsang\b|\bsur\b|agarwood|resin\b|palo\s*santo|charcoal\s*tablet", "incense"),
    (r"singing\s*bowl|sound\s*bowl|tibetan\s*bowl|tingsha", "singing_bowls"),
    (r"mala\b|prayer\s*bead|wrist\s*mala|bracelet|necklace|pendant|amulet", "malas"),
    (r"statue|figurine|gilded", "statues"),
    (r"ritual|vajra|dorje|\bbell\b|phurba|kapala|damaru|mandala|prayer.?wheel|conch", "ritual_objects"),
    (r"thangka|thanka|tangka|scroll\s*painting", "thangkas"),
    (r"prayer\s*flag|lungta|wind\s*horse|katag|khata", "prayer_flags"),
    (r"\bbook\b|\btext\b|sutra|dharma\s*pub|s[aā]dhana|commentary", "books"),
    (r"altar|offering\s*bowl|butter\s*lamp|incense\s*holder|burner|puja\s*set|stupa", "altar_supplies"),
]


# ---------------------------------------------------------------------------
# Pure function — testable without Supabase
# ---------------------------------------------------------------------------

def determine_cogs_quality(products_count: int, cogs_rows: list) -> dict:
    """
    Determine COGS data quality given active product count and raw COGS rows.

    Each row must have at minimum: cogs_pct (float or None), cogs_confidence (str).
    Rows without cogs_pct are excluded from the blended average.

    Args:
        products_count: Number of active products.
        cogs_rows: List of dicts with at least cogs_pct and cogs_confidence.

    Returns:
        Dict with keys: quality, coverage_pct, blended_cogs_pct, warning.
    """
    if products_count == 0 or not cogs_rows:
        return {
            "quality": "unavailable",
            "coverage_pct": 0.0,
            "blended_cogs_pct": None,
            "warning": "No COGS data available — projections cannot calculate margins.",
        }

    coverage_pct = len(cogs_rows) / products_count

    # Blended COGS % — simple average across products with a cogs_pct value
    cogs_pct_values = [
        row["cogs_pct"]
        for row in cogs_rows
        if row.get("cogs_pct") is not None
    ]
    blended_cogs_pct = (
        sum(cogs_pct_values) / len(cogs_pct_values) if cogs_pct_values else None
    )

    if coverage_pct < COGS_CONFIRMED_THRESHOLD:
        quality = "estimated"
        warning = (
            f"COGS data covers only {coverage_pct:.0%} of active products "
            f"(threshold: {COGS_CONFIRMED_THRESHOLD:.0%}) — projections will use estimated margins."
        )
        logger.warning(warning)
    else:
        quality = "confirmed"
        warning = None

    return {
        "quality": quality,
        "coverage_pct": round(coverage_pct, 4),
        "blended_cogs_pct": round(blended_cogs_pct, 4) if blended_cogs_pct is not None else None,
        "warning": warning,
    }


# ---------------------------------------------------------------------------
# Supabase queries (paginated where needed)
# ---------------------------------------------------------------------------

def _fetch_all_pages(client, table: str, select: str, filters: Optional[list] = None) -> list:
    """Fetch all rows from a table, handling Supabase's 1000-row page limit."""
    rows = []
    offset = 0
    while True:
        q = client.table(table).select(select).range(offset, offset + PAGE_SIZE - 1)
        if filters:
            for method, *args in filters:
                q = getattr(q, method)(*args)
        result = q.execute()
        batch = result.data or []
        rows.extend(batch)
        if len(batch) < PAGE_SIZE:
            break
        offset += PAGE_SIZE
    return rows


def _fetch_orders(client) -> list:
    """Fetch fulfilled orders in the analysis period."""
    return _fetch_all_pages(
        client,
        table="orders",
        select="id,created_at,total_price,fulfillment_status",
        filters=[
            ("gte", "created_at", PERIOD_START),
            ("lt", "created_at", PERIOD_END),
            ("eq", "fulfillment_status", "fulfilled"),
        ],
    )


def _fetch_active_products(client) -> list:
    """Fetch active products with COGS fields."""
    return _fetch_all_pages(
        client,
        table="products",
        select="id,title,status,price,cogs_confirmed,cogs_estimated,cogs_confidence",
        filters=[("eq", "status", "active")],
    )


# ---------------------------------------------------------------------------
# Aggregation helpers
# ---------------------------------------------------------------------------

def _summarize_orders(rows: list) -> dict:
    """Summarize orders — all fetched orders are counted (pre-filtered to fulfilled)."""
    if not rows:
        return {
            "total_count": 0,
            "total_revenue_usd": 0.0,
            "aov_usd": 0.0,
            "monthly_volume": {},
            "monthly_revenue": {},
        }

    total_revenue = sum(float(r["total_price"]) for r in rows)
    monthly_volume: dict[str, int] = defaultdict(int)
    monthly_revenue: dict[str, float] = defaultdict(float)
    for r in rows:
        # created_at is ISO 8601, e.g. "2025-03-15T14:22:00+00:00"
        month_key = r["created_at"][:7]  # "YYYY-MM"
        monthly_volume[month_key] += 1
        monthly_revenue[month_key] += float(r["total_price"])

    return {
        "total_count": len(rows),
        "total_revenue_usd": round(total_revenue, 2),
        "aov_usd": round(total_revenue / len(rows), 2),
        "monthly_volume": dict(sorted(monthly_volume.items())),
        "monthly_revenue": {k: round(v, 2) for k, v in sorted(monthly_revenue.items())},
    }


def _build_cogs_rows_from_products(product_rows: list) -> list:
    """
    Extract COGS data from product rows for determine_cogs_quality().

    Returns a list of dicts with: product_id, cogs_pct, cogs_confidence.
    cogs_pct is derived as cogs_confirmed/price or cogs_estimated/price.
    Products with no price or no COGS dollar amount are excluded.
    """
    cogs_rows = []
    for row in product_rows:
        price = row.get("price") or 0
        if price <= 0:
            continue

        cogs_confirmed = row.get("cogs_confirmed")
        cogs_estimated = row.get("cogs_estimated")
        cogs_amount = cogs_confirmed if cogs_confirmed is not None else cogs_estimated
        if cogs_amount is None:
            continue

        cogs_rows.append({
            "product_id": row["id"],
            "cogs_pct": round(cogs_amount / price, 4),
            "cogs_confidence": row.get("cogs_confidence") or "unknown",
        })
    return cogs_rows


def _classify_product(title: str) -> str:
    """Classify a product into a category based on title regex patterns."""
    text = title.lower()
    for pattern, category in CATEGORY_PATTERNS:
        if re.search(pattern, text):
            return category
    return "other"


def _summarize_products(rows: list) -> dict:
    """Summarize active products by category (using title regex heuristic)."""
    by_type: dict[str, int] = defaultdict(int)
    for row in rows:
        category = _classify_product(row.get("title", ""))
        by_type[category] += 1

    return {
        "active_count": len(rows),
        "by_product_type": dict(sorted(by_type.items())),
    }


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def build_baseline() -> dict:
    """
    Pull historical data from Supabase and return a baseline summary dict.

    Returns:
        Baseline dict with period, orders, products, and cogs sections.

    Raises:
        SystemExit on missing env vars or Supabase errors.
    """
    try:
        from ts_shared.supabase_client import get_client
    except ImportError as e:
        print(f"ERROR: Cannot import Supabase client — {e}", file=sys.stderr)
        sys.exit(1)

    try:
        client = get_client()
    except EnvironmentError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        order_rows = _fetch_orders(client)
        product_rows = _fetch_active_products(client)
    except Exception as e:
        print(f"ERROR: Supabase query failed — {e}", file=sys.stderr)
        sys.exit(1)

    orders_summary = _summarize_orders(order_rows)
    products_summary = _summarize_products(product_rows)

    cogs_rows = _build_cogs_rows_from_products(product_rows)
    cogs_summary = determine_cogs_quality(
        products_count=products_summary["active_count"],
        cogs_rows=cogs_rows,
    )

    return {
        "period": {"start": PERIOD_START, "end": PERIOD_END},
        "orders": orders_summary,
        "products": products_summary,
        "cogs": cogs_summary,
    }


def _print_summary(baseline: dict) -> None:
    """Print a human-readable summary of the baseline."""
    period = baseline["period"]
    orders = baseline["orders"]
    cogs = baseline["cogs"]
    products = baseline["products"]

    print(f"\n=== Tibetan Spirit Baseline ({period['start']} \u2192 {period['end']}) ===")
    print(
        f"Orders: {orders['total_count']:,} orders | "
        f"Revenue: ${orders['total_revenue_usd']:,.2f} | "
        f"AOV: ${orders['aov_usd']:,.2f}"
    )
    print(f"Active Products: {products['active_count']:,}")

    if products.get("by_product_type"):
        print("  Product Categories:")
        for cat, count in products["by_product_type"].items():
            print(f"    {cat}: {count}")

    if orders.get("monthly_revenue"):
        print("  Monthly Revenue:")
        for month, rev in orders["monthly_revenue"].items():
            vol = orders["monthly_volume"].get(month, 0)
            print(f"    {month}: ${rev:,.2f} ({vol} orders)")

    coverage_display = f"{cogs['coverage_pct']:.0%}" if cogs["coverage_pct"] else "0%"
    blended_display = (
        f" | Blended COGS: {cogs['blended_cogs_pct']:.1%}"
        if cogs["blended_cogs_pct"] is not None
        else ""
    )
    print(
        f"COGS Coverage: {coverage_display} of active products "
        f"({cogs['quality']} confidence){blended_display}"
    )

    if cogs["warning"]:
        print(f"\u26a0 WARNING: {cogs['warning']}")

    print()


if __name__ == "__main__":
    baseline = build_baseline()
    _print_summary(baseline)
