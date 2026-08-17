#!/usr/bin/env bash
# THE EDITH — backend launcher. Claude Max subscription brain (no API key).
# SD-4 / ROB-02: portable python resolution — no hardcoded paths in ZIP submission.
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
ROUND2="$(cd "$HERE/../.." && pwd)"

# Resolve Python: $EDITH_PY override -> walk up from script for .venv -> system python3
if [ -n "${EDITH_PY:-}" ]; then
    PY="$EDITH_PY"
elif [ -x "$HERE/.venv/bin/python" ]; then
    PY="$HERE/.venv/bin/python"
elif [ -x "$HERE/../../.venv/bin/python" ]; then
    PY="$HERE/../../.venv/bin/python"
elif [ -x "$HERE/../../../.venv/bin/python" ]; then
    PY="$HERE/../../../.venv/bin/python"
elif [ -x "$HERE/../../../../.venv/bin/python" ]; then
    PY="$HERE/../../../../.venv/bin/python"
elif [ -x "$ROUND2/.venv/bin/python" ]; then
    PY="$ROUND2/.venv/bin/python"
elif [ -x "/home/ujjwal/Documents/J.A.R.V.I.S./.venv/bin/python" ]; then
    # known-machine fallback (Jarvis dev box)
    PY="/home/ujjwal/Documents/J.A.R.V.I.S./.venv/bin/python"
else
    PY="$(command -v python3 || true)"
    if [ -z "$PY" ]; then
        echo "ERROR: no python3 found. Set EDITH_PY=/path/to/python or create a .venv." >&2
        exit 1
    fi
fi

export VULCAN_DATASET_ROOT="$ROUND2/dataforge/datasets/steel-maintenance-flagship"
export VULCAN_LLM_MODE="cache_first"
export VULCAN_LLM_PROVIDER="${EDITH_LLM_PROVIDER:-subscription}"  # cache_first: baked Claude answers hit instantly; live Claude on miss; auto-falls to grounded template without a token
export VULCAN_MODEL_LIGHT="claude-haiku-4-5"     # fast path: diagnosis / plan
export VULCAN_MODEL_HEAVY="claude-sonnet-4-6"    # rich path: RCA / multi-turn
export VULCAN_CLAUDE_TIMEOUT_S="90"              # subprocess SDK is slow; allow completion
unset ANTHROPIC_API_KEY

# First-run artifact build: the submission ZIP ships the RAG index prebuilt but
# trains the ML models on first launch (keeps the package < 50 MB). Idempotent.
MODELS_DIR="$ROUND2/vulcan/data/models"
if [ ! -d "$MODELS_DIR" ] || [ -z "$(ls -A "$MODELS_DIR" 2>/dev/null | grep -E '\.pkl|\.txt' || true)" ]; then
    echo "[EDITH] First run: training ML models from the dataset (~2-3 min, one-time)…"
    ( cd "$ROUND2/vulcan" && "$PY" -m vulcan.ml.models ) || \
        echo "[EDITH] WARN: ML model build failed — diagnosis/RUL will use the grounded fallback. RAG + reports still work."
fi
# RAG index: rebuild only if the prebuilt vectordb is somehow absent.
if [ ! -d "$ROUND2/vulcan/data/vectordb" ] || [ -z "$(ls -A "$ROUND2/vulcan/data/vectordb" 2>/dev/null || true)" ]; then
    echo "[EDITH] Building RAG index from the knowledge base (~2 min, one-time)…"
    ( cd "$ROUND2/vulcan" && "$PY" -m vulcan.rag.store ) || \
        echo "[EDITH] WARN: RAG index build failed — check internet for the embedding model download."
fi

cd "$HERE"
exec "$PY" -m uvicorn main:app --host 127.0.0.1 --port 8077 "$@"
