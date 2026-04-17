"""Tibetan Spirit v7/v8 — 36-month P&L engine with channel/product-line projections."""
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
    month: int = 1,
    calendar_month: int = 1,
    marketing_cfg: dict | None = None,
    start_month: int = 6,
    # --- Legacy v7 positional args (backward compat) ---
    pct: float | None = None,
    q4_multiplier: float = 2.0,
    q4_months: list[int] | None = None,
) -> float:
    """Marketing spend with monthly ramp schedule and per-year holiday multipliers.

    v8: pass *marketing_cfg* dict with ramp_schedule and holiday multipliers.
    v7 (legacy): pass *pct*, *q4_multiplier*, *q4_months* directly.
    """
    # --- Legacy v7 path ---
    if pct is not None:
        if q4_months is None:
            q4_months = [10, 11, 12, 1]
        base = product_revenue * pct
        if calendar_month in q4_months:
            base *= q4_multiplier
        return base

    # --- v8 path ---
    if marketing_cfg is None:
        return 0.0

    year = _year_for_month(month)

    # Determine base marketing percentage
    if year == 1 and "ramp_schedule" in marketing_cfg:
        pct_val = 0.0
        for entry in marketing_cfg["ramp_schedule"]:
            if month <= entry["through_month"]:
                pct_val = float(entry["pct"])
                break
        else:
            pct_val = float(marketing_cfg["ramp_schedule"][-1]["pct"])
    elif year == 1:
        pct_val = float(marketing_cfg.get("pct_of_product_revenue_y1", 0.0))
    elif year == 2:
        pct_val = float(marketing_cfg["pct_of_product_revenue_y2"])
    else:
        pct_val = float(marketing_cfg["pct_of_product_revenue_y3"])

    base = product_revenue * pct_val

    # Holiday multiplier
    holiday_months = marketing_cfg.get("holiday_months", [10, 11, 12])
    if calendar_month in holiday_months:
        multiplier_key = f"holiday_multiplier_y{year}"
        multiplier = float(marketing_cfg.get(multiplier_key, 1.0))
        base *= multiplier

    return base


def compute_platform_fee_rate(month: int, schedule: list[dict]) -> float:
    """Return blended platform fee rate for *month* from a schedule.

    Schedule is a list of dicts: [{"through_month": N, "rate": R}, ...]
    sorted by through_month ascending.
    """
    for entry in schedule:
        if month <= entry["through_month"]:
            return float(entry["rate"])
    return float(schedule[-1]["rate"])


