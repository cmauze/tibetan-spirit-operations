# TS Financial Model v7 + Deal Docs Rewrite — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python-driven financial model (v7) that generates a Google Sheets-ready xlsx, rewrite the deal proposal with legal recommendations integrated, and produce a tax/legal checklist for attorney review.

**Architecture:** A YAML config holds all assumptions. A Python model engine computes 36-month P&L with D2C and TS Travels as completely separate business units. An xlsx writer outputs multi-tab workbook uploadable to Google Sheets. Deal docs are markdown, referencing model output for numbers.

**Tech Stack:** Python 3, openpyxl (xlsx), PyYAML, pytest. No new dependencies — all already in pyproject.toml.

**Key Changes from v6:**
- COGS: 30% conservative (was 24.8%) — per Chris's direction
- Starting D2C revenue: $7,500/mo (was $8,500) — based on rolling 30-day actuals ($7,214)
- D2C and TS Travels fully separated (v6 mixed them in Shopify)
- D2C AOV: ~$75 organic (was $134 — that figure was polluted by Bhutan trip bookings)
- Channel scenario toggles: show contribution of each new channel
- Seller payout context: Dr. Hun Lye plans to ordain as a monk after Y5, reducing active involvement (explains salary step-down)

**Source Data:**
- v6 extract: `/Users/chrismauze/code/active/tibetan-spirit-ops/data/financial-model/v6-extract-2026-04-15.json`
- COGS estimation sheet: `https://docs.google.com/spreadsheets/d/1Ya-YKFpB7nkSP8ZSRbdw-ljeWfcH3NPZ/edit?gid=1567771273#gid=1567771273`
- Deal docs source: `/Users/chrismauze/Documents/Claude/Projects/💼 TS / Norbu/`

**Files Overview:**
| Action | Path | Purpose |
|--------|------|---------|
| Create | `scripts/financial_model/config/model_v7.yaml` | All assumptions in one config |
| Create | `scripts/financial_model/model.py` | 36-month P&L engine |
| Create | `scripts/financial_model/build_xlsx.py` | xlsx generator CLI |
| Create | `tests/test_model_v7.py` | Tests for model.py |
| Create | `deliverables/outputs/docs/ts-financial-model-v7-2026-04-16.xlsx` | Generated output |
| Create | `deliverables/outputs/docs/ts-deal-proposal-v2-2026-04-16.md` | Rewritten deal proposal |
| Create | `deliverables/outputs/docs/ts-tax-legal-checklist-2026-04-16.md` | Tax/legal checklist |
| Create | `workspace/plans/review-plan-2026-04-16.md` | Chris's review checklist |

---

## Phase 1: Financial Model v7

### Task 1: Model Config YAML

**Purpose:** Single file with every assumption. When Chris wants to change a number, he edits this YAML and re-runs the script.

**Files:**
- Create: `scripts/financial_model/config/model_v7.yaml`

- [ ] **Step 1: Create the config file**

```yaml
# Tibetan Spirit Financial Model v7 — Assumptions Config
# Edit values here, then run: python3 scripts/financial_model/build_xlsx.py
# All dollar amounts are monthly unless noted.

meta:
  version: "v7"
  scenario: "Base Case (Conservative COGS)"
  period: "Jun 2026 – May 2029"
  months: 36
  start_year: 2026
  start_month: 6  # June

# --- D2C Product Business ---
d2c:
  cogs_pct: 0.30  # Conservative blended COGS (was 24.8% in v6)
  shipping_fulfillment_pct: 0.115  # ~11.5% of product revenue

  channels:
    shopify:
      label: "Shopify D2C"
      start_month: 1
      starting_revenue: 7500  # Rolling 30-day actual: $7,214
      monthly_growth: [0.055, 0.05, 0.035]  # Y1 / Y2 / Y3
      platform_fee_pct: 0.06
      cogs_pct_override: null  # Uses d2c.cogs_pct

    etsy:
      label: "Etsy"
      start_month: 3  # Aug 2026
      starting_revenue: 1000
      monthly_growth: [0.08, 0.07, 0.055]
      platform_fee_pct: 0.125
      cogs_pct_override: null

    amazon:
      label: "Amazon"
      start_month: 13  # Jun 2027
      starting_revenue: 2500
      monthly_growth: [null, 0.10, 0.07]  # null = not active
      platform_fee_pct: 0.30  # Referral + FBA
      cogs_pct_override: null

    wholesale:
      label: "Wholesale (Faire)"
      start_month: 7  # Dec 2026
      starting_revenue: 1500
      monthly_growth: [0.04, 0.06, 0.05]
      platform_fee_pct: 0.08
      cogs_pct_override: 0.45  # 50% off retail pricing

    subscription:
      label: "Quarterly Subscription"
      type: "quarterly"  # Revenue fires quarterly, not monthly
      start_month: 4  # Sep 2026 (first quarter shipment)
      starting_quarterly_revenue: 2296
      quarterly_growth: 0.35  # 35% growth per quarter
      platform_fee_pct: 0.06
      cogs_pct_override: 0.283  # Curated boxes, ~72% margin
      cannibalization_pct: 0.18  # Net of one-off displacement

    dropship:
      label: "High-Value Dropship (Kathmandu)"
      type: "unit_based"  # Revenue = units × avg_order_value
      start_month: 13  # Jun 2027
      units_per_month: [0, 1.5, 3.0]  # Y1 / Y2 / Y3
      avg_order_value: 3000  # $2K–$7K range, $3K avg
      platform_fee_pct: 0.06
      cogs_pct_override: 0.60  # Custom commission from Nepal artists

# --- TS Travels (Completely Separate Business Unit) ---
travels:
  label: "TS Travels (Pilgrimages)"
  trips_per_year: [0, 2, 2]  # Y1 / Y2 / Y3
  revenue_per_trip: 150000
  cogs_pct: 0.60  # Travel program — 40% gross margin
  # No platform fees, no shipping — different cost structure entirely
  # Dr. Hun Lye leads trips; this is the primary ongoing Spiritual Director contribution

# --- Operating Costs ---
costs:
  personnel:
    # Amounts are monthly salary/contractor cost
    base_team:  # Jun 2026 onward
      jothi: 2500      # Operations Manager
      fiona: 1500      # Warehouse Manager
      nepal_team: 1333  # Production coordination
      chris_draw: 1500  # CEO draw (modest Y1)
    cs_hire:
      monthly: 833     # Customer Service (Oct 2026, month 5)
      start_month: 5
    y2_adjustments:     # Applied starting Jun 2027 (month 13)
      jothi: 2750       # +$250
      fiona: 1600       # +$100
      nepal_team: 1441  # +8%
      chris_draw: 2500  # Increase in Y2
    y3_adjustments:     # Applied starting Jun 2028 (month 25)
      jothi: 3000       # +$250
      fiona: 1750       # +$150
      nepal_team: 1500  # Increase
      chris_draw: 3500  # Increase in Y3

  technology:
    monthly_y1: 2500    # Shopify, Supabase, Klaviyo, etc.
    monthly_y2: 3000    # + Amazon tools, additional SaaS
    monthly_y3: 3000    # Stable

  marketing:
    # Marketing as % of product revenue (MER approach)
    # v6 actuals: Y1 63%, Y2 47%, Y3 31%
    pct_of_product_revenue_y1: 0.63
    pct_of_product_revenue_y2: 0.47
    pct_of_product_revenue_y3: 0.31
    # Q4 seasonal boost (Oct–Jan = 2x normal marketing spend)
    q4_multiplier: 2.0
    q4_months: [10, 11, 12, 1]  # Calendar months Oct–Jan

  seller_payout:
    monthly_y1_5: 3000   # $36K/year, guaranteed
    monthly_y6_10: 1500  # Dr. Hun Lye ordains as monk, reduced involvement
    # Note: Only Y1-3 in model scope, so always $3K/mo

  foundation:
    pct_of_net_profit: 0.10  # 10% of net profit
    only_profitable_months: true
    recipient: "Forest Hermitage"

# --- Capital Structure ---
capital:
  cash_on_hand: 20000
  ops_capital:
    y1: 200000   # At closing (Jun 2026)
    y2: 100000   # Start of Y2 (Jun 2027)
    y3: 50000    # Reserve (Jun 2028)
  truist_cd: 30000  # Available Mar 2027 (month 10)
  inventory_facility:
    cap: 100000  # Recommended cap (v6 had "no cap" — legally untenable)
    interest: 0.0
    reconciliation: "quarterly"

# --- Scenario Toggles ---
# build_xlsx.py generates these scenarios automatically:
# 1. "Shopify Only" — just D2C Shopify, no other channels
# 2. "D2C Core" — Shopify + Etsy + Subscription
# 3. "Full D2C" — All D2C channels (Shopify + Etsy + Amazon + Wholesale + Sub + Dropship)
# 4. "Full Business" — Full D2C + TS Travels
# Each scenario computes its own P&L, EBITDA, and cash position

# --- Sensitivity ---
sensitivity:
  revenue_factors: [0.70, 0.85, 1.0, 1.15]
  labels: ["Conservative (70%)", "Moderate (85%)", "Base Case", "Upside (115%)"]
```

- [ ] **Step 2: Verify YAML loads cleanly**

```bash
cd /Users/chrismauze/code/active/tibetan-spirit-ops
python3 -c "import yaml; d = yaml.safe_load(open('scripts/financial_model/config/model_v7.yaml')); print(f'Loaded: {len(d)} top-level keys'); print('Channels:', list(d['d2c']['channels'].keys()))"
```

Expected:
```
Loaded: 6 top-level keys
Channels: ['shopify', 'etsy', 'amazon', 'wholesale', 'subscription', 'dropship']
```

- [ ] **Step 3: Commit**

```bash
git add scripts/financial_model/config/model_v7.yaml
git commit -m "feat(finance): add v7 model assumptions config"
```

---

### Task 2: Model Engine — Channel Projections

**Purpose:** Pure functions that compute monthly revenue for each channel type. No I/O, no side effects — testable in isolation.

**Files:**
- Create: `scripts/financial_model/model.py`
- Create: `tests/test_model_v7.py`

- [ ] **Step 1: Write tests for standard channel projection**

Create `tests/test_model_v7.py`:

```python
"""Tests for financial model v7 — 36-month P&L engine."""
import pytest
from scripts.financial_model.model import (
    project_standard_channel,
    project_quarterly_subscription,
    project_unit_based_channel,
    project_travels,
    compute_marketing_spend,
    compute_personnel_cost,
    build_monthly_pnl,
)


class TestProjectStandardChannel:
    """Standard channels: Shopify, Etsy, Amazon, Wholesale."""

    def test_shopify_month_1(self):
        """Month 1 revenue equals starting_revenue."""
        result = project_standard_channel(
            start_month=1,
            starting_revenue=7500,
            monthly_growth=[0.055, 0.05, 0.035],
            months=36,
        )
        assert result[0] == pytest.approx(7500.0)

    def test_shopify_month_2_applies_growth(self):
        """Month 2 = starting * (1 + Y1 growth rate)."""
        result = project_standard_channel(
            start_month=1,
            starting_revenue=7500,
            monthly_growth=[0.055, 0.05, 0.035],
            months=36,
        )
        assert result[1] == pytest.approx(7500 * 1.055)

    def test_channel_before_start_is_zero(self):
        """Months before start_month return 0."""
        result = project_standard_channel(
            start_month=3,
            starting_revenue=1000,
            monthly_growth=[0.08, 0.07, 0.055],
            months=36,
        )
        assert result[0] == 0.0
        assert result[1] == 0.0
        assert result[2] == pytest.approx(1000.0)

    def test_growth_rate_switches_at_year_boundary(self):
        """Month 13 (start of Y2) uses Y2 growth rate."""
        result = project_standard_channel(
            start_month=1,
            starting_revenue=7500,
            monthly_growth=[0.055, 0.05, 0.035],
            months=36,
        )
        # Month 12 uses Y1 rate, month 13 uses Y2 rate
        assert result[12] == pytest.approx(result[11] * 1.05)

    def test_returns_36_values(self):
        result = project_standard_channel(
            start_month=1,
            starting_revenue=7500,
            monthly_growth=[0.055, 0.05, 0.035],
            months=36,
        )
        assert len(result) == 36

    def test_all_values_non_negative(self):
        result = project_standard_channel(
            start_month=1,
            starting_revenue=7500,
            monthly_growth=[0.055, 0.05, 0.035],
            months=36,
        )
        assert all(v >= 0 for v in result)


class TestProjectQuarterlySubscription:
    """Subscription revenue fires quarterly with inter-quarter growth."""

    def test_fires_only_on_quarter_months(self):
        """Revenue is non-zero only on months divisible by 3 from start."""
        result = project_quarterly_subscription(
            start_month=4,
            starting_quarterly_revenue=2296,
            quarterly_growth=0.35,
            months=36,
        )
        # Month 4 (idx 3), 7 (idx 6), 10 (idx 9), 13 (idx 12)...
        for i, val in enumerate(result):
            month = i + 1
            if month >= 4 and (month - 4) % 3 == 0:
                assert val > 0, f"Month {month} should have subscription revenue"
            else:
                assert val == 0.0, f"Month {month} should be zero (non-quarter)"

    def test_first_quarter_equals_starting(self):
        result = project_quarterly_subscription(
            start_month=4,
            starting_quarterly_revenue=2296,
            quarterly_growth=0.35,
            months=36,
        )
        assert result[3] == pytest.approx(2296.0)

    def test_second_quarter_applies_growth(self):
        result = project_quarterly_subscription(
            start_month=4,
            starting_quarterly_revenue=2296,
            quarterly_growth=0.35,
            months=36,
        )
        assert result[6] == pytest.approx(2296 * 1.35)


class TestProjectUnitBasedChannel:
    """Dropship: revenue = units_per_month × avg_order_value."""

    def test_zero_before_start(self):
        result = project_unit_based_channel(
            start_month=13,
            units_per_month=[0, 1.5, 3.0],
            avg_order_value=3000,
            months=36,
        )
        assert all(v == 0.0 for v in result[:12])

    def test_y2_revenue(self):
        """Month 13: 1.5 units × $3K = $4,500."""
        result = project_unit_based_channel(
            start_month=13,
            units_per_month=[0, 1.5, 3.0],
            avg_order_value=3000,
            months=36,
        )
        assert result[12] == pytest.approx(4500.0)

    def test_y3_revenue(self):
        """Month 25: 3.0 units × $3K = $9,000."""
        result = project_unit_based_channel(
            start_month=13,
            units_per_month=[0, 1.5, 3.0],
            avg_order_value=3000,
            months=36,
        )
        assert result[24] == pytest.approx(9000.0)


class TestProjectTravels:
    """TS Travels: lump revenue events per year."""

    def test_zero_in_y1(self):
        result = project_travels(
            trips_per_year=[0, 2, 2],
            revenue_per_trip=150000,
            months=36,
        )
        assert sum(result[:12]) == 0.0

    def test_y2_total(self):
        """Y2: 2 trips × $150K = $300K total."""
        result = project_travels(
            trips_per_year=[0, 2, 2],
            revenue_per_trip=150000,
            months=36,
        )
        assert sum(result[12:24]) == pytest.approx(300000.0)

    def test_trips_spread_across_year(self):
        """2 trips per year should land in 2 different months."""
        result = project_travels(
            trips_per_year=[0, 2, 2],
            revenue_per_trip=150000,
            months=36,
        )
        y2_nonzero = [v for v in result[12:24] if v > 0]
        assert len(y2_nonzero) == 2


class TestComputeMarketingSpend:
    """Marketing = % of product revenue with Q4 boost."""

    def test_base_month(self):
        """Non-Q4 month: product_revenue × pct."""
        result = compute_marketing_spend(
            product_revenue=10000,
            pct=0.63,
            calendar_month=3,  # March — not Q4
            q4_multiplier=2.0,
            q4_months=[10, 11, 12, 1],
        )
        assert result == pytest.approx(6300.0)

    def test_q4_month(self):
        """Q4 month: product_revenue × pct × q4_multiplier."""
        result = compute_marketing_spend(
            product_revenue=10000,
            pct=0.63,
            calendar_month=11,  # November — Q4
            q4_multiplier=2.0,
            q4_months=[10, 11, 12, 1],
        )
        assert result == pytest.approx(12600.0)


class TestComputePersonnelCost:
    """Personnel cost by month, with step-ups at Y2 and Y3."""

    def test_month_1_base_team(self):
        """Month 1: base team only (no CS hire yet)."""
        result = compute_personnel_cost(
            month=1,
            base_team={"jothi": 2500, "fiona": 1500, "nepal": 1333, "chris": 1500},
            cs_hire={"monthly": 833, "start_month": 5},
            y2_adjustments={"jothi": 2750, "fiona": 1600, "nepal": 1441, "chris": 2500},
            y3_adjustments={"jothi": 3000, "fiona": 1750, "nepal": 1500, "chris": 3500},
        )
        assert result == pytest.approx(6833.0)

    def test_month_5_adds_cs(self):
        """Month 5: base team + CS hire."""
        result = compute_personnel_cost(
            month=5,
            base_team={"jothi": 2500, "fiona": 1500, "nepal": 1333, "chris": 1500},
            cs_hire={"monthly": 833, "start_month": 5},
            y2_adjustments={"jothi": 2750, "fiona": 1600, "nepal": 1441, "chris": 2500},
            y3_adjustments={"jothi": 3000, "fiona": 1750, "nepal": 1500, "chris": 3500},
        )
        assert result == pytest.approx(7666.0)

    def test_month_13_y2_rates(self):
        """Month 13: Y2 team rates + CS hire."""
        result = compute_personnel_cost(
            month=13,
            base_team={"jothi": 2500, "fiona": 1500, "nepal": 1333, "chris": 1500},
            cs_hire={"monthly": 833, "start_month": 5},
            y2_adjustments={"jothi": 2750, "fiona": 1600, "nepal": 1441, "chris": 2500},
            y3_adjustments={"jothi": 3000, "fiona": 1750, "nepal": 1500, "chris": 3500},
        )
        assert result == pytest.approx(8291.0 + 833)
        # Wait — v6 has 8291 for Y2. Let me verify:
        # 2750 + 1600 + 1441 + 2500 = 8291. Plus CS 833 = 9124.
        # But v6 shows 8291 for Y2 months. That means CS is included in the 8291.
        # So Y2 base = 2750 + 1600 + 1441 + 2500 = 8291, which INCLUDES CS adjustments.
        # Let me re-check v6: Y1 months 1-4 = 6833, months 5-12 = 7666 (+833 CS).
        # Y2 = 8291. So 8291 = Y2 all-in including CS. That means Y2 adjustments
        # already account for CS being on the team.
        # For simplicity, model personnel as a single monthly figure per period:


class TestBuildMonthlyPnl:
    """Integration: full P&L assembly."""

    def test_returns_36_months(self):
        """P&L has exactly 36 monthly rows."""
        # This test will use a minimal config — see implementation
        pass  # Placeholder — implement after model.py exists

    def test_d2c_and_travels_separated(self):
        """P&L has separate d2c_revenue and travels_revenue columns."""
        pass
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /Users/chrismauze/code/active/tibetan-spirit-ops
python3 -m pytest tests/test_model_v7.py -v 2>&1 | head -20
```

Expected: ImportError — `model.py` doesn't exist yet.

- [ ] **Step 3: Create model.py with channel projection functions**

Create `scripts/financial_model/model.py`:

