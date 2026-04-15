"""
Scenario definition loader and projection runner.

Loads scenarios from YAML config, validates required fields, and runs
24-month projections using analysis.py math functions.

Usage:
    from scripts.financial_model.scenarios import load_scenarios, run_scenario

    scenarios = load_scenarios("scripts/financial_model/config/scenarios.yaml")
    projection = run_scenario(scenarios[0])
"""
from __future__ import annotations

import yaml
from pathlib import Path
from scripts.financial_model.analysis import project_24_months, calculate_sensitivity

REQUIRED_FIELDS = [
    "name",
    "category",
    "asp",
    "cogs_pct",
    "ramp",
    "upfront_investment",
    "ongoing_monthly",
]
RAMP_FIELDS = ["month_1", "month_6", "month_12", "month_24"]
SENSITIVITY_MULTIPLIERS = [0.5, 0.75, 1.0, 1.25, 1.5]


def load_scenarios(yaml_path: str | Path) -> list[dict]:
    """Load and validate scenarios from YAML file."""
    path = Path(yaml_path)
    if not path.exists():
        raise FileNotFoundError(f"Scenario file not found: {path}")

    with open(path) as f:
        data = yaml.safe_load(f)

    scenarios = data.get("scenarios", [])
    for i, s in enumerate(scenarios):
        missing = [f for f in REQUIRED_FIELDS if f not in s]
        if missing:
            raise ValueError(
                f"Scenario {i} ({s.get('name', 'unnamed')}) missing fields: {missing}"
            )

        ramp_missing = [f for f in RAMP_FIELDS if f not in s.get("ramp", {})]
        if ramp_missing:
            raise ValueError(
                f"Scenario {i} ({s.get('name', 'unnamed')}) ramp missing: {ramp_missing}"
            )

    return scenarios


def run_scenario(scenario: dict) -> dict:
    """Run a full projection for a single scenario.

    Returns dict with: scenario metadata, 24-month projection, sensitivity table.
    """
    projection = project_24_months(scenario)

    # Use month 12 volume as base for sensitivity
    month_12_orders = projection[11]["orders"]  # 0-indexed

    sensitivity = calculate_sensitivity(
        base_volume=month_12_orders,
        volume_multipliers=SENSITIVITY_MULTIPLIERS,
        asp=scenario["asp"],
        cogs_pct=scenario["cogs_pct"],
    )

    return {
        "name": scenario["name"],
        "category": scenario["category"],
        "projection": projection,
        "sensitivity": sensitivity,
        "summary": {
            "total_revenue_24mo": sum(m["revenue"] for m in projection),
            "total_gp_24mo": sum(m["gross_profit"] for m in projection),
            "breakeven_month": next(
                (m["month"] for m in projection if m["cumulative_net"] >= 0),
                None,  # Never breaks even in 24 months
            ),
            "month_24_run_rate": projection[-1]["revenue"] * 12,  # Annualized
        },
    }


def run_all_scenarios(yaml_path: str | Path) -> list[dict]:
    """Load all scenarios and run projections."""
    scenarios = load_scenarios(yaml_path)
    return [run_scenario(s) for s in scenarios]
