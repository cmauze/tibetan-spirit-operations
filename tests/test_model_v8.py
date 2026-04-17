"""Tests for financial model v8 — product-line-based P&L engine."""
import pytest
import yaml
from scripts.financial_model.model import (
    compute_platform_fee_rate,
    compute_marketing_spend,
    compute_personnel_cost,
    build_monthly_pnl,
    build_scenarios,
)


@pytest.fixture
def v8_config():
    with open("scripts/financial_model/config/model_v8.yaml") as f:
        return yaml.safe_load(f)


class TestComputePlatformFeeRate:
    def test_month_1_shopify_only(self):
        schedule = [
            {"through_month": 2, "rate": 0.06},
            {"through_month": 12, "rate": 0.07},
            {"through_month": 36, "rate": 0.09},
        ]
        assert compute_platform_fee_rate(1, schedule) == pytest.approx(0.06)

    def test_month_3_etsy_added(self):
        schedule = [
            {"through_month": 2, "rate": 0.06},
            {"through_month": 6, "rate": 0.065},
            {"through_month": 36, "rate": 0.09},
        ]
        assert compute_platform_fee_rate(3, schedule) == pytest.approx(0.065)

    def test_past_schedule_uses_last(self):
        schedule = [
            {"through_month": 12, "rate": 0.07},
            {"through_month": 24, "rate": 0.09},
        ]
        assert compute_platform_fee_rate(30, schedule) == pytest.approx(0.09)


class TestMarketingRampV8:
    @pytest.fixture
    def mkt_cfg(self):
        return {
            "ramp_schedule": [
                {"through_month": 1, "pct": 0.0},
                {"through_month": 4, "pct": 0.208},
                {"through_month": 12, "pct": 0.63},
            ],
            "pct_of_product_revenue_y2": 0.47,
            "pct_of_product_revenue_y3": 0.31,
            "holiday_months": [10, 11, 12],
            "holiday_multiplier_y1": 1.25,
            "holiday_multiplier_y2": 2.0,
            "holiday_multiplier_y3": 2.0,
        }

    def test_month_1_zero_spend(self, mkt_cfg):
        result = compute_marketing_spend(
            product_revenue=10000, month=1, calendar_month=6,
            marketing_cfg=mkt_cfg,
        )
        assert result == pytest.approx(0.0)

    def test_month_2_learning_rate(self, mkt_cfg):
        result = compute_marketing_spend(
            product_revenue=10000, month=2, calendar_month=7,
            marketing_cfg=mkt_cfg,
        )
        assert result == pytest.approx(2080.0)

    def test_month_5_full_rate(self, mkt_cfg):
        result = compute_marketing_spend(
            product_revenue=10000, month=5, calendar_month=10,
            marketing_cfg=mkt_cfg,
        )
        assert result == pytest.approx(10000 * 0.63 * 1.25)

    def test_y1_holiday_multiplier(self, mkt_cfg):
        result = compute_marketing_spend(
            product_revenue=10000, month=7, calendar_month=12,
            marketing_cfg=mkt_cfg,
        )
        assert result == pytest.approx(10000 * 0.63 * 1.25)

    def test_y2_holiday_multiplier(self, mkt_cfg):
        result = compute_marketing_spend(
            product_revenue=10000, month=17, calendar_month=10,
            marketing_cfg=mkt_cfg,
        )
        assert result == pytest.approx(10000 * 0.47 * 2.0)

    def test_y2_non_holiday(self, mkt_cfg):
        result = compute_marketing_spend(
            product_revenue=10000, month=14, calendar_month=7,
            marketing_cfg=mkt_cfg,
        )
        assert result == pytest.approx(10000 * 0.47)


class TestPersonnelV8:
    def test_y1_flat(self):
        cfg = {"monthly_y1": 6833, "monthly_y2": 7500, "monthly_y3": 8500}
        assert compute_personnel_cost(1, cfg) == pytest.approx(6833.0)
        assert compute_personnel_cost(4, cfg) == pytest.approx(6833.0)
        assert compute_personnel_cost(12, cfg) == pytest.approx(6833.0)

    def test_y2(self):
        cfg = {"monthly_y1": 6833, "monthly_y2": 7500, "monthly_y3": 8500}
        assert compute_personnel_cost(13, cfg) == pytest.approx(7500.0)

    def test_y3(self):
        cfg = {"monthly_y1": 6833, "monthly_y2": 7500, "monthly_y3": 8500}
        assert compute_personnel_cost(25, cfg) == pytest.approx(8500.0)


