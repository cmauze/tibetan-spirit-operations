"""Eval scaffolding for Tibetan Spirit AI skill testing.

Provides fixtures for loading SKILL.md files, mocking Claude Agent SDK
responses, and generating test data. All tests work with mocks — no live
API calls.

Usage:
    pytest tests/evals/ -v
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILLS_DIR = REPO_ROOT / "skills"


# ---------------------------------------------------------------------------
# Skill loading
# ---------------------------------------------------------------------------


def load_skill_md(skill_path: str) -> str:
    """Load a SKILL.md file by relative path from the skills directory.

    Args:
        skill_path: Relative path like "customer-service/ticket-triage"

    Returns:
        The full text content of the SKILL.md file.

    Raises:
        FileNotFoundError: If the SKILL.md file does not exist.
    """
    full_path = SKILLS_DIR / skill_path / "SKILL.md"
    if not full_path.exists():
        raise FileNotFoundError(f"SKILL.md not found at {full_path}")
    return full_path.read_text()


def load_skill_reference(skill_path: str, filename: str) -> str:
    """Load a supplementary reference file from a skill directory.

    Args:
        skill_path: Relative path like "customer-service/ticket-triage"
        filename: Name of the reference file like "response-templates.md"

    Returns:
        The full text content of the reference file.
    """
    full_path = SKILLS_DIR / skill_path / filename
    if not full_path.exists():
        raise FileNotFoundError(f"Reference file not found at {full_path}")
    return full_path.read_text()


@pytest.fixture
def skill_loader():
    """Fixture that returns the load_skill_md function."""
    return load_skill_md


@pytest.fixture
def reference_loader():
    """Fixture that returns the load_skill_reference function."""
    return load_skill_reference


# ---------------------------------------------------------------------------
# Mock Agent SDK
# ---------------------------------------------------------------------------


@dataclass
class MockAgentResponse:
    """Simulates a Claude Agent SDK response for eval testing."""

    content: str
    structured_output: dict[str, Any] = field(default_factory=dict)
    model: str = "claude-sonnet-4-20250514"
    input_tokens: int = 500
    output_tokens: int = 200
    stop_reason: str = "end_turn"


def make_mock_agent(responses: list[MockAgentResponse] | None = None) -> MagicMock:
    """Create a mock Agent SDK client that returns predefined responses.

    Args:
        responses: List of MockAgentResponse objects. The mock will return
                   them in order. If None, returns a default empty response.

    Returns:
        A MagicMock configured to simulate the Agent SDK interface.
    """
    agent = MagicMock()
    agent.run = AsyncMock()

    if responses is None:
        responses = [MockAgentResponse(content="", structured_output={})]

    side_effects = []
    for resp in responses:
        mock_result = MagicMock()
        mock_result.content = resp.content
        mock_result.structured_output = resp.structured_output
        mock_result.model = resp.model
        mock_result.usage.input_tokens = resp.input_tokens
        mock_result.usage.output_tokens = resp.output_tokens
        mock_result.stop_reason = resp.stop_reason
        side_effects.append(mock_result)

    agent.run.side_effect = side_effects
    return agent


@pytest.fixture
def mock_agent():
    """Fixture that returns the make_mock_agent factory."""
    return make_mock_agent


@pytest.fixture
def mock_agent_default():
    """Pre-configured mock agent with a single empty response."""
    return make_mock_agent()


# ---------------------------------------------------------------------------
# Mock Supabase (extends root conftest)
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_supabase_with_data():
    """Mock Supabase client pre-loaded with sample query results.

    Returns a factory function: call with table_name and data to configure.
    """
    client = MagicMock()
    _table_data: dict[str, list[dict]] = {}

    def configure(table_name: str, data: list[dict[str, Any]]) -> None:
        _table_data[table_name] = data

    def table_factory(table_name: str) -> MagicMock:
        table_mock = MagicMock()
        result_data = _table_data.get(table_name, [])

        # Support chained queries: .select().eq().limit().execute()
        table_mock.select.return_value = table_mock
        table_mock.insert.return_value = table_mock
        table_mock.update.return_value = table_mock
        table_mock.eq.return_value = table_mock
        table_mock.neq.return_value = table_mock
        table_mock.lt.return_value = table_mock
        table_mock.lte.return_value = table_mock
        table_mock.gt.return_value = table_mock
        table_mock.gte.return_value = table_mock
        table_mock.ilike.return_value = table_mock
        table_mock.in_.return_value = table_mock
        table_mock.order.return_value = table_mock
        table_mock.limit.return_value = table_mock
        table_mock.execute.return_value = MagicMock(data=result_data, count=len(result_data))
        return table_mock

    client.table.side_effect = table_factory
    client.configure = configure
    return client


# ---------------------------------------------------------------------------
# Test data generators
# ---------------------------------------------------------------------------


def make_customer_ticket(
    subject: str = "Question about my order",
    body: str = "Where is my order #1042?",
    email: str = "customer@example.com",
    channel: str = "email",
    order_number: str | None = "1042",
) -> dict[str, Any]:
    """Generate a sample customer service ticket for testing."""
    return {
        "id": "ticket-001",
        "subject": subject,
        "body": body,
        "from_email": email,
        "channel": channel,
        "order_number": order_number,
        "created_at": "2026-03-22T10:00:00Z",
        "metadata": {},
    }


def make_order(
    order_number: int = 1042,
    total_price: str = "89.95",
    fulfillment_status: str | None = None,
    financial_status: str = "paid",
    channel: str = "shopify",
    country: str = "US",
    items: list[dict[str, Any]] | None = None,
    delivered_at: str | None = "2026-03-10T12:00:00Z",
) -> dict[str, Any]:
    """Generate a sample order payload for testing."""
    if items is None:
        items = [
            {
                "id": 11111111,
                "title": "Tibetan Singing Bowl - 5 inch",
                "sku": "TS-BOWL-HH-5IN",
                "quantity": 1,
                "price": total_price,
            }
        ]
    return {
        "id": 5551234567890,
        "order_number": order_number,
        "email": "customer@example.com",
        "financial_status": financial_status,
        "fulfillment_status": fulfillment_status,
        "total_price": total_price,
        "currency": "USD",
        "channel": channel,
        "line_items": items,
        "shipping_address": {
            "city": "Asheville",
            "province": "North Carolina",
            "country": country,
            "zip": "28801",
        },
        "delivered_at": delivered_at,
        "created_at": "2026-03-08T10:00:00Z",
    }


def make_product(
    sku: str = "TS-BOWL-HH-5IN",
    title: str = "Hand-Hammered Singing Bowl - 5 inch",
    price: str = "89.95",
    category: str = "Singing Bowls",
    cogs_confirmed: float | None = 22.50,
    cogs_confidence: str = "confirmed",
    status: str = "active",
) -> dict[str, Any]:
    """Generate a sample product record for testing."""
    return {
        "id": 1001,
        "shopify_id": 7771234567890,
        "sku": sku,
        "title": title,
        "price": price,
        "category": category,
        "status": status,
        "cogs_confirmed": cogs_confirmed,
        "cogs_estimated": None if cogs_confirmed else 27.00,
        "cogs_confidence": cogs_confidence,
        "freight_per_unit": 2.50,
        "duty_rate": 0.03,
        "duty_hs_code": "8306.29",
        "margin_floor_by_channel": {
            "shopify": 40.0,
            "etsy": 35.0,
            "amazon": 25.0,
        },
        "tags": [],
    }


def make_supplier_payment(
    supplier_name: str = "Patan Metalworks",
    invoice_number: str = "PM-2026-089",
    amount_npr: int = 120000,
    exchange_rate: float = 133.20,
    payment_status: str = "pending",
    due_date: str = "2026-04-01",
) -> dict[str, Any]:
    """Generate a sample supplier payment record for testing."""
    return {
        "id": 501,
        "supplier_name": supplier_name,
        "invoice_number": invoice_number,
        "amount_npr": amount_npr,
        "amount_usd": round(amount_npr / exchange_rate, 2),
        "exchange_rate": exchange_rate,
        "payment_status": payment_status,
        "payment_method": "wire_transfer",
        "due_date": due_date,
    }


def make_inventory_item(
    sku: str = "TS-BOWL-HH-5IN",
    total_on_hand: int = 15,
    shopify_available: int = 12,
    nepal_pipeline: int = 0,
    nepal_eta: str | None = None,
    reorder_trigger_qty: int = 5,
    fba_allocated: int = 0,
) -> dict[str, Any]:
    """Generate a sample inventory_extended record for testing."""
    return {
        "product_id": 1001,
        "sku": sku,
        "total_on_hand": total_on_hand,
        "shopify_available": shopify_available,
        "fba_allocated": fba_allocated,
        "fba_in_transit": 0,
        "nepal_pipeline": nepal_pipeline,
        "nepal_eta": nepal_eta,
        "reorder_trigger_qty": reorder_trigger_qty,
        "safety_stock": 3,
        "in_transit": 0,
    }


@pytest.fixture
def ticket_factory():
    """Fixture that returns the make_customer_ticket factory."""
    return make_customer_ticket


@pytest.fixture
def order_factory():
    """Fixture that returns the make_order factory."""
    return make_order


@pytest.fixture
def product_factory():
    """Fixture that returns the make_product factory."""
    return make_product


@pytest.fixture
def supplier_payment_factory():
    """Fixture that returns the make_supplier_payment factory."""
    return make_supplier_payment


@pytest.fixture
def inventory_factory():
    """Fixture that returns the make_inventory_item factory."""
    return make_inventory_item
