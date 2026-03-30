"""
Claude API client with skill loading from agents/ tree, prompt caching, and cost calculation.

Usage:
    from ts_shared.claude_client import call_claude, load_skill, MODEL_SONNET

    meta, body = load_skill("shared/brand-guidelines")
    response = call_claude([body], "Summarize the brand voice.", model=MODEL_SONNET)
"""

import os
import re
from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, Field
from anthropic import Anthropic

# ---------------------------------------------------------------------------
# Model constants
# ---------------------------------------------------------------------------

MODEL_HAIKU = "claude-haiku-4-5-20251001"
MODEL_SONNET = "claude-sonnet-4-6"
MODEL_OPUS = "claude-opus-4-6"

# Cost per million tokens: (input, output, cache_read)
# Cache read = 90% discount on input price
_MODEL_COSTS: dict[str, tuple[float, float, float]] = {
    MODEL_HAIKU: (1.0, 5.0, 0.1),
    MODEL_SONNET: (3.0, 15.0, 0.3),
    MODEL_OPUS: (15.0, 75.0, 1.5),
}

# Repo root — relative to this file: lib/ts_shared/claude_client.py → ../../
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
AGENTS_DIR = REPO_ROOT / "agents"

# ---------------------------------------------------------------------------
# SkillMetadata
# ---------------------------------------------------------------------------


class SkillMetadata(BaseModel):
    """Parsed YAML frontmatter from a SKILL.md file."""

    name: str
    description: str = ""
    version: str = "0.1.0"
    category: str = ""
    tags: list[str] = Field(default_factory=list)
    author: str = ""
    model: str = "sonnet"
    cacheable: bool = True
    estimated_tokens: int = 0
    phase: int = 1
    depends_on: list[str] = Field(default_factory=list)
    external_apis: list[str] = Field(default_factory=list)
    cost_budget_usd: float = 0.15


# Regex to extract YAML frontmatter between --- delimiters
_FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def _parse_skill_file(text: str) -> tuple[SkillMetadata, str]:
    """Split a SKILL.md into (metadata, markdown_body)."""
    match = _FRONTMATTER_RE.match(text)
    if not match:
        raise ValueError("SKILL.md missing YAML frontmatter (--- delimiters)")
    raw_yaml = match.group(1)
    body = text[match.end():]
    data = yaml.safe_load(raw_yaml) or {}
    return SkillMetadata(**data), body.strip()


def _resolve_skill_path(skill_path: str) -> Path:
    """Resolve a skill path to its SKILL.md file.

    - "shared/brand-guidelines"  → agents/shared/brand-guidelines/SKILL.md
    - "customer-service/ticket-triage" → agents/customer-service/skills/ticket-triage/SKILL.md
    """
    parts = skill_path.split("/", 1)
    if len(parts) != 2:
        raise ValueError(f"Skill path must be 'category/skill-name', got: {skill_path!r}")

    category, skill_name = parts
    if category == "shared":
        return AGENTS_DIR / "shared" / skill_name / "SKILL.md"
    return AGENTS_DIR / category / "skills" / skill_name / "SKILL.md"


# ---------------------------------------------------------------------------
# Public API: skill loading
# ---------------------------------------------------------------------------


def load_skill(skill_path: str) -> tuple[SkillMetadata, str]:
    """Load a single SKILL.md from the agents/ tree.

    Args:
        skill_path: e.g. "shared/brand-guidelines" or "customer-service/ticket-triage"

    Returns:
        (SkillMetadata, markdown_body)
    """
    path = _resolve_skill_path(skill_path)
    if not path.exists():
        raise FileNotFoundError(f"Skill not found: {path}")
    return _parse_skill_file(path.read_text(encoding="utf-8"))