class TestBuildMonthlyPnlV8:
    def test_returns_36_months(self, v8_config):
        pnl = build_monthly_pnl(v8_config)
        assert len(pnl["month_labels"]) == 36
        assert len(pnl["d2c_total"]) == 36
        assert len(pnl["ebitda"]) == 36

    def test_has_product_lines(self, v8_config):
        pnl = build_monthly_pnl(v8_config)
        assert "shrine_core" in pnl["d2c_channels"]
        assert "incense" in pnl["d2c_channels"]
        assert "malas" in pnl["d2c_channels"]
        assert "premium" in pnl["d2c_channels"]

    def test_shrine_core_m1(self, v8_config):
        pnl = build_monthly_pnl(v8_config)
        assert pnl["d2c_channels"]["shrine_core"][0] == pytest.approx(2822.0)

    def test_premium_zero_before_m7(self, v8_config):
        pnl = build_monthly_pnl(v8_config)
        for i in range(6):
            assert pnl["d2c_channels"]["premium"][i] == 0.0

    def test_premium_m7_revenue(self, v8_config):
        pnl = build_monthly_pnl(v8_config)
        assert pnl["d2c_channels"]["premium"][6] == pytest.approx(1500.0)

    def test_m1_marketing_is_zero(self, v8_config):
        pnl = build_monthly_pnl(v8_config)
        assert pnl["costs"]["marketing"][0] == pytest.approx(0.0)

    def test_m2_marketing_is_learning_rate(self, v8_config):
        pnl = build_monthly_pnl(v8_config)
        d2c_m2 = pnl["d2c_total"][1]
        expected = d2c_m2 * 0.208
        assert pnl["costs"]["marketing"][1] == pytest.approx(expected)

    def test_personnel_flat_y1(self, v8_config):
        pnl = build_monthly_pnl(v8_config)
        for i in range(12):
            assert pnl["costs"]["personnel"][i] == pytest.approx(6833.0)

    def test_travels_y1_zero(self, v8_config):
        pnl = build_monthly_pnl(v8_config)
        assert sum(pnl["travels"][:12]) == 0.0

    def test_yearly_summary_exists(self, v8_config):
        pnl = build_monthly_pnl(v8_config)
        for y in ["Y1", "Y2", "Y3"]:
            assert y in pnl["yearly_summary"]
            assert pnl["yearly_summary"][y]["total_revenue"] > 0

    def test_first_month_label(self, v8_config):
        pnl = build_monthly_pnl(v8_config)
        assert pnl["month_labels"][0] == "Jun 26"

    def test_d2c_total_m1_is_7500(self, v8_config):
        pnl = build_monthly_pnl(v8_config)
        assert pnl["d2c_total"][0] == pytest.approx(7500.0)

    def test_cogs_per_line_uses_correct_rate(self, v8_config):
        pnl = build_monthly_pnl(v8_config)
        incense_rev_m1 = pnl["d2c_channels"]["incense"][0]
        incense_cogs_m1 = pnl["cogs_by_channel"]["incense"][0]
        assert incense_cogs_m1 == pytest.approx(incense_rev_m1 * 0.25)


class TestBuildScenariosV8:
    def test_four_scenarios(self, v8_config):
        scenarios = build_scenarios(v8_config)
        assert len(scenarios) == 4
        assert "Core D2C" in scenarios
        assert "Full Business" in scenarios

    def test_core_has_no_premium(self, v8_config):
        scenarios = build_scenarios(v8_config)
        core = scenarios["Core D2C"]
        assert all(v == 0.0 for v in core["d2c_channels"]["premium"])

    def test_full_business_has_travels(self, v8_config):
        scenarios = build_scenarios(v8_config)
        full = scenarios["Full Business"]
        assert sum(full["travels"][12:24]) > 0
