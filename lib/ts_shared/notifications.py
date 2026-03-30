"""
Notification dispatcher — Slack integration with graceful degradation.

Usage:
    from ts_shared.notifications import notify, send_slack

    notify("ceo", "Daily summary ready for review.")
    send_slack("#ops-alerts", "Inventory reorder triggered for SKU I82o.")
"""

import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

_slack_client = None


def _get_slack_client():
    """Lazy singleton for the Slack WebClient. Returns None if token missing."""
    global _slack_client
    if _slack_client is None:
        token = os.environ.get("SLACK_BOT_TOKEN")
        if not token:
            logger.warning("SLACK_BOT_TOKEN not set — Slack notifications disabled")
            return None
        from slack_sdk import WebClient

        _slack_client = WebClient(token=token)
    return _slack_client


def send_slack(channel: str, text: str, blocks: Optional[list] = None) -> bool:
    """Send a message to a Slack channel.

    Args:
        channel: Channel name (e.g. "#ops-alerts") or ID.
        text: Plain text fallback.
        blocks: Optional Block Kit blocks.

    Returns:
        True if sent, False if Slack unavailable.
    """
    client = _get_slack_client()
    if client is None:
        logger.info("Slack unavailable — would have sent to %s: %s", channel, text[:100])
        return False
    try:
        kwargs = {"channel": channel, "text": text}
        if blocks:
            kwargs["blocks"] = blocks
        client.chat_postMessage(**kwargs)
        return True
    except Exception as e:
        logger.error("Slack send failed for %s: %s", channel, e)
        return False


def send_slack_dm(user_id: str, text: str) -> bool:
    """Send a direct message to a Slack user.

    Args:
        user_id: Slack user ID.
        text: Message text.

    Returns:
        True if sent, False if Slack unavailable.
    """
    client = _get_slack_client()
    if client is None:
        logger.info("Slack unavailable — would have DM'd %s: %s", user_id, text[:100])
        return False
    try:
        client.chat_postMessage(channel=user_id, text=text)
        return True
    except Exception as e:
        logger.error("Slack DM failed for %s: %s", user_id, e)
        return False


# Channel mapping for roles (from env vars with sensible defaults)
_ROLE_CHANNELS: dict[str, str] = {}


def _get_role_channel(role_id: str) -> Optional[str]:
    """Resolve a role to its Slack channel."""
    if not _ROLE_CHANNELS:
        _ROLE_CHANNELS.update({
            "ceo": os.environ.get("SLACK_CHANNEL_OPS", "#ops-general"),
            "operations-manager": os.environ.get("SLACK_CHANNEL_OPS", "#ops-general"),
            "customer-service-lead": os.environ.get("SLACK_CHANNEL_CS", "#cs-queue"),
            "warehouse-manager": os.environ.get("SLACK_CHANNEL_OPS", "#ops-general"),
        })
    return _ROLE_CHANNELS.get(role_id)


def notify(role_id: str, message: str) -> bool:
    """Send a notification to a team member by role.

    Auto-selects Slack channel based on role. Degrades gracefully if Slack
    is unavailable (returns False, no crash).

    Args:
        role_id: e.g. "ceo", "operations-manager"
        message: Notification text.

    Returns:
        True if delivered, False otherwise.
    """
    channel = _get_role_channel(role_id)
    if not channel:
        logger.warning("No notification channel configured for role: %s", role_id)
        return False
    return send_slack(channel, f"[{role_id}] {message}")
