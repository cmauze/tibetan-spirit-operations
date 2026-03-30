"""
Notion operations for Academy wiki writes and cost log archiving.

Narrowed scope — dashboard operational data lives in Supabase.
This module handles only:
  1. Academy page creation (Jothi training modules)
  2. Cost log archival (backup of Supabase skill_invocations)

Usage:
    from ts_shared.notion_ops import create_academy_page, log_cost_to_notion
"""

import logging
import os
import time
from datetime import datetime, timezone

from ts_shared.notion_config import NOTION_DB, ACADEMY_PROPS, COST_LOG_PROPS

logger = logging.getLogger(__name__)

# Rate limit: Notion API allows 3 requests/second
_MIN_REQUEST_INTERVAL = 0.34  # ~3 req/sec
_last_request_time = 0.0

_MAX_RETRIES = 3
_BACKOFF_BASE = 1.0  # seconds

_client = None


def _get_client():
    """Lazy singleton for the Notion client."""
    global _client
    if _client is None:
        token = os.environ.get("NOTION_API_KEY")
        if not token:
            raise EnvironmentError("NOTION_API_KEY must be set")
        from notion_client import Client

        _client = Client(auth=token)
    return _client


def _rate_limit():
    """Enforce 3 req/sec rate limit."""
    global _last_request_time
    now = time.monotonic()
    elapsed = now - _last_request_time
    if elapsed < _MIN_REQUEST_INTERVAL:
        time.sleep(_MIN_REQUEST_INTERVAL - elapsed)
    _last_request_time = time.monotonic()


def _retry(fn, *args, **kwargs):
    """Execute fn with retry logic (3 retries, exponential backoff)."""
    last_err = None
    for attempt in range(_MAX_RETRIES):
        try:
            _rate_limit()
            return fn(*args, **kwargs)
        except Exception as e:
            last_err = e
            wait = _BACKOFF_BASE * (2**attempt)
            logger.warning("Notion API error (attempt %d/%d): %s. Retrying in %.1fs",
                           attempt + 1, _MAX_RETRIES, e, wait)
            time.sleep(wait)
    raise last_err


def create_academy_page(
    module_id: int,
    title: str,
    content: str,
    language: str = "id",
    section: str = "Getting Started",
    assignee: str = "operations-manager",
) -> str:
    """Create an Academy training module page in Notion.

    Args:
        module_id: Numeric module identifier (e.g. 1, 2, 3).
        title: Module title.
        content: Markdown content for the page body.
        language: Target language code ("id" for Bahasa Indonesia, "en" for English).
        section: Academy section name.
        assignee: Role ID of the person responsible.

    Returns:
        Notion page ID of the created page.
    """
    client = _get_client()
    db_id = NOTION_DB["academy_modules"]

    lang_label = f" [{language.upper()}]" if language != "en" else ""

    properties = {
        ACADEMY_PROPS["title"]: {"title": [{"text": {"content": f"{title}{lang_label}"}}]},
        ACADEMY_PROPS["section"]: {"select": {"name": section}},
        ACADEMY_PROPS["status"]: {"select": {"name": "Draft"}},
        ACADEMY_PROPS["assignee"]: {"select": {"name": assignee}},
        ACADEMY_PROPS["module_number"]: {"number": module_id},
    }

    # Split content into blocks (Notion has 2000-char limit per block)
    blocks = []
    for chunk in _chunk_text(content, 2000):
        blocks.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": chunk}}]
            },
        })

    page = _retry(
        client.pages.create,
        parent={"database_id": db_id},
        properties=properties,
        children=blocks,
    )

    page_id = page["id"]
    logger.info("Created Academy page: %s (module %d)", title, module_id)
    return page_id


def log_cost_to_notion(
    workflow: str,
    model: str,
    input_tokens: int,
    output_tokens: int,
    cached_tokens: int,
    cost_usd: float,
) -> str:
    """Archive a workflow cost entry to Notion cost log.

    Args:
        workflow: Workflow name (e.g. "daily_summary").
        model: Model used (e.g. "haiku-4.5").
        input_tokens: Total input tokens.
        output_tokens: Total output tokens.
        cached_tokens: Cached input tokens.
        cost_usd: Total cost in USD.

    Returns:
        Notion page ID of the created entry.
    """
    client = _get_client()
    db_id = NOTION_DB["cost_log"]
    now = datetime.now(timezone.utc)

    # Friendly model label for Notion select
    model_label = model
    if "haiku" in model:
        model_label = "haiku-4.5"
    elif "sonnet" in model:
        model_label = "sonnet-4.6"
    elif "opus" in model:
        model_label = "opus-4.6"

    run_title = f"{workflow} — {now.strftime('%Y-%m-%d %H:%M')}"

    properties = {
        COST_LOG_PROPS["title"]: {"title": [{"text": {"content": run_title}}]},
        COST_LOG_PROPS["workflow"]: {"select": {"name": workflow}},
        COST_LOG_PROPS["run_date"]: {"date": {"start": now.isoformat()}},
        COST_LOG_PROPS["model"]: {"select": {"name": model_label}},
        COST_LOG_PROPS["input_tokens"]: {"number": input_tokens},
        COST_LOG_PROPS["output_tokens"]: {"number": output_tokens},
        COST_LOG_PROPS["cached_tokens"]: {"number": cached_tokens},
        COST_LOG_PROPS["cost"]: {"number": round(cost_usd, 4)},
    }

    page = _retry(
        client.pages.create,
        parent={"database_id": db_id},
        properties=properties,
    )

    page_id = page["id"]
    logger.info("Logged cost to Notion: %s ($%.4f)", workflow, cost_usd)
    return page_id


def _chunk_text(text: str, max_len: int) -> list[str]:
    """Split text into chunks of max_len, breaking at newlines when possible."""
    if len(text) <= max_len:
        return [text]
    chunks = []
    while text:
        if len(text) <= max_len:
            chunks.append(text)
            break
        # Find last newline within limit
        cut = text.rfind("\n", 0, max_len)
        if cut <= 0:
            cut = max_len
        chunks.append(text[:cut])
        text = text[cut:].lstrip("\n")
    return chunks
