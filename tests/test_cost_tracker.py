"""Tests for ts_shared.cost_tracker — dual-write to Supabase + Notion."""

from unittest.mock import MagicMock, patch

import pytest

from ts_shared.cost_tracker import log_invocation


@patch("ts_shared.cost_tracker._write_notion")
@patch("ts_shared.cost_tracker._write_supabase")
def test_log_invocation_returns_uuid(mock_supabase, mock_notion):
    usage = MagicMock(input_tokens=5000, output_tokens=1000, cache_read_input_tokens=2000)

    inv_id = log_invocation(
        workflow="daily_summary",
        skill_name="channel-config",
        model="claude-haiku-4-5-20251001",
        usage=usage,
        latency_ms=1200,
    )

    assert len(inv_id) == 36  # UUID format
    assert "-" in inv_id
    mock_supabase.assert_called_once()
    mock_notion.assert_called_once()


@patch("ts_shared.cost_tracker._write_notion")
@patch("ts_shared.cost_tracker._write_supabase")
def test_log_invocation_passes_correct_values(mock_supabase, mock_notion):
    usage = MagicMock(input_tokens=10000, output_tokens=2000, cache_read_input_tokens=0)

    log_invocation(
        workflow="weekly_pnl",
        skill_name="margin-reporting",
        model="claude-sonnet-4-6",
        usage=usage,
        latency_ms=3000,
        trigger_source="manual",
        confidence=0.85,
        error=None,
    )

    sb_kwargs = mock_supabase.call_args[1]
    assert sb_kwargs["workflow"] == "weekly_pnl"
    assert sb_kwargs["skill_name"] == "margin-reporting"
    assert sb_kwargs["model"] == "claude-sonnet-4-6"
    assert sb_kwargs["input_tokens"] == 10000
    assert sb_kwargs["output_tokens"] == 2000
    assert sb_kwargs["latency_ms"] == 3000
    assert sb_kwargs["trigger_source"] == "manual"
    assert sb_kwargs["confidence"] == 0.85
    # cost = 10000/1M * $3 + 2000/1M * $15 = 0.03 + 0.03 = 0.06
    assert abs(sb_kwargs["cost_usd"] - 0.06) < 1e-4

    notion_kwargs = mock_notion.call_args[1]
    assert notion_kwargs["workflow"] == "weekly_pnl"
    assert notion_kwargs["model"] == "claude-sonnet-4-6"


@patch("ts_shared.cost_tracker._write_notion")
@patch("ts_shared.cost_tracker._write_supabase")
def test_log_invocation_with_error(mock_supabase, mock_notion):
    usage = MagicMock(input_tokens=100, output_tokens=0, cache_read_input_tokens=0)

    log_invocation(
        workflow="cs_email_drafts",
        skill_name="ticket-triage",
        model="claude-haiku-4-5-20251001",
        usage=usage,
        latency_ms=500,
        error="API timeout",
    )

    sb_kwargs = mock_supabase.call_args[1]
    assert sb_kwargs["error"] == "API timeout"


@patch("ts_shared.cost_tracker._write_notion")
@patch("ts_shared.cost_tracker._write_supabase")
def test_log_invocation_default_trigger_source(mock_supabase, mock_notion):
    usage = MagicMock(input_tokens=100, output_tokens=50, cache_read_input_tokens=0)

    log_invocation(
        workflow="daily_summary",
        skill_name="brand-guidelines",
        model="claude-haiku-4-5-20251001",
        usage=usage,
        latency_ms=200,
    )

    sb_kwargs = mock_supabase.call_args[1]
    assert sb_kwargs["trigger_source"] == "cron"


# ---------------------------------------------------------------------------
# _write_supabase integration (mocked client)
# ---------------------------------------------------------------------------


@patch("ts_shared.cost_tracker.get_client", create=True)
def test_write_supabase_inserts_row(mock_get_client):
    """Test that _write_supabase calls Supabase insert correctly."""
    mock_client = MagicMock()
    table_mock = MagicMock()
    table_mock.insert.return_value = table_mock
    table_mock.execute.return_value = MagicMock(data=[])
    mock_client.table.return_value = table_mock

    with patch("ts_shared.cost_tracker.get_client", return_value=mock_client):
        # Need to import after patching to get the mock
        pass

    # Direct test of _write_supabase
    from ts_shared.cost_tracker import _write_supabase

    with patch("ts_shared.supabase_client.get_client", return_value=mock_client):
        _write_supabase(
            invocation_id="test-uuid",
            workflow="daily_summary",
            skill_name="test",
            model="claude-haiku-4-5-20251001",
            input_tokens=100,
            output_tokens=50,
            cached_tokens=0,
            cost_usd=0.001,
            latency_ms=200,
            trigger_source="cron",
            confidence=None,
            error=None,
        )

    mock_client.table.assert_called_with("skill_invocations")
    insert_data = table_mock.insert.call_args[0][0]
    assert insert_data["id"] == "test-uuid"
    assert insert_data["agent_name"] == "daily_summary"
    assert insert_data["cost_usd"] == 0.001
