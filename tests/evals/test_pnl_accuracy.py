"""Eval tests for the weekly_pnl workflow.

Tests P&L calculation accuracy, week-over-week comparison logic, and edge cases.
No live API calls — all data is fixture-based.
"""

import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "lib"))

from workflows.weekly_pnl.run import (
    calculate_pnl, calculate_wow_change, get_cogs, get_landed_cost,
    build_pnl_prompt, SHOPIFY_PCT_FEE, SHOPIFY_FLAT_FEE,
)


# ---------------------------------------------------------------------------
# Fixture data
# ---------------------------------------------------------------------------

PRODUCTS = {
    "TS-BOWL-HH-5IN": {
        "sku": "TS-BOWL-HH-5IN",
        "title": "Hand-Hammered Singing Bowl 5 inch",
        "price": "89.95",
        "cogs_confirmed": 22.50,
        "cogs_estimated": None,
        "cogs_confidence": "confirmed",
        "freight_per_unit": 2.50,
        "duty_rate": 0.03,
    },
    "TS-INC-NADO-HAP": {
        "sku": "TS-INC-NADO-HAP",
        "title": "Nado Poizokhang Happiness Incense",
        "price": "15.00",
        "cogs_confirmed": None,
        "cogs_estimated": 3.50,
        "cogs_confidence": "estimated",
        "freight_per_unit": 0.45,
        "duty_rate": 0.0,
    },
    "TS-MALA-BODHI-108": {
        "sku": "TS-MALA-BODHI-108",
        "title": "Bodhi Seed Mala 108 Beads",
        "price": "35.00",
        "cogs_confirmed": None,
        "cogs_estimated": None,
        "cogs_confidence": "unknown",
        "freight_per_unit": None,
        "duty_rate": None,
    },
}


def _make_order(order_number, total_price, line_items):
    return {
        "order_number": str(order_number),
        "total_price": str(total_price),
        "line_items": line_items,
    }


WEEK_ORDERS = [
    _make_order(20210, 89.95, [
        {"sku": "TS-BOWL-HH-5IN", "title": "Hand-Hammered Singing Bowl 5 inch",
         "price": "89.95", "quantity": 1},
    ]),
    _make_order(20211, 45.00, [
        {"sku": "TS-INC-NADO-HAP", "title": "Nado Incense",
         "price": "15.00", "quantity": 2},
        {"sku": "TS-MALA-BODHI-108", "title": "Bodhi Seed Mala",
         "price": "15.00", "quantity": 1},
    ]),
    _make_order(20212, 89.95, [
        {"sku": "TS-BOWL-HH-5IN", "title": "Hand-Hammered Singing Bowl 5 inch",
         "price": "89.95", "quantity": 1},
    ]),
]


# ---------------------------------------------------------------------------
# get_cogs / get_landed_cost
# ---------------------------------------------------------------------------


class TestCOGS:
    def test_confirmed_cogs_preferred(self):
        assert get_cogs(PRODUCTS["TS-BOWL-HH-5IN"]) == 22.50

    def test_estimated_fallback(self):
        assert get_cogs(PRODUCTS["TS-INC-NADO-HAP"]) == 3.50

    def test_unknown_returns_zero(self):
        assert get_cogs(PRODUCTS["TS-MALA-BODHI-108"]) == 0.0

    def test_landed_cost_includes_freight_and_duty(self):
        cost = get_landed_cost(PRODUCTS["TS-BOWL-HH-5IN"])
        expected = 22.50 + 2.50 + (22.50 * 0.03)  # = 25.675
        assert abs(cost - expected) < 0.001

    def test_landed_cost_no_duty(self):
        cost = get_landed_cost(PRODUCTS["TS-INC-NADO-HAP"])
        expected = 3.50 + 0.45 + 0  # = 3.95
        assert abs(cost - expected) < 0.001

    def test_landed_cost_unknown_product(self):
        cost = get_landed_cost(PRODUCTS["TS-MALA-BODHI-108"])
        assert cost == 0.0


# ---------------------------------------------------------------------------
# calculate_pnl
# ---------------------------------------------------------------------------


