"""Output formatters for financial scenario model.

Formats scenario results into markdown reports and saves JSON/markdown files.
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from scripts.financial_model.analysis import calculate_blended_margin_impact

DISPLAY_MONTHS = [1, 3, 6, 12, 18, 24]
SENSITIVITY_LABELS = {0.5: "50%", 0.75: "75%", 1.0: "100%", 1.25: "125%", 1.5: "150%"}


def _dollar(v: float) -> str:
    return f"-${abs(v):,.0f}" if v < 0 else f"${v:,.0f}"


def _dollar_k(v: float) -> str:
    return f"${v / 1_000:,.0f}K" if abs(v) >= 1_000 else _dollar(v)


def _pct(v: float) -> str:
    return f"{v * 100:.1f}%"


def _derive_asp(result: dict) -> float:
    for row in result["projection"]:
        if row["orders"] > 0:
            return row["revenue"] / row["orders"]
    return 0.0


def _derive_cogs_pct(result: dict) -> float:
    for row in result["projection"]:
        if row["revenue"] > 0:
            return 1.0 - (row["gross_profit"] / row["revenue"])
    return 0.0


def _derive_upfront(result: dict) -> float:
    row = result["projection"][0]
    return -(row["cumulative_net"] - row["net_monthly"])


def format_scenario_summary(result: dict) -> str:
    """Format a single scenario result as a markdown section."""
    asp = _derive_asp(result)
    cogs_pct = _derive_cogs_pct(result)
    margin = 1.0 - cogs_pct
    s = result["summary"]
    upfront = _derive_upfront(result)

    be = s["breakeven_month"]
    be_str = f"Month {be}" if be is not None else "Never (24mo)"

    lines = [
        f"### {result['name']} ({result['category']})",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| ASP | {_dollar(asp)} |",
        f"| COGS | {_pct(cogs_pct)} |",
        f"| Gross Margin | {_pct(margin)} |",
        f"| Upfront Investment | {_dollar(upfront)} |",
        f"| Breakeven | {be_str} |",
        f"| 24-Month Revenue | {_dollar(s['total_revenue_24mo'])} |",
        f"| 24-Month Gross Profit | {_dollar(s['total_gp_24mo'])} |",
        f"| Month 24 Run Rate (ann.) | {_dollar(s['month_24_run_rate'])} |",
        "",
        "**Monthly Projection (key months):**",
        "",
        "| Month | Orders | Revenue | Gross Profit | Net Monthly | Cumulative |",
        "|-------|--------|---------|-------------|-------------|------------|",
    ]

    proj = {row["month"]: row for row in result["projection"]}
    for m in DISPLAY_MONTHS:
        if m in proj:
            r = proj[m]
            lines.append(
                f"| {m} | {r['orders']:.0f} | {_dollar(r['revenue'])} "
                f"| {_dollar(r['gross_profit'])} | {_dollar(r['net_monthly'])} "
                f"| {_dollar(r['cumulative_net'])} |"
            )

    lines.extend([
        "",
        "**Sensitivity (at Month 12 volume):**",
        "",
        "| Volume | Orders/mo | Monthly Revenue | Monthly GP |",
        "|--------|-----------|----------------|------------|",
    ])

    for row in result["sensitivity"]:
        label = SENSITIVITY_LABELS.get(row["multiplier"], f"{row['multiplier']:.0%}")
        lines.append(
            f"| {label} | {row['orders']:.0f} | {_dollar(row['revenue'])} "
            f"| {_dollar(row['gross_profit'])} |"
        )

    return "\n".join(lines)


def format_comparison_table(results: list[dict]) -> str:
    """Format a side-by-side comparison table of all scenarios."""
    if not results:
        return ""

    names = [r["name"] for r in results]
    header = "| Metric | " + " | ".join(names) + " |"
    sep = "|--------" + "|--------" * len(names) + "|"

    def row(label: str, values: list[str]) -> str:
        return f"| {label} | " + " | ".join(values) + " |"

    rows = [
        "## Scenario Comparison", "", header, sep,
        row("ASP", [_dollar(_derive_asp(r)) for r in results]),
        row("COGS %", [_pct(_derive_cogs_pct(r)) for r in results]),
        row("Gross Margin", [_pct(1.0 - _derive_cogs_pct(r)) for r in results]),
        row("Upfront Investment", [_dollar(_derive_upfront(r)) for r in results]),
        row("Breakeven Month", [
            str(r["summary"]["breakeven_month"]) if r["summary"]["breakeven_month"] else "N/A"
            for r in results
        ]),
        row("24-Mo Revenue", [_dollar_k(r["summary"]["total_revenue_24mo"]) for r in results]),
        row("24-Mo GP", [_dollar_k(r["summary"]["total_gp_24mo"]) for r in results]),
        row("Month 24 Run Rate", [_dollar_k(r["summary"]["month_24_run_rate"]) for r in results]),
    ]

    return "\n".join(rows)


def format_blended_impact(baseline: dict, results: list[dict]) -> str:
    """Show how each scenario blends with the existing business.

    Normalizes baseline revenue to a 24-month comparable by annualizing the
    historical period (which covers 2025-01 through 2026-03 = 15 months).
    """
    base_rev_historical = baseline["orders"]["total_revenue_usd"]
    monthly_volume = baseline["orders"].get("monthly_volume", {})
    baseline_months = max(len(monthly_volume), 1)
    base_rev_24mo = (base_rev_historical / baseline_months) * 24

    base_cogs = baseline["cogs"].get("blended_cogs_pct") or 0.0
    base_margin = 1.0 - base_cogs

    monthly_run_rate = base_rev_historical / baseline_months

    lines = [
        "## Blended Impact on Existing Business",
        "",
        f"Current baseline: {_dollar(monthly_run_rate)}/mo run rate | "
        f"{_pct(base_margin)} gross margin ({_pct(base_cogs)} COGS) | "
        f"24-mo comparable: {_dollar_k(base_rev_24mo)}",
        "",
        "| Scenario | New Revenue (24mo) | Blended Margin | Margin Change |",
        "|----------|-------------------|----------------|---------------|",
    ]

    for r in results:
        new_rev = r["summary"]["total_revenue_24mo"]
        new_margin = 1.0 - _derive_cogs_pct(r)
        blended = calculate_blended_margin_impact(base_rev_24mo, base_margin, new_rev, new_margin)
        delta = blended - base_margin
        sign = "+" if delta >= 0 else ""
        lines.append(
            f"| {r['name']} | {_dollar_k(new_rev)} | {_pct(blended)} "
            f"| {sign}{delta * 100:.1f}pp |"
        )

    return "\n".join(lines)


def format_full_report(baseline: dict, results: list[dict]) -> str:
    """Combine all sections into a single markdown document."""
    today = date.today().isoformat()
    sections = [
        f"# Tibetan Spirit — Line Extension Analysis",
        f"Generated: {today}",
        "",
        format_comparison_table(results),
        "",
        format_blended_impact(baseline, results),
        "",
        "## Detailed Scenarios",
    ]
    for r in results:
        sections.extend(["", format_scenario_summary(r)])

    return "\n".join(sections)


def save_json_output(results: list[dict], output_dir: str | Path) -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"scenarios-{date.today().isoformat()}.json"
    path.write_text(json.dumps(results, indent=2, default=str))
    return path


def save_markdown_report(baseline: dict, results: list[dict], output_dir: str | Path) -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"financial-model-{date.today().isoformat()}.md"
    path.write_text(format_full_report(baseline, results))
    return path
