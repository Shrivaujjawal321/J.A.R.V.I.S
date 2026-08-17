#!/usr/bin/env bash
# scripts/run_demo_capture.sh
# ============================
# Full demo capture pipeline:
#   1. Init DB
#   2. Start backend on :8000 (background)
#   3. Wait for health
#   4. Run capture script → saves data/demo/demo_cache.json
#   5. Kill backend
#
# Usage: bash scripts/run_demo_capture.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

PYTHON=".venv/bin/python"
UVICORN=".venv/bin/uvicorn"
PORT=8000
BASE_URL="http://127.0.0.1:${PORT}"
LOG="data/demo/backend_capture.log"
DEMO_DIR="data/demo"

mkdir -p "$DEMO_DIR"

echo "=== Maintenance Wizard — Demo Capture Pipeline ==="
echo "Repo root: $REPO_ROOT"
echo "Backend port: $PORT"
echo ""

# Step 1: Init DB
echo "[1/4] Initializing database..."
$PYTHON -c "
import os; os.chdir('$REPO_ROOT')
from wizard.core.db import init_db
init_db()
print('  DB initialized at data/wizard.db')
"

# Step 2: Start backend in background
echo "[2/4] Starting backend on :${PORT}..."
BACKEND_PORT=$PORT $UVICORN wizard.backend.app:app \
  --host 127.0.0.1 --port $PORT --workers 1 \
  > "$LOG" 2>&1 &
BACKEND_PID=$!
echo "  Backend PID: $BACKEND_PID"

# Cleanup on exit
cleanup() {
  echo ""
  echo "[cleanup] Killing backend PID $BACKEND_PID..."
  kill "$BACKEND_PID" 2>/dev/null || true
}
trap cleanup EXIT

# Step 3: Wait for health
echo "[3/4] Waiting for backend health..."
MAX_WAIT=60
WAITED=0
until curl -sf "${BASE_URL}/v1/health" > /dev/null 2>&1; do
  sleep 2
  WAITED=$((WAITED + 2))
  if [ $WAITED -ge $MAX_WAIT ]; then
    echo "ERROR: Backend did not come up in ${MAX_WAIT}s."
    echo "Last log lines:"
    tail -20 "$LOG"
    exit 1
  fi
  echo "  Waited ${WAITED}s..."
done
echo "  Backend healthy."

# Step 4: Run capture
echo "[4/4] Running demo cache capture..."
$PYTHON scripts/capture_demo_cache.py

echo ""
echo "=== Done ==="
echo "Demo cache: $REPO_ROOT/data/demo/demo_cache.json"
echo "Backend log: $REPO_ROOT/$LOG"
