#!/usr/bin/env python3
"""
Backfill Supabase from Shopify API.

Paginates through all accessible orders and products, upserting into
the Supabase orders and products tables. Respects Shopify's 60-day
API window (use import_orders_csv.py for full historical data).

Usage:
    python3 scripts/backfill_shopify.py              # backfill all
    python3 scripts/backfill_shopify.py --products    # products only
    python3 scripts/backfill_shopify.py --orders      # orders only
    python3 scripts/backfill_shopify.py --dry-run     # preview without writing

Also used as the daily sync (cron calls with no flags = full sync).
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

STORE_URL = os.environ.get("SHOPIFY_STORE_URL", "")
ACCESS_TOKEN = os.environ.get("SHOPIFY_ACCESS_TOKEN", "")
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")
API_VERSION = "2025-01"

CHANNEL_MAP = {"web": "shopify", "pos": "shopify", "shopify_draft_order": "shopify"}


def shopify_get(endpoint: str, params: dict | None = None) -> tuple[dict, str | None]:
    """GET from Shopify Admin API. Returns (data, next_page_url)."""
    url = f"https://{STORE_URL}/admin/api/{API_VERSION}/{endpoint}"
    if params:
        url += "?" + urllib.parse.urlencode(params)

    req = urllib.request.Request(url)
    req.add_header("X-Shopify-Access-Token", ACCESS_TOKEN)
    req.add_header("Content-Type", "application/json")

    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        # Parse Link header for pagination
        link_header = resp.headers.get("Link", "")
        next_url = None
        if 'rel="next"' in link_header:
            for part in link_header.split(","):
                if 'rel="next"' in part:
                    next_url = part.split("<")[1].split(">")[0]
        return data, next_url


def shopify_get_page(full_url: str) -> tuple[dict, str | None]:
    """GET a full URL (for cursor-based pagination)."""
    req = urllib.request.Request(full_url)
    req.add_header("X-Shopify-Access-Token", ACCESS_TOKEN)
    req.add_header("Content-Type", "application/json")

    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        link_header = resp.headers.get("Link", "")
        next_url = None
        if 'rel="next"' in link_header:
            for part in link_header.split(","):
                if 'rel="next"' in part:
                    next_url = part.split("<")[1].split(">")[0]
        return data, next_url


def supabase_upsert(table: str, rows: list[dict], on_conflict: str) -> int:
    """Upsert rows into Supabase. Returns count of rows sent."""
    if not rows:
        return 0
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates",
    }
    # Upsert in batches of 100
    total = 0
    for i in range(0, len(rows), 100):
        batch = rows[i : i + 100]
        body = json.dumps(batch, default=str).encode()
        req = urllib.request.Request(url, data=body, method="POST")
        for k, v in headers.items():
            req.add_header(k, v)
        with urllib.request.urlopen(req) as resp:
            resp.read()
        total += len(batch)
    return total


def transform_product(p: dict) -> dict:
    """Transform Shopify product → Supabase products row."""
    v = p.get("variants", [{}])[0]
    return {
        "shopify_id": p["id"],
        "title": p["title"],
        "handle": p.get("handle"),
        "sku": v.get("sku"),
        "price": float(v.get("price", 0)) if v.get("price") else None,
        "status": p.get("status", "active"),
        "cogs_confidence": "unknown",
    }


def transform_order(o: dict) -> dict:
    """Transform Shopify order → Supabase orders row."""
    source = o.get("source_name", "web")
    channel = CHANNEL_MAP.get(source, "shopify")

    # Determine fulfillment route from shipping country
    shipping = o.get("shipping_address") or {}
    country = shipping.get("country_code", "US")
    if country == "US":
        route = "domestic"
    elif country in ("MX", "GT", "HN", "SV", "CR", "PA", "CO", "PE", "CL", "AR", "BR"):
        route = "mexico"
    else:
        route = "nepal"

    line_items = [
        {
            "sku": li.get("sku"),
            "title": li.get("title"),
            "quantity": li.get("quantity"),
            "price": li.get("price"),
        }
        for li in o.get("line_items", [])
    ]

    return {
        "shopify_id": o["id"],
        "order_number": str(o.get("order_number", "")),
        "email": o.get("email"),
        "channel": channel,
        "total_price": float(o.get("total_price", 0)),
        "currency": o.get("currency", "USD"),
        "fulfillment_status": o.get("fulfillment_status"),
        "fulfillment_route": route,
        "line_items": line_items,
        "shipping_address": shipping if shipping else None,
        "created_at": o.get("created_at"),
    }


def backfill_products(dry_run: bool = False) -> int:
    """Fetch all products and upsert to Supabase."""
    print("\n--- Products ---")
    all_products = []
    data, next_url = shopify_get("products.json", {"limit": 250, "status": "active"})
    all_products.extend(data.get("products", []))
    print(f"  Page 1: {len(data.get('products', []))} products")

    while next_url:
        time.sleep(0.5)  # Rate limiting
        data, next_url = shopify_get_page(next_url)
        all_products.extend(data.get("products", []))
        print(f"  Page {len(all_products) // 250 + 1}: {len(all_products)} total")

    rows = [transform_product(p) for p in all_products]
    print(f"  Total products: {len(rows)}")

    if dry_run:
        print("  DRY RUN — skipping Supabase write")
        return len(rows)

    count = supabase_upsert("products", rows, "shopify_id")
    print(f"  Upserted to Supabase: {count}")
    return count


def backfill_orders(dry_run: bool = False) -> int:
    """Fetch all accessible orders and upsert to Supabase."""
    print("\n--- Orders ---")
    all_orders = []
    data, next_url = shopify_get("orders.json", {"limit": 250, "status": "any"})
    all_orders.extend(data.get("orders", []))
    print(f"  Page 1: {len(data.get('orders', []))} orders")

    while next_url:
        time.sleep(0.5)
        data, next_url = shopify_get_page(next_url)
        all_orders.extend(data.get("orders", []))
        page = len(all_orders) // 250 + 1
        print(f"  Page {page}: {len(all_orders)} total")

    rows = [transform_order(o) for o in all_orders]
    print(f"  Total orders: {len(rows)}")

    if rows:
        dates = [r["created_at"] for r in rows if r.get("created_at")]
        print(f"  Date range: {min(dates)[:10]} → {max(dates)[:10]}")

    if dry_run:
        print("  DRY RUN — skipping Supabase write")
        return len(rows)

    count = supabase_upsert("orders", rows, "shopify_id")
    print(f"  Upserted to Supabase: {count}")
    return count


def main():
    if not all([STORE_URL, ACCESS_TOKEN, SUPABASE_URL, SUPABASE_KEY]):
        print("ERROR: Missing env vars. Need SHOPIFY_STORE_URL, SHOPIFY_ACCESS_TOKEN, SUPABASE_URL, SUPABASE_SERVICE_KEY")
        return 1

    dry_run = "--dry-run" in sys.argv
    products_only = "--products" in sys.argv
    orders_only = "--orders" in sys.argv

    print(f"Shopify → Supabase Backfill")
    print(f"Store: {STORE_URL}")
    print(f"Time:  {datetime.now(timezone.utc).isoformat()}")
    if dry_run:
        print("MODE:  DRY RUN")

    start = time.time()

    if not orders_only:
        backfill_products(dry_run)
    if not products_only:
        backfill_orders(dry_run)

    elapsed = time.time() - start
    print(f"\nDone in {elapsed:.1f}s")

    # Refresh materialized views
    if not dry_run:
        print("\nRefreshing materialized views...")
        for view in [
            "product_margin_detail",
            "inventory_health",
            "channel_profitability_monthly",
            "marketing_roas_trailing",
        ]:
            try:
                body = json.dumps({"query": f"REFRESH MATERIALIZED VIEW CONCURRENTLY {view}"}).encode()
                # Use Supabase RPC or direct SQL
                url = f"{SUPABASE_URL}/rest/v1/rpc/exec_sql"
                # Fallback: just note it needs manual refresh
                print(f"  {view}: needs manual REFRESH (run via Supabase SQL editor)")
            except Exception:
                pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