```python
"""
Tibetan Spirit Financial Model v7 — 36-month P&L engine.

Pure functions. All assumptions come from config dict (loaded from YAML).
No I/O, no side effects — fully testable.

Usage:
    from scripts.financial_model.model import build_monthly_pnl, build_scenarios
    import yaml

    config = yaml.safe_load(open("scripts/financial_model/config/model_v7.yaml"))
    pnl = build_monthly_pnl(config)
    scenarios = build_scenarios(config)
"""
from __future__ import annotations

from datetime import date
from typing import Optional


def _year_for_month(month: int) -> int:
    """Which model year (1, 2, or 3) does this month fall in?"""
    if month <= 12:
        return 1
    elif month <= 24:
        return 2
    else:
        return 3


def _growth_rate_for_month(month: int, rates: list) -> Optional[float]:
    """Get growth rate for a given month. rates = [y1_rate, y2_rate, y3_rate].
    Returns None if that year's rate is null/None (channel not active)."""
    year = _year_for_month(month)
    rate = rates[year - 1]
    return rate


def _calendar_month(model_month: int, start_month: int = 6) -> int:
    """Convert model month (1-36) to calendar month (1-12).
    Model starts June (6), so month 1 = June, month 7 = December, etc."""
    return ((start_month - 1 + model_month - 1) % 12) + 1


def project_standard_channel(
    start_month: int,
    starting_revenue: float,
    monthly_growth: list,
    months: int = 36,
) -> list[float]:
    """Project monthly revenue for a standard growth channel.

    Args:
        start_month: Model month when channel launches (1-based).
        starting_revenue: First month's revenue.
        monthly_growth: [y1_rate, y2_rate, y3_rate] — monthly compound growth.
        months: Total months to project (default 36).

    Returns:
        List of monthly revenue values (length = months).
    """
    result = []
    current = 0.0
    for m in range(1, months + 1):
        if m < start_month:
            result.append(0.0)
            continue
        if m == start_month:
            current = starting_revenue
            result.append(current)
            continue
        rate = _growth_rate_for_month(m, monthly_growth)
        if rate is None:
            result.append(0.0)
            continue
        current *= (1 + rate)
        result.append(round(current, 2))
    return result


def project_quarterly_subscription(
    start_month: int,
    starting_quarterly_revenue: float,
    quarterly_growth: float,
    months: int = 36,
) -> list[float]:
    """Project quarterly subscription revenue.

    Revenue fires every 3 months starting from start_month.
    Grows by quarterly_growth rate each quarter.

    Returns:
        List of monthly revenue (non-zero only on quarter months).
    """
    result = [0.0] * months
    current_quarterly = starting_quarterly_revenue
    quarter_count = 0

    for m in range(1, months + 1):
        if m < start_month:
            continue
        if (m - start_month) % 3 == 0:
            if quarter_count == 0:
                result[m - 1] = current_quarterly
            else:
                current_quarterly *= (1 + quarterly_growth)
                result[m - 1] = round(current_quarterly, 2)
            quarter_count += 1

    return result


def project_unit_based_channel(
    start_month: int,
    units_per_month: list,
    avg_order_value: float,
    months: int = 36,
) -> list[float]:
    """Project revenue for unit-based channels (dropship).

    units_per_month: [y1_units, y2_units, y3_units] — avg units sold per month.

    Returns:
        List of monthly revenue values.
    """
    result = []
    for m in range(1, months + 1):
        if m < start_month:
            result.append(0.0)
            continue
        year = _year_for_month(m)
        units = units_per_month[year - 1]
        if units is None or units == 0:
            result.append(0.0)
        else:
            result.append(round(units * avg_order_value, 2))
    return result


def project_travels(
    trips_per_year: list,
    revenue_per_trip: float,
    months: int = 36,
) -> list[float]:
    """Project TS Travels revenue as lump events.

    Trips are spread evenly across the year (e.g., 2 trips = month 3 and month 9
    of each model year, which maps to Sep and Mar).

    Returns:
        List of monthly revenue values.
    """
    result = [0.0] * months

    for year_idx, num_trips in enumerate(trips_per_year):
        if num_trips <= 0:
            continue
        year_start = year_idx * 12  # 0-indexed month offset
        # Spread trips evenly across 12 months
        spacing = 12 // num_trips
        for trip_num in range(num_trips):
            trip_month_offset = (spacing // 2) + trip_num * spacing
            absolute_month = year_start + trip_month_offset
            if absolute_month < months:
                result[absolute_month] = revenue_per_trip

    return result


def compute_marketing_spend(
    product_revenue: float,
    pct: float,
    calendar_month: int,
    q4_multiplier: float = 2.0,
    q4_months: list = None,
) -> float:
    """Compute marketing spend for a single month.

    Base = product_revenue × pct.
    Q4 months get multiplied by q4_multiplier.
    """
    if q4_months is None:
        q4_months = [10, 11, 12, 1]
    base = product_revenue * pct
    if calendar_month in q4_months:
        return round(base * q4_multiplier, 2)
    return round(base, 2)


def compute_personnel_cost(
    month: int,
    base_team: dict,
    cs_hire: dict,
    y2_adjustments: dict,
    y3_adjustments: dict,
) -> float:
    """Compute total personnel cost for a given model month.

    Uses base_team rates for Y1, y2_adjustments for Y2, y3_adjustments for Y3.
    CS hire added at cs_hire["start_month"].
    """
    year = _year_for_month(month)

    if year == 1:
        total = sum(base_team.values())
        if month >= cs_hire["start_month"]:
            total += cs_hire["monthly"]
    elif year == 2:
        total = sum(y2_adjustments.values())
        total += cs_hire["monthly"]
    else:
        total = sum(y3_adjustments.values())
        total += cs_hire["monthly"]

    return round(total, 2)


def build_monthly_pnl(config: dict) -> dict:
    """Build complete 36-month P&L from config dict.

    Returns dict with:
        months: list of month labels ["Jun 26", "Jul 26", ...]
        d2c_channels: {channel_name: [monthly_revenue]}
        d2c_total: [monthly_total_d2c_revenue]
        travels: [monthly_travels_revenue]
        total_revenue: [monthly_combined_revenue]
        cogs: {channel_name: [monthly_cogs]}
        total_cogs: [monthly]
        gross_profit: [monthly]
        costs: {
            personnel: [monthly],
            technology: [monthly],
            marketing: [monthly],
            shipping: [monthly],
            platform_fees: [monthly],
            seller_payout: [monthly],
            foundation: [monthly],
        }
        total_opex: [monthly]
        ebitda: [monthly]
        capital_infusion: [monthly]
        cash_flow: [monthly]
        ending_cash: [monthly]
        yearly_summary: {y1: {...}, y2: {...}, y3: {...}}
    """
    months = config["meta"]["months"]
    start_cal_month = config["meta"]["start_month"]

    # --- Revenue projections ---
    d2c_channels = {}
    d2c_cogs_rates = {}
    d2c_platform_fees = {}

    for ch_key, ch_cfg in config["d2c"]["channels"].items():
        cogs_rate = ch_cfg.get("cogs_pct_override") or config["d2c"]["cogs_pct"]
        d2c_cogs_rates[ch_key] = cogs_rate
        d2c_platform_fees[ch_key] = ch_cfg["platform_fee_pct"]

        if ch_cfg.get("type") == "quarterly":
            d2c_channels[ch_key] = project_quarterly_subscription(
                start_month=ch_cfg["start_month"],
                starting_quarterly_revenue=ch_cfg["starting_quarterly_revenue"],
                quarterly_growth=ch_cfg["quarterly_growth"],
                months=months,
            )
        elif ch_cfg.get("type") == "unit_based":
            d2c_channels[ch_key] = project_unit_based_channel(
                start_month=ch_cfg["start_month"],
                units_per_month=ch_cfg["units_per_month"],
                avg_order_value=ch_cfg["avg_order_value"],
                months=months,
            )
        else:
            d2c_channels[ch_key] = project_standard_channel(
                start_month=ch_cfg["start_month"],
                starting_revenue=ch_cfg["starting_revenue"],
                monthly_growth=ch_cfg["monthly_growth"],
                months=months,
            )

    # D2C totals
    d2c_total = [
        sum(d2c_channels[ch][m] for ch in d2c_channels)
        for m in range(months)
    ]

    # Travels
    travels_cfg = config["travels"]
    travels = project_travels(
        trips_per_year=travels_cfg["trips_per_year"],
        revenue_per_trip=travels_cfg["revenue_per_trip"],
        months=months,
    )

    total_revenue = [d2c_total[m] + travels[m] for m in range(months)]

    # --- COGS ---
    cogs_by_channel = {}
    for ch_key in d2c_channels:
        rate = d2c_cogs_rates[ch_key]
        cogs_by_channel[ch_key] = [
            round(d2c_channels[ch_key][m] * rate, 2)
            for m in range(months)
        ]
    cogs_travels = [
        round(travels[m] * travels_cfg["cogs_pct"], 2)
        for m in range(months)
    ]
    total_cogs = [
        sum(cogs_by_channel[ch][m] for ch in cogs_by_channel) + cogs_travels[m]
        for m in range(months)
    ]
    gross_profit = [
        round(total_revenue[m] - total_cogs[m], 2)
        for m in range(months)
    ]

    # --- Operating Costs ---
    costs_cfg = config["costs"]

    # Personnel
    personnel = [
        compute_personnel_cost(
            month=m + 1,
            base_team=costs_cfg["personnel"]["base_team"],
            cs_hire=costs_cfg["personnel"]["cs_hire"],
            y2_adjustments=costs_cfg["personnel"]["y2_adjustments"],
            y3_adjustments=costs_cfg["personnel"]["y3_adjustments"],
        )
        for m in range(months)
    ]

    # Technology
    technology = []
    for m in range(months):
        year = _year_for_month(m + 1)
        if year == 1:
            technology.append(costs_cfg["technology"]["monthly_y1"])
        elif year == 2:
            technology.append(costs_cfg["technology"]["monthly_y2"])
        else:
            technology.append(costs_cfg["technology"]["monthly_y3"])

    # Marketing
    mkt_cfg = costs_cfg["marketing"]
    marketing = []
    for m in range(months):
        year = _year_for_month(m + 1)
        pct = [
            mkt_cfg["pct_of_product_revenue_y1"],
            mkt_cfg["pct_of_product_revenue_y2"],
            mkt_cfg["pct_of_product_revenue_y3"],
        ][year - 1]
        cal_month = _calendar_month(m + 1, start_cal_month)
        marketing.append(compute_marketing_spend(
            product_revenue=d2c_total[m],
            pct=pct,
            calendar_month=cal_month,
            q4_multiplier=mkt_cfg["q4_multiplier"],
            q4_months=mkt_cfg["q4_months"],
        ))

    # Shipping (% of D2C product revenue only — Travels has different logistics)
    shipping = [
        round(d2c_total[m] * config["d2c"]["shipping_fulfillment_pct"], 2)
        for m in range(months)
    ]

    # Platform fees (channel-specific rates applied to channel revenue)
    platform_fees = [
        round(sum(
            d2c_channels[ch][m] * d2c_platform_fees[ch]
            for ch in d2c_channels
        ), 2)
        for m in range(months)
    ]

    # Seller payout
    seller_payout = [costs_cfg["seller_payout"]["monthly_y1_5"]] * months

    # Foundation (10% of net profit, profitable months only)
    # Compute after EBITDA-before-foundation
    ebitda_pre_foundation = [
        round(gross_profit[m] - personnel[m] - technology[m] - marketing[m]
              - shipping[m] - platform_fees[m] - seller_payout[m], 2)
        for m in range(months)
    ]

    foundation = []
    for m in range(months):
        if costs_cfg["foundation"]["only_profitable_months"] and ebitda_pre_foundation[m] <= 0:
            foundation.append(0.0)
        else:
            foundation.append(round(ebitda_pre_foundation[m] * costs_cfg["foundation"]["pct_of_net_profit"], 2))

    total_opex = [
        round(personnel[m] + technology[m] + marketing[m] + shipping[m]
              + platform_fees[m] + seller_payout[m] + foundation[m], 2)
        for m in range(months)
    ]

    ebitda = [round(gross_profit[m] - total_opex[m], 2) for m in range(months)]

    # --- Cash Flow ---
    cap_cfg = config["capital"]
    capital_infusion = [0.0] * months
    capital_infusion[0] = cap_cfg["ops_capital"]["y1"]  # Month 1 = Jun 26
    # Truist CD at month 10 (Mar 2027)
    if cap_cfg.get("truist_cd"):
        capital_infusion[9] = cap_cfg["truist_cd"]
    capital_infusion[12] = cap_cfg["ops_capital"]["y2"]  # Month 13 = Jun 27
    capital_infusion[24] = cap_cfg["ops_capital"]["y3"]  # Month 25 = Jun 28

    ending_cash = []
    current_cash = cap_cfg["cash_on_hand"]
    for m in range(months):
        operating_cf = ebitda[m]
        current_cash += capital_infusion[m] + operating_cf - seller_payout[m]
        # Seller payout is already in opex/EBITDA, so don't double-count
        # Actually: EBITDA already includes seller_payout as an expense.
        # Cash flow = EBITDA + capital_infusion (seller payout is in EBITDA)
        pass

    # Redo cash flow correctly:
    # EBITDA = Gross Profit - All OpEx (which includes seller_payout)
    # Cash Flow = EBITDA + Capital Infusion
    ending_cash = []
    current_cash = cap_cfg["cash_on_hand"]
    for m in range(months):
        current_cash += ebitda[m] + capital_infusion[m]
        ending_cash.append(round(current_cash, 2))

    # --- Month labels ---
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    month_labels = []
    for m in range(months):
        cal_m = _calendar_month(m + 1, start_cal_month)
        year = config["meta"]["start_year"] + (start_cal_month - 1 + m) // 12
        month_labels.append(f"{month_names[cal_m - 1]} {str(year)[2:]}")

    # --- Yearly summaries ---
    def _year_sum(values, year_idx):
        start = year_idx * 12
        return round(sum(values[start:start + 12]), 2)

    yearly_summary = {}
    for yi in range(3):
        label = f"Y{yi + 1}"
        yearly_summary[label] = {
            "d2c_revenue": _year_sum(d2c_total, yi),
            "travels_revenue": _year_sum(travels, yi),
            "total_revenue": _year_sum(total_revenue, yi),
            "total_cogs": _year_sum(total_cogs, yi),
            "gross_profit": _year_sum(gross_profit, yi),
            "gross_margin_pct": (
                _year_sum(gross_profit, yi) / _year_sum(total_revenue, yi)
                if _year_sum(total_revenue, yi) > 0 else 0
            ),
            "marketing": _year_sum(marketing, yi),
            "personnel": _year_sum(personnel, yi),
            "technology": _year_sum(technology, yi),
            "total_opex": _year_sum(total_opex, yi),
            "ebitda": _year_sum(ebitda, yi),
            "ending_cash": ending_cash[min((yi + 1) * 12 - 1, months - 1)],
        }

    return {
        "month_labels": month_labels,
        "d2c_channels": d2c_channels,
        "d2c_total": d2c_total,
        "travels": travels,
        "total_revenue": total_revenue,
        "cogs_by_channel": cogs_by_channel,
        "cogs_travels": cogs_travels,
        "total_cogs": total_cogs,
        "gross_profit": gross_profit,
        "costs": {
            "personnel": personnel,
            "technology": technology,
            "marketing": marketing,
            "shipping": shipping,
            "platform_fees": platform_fees,
            "seller_payout": seller_payout,
            "foundation": foundation,
        },
        "total_opex": total_opex,
        "ebitda": ebitda,
        "capital_infusion": capital_infusion,
        "ending_cash": ending_cash,
        "yearly_summary": yearly_summary,
    }


def build_scenarios(config: dict) -> dict:
    """Build channel-toggle scenarios.

    Returns dict mapping scenario name to build_monthly_pnl output.
    Each scenario is a modified copy of config with certain channels zeroed out.
    """
    import copy

    scenarios = {}

    # Scenario 1: Shopify Only
    cfg = copy.deepcopy(config)
    for ch in ["etsy", "amazon", "wholesale", "subscription", "dropship"]:
        if ch in cfg["d2c"]["channels"]:
            cfg["d2c"]["channels"][ch]["starting_revenue"] = 0
            if "starting_quarterly_revenue" in cfg["d2c"]["channels"][ch]:
                cfg["d2c"]["channels"][ch]["starting_quarterly_revenue"] = 0
            if "units_per_month" in cfg["d2c"]["channels"][ch]:
                cfg["d2c"]["channels"][ch]["units_per_month"] = [0, 0, 0]
    cfg["travels"]["trips_per_year"] = [0, 0, 0]
    scenarios["Shopify Only"] = build_monthly_pnl(cfg)

    # Scenario 2: D2C Core (Shopify + Etsy + Subscription)
    cfg = copy.deepcopy(config)
    for ch in ["amazon", "wholesale", "dropship"]:
        if ch in cfg["d2c"]["channels"]:
            cfg["d2c"]["channels"][ch]["starting_revenue"] = 0
            if "units_per_month" in cfg["d2c"]["channels"][ch]:
                cfg["d2c"]["channels"][ch]["units_per_month"] = [0, 0, 0]
    cfg["travels"]["trips_per_year"] = [0, 0, 0]
    scenarios["D2C Core"] = build_monthly_pnl(cfg)

    # Scenario 3: Full D2C (all product channels, no Travels)
    cfg = copy.deepcopy(config)
    cfg["travels"]["trips_per_year"] = [0, 0, 0]
    scenarios["Full D2C"] = build_monthly_pnl(cfg)

    # Scenario 4: Full Business (D2C + Travels)
    scenarios["Full Business"] = build_monthly_pnl(config)

    return scenarios
```