class TestCalculatePNL:
    def test_empty_orders(self):
        result = calculate_pnl([], PRODUCTS)
        assert result["revenue"] == 0.0
        assert result["order_count"] == 0
        assert result["margin_pct"] == 0.0

    def test_revenue_sum(self):
        result = calculate_pnl(WEEK_ORDERS, PRODUCTS)
        expected = 89.95 + 45.00 + 89.95
        assert result["revenue"] == round(expected, 2)

    def test_order_count(self):
        result = calculate_pnl(WEEK_ORDERS, PRODUCTS)
        assert result["order_count"] == 3

    def test_aov(self):
        result = calculate_pnl(WEEK_ORDERS, PRODUCTS)
        expected_rev = 89.95 + 45.00 + 89.95
        assert result["aov"] == round(expected_rev / 3, 2)

    def test_cogs_calculation(self):
        """Verify COGS = sum of landed costs across all line items."""
        result = calculate_pnl(WEEK_ORDERS, PRODUCTS)
        bowl_landed = 22.50 + 2.50 + (22.50 * 0.03)  # 25.675
        incense_landed = 3.50 + 0.45  # 3.95
        mala_landed = 0.0  # unknown

        expected_cogs = (bowl_landed * 2) + (incense_landed * 2) + (mala_landed * 1)
        assert abs(result["cogs"] - round(expected_cogs, 2)) < 0.01

    def test_fees_calculation(self):
        """Verify Shopify fees = 2.5% + $0.30 per order."""
        result = calculate_pnl(WEEK_ORDERS, PRODUCTS)
        expected_fees = sum(
            float(o["total_price"]) * SHOPIFY_PCT_FEE + SHOPIFY_FLAT_FEE
            for o in WEEK_ORDERS
        )
        assert abs(result["fees"] - round(expected_fees, 2)) < 0.01

    def test_gross_profit(self):
        result = calculate_pnl(WEEK_ORDERS, PRODUCTS)
        expected = result["revenue"] - result["cogs"] - result["fees"]
        assert abs(result["gross_profit"] - round(expected, 2)) < 0.01

    def test_margin_pct(self):
        result = calculate_pnl(WEEK_ORDERS, PRODUCTS)
        expected = result["gross_profit"] / result["revenue"] * 100
        assert abs(result["margin_pct"] - round(expected, 1)) < 0.1

    def test_top_products_sorted_by_revenue(self):
        result = calculate_pnl(WEEK_ORDERS, PRODUCTS)
        revenues = [p["revenue"] for p in result["top_products"]]
        assert revenues == sorted(revenues, reverse=True)

    def test_cogs_confidence_counts(self):
        result = calculate_pnl(WEEK_ORDERS, PRODUCTS)
        assert result["cogs_confirmed_count"] == 1  # bowl
        assert result["cogs_estimated_count"] == 1  # incense
        assert result["cogs_unknown_count"] == 1    # mala

    def test_single_order(self):
        orders = [WEEK_ORDERS[0]]
        result = calculate_pnl(orders, PRODUCTS)
        assert result["order_count"] == 1
        assert result["revenue"] == 89.95

    def test_missing_sku_in_products(self):
        """Orders with SKUs not in products dict should use 0 COGS."""
        orders = [
            _make_order(99, 50.00, [
                {"sku": "UNKNOWN-SKU", "title": "Mystery Item",
                 "price": "50.00", "quantity": 1},
            ]),
        ]
        result = calculate_pnl(orders, PRODUCTS)
        assert result["revenue"] == 50.00
        assert result["cogs"] == 0.0


# ---------------------------------------------------------------------------
# calculate_wow_change
# ---------------------------------------------------------------------------


class TestWoWChange:
    def test_positive_growth(self):
        current = {"revenue": 1000, "gross_profit": 500, "order_count": 10,
                    "aov": 100, "margin_pct": 50}
        prior = {"revenue": 800, "gross_profit": 400, "order_count": 8,
                 "aov": 100, "margin_pct": 50}
        wow = calculate_wow_change(current, prior)
        assert wow["revenue"]["direction"] == "up"
        assert wow["revenue"]["change_pct"] == 25.0

    def test_negative_decline(self):
        current = {"revenue": 500, "gross_profit": 250, "order_count": 5,
                    "aov": 100, "margin_pct": 50}
        prior = {"revenue": 1000, "gross_profit": 500, "order_count": 10,
                 "aov": 100, "margin_pct": 50}
        wow = calculate_wow_change(current, prior)
        assert wow["revenue"]["direction"] == "down"
        assert wow["revenue"]["change_pct"] == -50.0

    def test_flat_within_threshold(self):
        current = {"revenue": 100, "gross_profit": 50, "order_count": 10,
                    "aov": 10, "margin_pct": 50}
        prior = {"revenue": 99, "gross_profit": 50, "order_count": 10,
                 "aov": 9.9, "margin_pct": 50}
        wow = calculate_wow_change(current, prior)
        assert wow["revenue"]["direction"] == "flat"

    def test_zero_prior_week(self):
        """Zero revenue prior week should show 100% increase."""
        current = {"revenue": 500, "gross_profit": 250, "order_count": 5,
                    "aov": 100, "margin_pct": 50}
        prior = {"revenue": 0, "gross_profit": 0, "order_count": 0,
                 "aov": 0, "margin_pct": 0}
        wow = calculate_wow_change(current, prior)
        assert wow["revenue"]["change_pct"] == 100.0
        assert wow["revenue"]["direction"] == "up"

    def test_both_zero(self):
        current = {"revenue": 0, "gross_profit": 0, "order_count": 0,
                    "aov": 0, "margin_pct": 0}
        prior = {"revenue": 0, "gross_profit": 0, "order_count": 0,
                 "aov": 0, "margin_pct": 0}
        wow = calculate_wow_change(current, prior)
        assert wow["revenue"]["change_pct"] == 0.0
        assert wow["revenue"]["direction"] == "flat"


