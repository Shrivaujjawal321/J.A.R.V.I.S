#!/usr/bin/env bash
# Run the Publisher Agent on a single app via headless `claude -p`.
#
# Usage: ./publish-app.sh <app-name> [allow-yellow]
#   app-name     : e.g. 02-invoflow
#   allow-yellow : "true" to publish yellow apps too (default: false)

set -uo pipefail

APP_NAME="${1:?app name required}"
ALLOW_YELLOW="${2:-false}"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP_DIR="$ROOT/$APP_NAME"
SYS_DIR="$ROOT/agentic-system"
PROMPT_FILE="$SYS_DIR/prompts/publisher.md"
REPORT_DIR="$SYS_DIR/reports/$APP_NAME"
TEST_REPORT="$REPORT_DIR/test.json"
REPORT_PATH="$REPORT_DIR/publish.json"

mkdir -p "$REPORT_DIR"

if [ ! -f "$TEST_REPORT" ]; then
  echo "{\"app\":\"$APP_NAME\",\"status\":\"skipped\",\"reason\":\"no test report\"}" > "$REPORT_PATH"
  echo "[publisher] $APP_NAME → skipped (no test report)"
  exit 0
fi

INPUT=$(cat <<EOF
$(cat "$PROMPT_FILE")

---

## Run inputs
- APP_NAME: $APP_NAME
- APP_DIR: $APP_DIR
- TEST_REPORT_PATH: $TEST_REPORT
- REPORT_PATH: $REPORT_PATH
- ALLOW_YELLOW: $ALLOW_YELLOW

Begin now. Always write the JSON report to REPORT_PATH at the end.
EOF
)

ALLOWED='Bash,Read'

cd "$APP_DIR"
echo "[publisher] $APP_NAME — starting (allow-yellow=$ALLOW_YELLOW)"

echo "$INPUT" | claude -p \
  --add-dir "$APP_DIR" \
  --add-dir "$SYS_DIR" \
  --allowedTools "$ALLOWED" \
  --permission-mode bypassPermissions \
  > "$REPORT_DIR/publish.stdout.log" 2> "$REPORT_DIR/publish.stderr.log"

if [ ! -f "$REPORT_PATH" ]; then
  echo "{\"app\":\"$APP_NAME\",\"status\":\"failed\",\"reason\":\"agent did not write report\"}" > "$REPORT_PATH"
fi

STATUS=$(grep -oE '"status"[[:space:]]*:[[:space:]]*"[^"]*"' "$REPORT_PATH" | head -1 | sed -E 's/.*"([^"]+)"$/\1/')
echo "[publisher] $APP_NAME → ${STATUS:-unknown}"