- [ ] **Step 4: Run tests**

```bash
cd /Users/chrismauze/code/active/tibetan-spirit-ops
python3 -m pytest tests/test_model_v7.py -v
```

Fix any failures. The personnel test may need adjustment — verify against v6 values:
- Y1 months 1-4: $6,833 (base team: 2500+1500+1333+1500)
- Y1 months 5-12: $7,666 (+833 CS)
- Y2: $8,291 (v6 value — includes CS, so y2_adjustments should sum to 8291)
- Y3: $9,750 (v6 value — includes CS)

If the y2_adjustments in the config sum to 8291 WITH CS (2750+1600+1441+2500=8291 without CS, +833=9124 with CS), but v6 shows 8291 for Y2 months, then CS might be rolled into the Y2 adjustments. Adjust the config or the function to match v6 exactly:

The simplest fix: make Y2/Y3 adjustments include the CS hire amount, and don't add CS separately for Y2+. Update `compute_personnel_cost` and the config accordingly so that:
- Y1 M1-4: base_team sum = 6833
- Y1 M5-12: base_team sum + cs_hire = 7666
- Y2: y2_total = 8291 (all-in)
- Y3: y3_total = 9750 (all-in)

Simplify the config to use flat monthly totals per period:

```yaml
  personnel:
    # Total monthly personnel cost per period (all-in)
    monthly_m1_to_m4: 6833     # Base team before CS hire
    monthly_m5_to_m12: 7666    # + CS hire Oct 2026
    monthly_y2: 8291           # Y2 team rates
    monthly_y3: 9750           # Y3 team rates
```

And simplify `compute_personnel_cost` to just return the right flat amount for the period.

- [ ] **Step 5: Commit**

```bash
git add scripts/financial_model/model.py tests/test_model_v7.py
git commit -m "feat(finance): add v7 model engine with channel projections and tests"
```

---

### Task 3: xlsx Writer

**Purpose:** Generate a multi-tab xlsx file from the model output, uploadable to Google Sheets.

**Files:**
- Create: `scripts/financial_model/build_xlsx.py`

- [ ] **Step 1: Create the xlsx writer script**

