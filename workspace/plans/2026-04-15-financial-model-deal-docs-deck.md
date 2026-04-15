# TS Financial Model + Deal Docs + Vision Deck — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce three deliverables from the v6 Excel financial model: (1) validated data extract as reusable JSON, (2) investment proposal document for Dr. Hun Lye and investors, (3) vision pitch deck for Chris's investors that also establishes brand voice/mission as a foundational artifact.

**Architecture:** The v6 Excel (`TS-Financial-Model-v6-Moderate-Upside.xlsx`) is the single source of truth for all financial data. A Python extraction script reads it into a JSON summary. The deal docs and deck reference that JSON. All deliverables go to `deliverables/outputs/`. The existing Python scenario model (line-extension scenarios) is archived — its math functions are kept for future reuse but are not used in this workstream.

**Tech Stack:** Python 3 (openpyxl for xlsx reading), Marp (deck generation via `marp-deck` skill), Markdown (deal docs), Supabase MCP (baseline validation)

**Key Constraints:**
- NEVER fabricate financial data — all numbers from v6 Excel or Supabase
- NEVER use prohibited marketing language (see `rules/marketing-discipline.md`)
- NEVER use VC/PE jargon in deal docs — audience is unsophisticated financially
- NEVER promise specific returns — show ranges and scenarios
- Brand rules from `rules/brand-voice.md` and `rules/cultural-sensitivity.md` apply to all customer/external-facing content
- Deal docs are a conversation starter, NOT a legal document
- Vision deck is the foundational brand/mission artifact — subsequent docs (Operational Handbook, learning paths) will reference it

**Source Files:**
- v6 Excel: `/Users/chrismauze/Documents/Claude/Projects/💼 TS / Norbu/TS-Financial-Model-v6-Moderate-Upside.xlsx`
- LOI v4: `/Users/chrismauze/Documents/Claude/Projects/💼 TS / Norbu/Tibetan-Spirit-LOI-v4.docx`
- Term Sheet v3: `/Users/chrismauze/Documents/Claude/Projects/💼 TS / Norbu/Tibetan-Spirit-Term-Sheet-v3.docx`
- Model Handoff: `/Users/chrismauze/Documents/Claude/Projects/💼 TS / Norbu/TS-Model-Upside-Handoff.md`
- Google Sheet (editable v6): `https://docs.google.com/spreadsheets/u/0/d/1582dIHeTsLdcIHoaQfPsc5Hu6aHbsiZ8/edit`
- Reference decks: see Task 7 for paths

**Audience Map:**
| Deliverable | Primary Audience | Tone | Financial Sophistication |
|---|---|---|---|
| Deal Proposal | Dr. Hun Lye (business owner) + Chris's investors | Warm, respectful, plain English | Low (Dr. Hun Lye) / Medium (investors) |
| Vision Deck | Chris's investors (already bought in) | Data-forward, zero BS, no hype | Medium — they understand business but not PE jargon |

---

## Phase 1: Data Foundation (tasks can run in parallel)

### Task 1: Extract v6 Excel to Reusable JSON

**Purpose:** Create a single JSON file that every downstream document references. This avoids re-reading the xlsx and ensures all deliverables use identical numbers.

**Files:**
- Create: `scripts/financial_model/extract_v6.py`
- Create: `data/financial-model/v6-extract-2026-04-15.json`

- [ ] **Step 1: Create the extraction script**

