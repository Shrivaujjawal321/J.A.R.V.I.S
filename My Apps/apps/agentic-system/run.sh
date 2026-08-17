#!/usr/bin/env bash
# Orchestrator — runs Tester then Publisher on every numbered app, sequentially.
#
# Usage:
#   ./run.sh                       # all apps 01-10
#   ./run.sh 01-hiresync-ai 04-learnforge   # specific apps
#   ALLOW_YELLOW=true ./run.sh     # publish yellow apps too
#   SKIP_PUBLISH=true ./run.sh     # only test, don't push/deploy
#   START_PORT=4001 ./run.sh       # change base port (default 3001)

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SYS_DIR="$ROOT/agentic-system"

ALLOW_YELLOW="${ALLOW_YELLOW:-false}"
SKIP_PUBLISH="${SKIP_PUBLISH:-false}"
START_PORT="${START_PORT:-3001}"

# Pick apps
if [ $# -gt 0 ]; then
  APPS=("$@")
else
  mapfile -t APPS < <(cd "$ROOT" && ls -d [0-9][0-9]-*/ 2>/dev/null | sed 's:/$::' | sort)
fi

if [ ${#APPS[@]} -eq 0 ]; then
  echo "no apps found in $ROOT" >&2
  exit 1
fi

echo "═══════════════════════════════════════════════════════════"
echo "  Agentic system — testing ${#APPS[@]} app(s)"
echo "  Root:         $ROOT"
echo "  Allow yellow: $ALLOW_YELLOW"
echo "  Skip publish: $SKIP_PUBLISH"
echo "═══════════════════════════════════════════════════════════"

PORT=$START_PORT
declare -A TEST_STATUS
declare -A PUB_STATUS

for APP in "${APPS[@]}"; do
  echo ""
  echo "── $APP ─────────────────────────────────────────────"
  bash "$SYS_DIR/test-app.sh" "$APP" "$PORT"
  TR="$SYS_DIR/reports/$APP/test.json"
  TEST_STATUS[$APP]=$(grep -oE '"status"[[:space:]]*:[[:space:]]*"[^"]*"' "$TR" 2>/dev/null | head -1 | sed -E 's/.*"([^"]+)"$/\1/')
  TEST_STATUS[$APP]="${TEST_STATUS[$APP]:-unknown}"

  if [ "$SKIP_PUBLISH" != "true" ]; then
    bash "$SYS_DIR/publish-app.sh" "$APP" "$ALLOW_YELLOW"
    PR="$SYS_DIR/reports/$APP/publish.json"
    PUB_STATUS[$APP]=$(grep -oE '"status"[[:space:]]*:[[:space:]]*"[^"]*"' "$PR" 2>/dev/null | head -1 | sed -E 's/.*"([^"]+)"$/\1/')
    PUB_STATUS[$APP]="${PUB_STATUS[$APP]:-unknown}"
  else
    PUB_STATUS[$APP]="skipped"
  fi

  PORT=$((PORT + 1))
done

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  Summary"
echo "═══════════════════════════════════════════════════════════"
printf "  %-25s  %-10s  %-10s\n" "APP" "TEST" "PUBLISH"
printf "  %-25s  %-10s  %-10s\n" "───" "────" "───────"
for APP in "${APPS[@]}"; do
  printf "  %-25s  %-10s  %-10s\n" "$APP" "${TEST_STATUS[$APP]}" "${PUB_STATUS[$APP]}"
done
echo ""
echo "  Reports: $SYS_DIR/reports/<app>/{test,publish}.json"
