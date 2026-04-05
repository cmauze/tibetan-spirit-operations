#!/bin/bash
# Hook: PreToolUse budget check for tibetan-spirit-ops
# Matcher: mcp__shopify__.*|Bash
# Exit 0 = allow, Exit 2 = block

set -euo pipefail

# Per-agent daily budget caps (USD)
declare -A BUDGETS=(
  ["cs-drafter"]="2.00"
  ["finance-analyst"]="0.50"
  ["fulfillment-manager"]="2.00"
  ["inventory-analyst"]="2.00"
  ["marketing-strategist"]="2.00"
  ["catalog-curator"]="5.00"
)
DEFAULT_BUDGET="2.00"

DATA_FILE="data/agent-runs.json"
TODAY=$(date +%Y-%m-%d)

# If no data file, allow (nothing spent yet)
if [ ! -f "$DATA_FILE" ]; then
  echo '{"continue": true}'
  exit 0
fi

# Parse input for agent context
INPUT=$(cat)
AGENT=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(d.get('agent_name', 'unknown'))
except:
    print('unknown')
" 2>/dev/null || echo "unknown")

BUDGET="${BUDGETS[$AGENT]:-$DEFAULT_BUDGET}"

# Sum today's cost for this agent
DAILY_SPEND=$(python3 -c "
import json
from datetime import date
try:
    with open('$DATA_FILE') as f:
        runs = json.load(f)
    total = sum(
        r.get('cost_usd', 0)
        for r in runs
        if r.get('agent') == '$AGENT' and r.get('date', '').startswith('$TODAY')
    )
    print(f'{total:.2f}')
except Exception:
    print('0.00')
" 2>/dev/null || echo "0.00")

# Check against budget
if python3 -c "exit(0 if float('$DAILY_SPEND') >= float('$BUDGET') else 1)" 2>/dev/null; then
  echo "Agent $AGENT daily budget of \$$BUDGET exceeded (spent: \$$DAILY_SPEND)" >&2
  exit 2
fi

echo '{"continue": true}'
exit 0
