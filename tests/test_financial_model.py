"""Tests for financial scenario projection math.

All functions live in scripts/financial_model/analysis.py (not yet implemented).
These tests are intentionally RED — they will fail until the implementation is written.
"""

import math
import pytest

from scripts.financial_model.analysis import (
    calculate_monthly_revenue,
    interpolate_ramp,
    calculate_gross_profit,
    calculate_breakeven_months,
    calculate_blended_margin_impact,
    calculate_sensitivity,
    project_24_months,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_ramp():
    """Standard ramp profile: slow start, plateaus at month 12+."""
    return {
        "month_1": 50,
        "month_6": 150,
        "month_12": 300,
        "month_24": 400,
    }


@pytest.fixture
def sample_scenario(sample_ramp):
    """Minimal scenario dict for project_24_months."""
    return {
        "asp": 85.00,
        "cogs_pct": 0.45,
        "ramp": sample_ramp,
        "upfront_investment": 10_000.00,
        "ongoing_monthly": {
            "storage": 200.00,
            "marketing": 500.00,
        },
    }


# ---------------------------------------------------------------------------
# 1. calculate_monthly_revenue
# ---------------------------------------------------------------------------

class TestCalculateMonthlyRevenue:

    def test_basic_multiplication(self):
        """Revenue is simply ASP × orders."""
        assert calculate_monthly_revenue(asp=100.0, orders_per_month=50) == 5_000.0

    def test_fractional_asp(self):
        """Fractional ASP values round-trip correctly."""
        result = calculate_monthly_revenue(asp=85.50, orders_per_month=200)
        assert result == pytest.approx(17_100.0)

    def test_zero_orders(self):
        """Zero orders → zero revenue, regardless of ASP."""
        assert calculate_monthly_revenue(asp=99.99, orders_per_month=0) == 0.0

    def test_zero_asp(self):
        """Zero ASP → zero revenue, regardless of order count."""
        assert calculate_monthly_revenue(asp=0.0, orders_per_month=500) == 0.0

    def test_returns_float(self):
        """Return type is always float."""
        result = calculate_monthly_revenue(asp=10, orders_per_month=10)
        assert isinstance(result, float)


# ---------------------------------------------------------------------------
# 2. interpolate_ramp
# ---------------------------------------------------------------------------

class TestInterpolateRamp:

    def test_month_1_exact(self, sample_ramp):
        """Month 1 returns ramp_points['month_1'] exactly."""
        assert interpolate_ramp(sample_ramp, month=1) == 50.0

    def test_month_6_exact(self, sample_ramp):
        """Month 6 returns ramp_points['month_6'] exactly."""
        assert interpolate_ramp(sample_ramp, month=6) == 150.0

    def test_month_12_exact(self, sample_ramp):
        """Month 12 returns ramp_points['month_12'] exactly."""
        assert interpolate_ramp(sample_ramp, month=12) == 300.0

    def test_month_24_exact(self, sample_ramp):
        """Month 24 returns ramp_points['month_24'] exactly."""
        assert interpolate_ramp(sample_ramp, month=24) == 400.0

    def test_midpoint_month_3(self, sample_ramp):
        """Month 3 is midpoint between month_1 and month_6: (50+150)/2 = 100."""
        # Linear interpolation between month 1 (50) and month 6 (150):
        # fraction = (3-1)/(6-1) = 2/5 = 0.4
        # result = 50 + 0.4 * (150-50) = 50 + 40 = 90
        result = interpolate_ramp(sample_ramp, month=3)
        assert result == pytest.approx(90.0)

    def test_interpolation_month_9(self, sample_ramp):
        """Month 9 interpolates between month_6 (150) and month_12 (300)."""
        # fraction = (9-6)/(12-6) = 3/6 = 0.5
        # result = 150 + 0.5 * (300-150) = 225
        result = interpolate_ramp(sample_ramp, month=9)
        assert result == pytest.approx(225.0)

    def test_interpolation_month_18(self, sample_ramp):
        """Month 18 interpolates between month_12 (300) and month_24 (400)."""
        # fraction = (18-12)/(24-12) = 6/12 = 0.5
        # result = 300 + 0.5 * (400-300) = 350
        result = interpolate_ramp(sample_ramp, month=18)
        assert result == pytest.approx(350.0)

    def test_flat_ramp_returns_constant(self):
        """If all ramp points are equal, all months return that value."""
        flat_ramp = {"month_1": 100, "month_6": 100, "month_12": 100, "month_24": 100}
        for month in [1, 3, 6, 12, 18, 24]:
            assert interpolate_ramp(flat_ramp, month=month) == pytest.approx(100.0)


# ---------------------------------------------------------------------------
# 3. calculate_gross_profit
# ---------------------------------------------------------------------------

class TestCalculateGrossProfit:

    def test_standard_margin(self):
        """45% COGS → 55% gross margin on $10,000 revenue = $5,500."""
        assert calculate_gross_profit(revenue=10_000.0, cogs_pct=0.45) == pytest.approx(5_500.0)

    def test_zero_cogs(self):
        """0% COGS → 100% gross margin (revenue = gross profit)."""
        assert calculate_gross_profit(revenue=5_000.0, cogs_pct=0.0) == pytest.approx(5_000.0)

    def test_full_cogs(self):
        """100% COGS → 0 gross profit."""
        assert calculate_gross_profit(revenue=5_000.0, cogs_pct=1.0) == pytest.approx(0.0)

    def test_zero_revenue(self):
        """Zero revenue → zero gross profit regardless of COGS %."""
        assert calculate_gross_profit(revenue=0.0, cogs_pct=0.45) == pytest.approx(0.0)

    def test_fractional_cogs_precision(self):
        """COGS of 33.33% on $3,000 revenue."""
        result = calculate_gross_profit(revenue=3_000.0, cogs_pct=1 / 3)
        assert result == pytest.approx(2_000.0, rel=1e-4)


# ---------------------------------------------------------------------------
# 4. calculate_breakeven_months
# ---------------------------------------------------------------------------

class TestCalculateBreakevenMonths:

    def test_standard_breakeven(self):
        """$10,000 investment / $1,000/month GP = 10 months."""
        assert calculate_breakeven_months(
            upfront_investment=10_000.0,
            monthly_gross_profit=1_000.0,
        ) == pytest.approx(10.0)

    def test_fractional_breakeven(self):
        """$10,000 / $3,000/month = 3.333... months."""
        result = calculate_breakeven_months(
            upfront_investment=10_000.0,
            monthly_gross_profit=3_000.0,
        )
        assert result == pytest.approx(10_000 / 3_000)

    def test_zero_gross_profit_returns_infinity(self):
        """Zero monthly GP → infinite breakeven (never breaks even)."""
        result = calculate_breakeven_months(
            upfront_investment=10_000.0,
            monthly_gross_profit=0.0,
        )
        assert result == float("inf")

    def test_zero_investment(self):
        """Zero investment → instant breakeven (0 months)."""
        result = calculate_breakeven_months(
            upfront_investment=0.0,
            monthly_gross_profit=1_000.0,
        )
        assert result == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# 5. calculate_blended_margin_impact
# ---------------------------------------------------------------------------

class TestCalculateBlendedMarginImpact:

    def test_equal_revenue_streams(self):
        """Two equal revenue streams average their margins: (0.6 + 0.4) / 2 = 0.5."""
        result = calculate_blended_margin_impact(
            baseline_revenue=10_000.0,
            baseline_margin=0.60,
            new_revenue=10_000.0,
            new_margin=0.40,
        )
        assert result == pytest.approx(0.50)

    def test_weighted_toward_larger_stream(self):
        """Larger revenue stream dominates blended margin."""
        # 90% weight on 60% margin, 10% on 20% margin → 0.9*0.6 + 0.1*0.2 = 0.56
        result = calculate_blended_margin_impact(
            baseline_revenue=90_000.0,
            baseline_margin=0.60,
            new_revenue=10_000.0,
            new_margin=0.20,
        )
        assert result == pytest.approx(0.56)

    def test_zero_new_revenue_returns_baseline_margin(self):
        """Adding zero new revenue leaves margin unchanged."""
        result = calculate_blended_margin_impact(
            baseline_revenue=10_000.0,
            baseline_margin=0.55,
            new_revenue=0.0,
            new_margin=0.0,
        )
        assert result == pytest.approx(0.55)

    def test_zero_total_revenue_returns_zero(self):
        """Both streams at zero → return 0.0, not division error."""
        result = calculate_blended_margin_impact(
            baseline_revenue=0.0,
            baseline_margin=0.50,
            new_revenue=0.0,
            new_margin=0.50,
        )
        assert result == 0.0

    def test_same_margin_returns_same(self):
        """If both streams share a margin, blended = that margin."""
        result = calculate_blended_margin_impact(
            baseline_revenue=5_000.0,
            baseline_margin=0.55,
            new_revenue=15_000.0,
            new_margin=0.55,
        )
        assert result == pytest.approx(0.55)


# ---------------------------------------------------------------------------
# 6. calculate_sensitivity
# ---------------------------------------------------------------------------

class TestCalculateSensitivity:

    def test_returns_five_rows(self):
        """Sensitivity table always has exactly 5 rows (one per multiplier)."""
        result = calculate_sensitivity(
            base_volume=100,
            volume_multipliers=[0.5, 0.75, 1.0, 1.25, 1.5],
            asp=80.0,
            cogs_pct=0.45,
        )
        assert len(result) == 5

    def test_base_case_multiplier_1(self):
        """At 1.0× multiplier, orders = base_volume, revenue and GP are correct."""
        result = calculate_sensitivity(
            base_volume=100,
            volume_multipliers=[0.5, 0.75, 1.0, 1.25, 1.5],
            asp=80.0,
            cogs_pct=0.45,
        )
        base_row = next(r for r in result if r["multiplier"] == 1.0)
        assert base_row["orders"] == pytest.approx(100.0)
        assert base_row["revenue"] == pytest.approx(8_000.0)
        assert base_row["gross_profit"] == pytest.approx(4_400.0)

    def test_half_volume_multiplier(self):
        """At 0.5× multiplier, orders and revenue are halved."""
        result = calculate_sensitivity(
            base_volume=200,
            volume_multipliers=[0.5, 0.75, 1.0, 1.25, 1.5],
            asp=100.0,
            cogs_pct=0.40,
        )
        half_row = next(r for r in result if r["multiplier"] == 0.5)
        assert half_row["orders"] == pytest.approx(100.0)
        assert half_row["revenue"] == pytest.approx(10_000.0)
        assert half_row["gross_profit"] == pytest.approx(6_000.0)

    def test_result_dict_has_required_keys(self):
        """Every row has multiplier, orders, revenue, gross_profit keys."""
        result = calculate_sensitivity(
            base_volume=50,
            volume_multipliers=[0.5, 0.75, 1.0, 1.25, 1.5],
            asp=60.0,
            cogs_pct=0.50,
        )
        required_keys = {"multiplier", "orders", "revenue", "gross_profit"}
        for row in result:
            assert required_keys.issubset(row.keys())

    def test_gross_profit_monotonically_increases(self):
        """Higher multipliers → higher gross profit (given positive ASP and margin)."""
        result = calculate_sensitivity(
            base_volume=100,
            volume_multipliers=[0.5, 0.75, 1.0, 1.25, 1.5],
            asp=80.0,
            cogs_pct=0.45,
        )
        gross_profits = [r["gross_profit"] for r in result]
        assert gross_profits == sorted(gross_profits)


# ---------------------------------------------------------------------------
# 7. project_24_months
# ---------------------------------------------------------------------------

class TestProject24Months:

    def test_returns_24_rows(self, sample_scenario):
        """Projection returns exactly 24 monthly rows."""
        result = project_24_months(sample_scenario)
        assert len(result) == 24

    def test_month_numbers_are_sequential(self, sample_scenario):
        """Month field runs 1 through 24 in order."""
        result = project_24_months(sample_scenario)
        months = [row["month"] for row in result]
        assert months == list(range(1, 25))

    def test_required_keys_present(self, sample_scenario):
        """Every row has all required fields."""
        result = project_24_months(sample_scenario)
        required_keys = {"month", "orders", "revenue", "gross_profit", "net_monthly", "cumulative_net"}
        for row in result:
            assert required_keys.issubset(row.keys())

    def test_month_1_revenue_math(self, sample_scenario):
        """Month 1: orders=50, ASP=85 → revenue=4,250."""
        result = project_24_months(sample_scenario)
        row = result[0]
        assert row["month"] == 1
        assert row["orders"] == pytest.approx(50.0)
        assert row["revenue"] == pytest.approx(50.0 * 85.0)

    def test_month_1_gross_profit(self, sample_scenario):
        """Month 1: revenue=4,250, COGS=45% → GP=2,337.50."""
        result = project_24_months(sample_scenario)
        row = result[0]
        expected_gp = 50.0 * 85.0 * (1 - 0.45)
        assert row["gross_profit"] == pytest.approx(expected_gp)

    def test_month_1_net_monthly(self, sample_scenario):
        """Month 1: GP minus ongoing costs (200+500=700) = net_monthly."""
        result = project_24_months(sample_scenario)
        row = result[0]
        expected_gp = 50.0 * 85.0 * (1 - 0.45)
        expected_net = expected_gp - 700.0
        assert row["net_monthly"] == pytest.approx(expected_net)

    def test_month_1_cumulative_net_includes_upfront(self, sample_scenario):
        """Month 1 cumulative_net = net_monthly[0] - upfront_investment."""
        result = project_24_months(sample_scenario)
        row1 = result[0]
        expected_gp = 50.0 * 85.0 * (1 - 0.45)
        expected_net = expected_gp - 700.0
        expected_cumulative = expected_net - 10_000.0
        assert row1["cumulative_net"] == pytest.approx(expected_cumulative)

    def test_cumulative_net_is_running_sum(self, sample_scenario):
        """cumulative_net[n] = sum of net_monthly[0..n] minus upfront_investment."""
        result = project_24_months(sample_scenario)
        running = -sample_scenario["upfront_investment"]
        for row in result:
            running += row["net_monthly"]
            assert row["cumulative_net"] == pytest.approx(running)

    def test_cumulative_net_eventually_positive(self, sample_scenario):
        """With a profitable ramp, cumulative_net should turn positive before month 24."""
        result = project_24_months(sample_scenario)
        final_cumulative = result[-1]["cumulative_net"]
        # At month 24: orders=400, revenue=34,000, GP=18,700, net=18,000/mo
        # This scenario should clearly be profitable by month 24
        assert final_cumulative > 0, "Scenario should be profitable by month 24"