def load_skills(skill_paths: list[str]) -> tuple[list[SkillMetadata], str]:
    """Load multiple skills with dependency resolution.

    - Always loads shared/brand-guidelines FIRST.
    - Auto-resolves depends_on (co-loads dependencies).
    - Deduplicates: each skill loaded once.

    Returns:
        (list[SkillMetadata], concatenated_markdown_body)
    """
    # Collect all paths including dependencies
    all_paths: list[str] = []
    seen: set[str] = set()

    def _enqueue(path: str) -> None:
        if path in seen:
            return
        seen.add(path)
        # Load to discover dependencies
        meta, _ = load_skill(path)
        for dep in meta.depends_on:
            _enqueue(dep)
        all_paths.append(path)

    for p in skill_paths:
        _enqueue(p)

    # Ensure brand-guidelines is first
    bg = "shared/brand-guidelines"
    if bg in all_paths:
        all_paths.remove(bg)
    all_paths.insert(0, bg)

    # Load all in final order
    metadatas: list[SkillMetadata] = []
    sections: list[str] = []
    for path in all_paths:
        meta, body = load_skill(path)
        metadatas.append(meta)
        sections.append(f"## Skill: {meta.name}\n\n{body}")

    return metadatas, "\n\n---\n\n".join(sections)


def get_skill_index() -> list[SkillMetadata]:
    """Tier 1 startup load: scan all SKILL.md files, return frontmatter only (~50 tokens/skill)."""
    index: list[SkillMetadata] = []
    for skill_file in sorted(AGENTS_DIR.rglob("SKILL.md")):
        try:
            meta, _ = _parse_skill_file(skill_file.read_text(encoding="utf-8"))
            index.append(meta)
        except (ValueError, yaml.YAMLError):
            continue  # Skip malformed files
    return index


# ---------------------------------------------------------------------------
# Public API: Claude calls
# ---------------------------------------------------------------------------

_client: Optional[Anthropic] = None


def _get_client() -> Anthropic:
    """Lazy singleton for the Anthropic client."""
    global _client
    if _client is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise EnvironmentError("ANTHROPIC_API_KEY must be set")
        _client = Anthropic(api_key=api_key)
    return _client


def call_claude(
    system_parts: list[str],
    user_message: str,
    model: str = MODEL_SONNET,
    max_tokens: int = 2000,
):
    """Call Claude with prompt caching on system blocks.

    Args:
        system_parts: List of system prompt strings. Each gets cache_control.
        user_message: The user message content.
        model: Model ID (use MODEL_* constants).
        max_tokens: Maximum output tokens.

    Returns:
        anthropic.types.Message
    """
    client = _get_client()
    system_blocks = [
        {
            "type": "text",
            "text": part,
            "cache_control": {"type": "ephemeral"},
        }
        for part in system_parts
    ]
    return client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system_blocks,
        messages=[{"role": "user", "content": user_message}],
    )


def calculate_cost(usage, model: str) -> float:
    """Calculate cost in USD from a Message.usage object.

    Args:
        usage: anthropic.types.Usage with input_tokens, output_tokens,
               and optionally cache_read_input_tokens.
        model: Model ID.

    Returns:
        Cost in USD.
    """
    costs = _MODEL_COSTS.get(model)
    if not costs:
        raise ValueError(f"Unknown model for cost calculation: {model}")
    input_cost_per_m, output_cost_per_m, cache_read_cost_per_m = costs

    input_tokens = getattr(usage, "input_tokens", 0) or 0
    output_tokens = getattr(usage, "output_tokens", 0) or 0
    cache_read_tokens = getattr(usage, "cache_read_input_tokens", 0) or 0

    # Cache-read tokens are already counted in input_tokens by the API,
    # so we subtract them from input and price them at the discounted rate.
    standard_input = input_tokens - cache_read_tokens

    cost = (
        (standard_input / 1_000_000) * input_cost_per_m
        + (cache_read_tokens / 1_000_000) * cache_read_cost_per_m
        + (output_tokens / 1_000_000) * output_cost_per_m
    )
    return round(cost, 6)