```python
#!/usr/bin/env python3
"""Extract v6 Excel financial model into a reusable JSON summary.

Reads TS-Financial-Model-v6-Moderate-Upside.xlsx and outputs a structured
JSON file that deal docs and deck generation scripts can reference.
"""
import json
import sys
from datetime import date
from pathlib import Path

import openpyxl


V6_PATH = Path("/Users/chrismauze/Documents/Claude/Projects/💼 TS / Norbu/TS-Financial-Model-v6-Moderate-Upside.xlsx")
OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "financial-model"


def extract_assumptions(wb):
    """Extract key assumptions from the Assumptions tab."""
    ws = wb["Assumptions"]
    assumptions = {}
    for row in ws.iter_rows(min_row=1, max_row=ws.max_row, values_only=False):
        cells = {c.coordinate: c.value for c in row if c.value is not None}
        if cells:
            # Build key-value pairs from A/B columns
            a_val = None
            b_val = None
            c_val = None
            for coord, val in cells.items():
                col = coord[0]
                if col == "A":
                    a_val = val
                elif col == "B":
                    b_val = val
                elif col == "C":
                    c_val = val
            if a_val and b_val is not None:
                assumptions[str(a_val).strip()] = {
                    "value": b_val,
                    "note": c_val,
                }
    return assumptions


def extract_monthly_pnl(wb):
    """Extract the full Monthly P&L into a structured dict."""
    ws = wb["Monthly P&L"]
    # Row 4 has headers (month labels)
    headers = []
    for cell in ws[4]:
        if cell.value:
            headers.append((cell.column, str(cell.value)))

    # Map column index to month label
    col_to_month = {col: label for col, label in headers}

    pnl = {}
    for row in ws.iter_rows(min_row=6, max_row=ws.max_row, values_only=False):
        label_cell = row[0]  # Column A
        if label_cell.value is None:
            continue
        label = str(label_cell.value).strip()
        row_data = {}
        for cell in row[1:]:  # Skip column A
            if cell.column in col_to_month and cell.value is not None:
                row_data[col_to_month[cell.column]] = cell.value
        if row_data:
            pnl[label] = row_data
    return pnl


def extract_cogs(wb):
    """Extract Product COGS by channel."""
    ws = wb["Product COGS"]
    channels = []
    for row in ws.iter_rows(min_row=4, max_row=ws.max_row, values_only=False):
        vals = [c.value for c in row]
        if vals[0] and vals[1] is not None:
            channels.append({
                "channel": vals[0],
                "cogs_pct": vals[1],
                "gross_margin": vals[2],
                "notes": vals[3],
            })
    return channels


def extract_sensitivity(wb):
    """Extract sensitivity analysis."""
    ws = wb["Sensitivity"]
    scenarios = []
    for row in ws.iter_rows(min_row=4, max_row=ws.max_row, values_only=False):
        vals = [c.value for c in row]
        if vals[0]:
            scenarios.append({
                "scenario": vals[0],
                "revenue_factor": vals[1],
                "y1_ebitda": vals[2],
                "y2_ebitda": vals[3],
                "y3_ebitda": vals[4],
                "m36_cash": vals[5] if len(vals) > 5 else None,
            })
    return scenarios


def extract_capital_summary(wb):
    """Extract capital deployment summary."""
    ws = wb["Capital Summary"]
    items = {}
    for row in ws.iter_rows(min_row=1, max_row=ws.max_row, values_only=False):
        vals = [c.value for c in row]
        if vals[0] and vals[1] is not None:
            items[str(vals[0]).strip()] = vals[1]
    return items


def build_summary(pnl):
    """Compute high-level summary metrics from the P&L."""
    revenue = pnl.get("TOTAL REVENUE", {})
    ebitda = pnl.get("EBITDA", {})
    cash = pnl.get("ENDING CASH BALANCE", {})

    return {
        "revenue": {
            "y1": revenue.get("Y1 Total"),
            "y2": revenue.get("Y2 Total"),
            "y3": revenue.get("Y3 Total"),
        },
        "ebitda": {
            "y1": ebitda.get("Y1 Total"),
            "y2": ebitda.get("Y2 Total"),
            "y3": ebitda.get("Y3 Total"),
        },
        "ending_cash_m36": cash.get("May 29"),
        "product_revenue": {
            "y1": pnl.get("Product Revenue", {}).get("Y1 Total"),
            "y2": pnl.get("Product Revenue", {}).get("Y2 Total"),
            "y3": pnl.get("Product Revenue", {}).get("Y3 Total"),
        },
        "travel_revenue": {
            "y1": pnl.get("Travel Revenue", {}).get("Y1 Total"),
            "y2": pnl.get("Travel Revenue", {}).get("Y2 Total"),
            "y3": pnl.get("Travel Revenue", {}).get("Y3 Total"),
        },
        "gross_profit": {
            "y1": pnl.get("GROSS PROFIT", {}).get("Y1 Total"),
            "y2": pnl.get("GROSS PROFIT", {}).get("Y2 Total"),
            "y3": pnl.get("GROSS PROFIT", {}).get("Y3 Total"),
        },
        "total_marketing": {
            "y1": pnl.get("Marketing & Advertising", {}).get("Y1 Total"),
            "y2": pnl.get("Marketing & Advertising", {}).get("Y2 Total"),
            "y3": pnl.get("Marketing & Advertising", {}).get("Y3 Total"),
        },
    }


def extract_channel_revenue(pnl):
    """Extract per-channel revenue for Y1/Y2/Y3."""
    channels = [
        "Shopify D2C", "Amazon", "Etsy", "Wholesale",
        "Quarterly Subscription (net)", "High-Value Dropship", "TS Travels (per-trip)"
    ]
    result = {}
    for ch in channels:
        key = f"  {ch}"
        data = pnl.get(key, {})
        result[ch] = {
            "y1": data.get("Y1 Total"),
            "y2": data.get("Y2 Total"),
            "y3": data.get("Y3 Total"),
        }
    return result


def main():
    if not V6_PATH.exists():
        print(f"ERROR: v6 Excel not found at {V6_PATH}", file=sys.stderr)
        sys.exit(1)

    wb = openpyxl.load_workbook(V6_PATH, data_only=True)

    pnl = extract_monthly_pnl(wb)
    output = {
        "extracted_date": date.today().isoformat(),
        "source_file": V6_PATH.name,
        "model_version": "v6 Moderate Upside",
        "model_period": "Jun 2026 – May 2029 (36 months)",
        "summary": build_summary(pnl),
        "channel_revenue": extract_channel_revenue(pnl),
        "assumptions": extract_assumptions(wb),
        "cogs_by_channel": extract_cogs(wb),
        "sensitivity": extract_sensitivity(wb),
        "capital_summary": extract_capital_summary(wb),
        "monthly_pnl": pnl,
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / f"v6-extract-{date.today().isoformat()}.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2, default=str)

    print(f"Extracted v6 model to {out_path}")
    print(f"  Revenue: Y1=${output['summary']['revenue']['y1']:,.0f}  Y2=${output['summary']['revenue']['y2']:,.0f}  Y3=${output['summary']['revenue']['y3']:,.0f}")
    print(f"  EBITDA:  Y1=${output['summary']['ebitda']['y1']:,.0f}  Y2=${output['summary']['ebitda']['y2']:,.0f}  Y3=${output['summary']['ebitda']['y3']:,.0f}")

    return out_path


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run the extraction script**

```bash
cd /Users/chrismauze/code/active/tibetan-spirit-ops
python3 scripts/financial_model/extract_v6.py
```

Expected output:
```
Extracted v6 model to data/financial-model/v6-extract-2026-04-15.json
  Revenue: Y1=$173,294  Y2=$772,794  Y3=$1,237,040
  EBITDA:  Y1=$-163,795  Y2=$-49,317  Y3=$76,284
