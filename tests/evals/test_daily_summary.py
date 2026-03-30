"""Eval tests for the daily_summary workflow.

Tests metric calculations and prompt construction with mock data.
No live API calls — Claude responses are mocked.
"""

import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Ensure workflow module is importable
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "lib"))

from workflows.daily_summary.run import calculate_metrics, build_user_prompt


# ---------------------------------------------------------------------------
# Test data
# ---------------------------------------------------------------------------

def _make_order(
    order_number: int,
    total_price: float,
    line_items: list[dict],
    fulfillment_status: str = None,
    hours_ago: int = 0,
):
    """Create a mock order dict."""
    created = datetime.now(timezone.utc) - timedelta(hours=hours_ago)
    return {
        "id": f"order-{order_number}",
        "order_number": str(order_number),
        "total_price": str(total_price),
        "fulfillment_status": fulfillment_status,
        "created_at": created.isoformat(),
        "line_items": line_items,
    }


SAMPLE_ORDERS = [
    _make_order(
        20210, 89.95,
        [{"title": "Singing Bowl 5 inch", "price": "89.95", "quantity": 1}],
    ),
    _make_order(
        20211, 45.00,
        [
            {"title": "Nado Incense", "price": "15.00", "quantity": 2},
            {"title": "Bodhi Mala", "price": "15.00", "quantity": 1},
        ],
    ),
    _make_order(
        20212, 650.00,
        [{"title": "Large Thangka", "price": "650.00", "quantity": 1}],
    ),
    _make_order(
        20213, 22.50,
        [{"title": "Prayer Flags Set", "price": "22.50", "quantity": 1}],
    ),
    _make_order(
        20214, 120.00,
        [
            {"title": "Singing Bowl 5 inch", "price": "89.95", "quantity": 1},
            {"title": "Nado Incense", "price": "15.00", "quantity": 2},
        ],
    ),
]


# ---------------------------------------------------------------------------
# calculate_metrics tests
# ---------------------------------------------------------------------------


class TestCalculateMetrics:
    def test_empty_orders(self):
        result = calculate_metrics([])
        assert result["order_count"] == 0
        assert result["revenue"] == 0.0
        assert result["aov"] == 0.0
        assert result["top_products"] == []
        assert result["large_orders"] == []

    def test_order_count(self):
        result = calculate_metrics(SAMPLE_ORDERS)
        assert result["order_count"] == 5

    def test_revenue_sum(self):
        result = calculate_metrics(SAMPLE_ORDERS)
        expected = 89.95 + 45.00 + 650.00 + 22.50 + 120.00
        assert result["revenue"] == round(expected, 2)

    def test_aov(self):
        result = calculate_metrics(SAMPLE_ORDERS)
        expected_rev = 89.95 + 45.00 + 650.00 + 22.50 + 120.00
        expected_aov = expected_rev / 5
        assert result["aov"] == round(expected_aov, 2)

    def test_top_products_capped_at_5(self):
        result = calculate_metrics(SAMPLE_ORDERS)
        assert len(result["top_products"]) <= 5

    def test_top_products_sorted_desc(self):
        result = calculate_metrics(SAMPLE_ORDERS)
        revenues = [p["revenue"] for p in result["top_products"]]
        assert revenues == sorted(revenues, reverse=True)

    def test_singing_bowl_aggregated(self):
        """Singing Bowl 5 inch appears in orders 20210 and 20214."""
        result = calculate_metrics(SAMPLE_ORDERS)
        bowl = next(
            (p for p in result["top_products"] if "Singing Bowl" in p["title"]),
            None,
        )
        assert bowl is not None
        assert bowl["revenue"] == round(89.95 + 89.95, 2)

    def test_large_orders_over_500(self):
        result = calculate_metrics(SAMPLE_ORDERS)
        assert len(result["large_orders"]) == 1
        assert result["large_orders"][0]["order_number"] == "20212"
        assert result["large_orders"][0]["total"] == 650.00

    def test_no_large_orders(self):
        small_orders = [
            _make_order(1, 50.00, [{"title": "X", "price": "50.00", "quantity": 1}]),
        ]
        result = calculate_metrics(small_orders)
        assert result["large_orders"] == []


# ---------------------------------------------------------------------------
# build_user_prompt tests
# ---------------------------------------------------------------------------


class TestBuildUserPrompt:
    def test_includes_metrics(self):
        metrics = calculate_metrics(SAMPLE_ORDERS)
        prompt = build_user_prompt(metrics, [])
        assert "Orders today: 5" in prompt
        assert "$927.45" in prompt

    def test_includes_unfulfilled_flag(self):
        unfulfilled = [
            {"order_number": "20100", "total_price": "89.95", "created_at": "2026-03-28T10:00:00Z"}
        ]
        metrics = calculate_metrics(SAMPLE_ORDERS)
        prompt = build_user_prompt(metrics, unfulfilled)
        assert "20100" in prompt
        assert "1 total" in prompt

    def test_includes_decision_support_template(self):
        metrics = calculate_metrics([])
        prompt = build_user_prompt(metrics, [])
        assert "STATUS: GREEN/YELLOW/RED" in prompt
        assert "VALUES CHECK:" in prompt
        assert "COST:" in prompt

    def test_no_orders_formatting(self):
        metrics = calculate_metrics([])
        prompt = build_user_prompt(metrics, [])
        assert "Orders today: 0" in prompt
        assert "Revenue: $0.00" in prompt


# ---------------------------------------------------------------------------
# Full workflow run (mocked)
# ---------------------------------------------------------------------------


class TestDailySummaryRun:
    @patch("workflows.daily_summary.run.notify")
    @patch("workflows.daily_summary.run.log_invocation")
    @patch("workflows.daily_summary.run.update_workflow_health")
    @patch("workflows.daily_summary.run.log_workflow_run")
    @patch("workflows.daily_summary.run.create_task")
    @patch("workflows.daily_summary.run.call_claude")
    @patch("workflows.daily_summary.run.load_skills")
    @patch("workflows.daily_summary.run.get_client")
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
        from workflows.daily_summary.run import run

        # Mock Supabase queries
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        orders_table = MagicMock()
        orders_table.select.return_value = orders_table
        orders_table.gte.return_value = orders_table
        orders_table.is_.return_value = orders_table
        orders_table.lt.return_value = orders_table

        call_count = [0]

        def orders_execute():
            call_count[0] += 1
            if call_count[0] == 1:
                return MagicMock(data=SAMPLE_ORDERS)
            return MagicMock(data=[])

        orders_table.execute.side_effect = orders_execute
        mock_client.table.return_value = orders_table

        # Mock skills
        mock_load_skills.return_value = ([], "skills content")

        # Mock Claude response
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Daily summary text\nSTATUS: GREEN")]
        mock_response.usage.input_tokens = 500
        mock_response.usage.output_tokens = 200
        mock_response.usage.cache_read_input_tokens = 0
        mock_call_claude.return_value = mock_response

        # Mock dashboard ops
        mock_log_run.return_value = "run-123"
        mock_create_task.return_value = "task-456"

        result = run()

        assert result == "task-456"
        mock_call_claude.assert_called_once()
        mock_create_task.assert_called_once()
        mock_log_run.assert_called_once()
        mock_health.assert_called_once()
        mock_notify.assert_called_once()

        # Verify task was created with auto_logged status
        task_kwargs = mock_create_task.call_args
        assert task_kwargs.kwargs["status"] == "auto_logged"
        assert task_kwargs.kwargs["assignee"] == "ceo"
