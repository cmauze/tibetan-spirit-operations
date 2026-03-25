#!/usr/bin/env python3
"""
Import historical Shopify orders from CSV export.

Bypasses the 60-day API limitation by importing the CSV that Shopify
generates from Admin → Orders → Export.

Usage:
    python3 scripts/import_orders_csv.py orders_export.csv
    python3 scripts/import_orders_csv.py orders_export.csv --dry-run

How to export from Shopify:
    1. Go to: admin.shopify.com/store/tibetanspirits/orders
    2. Click "Export" (top right)
    3. Select "All orders" and "Plain CSV"
    4. Download the file
    5. Run this script with the downloaded file

The CSV contains one row per line item. This script groups by order
and upserts into the Supabase orders table.
"""

from __future__ import annotations

import csv
import json
import os
import sys
import time
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")

LATAM_COUNTRIES = {"MX", "GT", "HN", "SV", "CR", "PA", "CO", "PE", "CL", "AR", "BR", "EC", "VE", "UY", "PY", "BO"}


def supabase_upsert(table: str, rows: list[dict]) -> int:
    """Upsert rows to Supabase in batches of 100."""
    if not rows:
        return 0
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates",
    }
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
        if total % 500 == 0:
            print(f"    ... {total} rows upserted")
    return total


def parse_csv(filepath: str) -> list[dict]:
    """
    Parse Shopify orders CSV. Groups line items by order name.

    Shopify CSV columns (relevant ones):
      Name, Email, Financial Status, Paid at, Fulfillment Status,
      Currency, Subtotal, Shipping, Total, Discount Amount,
      Lineitem quantity, Lineitem name, Lineitem price, Lineitem sku,
      Shipping Name, Shipping Street, Shipping City, Shipping Province,
      Shipping Country, Shipping Zip, Created at, Id
    """
    orders_by_name = defaultdict(lambda: {"line_items": [], "rows": []})

    with open(filepath, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get("Name", "").strip()
            if not name:
                continue
            orders_by_name[name]["rows"].append(row)
            if row.get("Lineitem name"):
                orders_by_name[name]["line_items"].append({
                    "sku": row.get("Lineitem sku", ""),
                    "title": row.get("Lineitem name", ""),
                    "quantity": int(row.get("Lineitem quantity", 1) or 1),
                    "price": row.get("Lineitem price", "0"),
                })

    results = []
    for name, data in orders_by_name.items():
        first_row = data["rows"][0]

        # Parse order number from name (e.g., "#1001" → 1001)
        order_num = name.lstrip("#")

        # Determine channel
        channel = "shopify"  # CSV export is Shopify orders

        # Determine fulfillment route
        country = first_row.get("Shipping Country", "US")
        if country == "US":
            route = "domestic"
        elif country in LATAM_COUNTRIES:
            route = "mexico"
        else:
            route = "nepal"

        # Shipping address
        shipping = {}
        for field in ["Name", "Street", "City", "Province", "Country", "Zip", "Province Code", "Country Code"]:
            key = f"Shipping {field}"
            if first_row.get(key):
                shipping[field.lower().replace(" ", "_")] = first_row[key]

        # Parse created_at
        created_at = first_row.get("Created at", "")

        # Shopify ID (numeric, from the Id column)
        shopify_id = first_row.get("Id", "")
        try:
            shopify_id = int(shopify_id) if shopify_id else None
        except (ValueError, TypeError):
            shopify_id = None

        total_price = first_row.get("Total", "0")
        try:
            total_price = float(total_price) if total_price else 0
        except (ValueError, TypeError):
            total_price = 0

        order = {
            "order_number": order_num,
            "email": first_row.get("Email", ""),
            "channel": channel,
            "total_price": total_price,
            "currency": first_row.get("Currency", "USD"),
            "fulfillment_status": first_row.get("Fulfillment Status") or None,
            "fulfillment_route": route,
            "line_items": data["line_items"],
            "shipping_address": shipping if shipping else None,
            "created_at": created_at if created_at else None,
        }

        # Only include shopify_id if we have it (for upsert key)
        if shopify_id:
            order["shopify_id"] = shopify_id

        results.append(order)

    return results


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/import_orders_csv.py <orders_export.csv> [--dry-run]")
        print()
        print("Export from Shopify:")
        print("  1. admin.shopify.com/store/tibetanspirits/orders")
        print("  2. Click 'Export' → 'All orders' → 'Plain CSV'")
        print("  3. Run this script with the downloaded file")
        return 1

    filepath = sys.argv[1]
    dry_run = "--dry-run" in sys.argv

    if not os.path.exists(filepath):
        print(f"ERROR: File not found: {filepath}")
        return 1

    if not dry_run and not all([SUPABASE_URL, SUPABASE_KEY]):
        print("ERROR: SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")
        return 1

    print(f"Shopify CSV → Supabase Import")
    print(f"File: {filepath}")
    print(f"Time: {datetime.now(timezone.utc).isoformat()}")
    if dry_run:
        print("MODE: DRY RUN")
    print()

    start = time.time()

    print("Parsing CSV...")
    orders = parse_csv(filepath)
    print(f"  Unique orders: {len(orders)}")

    if orders:
        dates = [o["created_at"] for o in orders if o.get("created_at")]
        if dates:
            print(f"  Date range: {min(dates)[:10]} → {max(dates)[:10]}")

        totals = sum(o["total_price"] for o in orders)
        print(f"  Total revenue: ${totals:,.2f}")

        # Show year breakdown
        by_year = defaultdict(lambda: {"count": 0, "revenue": 0})
        for o in orders:
            if o.get("created_at"):
                year = o["created_at"][:4]
                by_year[year]["count"] += 1
                by_year[year]["revenue"] += o["total_price"]

        print(f"\n  Year breakdown:")
        for year in sorted(by_year.keys()):
            d = by_year[year]
            print(f"    {year}: {d['count']:>6,} orders  ${d['revenue']:>12,.2f}")

    if dry_run:
        print("\n  DRY RUN — skipping Supabase write")
    else:
        print(f"\n  Upserting to Supabase...")
        # Orders without shopify_id can't use the unique constraint
        # Split into: with ID (upsert) and without ID (insert)
        with_id = [o for o in orders if o.get("shopify_id")]
        without_id = [o for o in orders if not o.get("shopify_id")]

        if with_id:
            count = supabase_upsert("orders", with_id)
            print(f"    Upserted (with Shopify ID): {count}")
        if without_id:
            # For orders without Shopify ID, insert with order_number dedup
            count = supabase_upsert("orders", without_id)
            print(f"    Inserted (without Shopify ID): {count}")

    elapsed = time.time() - start
    print(f"\nDone in {elapsed:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
