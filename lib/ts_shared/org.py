"""
Org chart resolver — parses ORG.md into structured role data.

Usage:
    from ts_shared.org import resolve_role

    role = resolve_role("ceo")
    print(role.person, role.language)  # "Chris Mauzé", "English"
"""

import re
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_ORG_PATH = REPO_ROOT / "ORG.md"


class OrgRole(BaseModel):
    """A team member's role and contact details parsed from ORG.md."""

    role_id: str
    person: str
    location: str = ""
    contact_methods: list[str] = Field(default_factory=list)
    language: str = "English"
    approves: list[str] = Field(default_factory=list)
    handles: list[str] = Field(default_factory=list)


_org_cache: Optional[dict[str, OrgRole]] = None
_org_path_cached: Optional[Path] = None


def load_org(org_path: Optional[str] = None) -> dict[str, OrgRole]:
    """Parse ORG.md into a dict of role_id -> OrgRole.

    Args:
        org_path: Path to ORG.md. Defaults to repo root.

    Returns:
        Dict mapping role IDs to OrgRole objects.
    """
    global _org_cache, _org_path_cached
    path = Path(org_path) if org_path else DEFAULT_ORG_PATH

    if _org_cache is not None and _org_path_cached == path:
        return _org_cache

    if not path.exists():
        raise FileNotFoundError(f"ORG.md not found: {path}")

    text = path.read_text(encoding="utf-8")
    roles = _parse_org_table(text)

    # Enrich with communication protocol details
    _parse_protocols(text, roles)

    _org_cache = roles
    _org_path_cached = path
    return roles


def resolve_role(role_id: str, org_path: Optional[str] = None) -> OrgRole:
    """Look up a single role by ID.

    Args:
        role_id: e.g. "ceo", "operations-manager"
        org_path: Optional path to ORG.md.

    Returns:
        OrgRole for the given ID.

    Raises:
        KeyError: If role_id not found.
    """
    roles = load_org(org_path)
    if role_id not in roles:
        raise KeyError(f"Unknown role: {role_id!r}. Available: {list(roles.keys())}")
    return roles[role_id]


def clear_cache() -> None:
    """Clear the cached org data (useful in tests)."""
    global _org_cache, _org_path_cached
    _org_cache = None
    _org_path_cached = None


# ---------------------------------------------------------------------------
# Internal parsing
# ---------------------------------------------------------------------------

# Match markdown table rows: | `role` | person | location | channels | language | approves |
_TABLE_ROW_RE = re.compile(
    r"\|\s*`([^`]+)`\s*\|"   # role_id in backticks
    r"\s*([^|\n]+)\|"         # person
    r"\s*([^|\n]+)\|"         # location
    r"\s*([^|\n]+)\|"         # contact channels
    r"\s*([^|\n]+)\|"         # language
    r"\s*([^|\n]*)\|"         # approves
)


def _parse_org_table(text: str) -> dict[str, OrgRole]:
    """Extract roles from the markdown table in ORG.md."""
    roles: dict[str, OrgRole] = {}
    for match in _TABLE_ROW_RE.finditer(text):
        role_id = match.group(1).strip()
        person = match.group(2).strip()
        location = match.group(3).strip()
        channels_raw = match.group(4).strip()
        language = match.group(5).strip()
        approves_raw = match.group(6).strip()

        contact_methods = [c.strip() for c in channels_raw.split(",") if c.strip()]
        approves = [a.strip() for a in approves_raw.split(",") if a.strip()]

        roles[role_id] = OrgRole(
            role_id=role_id,
            person=person,
            location=location,
            contact_methods=contact_methods,
            language=language,
            approves=approves,
        )
    return roles


def _parse_protocols(text: str, roles: dict[str, OrgRole]) -> None:
    """Enrich roles with 'Handles' info from the Escalation table."""
    # Match escalation table: | Content Type | Approver | Channel |
    # And also look for "Handles:" lines in protocol sections
    handles_re = re.compile(
        r"###\s+(\S+)\s*\n"  # ### role-id
        r"(.*?)(?=\n###|\n##|\Z)",  # content until next section
        re.DOTALL,
    )
    for match in handles_re.finditer(text):
        role_id = match.group(1).strip()
        section = match.group(2)
        if role_id not in roles:
            continue
        # Look for "Handles:" or "Scope:" lines
        for line in section.split("\n"):
            line = line.strip().lstrip("- ")
            if line.startswith("**Scope:**") or line.startswith("**When to contact:**"):
                items = line.split(":", 1)[1].strip().rstrip("*")
                roles[role_id].handles = [h.strip() for h in items.split(",") if h.strip()]
