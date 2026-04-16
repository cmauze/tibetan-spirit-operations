"""Tibetan Spirit v7 — 36-month P&L engine with channel projections."""
from __future__ import annotations

import copy
from typing import Any

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _year_for_month(month: int) -> int:
    """Return 1, 2, or 3 for a model month (1-36)."""
    if month <= 12:
        return 1
    if month <= 24:
        return 2
    return 3


def _growth_rate_for_month(month: int, rates: list) -> float | None:
    """Get the Y1/Y2/Y3 growth rate for *month*; returns None when inactive."""
    return rates[_year_for_month(month) - 1]


def _calendar_month(model_month: int, start_month: int = 6) -> int:
    """Convert model month (1-36) to calendar month (1-12).

    Model month 1 = June (start_month=6).
    """
    return ((start_month - 1 + model_month - 1) % 12) + 1


# ---------------------------------------------------------------------------
# Channel projection functions (pure, no I/O)
# ---------------------------------------------------------------------------

def project_standard_channel(
    start_month: int,
    starting_revenue: float,
    monthly_growth: list,
    months: int = 36,
) -> list[float]:
    """Compound monthly growth, switching rate at year boundaries.

    Months before *start_month* are 0.  If a year's rate is ``None`` those
    months produce 0 (channel not yet active).
    """
    result: list[float] = []
    prev = 0.0
    for m in range(1, months + 1):
        if m < start_month:
            result.append(0.0)
            continue
        rate = _growth_rate_for_month(m, monthly_growth)
        if rate is None:
            result.append(0.0)
            continue
        if m == start_month:
            result.append(float(starting_revenue))
            prev = float(starting_revenue)
        else:
            # If previous month was zero (channel just became active), use
            # starting_revenue as the base.
            if prev == 0.0:
                result.append(float(starting_revenue))
                prev = float(starting_revenue)
            else:
                val = prev * (1 + rate)
                result.append(val)
                prev = val
    return result


def project_quarterly_subscription(
    start_month: int,
    starting_quarterly_revenue: float,
    quarterly_growth: float,
    months: int = 36,
) -> list[float]:
    """Revenue fires every 3 months from *start_month*, growing each quarter."""
    result: list[float] = []
    quarter_idx = 0
    for m in range(1, months + 1):
        if m < start_month:
            result.append(0.0)
            continue
        offset = m - start_month
        if offset % 3 == 0:
            val = starting_quarterly_revenue * ((1 + quarterly_growth) ** quarter_idx)
            result.append(val)
            quarter_idx += 1
        else:
            result.append(0.0)
    return result


def project_unit_based_channel(
    start_month: int,
    units_per_month: list,
    avg_order_value: float,
    months: int = 36,
) -> list[float]:
    """Revenue = units x AOV per month. *units_per_month* is [y1, y2, y3]."""
    result: list[float] = []
    for m in range(1, months + 1):
        if m < start_month:
            result.append(0.0)
            continue
        year = _year_for_month(m)
        units = units_per_month[year - 1]
        result.append(float(units * avg_order_value))
    return result


def project_travels(
    trips_per_year: list,
    revenue_per_trip: float,
    months: int = 36,
) -> list[float]:
    """Lump revenue events spread evenly across each year's 12 months.

    For *n* trips in a year, place revenue in *n* evenly-spaced months.
    """
    result: list[float] = [0.0] * months
    for year_idx in range(3):
        n_trips = trips_per_year[year_idx]
        if n_trips == 0:
            continue
        year_start = year_idx * 12  # index offset
        # Spread n_trips evenly across 12 months
        spacing = 12 / n_trips
        for t in range(n_trips):
            month_idx = year_start + int(round(spacing * t + spacing / 2)) - 1
            month_idx = min(month_idx, year_start + 11)  # clamp to year
            result[month_idx] = revenue_per_trip
    return result


# ---------------------------------------------------------------------------
# Cost functions
# ---------------------------------------------------------------------------

def compute_marketing_spend(
    product_revenue: float,
    pct: float,
    calendar_month: int,
    q4_multiplier: float = 2.0,
    q4_months: list[int] | None = None,
) -> float:
    """Base = product_revenue x pct; Q4 calendar months get multiplied."""
    if q4_months is None:
        q4_months = [10, 11, 12, 1]
    base = product_revenue * pct
    if calendar_month in q4_months:
        base *= q4_multiplier
    return base


def compute_personnel_cost(month: int, personnel_cfg: dict) -> float:
    """Return the flat monthly personnel cost for *month* (1-36)."""
    if month <= 4:
        return float(personnel_cfg["monthly_m1_to_m4"])
    if month <= 12:
        return float(personnel_cfg["monthly_m5_to_m12"])
    if month <= 24:
        return float(personnel_cfg["monthly_y2"])
    return float(personnel_cfg["monthly_y3"])


