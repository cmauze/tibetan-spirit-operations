#!/usr/bin/env bash
# publish-plugin.sh — Regenerate plugin skills/ from project skills/ with sanitization
#
# Usage: scripts/publish-plugin.sh
#
# Project skills/ is the canonical operational source.
# Plugin skills/ is auto-generated. Do not edit plugin skills/ directly.
# Sanitization rules are defined in plugin/d2c-operations-lead/sanitize.yaml.

set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$REPO/skills"
DEST="$REPO/plugin/d2c-operations-lead/skills"
SANITIZE="$REPO/plugin/d2c-operations-lead/sanitize.yaml"
APPLY_SCRIPT="$REPO/scripts/_apply_sanitize.py"

echo "[publish] Regenerating plugin skills from project skills..."
echo "[publish] Source:      $SRC"
echo "[publish] Destination: $DEST"
echo "[publish] Rules:       $SANITIZE"
echo ""

# ── Step 1: Clean copy ────────────────────────────────────────────────────────
rm -rf "$DEST"
cp -R "$SRC" "$DEST"
find "$DEST" -name ".DS_Store" -delete

echo "[publish] Copied $(find "$DEST" -type f | wc -l | tr -d ' ') files to plugin."
echo ""

# ── Step 2: Apply sanitization replacements ───────────────────────────────────
python3 "$APPLY_SCRIPT" "$DEST" "$SANITIZE"
echo ""

# ── Step 3: Report remaining differences ─────────────────────────────────────
echo "[publish] Checking for remaining differences between project and plugin..."
remaining=$(diff -rq "$SRC" "$DEST" 2>/dev/null || true)

if [[ -z "$remaining" ]]; then
  echo "[publish] WARNING: No remaining differences. Plugin is identical to project."
  echo "[publish] Check sanitize.yaml — replacements may not be matching."
else
  echo "$remaining"
  echo ""
  echo "[publish] Review diff above."
  echo "[publish] Differences should reflect only intentional sanitization replacements."
  echo "[publish] If unexpected differences remain, add rules to sanitize.yaml."
fi

echo ""
echo "[publish] Done."
