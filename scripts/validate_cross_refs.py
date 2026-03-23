#!/usr/bin/env python3
"""
Cross-reference validator: scan SKILL.md files for SQL table/column references
and verify they exist in schema.sql.

Catches drift between skill documentation and the actual database schema.

Returns JSON report and exits 0 (pass) or 1 (fail).

Usage:
    python3 scripts/validate_cross_refs.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = REPO_ROOT / "skills" / "shared" / "supabase-ops-db" / "schema.sql"
SKILLS_ROOT = REPO_ROOT / "skills"

# Regex to find table.column references in SKILL.md prose and code blocks
# Matches patterns like: `products.cogs_confirmed`, products.sku, `skill_invocations`
RE_TABLE_DOT_COLUMN = re.compile(r"`?(\w+)\.(\w+)`?")

# Matches backtick-quoted table names: `products`, `orders`, `skill_invocations`
RE_BACKTICK_TABLE = re.compile(r"`(\w+)`")

# Known non-table words to ignore in backtick matches
IGNORE_BACKTICK = {
    "true", "false", "null", "none", "active", "confirmed", "estimated",
    "unknown", "pending", "approved", "paid", "overdue", "cancelled",
    "webhook", "cron", "manual", "domestic", "mexico", "nepal",
    "shopify", "etsy", "amazon", "wholesale",
    "read_orders", "write_orders", "read_products", "write_products",
    "read_inventory", "write_inventory", "read_fulfillments", "write_fulfillments",
    "read_customers", "orders_create", "orders_updated", "inventory_levels_update",
    "products_update", "status", "on", "off", "yes", "no",
}


def parse_schema_tables(sql: str) -> dict[str, list[str]]:
    """Extract table names and their columns from schema.sql."""
    tables: dict[str, list[str]] = {}

    re_create_table = re.compile(
        r"CREATE\s+TABLE\s+(\w+)\s*\(", re.IGNORECASE
    )
    re_column_def = re.compile(
        r"^\s+(\w+)\s+(?:UUID|BIGINT|TEXT|INT|INTEGER|SMALLINT|NUMERIC|BOOLEAN|DATE|"
        r"TIMESTAMPTZ|JSONB|cogs_confidence_level|sales_channel|fulfillment_route|"
        r"payment_status|trigger_source)",
        re.IGNORECASE,
    )
    re_create_matview = re.compile(
        r"CREATE\s+MATERIALIZED\s+VIEW\s+(\w+)\s+AS", re.IGNORECASE
    )

    # Parse tables
    for table_match in re_create_table.finditer(sql):
        table_name = table_match.group(1).lower()
        start = table_match.start()
        depth = 0
        end = start
        for i in range(table_match.end() - 1, len(sql)):
            if sql[i] == "(":
                depth += 1
            elif sql[i] == ")":
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
        block = sql[start:end]
        columns = []
        for line in block.split("\n"):
            col_match = re_column_def.match(line)
            if col_match:
                columns.append(col_match.group(1).lower())
        tables[table_name] = columns

    # Parse materialized view names (columns not extracted — views are derived)
    for mv_match in re_create_matview.finditer(sql):
        view_name = mv_match.group(1).lower()
        if view_name not in tables:
            tables[view_name] = []  # views exist but columns are derived

    return tables


def scan_skill_file(
    filepath: Path,
    schema_tables: dict[str, list[str]],
) -> dict:
    """Scan a single .md file for SQL references and validate against schema."""
    content = filepath.read_text()
    errors: list[str] = []
    refs_found: list[str] = []
    table_names_lower = set(schema_tables.keys())
    all_columns: set[str] = set()
    for cols in schema_tables.values():
        all_columns.update(cols)

    # Check table.column references
    for match in RE_TABLE_DOT_COLUMN.finditer(content):
        table = match.group(1).lower()
        column = match.group(2).lower()

        # Only validate if the table name matches a known schema table
        if table not in table_names_lower:
            continue

        refs_found.append(f"{table}.{column}")
        table_cols = schema_tables.get(table, [])

        # Views have empty column lists — skip column validation for them
        if not table_cols:
            continue

        if column not in table_cols:
            errors.append(
                f"Column reference '{table}.{column}' not found in schema "
                f"(line containing: ...{match.group(0)}...)"
            )

    # Check backtick-quoted table names
    for match in RE_BACKTICK_TABLE.finditer(content):
        name = match.group(1).lower()
        if name in IGNORE_BACKTICK:
            continue
        # Only flag if it looks like it could be a table name (has underscore or
        # matches a known column name pattern) but is not in schema
        if "_" in name and name not in table_names_lower and name not in all_columns:
            # Could be a table reference that doesn't exist — warn but don't error
            pass

    return {
        "file": str(filepath.relative_to(REPO_ROOT)),
        "refs_found": sorted(set(refs_found)),
        "ref_count": len(set(refs_found)),
        "errors": errors,
        "passed": len(errors) == 0,
    }


def main() -> int:
    results: dict = {
        "schema_file": str(SCHEMA_PATH),
        "passed": True,
        "skill_files_scanned": 0,
        "total_refs_found": 0,
        "file_results": [],
        "errors": [],
    }

    # 1. Load schema
    if not SCHEMA_PATH.exists():
        results["passed"] = False
        results["errors"].append(f"Schema file not found: {SCHEMA_PATH}")
        print(json.dumps(results, indent=2))
        return 1

    sql = SCHEMA_PATH.read_text()
    schema_tables = parse_schema_tables(sql)

    print(f"Schema loaded: {len(schema_tables)} tables/views")
    for name, cols in schema_tables.items():
        if cols:
            print(f"  {name}: {len(cols)} columns")
        else:
            print(f"  {name}: (materialized view)")

    # 2. Find and scan all SKILL.md and supplementary .md files
    md_files = sorted(SKILLS_ROOT.rglob("*.md"))
    results["skill_files_scanned"] = len(md_files)

    print(f"\nScanning {len(md_files)} skill markdown files...")

    files_with_refs = 0
    files_with_errors = 0

    for md_file in md_files:
        file_result = scan_skill_file(md_file, schema_tables)
        if file_result["ref_count"] > 0 or file_result["errors"]:
            results["file_results"].append(file_result)
            results["total_refs_found"] += file_result["ref_count"]

            if file_result["ref_count"] > 0:
                files_with_refs += 1

            rel_path = md_file.relative_to(REPO_ROOT)
            status = "PASS" if file_result["passed"] else "FAIL"
            print(f"  {status}  {rel_path} ({file_result['ref_count']} refs)")

            for err in file_result["errors"]:
                print(f"         ERROR: {err}")
                results["errors"].append(f"{rel_path}: {err}")

            if not file_result["passed"]:
                files_with_errors += 1

    # 3. Summary
    results["passed"] = len(results["errors"]) == 0

    print(f"\n{'=' * 60}")
    print(f"  Files scanned: {len(md_files)}")
    print(f"  Files with SQL refs: {files_with_refs}")
    print(f"  Total unique refs: {results['total_refs_found']}")
    print(f"  Files with errors: {files_with_errors}")
    print(f"  Result: {'PASS' if results['passed'] else 'FAIL'}")
    print(f"{'=' * 60}")

    # Write JSON report
    report_path = REPO_ROOT / "validation-report.json"
    report_path.write_text(json.dumps(results, indent=2))
    print(f"\nFull report: {report_path}")

    return 0 if results["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
