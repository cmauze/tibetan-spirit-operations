"""
Financial scenario projection math for Tibetan Spirit.

All functions raise NotImplementedError until Task 3 (projection engine) is implemented.
Tests in tests/test_financial_model.py are intentionally RED until this module is built.
"""


def calculate_monthly_revenue(asp: float, orders_per_month: int) -> float:
    raise NotImplementedError("Task 3: implement projection engine")


def interpolate_ramp(ramp_points: dict, month: int) -> float:
    raise NotImplementedError("Task 3: implement projection engine")


def calculate_gross_profit(revenue: float, cogs_pct: float) -> float:
    raise NotImplementedError("Task 3: implement projection engine")


def calculate_breakeven_months(upfront_investment: float, monthly_gross_profit: float) -> float:
    raise NotImplementedError("Task 3: implement projection engine")


def calculate_blended_margin_impact(
    baseline_revenue: float,
    baseline_margin: float,
    new_revenue: float,
    new_margin: float,
) -> float:
    raise NotImplementedError("Task 3: implement projection engine")


def calculate_sensitivity(
    base_volume: int,
    volume_multipliers: list,
    asp: float,
    cogs_pct: float,
) -> list:
    raise NotImplementedError("Task 3: implement projection engine")


def project_24_months(scenario: dict) -> list:
    raise NotImplementedError("Task 3: implement projection engine")