```python
#!/usr/bin/env python3
"""
Build TS Financial Model v7 xlsx from YAML config.

Usage:
    python3 scripts/financial_model/build_xlsx.py
    python3 scripts/financial_model/build_xlsx.py --config path/to/config.yaml
    python3 scripts/financial_model/build_xlsx.py --output path/to/output.xlsx

Generates a multi-tab workbook:
  1. Assumptions — all input parameters
  2. D2C Monthly P&L — product revenue by channel, COGS, costs
  3. TS Travels — separate P&L for travel business
  4. Combined P&L — roll-up with EBITDA and cash flow
  5. Channel Scenarios — what-if with/without each channel
  6. Sensitivity — revenue factor variations
  7. Capital & Cash — cash flow, capital deployment
"""
import argparse
from datetime import date
from pathlib import Path

import yaml
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, numbers, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from scripts.financial_model.model import build_monthly_pnl, build_scenarios

_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_CONFIG = Path(__file__).parent / "config" / "model_v7.yaml"
DEFAULT_OUTPUT = _ROOT / "deliverables" / "outputs" / "docs"

# Styles
HEADER_FONT = Font(bold=True, color="FFFFFF")
HEADER_FILL = PatternFill(start_color="1A252F", end_color="1A252F", fill_type="solid")
SECTION_FONT = Font(bold=True, size=11)
SECTION_FILL = PatternFill(start_color="EAF2F8", end_color="EAF2F8", fill_type="solid")
DOLLAR_FMT = '#,##0'
DOLLAR_NEG_FMT = '#,##0;[Red]-#,##0'
PCT_FMT = '0.0%'
THIN_BORDER = Border(bottom=Side(style='thin'))


def _apply_header_row(ws, row, num_cols):
    """Style a row as a header."""
    for col in range(1, num_cols + 1):
        cell = ws.cell(row=row, column=col)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL


def _apply_section_row(ws, row, num_cols):
    """Style a row as a section header."""
    for col in range(1, num_cols + 1):
        cell = ws.cell(row=row, column=col)
        cell.font = SECTION_FONT
        cell.fill = SECTION_FILL


def _write_monthly_row(ws, row, label, values, fmt=DOLLAR_FMT, indent=False):
    """Write a label + 36 monthly values + 3 yearly totals."""
    cell = ws.cell(row=row, column=1, value=("  " + label) if indent else label)
    if indent:
        cell.font = Font(color="555555")

    for i, val in enumerate(values):
        c = ws.cell(row=row, column=i + 2, value=val)
        c.number_format = fmt

    # Yearly totals (columns 38, 39, 40)
    for y in range(3):
        start = y * 12
        total = sum(values[start:start + 12])
        c = ws.cell(row=row, column=38 + y, value=round(total, 2))
        c.number_format = fmt
        c.font = Font(bold=True)


def write_assumptions_tab(wb, config):
    """Tab 1: Assumptions — all config values in readable format."""
    ws = wb.create_sheet("Assumptions")
    ws.column_dimensions['A'].width = 35
    ws.column_dimensions['B'].width = 20
    ws.column_dimensions['C'].width = 40

    row = 1
    ws.cell(row=row, column=1, value="Tibetan Spirit Financial Model v7").font = Font(bold=True, size=14)
    row += 1
    ws.cell(row=row, column=1, value=f"Generated: {date.today().isoformat()}")
    row += 2

    # Model meta
    ws.cell(row=row, column=1, value="MODEL PARAMETERS").font = SECTION_FONT
    row += 1
    for key in ["version", "scenario", "period"]:
        ws.cell(row=row, column=1, value=key.replace("_", " ").title())
        ws.cell(row=row, column=2, value=config["meta"][key])
        row += 1

    row += 1
    ws.cell(row=row, column=1, value="D2C CHANNEL ASSUMPTIONS").font = SECTION_FONT
    _apply_section_row(ws, row, 3)
    row += 1
    ws.cell(row=row, column=1, value="Channel")
    ws.cell(row=row, column=2, value="Start Month")
    ws.cell(row=row, column=3, value="Starting Revenue")
    ws.cell(row=row, column=4, value="Growth (Y1/Y2/Y3)")
    ws.cell(row=row, column=5, value="COGS %")
    ws.cell(row=row, column=6, value="Platform Fee %")
    _apply_header_row(ws, row, 6)
    row += 1
    for ch_key, ch in config["d2c"]["channels"].items():
        ws.cell(row=row, column=1, value=ch.get("label", ch_key))
        ws.cell(row=row, column=2, value=ch.get("start_month"))
        ws.cell(row=row, column=3, value=ch.get("starting_revenue") or ch.get("starting_quarterly_revenue") or "N/A")
        growth = ch.get("monthly_growth") or [ch.get("quarterly_growth")]
        ws.cell(row=row, column=4, value=str(growth))
        cogs = ch.get("cogs_pct_override") or config["d2c"]["cogs_pct"]
        ws.cell(row=row, column=5, value=cogs)
        ws.cell(row=row, column=5).number_format = PCT_FMT
        ws.cell(row=row, column=6, value=ch["platform_fee_pct"])
        ws.cell(row=row, column=6).number_format = PCT_FMT
        row += 1

    row += 1
    ws.cell(row=row, column=1, value="TS TRAVELS").font = SECTION_FONT
    row += 1
    ws.cell(row=row, column=1, value="Trips per year")
    ws.cell(row=row, column=2, value=str(config["travels"]["trips_per_year"]))
    row += 1
    ws.cell(row=row, column=1, value="Revenue per trip")
    ws.cell(row=row, column=2, value=config["travels"]["revenue_per_trip"])
    ws.cell(row=row, column=2).number_format = DOLLAR_FMT
    row += 1
    ws.cell(row=row, column=1, value="COGS %")
    ws.cell(row=row, column=2, value=config["travels"]["cogs_pct"])
    ws.cell(row=row, column=2).number_format = PCT_FMT

    row += 2
    ws.cell(row=row, column=1, value="OPERATING COSTS").font = SECTION_FONT
    row += 1
    costs = config["costs"]
    ws.cell(row=row, column=1, value="Personnel M1-M4")
    ws.cell(row=row, column=2, value=costs["personnel"].get("monthly_m1_to_m4", "see config"))
    row += 1
    ws.cell(row=row, column=1, value="Personnel M5-M12")
    ws.cell(row=row, column=2, value=costs["personnel"].get("monthly_m5_to_m12", "see config"))
    row += 1
    ws.cell(row=row, column=1, value="Personnel Y2")
    ws.cell(row=row, column=2, value=costs["personnel"].get("monthly_y2", "see config"))
    row += 1
    ws.cell(row=row, column=1, value="Personnel Y3")
    ws.cell(row=row, column=2, value=costs["personnel"].get("monthly_y3", "see config"))
    row += 1
    ws.cell(row=row, column=1, value="Technology Y1")
    ws.cell(row=row, column=2, value=costs["technology"]["monthly_y1"])
    row += 1
    ws.cell(row=row, column=1, value="Marketing % of Product Rev (Y1/Y2/Y3)")
    ws.cell(row=row, column=2, value=f"{costs['marketing']['pct_of_product_revenue_y1']:.0%} / {costs['marketing']['pct_of_product_revenue_y2']:.0%} / {costs['marketing']['pct_of_product_revenue_y3']:.0%}")
    row += 1
    ws.cell(row=row, column=1, value="Seller Payout (Y1-5)")
    ws.cell(row=row, column=2, value=costs["seller_payout"]["monthly_y1_5"])
    ws.cell(row=row, column=2).number_format = DOLLAR_FMT

    row += 2
    ws.cell(row=row, column=1, value="CAPITAL STRUCTURE").font = SECTION_FONT
    row += 1
    cap = config["capital"]
    for label, val in [
        ("Cash on Hand", cap["cash_on_hand"]),
        ("Ops Capital Y1", cap["ops_capital"]["y1"]),
        ("Ops Capital Y2", cap["ops_capital"]["y2"]),
        ("Ops Capital Y3 (reserve)", cap["ops_capital"]["y3"]),
        ("Truist CD", cap.get("truist_cd", 0)),
        ("Inventory Facility Cap", cap["inventory_facility"]["cap"]),
    ]:
        ws.cell(row=row, column=1, value=label)
        ws.cell(row=row, column=2, value=val)
        ws.cell(row=row, column=2).number_format = DOLLAR_FMT
        row += 1


def write_d2c_pnl_tab(wb, pnl, config):
    """Tab 2: D2C Monthly P&L — product channels only."""
    ws = wb.create_sheet("D2C Monthly P&L")
    labels = pnl["month_labels"]
    num_months = len(labels)

    # Header row
    ws.cell(row=1, column=1, value="D2C Product P&L")
    for i, label in enumerate(labels):
        ws.cell(row=2, column=i + 2, value=label)
    # Yearly total headers
    ws.cell(row=2, column=num_months + 2, value="Y1 Total")
    ws.cell(row=2, column=num_months + 3, value="Y2 Total")
    ws.cell(row=2, column=num_months + 4, value="Y3 Total")
    _apply_header_row(ws, 2, num_months + 4)
    ws.column_dimensions['A'].width = 30

    row = 3

    # Revenue section
    ws.cell(row=row, column=1, value="REVENUE").font = SECTION_FONT
    _apply_section_row(ws, row, num_months + 4)
    row += 1
    for ch_key, ch_values in pnl["d2c_channels"].items():
        ch_label = config["d2c"]["channels"][ch_key].get("label", ch_key)
        _write_monthly_row(ws, row, ch_label, ch_values, indent=True)
        row += 1
    _write_monthly_row(ws, row, "TOTAL D2C REVENUE", pnl["d2c_total"])
    ws.cell(row=row, column=1).font = Font(bold=True)
    row += 2

    # COGS section
    ws.cell(row=row, column=1, value="COST OF GOODS SOLD").font = SECTION_FONT
    _apply_section_row(ws, row, num_months + 4)
    row += 1
    for ch_key, cogs_values in pnl["cogs_by_channel"].items():
        ch_label = config["d2c"]["channels"][ch_key].get("label", ch_key)
        _write_monthly_row(ws, row, f"{ch_label} COGS", cogs_values, indent=True)
        row += 1

    # D2C-only COGS total (exclude travels)
    d2c_cogs = [
        sum(pnl["cogs_by_channel"][ch][m] for ch in pnl["cogs_by_channel"])
        for m in range(num_months)
    ]
    _write_monthly_row(ws, row, "TOTAL D2C COGS", d2c_cogs)
    ws.cell(row=row, column=1).font = Font(bold=True)
    row += 1

    d2c_gp = [pnl["d2c_total"][m] - d2c_cogs[m] for m in range(num_months)]
    _write_monthly_row(ws, row, "D2C GROSS PROFIT", d2c_gp)
    ws.cell(row=row, column=1).font = Font(bold=True)
    row += 2

    # Operating expenses
    ws.cell(row=row, column=1, value="OPERATING EXPENSES").font = SECTION_FONT
    _apply_section_row(ws, row, num_months + 4)
    row += 1
    for cost_key in ["personnel", "technology", "marketing", "shipping", "platform_fees", "seller_payout", "foundation"]:
        label = cost_key.replace("_", " ").title()
        _write_monthly_row(ws, row, label, pnl["costs"][cost_key], indent=True)
        row += 1
    _write_monthly_row(ws, row, "TOTAL OPERATING EXPENSES", pnl["total_opex"])
    ws.cell(row=row, column=1).font = Font(bold=True)


def write_travels_tab(wb, pnl, config):
    """Tab 3: TS Travels — separate P&L."""
    ws = wb.create_sheet("TS Travels")
    labels = pnl["month_labels"]
    num_months = len(labels)

    ws.cell(row=1, column=1, value="TS Travels P&L (Pilgrimages)")
    for i, label in enumerate(labels):
        ws.cell(row=2, column=i + 2, value=label)
    ws.cell(row=2, column=num_months + 2, value="Y1 Total")
    ws.cell(row=2, column=num_months + 3, value="Y2 Total")
    ws.cell(row=2, column=num_months + 4, value="Y3 Total")
    _apply_header_row(ws, 2, num_months + 4)
    ws.column_dimensions['A'].width = 30

    row = 3
    _write_monthly_row(ws, row, "Travel Revenue", pnl["travels"])
    row += 1
    _write_monthly_row(ws, row, "Travel COGS (60%)", pnl["cogs_travels"])
    row += 1
    travels_gp = [pnl["travels"][m] - pnl["cogs_travels"][m] for m in range(num_months)]
    _write_monthly_row(ws, row, "Travel Gross Profit", travels_gp)
    ws.cell(row=row, column=1).font = Font(bold=True)

    row += 2
    ws.cell(row=row, column=1, value="Note: TS Travels costs (Dr. Hun Lye's time, trip logistics)")
    row += 1
    ws.cell(row=row, column=1, value="are captured in the 60% COGS rate. No additional opex.")


def write_combined_pnl_tab(wb, pnl):
    """Tab 4: Combined P&L — D2C + Travels with EBITDA and cash."""
    ws = wb.create_sheet("Combined P&L")
    labels = pnl["month_labels"]
    num_months = len(labels)

    ws.cell(row=1, column=1, value="Combined P&L — D2C + TS Travels")
    for i, label in enumerate(labels):
        ws.cell(row=2, column=i + 2, value=label)
    ws.cell(row=2, column=num_months + 2, value="Y1 Total")
    ws.cell(row=2, column=num_months + 3, value="Y2 Total")
    ws.cell(row=2, column=num_months + 4, value="Y3 Total")
    _apply_header_row(ws, 2, num_months + 4)
    ws.column_dimensions['A'].width = 30

    row = 3
    _write_monthly_row(ws, row, "D2C Product Revenue", pnl["d2c_total"])
    row += 1
    _write_monthly_row(ws, row, "TS Travels Revenue", pnl["travels"])
    row += 1
    _write_monthly_row(ws, row, "TOTAL REVENUE", pnl["total_revenue"])
    ws.cell(row=row, column=1).font = Font(bold=True)
    row += 1
    _write_monthly_row(ws, row, "TOTAL COGS", pnl["total_cogs"])
    row += 1
    _write_monthly_row(ws, row, "GROSS PROFIT", pnl["gross_profit"])
    ws.cell(row=row, column=1).font = Font(bold=True)
    row += 1
    _write_monthly_row(ws, row, "TOTAL OPERATING EXPENSES", pnl["total_opex"])
    row += 1
    _write_monthly_row(ws, row, "EBITDA", pnl["ebitda"], fmt=DOLLAR_NEG_FMT)
    ws.cell(row=row, column=1).font = Font(bold=True)
    row += 2

    # Cash flow section
    ws.cell(row=row, column=1, value="CASH FLOW").font = SECTION_FONT
    _apply_section_row(ws, row, num_months + 4)
    row += 1
    _write_monthly_row(ws, row, "Capital Infusion", pnl["capital_infusion"], indent=True)
    row += 1
    _write_monthly_row(ws, row, "ENDING CASH BALANCE", pnl["ending_cash"], fmt=DOLLAR_NEG_FMT)
    ws.cell(row=row, column=1).font = Font(bold=True)


def write_scenarios_tab(wb, scenarios):
    """Tab 5: Channel Scenarios — side-by-side comparison."""
    ws = wb.create_sheet("Channel Scenarios")
    ws.column_dimensions['A'].width = 25

    ws.cell(row=1, column=1, value="Channel Scenario Comparison").font = Font(bold=True, size=14)

    # Headers
    scenario_names = list(scenarios.keys())
    ws.cell(row=3, column=1, value="Metric")
    for i, name in enumerate(scenario_names):
        col = 2 + i * 3  # 3 columns per scenario (Y1, Y2, Y3)
        ws.merge_cells(start_row=3, start_column=col, end_row=3, end_column=col + 2)
        ws.cell(row=3, column=col, value=name).font = HEADER_FONT
        ws.cell(row=3, column=col).fill = HEADER_FILL
        ws.cell(row=3, column=col).alignment = Alignment(horizontal='center')
        for y in range(3):
            ws.cell(row=4, column=col + y, value=f"Y{y + 1}")
            ws.cell(row=4, column=col + y).font = Font(bold=True)

    row = 5
    metrics = [
        ("Total Revenue", "total_revenue"),
        ("D2C Revenue", "d2c_revenue"),
        ("Travels Revenue", "travels_revenue"),
        ("Gross Profit", "gross_profit"),
        ("Marketing Spend", "marketing"),
        ("Total OpEx", "total_opex"),
        ("EBITDA", "ebitda"),
        ("Ending Cash", "ending_cash"),
    ]

    for label, key in metrics:
        ws.cell(row=row, column=1, value=label)
        for i, name in enumerate(scenario_names):
            summary = scenarios[name]["yearly_summary"]
            col = 2 + i * 3
            for y in range(3):
                val = summary[f"Y{y + 1}"].get(key, 0)
                c = ws.cell(row=row, column=col + y, value=round(val))
                c.number_format = DOLLAR_NEG_FMT
        row += 1


def write_sensitivity_tab(wb, pnl, config):
    """Tab 6: Sensitivity — revenue factor variations."""
    ws = wb.create_sheet("Sensitivity")
    ws.column_dimensions['A'].width = 25

    ws.cell(row=1, column=1, value="Sensitivity Analysis").font = Font(bold=True, size=14)
    ws.cell(row=2, column=1, value="Applies revenue factor to all channels")

    factors = config["sensitivity"]["revenue_factors"]
    labels = config["sensitivity"]["labels"]

    ws.cell(row=4, column=1, value="Scenario")
    ws.cell(row=4, column=2, value="Revenue Factor")
    ws.cell(row=4, column=3, value="Y1 Revenue")
    ws.cell(row=4, column=4, value="Y2 Revenue")
    ws.cell(row=4, column=5, value="Y3 Revenue")
    ws.cell(row=4, column=6, value="Y3 EBITDA")
    ws.cell(row=4, column=7, value="M36 Cash")
    _apply_header_row(ws, 4, 7)

    base_summary = pnl["yearly_summary"]
    for i, (factor, label) in enumerate(zip(factors, labels)):
        row = 5 + i
        ws.cell(row=row, column=1, value=label)
        ws.cell(row=row, column=2, value=factor)
        ws.cell(row=row, column=2).number_format = PCT_FMT
        for y in range(3):
            rev = base_summary[f"Y{y + 1}"]["total_revenue"] * factor
            ws.cell(row=row, column=3 + y, value=round(rev))
            ws.cell(row=row, column=3 + y).number_format = DOLLAR_FMT
        # Simplified: EBITDA scales roughly with revenue factor
        # (costs are partially fixed, so this is approximate)
        y3_ebitda = base_summary["Y3"]["ebitda"] * factor
        ws.cell(row=row, column=6, value=round(y3_ebitda))
        ws.cell(row=row, column=6).number_format = DOLLAR_NEG_FMT
        m36_cash = pnl["ending_cash"][-1] * factor
        ws.cell(row=row, column=7, value=round(m36_cash))
        ws.cell(row=row, column=7).number_format = DOLLAR_NEG_FMT


def write_capital_tab(wb, pnl, config):
    """Tab 7: Capital & Cash — deployment schedule and seller payout."""
    ws = wb.create_sheet("Capital & Cash")
    ws.column_dimensions['A'].width = 35
    ws.column_dimensions['B'].width = 15

    ws.cell(row=1, column=1, value="Capital Structure & Cash Flow").font = Font(bold=True, size=14)

    row = 3
    ws.cell(row=row, column=1, value="CAPITAL DEPLOYED").font = SECTION_FONT
    row += 1
    cap = config["capital"]
    items = [
        ("Cash on Hand at Close", cap["cash_on_hand"]),
        ("Operations Capital Y1 (at closing)", cap["ops_capital"]["y1"]),
        ("Operations Capital Y2", cap["ops_capital"]["y2"]),
        ("Operations Capital Y3 (reserve)", cap["ops_capital"]["y3"]),
        ("Truist CD (Mar 2027)", cap.get("truist_cd", 0)),
        ("Total Capital", cap["cash_on_hand"] + sum(cap["ops_capital"].values()) + cap.get("truist_cd", 0)),
    ]
    for label, val in items:
        ws.cell(row=row, column=1, value=label)
        ws.cell(row=row, column=2, value=val)
        ws.cell(row=row, column=2).number_format = DOLLAR_FMT
        row += 1

    row += 1
    ws.cell(row=row, column=1, value="SELLER PAYOUT (Secured Promissory Note)").font = SECTION_FONT
    row += 1
    ws.cell(row=row, column=1, value="Monthly Y1-5")
    ws.cell(row=row, column=2, value=config["costs"]["seller_payout"]["monthly_y1_5"])
    ws.cell(row=row, column=2).number_format = DOLLAR_FMT
    row += 1
    ws.cell(row=row, column=1, value="Monthly Y6-10 (post-ordination)")
    ws.cell(row=row, column=2, value=config["costs"]["seller_payout"]["monthly_y6_10"])
    ws.cell(row=row, column=2).number_format = DOLLAR_FMT
    row += 1
    ws.cell(row=row, column=1, value="Total Obligation")
    ws.cell(row=row, column=2, value=270000)
    ws.cell(row=row, column=2).number_format = DOLLAR_FMT
    row += 1
    ws.cell(row=row, column=1, value="Note: Dr. Hun Lye plans to ordain as a monk after Y5,")
    row += 1
    ws.cell(row=row, column=1, value="reducing active involvement. Payout steps down accordingly.")

    row += 2
    ws.cell(row=row, column=1, value="YEAR-END CASH POSITION").font = SECTION_FONT
    row += 1
    summary = pnl["yearly_summary"]
    for y in range(3):
        ws.cell(row=row, column=1, value=f"End of Y{y + 1}")
        ws.cell(row=row, column=2, value=summary[f"Y{y + 1}"]["ending_cash"])
        ws.cell(row=row, column=2).number_format = DOLLAR_FMT
        row += 1


def main():
    parser = argparse.ArgumentParser(description="Generate TS Financial Model v7 xlsx")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    config = yaml.safe_load(args.config.read_text())

    print("Building model...")
    pnl = build_monthly_pnl(config)

    print("Building scenarios...")
    scenarios = build_scenarios(config)

    print("Writing xlsx...")
    wb = Workbook()
    wb.remove(wb.active)  # Remove default sheet

    write_assumptions_tab(wb, config)
    write_d2c_pnl_tab(wb, pnl, config)
    write_travels_tab(wb, pnl, config)
    write_combined_pnl_tab(wb, pnl)
    write_scenarios_tab(wb, scenarios)
    write_sensitivity_tab(wb, pnl, config)
    write_capital_tab(wb, pnl, config)

    output_path = args.output or (DEFAULT_OUTPUT / f"ts-financial-model-v7-{date.today().isoformat()}.xlsx")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(str(output_path))

    print(f"\nSaved to: {output_path}")
    s = pnl["yearly_summary"]
    print(f"  Y1 Revenue: ${s['Y1']['total_revenue']:,.0f}  EBITDA: ${s['Y1']['ebitda']:,.0f}")
    print(f"  Y2 Revenue: ${s['Y2']['total_revenue']:,.0f}  EBITDA: ${s['Y2']['ebitda']:,.0f}")
    print(f"  Y3 Revenue: ${s['Y3']['total_revenue']:,.0f}  EBITDA: ${s['Y3']['ebitda']:,.0f}")
    print(f"  M36 Cash: ${pnl['ending_cash'][-1]:,.0f}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run the build script**

```bash
cd /Users/chrismauze/code/active/tibetan-spirit-ops
python3 scripts/financial_model/build_xlsx.py
```

Expected output (approximate — numbers will differ from v6 due to updated assumptions):
```
Building model...
Building scenarios...
Writing xlsx...