```

- [ ] **Step 3: Verify JSON output**

Read `data/financial-model/v6-extract-2026-04-15.json` and spot-check:
- `summary.revenue.y1` ≈ $173,294
- `summary.ebitda.y3` ≈ $76,284
- `channel_revenue["Shopify D2C"].y1` ≈ $139,278
- `sensitivity[0].scenario` = "Base (Moderate Upside)"
- `capital_summary["Total Capital"]` = 380,000

- [ ] **Step 4: Commit**

```bash
git add scripts/financial_model/extract_v6.py data/financial-model/v6-extract-2026-04-15.json
git commit -m "feat(finance): add v6 Excel extraction script and JSON output"
```

---

### Task 2: Validate v6 Baseline Against Live Supabase Data

**Purpose:** Confirm the v6 model's starting assumptions ($8,500/mo Shopify, 24.8% COGS, 559 products) are consistent with live Supabase data. Document any discrepancies.

**Files:**
- Create: `deliverables/outputs/docs/baseline-validation-2026-04-15.md`

- [ ] **Step 1: Pull current baseline metrics from Supabase**

Use the Supabase MCP plugin to query:
```sql
-- Total fulfilled orders and revenue (last 12 months)
SELECT COUNT(*) as order_count, 
       SUM(total_price::numeric) as total_revenue,
       AVG(total_price::numeric) as aov
FROM ts_orders 
WHERE fulfillment_status = 'fulfilled' 
AND created_at >= '2025-04-01';

-- Active product count
SELECT COUNT(*) FROM ts_products WHERE status = 'active';

-- Monthly revenue trend (last 6 months)
SELECT DATE_TRUNC('month', created_at) as month,
       COUNT(*) as orders,
       SUM(total_price::numeric) as revenue
FROM ts_orders
WHERE fulfillment_status = 'fulfilled'
AND created_at >= '2025-10-01'
GROUP BY 1 ORDER BY 1;
```

- [ ] **Step 2: Compare against v6 starting assumptions**

v6 assumes at closing (Jun 2026):
- Shopify D2C: $8,500/mo starting revenue
- Product COGS: 24.8% (Shopify channel)
- Blended COGS: varies by channel (24.8% core, 45% wholesale, 60% dropship)
- Platform fees: 6% Shopify, 12.5% Etsy, 30% Amazon, 8% wholesale

The v6 Model Handoff notes the business does "$7–10K/month on Shopify with ZERO paid advertising." If current Supabase data shows ~$20K/mo, that may include a broader time window or seasonal peaks. Document the reconciliation.

- [ ] **Step 3: Write validation report**

Save to `deliverables/outputs/docs/baseline-validation-2026-04-15.md`:

```markdown
# Baseline Validation: v6 Model vs. Live Supabase Data

**Date:** 2026-04-15
**v6 Model:** TS-Financial-Model-v6-Moderate-Upside.xlsx

