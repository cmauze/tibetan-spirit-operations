"""Shared pytest fixtures for Tibetan Spirit AI Ops tests."""

import os
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"


# ---------------------------------------------------------------------------
# Server-module mocks
#
# server.server imports claude_agent_sdk and ts_shared.* at module level.
# We must inject stubs before server.server is imported, then immediately
# remove the stubs so other test modules (test_supabase_client, test_logging_utils)
# import the real implementations.
#
# Strategy: inject stubs in pytest_configure → import server.server →
# immediately pop the stubs from sys.modules. The server module retains
# its references to the mocked objects; sys.modules is clean for everyone else.
# ---------------------------------------------------------------------------

class _MockResultMessage:
    result = "Skill executed successfully"
    total_cost_usd = 0.001
    usage = {"input_tokens": 100, "output_tokens": 50, "cache_read_input_tokens": 0}


async def _mock_query(prompt, options=None):
    yield _MockResultMessage()


def pytest_configure(config):
    """Install stubs, import server.server, then remove stubs from sys.modules.

    After this function returns:
    - server.server is imported and cached in sys.modules with mock bindings.
    - claude_agent_sdk, ts_shared, ts_shared.logging_utils, and
      ts_shared.supabase_client are NOT in sys.modules, so subsequent imports
      of the real ts_shared modules work correctly.
    """
    mock_sdk = MagicMock()
    mock_sdk.query = _mock_query
    mock_sdk.ClaudeAgentOptions = MagicMock()
    mock_sdk.ResultMessage = _MockResultMessage

    mock_logging = MagicMock()
    mock_logging.log_skill_invocation = AsyncMock(return_value="test-inv-id")

    stub_keys = [
        "claude_agent_sdk",
        "ts_shared",
        "ts_shared.logging_utils",
        "ts_shared.supabase_client",
    ]

    stubs = {
        "claude_agent_sdk": mock_sdk,
        "ts_shared": MagicMock(),
        "ts_shared.logging_utils": mock_logging,
        "ts_shared.supabase_client": MagicMock(),
    }

    sys.modules.update(stubs)

    # Force server.server to be imported now while stubs are present
    import importlib
    importlib.import_module("server.server")

    # Remove stubs so real ts_shared modules are importable by other test files
    for key in stub_keys:
        sys.modules.pop(key, None)


@pytest.fixture
def repo_root():
    """Path to the repository root."""
    return REPO_ROOT


@pytest.fixture
def skills_dir():
    """Path to the skills directory."""
    return SKILLS_DIR


@pytest.fixture
def mock_supabase_client():
    """Mock Supabase client for unit tests that don't need a real DB connection."""
    client = MagicMock()
    # Chain .table().select().execute() etc.
    table_mock = MagicMock()
    table_mock.select.return_value = table_mock
    table_mock.insert.return_value = table_mock
    table_mock.eq.return_value = table_mock
    table_mock.limit.return_value = table_mock
    table_mock.execute.return_value = MagicMock(data=[], count=0)
    client.table.return_value = table_mock
    return client


@pytest.fixture
def sample_order_payload():
    """Sample Shopify order webhook payload for testing."""
    return {
        "id": 5551234567890,
        "order_number": 1042,
        "email": "customer@example.com",
        "financial_status": "paid",
        "fulfillment_status": None,
        "total_price": "89.95",
        "currency": "USD",
        "line_items": [
            {
                "id": 11111111,
                "title": "Tibetan Singing Bowl - 5 inch",
                "sku": "SB-05-BRZ",
                "quantity": 1,
                "price": "89.95",
            }
        ],
        "shipping_address": {
            "city": "Asheville",
            "province": "North Carolina",
            "country": "US",
            "zip": "28801",
        },
    }


@pytest.fixture
def sample_inventory_payload():
    """Sample Shopify inventory update webhook payload."""
    return {
        "inventory_item_id": 44444444,
        "location_id": 55555555,
        "available": 3,
        "updated_at": "2026-03-23T12:00:00Z",
    }
