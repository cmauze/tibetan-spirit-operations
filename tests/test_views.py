"""Tests for ts_shared.views — materialized view refresh."""

from unittest.mock import MagicMock, patch

import pytest


def test_refresh_views_unknown_view():
    """Unknown view names are skipped."""
    from ts_shared.views import refresh_views

    results = refresh_views(["nonexistent_view"])
    assert results["nonexistent_view"] is False


def test_refresh_views_known_views_list():
    from ts_shared.views import KNOWN_VIEWS

    assert "channel_profitability_monthly" in KNOWN_VIEWS
    assert "product_margin_detail" in KNOWN_VIEWS
    assert "inventory_health" in KNOWN_VIEWS
    assert "marketing_roas_trailing" in KNOWN_VIEWS


@patch("ts_shared.supabase_client.get_client")
def test_refresh_views_calls_rpc(mock_get_client):
    mock_client = MagicMock()
    rpc_mock = MagicMock()
    rpc_mock.execute.return_value = MagicMock()
    mock_client.rpc.return_value = rpc_mock
    mock_get_client.return_value = mock_client

    from ts_shared.views import refresh_views

    results = refresh_views(["channel_profitability_monthly"])
    assert results["channel_profitability_monthly"] is True
    mock_client.rpc.assert_called_once_with(
        "refresh_materialized_view",
        {"view_name": "channel_profitability_monthly"},
    )
