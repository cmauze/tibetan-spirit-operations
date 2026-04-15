# Restock Formulas & Lead-Time Tiers

## Lead-Time Tiers

| Source | Lead Time | Restock Quantity |
|--------|-----------|-----------------|
| Domestic | 2–4 weeks | velocity × 60 days |
| Nepal-sourced | 8–12 weeks | velocity × 90 days |

Use conservative estimate when sourcing tier is uncertain.

## Formulas

- **Reorder point:** velocity × 14 days
- **Critical alert (top-20 SKU):** velocity × 7 days
- **Safety stock:** max(velocity × 6, 2 units)
- **Overstock threshold:** on_hand > velocity × 180 with no active promotion

## Pipeline Adjustments

- Subtract `nepal_pipeline` in-transit units from Nepal restock quantity if populated
- Include `fba_allocated` and `fba_in_transit` in safety stock when present