# ---------------------------------------------------------------------------
# build_pnl_prompt
# ---------------------------------------------------------------------------


class TestBuildPNLPrompt:
    def test_includes_financial_data(self):
        pnl = calculate_pnl(WEEK_ORDERS, PRODUCTS)
        wow = calculate_wow_change(pnl, pnl)
        prompt = build_pnl_prompt(pnl, pnl, wow, "2026-03-23", "2026-03-30")
        assert f"${pnl['revenue']:.2f}" in prompt
        assert f"${pnl['cogs']:.2f}" in prompt

    def test_includes_decision_support(self):
        pnl = calculate_pnl([], PRODUCTS)
        wow = calculate_wow_change(pnl, pnl)
        prompt = build_pnl_prompt(pnl, pnl, wow, "2026-03-23", "2026-03-30")
        assert "STATUS: GREEN/YELLOW/RED" in prompt
        assert "VALUES CHECK:" in prompt

    def test_includes_cogs_quality(self):
        pnl = calculate_pnl(WEEK_ORDERS, PRODUCTS)
        wow = calculate_wow_change(pnl, pnl)
        prompt = build_pnl_prompt(pnl, pnl, wow, "2026-03-23", "2026-03-30")
        assert "Confirmed:" in prompt
        assert "Unknown:" in prompt


# ---------------------------------------------------------------------------
# Full run (mocked)
# ---------------------------------------------------------------------------


class TestWeeklyPNLRun:
    @patch("workflows.weekly_pnl.run.notify")
    @patch("workflows.weekly_pnl.run.log_invocation")
    @patch("workflows.weekly_pnl.run.update_workflow_health")
    @patch("workflows.weekly_pnl.run.log_workflow_run")
    @patch("workflows.weekly_pnl.run.create_task")
    @patch("workflows.weekly_pnl.run.call_claude")
    @patch("workflows.weekly_pnl.run.load_skills")
    @patch("workflows.weekly_pnl.run.get_client")
    def test_full_run(
        self,
        mock_get_client,
        mock_load_skills,
        mock_call_claude,
        mock_create_task,
        mock_log_run,
        mock_health,
        mock_log_inv,
        mock_notify,
    ):
        from workflows.weekly_pnl.run import run

        # Mock Supabase
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        table_mock = MagicMock()
        table_mock.select.return_value = table_mock
        table_mock.eq.return_value = table_mock
        table_mock.gte.return_value = table_mock
        table_mock.lt.return_value = table_mock

        call_count = [0]

        def table_execute():
            call_count[0] += 1
            if call_count[0] == 1:
                # products query
                return MagicMock(data=list(PRODUCTS.values()))
            elif call_count[0] == 2:
                # current week orders
                return MagicMock(data=WEEK_ORDERS)
            elif call_count[0] == 3:
                # prior week orders
                return MagicMock(data=[WEEK_ORDERS[0]])
            return MagicMock(data=[])

        table_mock.execute.side_effect = table_execute
        mock_client.table.return_value = table_mock

        # Mock skills
        mock_load_skills.return_value = ([], "skills content")

        # Mock Claude response
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="P&L Report\nSTATUS: GREEN")]
        mock_response.usage.input_tokens = 2000
        mock_response.usage.output_tokens = 800
        mock_response.usage.cache_read_input_tokens = 0
        mock_call_claude.return_value = mock_response

        mock_log_run.return_value = "run-789"
        mock_create_task.return_value = "task-012"

        result = run()

        assert result == "task-012"
        mock_call_claude.assert_called_once()
        mock_create_task.assert_called_once()

        # Verify task created as needs_review with ceo assignee
        task_kwargs = mock_create_task.call_args
        assert task_kwargs.kwargs["status"] == "needs_review"
        assert task_kwargs.kwargs["assignee"] == "ceo"
        assert task_kwargs.kwargs["priority"] == "P2"

        # Verify output contains P&L data
        output = task_kwargs.kwargs["output"]
        assert "revenue" in output
        assert "cogs" in output
        assert "week_over_week" in output
