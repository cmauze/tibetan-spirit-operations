"""Shared pytest fixtures for Tibetan Spirit AI Ops tests."""

import os
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "agents"


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
