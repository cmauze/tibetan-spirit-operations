#!/bin/bash
# Hook: Stop — check for uncommitted secrets in staged changes
# Exit 0 = allow, Exit 1 = warn (non-blocking)
set -euo pipefail

if ! git rev-parse --is-inside-work-tree 2>>"${TMPDIR:-/tmp}/ts-ops-hooks.log"; then
  exit 0
fi

STAGED=$(git diff --cached --diff-filter=ACM 2>/dev/null || true)
if [ -z "$STAGED" ]; then
  exit 0
fi

PATTERNS='(sk-[a-zA-Z0-9]{20,}|xoxb-[a-zA-Z0-9-]+|AKIA[0-9A-Z]{16}|ghp_[a-zA-Z0-9]{36}|glpat-[a-zA-Z0-9_-]{20,})'

if echo "$STAGED" | grep -qE "$PATTERNS"; then
  echo "WARNING: Staged changes may contain API keys or tokens." >&2
  echo "Review staged diff before committing." >&2
  exit 1
fi

exit 0
