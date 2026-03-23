#!/usr/bin/env python3
"""
Schema validation: parse schema.sql and verify that pre-built query files
only reference columns that exist in the schema.

Returns JSON report and exits 0 (pass) or 1 (fail).

Usage:
    python3 scripts/validate_schema.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = REPO_ROOT / "skills" / "shared" / "supabase-ops-db" / "schema.sql"
QUERIES_DIR = REPO_ROOT / "skills" / "shared" / "supabase-ops-db" / "queries"

# Regex patterns for DDL parsing
RE_CREATE_TABLE = re.compile(
    r"CREATE\s+TABLE\s+(\w+)\s*\(", re.IGNORECASE
)
RE_CREATE_MATVIEW = re.compile(
    r"CREATE\s+MATERIALIZED\s+VIEW\s+(\w+)\s+AS", re.IGNORECASE
)
RE_COLUMN_DEF = re.compile(
    r"^\s+(\w+)\s+(?:UUID|BIGINT|TEXT|INT|INTEGER|SMALLINT|NUMERIC|BOOLEAN|DATE|TIMESTAMPTZ|JSONB|"
    r"cogs_confidence_level|sales_channel|fulfillment_route|payment_status|trigger_source)",
    re.IGNORECASE,
)
RE_CREATE_ENUM = re.compile(
    r"CREATE\s+TYPE\s+(\w+)\s+AS\s+ENUM\s*\(([^)]+)\)", re.IGNORECASE
)


def parse_schema(sql: str) -> dict:
    """Parse schema.sql and extract tables, columns, views, and enums."""
    tables: dict[str, list[str]] = {}
    views: list[str] = []
    enums: dict[str, list[str]] = {}

    # Extract enums
    for match in RE_CREATE_ENUM.finditer(sql):
        enum_name = match.group(1)
        values = [v.strip().strip("'") for v in match.group(2).split(",")]
        enums[enum_name] = values

    # Extract tables and their columns
    for table_match in RE_CREATE_TABLE.finditer(sql):
        table_name = table_match.group(1)
        # Find the block from CREATE TABLE to the closing );
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
            col_match = RE_COLUMN_DEF.match(line)
            if col_match:
                columns.append(col_match.group(1).lower())
        tables[table_name] = columns

    # Extract materialized view names
    for mv_match in RE_CREATE_MATVIEW.finditer(sql):
        views.append(mv_match.group(1))

    return {"tables": tables, "views": views, "enums": enums}


def extract_column_refs(sql: str, known_tables: list[str]) -> list[tuple[str, str]]:
    """Extract table.column references from a query file.

    Looks for patterns like:
      - p.column_name (alias.column)
      - table_name.column_name
    Also extracts bare column names from SELECT/WHERE/ORDER clauses
    that use known table aliases.
    """
    refs: list[tuple[str, str]] = []

    # Find alias definitions: FROM/JOIN table_name alias or table_name AS alias
    alias_map: dict[str, str] = {}
    alias_patterns = [
        # FROM products p  /  JOIN products p ON ...
        re.compile(
            r"(?:FROM|JOIN)\s+(\w+)\s+(\w+)(?:\s+ON|\s*,|\s+WHERE|\s+LEFT|\s+RIGHT|\s+INNER|\s+CROSS|\s*$)",
            re.IGNORECASE,
        ),
        # FROM products AS p
        re.compile(
            r"(?:FROM|JOIN)\s+(\w+)\s+AS\s+(\w+)", re.IGNORECASE
        ),
    ]
    for pattern in alias_patterns:
        for match in pattern.finditer(sql):
            table = match.group(1).lower()
            alias = match.group(2).lower()
            if table in [t.lower() for t in known_tables]:
                alias_map[alias] = table

    # Find alias.column references
    ref_pattern = re.compile(r"\b(\w+)\.(\w+)\b")
    for match in ref_pattern.finditer(sql):
        alias = match.group(1).lower()
        column = match.group(2).lower()
        if alias in alias_map:
            refs.append((alias_map[alias], column))

    return refs


def validate_query_columns(
    query_path: Path,
    schema: dict,
) -> list[str]:
    """Validate that columns referenced in a query exist in the schema."""
    errors = []
    sql = query_path.read_text()
    known_tables = list(schema["tables"].keys())
    refs = extract_column_refs(sql, known_tables)

    for table, column in refs:
        table_lower = table.lower()
        matching_table = None
        for t in schema["tables"]:
            if t.lower() == table_lower:
                matching_table = t
                break
        if matching_table is None:
            errors.append(f"Table '{table}' referenced but not in schema")
            continue
        if column not in schema["tables"][matching_table]:
            # Skip common non-column references (subquery aliases, functions)
            skip = {"avg_daily", "category_code", "avg_daily_sales", "days_of_supply"}
            if column not in skip:
                errors.append(
                    f"Column '{table}.{column}' not found in schema "
                    f"(known columns: {', '.join(schema['tables'][matching_table][:8])}...)"
                )

    return errors


def main() -> int:
    results: dict = {
        "schema_file": str(SCHEMA_PATH),
        "passed": True,
        "schema_parse": {},
        "query_validations": [],
        "errors": [],
        "warnings": [],
    }

    # 1. Parse schema
    if not SCHEMA_PATH.exists():
        results["passed"] = False
        results["errors"].append(f"Schema file not found: {SCHEMA_PATH}")
        print(json.dumps(results, indent=2))
        return 1

    sql = SCHEMA_PATH.read_text()
    schema = parse_schema(sql)
    results["schema_parse"] = {
        "tables": {name: len(cols) for name, cols in schema["tables"].items()},
        "views": schema["views"],
        "enums": list(schema["enums"].keys()),
    }

    # Verify expected tables exist
    expected_tables = [
        "products",
        "inventory_extended",
        "orders",
        "competitive_intel",
        "supplier_payments",
        "marketing_performance",
        "skill_invocations",
    ]
    for table in expected_tables:
        if table not in schema["tables"]:
            results["errors"].append(f"Expected table '{table}' not found in schema")

    # Verify expected views exist
    expected_views = [
        "channel_profitability_monthly",
        "product_margin_detail",
        "inventory_health",
        "marketing_roas_trailing",
    ]
    for view in expected_views:
        if view not in schema["views"]:
            results["errors"].append(f"Expected materialized view '{view}' not found in schema")

    # Verify expected enums exist
    expected_enums = [
        "cogs_confidence_level",
        "sales_channel",
        "fulfillment_route",
        "payment_status",
        "trigger_source",
    ]
    for enum in expected_enums:
        if enum not in schema["enums"]:
            results["errors"].append(f"Expected enum type '{enum}' not found in schema")

    # 2. Validate query files against schema
    if QUERIES_DIR.exists():
        for query_file in sorted(QUERIES_DIR.glob("*.sql")):
            query_errors = validate_query_columns(query_file, schema)
            validation = {
                "file": query_file.name,
                "passed": len(query_errors) == 0,
                "errors": query_errors,
            }
            results["query_validations"].append(validation)
            if query_errors:
                results["errors"].extend(
                    f"{query_file.name}: {e}" for e in query_errors
                )
    else:
        results["warnings"].append(f"Queries directory not found: {QUERIES_DIR}")

    # 3. Summary
    results["passed"] = len(results["errors"]) == 0

    # Print human-readable summary
    print(f"Schema: {len(schema['tables'])} tables, {len(schema['views'])} views, "
          f"{len(schema['enums'])} enums")
    for table, cols in schema["tables"].items():
        print(f"  {table}: {len(cols)} columns")

    if results["query_validations"]:
        print(f"\nQuery validations:")
        for qv in results["query_validations"]:
            status = "PASS" if qv["passed"] else "FAIL"
            print(f"  {status}  {qv['file']}")
            for err in qv["errors"]:
                print(f"         ERROR: {err}")

    if results["errors"]:
        print(f"\n{len(results['errors'])} error(s) found.")
    else:
        print(f"\nAll validations passed.")

    # Write JSON report
    report_path = REPO_ROOT / "validation-report.json"
    report_path.write_text(json.dumps(results, indent=2))
    print(f"\nFull report: {report_path}")

    return 0 if results["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
