#!/usr/bin/env python3
"""
Update product COGS from confirmed supplier pricing spreadsheet.

Source: "Catalog: TS Product prices / Dinesh" Google Sheet
Data: NPR purchase prices from Nepal supplier, converted to USD at ~135 NPR/USD
Shipping: $1.70 flat per unit

Updates products.cogs_confirmed, products.freight_per_unit, and
products.cogs_confidence = 'confirmed' for matched SKUs.

Usage:
    python3 scripts/update_cogs_from_spreadsheet.py --dry-run
    python3 scripts/update_cogs_from_spreadsheet.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from ts_shared.supabase_client import get_client

# Confirmed supplier COGS from spreadsheet (NPR prices converted to USD at ~135 NPR/USD)
# Format: (SKU, product_name, cogs_usd, freight_per_unit)
CONFIRMED_COGS = [
    # STICK INCENSE
    ("IS015", "Nado Poizokhang Orange (Highest Grade)", 3.26, 1.70),
    ("IS011", "Nado Poizokhang Riwo Sangcho", 2.04, 1.70),
    ("IS225", "Nado Poizokhang Sur & Sang", 2.04, 1.70),
    ("IS018", "Nado Poizokhang Yellow", 3.04, 1.70),
    ("IS001", "Bhutanese Drichog Chotrin", 2.85, 1.70),
    ("IS002", "Bhutanese Drizang Kuenchap", 1.48, 1.70),
    ("IX200", "Namdroling Incense", 4.48, 1.70),
    ("IS232", "Nepal Hyolmo Incense", 0.52, 1.70),
    ("IS003", "Druk: Avalokitesvara", 0.67, 1.70),
    ("IS012", "Druk: Amitaba", 0.67, 1.70),
    ("IS005", "Druk: Manjushree", 0.67, 1.70),
    ("IS014", "Druk Shakyamuni", 0.67, 1.70),
    ("IS013", "Druk: Green Tara", 0.67, 1.70),
    # POWDERED INCENSE
    ("IP105", "Shechen Sur Powder", 2.04, 1.70),
    ("I03A3", "Zhingkham Kuenchap Choetrin Sang Powder", 2.04, 1.70),
    ("I82C", "Deity: Green Tara bhutanese sang", 0.67, 1.70),
    ("I82J", "Deity: White Tara bhutanese sang", 0.67, 1.70),
    ("I82E", "Deity: kurukullle bhutanese sang", 0.67, 1.70),
    ("I82D", "Deity: Guru Rinpoche bhutanese sang", 0.67, 1.70),
    ("I82L", "Deity: shakyamuni bhutanese sang", 0.67, 1.70),
    ("I82k", "Deity: amitabha bhutanese sang", 0.67, 1.70),
    ("I82M", "Deity: long life bhutanese sang", 0.67, 1.70),
    ("I82N", "Deity: rewo sangcho bhutanese sang", 0.67, 1.70),
    ("I82o", "Deity: kur sur bhutanese sang", 0.67, 1.70),
    # ACCESSORIES
    ("i40b", "Wood Burner Painted", 7.78, 1.70),
    ("i44a", "Metal Censer Small", 9.63, 1.70),
    ("i44b", "Metal Censer Medium", 11.11, 1.70),
    ("i44c", "Metal Censer Large", 13.33, 1.70),
]

DUTY_RATE = 0.05


def main():
    dry_run = "--dry-run" in sys.argv

    if dry_run:
        print("=== DRY RUN — no database changes ===\n")

    client = get_client()

    # Build SKU lookup (case-insensitive)
    cogs_by_sku = {}
    for sku, name, cogs_usd, freight in CONFIRMED_COGS:
        cogs_by_sku[sku.upper()] = {
            "name": name,
            "cogs_confirmed": round(cogs_usd, 2),
            "freight_per_unit": freight,
        }

    # Fetch all products
    print("Fetching products from Supabase...")
    result = client.table("products").select(
        "id, sku, title, price, cogs_confirmed, cogs_estimated, cogs_confidence"
    ).execute()
    products = result.data
    print(f"Found {len(products)} products\n")

    # Match and prepare updates
    matched = []
    unmatched_skus = list(cogs_by_sku.keys())

    for product in products:
        sku = (product.get("sku") or "").upper()
        if sku in cogs_by_sku:
            cogs_data = cogs_by_sku[sku]
            price = float(product.get("price") or 0)
            cogs = cogs_data["cogs_confirmed"]
            freight = cogs_data["freight_per_unit"]
            landed = cogs + freight + (cogs * DUTY_RATE)
            margin = ((price - landed) / price * 100) if price > 0 else 0

            matched.append({
                "id": product["id"],
                "sku": product.get("sku"),
                "title": product.get("title"),
                "price": price,
                "cogs": cogs,
                "freight": freight,
                "landed": landed,
                "margin_pct": margin,
                "old_confidence": product.get("cogs_confidence"),
            })
            unmatched_skus.remove(sku)

    # Print match report
    print(f"{'SKU':<10} {'Title':<45} {'Price':>7} {'COGS':>7} {'Freight':>8} {'Landed':>8} {'Margin':>7}")
    print("-" * 102)

    for m in matched:
        title = (m["title"] or "")[:44]
        print(
            f"{m['sku']:<10} {title:<45} "
            f"${m['price']:>6.2f} ${m['cogs']:>5.2f} "
            f"${m['freight']:>6.2f} ${m['landed']:>6.2f} {m['margin_pct']:>6.1f}%"
        )

    print(f"\nMatched: {len(matched)} / {len(CONFIRMED_COGS)} SKUs")

    if unmatched_skus:
        print(f"\nUnmatched SKUs (not found in database):")
        for sku in unmatched_skus:
            name = cogs_by_sku[sku]["name"]
            print(f"  {sku} — {name}")

    if dry_run:
        print("\n=== DRY RUN complete — no changes made ===")
        return

    if not matched:
        print("\nNo matches to update.")
        return

    # Apply updates
    print(f"\nUpdating {len(matched)} products...")
    updated = 0
    for m in matched:
        client.table("products").update({
            "cogs_confirmed": m["cogs"],
            "freight_per_unit": m["freight"],
            "duty_rate": DUTY_RATE,
            "cogs_confidence": "confirmed",
        }).eq("id", m["id"]).execute()
        updated += 1

    print(f"Updated {updated} products with confirmed COGS.")

    # Refresh materialized views
    print("\nRefreshing materialized views...")
    for view in ["product_margin_detail", "channel_profitability_monthly"]:
        try:
            client.rpc("exec_sql", {
                "query": f"REFRESH MATERIALIZED VIEW CONCURRENTLY {view}"
            }).execute()
            print(f"  Refreshed {view}")
        except Exception as e:
            print(f"  WARN: Could not refresh {view}: {e}")
            print(f"  Run manually: REFRESH MATERIALIZED VIEW CONCURRENTLY {view};")

    print("\nDone.")


if __name__ == "__main__":
    main()
