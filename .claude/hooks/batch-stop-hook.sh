#!/bin/bash
# batch-stop-hook.sh — Stop hook for /batch loop tracking.
# Reads progress_cmd from .claude/GOAL.md and blocks stop until target is reached.

set -euo pipefail

# Read stdin — hooks receive a JSON object with session context.
# Exit immediately for subagent stops; only enforce on the interactive session.
INPUT=$(cat)
HOOK_EVENT=$(echo "$INPUT" | jq -r '.hook_event_name // "Stop"' 2>/dev/null || echo "Stop")
if [[ "$HOOK_EVENT" != "Stop" ]]; then
  exit 0
fi

GOAL_FILE=".claude/GOAL.md"

if [[ ! -f "$GOAL_FILE" ]]; then
  exit 0
fi

FRONTMATTER=$(sed -n '/^---$/,/^---$/{ /^---$/d; p; }' "$GOAL_FILE")
STATUS=$(echo "$FRONTMATTER" | grep '^status:' | sed 's/status: *//' | tr -d ' "' || echo "")
BASELINE=$(echo "$FRONTMATTER" | grep '^baseline:' | sed 's/baseline: *//' | tr -d ' "' || echo "0")
TARGET=$(echo "$FRONTMATTER" | grep '^target:' | sed 's/target: *//' | tr -d ' "' || echo "")
PROGRESS_CMD=$(echo "$FRONTMATTER" | grep '^progress_cmd:' | sed 's/progress_cmd: *//' | tr -d '"' || echo "")

if [[ "$STATUS" != "active" ]]; then
  exit 0
fi

if [[ -z "$TARGET" ]] || ! [[ "$TARGET" =~ ^[0-9]+$ ]]; then
  echo "⚠️  GOAL.md is active but target is missing or invalid." >&2
  exit 0
fi

if [[ -z "$PROGRESS_CMD" ]]; then
  echo "⚠️  GOAL.md is active but progress_cmd is missing." >&2
  exit 0
fi

# Run the configurable progress command to get the current count.
CURRENT=$(bash -c "$PROGRESS_CMD" 2>/dev/null | tr -d ' ' || echo "0")
if ! [[ "$CURRENT" =~ ^[0-9]+$ ]]; then
  echo "⚠️  progress_cmd did not return an integer (got: $CURRENT)." >&2
  exit 0
fi

NEEDED=$(( BASELINE + TARGET ))
DONE=$(( CURRENT - BASELINE ))

if [[ "$CURRENT" -ge "$NEEDED" ]]; then
  TEMP_FILE="${GOAL_FILE}.tmp.$$"
  sed "s/^status: .*/status: done/" "$GOAL_FILE" > "$TEMP_FILE"
  mv "$TEMP_FILE" "$GOAL_FILE"
  echo "✅ Batch complete: $DONE/$TARGET iterations done."
  exit 0
fi

REMAINING=$(( NEEDED - CURRENT ))
GOAL_BODY=$(awk '/^---$/{i++; next} i>=2' "$GOAL_FILE")

jq -n \
  --arg goal "$GOAL_BODY" \
  --argjson done "$DONE" \
  --argjson remaining "$REMAINING" \
  --argjson target "$TARGET" \
  '{
    "decision": "block",
    "reason": ("🎯 Progress: " + ($done|tostring) + "/" + ($target|tostring) + " iterations done. " + ($remaining|tostring) + " remaining.\n\n" + $goal),
    "systemMessage": ("🎯 Batch active | " + ($done|tostring) + "/" + ($target|tostring) + " done — " + ($remaining|tostring) + " remaining.")
  }'

exit 0
