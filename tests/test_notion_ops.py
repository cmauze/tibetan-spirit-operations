"""Tests for ts_shared.notion_ops — Academy pages and cost log archiving."""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from ts_shared.notion_config import NOTION_DB, ACADEMY_PROPS, COST_LOG_PROPS


# ---------------------------------------------------------------------------
# notion_config tests
# ---------------------------------------------------------------------------


def test_notion_db_has_required_keys():
    assert "academy_modules" in NOTION_DB
    assert "cost_log" in NOTION_DB


def test_notion_db_env_override(monkeypatch):
    monkeypatch.setenv("NOTION_DB_ACADEMY", "custom-academy-id")
    # Re-import to pick up env var
    import importlib
    import ts_shared.notion_config as nc
    importlib.reload(nc)
    assert nc.NOTION_DB["academy_modules"] == "custom-academy-id"
    # Restore
    monkeypatch.delenv("NOTION_DB_ACADEMY")
    importlib.reload(nc)


# ---------------------------------------------------------------------------
# notion_ops tests (all mocked — no real Notion calls)
# ---------------------------------------------------------------------------


@patch("ts_shared.notion_ops._get_client")
def test_create_academy_page(mock_get_client):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    mock_client.pages.create.return_value = {"id": "page-123"}

    from ts_shared.notion_ops import create_academy_page

    page_id = create_academy_page(
        module_id=1,
        title="Order Lifecycle",
        content="This module covers order processing basics.",
        language="id",
        section="Getting Started",
    )

    assert page_id == "page-123"
    mock_client.pages.create.assert_called_once()
    call_kwargs = mock_client.pages.create.call_args[1]
    props = call_kwargs["properties"]
    # Title should have language tag
    title_text = props[ACADEMY_PROPS["title"]]["title"][0]["text"]["content"]
    assert "[ID]" in title_text
    assert "Order Lifecycle" in title_text
    # Section
    assert props[ACADEMY_PROPS["section"]]["select"]["name"] == "Getting Started"
    # Status should be Draft
    assert props[ACADEMY_PROPS["status"]]["select"]["name"] == "Draft"
    # Children should be paragraph blocks
    assert len(call_kwargs["children"]) >= 1
    assert call_kwargs["children"][0]["type"] == "paragraph"


@patch("ts_shared.notion_ops._get_client")
def test_create_academy_page_english_no_tag(mock_get_client):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    mock_client.pages.create.return_value = {"id": "page-456"}

    from ts_shared.notion_ops import create_academy_page

    create_academy_page(module_id=2, title="Dashboard Guide", content="...", language="en")

    call_kwargs = mock_client.pages.create.call_args[1]
    title_text = call_kwargs["properties"][ACADEMY_PROPS["title"]]["title"][0]["text"]["content"]
    assert "[EN]" not in title_text
    assert title_text == "Dashboard Guide"


@patch("ts_shared.notion_ops._get_client")
def test_create_academy_page_long_content_chunked(mock_get_client):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    mock_client.pages.create.return_value = {"id": "page-789"}

    from ts_shared.notion_ops import create_academy_page

    long_content = "A" * 5000  # Exceeds 2000-char block limit
    create_academy_page(module_id=3, title="Long Module", content=long_content)

    call_kwargs = mock_client.pages.create.call_args[1]
    assert len(call_kwargs["children"]) >= 3  # 5000 / 2000 = 3 chunks


@patch("ts_shared.notion_ops._get_client")
def test_log_cost_to_notion(mock_get_client):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    mock_client.pages.create.return_value = {"id": "cost-001"}

    from ts_shared.notion_ops import log_cost_to_notion

    page_id = log_cost_to_notion(
        workflow="daily_summary",
        model="claude-haiku-4-5-20251001",
        input_tokens=5000,
        output_tokens=1000,
        cached_tokens=3000,
        cost_usd=0.0085,
    )

    assert page_id == "cost-001"
    mock_client.pages.create.assert_called_once()
    call_kwargs = mock_client.pages.create.call_args[1]
    props = call_kwargs["properties"]
    assert props[COST_LOG_PROPS["workflow"]]["select"]["name"] == "daily_summary"
    assert props[COST_LOG_PROPS["model"]]["select"]["name"] == "haiku-4.5"
    assert props[COST_LOG_PROPS["input_tokens"]]["number"] == 5000
    assert props[COST_LOG_PROPS["output_tokens"]]["number"] == 1000
    assert props[COST_LOG_PROPS["cached_tokens"]]["number"] == 3000
    assert props[COST_LOG_PROPS["cost"]]["number"] == 0.0085


@patch("ts_shared.notion_ops._get_client")
def test_log_cost_model_label_sonnet(mock_get_client):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    mock_client.pages.create.return_value = {"id": "cost-002"}

    from ts_shared.notion_ops import log_cost_to_notion

    log_cost_to_notion(
        workflow="weekly_pnl",
        model="claude-sonnet-4-6",
        input_tokens=10000,
        output_tokens=2000,
        cached_tokens=0,
        cost_usd=0.06,
    )

    call_kwargs = mock_client.pages.create.call_args[1]
    assert call_kwargs["properties"][COST_LOG_PROPS["model"]]["select"]["name"] == "sonnet-4.6"


def test_get_client_missing_env(monkeypatch):
    """_get_client raises EnvironmentError when NOTION_API_KEY missing."""
    monkeypatch.delenv("NOTION_API_KEY", raising=False)
    # Reset singleton
    import ts_shared.notion_ops as nops
    nops._client = None
    with pytest.raises(EnvironmentError, match="NOTION_API_KEY"):
        nops._get_client()


def test_chunk_text():
    from ts_shared.notion_ops import _chunk_text

    # Short text stays as one chunk
    assert _chunk_text("hello", 100) == ["hello"]

    # Long text gets split
    chunks = _chunk_text("a" * 5000, 2000)
    assert len(chunks) == 3
    assert all(len(c) <= 2000 for c in chunks)

    # Prefers splitting at newlines
    text = "line1\n" * 300  # ~1800 chars
    text += "line2\n" * 300  # another ~1800 chars
    chunks = _chunk_text(text, 2000)
    assert len(chunks) >= 2
    for chunk in chunks:
        assert len(chunk) <= 2000
