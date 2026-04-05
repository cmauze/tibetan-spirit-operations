#!/usr/bin/env python3
"""
Look up a Shopify order by number. Thin wrapper around shopify_query.py.
Referenced by cs-drafter.md for order enrichment during CS workflows.

Usage:
    python3 scripts/lookup-order.py <order_number>
    python3 scripts/lookup-order.py 1234
"""

import subprocess
import sys
import os

if len(sys.argv) < 2:
    print("Usage: lookup-order.py <order_number>", file=sys.stderr)
    sys.exit(1)

script_dir = os.path.dirname(os.path.abspath(__file__))
result = subprocess.run(
    [sys.executable, os.path.join(script_dir, "shopify_query.py"), "order", sys.argv[1]],
    capture_output=False,
)
sys.exit(result.returncode)