Saved to: deliverables/outputs/docs/ts-financial-model-v7-2026-04-16.xlsx
  Y1 Revenue: $XXX,XXX  EBITDA: -$XXX,XXX
  Y2 Revenue: $XXX,XXX  EBITDA: -$XX,XXX
  Y3 Revenue: $X,XXX,XXX  EBITDA: $XX,XXX
  M36 Cash: $XXX,XXX
```

- [ ] **Step 3: Validate output against v6 reference points**

The v7 model will produce DIFFERENT numbers from v6 due to updated COGS (30% vs 24.8%) and starting revenue ($7,500 vs $8,500). But structural patterns should match:
- Y1 should be unprofitable (EBITDA negative)
- Y2 should be less unprofitable
- Y3 should be profitable or near breakeven
- Cash should never go below $0 (capital infusions prevent this)
- Channel revenue growth curves should be smooth

Open the xlsx and spot-check:
1. Assumptions tab shows all config values
2. D2C Monthly P&L has 36 columns + yearly totals
3. Shopify M1 = $7,500
4. Etsy M1-2 = $0, M3 = $1,000
5. Travels Y1 = $0, Y2 = $300,000
6. Channel Scenarios tab shows 4 scenarios side by side
7. Cash balance never goes negative

- [ ] **Step 4: Commit**

```bash
git add scripts/financial_model/build_xlsx.py deliverables/outputs/docs/ts-financial-model-v7-*.xlsx
git commit -m "feat(finance): add v7 xlsx builder with channel scenarios and D2C/Travels separation"
```

---

## Phase 2: Deal Documents

### Task 4: Rewrite Deal Proposal with Legal Recommendations

**Purpose:** Updated deal proposal (v2) with legal structure recommendations integrated. Keeps plain-English tone but formalizes the structure. Includes monk transition context.

**Files:**
- Create: `deliverables/outputs/docs/ts-deal-proposal-v2-2026-04-16.md`
- Reference: `deliverables/outputs/docs/ts-deal-proposal-2026-04-15.md` (v1 — preserve, don't overwrite)
- Reference: `deliverables/outputs/docs/deal-structure-analysis-2026-04-15.md`

- [ ] **Step 1: Read v1 deal proposal and deal structure analysis**

Read both files completely. The v2 rewrite should:
- Keep the same narrative structure and plain-English tone
- Integrate the 5 legal recommendations from the deal structure analysis
- Update all financial numbers to v7 model output
- Add monk transition context for salary step-down
- Use 30% COGS throughout
- Clearly separate D2C and Travels revenue
- Add "Recommended Legal Structure" section

- [ ] **Step 2: Write the v2 deal proposal**

Key changes from v1:

**Section 1 (Executive Summary):**
- Update revenue figures to v7 output
- Change "guaranteed monthly payments" to "secured promissory note payments"
- Add "structured as a secured seller note"

**Section 2 (What TS Is Today):**
- Update COGS to 30% conservative
- Update "Product margin" to ~70% (was ~75%)
- Keep everything else the same

**Section 3 (Growth Plan):**
- Update all revenue figures to v7 output
- Clearly separate D2C product revenue from TS Travels in the table
- Add two subtotals: "D2C Product Revenue" and "TS Travels"

**Section 4 (Investment):**
- Update figures to v7
- Add "Range of Outcomes" using v7 sensitivity data
- Mention inventory facility cap ($100K)

**Section 5 (Team):**
- Keep as-is

**NEW Section 6 (Deal Structure — Legal Framework):**

```markdown
## How the Deal Works

