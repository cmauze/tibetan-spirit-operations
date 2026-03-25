#!/usr/bin/env python3
"""
Shopify connection validation + sample workflow test.

Verifies we can:
1. Authenticate to the Shopify Admin API
2. Fetch shop metadata
3. List products with inventory data
4. Pull recent orders
5. Demonstrate the kind of data flow our skills will process

Usage:
    python3 scripts/test_shopify_connection.py
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone

# Load .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # fallback to os.environ directly

STORE_URL = os.environ.get("SHOPIFY_STORE_URL", "")
ACCESS_TOKEN = os.environ.get("SHOPIFY_ACCESS_TOKEN", "")
API_VERSION = "2025-01"
BASE_URL = f"https://{STORE_URL}/admin/api/{API_VERSION}"

if not STORE_URL or not ACCESS_TOKEN:
    print("ERROR: SHOPIFY_STORE_URL and SHOPIFY_ACCESS_TOKEN must be set in .env")
    sys.exit(1)


def shopify_get(endpoint: str, params: dict | None = None) -> dict:
    """Make an authenticated GET request to the Shopify Admin API."""
    import urllib.request
    import urllib.parse

    url = f"{BASE_URL}/{endpoint}"
    if params:
        url += "?" + urllib.parse.urlencode(params)

    req = urllib.request.Request(url)
    req.add_header("X-Shopify-Access-Token", ACCESS_TOKEN)
    req.add_header("Content-Type", "application/json")

    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def test_shop_info():
    """Step 1: Verify authentication + fetch shop metadata."""
    print("=" * 60)
    print("STEP 1: Shop Authentication & Metadata")
    print("=" * 60)

    data = shopify_get("shop.json")
    shop = data["shop"]

    print(f"  Store name:     {shop['name']}")
    print(f"  Domain:         {shop['domain']}")
    print(f"  Shopify domain: {shop['myshopify_domain']}")
    print(f"  Currency:       {shop['currency']}")
    print(f"  Country:        {shop['country_name']}")
    print(f"  Plan:           {shop['plan_display_name']}")
    print(f"  Created:        {shop['created_at']}")
    print(f"  Auth:           PASS")
    print()
    return shop


def test_products():
    """Step 2: Fetch products — the data our skills will work with."""
    print("=" * 60)
    print("STEP 2: Product Catalog Sample")
    print("=" * 60)

    data = shopify_get("products.json", {"limit": 10, "status": "active"})
    products = data.get("products", [])

    print(f"  Active products fetched: {len(products)}")
    print()

    for i, p in enumerate(products[:5], 1):
        variants = p.get("variants", [])
        first_variant = variants[0] if variants else {}
        print(f"  [{i}] {p['title']}")
        print(f"      SKU:    {first_variant.get('sku', 'N/A')}")
        print(f"      Price:  ${first_variant.get('price', 'N/A')}")
        print(f"      Stock:  {first_variant.get('inventory_quantity', 'N/A')} units")
        print(f"      Status: {p['status']}")
        print()

    return products


def test_orders():
    """Step 3: Fetch recent orders — what triggers our Operations Agent."""
    print("=" * 60)
    print("STEP 3: Recent Orders")
    print("=" * 60)

    data = shopify_get("orders.json", {"limit": 5, "status": "any"})
    orders = data.get("orders", [])

    print(f"  Recent orders fetched: {len(orders)}")
    print()

    for i, o in enumerate(orders[:5], 1):
        line_items = o.get("line_items", [])
        items_summary = ", ".join(
            f"{li['title']} x{li['quantity']}" for li in line_items[:3]
        )
        shipping = o.get("shipping_address", {})
        destination = f"{shipping.get('city', '?')}, {shipping.get('province', '?')}, {shipping.get('country', '?')}" if shipping else "N/A"

        print(f"  [#{o.get('order_number', '?')}] ${o.get('total_price', '?')} {o.get('currency', 'USD')}")
        print(f"      Items:       {items_summary}")
        print(f"      Fulfillment: {o.get('fulfillment_status', 'unfulfilled')}")
        print(f"      Financial:   {o.get('financial_status', '?')}")
        print(f"      Ship to:     {destination}")
        print(f"      Created:     {o.get('created_at', '?')}")
        print()

    return orders


def test_workflow_simulation(products, orders):
    """Step 4: Simulate what our skills would do with this data."""
    print("=" * 60)
    print("STEP 4: Workflow Simulation")
    print("=" * 60)

    if not orders:
        print("  No orders to simulate with.")
        return

    order = orders[0]
    shipping = order.get("shipping_address", {})
    country = shipping.get("country_code", "US")

    # Simulate fulfillment routing (fulfillment-domestic skill logic)
    if country == "US":
        route = "domestic (Fiona, Asheville)"
    elif country == "MX" or country in ("GT", "HN", "SV", "CR", "PA", "CO", "PE", "CL", "AR", "BR"):
        route = "mexico (Omar, Espíritu Tibetano)"
    else:
        route = "nepal (international)"

    print(f"  Order #{order.get('order_number')}:")
    print(f"    Fulfillment route: {route}")
    print(f"    Total: ${order.get('total_price')} {order.get('currency', 'USD')}")

    # Check if any line items are below reorder threshold
    if products:
        low_stock = [
            p for p in products
            if p.get("variants") and p["variants"][0].get("inventory_quantity", 999) < 5
        ]
        print(f"    Low stock products (< 5 units): {len(low_stock)}")
        for p in low_stock[:3]:
            v = p["variants"][0]
            print(f"      - {p['title']} (SKU: {v.get('sku', 'N/A')}): {v.get('inventory_quantity', '?')} units")

    print()


def test_inventory_locations():
    """Step 5: Fetch inventory locations — needed for multi-location routing."""
    print("=" * 60)
    print("STEP 5: Inventory Locations")
    print("=" * 60)

    data = shopify_get("locations.json")
    locations = data.get("locations", [])

    print(f"  Locations: {len(locations)}")
    for loc in locations:
        print(f"    - {loc['name']} ({loc.get('city', '?')}, {loc.get('country_code', '?')})")
        print(f"      Active: {loc.get('active', False)}")
    print()


def main():
    print()
    print("Tibetan Spirit — Shopify Connection Test")
    print(f"Store: {STORE_URL}")
    print(f"API Version: {API_VERSION}")
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print()

    try:
        shop = test_shop_info()
        products = test_products()
        orders = test_orders()
        test_workflow_simulation(products, orders)
        test_inventory_locations()

        print("=" * 60)
        print("ALL TESTS PASSED")
        print("=" * 60)
        print(f"  Shop: {shop['name']} ({shop['myshopify_domain']})")
        print(f"  Products accessible: YES")
        print(f"  Orders accessible: YES")
        print(f"  Locations accessible: YES")
        print(f"  Fulfillment routing: SIMULATED")
        print()
        return 0

    except Exception as e:
        print(f"\nFAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
