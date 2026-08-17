#!/usr/bin/env bash
# THE EDITH — one-command launcher (backend :8077 + frontend :3000).
# Usage:  bash start.sh            (production frontend if built, else dev)
#         bash start.sh dev        (force dev frontend)
#         bash start.sh stop       (stop both)
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
LOGS="$HERE/data/logs"; mkdir -p "$LOGS"

if [ "${1:-}" = "stop" ]; then
  fuser -k 8077/tcp 2>/dev/null || true
  fuser -k 3000/tcp 2>/dev/null || true
  echo "EDITH stopped (ports 8077 + 3000 freed)."
  exit 0
fi

# ── backend ───────────────────────────────────────────────────────────────────
if curl -s -o /dev/null --max-time 2 http://127.0.0.1:8077/api/health; then
  echo "backend  : already running on :8077"
else
  nohup bash "$HERE/backend/run.sh" > "$LOGS/backend.log" 2>&1 &
  echo "backend  : starting on :8077 (log: data/logs/backend.log)"
fi

# ── frontend ──────────────────────────────────────────────────────────────────
cd "$HERE/frontend"
if [ ! -d node_modules ]; then
  echo "frontend : installing dependencies (first run)…"
  npm install --no-audit --no-fund
fi
if curl -s -o /dev/null --max-time 2 http://127.0.0.1:3000/; then
  echo "frontend : already running on :3000"
else
  if [ "${1:-}" != "dev" ] && [ -d .next ] && [ -f .next/BUILD_ID ]; then
    nohup npm run start -- --port 3000 > "$LOGS/frontend.log" 2>&1 &
    echo "frontend : starting PRODUCTION build on :3000 (stable — recommended for demo)"
  else
    nohup npm run dev -- --port 3000 > "$LOGS/frontend.log" 2>&1 &
    echo "frontend : starting dev server on :3000 (run 'npm run build' once for the stable production mode)"
  fi
fi

# ── wait + verify ─────────────────────────────────────────────────────────────
echo -n "waiting for services"
for i in $(seq 1 30); do
  B=$(curl -s -o /dev/null -w '%{http_code}' --max-time 2 http://127.0.0.1:8077/api/health 2>/dev/null || true)
  F=$(curl -s -o /dev/null -w '%{http_code}' --max-time 2 http://127.0.0.1:3000/ 2>/dev/null || true)
  if [ "$B" = "200" ] && [ "$F" = "200" ]; then break; fi
  echo -n "."; sleep 2
done
echo ""
echo "backend  : HTTP ${B:-down}  http://127.0.0.1:8077/api/health"
echo "frontend : HTTP ${F:-down}  http://localhost:3000"
[ "$B" = "200" ] && [ "$F" = "200" ] && echo "THE EDITH is up → open http://localhost:3000" || echo "Something didn't start — check data/logs/*.log"
