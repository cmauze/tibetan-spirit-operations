#!/bin/bash
# Hook: SessionStart — context injection for tibetan-spirit-ops
# Event: SessionStart (fires on startup, resume, clear, compact)
# Purpose: Inject date, git state, agent activity, CS draft status, ORG.md reference

set -euo pipefail

INPUT=$(cat)
SOURCE=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('source','startup'))" 2>/dev/null || echo "startup")

TODAY=$(date +%Y-%m-%d)
DATA_DIR="data"

# Git context
BRANCH="unknown"
CHANGES="0"
if git rev-parse --is-inside-work-tree 2>/dev/null; then
    BRANCH=$(git branch --show-current 2>/dev/null || echo "detached")
    CHANGES=$(git status --short 2>/dev/null | wc -l | tr -d ' ')
fi

# Active agent run count (today)
AGENT_COUNT=$(python3 -c "
import json
from datetime import date
try:
    with open('$DATA_DIR/agent-runs.json', 'r') as f:
        runs = json.load(f)
    today = str(date.today())
    count = sum(1 for r in runs if r.get('timestamp', '').startswith(today))
    print(count)
except Exception:
    print(0)
" 2>/dev/null || echo "0")

# Pending CS drafts count (if cs-drafts directory or data exists)
CS_DRAFTS=$(python3 -c "
import json, os
count = 0
try:
    drafts_dir = '$DATA_DIR/cs-drafts'
    if os.path.isdir(drafts_dir):
        count = len([f for f in os.listdir(drafts_dir) if f.endswith('.json')])
    else:
        # Check agent-runs for pending cs-drafter outputs
        with open('$DATA_DIR/agent-runs.json', 'r') as f:
            runs = json.load(f)
        count = sum(1 for r in runs if r.get('agent') == 'cs-drafter' and r.get('status') == 'pending_review')
except Exception:
    pass
print(count)
" 2>/dev/null || echo "0")

echo "{\"additionalContext\": \"[tibetan-spirit-ops session ($SOURCE)] Date: $TODAY | Branch: $BRANCH | Uncommitted: $CHANGES | Today's agent runs: $AGENT_COUNT | Pending CS drafts: $CS_DRAFTS | Org chart: ORG.md | Full ops reference: docs/OPERATIONS-REFERENCE.md\"}"
exit 0
