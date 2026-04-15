"""
Financial scenario projection math for Tibetan Spirit.

Pure functions for revenue, margin, ramp interpolation, sensitivity analysis,
and 24-month projections. No external dependencies beyond Python stdlib.
"""


def calculate_monthly_revenue(asp: float, orders_per_month: int) -> float:
    """Revenue = ASP * orders per month."""
    return float(asp * orders_per_month)


def interpolate_ramp(ramp_points: dict, month: int) -> float:
    """Linear interpolation across ramp anchor points.

    ramp_points keys: month_1, month_6, month_12, month_24.
    Clamps to month_1 if month < 1, month_24 if month > 24.
    """
    anchors = sorted(
        [(int(k.split("_")[1]), v) for k, v in ramp_points.items()],
        key=lambda x: x[0],
    )

    # Clamp below first anchor
    if month <= anchors[0][0]:
        return float(anchors[0][1])

    # Clamp above last anchor
    if month >= anchors[-1][0]:
        return float(anchors[-1][1])

    # Find surrounding anchors and interpolate
    for i in range(len(anchors) - 1):
        low_month, low_val = anchors[i]
        high_month, high_val = anchors[i + 1]
        if low_month <= month <= high_month:
            if month == low_month:
                return float(low_val)
            fraction = (month - low_month) / (high_month - low_month)
            return float(low_val + fraction * (high_val - low_val))

    # Should not reach here, but return last anchor as fallback
    return float(anchors[-1][1])


def calculate_gross_profit(revenue: float, cogs_pct: float) -> float:
    """Gross profit = revenue * (1 - COGS %)."""
    return float(revenue * (1 - cogs_pct))


def calculate_breakeven_months(
    upfront_investment: float, monthly_gross_profit: float
) -> float:
    """Months to recoup upfront investment at given monthly gross profit.

    Returns float('inf') when monthly_gross_profit is zero.
    """
    if monthly_gross_profit == 0:
        return float("inf")
    return float(upfront_investment / monthly_gross_profit)


def calculate_blended_margin_impact(
    baseline_revenue: float,
    baseline_margin: float,
    new_revenue: float,
    new_margin: float,
) -> float:
    """Weighted-average margin across two revenue streams.

    Returns 0.0 when total revenue is zero (avoids ZeroDivisionError).
    """
    total = baseline_revenue + new_revenue
    if total == 0:
        return 0.0
    return float(
        (baseline_revenue * baseline_margin + new_revenue * new_margin) / total
    )


def calculate_sensitivity(
    base_volume: int,
    volume_multipliers: list,
    asp: float,
    cogs_pct: float,
) -> list:
    """Sensitivity table: one row per volume multiplier.

    Each row: {multiplier, orders, revenue, gross_profit}.
    """
    results = []
    for mult in volume_multipliers:
        orders = base_volume * mult
        revenue = orders * asp
        gross_profit = revenue * (1 - cogs_pct)
        results.append(
            {
                "multiplier": mult,
                "orders": float(orders),
                "revenue": float(revenue),
                "gross_profit": float(gross_profit),
            }
        )
    return results


def project_24_months(scenario: dict) -> list:
    """Generate a 24-month projection from a scenario dict.

    Scenario keys: asp, cogs_pct, ramp, upfront_investment, ongoing_monthly.
    Returns list of 24 dicts, each with: month, orders, revenue,
    gross_profit, net_monthly, cumulative_net.

    cumulative_net starts at -upfront_investment and accumulates net_monthly.
    """
    asp = scenario["asp"]
    cogs_pct = scenario["cogs_pct"]
    ramp = scenario["ramp"]
    upfront = scenario["upfront_investment"]
    ongoing_costs = sum(scenario["ongoing_monthly"].values())

    cumulative_net = -upfront
    rows = []

    for month in range(1, 25):
        orders = interpolate_ramp(ramp, month)
        revenue = orders * asp
        gross_profit = revenue * (1 - cogs_pct)
        net_monthly = gross_profit - ongoing_costs
        cumulative_net += net_monthly

        rows.append(
            {
                "month": month,
                "orders": float(orders),
                "revenue": float(revenue),
                "gross_profit": float(gross_profit),
                "net_monthly": float(net_monthly),
                "cumulative_net": float(cumulative_net),
            }
        )

    return rows
