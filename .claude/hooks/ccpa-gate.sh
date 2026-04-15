#!/bin/bash
# ccpa-gate.sh — Block direct email sending from agents
# Exit 2 = BLOCK, Exit 1 = WARN, Exit 0 = PASS
#
# Checks PreToolUse for any tool that could send email directly.
# cs-drafter must DRAFT only, never SEND.

TOOL_NAME="${CLAUDE_TOOL_NAME:-}"

# Block any gmail send tools (not search/read/draft)
case "$TOOL_NAME" in
  *gmail_send*)
    echo "BLOCKED: Direct email sending is prohibited. Use draft workflow instead."
    exit 2
    ;;
  *gmail_create_draft*)
    # gmail_create_draft is allowed — it creates a draft, not sends
    exit 0
    ;;
  *)
    exit 0
    ;;
esac