## Summary
[One paragraph: does v6's starting point match reality?]

## Comparison Table
| Metric | v6 Assumption | Supabase Actual | Delta | Notes |
|--------|--------------|-----------------|-------|-------|
| Monthly Shopify Revenue | $8,500 | $X,XXX | X% | [context] |
| Active Products | 559 | XXX | X | [context] |
| Blended COGS | 24.8% | XX.X% | X% | [context] |
| AOV | ~$134 | $XXX | X% | [context] |

## Discrepancies & Root Causes
[Document any gaps >5% and explain why]

## Recommendation
[Any v6 assumptions that should be updated?]
```

- [ ] **Step 4: Commit**

```bash
git add deliverables/outputs/docs/baseline-validation-2026-04-15.md
git commit -m "docs(finance): add baseline validation v6 vs Supabase"
```

---

### Task 3: Deal Structure Analysis

**Purpose:** Research alternative deal structures for small business acquisitions and compare against current LOI v4 / Term Sheet v3. Provide analysis on the guaranteed-salary vs. equity-retention tradeoff, considering the seller's preference for stability and simplicity.

**Files:**
- Create: `deliverables/outputs/docs/deal-structure-analysis-2026-04-15.md`

- [ ] **Step 1: Research alternative structures**

Search for best practices in small business acquisitions with these characteristics:
- Sub-$500K acquisition value
- Seller stays on in advisory/spiritual-director role
- Buyer provides operations capital
- Seller is financially unsophisticated and values simplicity
- Seller prefers guaranteed income over equity upside

Structures to analyze:
1. **Current structure (LOI v4):** $1 nominal + $270K guaranteed payout + seller advisory role
2. **Earnout model:** Lower guaranteed + performance-based bonus tied to revenue milestones
3. **Equity retention with buyout schedule:** Seller retains X% equity, bought out over time at formula price
4. **Seller financing with security interest:** Traditional seller note with UCC filing
5. **Revenue royalty:** Seller receives X% of gross revenue for Y years instead of fixed payments

- [ ] **Step 2: Analyze tradeoffs for each structure**

For each structure, evaluate:
- **Simplicity for seller** (can they understand it without a lawyer?)
- **Financial security for seller** (guaranteed income vs. upside/downside risk)
- **Cash flow impact on business** (how does it affect the growth plan?)
- **Tax implications** (asset purchase vs. stock purchase, ordinary income vs. capital gains)
- **Alignment of incentives** (does the seller stay motivated?)
- **Risk allocation** (who bears downside if business underperforms?)

- [ ] **Step 3: Write the analysis document**

Use this structure:
```markdown
# Deal Structure Analysis — Tibetan Spirit Acquisition

**Date:** 2026-04-15
**Context:** Analysis of alternative deal structures, benchmarked against LOI v4 and Term Sheet v3.

## Current Deal Structure Summary
[Summarize LOI v4 terms: $1 nominal, $270K payout, $350K ops capital, inventory facility]

## Alternative Structures Considered
### 1. Earnout Model
[Pros/Cons/Recommendation]

### 2. Equity Retention with Buyout
[Pros/Cons/Recommendation]

### 3. Seller Financing with Security
[Pros/Cons/Recommendation]

### 4. Revenue Royalty
[Pros/Cons/Recommendation]

## Comparative Matrix
| Factor | Current (LOI v4) | Earnout | Equity Retention | Seller Note | Revenue Royalty |
|--------|------------------|---------|------------------|-------------|-----------------|
| Seller simplicity | ★★★★★ | ★★★ | ★★ | ★★★★ | ★★★★ |
| Seller security | ★★★★★ | ★★★ | ★★ | ★★★★ | ★★★ |
| Cash flow impact | ... | ... | ... | ... | ... |

## Recommendation
[Why the current structure is/isn't optimal, and any suggested modifications]
```

- [ ] **Step 4: Commit**

```bash
git add deliverables/outputs/docs/deal-structure-analysis-2026-04-15.md
git commit -m "docs(finance): add deal structure analysis with alternatives"
```

---

### Task 4: Archive Python Model Line-Extension Scenarios

**Purpose:** The 5 line-extension scenarios in `config/scenarios.yaml` are superseded by v6's channel model. Archive them. Keep the Python infrastructure (math functions, Supabase pull, formatters) — they're tested and may be adapted to v6's structure later.

**Files:**
- Move: `scripts/financial_model/config/scenarios.yaml` → `_archive/financial-model/scenarios-line-extensions.yaml`

- [ ] **Step 1: Create archive directory and move the YAML**

```bash
mkdir -p _archive/financial-model
cp scripts/financial_model/config/scenarios.yaml _archive/financial-model/scenarios-line-extensions.yaml
```

- [ ] **Step 2: Add a README explaining the archive**

Create `_archive/financial-model/README.md`:
```markdown
# Archived: Line-Extension Scenario Model

**Archived:** 2026-04-15
**Reason:** Superseded by v6 Excel financial model (TS-Financial-Model-v6-Moderate-Upside.xlsx)

## What's Here
- `scenarios-line-extensions.yaml` — 5 hypothetical product line scenarios (meditation cushions, online dharma courses, incense gift sets, ritual supplies subscription, wholesale to dharma centers)

## What's Still Active
The Python infrastructure at `scripts/financial_model/` is still active:
- `analysis.py` — Pure math functions (7 functions, 49 tests)
- `baseline.py` — Supabase baseline data pull
- `output.py` — Markdown and JSON formatters
- `scenarios.py` — YAML loader and scenario runner
- `run.py` — CLI entry point
- `extract_v6.py` — v6 Excel extraction script (new)

These can be adapted to produce reports from the v6 model's structure in a future session.

## Why Two Models?
The line-extension model answered: "Which new product lines should we add?"
The v6 Excel answers: "What does the full business P&L look like over 36 months?"
The v6 is the source of truth for deal docs, investor deck, and operational planning.
```

- [ ] **Step 3: Do NOT delete the original YAML** — leave it in place so existing tests still pass. The archive is a copy for reference. If tests are later updated to not depend on it, it can be removed.

- [ ] **Step 4: Commit**

```bash
git add _archive/financial-model/
git commit -m "docs(finance): archive line-extension scenarios, superseded by v6"
```

---

### Task 5: Verify Google Sheets Matches v6

**Purpose:** Chris shared a Google Sheet that should be "close to v6." Verify it matches the v6 Excel data and document the workflow for editing scenarios.

**Files:**
- Create: `deliverables/outputs/docs/google-sheets-workflow-2026-04-15.md`

- [ ] **Step 1: Access the Google Sheet**

URL: `https://docs.google.com/spreadsheets/u/0/d/1582dIHeTsLdcIHoaQfPsc5Hu6aHbsiZ8/edit`

Note: This is an imported .xlsx in Google Sheets. Since it's the v6 Excel uploaded to Google, it should match exactly. Check that formulas resolved correctly in Google Sheets (some Excel formulas don't translate perfectly).

- [ ] **Step 2: Spot-check key metrics**

Compare these values between Google Sheet and v6 JSON extract:
- Y1 Total Revenue: $173,294
- Y3 EBITDA: $76,284
- M36 Ending Cash: $155,172
- Shopify D2C Y1: $139,278
- Total Marketing Y1: $109,640

- [ ] **Step 3: Write workflow document**

```markdown
# Financial Model — Google Sheets Workflow

**Date:** 2026-04-15

## How to Edit Scenarios
1. Open the [TS Financial Model v6](https://docs.google.com/spreadsheets/u/0/d/1582dIHeTsLdcIHoaQfPsc5Hu6aHbsiZ8/edit) in Google Sheets
2. Go to the **Assumptions** tab
3. Edit blue-highlighted input cells (growth rates, ROAS, personnel costs, etc.)
4. The Monthly P&L, Sensitivity, and other tabs auto-calculate

## Key Assumptions You Can Change
| Assumption | Location | Current Value | Notes |
|---|---|---|---|
| Shopify D2C Growth (mo) | Assumptions B26 | 5.5% / 5.0% / 3.5% | Y1 / Y2 / Y3 |
| Etsy Growth (mo) | Assumptions B27 | 8% / 7% / 5.5% | Launches M3 |
| Amazon Growth (mo) | Assumptions B28 | — / 10% / 7% | Launches M13 |
| Blended ROAS | Assumptions B30 | 3.5x | Decays annually |
| Personnel costs | Assumptions B37-B41 | See tab | Per-person monthly |

## After Editing
- Check the **Sensitivity** tab to see how changes affect outcomes
- Check **Capital Summary** to ensure cash doesn't go negative
- Check **Monthly P&L** row 48 (Ending Cash Balance) for any months below $20K

## Syncing Changes Back
If you make significant changes in Google Sheets:
1. Download as .xlsx (File → Download → Microsoft Excel)
2. Save to `~/Documents/Claude/Projects/💼 TS / Norbu/` with a new version name
3. Run `python3 scripts/financial_model/extract_v6.py` (update V6_PATH if filename changed)
4. The JSON extract updates, and deal docs/deck can be regenerated

## Known Limitations
- Google Sheets may not perfectly replicate all Excel formulas
- The model was built with openpyxl (Python) — some formatting may differ
- Always cross-check key metrics after importing
```

- [ ] **Step 4: Commit**

```bash
git add deliverables/outputs/docs/google-sheets-workflow-2026-04-15.md
git commit -m "docs(finance): add Google Sheets workflow for v6 model editing"
```

---

## Phase 2: Deal Docs (depends on Tasks 1 + 3)

### Task 6: Write Investment Proposal

**Purpose:** Create the deal proposal document for Dr. Hun Lye and Chris's investors. This is the primary written deliverable — a conversation starter, not a legal document.

**Skill dependency:** Use `deal-memo-drafting` skill if available for structure guidance, but adapt heavily for audience (small spiritual goods business, not PE deal).

**Files:**
- Create: `deliverables/outputs/docs/ts-deal-proposal-2026-04-15.md`

**Critical rules (re-read before writing):**
- `rules/brand-voice.md`: Warm but not casual, no spiritual bypassing
- `rules/cultural-sensitivity.md`: Accurate terminology, lineage respect
- `rules/marketing-discipline.md`: No scarcity, no FOMO, no healing claims
- LOI v4 + Term Sheet v3 define the deal terms — summarize, don't modify
- v6 JSON extract provides all financial data — never make up numbers
- Dr. Hun Lye is the primary reader — write for him, not for PE analysts

- [ ] **Step 1: Load data dependencies**

Read these files:
- `data/financial-model/v6-extract-2026-04-15.json` (financial data)
- `deliverables/outputs/docs/deal-structure-analysis-2026-04-15.md` (deal analysis)
- `rules/brand-voice.md` (tone guide)
- `rules/cultural-sensitivity.md` (terminology)

- [ ] **Step 2: Draft Executive Summary (1 page max)**

Structure:
```markdown
## Executive Summary

Tibetan Spirit is [what it is — 1 sentence]. [What we're proposing — 1 sentence].
[Why this is good for everyone involved — 2-3 sentences].

**The Proposal at a Glance:**
| | |
|---|---|
| What's being acquired | All assets and operations of Tibetan Spirit |
| Purchase structure | $1 nominal acquisition + guaranteed monthly payments to Dr. Hun Lye |
| Seller receives | $270,000 total over 10 years ($3,000/month for 5 years, then $1,500/month) |
| Buyer invests | $350,000 in operations capital over 3 years |
| Seller's continuing role | Spiritual Director — guiding authenticity, product integrity, and TS Travels |
| Growth target | From ~$10K/month today to $100K+/month within 3 years |
```

Plain English. No jargon. "Monthly payments" not "seller payout obligation."

- [ ] **Step 3: Draft Business Overview (use baseline data)**

Structure:
```markdown
## What Tibetan Spirit Is Today

### The Business
[1-2 paragraphs: what TS sells, who buys it, what makes it special]
- Founded by Dr. Hun Lye (Drikung Kagyu lineage)
- Himalayan artisan goods: incense, singing bowls, malas, prayer flags, thangkas, ritual supplies
- 559 active products sourced directly from Nepal
- Current revenue: ~$8,500–10,000/month on Shopify (with zero paid advertising)

### By the Numbers
| Metric | Value |
|---|---|
| Monthly revenue | ~$8,500 (organic only, no ads) |
| Active products | 559 |
| Average order value | ~$134 |
| Product cost (COGS) | 24.8% of revenue |
| Profit margin on products | ~75% |
| Platform | Shopify D2C |

### What Makes This Special
[2-3 paragraphs on the moat: authentic sourcing, Drikung Kagyu lineage, practitioner audience, Dr. Hun Lye's credibility, direct Nepal relationships]
```

Use "profit margin on products" not "gross margin." Use "monthly revenue" not "MRR."

- [ ] **Step 4: Draft Growth Vision**

Structure:
```markdown
## Where We're Taking Tibetan Spirit

### The Opportunity
[1-2 paragraphs: this business has never had marketing, SEO, or multi-channel distribution. What happens when you add those?]

### Growth Plan by Year

**Year 1 (Jun 2026 – May 2027): Build the Foundation**
- Launch email marketing (Klaviyo) — Buddhist audiences have 55% email open rates
- Begin paid advertising (Meta, Google, Pinterest) — target 2.5x+ return on ad spend
- Launch on Etsy (Month 3) — natural home for artisan Buddhist goods
- Invest in SEO/content — "singing bowls" gets 40-60K monthly Google searches
- Total revenue: ~$173,000

**Year 2 (Jun 2027 – May 2028): Expand Channels**
- Launch on Amazon (Month 13)
- Launch TS Travels (2 pilgrimage trips at ~$150K each)
- Add high-value dropship items ($2K–$7K statues, thangkas from Kathmandu)
- Begin wholesale to dharma centers via Faire
- Total revenue: ~$773,000

**Year 3 (Jun 2028 – May 2029): Scale Profitably**
- All channels mature, subscription base grows
- Business becomes cash-flow positive (EBITDA ~$76,000)
- Revenue approaches $1.2 million
- Ending cash position: ~$155,000

### Revenue by Channel (3-Year View)
| Channel | Year 1 | Year 2 | Year 3 |
|---|---|---|---|
| Shopify (online store) | $139,000 | $257,000 | $424,000 |
| Etsy | $14,000 | $39,000 | $80,000 |
| Amazon | — | $53,000 | $140,000 |
| Wholesale (dharma centers) | $10,000 | $32,000 | $61,000 |
| Subscription boxes | $10,000 | $37,000 | $124,000 |
| High-value items (dropship) | — | $54,000 | $108,000 |
| TS Travels (pilgrimage trips) | — | $300,000 | $300,000 |
| **Total** | **$173,000** | **$773,000** | **$1,237,000** |
```

All numbers from v6 JSON extract. Round to nearest $1K for readability.

- [ ] **Step 5: Draft Investment & Returns section**

Structure:
```markdown
## Investment & What to Expect

### What Capital Is Needed
| Investment | Amount | When | Purpose |
|---|---|---|---|
| Operations capital (Year 1) | $200,000 | At closing | Marketing, team, technology, working capital |
| Operations capital (Year 2) | $100,000 | As needed | Continued growth investment |
| Reserve (Year 3) | $50,000 | If needed | Safety net; business expected to be self-sustaining |
| **Total** | **$350,000** | Over 3 years | Interest-free, repayment deferred |

### Range of Outcomes
We've modeled three scenarios to show what could happen:

| Scenario | Description | Year 3 Profit | Cash at Month 36 |
|---|---|---|---|
| **Conservative** | Everything takes longer, lower growth | [from sensitivity] | [from sensitivity] |
| **Base case** | Average execution on standard growth levers | $76,000/year | $155,000 |
| **If things go better** | Strong execution, market tailwinds | [from sensitivity] | [from sensitivity] |

[1 paragraph explaining that Year 1-2 are intentionally unprofitable — we're investing in growth. The marketing spend is front-loaded. The business turns profitable in Year 3 and stays profitable.]

### When Does the Investment Come Back?
Operations capital repayment begins in Year 4, only after the business achieves sustained profitability. Monthly repayments are capped at 15% of cash flow — the business always comes first.
```

Use "profit" not "EBITDA." Use "cash at month 36" not "ending cash balance." Use "if things go better" not "optimistic scenario."

- [ ] **Step 6: Draft Team & Execution section**

```markdown
## Who's Running This

| Person | Role | What They Do |
|---|---|---|
| Chris Mauzé | CEO & Strategy | Growth strategy, AI operations, marketing, financial management |
| Dr. Hun Lye | Spiritual Director | Product authenticity, cultural integrity, TS Travels leadership |
| Jothi | Operations Manager | Supply chain, customer service, day-to-day operations |
| Fiona | Warehouse Manager | Inventory, shipping, fulfillment |
| Nepal Team | Production | Artisan coordination, sourcing, quality control |
| CS Hire (Oct 2026) | Customer Service | Dedicated customer support as volume grows |

### The AI Advantage
[1 paragraph: Chris's background in AI operations means TS gets enterprise-level automation at a fraction of the cost. Automated customer service drafting, inventory forecasting, financial reporting — capabilities that businesses 10x this size typically can't afford. Be specific: "Our AI systems draft customer emails in under 30 seconds" not "we use AI."]
```

- [ ] **Step 7: Draft Terms Overview section**

```markdown
## How the Deal Works

This section summarizes the key terms. The full details are in the Letter of Intent and Term Sheet.

**For Dr. Hun Lye:**
- You receive $3,000 per month for 5 years ($180,000 total), then $1,500 per month for 5 more years ($90,000 total)
- These payments are **guaranteed** — they don't depend on how the business performs
- You continue as Spiritual Director, ensuring the business stays true to its roots
- You lead 1-2 TS Travels pilgrimage trips per year

**For the Business:**
- Chris provides $350,000 in operations capital over 3 years to fund growth
- A separate inventory credit line (0% interest) ensures we can always keep products in stock
- 10% of profits go to the Foundation (Forest Hermitage) in months when the business is profitable

**What Stays the Same:**
- The products, the sourcing relationships, the Nepal team
- The commitment to authentic Himalayan artisan goods
- Dr. Hun Lye's spiritual guidance and direction
- The practice-first philosophy that makes Tibetan Spirit special
```

- [ ] **Step 8: Review entire document against constraints**

Checklist:
- [ ] No VC/PE jargon (EBITDA, IRR, terminal value, MOIC)
- [ ] All numbers match v6 JSON extract
- [ ] Conservative scenario shown alongside base case
- [ ] Brand voice: warm, respectful, professional
- [ ] Cultural sensitivity: correct terminology (mala not prayer bracelet, thangka not Buddhist painting)
- [ ] No healing claims, scarcity tactics, or spiritual benefit promises
- [ ] Deal terms match LOI v4 exactly
- [ ] Readable by someone who runs a small spiritual goods business

- [ ] **Step 9: Commit**

```bash
git add deliverables/outputs/docs/ts-deal-proposal-2026-04-15.md
git commit -m "docs(deal): add investment proposal for TS acquisition"
```

---

## Phase 3: Vision Deck (depends on Task 6)

### Task 7: Create Vision Pitch Deck

**Purpose:** Create a Marp slide deck (~12-15 slides) for Chris's investors. Data-heavy, zero BS, no hype. This is also the foundational brand voice/mission document — subsequent artifacts (Operational Handbook, learning paths) will reference it.

**Skill dependency:** Use `marp-deck` skill for deck generation and conversion.

**Files:**
- Create: `deliverables/outputs/decks/ts-vision-deck-2026-04-15.md`

**Reference materials (for structure, NOT tone):**
- Attaboy Seed Deck: `/Users/chrismauze/Documents/Files/Business/laurina partners/examples/Attaboy-Seed-Deck.pdf` — good Problem → Solution → Market → Product → Financials → Team → Ask flow
- Stars+Honey IC Memo: `/Users/chrismauze/Documents/Claude/Projects/Crane Diligence/Diligence examples/Stars+honey Clean Presentation.pdf` — good "investment merits" table, risk presentation, data-forward
- Vacation IC Memo: `/Users/chrismauze/Documents/Claude/Projects/Crane Diligence/Diligence examples/2026.01.28 Vacation IC.pdf` — good exec summary, BETTER/MIXED/UNCHANGED framework

**Style rules for this deck:**
- Data-heavy, narrative-light — let the numbers talk
- No stock photos, clip art, or "inspirational" imagery
- Clean, professional, minimal design
- Every slide has a "so what" — no filler slides
- If a claim can be backed by a number, back it with a number
- Conservative projections with upside shown as sensitivity ranges
- This audience is already bought in — they want to see the vision with real numbers

- [ ] **Step 1: Load data dependencies**

Read:
- `data/financial-model/v6-extract-2026-04-15.json`
- `deliverables/outputs/docs/ts-deal-proposal-2026-04-15.md` (narrative already written)
- `rules/brand-voice.md`
- `rules/cultural-sensitivity.md`

- [ ] **Step 2: Draft Marp slide deck**

Use the `marp-deck` skill. The deck structure (adapt based on what the data says):

**Slide 1: Title**
- Tibetan Spirit: Growth Vision 2026–2029
- Clean, minimal, no tagline

**Slide 2: What We Have Today**
- Current state snapshot: ~$8.5K/mo revenue, 559 products, ~$134 AOV, 75% product margins
- Zero paid advertising, zero email marketing, zero multi-channel
- "This is a business that has never been marketed."

**Slide 3: What Makes This Defensible**
- Authentic Drikung Kagyu lineage (Dr. Hun Lye)
- Direct Nepal sourcing relationships (50-80% gross margins)
- Practitioner audience (not "wellness tourists")
- 559-product catalog with decades of curation
- Competitors: DharmaCrafts ($3-8M), DharmaShop, Buddha Groove ($5M+) — TS has the authenticity moat they don't

**Slide 4: The Opportunity**
- Business has never had: paid ads, email marketing, SEO, multi-channel distribution
- Religious/spiritual audiences: 55.7% email open rates (highest industry)
- Search volume: "singing bowls" 40-60K/mo, "mala beads" 10-20K/mo
- Comparable businesses in this space do $3-8M+ revenue

**Slide 5: Financial Model — Revenue Trajectory**
- 3-year revenue chart: $173K → $773K → $1.24M
- Channel mix visualization
- "Revenue includes TS Travels ($300K/yr from Y2)"

**Slide 6: Financial Model — Path to Profitability**
- EBITDA trajectory: -$164K → -$49K → +$76K
- Ending cash: $50K → $65K → $155K
- "Negative EBITDA in Y1-2 is intentional — we're investing in growth"

**Slide 7: Channel Strategy**
- Shopify D2C (core): $139K → $257K → $424K
- Marketplaces (Etsy M3, Amazon M13): $0 → $92K → $220K
- Subscription: $10K → $37K → $124K
- Wholesale: $10K → $32K → $61K
- Dropship (high-value): $0 → $54K → $108K
- TS Travels: $0 → $300K → $300K

**Slide 8: Growth Roadmap**
- Phase 1 ($8K/mo → $15K/mo): Email, SEO, paid ads, Etsy launch
- Phase 2 ($15K/mo → $65K/mo): Amazon, TS Travels, dropship, wholesale
- Phase 3 ($65K/mo → $100K+/mo): Subscription scale, all channels mature

**Slide 9: AI Operations Advantage**
- 6 specialized AI agents handling: CS drafting, inventory forecasting, fulfillment tracking, catalog management, marketing strategy, financial analysis
- Specific metrics: "CS email drafts generated in <30 seconds", "Weekly P&L automated", "Inventory alerts at 9am daily"
- "Capabilities that businesses 10x this size typically can't afford"
- All customer-facing outputs require human approval

**Slide 10: Capital Requirements**
- Y1: $200K (marketing, team, technology)
- Y2: $100K (continued growth)
- Y3: $50K (reserve, expected cash-flow positive)
- Total: $350K operations capital + revolving inventory facility
- Repayment: deferred to Y4+, capped at 15% of cash flow

**Slide 11: Sensitivity Analysis**
- Base case: $76K Y3 EBITDA, $155K M36 cash
- Conservative (70% revenue): [from v6 sensitivity tab]
- Show that even at 70% of plan, business is viable

**Slide 12: Risk & Mitigation**
- Supply chain (Nepal): Multiple supplier relationships, inventory buffer
- Single-channel dependency (Shopify): Multi-channel launch by M3 (Etsy), M13 (Amazon)
- Category concentration: Expanding into high-value items, subscription, TS Travels
- Execution risk: Conservative assumptions (low end of market research ranges, average execution)

**Slide 13: Team**
- Chris Mauzé: CEO — CPO-level ops experience, AI automation expertise
- Dr. Hun Lye: Spiritual Director — Drikung Kagyu lineage, ensures authenticity
- Jothi: Operations Manager — Supply chain, CS, daily operations
- Fiona: Warehouse — Inventory, shipping
- Omar/Nepal: Production coordination

**Slide 14: The Vision**
- "Tibetan Spirit is both a business and a service to the dharma community"
- 10% of profits to Forest Hermitage Foundation
- The goal: build the most trusted source of authentic Himalayan practice goods
- Not "disrupting wellness" — serving practitioners with integrity

- [ ] **Step 3: Run marp-deck skill to generate HTML/PDF**

Invoke the `marp-deck` skill to convert the Marp markdown to HTML and PDF.

- [ ] **Step 4: Review deck against constraints**

Checklist:
- [ ] Every slide has data or a clear "so what"
- [ ] No stock photos, clip art, or decorative imagery
- [ ] All numbers match v6 JSON extract
- [ ] Conservative projections shown alongside base
- [ ] No prohibited language (exotic, mystical, healing claims, zen vibes)
- [ ] Correct Buddhist terminology (mala, thangka, dharma, sangha)
- [ ] Practice-first framing, not home-decor or wellness-tourism framing
- [ ] Tone: data-forward, honest about risks, no hype
- [ ] ~12-15 slides (no filler)
- [ ] Brand voice and mission are clearly established (this is foundational)

- [ ] **Step 5: Commit**

```bash
git add deliverables/outputs/decks/ts-vision-deck-2026-04-15.md
git commit -m "docs(deck): add vision pitch deck for TS investors"
```

---

## Execution Order

```
Phase 1 (parallel):
  ├── Task 1: Extract v6 Excel to JSON (blocks Phase 2 + 3)
  ├── Task 2: Validate v6 Baseline vs Supabase
  ├── Task 3: Deal Structure Analysis (blocks Phase 2)
  ├── Task 4: Archive Python Model Scenarios
  └── Task 5: Verify Google Sheets

Phase 2 (after Tasks 1 + 3):
  └── Task 6: Write Investment Proposal (blocks Phase 3)

Phase 3 (after Task 6):
  └── Task 7: Create Vision Pitch Deck
```

## Success Criteria

- [ ] v6 data extracted to JSON and spot-checked
- [ ] Baseline validated against Supabase (discrepancies documented)
- [ ] Deal structure alternatives analyzed
- [ ] Deal proposal readable by non-financial business owner
- [ ] Deal proposal presents conservative + base scenarios
- [ ] Vision deck has ~12-15 data-backed slides with no filler
- [ ] Vision deck projections tie directly to v6 model output
- [ ] Vision deck establishes brand voice/mission as foundational artifact
- [ ] All deliverables saved to `deliverables/outputs/`
- [ ] Line-extension scenarios archived with explanation
- [ ] Google Sheets workflow documented
- [ ] Chris reviews and approves before any external distribution
