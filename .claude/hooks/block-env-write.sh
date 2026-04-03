#!/bin/bash
# Hook: PreToolUse — block writes to .env files
# Matcher: Write|Edit
# Exit 0 = allow, Exit 2 = block
set -euo pipefail

INPUT=$(cat)

FILE_PATH=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    inp = d.get('tool_input', {})
    print(inp.get('file_path', inp.get('path', '')))
except Exception:
    print('')
" 2>/dev/null || echo "")

if echo "$FILE_PATH" | grep -qE '(^|/)\.env($|\.)'; then
  echo "BLOCKED: Writing to .env files is not permitted." >&2
  exit 2
fi

exit 0
