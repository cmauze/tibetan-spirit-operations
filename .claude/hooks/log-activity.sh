#!/bin/bash
# Hook: PostToolUse activity logger for tibetan-spirit-ops
# Matcher: Bash|Write|Edit|mcp__.*
# Async: true (non-blocking)

set -euo pipefail

DATA_FILE="data/agent-runs.json"
TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)
TODAY=$(date +%Y-%m-%d)

# Create data dir and file if missing
mkdir -p data
if [ ! -f "$DATA_FILE" ]; then
  echo '[]' > "$DATA_FILE"
fi

# Parse input
INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(d.get('tool_name', 'unknown'))
except:
    print('unknown')
" 2>/dev/null || echo "unknown")

SESSION_ID=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(d.get('session_id', 'unknown'))
except:
    print('unknown')
" 2>/dev/null || echo "unknown")

# Append log entry
python3 -c "
import json

entry = {
    'timestamp': '$TIMESTAMP',
    'date': '$TODAY',
    'tool': '$TOOL_NAME',
    'session_id': '$SESSION_ID',
    'agent': 'unknown',
    'cost_usd': 0.0
}

try:
    with open('$DATA_FILE') as f:
        runs = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    runs = []

runs.append(entry)

# Keep last 1000 entries to prevent unbounded growth
runs = runs[-1000:]

with open('$DATA_FILE', 'w') as f:
    json.dump(runs, f, indent=2)
" 2>/dev/null || true

exit 0
