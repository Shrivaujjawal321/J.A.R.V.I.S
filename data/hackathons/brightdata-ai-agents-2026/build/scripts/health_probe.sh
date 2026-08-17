#!/usr/bin/env bash
# =============================================================================
# scripts/health_probe.sh
# =======================
# Probe the backend /health endpoint every 10s for 60s.
# Use this 5 minutes before demo recording to confirm Fly.io machine is warm
# and not returning 5xx errors.
#
# Usage:
#   ./scripts/health_probe.sh                       # probes localhost:8000
#   BACKEND_URL=https://altbrief-api.fly.dev ./scripts/health_probe.sh
#   make health-probe
#
# Exit codes:
#   0 — all probes returned HTTP 200
#   1 — one or more probes returned 5xx or connection refused
# =============================================================================

set -euo pipefail

BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"
HEALTH_URL="${BACKEND_URL}/health"
INTERVAL_S=10
DURATION_S=60
MAX_PROBES=$(( DURATION_S / INTERVAL_S ))

echo "AltBrief Health Probe"
echo "URL:      ${HEALTH_URL}"
echo "Interval: ${INTERVAL_S}s"
echo "Duration: ${DURATION_S}s (${MAX_PROBES} probes)"
echo "========================================"

FAIL_COUNT=0
PROBE_NUM=0

while [ "$PROBE_NUM" -lt "$MAX_PROBES" ]; do
    PROBE_NUM=$(( PROBE_NUM + 1 ))
    TIMESTAMP=$(date -u +"%H:%M:%S")

    # curl flags:
    #   -s           silent (no progress)
    #   -o /dev/null discard body
    #   -w "%{http_code}" write HTTP status code to stdout
    #   --max-time 5 abort if backend takes >5s (it should respond in <1s)
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
        --max-time 5 \
        "${HEALTH_URL}" 2>/dev/null || echo "000")

    if [ "$HTTP_CODE" = "200" ]; then
        echo "[${TIMESTAMP}] Probe ${PROBE_NUM}/${MAX_PROBES}: HTTP ${HTTP_CODE} OK"
    else
        echo "[${TIMESTAMP}] Probe ${PROBE_NUM}/${MAX_PROBES}: HTTP ${HTTP_CODE} FAIL"
        FAIL_COUNT=$(( FAIL_COUNT + 1 ))
    fi

    # Don't sleep after the last probe
    if [ "$PROBE_NUM" -lt "$MAX_PROBES" ]; then
        sleep "${INTERVAL_S}"
    fi
done

echo "========================================"
if [ "$FAIL_COUNT" -eq 0 ]; then
    echo "All ${MAX_PROBES} probes passed. Backend is warm and healthy."
    echo "Safe to start demo recording."
    exit 0
else
    echo "FAIL: ${FAIL_COUNT}/${MAX_PROBES} probes returned non-200."
    echo "Check Fly.io logs: fly logs --app altbrief-api"
    exit 1
fi
