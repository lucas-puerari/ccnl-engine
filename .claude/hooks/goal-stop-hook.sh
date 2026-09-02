#!/bin/bash
# goal-stop-hook.sh — project-local Stop hook for git-history-based goal tracking.
# Goal is reached when git log contains at least (baseline + target) feat CCNL commits.

set -euo pipefail

GOAL_FILE=".claude/GOAL.md"

if [[ ! -f "$GOAL_FILE" ]]; then
  exit 0
fi

FRONTMATTER=$(sed -n '/^---$/,/^---$/{ /^---$/d; p; }' "$GOAL_FILE")
STATUS=$(echo "$FRONTMATTER" | grep '^status:' | sed 's/status: *//' | tr -d ' "' || echo "")
BASELINE=$(echo "$FRONTMATTER" | grep '^baseline:' | sed 's/baseline: *//' | tr -d ' "' || echo "0")
TARGET=$(echo "$FRONTMATTER" | grep '^target:' | sed 's/target: *//' | tr -d ' "' || echo "")

if [[ "$STATUS" != "active" ]]; then
  exit 0
fi

if [[ -z "$TARGET" ]] || ! [[ "$TARGET" =~ ^[0-9]+$ ]]; then
  echo "⚠️  GOAL.md is active but target is missing or invalid. Edit .claude/GOAL.md to fix." >&2
  exit 0
fi

# Count contract JSON files — source of truth, independent of commit message wording
CURRENT=$(ls src/ccnl_engine/contracts/data/*.json 2>/dev/null | grep -v '__init__' | wc -l | tr -d ' ')
NEEDED=$(( BASELINE + TARGET ))
ADDED=$(( CURRENT - BASELINE ))

if [[ "$CURRENT" -ge "$NEEDED" ]]; then
  TEMP_FILE="${GOAL_FILE}.tmp.$$"
  sed "s/^status: .*/status: done/" "$GOAL_FILE" > "$TEMP_FILE"
  mv "$TEMP_FILE" "$GOAL_FILE"
  echo "✅ Goal achieved: $ADDED new CCNL contracts added (needed $TARGET)."
  exit 0
fi

REMAINING=$(( NEEDED - CURRENT ))
GOAL_BODY=$(awk '/^---$/{i++; next} i>=2' "$GOAL_FILE")

jq -n \
  --arg goal "$GOAL_BODY" \
  --argjson added "$ADDED" \
  --argjson remaining "$REMAINING" \
  --argjson target "$TARGET" \
  '{
    "decision": "block",
    "reason": ("🎯 Progress: " + ($added|tostring) + "/" + ($target|tostring) + " CCNL contracts added. " + ($remaining|tostring) + " remaining.\n\n" + $goal),
    "systemMessage": ("🎯 Goal active | " + ($added|tostring) + "/" + ($target|tostring) + " CCNL added — " + ($remaining|tostring) + " more needed.")
  }'

exit 0