# ---------------------------------------------------------------------------
# Main P&L builder
# ---------------------------------------------------------------------------

_MONTH_ABBR = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
]


def _make_month_labels(start_month: int, start_year: int, months: int) -> list[str]:
    labels: list[str] = []
    for m in range(1, months + 1):
        cm = _calendar_month(m, start_month)
        year = start_year + (start_month - 1 + m - 1) // 12
        labels.append(f"{_MONTH_ABBR[cm - 1]} {year % 100:02d}")
    return labels


def build_monthly_pnl(config: dict[str, Any]) -> dict[str, Any]:
    """Build the complete 36-month P&L from a config dict."""
    meta = config["meta"]
    months = meta["months"]
    start_month = meta["start_month"]
    start_year = meta["start_year"]
    d2c_cfg = config["d2c"]
    travels_cfg = config["travels"]
    costs_cfg = config["costs"]
    capital_cfg = config["capital"]

    month_labels = _make_month_labels(start_month, start_year, months)

    # --- Revenue: D2C channels ---
    d2c_channels: dict[str, list[float]] = {}
    for ch_name, ch_cfg in d2c_cfg["channels"].items():
        ch_type = ch_cfg.get("type", "standard")
        if ch_type == "quarterly":
            d2c_channels[ch_name] = project_quarterly_subscription(
                start_month=ch_cfg["start_month"],
                starting_quarterly_revenue=ch_cfg["starting_quarterly_revenue"],
                quarterly_growth=ch_cfg["quarterly_growth"],
                months=months,
            )
        elif ch_type == "unit_based":
            d2c_channels[ch_name] = project_unit_based_channel(
                start_month=ch_cfg["start_month"],
                units_per_month=ch_cfg["units_per_month"],
                avg_order_value=ch_cfg["avg_order_value"],
                months=months,
            )
        else:
            d2c_channels[ch_name] = project_standard_channel(
                start_month=ch_cfg["start_month"],
                starting_revenue=ch_cfg["starting_revenue"],
                monthly_growth=ch_cfg["monthly_growth"],
                months=months,
            )

    d2c_total = [
        sum(d2c_channels[ch][i] for ch in d2c_channels) for i in range(months)
    ]

    # --- Revenue: Travels ---
    travels = project_travels(
        trips_per_year=travels_cfg["trips_per_year"],
        revenue_per_trip=travels_cfg["revenue_per_trip"],
        months=months,
    )

    total_revenue = [d2c_total[i] + travels[i] for i in range(months)]

    # --- COGS ---
    cogs_by_channel: dict[str, list[float]] = {}
    for ch_name, ch_cfg in d2c_cfg["channels"].items():
        cogs_pct = ch_cfg.get("cogs_pct_override") or d2c_cfg["cogs_pct"]
        cogs_by_channel[ch_name] = [
            d2c_channels[ch_name][i] * cogs_pct for i in range(months)
        ]

    cogs_travels = [travels[i] * travels_cfg["cogs_pct"] for i in range(months)]

    total_cogs = [
        sum(cogs_by_channel[ch][i] for ch in cogs_by_channel) + cogs_travels[i]
        for i in range(months)
    ]
    gross_profit = [total_revenue[i] - total_cogs[i] for i in range(months)]

    # --- Operating costs ---
    personnel = [
        compute_personnel_cost(m + 1, costs_cfg["personnel"]) for m in range(months)
    ]

    tech_cfg = costs_cfg["technology"]
    technology = []
    for m in range(1, months + 1):
        year = _year_for_month(m)
        if year == 1:
            technology.append(float(tech_cfg["monthly_y1"]))
        elif year == 2:
            technology.append(float(tech_cfg["monthly_y2"]))
        else:
            technology.append(float(tech_cfg["monthly_y3"]))

    mkt_cfg = costs_cfg["marketing"]
    mkt_pcts = [
        mkt_cfg["pct_of_product_revenue_y1"],
        mkt_cfg["pct_of_product_revenue_y2"],
        mkt_cfg["pct_of_product_revenue_y3"],
    ]
    marketing = []
    for m in range(1, months + 1):
        pct = mkt_pcts[_year_for_month(m) - 1]
        cm = _calendar_month(m, start_month)
        marketing.append(compute_marketing_spend(
            product_revenue=d2c_total[m - 1],
            pct=pct,
            calendar_month=cm,
            q4_multiplier=mkt_cfg["q4_multiplier"],
            q4_months=mkt_cfg["q4_months"],
        ))

    shipping = [d2c_total[i] * d2c_cfg["shipping_fulfillment_pct"] for i in range(months)]

    platform_fees: list[float] = []
    for i in range(months):
        total = 0.0
        for ch_name, ch_cfg in d2c_cfg["channels"].items():
            total += d2c_channels[ch_name][i] * ch_cfg["platform_fee_pct"]
        platform_fees.append(total)

    seller_payout_amt = float(costs_cfg["seller_payout"]["monthly_y1_5"])
    seller_payout = [seller_payout_amt] * months

    # Foundation: 10% of EBITDA-before-foundation on profitable months
    foundation_pct = config["costs"]["foundation"]["pct_of_net_profit"]
    only_profitable = config["costs"]["foundation"]["only_profitable_months"]

    # Compute EBITDA-before-foundation first
    ebitda_before_foundation: list[float] = []
    for i in range(months):
        opex_excl_foundation = (
            personnel[i] + technology[i] + marketing[i]
            + shipping[i] + platform_fees[i] + seller_payout[i]
        )
        ebitda_before_foundation.append(gross_profit[i] - opex_excl_foundation)

    foundation: list[float] = []
    for i in range(months):
        if only_profitable and ebitda_before_foundation[i] <= 0:
            foundation.append(0.0)
        else:
            foundation.append(ebitda_before_foundation[i] * foundation_pct)

    total_opex = [
        personnel[i] + technology[i] + marketing[i] + shipping[i]
        + platform_fees[i] + seller_payout[i] + foundation[i]
        for i in range(months)
    ]

    ebitda = [gross_profit[i] - total_opex[i] for i in range(months)]

    # --- Cash flow ---
    capital_infusion = [0.0] * months
    capital_infusion[0] += capital_cfg["ops_capital"]["y1"]     # month 1
    capital_infusion[9] += capital_cfg["truist_cd"]              # month 10
    capital_infusion[12] += capital_cfg["ops_capital"]["y2"]     # month 13
    capital_infusion[24] += capital_cfg["ops_capital"]["y3"]     # month 25

    ending_cash: list[float] = []
    cash = float(capital_cfg["cash_on_hand"])
    for i in range(months):
        cash += capital_infusion[i] + ebitda[i]
        ending_cash.append(cash)

    # --- Yearly summary ---
    def _sum_slice(arr: list[float], start: int, end: int) -> float:
        return sum(arr[start:end])

    yearly_summary: dict[str, dict[str, float]] = {}
    for label, s, e in [("Y1", 0, 12), ("Y2", 12, 24), ("Y3", 24, 36)]:
        yearly_summary[label] = {
            "d2c_total": _sum_slice(d2c_total, s, e),
            "travels": _sum_slice(travels, s, e),
            "total_revenue": _sum_slice(total_revenue, s, e),
            "total_cogs": _sum_slice(total_cogs, s, e),
            "gross_profit": _sum_slice(gross_profit, s, e),
            "personnel": _sum_slice(personnel, s, e),
            "technology": _sum_slice(technology, s, e),
            "marketing": _sum_slice(marketing, s, e),
            "shipping": _sum_slice(shipping, s, e),
            "platform_fees": _sum_slice(platform_fees, s, e),
            "seller_payout": _sum_slice(seller_payout, s, e),
            "foundation": _sum_slice(foundation, s, e),
            "total_opex": _sum_slice(total_opex, s, e),
            "ebitda": _sum_slice(ebitda, s, e),
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


# ---------------------------------------------------------------------------
# Scenario builder
# ---------------------------------------------------------------------------

def _zero_channel(cfg: dict, ch_name: str) -> None:
    """Zero out a channel in a config copy."""
    ch = cfg["d2c"]["channels"][ch_name]
    ch_type = ch.get("type", "standard")
    if ch_type == "quarterly":
        ch["starting_quarterly_revenue"] = 0
    elif ch_type == "unit_based":
        ch["units_per_month"] = [0, 0, 0]
    else:
        ch["starting_revenue"] = 0


def _zero_travels(cfg: dict) -> None:
    cfg["travels"]["trips_per_year"] = [0, 0, 0]


def build_scenarios(config: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Build four P&L scenarios from the base config."""
    all_channels = list(config["d2c"]["channels"].keys())

    # 1. Shopify Only
    cfg1 = copy.deepcopy(config)
    for ch in all_channels:
        if ch != "shopify":
            _zero_channel(cfg1, ch)
    _zero_travels(cfg1)

    # 2. D2C Core (shopify + etsy + subscription)
    cfg2 = copy.deepcopy(config)
    core = {"shopify", "etsy", "subscription"}
    for ch in all_channels:
        if ch not in core:
            _zero_channel(cfg2, ch)
    _zero_travels(cfg2)

    # 3. Full D2C (all product channels, no travels)
    cfg3 = copy.deepcopy(config)
    _zero_travels(cfg3)

    # 4. Full Business (unmodified)
    return {
        "Shopify Only": build_monthly_pnl(cfg1),
        "D2C Core": build_monthly_pnl(cfg2),
        "Full D2C": build_monthly_pnl(cfg3),
        "Full Business": build_monthly_pnl(config),
    }
