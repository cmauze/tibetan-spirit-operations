"""Tests for the FastAPI server endpoints.

These tests mock the Agent SDK and Supabase to test server behavior
without requiring external services.

sys.modules stubs for claude_agent_sdk and ts_shared.* are installed by
pytest_configure in tests/conftest.py before collection, so this module
can import server.server at the top level without any module-level hacks.
"""

import base64
import hashlib
import hmac
import json
from unittest.mock import patch

import pytest

from server.server import app, verify_shopify_webhook
from httpx import ASGITransport, AsyncClient


@pytest.fixture
def test_client():
    """Async HTTP test client for the FastAPI app."""
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


@pytest.mark.asyncio
async def test_health_endpoint(test_client):
    """Health endpoint returns 200 with status ok."""
    async with test_client as client:
        response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "timestamp" in data
    assert data["version"] == "0.2.0"


def test_hmac_validation_valid():
    """Valid HMAC signature passes verification."""
    secret = "test-secret"
    body = b'{"test": "payload"}'
    digest = hmac.new(secret.encode(), body, hashlib.sha256).digest()
    signature = base64.b64encode(digest).decode()

    with patch("server.server.SHOPIFY_WEBHOOK_SECRET", secret):
        assert verify_shopify_webhook(body, signature) is True


def test_hmac_validation_invalid():
    """Invalid HMAC signature is rejected."""
    with patch("server.server.SHOPIFY_WEBHOOK_SECRET", "test-secret"):
        assert verify_shopify_webhook(b"test", "bad-signature") is False


def test_hmac_validation_no_secret():
    """Missing secret skips validation (returns True with warning)."""
    with patch("server.server.SHOPIFY_WEBHOOK_SECRET", ""):
        assert verify_shopify_webhook(b"test", "anything") is True


@pytest.mark.asyncio
async def test_run_skill_invalid_api_key(test_client):
    """run-skill rejects requests with invalid API key."""
    async with test_client as client:
        response = await client.post(
            "/api/run-skill",
            json={"agent": "operations", "skill": "operations/fulfillment-domestic", "prompt": "test"},
            headers={"x-api-key": "wrong-key"},
        )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_run_skill_valid_request(test_client):
    """run-skill accepts valid request with correct API key."""
    with patch("server.server.API_KEY", "test-key"):
        async with test_client as client:
            response = await client.post(
                "/api/run-skill",
                json={
                    "agent": "operations",
                    "skill": "operations/fulfillment-domestic",
                    "prompt": "test order routing",
                },
                headers={"x-api-key": "test-key"},
            )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "accepted"
    assert data["agent"] == "operations"


@pytest.mark.asyncio
async def test_order_webhook_accepted(test_client):
    """Order webhook returns 200 for valid payload (no HMAC required when header missing)."""
    payload = {"id": 123, "order_number": 1042, "email": "test@example.com"}
    async with test_client as client:
        response = await client.post(
            "/webhooks/shopify/orders/create",
            content=json.dumps(payload),
            headers={"content-type": "application/json"},
        )
    assert response.status_code == 200
    assert response.json()["status"] == "accepted"
    assert response.json()["order_id"] == 123


@pytest.mark.asyncio
async def test_agent_configs_cover_all_agents(test_client):
    """All 6 agents are configured."""
    from server.server import AGENT_CONFIGS

    expected = {"customer-service", "operations", "ecommerce", "category-management", "marketing", "finance"}
    assert set(AGENT_CONFIGS.keys()) == expected

    for name, config in AGENT_CONFIGS.items():
        assert "model" in config, f"{name} missing model"
        assert "max_turns" in config, f"{name} missing max_turns"
        assert "max_budget_usd" in config, f"{name} missing max_budget_usd"
        assert "skills" in config, f"{name} missing skills"
        assert config["model"] in ("haiku", "sonnet", "opus"), f"{name} invalid model"
