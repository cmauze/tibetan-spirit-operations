"""Tests for ts_shared.notifications — Slack integration with graceful degradation."""

from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Graceful degradation (no SLACK_BOT_TOKEN)
# ---------------------------------------------------------------------------


def test_send_slack_degrades_without_token(monkeypatch):
    """send_slack returns False and doesn't crash when SLACK_BOT_TOKEN missing."""
    monkeypatch.delenv("SLACK_BOT_TOKEN", raising=False)

    import ts_shared.notifications as notif
    notif._slack_client = None  # Reset singleton

    result = notif.send_slack("#test", "hello")
    assert result is False


def test_send_slack_dm_degrades_without_token(monkeypatch):
    monkeypatch.delenv("SLACK_BOT_TOKEN", raising=False)

    import ts_shared.notifications as notif
    notif._slack_client = None

    result = notif.send_slack_dm("U12345", "hello")
    assert result is False


def test_notify_degrades_without_token(monkeypatch):
    monkeypatch.delenv("SLACK_BOT_TOKEN", raising=False)

    import ts_shared.notifications as notif
    notif._slack_client = None
    notif._ROLE_CHANNELS.clear()

    result = notif.notify("ceo", "Test notification")
    assert result is False


# ---------------------------------------------------------------------------
# With mocked Slack client
# ---------------------------------------------------------------------------


@patch("ts_shared.notifications._get_slack_client")
def test_send_slack_success(mock_get_client):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client

    import ts_shared.notifications as notif

    result = notif.send_slack("#ops-alerts", "Inventory low!")
    assert result is True
    mock_client.chat_postMessage.assert_called_once_with(
        channel="#ops-alerts", text="Inventory low!"
    )


@patch("ts_shared.notifications._get_slack_client")
def test_send_slack_with_blocks(mock_get_client):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client

    import ts_shared.notifications as notif

    blocks = [{"type": "section", "text": {"type": "mrkdwn", "text": "Hello"}}]
    result = notif.send_slack("#test", "fallback", blocks=blocks)
    assert result is True
    call_kwargs = mock_client.chat_postMessage.call_args[1]
    assert call_kwargs["blocks"] == blocks


@patch("ts_shared.notifications._get_slack_client")
def test_send_slack_handles_api_error(mock_get_client):
    mock_client = MagicMock()
    mock_client.chat_postMessage.side_effect = Exception("rate_limited")
    mock_get_client.return_value = mock_client

    import ts_shared.notifications as notif

    result = notif.send_slack("#test", "hello")
    assert result is False


@patch("ts_shared.notifications._get_slack_client")
def test_send_slack_dm_success(mock_get_client):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client

    import ts_shared.notifications as notif

    result = notif.send_slack_dm("U12345", "DM text")
    assert result is True
    mock_client.chat_postMessage.assert_called_once_with(channel="U12345", text="DM text")


@patch("ts_shared.notifications.send_slack")
def test_notify_routes_to_correct_channel(mock_send_slack, monkeypatch):
    monkeypatch.setenv("SLACK_CHANNEL_OPS", "#my-ops")

    import ts_shared.notifications as notif
    notif._ROLE_CHANNELS.clear()  # Force re-read of env vars

    mock_send_slack.return_value = True
    result = notif.notify("ceo", "Report ready")
    assert result is True
    mock_send_slack.assert_called_once()
    call_args = mock_send_slack.call_args
    assert "#my-ops" in call_args[0][0]
    assert "[ceo]" in call_args[0][1]


@patch("ts_shared.notifications.send_slack")
def test_notify_unknown_role(mock_send_slack):
    import ts_shared.notifications as notif
    notif._ROLE_CHANNELS.clear()

    result = notif.notify("unknown-role", "Hello")
    assert result is False
    mock_send_slack.assert_not_called()
