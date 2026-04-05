#!/usr/bin/env python3
"""
On-demand Shopify query tool for TS agent workflows.

Provides real-time Shopify lookups when agents need data not yet synced to Supabase.
Read-only. Uses REST Admin API 2025-01 (matching proven test_shopify_connection.py pattern).

Commands:
    order <order_number>          Look up order by number (e.g., 1234)
    product <sku_or_title>        Look up product by SKU or title substring
    inventory [--low <threshold>] Stock levels, optionally filtered to low stock
    recent-orders [--days N]      Recent orders (default: 7 days)
    customer <email>              Customer info for CS enrichment

Usage:
    python3 scripts/shopify_query.py order 1234
    python3 scripts/shopify_query.py product "singing bowl"
    python3 scripts/shopify_query.py inventory --low 5
    python3 scripts/shopify_query.py recent-orders --days 3
    python3 scripts/shopify_query.py customer "buyer@example.com"

Output: JSON to stdout. Errors to stderr.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

STORE_URL = os.environ.get("SHOPIFY_STORE_URL", "")
ACCESS_TOKEN = os.environ.get("SHOPIFY_ACCESS_TOKEN", "")
API_VERSION = "2025-01"
BASE_URL = f"https://{STORE_URL}/admin/api/{API_VERSION}"

if not STORE_URL or not ACCESS_TOKEN:
    print("ERROR: SHOPIFY_STORE_URL and SHOPIFY_ACCESS_TOKEN must be set in .env", file=sys.stderr)
    sys.exit(1)


def shopify_get(endpoint: str, params: dict | None = None) -> dict:
    """Authenticated GET to Shopify Admin API. Returns parsed JSON."""
    url = f"{BASE_URL}/{endpoint}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url)
    req.add_header("X-Shopify-Access-Token", ACCESS_TOKEN)
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def shopify_get_paginated(endpoint: str, params: dict | None = None, key: str = "") -> list:
    """Fetch all pages via Link header cursor pagination."""
    results = []
    url = f"{BASE_URL}/{endpoint}"
    if params:
        url += "?" + urllib.parse.urlencode(params)

    while url:
        req = urllib.request.Request(url)
        req.add_header("X-Shopify-Access-Token", ACCESS_TOKEN)
        req.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            results.extend(data.get(key, []))
            # Parse Link header for next page
            link = resp.headers.get("Link", "")
            url = None
            if 'rel="next"' in link:
                for part in link.split(","):
                    if 'rel="next"' in part:
                        url = part.split("<")[1].split(">")[0]
    return results


def cmd_order(args: list[str]) -> dict:
    """Look up order by order number."""
    if not args:
        return {"error": "Usage: order <order_number>"}
    order_number = args[0]
    data = shopify_get("orders.json", {"name": order_number, "status": "any"})
    orders = data.get("orders", [])
    if not orders:
        data = shopify_get("orders.json", {"name": f"#{order_number}", "status": "any"})
        orders = data.get("orders", [])
    if not orders:
        return {"error": f"Order {order_number} not found"}
    o = orders[0]
    shipping = o.get("shipping_address") or {}
    return {
        "order_number": o.get("order_number"),
        "created_at": o.get("created_at"),
        "financial_status": o.get("financial_status"),
        "fulfillment_status": o.get("fulfillment_status") or "unfulfilled",
        "total_price": o.get("total_price"),
        "currency": o.get("currency"),
        "customer_email": o.get("email"),
        "shipping": {
            "name": shipping.get("name"),
            "city": shipping.get("city"),
            "province": shipping.get("province"),
            "country": shipping.get("country"),
            "country_code": shipping.get("country_code"),
        },
        "line_items": [
            {
                "title": li.get("title"),
                "sku": li.get("sku"),
                "quantity": li.get("quantity"),
                "price": li.get("price"),
            }
            for li in o.get("line_items", [])
        ],
        "fulfillments": [
            {
                "status": f.get("status"),
                "tracking_number": f.get("tracking_number"),
                "tracking_url": f.get("tracking_url"),
                "created_at": f.get("created_at"),
            }
            for f in o.get("fulfillments", [])
        ],
        "note": o.get("note"),
        "tags": o.get("tags"),
    }


def cmd_product(args: list[str]) -> dict:
    """Look up product by SKU or title substring."""
    if not args:
        return {"error": "Usage: product <sku_or_title>"}
    query = " ".join(args).lower()
    products = shopify_get_paginated("products.json", {"limit": 250, "status": "active"}, key="products")
    matches = []
    for p in products:
        title_match = query in p.get("title", "").lower()
        sku_match = any(query == (v.get("sku") or "").lower() for v in p.get("variants", []))
        if title_match or sku_match:
            v = p["variants"][0] if p.get("variants") else {}
            matches.append({
                "title": p.get("title"),
                "handle": p.get("handle"),
                "sku": v.get("sku"),
                "price": v.get("price"),
                "inventory_quantity": v.get("inventory_quantity"),
                "status": p.get("status"),
                "product_type": p.get("product_type"),
                "vendor": p.get("vendor"),
                "shopify_id": p.get("id"),
            })
    if not matches:
        return {"error": f"No products matching '{query}'", "total_searched": len(products)}
    return {"matches": matches, "count": len(matches)}


def cmd_inventory(args: list[str]) -> dict:
    """Stock levels. Use --low <N> to filter to items below threshold."""
    threshold = None
    if "--low" in args:
        idx = args.index("--low")
        threshold = int(args[idx + 1]) if idx + 1 < len(args) else 5

    products = shopify_get_paginated("products.json", {"limit": 250, "status": "active"}, key="products")
    items = []
    for p in products:
        for v in p.get("variants", []):
            qty = v.get("inventory_quantity", 0)
            if threshold is not None and qty >= threshold:
                continue
            items.append({
                "title": p.get("title"),
                "sku": v.get("sku"),
                "inventory_quantity": qty,
                "price": v.get("price"),
            })

    items.sort(key=lambda x: x["inventory_quantity"])
    summary = {
        "total_products": len(products),
        "items": items if threshold else items[:50],
    }
    if threshold:
        summary["threshold"] = threshold
        summary["below_threshold"] = len(items)
    return summary


def cmd_recent_orders(args: list[str]) -> dict:
    """Recent orders. Use --days N to specify window (default 7)."""
    days = 7
    if "--days" in args:
        idx = args.index("--days")
        days = int(args[idx + 1]) if idx + 1 < len(args) else 7

    since = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%S-00:00")
    data = shopify_get("orders.json", {"created_at_min": since, "status": "any", "limit": 250})
    orders = data.get("orders", [])

    result = []
    for o in orders:
        shipping = o.get("shipping_address") or {}
        result.append({
            "order_number": o.get("order_number"),
            "created_at": o.get("created_at"),
            "total_price": o.get("total_price"),
            "currency": o.get("currency"),
            "financial_status": o.get("financial_status"),
            "fulfillment_status": o.get("fulfillment_status") or "unfulfilled",
            "item_count": sum(li.get("quantity", 0) for li in o.get("line_items", [])),
            "country": shipping.get("country_code"),
        })

    return {
        "days": days,
        "order_count": len(result),
        "total_revenue": sum(float(o["total_price"]) for o in result),
        "orders": result,
    }


def cmd_customer(args: list[str]) -> dict:
    """Customer lookup by email for CS enrichment."""
    if not args:
        return {"error": "Usage: customer <email>"}
    email = args[0]
    data = shopify_get("customers/search.json", {"query": f"email:{email}"})
    customers = data.get("customers", [])
    if not customers:
        return {"error": f"No customer found for {email}"}
    c = customers[0]
    return {
        "email": c.get("email"),
        "first_name": c.get("first_name"),
        "last_name": c.get("last_name"),
        "orders_count": c.get("orders_count"),
        "total_spent": c.get("total_spent"),
        "created_at": c.get("created_at"),
        "tags": c.get("tags"),
        "note": c.get("note"),
        "default_address": {
            "city": (c.get("default_address") or {}).get("city"),
            "province": (c.get("default_address") or {}).get("province"),
            "country": (c.get("default_address") or {}).get("country"),
        },
    }


COMMANDS = {
    "order": cmd_order,
    "product": cmd_product,
    "inventory": cmd_inventory,
    "recent-orders": cmd_recent_orders,
    "customer": cmd_customer,
}


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__, file=sys.stderr)
        print(f"Commands: {', '.join(COMMANDS.keys())}", file=sys.stderr)
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd not in COMMANDS:
        print(f"Unknown command: {cmd}. Available: {', '.join(COMMANDS.keys())}", file=sys.stderr)
        sys.exit(1)

    result = COMMANDS[cmd](sys.argv[2:])
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
