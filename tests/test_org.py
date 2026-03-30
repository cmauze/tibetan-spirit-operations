"""Tests for ts_shared.org — ORG.md parsing and role resolution."""

import pytest

from ts_shared.org import load_org, resolve_role, clear_cache, OrgRole


@pytest.fixture(autouse=True)
def _clear_org_cache():
    """Clear org cache before each test."""
    clear_cache()
    yield
    clear_cache()


# ---------------------------------------------------------------------------
# load_org
# ---------------------------------------------------------------------------


def test_load_org_returns_all_roles():
    roles = load_org()
    assert "ceo" in roles
    assert "operations-manager" in roles
    assert "customer-service-lead" in roles
    assert "warehouse-manager" in roles
    assert "spiritual-director" in roles
    assert "mexico-fulfillment" in roles


def test_load_org_caches():
    roles1 = load_org()
    roles2 = load_org()
    assert roles1 is roles2  # Same object (cached)


def test_load_org_missing_file():
    with pytest.raises(FileNotFoundError):
        load_org("/nonexistent/ORG.md")


# ---------------------------------------------------------------------------
# resolve_role
# ---------------------------------------------------------------------------


def test_resolve_ceo():
    role = resolve_role("ceo")
    assert isinstance(role, OrgRole)
    assert role.person == "Chris Mauzé"
    assert role.language == "English"
    assert "Slack" in role.contact_methods


def test_resolve_operations_manager():
    role = resolve_role("operations-manager")
    assert role.person == "Jothi"
    assert role.language == "Bahasa Indonesia (formal)"
    assert "Slack" in role.contact_methods


def test_resolve_warehouse_manager():
    role = resolve_role("warehouse-manager")
    assert role.person == "Fiona"
    assert role.language == "Chinese (Mandarin)"
    assert "Dashboard" in role.contact_methods


def test_resolve_spiritual_director():
    role = resolve_role("spiritual-director")
    assert role.person == "Dr. Hun Lye"
    assert role.language == "English"
    assert "Email only" in role.contact_methods


def test_resolve_mexico_fulfillment():
    role = resolve_role("mexico-fulfillment")
    assert "Omar" in role.person
    assert role.language == "Spanish"


def test_resolve_unknown_role():
    with pytest.raises(KeyError, match="Unknown role"):
        resolve_role("nonexistent-role")


def test_ceo_has_approvals():
    role = resolve_role("ceo")
    # CEO approves pricing, budget, strategy, etc.
    approves_str = ", ".join(role.approves)
    assert "budget" in approves_str.lower() or "pricing" in approves_str.lower()


def test_org_role_model_fields():
    role = resolve_role("ceo")
    assert role.role_id == "ceo"
    assert isinstance(role.contact_methods, list)
    assert isinstance(role.approves, list)
