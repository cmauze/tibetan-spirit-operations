#!/usr/bin/env python3
"""
Seed estimated COGS data for all products based on category-level estimates.

Applies COGS percentages from the financial model, sets freight tiers by price,
and marks all products as cogs_confidence = 'estimated'. These estimates serve
as a baseline until confirmed COGS from supplier invoices replace them.

Usage:
    python3 scripts/seed_cogs_from_model.py
    python3 scripts/seed_cogs_from_model.py --dry-run
"""

from __future__ import annotations

import os
import re
import sys
from collections import defaultdict

# Add lib/ to path for ts_shared imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from ts_shared.supabase_client import get_client


# Category COGS rates (% of retail price)
CATEGORY_COGS_RATES = {
    "incense": 0.24,
    "singing_bowls": 0.30,
    "malas": 0.20,
    "prayer_beads": 0.20,
    "statues": 0.35,
    "ritual_objects": 0.35,
    "thangkas": 0.40,
    "prayer_flags": 0.15,
    "books": 0.10,
    "texts": 0.10,
    "altar_supplies": 0.25,
}
DEFAULT_COGS_RATE = 0.25

# Category classification patterns (applied to title and handle)
CATEGORY_PATTERNS: list[tuple[str, str]] = [
    (r"incense|dhoop|nado|rope\s*incense|cone\s*incense", "incense"),
    (r"singing\s*bowl|sound\s*bowl|tibetan\s*bowl", "singing_bowls"),
    (r"mala\b|prayer\s*bead|japa|wrist\s*mala|guru\s*bead", "malas"),
    (r"statue|buddha\s*figure|tara\s*figure|figurine|bronze\s*figure", "statues"),
    (r"ritual|vajra|dorje|bell|ghanta|phurba|kapala|damaru|bumpa", "ritual_objects"),
    (r"thangka|thanka|tangka|scroll\s*painting", "thangkas"),
    (r"prayer\s*flag|lungta|wind\s*horse|flag\s*strand", "prayer_flags"),
    (r"book|text|sutra|dharma\s*pub|snow\s*lion|shambhala\s*pub", "books"),
    (r"altar|offering\s*bowl|butter\s*lamp|incense\s*holder|burner|censer|puja\s*set", "altar_supplies"),
]

DUTY_RATE = 0.05


def classify_product(title: str, handle: str) -> str:
    """Classify a product into a category based on title/handle patterns."""
    text = f"{title} {handle}".lower()
    for pattern, category in CATEGORY_PATTERNS:
        if re.search(pattern, text):
            return category
    return "other"


def get_freight_per_unit(price: float) -> float:
    """Determine freight per unit based on price tier."""
    if price < 20:
        return 2.50
    elif price < 50:
        return 4.00
    elif price < 100:
        return 6.00
    else:
        return 8.00


def main():
    dry_run = "--dry-run" in sys.argv

    if dry_run:
        print("=== DRY RUN — no database changes will be made ===\n")

    client = get_client()

    # Fetch all products
    print("Fetching products from Supabase...")
    result = client.table("products").select("id, title, handle, price, cogs_confirmed, cogs_estimated, cogs_confidence").execute()
    products = result.data

    if not products:
        print("ERROR: No products found in database.")
        sys.exit(1)

    print(f"Found {len(products)} products\n")

    # Classify and calculate COGS
    category_counts: dict[str, int] = defaultdict(int)
    category_revenue: dict[str, float] = defaultdict(float)
    category_cogs: dict[str, float] = defaultdict(float)
    updates: list[dict] = []
    skipped_confirmed = 0
    skipped_no_price = 0

    for product in products:
        price = float(product.get("price") or 0)

        # Skip products with no price
        if price <= 0:
            skipped_no_price += 1
            continue

        # Skip products that already have confirmed COGS
        if product.get("cogs_confidence") == "confirmed" and product.get("cogs_confirmed"):
            skipped_confirmed += 1
            continue

        title = product.get("title", "")
        handle = product.get("handle", "")
        category = classify_product(title, handle)

        cogs_rate = CATEGORY_COGS_RATES.get(category, DEFAULT_COGS_RATE)
        cogs_estimated = round(price * cogs_rate, 2)
        freight = get_freight_per_unit(price)

        category_counts[category] += 1
        category_revenue[category] += price
        category_cogs[category] += cogs_estimated + freight + (cogs_estimated * DUTY_RATE)

        updates.append({
            "id": product["id"],
            "cogs_estimated": cogs_estimated,
            "freight_per_unit": freight,
            "duty_rate": DUTY_RATE,
            "cogs_confidence": "estimated",
        })

    # Print summary
    print(f"{'Category':<20} {'Count':>6} {'Avg Price':>10} {'COGS Rate':>10} {'Avg COGS':>10} {'Avg Landed':>11}")
    print("-" * 77)

    total_revenue = 0.0
    total_landed = 0.0

    for category in sorted(category_counts.keys()):
        count = category_counts[category]
        rev = category_revenue[category]
        cogs = category_cogs[category]
        avg_price = rev / count if count else 0
        rate = CATEGORY_COGS_RATES.get(category, DEFAULT_COGS_RATE)
        avg_cogs = (rev * rate) / count if count else 0
        avg_landed = cogs / count if count else 0

        total_revenue += rev
        total_landed += cogs

        print(f"{category:<20} {count:>6} {avg_price:>10.2f} {rate:>9.0%} {avg_cogs:>10.2f} {avg_landed:>11.2f}")

    print("-" * 77)
    blended_margin = (total_revenue - total_landed) / total_revenue * 100 if total_revenue else 0
    print(f"{'TOTAL':<20} {sum(category_counts.values()):>6} {total_revenue:>10.2f} {'':>10} {total_landed:>10.2f} {blended_margin:>10.1f}%")
    print(f"\nSkipped: {skipped_confirmed} confirmed, {skipped_no_price} no price")
    print(f"Updates to apply: {len(updates)}")

    if dry_run:
        print("\n=== DRY RUN complete — no changes made ===")
        return

    if not updates:
        print("\nNo updates needed.")
        return

    # Apply updates in batches
    print(f"\nApplying {len(updates)} updates...")
    batch_size = 50
    updated = 0

    for i in range(0, len(updates), batch_size):
        batch = updates[i : i + batch_size]
        for record in batch:
            product_id = record.pop("id")
            client.table("products").update(record).eq("id", product_id).execute()
            updated += 1

        print(f"  Updated {updated}/{len(updates)} products...")

    print(f"\nAll {updated} products updated with estimated COGS.")

    # Refresh materialized views
    print("\nRefreshing materialized views...")
    try:
        client.rpc("refresh_materialized_views", {}).execute()
        print("  Materialized views refreshed via RPC.")
    except Exception:
        # RPC may not exist yet — try direct SQL via postgrest
        for view in ["channel_profitability_monthly", "product_margin_detail"]:
            try:
                client.postgrest.rpc(
                    "exec_sql",
                    {"query": f"REFRESH MATERIALIZED VIEW CONCURRENTLY {view}"},
                ).execute()
                print(f"  Refreshed {view}")
            except Exception as e:
                print(f"  WARN: Could not refresh {view}: {e}")
                print(f"  Run manually: REFRESH MATERIALIZED VIEW CONCURRENTLY {view};")

    print("\nDone.")


if __name__ == "__main__":
    main()
