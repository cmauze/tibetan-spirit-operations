"""Tests for ts_shared.claude_client — skill loading, cost calculation, API call."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from ts_shared.claude_client import (
    MODEL_HAIKU,
    MODEL_SONNET,
    MODEL_OPUS,
    SkillMetadata,
    calculate_cost,
    get_skill_index,
    load_skill,
    load_skills,
    _parse_skill_file,
    _resolve_skill_path,
    call_claude,
    SKILLS_DIR,
)


# ---------------------------------------------------------------------------
# SkillMetadata parsing
# ---------------------------------------------------------------------------


SAMPLE_SKILL = """\
---
name: test-skill
description: A test skill.
version: "1.0.0"
category: shared
tags: [test, unit]
author: test-team
model: haiku
cacheable: true
estimated_tokens: 500
phase: 1
depends_on: []
external_apis: [supabase]
cost_budget_usd: 0.05
---

# Test Skill

This is the body.
"""


def test_parse_skill_file():
    meta, body = _parse_skill_file(SAMPLE_SKILL)
    assert meta.name == "test-skill"
    assert meta.model == "haiku"
    assert meta.tags == ["test", "unit"]
    assert meta.estimated_tokens == 500
    assert meta.external_apis == ["supabase"]
    assert "# Test Skill" in body


def test_parse_skill_file_missing_frontmatter():
    with pytest.raises(ValueError, match="missing YAML frontmatter"):
        _parse_skill_file("# No frontmatter here\nJust markdown.")


def test_skill_metadata_defaults():
    meta = SkillMetadata(name="minimal")
    assert meta.version == "0.1.0"
    assert meta.phase == 1
    assert meta.cacheable is True
    assert meta.depends_on == []


# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------


def test_resolve_canonical_skill_path():
    """Canonical path: skills/{name}/SKILL.md at repo root."""
    path = _resolve_skill_path("shared/cs-triage")
    assert path == SKILLS_DIR / "cs-triage" / "SKILL.md"


def test_resolve_skill_path_extracts_name():
    """Category prefix is stripped; name resolves to canonical location."""
    path = _resolve_skill_path("customer-service/order-inquiry")
    assert path == SKILLS_DIR / "order-inquiry" / "SKILL.md"


# ---------------------------------------------------------------------------
# load_skill (live filesystem)
# ---------------------------------------------------------------------------


def test_load_skill_cs_triage():
    """Load a real SKILL.md from the skills/ tree."""
    meta, body = load_skill("shared/cs-triage")
    assert meta.name == "cs-triage"
    assert len(body) > 100


def test_load_skill_not_found():
    with pytest.raises(FileNotFoundError):
        load_skill("shared/nonexistent-skill")


def test_load_skill_order_inquiry():
    meta, body = load_skill("customer-service/order-inquiry")
    assert meta.name == "order-inquiry"


# ---------------------------------------------------------------------------
# load_skills (multi-load with dependency resolution)
# ---------------------------------------------------------------------------


def test_load_skills_multiple():
    """Loading multiple skills returns all of them."""
    metas, body = load_skills(["shared/cs-triage", "shared/order-inquiry"])
    names = [m.name for m in metas]
    assert "cs-triage" in names
    assert "order-inquiry" in names


def test_load_skills_deduplication():
    """Same skill requested twice is only loaded once."""
    metas, body = load_skills([
        "shared/cs-triage",
        "customer-service/cs-triage",
    ])
    names = [m.name for m in metas]
    assert names.count("cs-triage") == 1


# ---------------------------------------------------------------------------
# get_skill_index
# ---------------------------------------------------------------------------


def test_get_skill_index_returns_all():
    index = get_skill_index()
    assert len(index) >= 8  # 8 skills in skills/ directory
    names = {m.name for m in index}
    assert "cs-triage" in names
    assert "order-inquiry" in names


# ---------------------------------------------------------------------------
# calculate_cost
# ---------------------------------------------------------------------------


def test_calculate_cost_haiku():
    usage = MagicMock(input_tokens=1000, output_tokens=500, cache_read_input_tokens=0)
    cost = calculate_cost(usage, MODEL_HAIKU)
    # 1000/1M * $1 + 500/1M * $5 = 0.001 + 0.0025 = 0.0035
    assert abs(cost - 0.0035) < 1e-6


def test_calculate_cost_sonnet():
    usage = MagicMock(input_tokens=10000, output_tokens=2000, cache_read_input_tokens=0)
    cost = calculate_cost(usage, MODEL_SONNET)
    # 10000/1M * $3 + 2000/1M * $15 = 0.03 + 0.03 = 0.06
    assert abs(cost - 0.06) < 1e-6


def test_calculate_cost_opus():
    usage = MagicMock(input_tokens=5000, output_tokens=1000, cache_read_input_tokens=0)
    cost = calculate_cost(usage, MODEL_OPUS)
    # 5000/1M * $15 + 1000/1M * $75 = 0.075 + 0.075 = 0.15
    assert abs(cost - 0.15) < 1e-6


def test_calculate_cost_with_cache():
    usage = MagicMock(input_tokens=10000, output_tokens=1000, cache_read_input_tokens=8000)
    cost = calculate_cost(usage, MODEL_SONNET)
    # standard_input = 10000-8000 = 2000
    # 2000/1M * $3 = 0.006
    # 8000/1M * $0.3 = 0.0024
    # 1000/1M * $15 = 0.015
    # total = 0.0234
    assert abs(cost - 0.0234) < 1e-6


def test_calculate_cost_unknown_model():
    usage = MagicMock(input_tokens=100, output_tokens=50, cache_read_input_tokens=0)
    with pytest.raises(ValueError, match="Unknown model"):
        calculate_cost(usage, "claude-unknown-99")


# ---------------------------------------------------------------------------
# call_claude (mocked API)
# ---------------------------------------------------------------------------


@patch("ts_shared.claude_client._get_client")
def test_call_claude_sends_correct_params(mock_get_client):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    mock_client.messages.create.return_value = MagicMock(
        content=[MagicMock(text="Hello!")],
        usage=MagicMock(input_tokens=100, output_tokens=20, cache_read_input_tokens=0),
    )

    result = call_claude(
        system_parts=["You are a helpful assistant.", "Follow brand guidelines."],
        user_message="Summarize.",
        model=MODEL_HAIKU,
        max_tokens=500,
    )

    mock_client.messages.create.assert_called_once()
    call_kwargs = mock_client.messages.create.call_args[1]
    assert call_kwargs["model"] == MODEL_HAIKU
    assert call_kwargs["max_tokens"] == 500
    assert len(call_kwargs["system"]) == 2
    assert call_kwargs["system"][0]["cache_control"] == {"type": "ephemeral"}
    assert call_kwargs["messages"][0]["content"] == "Summarize."