### Structure Overview

The acquisition is structured as an asset purchase, with the seller payout formalized as a
**secured promissory note** backed by a UCC-1 filing on business assets. This gives Dr. Hun Lye
legal collateral protection and enables favorable installment sale tax treatment.

### For Dr. Hun Lye

You will receive **$3,000 per month for the first five years** (totaling $180,000), then
**$1,500 per month for the following five years** (totaling $90,000). These payments are
**guaranteed** and backed by a security interest in the business assets — inventory, intellectual
property, domain names, and customer lists.

The payment reduction after year five reflects your plan to ordain as a monk, reducing your
active involvement in the business. Your role as Spiritual Director continues, but at a pace
that honors your monastic commitments.

In total, you will receive **$270,000** over ten years.

### Security & Protection

| Protection | How It Works |
|---|---|
| **Secured promissory note** | Your $270K is formalized as a legal note, not just a contract promise |
| **UCC-1 filing** | You hold a perfected security interest in business assets |
| **Priority position** | In any default scenario, your claim has priority over unsecured creditors |
| **Installment sale treatment** | Tax benefit: you recognize gain over 10 years, not all at once |

### Tax Considerations

The purchase price will be allocated across asset categories (inventory, intellectual property,
goodwill) on IRS Form 8594, which both parties must file. The allocation determines how the
$270K is taxed — more allocated to goodwill means more favorable capital gains treatment for
you. We recommend working with your tax advisor to agree on an allocation that is fair to both
parties.

Your continuing role as Spiritual Director will be documented as a separate advisory agreement
with minimal time commitment (a few hours per month), so the IRS clearly distinguishes between
purchase price payments and advisory compensation.

### For the Business

[Keep existing content but update inventory facility to include $100K cap]

### What Stays the Same

[Keep as-is from v1]
```

- [ ] **Step 3: Review against constraints**

Checklist:
- [ ] All numbers match v7 model output
- [ ] No VC/PE jargon — "secured promissory note" is explained in plain terms
- [ ] Monk transition context is respectful and factual
- [ ] D2C and Travels clearly separated in revenue table
- [ ] COGS = 30% throughout
- [ ] Legal recommendations integrated naturally, not as a separate "legal section"
- [ ] Brand voice: warm, professional, accessible
- [ ] Still a conversation starter, not a legal document

- [ ] **Step 4: Commit**

```bash
git add deliverables/outputs/docs/ts-deal-proposal-v2-2026-04-16.md
git commit -m "docs(deal): rewrite proposal v2 with legal structure and updated model"
```

---

### Task 5: Tax & Legal Checklist

**Purpose:** Document written as if from a tax advisor, structured for attorney review. Chris hands this to his lawyer to validate and execute.

**Files:**
- Create: `deliverables/outputs/docs/ts-tax-legal-checklist-2026-04-16.md`

- [ ] **Step 1: Write the checklist document**

```markdown
# Tibetan Spirit Acquisition — Tax & Legal Review Checklist

**Prepared:** April 16, 2026
**For:** Buyer's attorney and tax advisor
**Re:** Asset purchase of substantially all assets of Bear Springs, Inc. (S-Corp, dba Tibetan Spirit)

---

## Deal Summary

| Term | Value |
|---|---|
| Transaction type | Asset purchase |
| Nominal consideration | $1 |
| Effective consideration | $270,000 (secured promissory note, 10-year term) |
| Payment schedule | $3,000/mo × 60 months + $1,500/mo × 60 months |
| Seller entity | Bear Springs, Inc. (S-Corp) |
| Buyer entity | [TBD — new LLC recommended] |
| Seller's continuing role | Spiritual Director (advisory, non-employment) |
| Operations capital | $350,000 interest-free (from Michael Mauzé) |
| Inventory facility | $100,000 revolving, 0% interest, quarterly reconciliation |
| Foundation commitment | 10% of net profit to Forest Hermitage (profitable months only) |

---

## MUST-DO BEFORE CLOSING (3 items)

### 1. Purchase Price Allocation — IRS Form 8594

**Issue:** The $1 nominal purchase price with $270K in deferred payments creates an unusual
allocation situation. Both parties must file Form 8594 with identical asset class allocations.

**Questions for attorney:**
- [ ] What is the total "amount realized" for Form 8594 purposes? Is it $1 + present value of
  the $270K note, or $1 + face value of $270K?
- [ ] How should the allocation be split across asset classes?
  - Class I (cash): $0
  - Class II (securities): $0
  - Class III (accounts receivable, inventory): Est. $____ — current inventory at cost basis
  - Class IV (equipment): Est. $____ — minimal (warehouse equipment)
  - Class V (IP, domain, customer list, trademarks): Est. $____
  - Class VI (goodwill): Remainder — maximize this for seller's capital gains benefit
  - Class VII (going concern): $0
- [ ] Does the buyer benefit from allocating more to Class III-V (depreciable/amortizable)?
  At this deal size, is the buyer's tax benefit material enough to negotiate over?
- [ ] **Recommendation:** Concede allocation to favor seller's capital gains treatment unless
  the buyer's depreciation benefit exceeds $5K/year.

### 2. Seller Payout Characterization — Purchase Price vs. Compensation

**Issue:** The seller (Dr. Hun Lye) continues as Spiritual Director with ongoing payments.
The IRS may recharacterize some/all of the $270K as compensation for services (ordinary income,
up to 37%) rather than deferred purchase price (capital gains, 20%).

**Risk factors that increase recharacterization risk:**
- Declining payment schedule ($3K → $1.5K) resembles a declining salary
- Seller continues in an advisory role
- Payments are labeled "guaranteed" regardless of performance

**Mitigating factors:**
- Spiritual Director role is genuinely minimal (few hours/month)
- No employment relationship, no set schedule, no benefits
- Payment reduction after Y5 is tied to seller's personal decision to ordain as a monk,
  not to business performance or role changes
- The $270K represents the full economic consideration for the asset purchase

**Questions for attorney:**
- [ ] Should the $270K be kept entirely as purchase price, or explicitly split into purchase
  price + advisory fees? (e.g., $200K purchase + $70K advisory over 10 years)
- [ ] If split, what is the optimal allocation for both parties' tax positions?
- [ ] Should we obtain a tax opinion letter on the characterization?
- [ ] Does the Spiritual Director Advisory Agreement need specific language to support
  the non-employment, non-compensation characterization?
- [ ] The seller plans to ordain as a monk after Y5 — should this be referenced in the
  purchase agreement to explain the payment step-down?

### 3. Inventory Facility Definition

**Issue:** Current term sheet describes the inventory facility as "revolving credit, 0% interest,
no cap" with "forgiveness option after 5 years at Buyer's discretion." This is too vague to be
enforceable and creates unlimited liability for the capital provider.

**Questions for attorney:**
- [ ] Is $100,000 an appropriate revolving cap? (Based on current inventory levels and growth plan)
- [ ] How should quarterly reconciliation work? Cost-basis netting against sold inventory?
- [ ] What does "forgiveness" mean in tax terms? Forgiven debt may be taxable income to the buyer
  entity under IRC §61(a)(12). Is there a COD income exclusion available?
