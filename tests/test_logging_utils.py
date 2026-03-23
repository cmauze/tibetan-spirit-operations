"""Tests for skill invocation logging."""

import asyncio
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone

import pytest


@pytest.fixture
def mock_supabase():
    """Mock the Supabase client for logging tests."""
    client = MagicMock()
    table = MagicMock()
    table.insert.return_value = table
    table.execute.return_value = MagicMock(data=[{"id": "test-123"}])
    client.table.return_value = table
    return client, table


def test_log_invocation_returns_id(mock_supabase):
    """log_skill_invocation returns an invocation ID."""
    client, table = mock_supabase

    with patch("ts_shared.supabase_client.get_client", return_value=client):
        from ts_shared.logging_utils import log_skill_invocation

        result = asyncio.get_event_loop().run_until_complete(
            log_skill_invocation(
                agent_name="operations",
                skill_name="fulfillment-domestic",
                prompt="Route order #1042",
                result={"status": "routed", "route": "domestic"},
            )
        )

        assert result is not None
        assert isinstance(result, str)
        table.insert.assert_called_once()


def test_log_invocation_fallback_on_error():
    """log_skill_invocation falls back to local logging when Supabase fails."""
    failing_client = MagicMock()
    failing_table = MagicMock()
    failing_table.insert.return_value = failing_table
    failing_table.execute.side_effect = Exception("Connection refused")
    failing_client.table.return_value = failing_table

    with patch("ts_shared.supabase_client.get_client", return_value=failing_client):
        from ts_shared.logging_utils import log_skill_invocation

        # Should not raise — fallback to local logging
        result = asyncio.get_event_loop().run_until_complete(
            log_skill_invocation(
                agent_name="operations",
                skill_name="test-skill",
                prompt="test prompt",
                result={"error": "test"},
            )
        )

        assert result is not None