def compute_personnel_cost(month: int, personnel_cfg: dict) -> float:
    """Return flat monthly personnel cost for *month* (1-36).

    Supports both v7 format (monthly_m1_to_m4, monthly_m5_to_m12)
    and v8 format (monthly_y1, monthly_y2, monthly_y3).
    """
    year = _year_for_month(month)

    # v8 format: flat per year
    if "monthly_y1" in personnel_cfg:
        if year == 1:
            return float(personnel_cfg["monthly_y1"])
        if year == 2:
            return float(personnel_cfg["monthly_y2"])
        return float(personnel_cfg["monthly_y3"])

    # v7 fallback format
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
    """Build the complete 36-month P&L from a config dict.

    Supports both v7 (channel-based) and v8 (product-line-based) configs.
    """
    meta = config["meta"]
    months = meta["months"]
    start_month = meta["start_month"]
    start_year = meta["start_year"]
    d2c_cfg = config["d2c"]
    travels_cfg = config["travels"]
    costs_cfg = config["costs"]
    capital_cfg = config["capital"]

    month_labels = _make_month_labels(start_month, start_year, months)

    # --- Revenue: D2C product lines (v8) or channels (v7) ---
    lines_cfg = d2c_cfg.get("product_lines", d2c_cfg.get("channels", {}))
    d2c_lines: dict[str, list[float]] = {}
    for line_name, line_cfg in lines_cfg.items():
        line_type = line_cfg.get("type", "standard")
        if line_type == "quarterly":
            d2c_lines[line_name] = project_quarterly_subscription(
                start_month=line_cfg["start_month"],
                starting_quarterly_revenue=line_cfg["starting_quarterly_revenue"],
                quarterly_growth=line_cfg["quarterly_growth"],
                months=months,
            )
        elif line_type == "unit_based":
            d2c_lines[line_name] = project_unit_based_channel(
                start_month=line_cfg["start_month"],
                units_per_month=line_cfg["units_per_month"],
                avg_order_value=line_cfg["avg_order_value"],
                months=months,
            )
        else:
            d2c_lines[line_name] = project_standard_channel(
                start_month=line_cfg["start_month"],
                starting_revenue=line_cfg["starting_revenue"],
                monthly_growth=line_cfg["monthly_growth"],
                months=months,
            )

    d2c_total = [
        sum(d2c_lines[ln][i] for ln in d2c_lines) for i in range(months)
    ]

    # --- Revenue: Travels ---
    travels = project_travels(
        trips_per_year=travels_cfg["trips_per_year"],
        revenue_per_trip=travels_cfg["revenue_per_trip"],
        months=months,
    )

    total_revenue = [d2c_total[i] + travels[i] for i in range(months)]

    # --- COGS (per product line) ---
    default_cogs = d2c_cfg.get("cogs_pct", 0.30)
    cogs_by_line: dict[str, list[float]] = {}
    for line_name, line_cfg in lines_cfg.items():
        cogs_pct = line_cfg.get("cogs_pct", line_cfg.get("cogs_pct_override") or default_cogs)
        cogs_by_line[line_name] = [
            d2c_lines[line_name][i] * cogs_pct for i in range(months)
        ]

    cogs_travels = [travels[i] * travels_cfg["cogs_pct"] for i in range(months)]

    total_cogs = [
        sum(cogs_by_line[ln][i] for ln in cogs_by_line) + cogs_travels[i]
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

    # --- Marketing ---
    mkt_cfg = costs_cfg["marketing"]
    marketing = []
    for m in range(1, months + 1):
        cm = _calendar_month(m, start_month)
        if "ramp_schedule" in mkt_cfg or "holiday_multiplier_y1" in mkt_cfg:
            # v8 format
            marketing.append(compute_marketing_spend(
                product_revenue=d2c_total[m - 1],
                month=m,
                calendar_month=cm,
                marketing_cfg=mkt_cfg,
            ))
        else:
            # v7 format
            mkt_pcts = [
                mkt_cfg["pct_of_product_revenue_y1"],
                mkt_cfg["pct_of_product_revenue_y2"],
                mkt_cfg["pct_of_product_revenue_y3"],
            ]
            marketing.append(compute_marketing_spend(
                product_revenue=d2c_total[m - 1],
                calendar_month=cm,
                pct=mkt_pcts[_year_for_month(m) - 1],
                q4_multiplier=mkt_cfg["q4_multiplier"],
                q4_months=mkt_cfg["q4_months"],
            ))

    shipping = [d2c_total[i] * d2c_cfg["shipping_fulfillment_pct"] for i in range(months)]

    # --- Platform fees ---
    fee_schedule = d2c_cfg.get("platform_fee_schedule")
    platform_fees: list[float] = []
    for i in range(months):
        if fee_schedule:
            rate = compute_platform_fee_rate(i + 1, fee_schedule)
            platform_fees.append(d2c_total[i] * rate)
        else:
            # v7 fallback: per-channel/per-line fee rates
            total = 0.0
            for line_name, line_cfg in lines_cfg.items():
                total += d2c_lines[line_name][i] * line_cfg["platform_fee_pct"]
            platform_fees.append(total)

    seller_payout_amt = float(costs_cfg["seller_payout"]["monthly_y1_5"])
    seller_payout = [seller_payout_amt] * months

    # Foundation: % of EBITDA-before-foundation on profitable months
    foundation_pct = costs_cfg["foundation"]["pct_of_net_profit"]
    only_profitable = costs_cfg["foundation"]["only_profitable_months"]

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
    capital_infusion[0] += capital_cfg["ops_capital"]["y1"]
    capital_infusion[9] += capital_cfg["truist_cd"]
    capital_infusion[12] += capital_cfg["ops_capital"]["y2"]
    capital_infusion[24] += capital_cfg["ops_capital"]["y3"]

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
        "d2c_channels": d2c_lines,  # Keep key name for build_xlsx compat
        "d2c_total": d2c_total,
        "travels": travels,
        "total_revenue": total_revenue,
        "cogs_by_channel": cogs_by_line,  # Keep key name for build_xlsx compat
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

def _zero_line(cfg: dict, line_name: str) -> None:
    """Zero out a product line (or channel) in a config copy."""
    lines_key = "product_lines" if "product_lines" in cfg["d2c"] else "channels"
    line = cfg["d2c"][lines_key][line_name]
    line_type = line.get("type", "standard")
    if line_type == "quarterly":
        line["starting_quarterly_revenue"] = 0
    elif line_type == "unit_based":
        line["units_per_month"] = [0, 0, 0]
    else:
        line["starting_revenue"] = 0


def _zero_travels(cfg: dict) -> None:
    cfg["travels"]["trips_per_year"] = [0, 0, 0]


def build_scenarios(config: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Build four P&L scenarios from the base config."""
    lines_key = "product_lines" if "product_lines" in config["d2c"] else "channels"
    all_lines = list(config["d2c"][lines_key].keys())

    # Identify line categories
    standard_lines = [ln for ln in all_lines
                      if config["d2c"][lines_key][ln].get("type", "standard") == "standard"]
    special_lines = [ln for ln in all_lines if ln not in standard_lines]

    # 1. Core Only — standard product lines only, no premium/subscription/travels
    cfg1 = copy.deepcopy(config)
    for ln in special_lines:
        _zero_line(cfg1, ln)
    _zero_travels(cfg1)

    # 2. D2C + Premium — standard lines + premium, no subscription or travels
    cfg2 = copy.deepcopy(config)
    for ln in special_lines:
        if ln != "premium":
            _zero_line(cfg2, ln)
    _zero_travels(cfg2)

    # 3. Full D2C — all product lines, no travels
    cfg3 = copy.deepcopy(config)
    _zero_travels(cfg3)

    # 4. Full Business (unmodified)
    return {
        "Core D2C": build_monthly_pnl(cfg1),
        "D2C + Premium": build_monthly_pnl(cfg2),
        "Full D2C": build_monthly_pnl(cfg3),
        "Full Business": build_monthly_pnl(config),
    }