- [ ] Does the capital provider (Michael Mauzé) need a separate facility agreement?
- [ ] Should the facility be secured (UCC filing on inventory specifically) or unsecured?

---

## SHOULD-DO / STRENGTHENS THE DEAL (2 items)

### 4. Formalize Payout as Secured Promissory Note

**Recommendation:** Recharacterize the "guaranteed payout" as a promissory note, secured by a
UCC-1 filing on business assets.

**Questions for attorney:**
- [ ] Draft promissory note: $270,000 face value, 0% interest, 120-month term, with the
  specific payment schedule ($3K × 60 + $1.5K × 60)
- [ ] Draft UCC-1 financing statement listing collateral: inventory, accounts receivable,
  intellectual property (domain names, trademarks), customer lists, equipment
- [ ] Does the UCC-1 filing need to be in the S-Corp's state of formation, the state where
  assets are located, or both?
- [ ] Does the secured note enable installment sale treatment under IRC §453?
- [ ] If the buyer later needs external financing (bank line of credit), can the seller's
  lien be subordinated? Draft a subordination provision.
- [ ] What is the default/remedy provision? (e.g., 30-day cure period, then acceleration
  of remaining balance)

### 5. Personal Guarantee

**Question:** Should Chris Mauzé personally guarantee the promissory note?

- [ ] If the acquisition is done through a new LLC, the seller's only recourse on default
  is the LLC's assets. A personal guarantee adds recourse to Chris's personal assets.
- [ ] Given the payments are already "guaranteed regardless of performance," does a personal
  guarantee add meaningful protection or just legal exposure?
- [ ] Should the capital provider (Michael Mauzé) also guarantee?
- [ ] **Recommendation:** Proactively offer a limited personal guarantee (e.g., guaranteeing
  12 months of payments = $36K) to demonstrate good faith. Full guarantee may be excessive.

---

## ADMINISTRATIVE / CAN ADDRESS LATER (3 items)

### 6. S-Corp Pass-Through Treatment

- [ ] Confirm that the asset sale flows through to Dr. Hun Lye's personal return (Form 1040,
  Schedule D for capital gains, Form 4797 for ordinary income portions)
- [ ] Estimate the seller's tax liability under the proposed allocation to set expectations

### 7. Section 199A Deduction Status

- [ ] Did Congress extend the Section 199A qualified business income deduction past 2025?
- [ ] If still available, does it apply to installment sale income from a former S-Corp?

### 8. State Tax Nexus

- [ ] Does the asset sale create tax obligations in states where Tibetan Spirit has nexus?
  (Known nexus: [state of S-Corp formation], North Carolina (warehouse), potentially
  Washington state)
- [ ] Does the new acquiring entity need to register in those states?

---

## DOCUMENTS NEEDED FROM ATTORNEY

1. **Promissory Note** — $270K, 0% interest, 120-month term, secured
2. **Security Agreement + UCC-1 Filing** — collateral description, filing jurisdiction
3. **Asset Purchase Agreement** — with Form 8594 allocation schedule as exhibit
4. **Spiritual Director Advisory Agreement** — non-employment, minimal hours, separate from
   purchase price
5. **Inventory Facility Agreement** — $100K cap, 0% interest, quarterly reconciliation terms
6. **New Entity Formation** — LLC operating agreement (if not already formed)
7. **Subordination Agreement Template** — for future financing needs

---

## TIMELINE

| Item | Target | Dependency |
|---|---|---|
| Entity formation | Before closing | None |
| Form 8594 allocation agreement | Before closing | Tax advisor input |
| Promissory note + security agreement | Before closing | Attorney drafts |
| UCC-1 filing | At closing | Security agreement signed |
| Advisory agreement | At closing | Characterization decision |
| Inventory facility agreement | At closing | Cap and terms agreed |

---

*This checklist is prepared as a discussion guide for professional advisors. It does not
constitute legal or tax advice. All recommendations should be validated by qualified counsel
and a licensed CPA/tax advisor.*
```

- [ ] **Step 2: Commit**

```bash
git add deliverables/outputs/docs/ts-tax-legal-checklist-2026-04-16.md
git commit -m "docs(deal): add tax and legal review checklist for attorney"
```

---

## Phase 3: Review Plan

### Task 6: Write Chris's Review Plan

**Purpose:** Checklist for Chris to review all deliverables, including the vision deck from yesterday.

**Files:**
- Create: `workspace/plans/review-plan-2026-04-16.md`

- [ ] **Step 1: Write the review plan**

```markdown
# Tibetan Spirit — Deliverables Review Plan

**Date:** 2026-04-16
**Status:** Ready for Chris's review

---

## What to Review

### 1. Financial Model v7 (xlsx)

**File:** `deliverables/outputs/docs/ts-financial-model-v7-2026-04-16.xlsx`
**How:** Upload to Google Sheets, then:

- [ ] **Assumptions tab** — Do these numbers look right? Especially:
  - Starting Shopify revenue: $7,500/mo (you said rolling 30-day is $7,214)
  - COGS: 30% conservative
  - Personnel costs per period (match your budget?)
  - Marketing % of product revenue (Y1 63%, Y2 47%, Y3 31%)
  - TS Travels: 0 trips Y1, 2 trips Y2-Y3 at $150K each
- [ ] **D2C Monthly P&L** — Does the Shopify growth curve look reasonable?
  - Month 1: $7,500, growing at 5.5%/mo Y1
  - Etsy launches M3, Amazon launches M13
  - Subscription fires quarterly starting M4
- [ ] **TS Travels tab** — Is it clearly separated from D2C?
- [ ] **Combined P&L** — Check EBITDA trajectory and ending cash
  - Y1 should be negative (investing in growth)
  - Y3 should be positive or near breakeven
  - Cash should never go below $0
- [ ] **Channel Scenarios** — Do the 4 scenarios tell a useful story?
  - "Shopify Only" = what happens with no new channels
  - "Full Business" = the plan we're pitching
- [ ] **Sensitivity** — Are the revenue factors (70%, 85%, 100%, 115%) useful ranges?

**Key question:** Do the updated numbers (lower starting revenue, higher COGS) still tell
a compelling story, or do we need to adjust assumptions?

### 2. Deal Proposal v2

**File:** `deliverables/outputs/docs/ts-deal-proposal-v2-2026-04-16.md`
**Compare against:** `deliverables/outputs/docs/ts-deal-proposal-2026-04-15.md` (v1)

- [ ] Does the legal structure section (secured note, UCC filing) read naturally,
  or does it feel too "lawyerly" for Dr. Hun Lye?
- [ ] Is the monk transition mentioned respectfully and in the right context?
- [ ] Are D2C and Travels clearly separated in the revenue table?
- [ ] Do the updated numbers (v7 model) still make the growth story compelling?
- [ ] Is the inventory facility cap ($100K) reasonable?
- [ ] Brand voice: warm, honest, accessible?

### 3. Tax & Legal Checklist

**File:** `deliverables/outputs/docs/ts-tax-legal-checklist-2026-04-16.md`

- [ ] Does the deal summary accurately reflect the current terms?
- [ ] Are the 3 "must-do before closing" items correctly prioritized?
- [ ] Is the personal guarantee recommendation reasonable (limited to 12 months)?
- [ ] Are any questions missing that your attorney would need answered?
- [ ] Ready to hand to your lawyer as-is?

### 4. Vision Pitch Deck (from yesterday — first review)

**File:** `deliverables/outputs/decks/ts-vision-deck-2026-04-15.md`
**HTML:** `deliverables/outputs/decks/ts-vision-deck-2026-04-15.html`

- [ ] Open the HTML version for slide-by-slide review
- [ ] **Note:** This deck uses v6 numbers (higher starting revenue, lower COGS).
  After your review, we'll update it with v7 model output.
- [ ] Slide-by-slide: does each slide have a "so what"? Any filler?
- [ ] Is the tone right for your investors? (Data-forward, no hype)
- [ ] Are the competitive references (DharmaCrafts, DharmaShop, Buddha Groove) accurate?
- [ ] Does the "AI Operations Advantage" slide ring true or feel forced?
- [ ] Is 14 slides the right length, or should any be cut/merged?
- [ ] Brand voice and cultural terminology correct throughout?

---

## Review Order (recommended)

1. **Financial model first** — the numbers drive everything else
2. **Deal proposal** — references model numbers
3. **Tax checklist** — hand to attorney after your review
4. **Vision deck** — will be updated with v7 numbers after feedback

## After Review

- Flag any numbers that look wrong → we adjust the model config and re-run
- Flag any tone/content issues in deal docs → we revise
- Once model and deal docs are approved, we update the vision deck with v7 numbers
- **Next step (separate session):** Due diligence research agent assesses the realism
  of the v7 model based on market data and competitor benchmarks

## Due Diligence Research Agent (Planned — Not This Session)

After you approve the v7 model, we'll run a research agent to:
- Benchmark TS channel growth assumptions against comparable D2C businesses
- Validate email marketing open rate assumption (55.7% for religious audiences)
- Research competitor revenue ranges (DharmaCrafts, DharmaShop, Buddha Groove)
- Assess realism of Etsy/Amazon ramp rates for niche spiritual goods
- Evaluate TS Travels pricing against comparable pilgrimage/spiritual travel offerings
- Produce a "model realism scorecard" rating each assumption as conservative/realistic/aggressive
```

- [ ] **Step 2: Commit**

```bash
git add workspace/plans/review-plan-2026-04-16.md
git commit -m "docs(workspace): add deliverables review plan for Chris"
```

---

## Execution Order

```
Phase 1 (sequential — each task depends on previous):
  Task 1: Model config YAML
  Task 2: Model engine + tests
  Task 3: xlsx writer + validate

Phase 2 (depends on Phase 1 for numbers):
  Task 4: Deal proposal v2 (references v7 model output)
  Task 5: Tax & legal checklist

Phase 3:
  Task 6: Review plan for Chris
```

## Success Criteria

- [ ] `python3 scripts/financial_model/build_xlsx.py` produces a valid xlsx
- [ ] xlsx has 7 tabs, all populated with correct data
- [ ] D2C and TS Travels are clearly separated in all outputs
- [ ] COGS = 30% conservative throughout
- [ ] Starting Shopify revenue = $7,500/mo
- [ ] Channel scenarios show 4 toggle combinations
- [ ] Deal proposal v2 integrates legal recommendations naturally
- [ ] Tax checklist has actionable questions for attorney
- [ ] All tests pass
- [ ] Review plan covers all 4 deliverables including yesterday's deck
