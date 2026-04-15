#!/usr/bin/env python3
"""
Run the financial scenario model end-to-end.

Usage:
    python3 scripts/financial_model/run.py
    python3 scripts/financial_model/run.py --scenarios path/to/custom.yaml
"""
import argparse
import os
import sys
from pathlib import Path

# Support running from worktree or main repo root (same pattern as baseline.py).
_root = Path(__file__).resolve().parent.parent.parent

from dotenv import load_dotenv

load_dotenv(_root / ".env")
if not os.environ.get("SUPABASE_URL"):
    load_dotenv(_root.parent.parent / ".env")

sys.path.insert(0, str(_root / "lib"))
sys.path.insert(0, str(_root))

from scripts.financial_model.baseline import build_baseline
from scripts.financial_model.scenarios import run_all_scenarios
from scripts.financial_model.output import (
    save_json_output,
    save_markdown_report,
    format_comparison_table,
)

DEFAULT_SCENARIOS = Path(__file__).parent / "config" / "scenarios.yaml"


def main():
    parser = argparse.ArgumentParser(
        description="Tibetan Spirit line extension scenario model"
    )
    parser.add_argument(
        "--scenarios",
        type=Path,
        default=DEFAULT_SCENARIOS,
        help="Path to scenarios YAML file",
    )
    args = parser.parse_args()

    print("Pulling baseline from Supabase...")
    baseline = build_baseline()

    print(f"Running scenarios from {args.scenarios}...")
    results = run_all_scenarios(args.scenarios)

    # Print comparison to stdout
    print("\n" + format_comparison_table(results))

    # Save outputs
    json_path = save_json_output(results, _root / "data" / "financial-model")
    md_path = save_markdown_report(
        baseline, results, _root / "deliverables" / "docs"
    )

    print(f"\nJSON saved: {json_path}")
    print(f"Report saved: {md_path}")


if __name__ == "__main__":
    main()
