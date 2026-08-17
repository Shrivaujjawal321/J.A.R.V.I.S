#!/usr/bin/env bash
# Run the Tester Agent on a single app via headless `claude -p`.
#
# Usage: ./test-app.sh <app-name> <port>
#   app-name : directory under apps/, e.g. 01-hiresync-ai
#   port     : dev-server port, e.g. 3001

set -uo pipefail

APP_NAME="${1:?app name required}"
PORT="${2:?port required}"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP_DIR="$ROOT/$APP_NAME"
SYS_DIR="$ROOT/agentic-system"
PROMPT_FILE="$SYS_DIR/prompts/tester.md"
REPORT_DIR="$SYS_DIR/reports/$APP_NAME"
REPORT_PATH="$REPORT_DIR/test.json"

mkdir -p "$REPORT_DIR"

if [ ! -d "$APP_DIR" ]; then
  echo "{\"app\":\"$APP_NAME\",\"status\":\"red\",\"phase\":\"setup\",\"errors\":[\"app dir not found\"]}" > "$REPORT_PATH"
  exit 1
fi

# Build the user message: prompt + concrete inputs
INPUT=$(cat <<EOF
$(cat "$PROMPT_FILE")

---

## Run inputs
- APP_NAME: $APP_NAME
- APP_DIR: $APP_DIR
- PORT: $PORT
- REPORT_PATH: $REPORT_PATH

Begin now. Write the JSON report to REPORT_PATH at the end (always — even on failure).
EOF
)

# Allow the tools the tester needs. Bash is broad; we constrain the agent via the prompt's "hard rules".
ALLOWED='Bash,Read,Edit,Write,Grep,Glob,mcp__chrome-devtools__new_page,mcp__chrome-devtools__navigate_page,mcp__chrome-devtools__take_snapshot,mcp__chrome-devtools__list_console_messages,mcp__chrome-devtools__click,mcp__chrome-devtools__wait_for,mcp__chrome-devtools__close_page,mcp__chrome-devtools__list_pages,mcp__chrome-devtools__select_page'

cd "$APP_DIR"
echo "[tester] $APP_NAME on port $PORT — starting"

# claude -p runs headless; --add-dir scopes file ops; subscription auth is inherited.
echo "$INPUT" | claude -p \
  --add-dir "$APP_DIR" \
  --add-dir "$SYS_DIR" \
  --allowedTools "$ALLOWED" \
  --permission-mode bypassPermissions \
  > "$REPORT_DIR/agent.stdout.log" 2> "$REPORT_DIR/agent.stderr.log"

# Make sure the dev server didn't leak
PIDFILE="/tmp/devserver-$APP_NAME.pid"
if [ -f "$PIDFILE" ]; then
  kill "$(cat "$PIDFILE")" 2>/dev/null || true
  rm -f "$PIDFILE"
fi

if [ ! -f "$REPORT_PATH" ]; then
  echo "{\"app\":\"$APP_NAME\",\"status\":\"red\",\"phase\":\"agent\",\"errors\":[\"agent did not write report\"]}" > "$REPORT_PATH"
fi

STATUS=$(grep -oE '"status"[[:space:]]*:[[:space:]]*"[^"]*"' "$REPORT_PATH" | head -1 | sed -E 's/.*"([^"]+)"$/\1/')
echo "[tester] $APP_NAME → ${STATUS:-unknown}"
