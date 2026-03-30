#!/usr/bin/env python3
"""
Structural validator for SKILL.md files.

Checks YAML frontmatter, required sections, cultural anti-patterns,
and model routing. Returns JSON report per file.

Usage:
    python3 scripts/validate_skill.py                    # validate all skills
    python3 scripts/validate_skill.py agents/customer-service/skills/ticket-triage
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

CULTURAL_ANTI_PATTERNS = [
    r"\bexotic\b",
    r"\bmystical\b",
    r"\bhome\s+decor\b",
    r"\bOriental\b",
    r"\bHimalayan\s+magic\b",
    r"\btrinket\b",
    r"\bcurio(?:s|sity)?\b",
    r"\bethnic\b",
]

REQUIRED_SECTIONS = {
    "purpose_or_overview": [
        r"(?i)##\s*(purpose|overview|what this skill does)",
    ],
    "decision_logic": [
        r"(?i)##\s*(decision|logic|workflow|process|steps|classification|routing)",
        r"(?i)(if|when|condition|rule|tier|level)\s",
    ],
    "output_format": [
        r"(?i)##\s*(output|response|result|report)\s*(format|structure|schema)?",
        r"(?i)```json",
    ],
    "phase_behavior": [
        r"(?i)(phase\s*1|phase\s*2|human\s*approv|HITL|human.in.the.loop|approval\s*require)",
    ],
}

MODEL_ROUTING_PATTERNS = [
    r"(?i)\b(haiku|sonnet|opus)\b",
    r"(?i)model\s*(routing|selection|choice)",
]


def parse_frontmatter(content: str) -> tuple[dict | None, list[str]]:
    """Extract YAML frontmatter from SKILL.md content."""
    errors = []
    if not content.startswith("---"):
        errors.append("Missing YAML frontmatter (file must start with ---)")
        return None, errors

    parts = content.split("---", 2)
    if len(parts) < 3:
        errors.append("Malformed YAML frontmatter (missing closing ---)")
        return None, errors

    frontmatter_text = parts[1].strip()
    fm = {}
    for line in frontmatter_text.split("\n"):
        line = line.strip()
        if ":" in line:
            key, _, value = line.partition(":")
            fm[key.strip()] = value.strip()

    if "name" not in fm:
        errors.append("Frontmatter missing 'name' field")
    if "description" not in fm:
        errors.append("Frontmatter missing 'description' field")

    return fm, errors


def check_sections(content: str) -> tuple[list[str], list[str]]:
    """Check for required sections. Returns (warnings, errors)."""
    warnings = []
    errors = []

    for section_name, patterns in REQUIRED_SECTIONS.items():
        found = any(re.search(p, content) for p in patterns)
        if not found:
            label = section_name.replace("_", " ")
            if section_name == "phase_behavior":
                warnings.append(f"No {label} section detected (recommended)")
            else:
                errors.append(f"Missing required section: {label}")

    return warnings, errors


def check_cultural_anti_patterns(content: str) -> list[str]:
    """Scan for culturally insensitive language."""
    warnings = []
    for i, line in enumerate(content.split("\n"), 1):
        for pattern in CULTURAL_ANTI_PATTERNS:
            match = re.search(pattern, line)
            if match:
                word = match.group()
                # Skip if in a "do not use" or "avoid" context
                context_start = max(0, match.start() - 60)
                context = line[context_start:match.start()].lower()
                if any(neg in context for neg in ["never use", "don't use", "do not use", "avoid", "prohibited", "anti-pattern"]):
                    continue
                warnings.append(f"Line {i}: cultural anti-pattern '{word}' — review context")

    return warnings


def check_model_routing(content: str) -> list[str]:
    """Check for model routing specification."""
    warnings = []
    found = any(re.search(p, content) for p in MODEL_ROUTING_PATTERNS)
    if not found:
        warnings.append("No model routing specified (haiku/sonnet/opus)")
    return warnings


def validate_skill(skill_dir: Path) -> dict:
    """Validate a single SKILL.md file. Returns JSON-serializable report."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return {
            "file": str(skill_dir),
            "passed": False,
            "warnings": [],
            "errors": [f"SKILL.md not found in {skill_dir}"],
        }

    content = skill_md.read_text()
    all_warnings = []
    all_errors = []

    # 1. Frontmatter
    fm, fm_errors = parse_frontmatter(content)
    all_errors.extend(fm_errors)

    # 2. Required sections
    section_warnings, section_errors = check_sections(content)
    all_warnings.extend(section_warnings)
    all_errors.extend(section_errors)

    # 3. Cultural anti-patterns
    anti_pattern_warnings = check_cultural_anti_patterns(content)
    all_warnings.extend(anti_pattern_warnings)

    # Also check any supplementary .md files in the same directory
    for md_file in skill_dir.glob("*.md"):
        if md_file.name == "SKILL.md":
            continue
        supp_content = md_file.read_text()
        supp_warnings = check_cultural_anti_patterns(supp_content)
        all_warnings.extend(
            w.replace("Line", f"{md_file.name} line") for w in supp_warnings
        )

    # 4. Model routing
    model_warnings = check_model_routing(content)
    all_warnings.extend(model_warnings)

    return {
        "file": str(skill_dir),
        "passed": len(all_errors) == 0,
        "warnings": all_warnings,
        "errors": all_errors,
    }


def find_skill_dirs(root: Path) -> list[Path]:
    """Find all directories containing SKILL.md files."""
    return sorted(d.parent for d in root.rglob("SKILL.md"))


def main():
    repo_root = Path(__file__).resolve().parent.parent
    agents_root = repo_root / "agents"

    if len(sys.argv) > 1:
        # Validate specific skill directory
        targets = [Path(sys.argv[1])]
    else:
        targets = find_skill_dirs(agents_root)

    results = []
    total_passed = 0
    total_failed = 0
    total_warnings = 0

    for skill_dir in targets:
        report = validate_skill(skill_dir)
        results.append(report)

        status = "PASS" if report["passed"] else "FAIL"
        if report["passed"]:
            total_passed += 1
        else:
            total_failed += 1
        total_warnings += len(report["warnings"])

        # Print summary per file
        rel_path = skill_dir.relative_to(agents_root) if agents_root in skill_dir.parents else skill_dir
        print(f"  {status}  {rel_path}", end="")
        if report["warnings"]:
            print(f"  ({len(report['warnings'])} warnings)", end="")
        print()

        for err in report["errors"]:
            print(f"         ERROR: {err}")
        for warn in report["warnings"]:
            print(f"         WARN:  {warn}")

    # Summary
    print(f"\n{'─' * 60}")
    print(f"  {total_passed} passed, {total_failed} failed, {total_warnings} warnings")
    print(f"{'─' * 60}")

    # Output JSON report
    report_path = repo_root / "validation-report.json"
    report_path.write_text(json.dumps(results, indent=2))
    print(f"\nFull report: {report_path}")

    return 0 if total_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
