# =============================================================================
# Maintenance Wizard — Makefile
# Tata Steel AI Hackathon 2026 · Round 2
#
# Targets:
#   make setup       — create venv + pip install -e .
#   make run-backend — start FastAPI server (port 8000)
#   make run-ui      — start Streamlit frontend (port 8501)
#   make run         — start both (backend in background)
#   make test        — run pytest
#   make gen-data    — generate synthetic dataset + KG
#   make train       — train ML models (WeibullAFT, LightGBM, IsolationForest)
#   make reset       — drop wizard.db + vector stores + re-init
#   make lint        — ruff + mypy
#   make check-secrets — grep for committed API keys (pre-submission)
# =============================================================================

PYTHON      := python3
VENV        := .venv
VENV_PYTHON := $(VENV)/bin/python
PIP         := $(VENV)/bin/pip
UVICORN     := $(VENV)/bin/uvicorn
STREAMLIT   := $(VENV)/bin/streamlit
PYTEST      := $(VENV)/bin/pytest
TORCH_INDEX := https://download.pytorch.org/whl/cpu

.PHONY: all setup install-torch run-backend run-ui run test gen-data train \
        reset lint check-secrets init-db help

help:
	@echo "Maintenance Wizard — available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	  awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'

# ─── Setup ───────────────────────────────────────────────────────────────────

setup: ## Create venv, install CPU torch, install package in editable mode
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip setuptools wheel
	$(PIP) install torch==2.3.1+cpu --index-url $(TORCH_INDEX)
	$(PIP) install -e ".[dev]"
	@echo ""
	@echo "Setup complete. Activate with:  source $(VENV)/bin/activate"
	@echo "Then run:  make gen-data && make train && make run"

install-torch: ## Install CPU-only PyTorch into existing venv
	$(PIP) install torch==2.3.1+cpu --index-url $(TORCH_INDEX)

# ─── Run ─────────────────────────────────────────────────────────────────────

init-db: ## Initialize wizard.db tables (idempotent)
	$(VENV_PYTHON) -c "from wizard.core.db import init_db; init_db()"
	@echo "Database initialized at data/wizard.db"

run-backend: init-db ## Start FastAPI backend on port 8000
	$(UVICORN) wizard.backend.main:app \
	  --host 127.0.0.1 \
	  --port 8000 \
	  --workers 1 \
	  --reload

run-ui: ## Start Streamlit frontend on port 8501
	$(STREAMLIT) run wizard/ui/app.py \
	  --server.port 8501 \
	  --server.headless true

run: init-db ## Start both backend (bg) + frontend (fg)
	@echo "Starting backend in background..."
	$(UVICORN) wizard.backend.main:app --host 127.0.0.1 --port 8000 --workers 1 &
	@sleep 2
	@echo "Starting Streamlit frontend..."
	$(STREAMLIT) run wizard/ui/app.py --server.port 8501 --server.headless true

# ─── Data + Training ─────────────────────────────────────────────────────────

gen-data: ## Generate synthetic KB (500 docs) + NASA/AI4I framing + KG ontology
	$(VENV_PYTHON) wizard/data/gen_synthetic.py
	$(VENV_PYTHON) wizard/data/gen_datasets.py
	$(VENV_PYTHON) wizard/knowledge/build_kg.py
	@echo "Data generation complete. Check data/synthetic/ and data/kg/"

train: ## Train all ML models offline (WeibullAFT, LightGBM, IsolationForest, LSTM-AE)
	$(VENV_PYTHON) wizard/ml/train_rul.py
	$(VENV_PYTHON) wizard/ml/train_failure.py
	$(VENV_PYTHON) wizard/ml/train_anomaly.py
	@echo "Models saved to data/models/"

ingest: ## Ingest synthetic KB into LanceDB (RAG)
	$(VENV_PYTHON) wizard/rag/ingest.py

# ─── Test ─────────────────────────────────────────────────────────────────────

test: ## Run pytest suite
	$(PYTEST) tests/ -v --tb=short --cov=wizard --cov-report=term-missing

test-smoke: ## Smoke-test core module compilation
	$(VENV_PYTHON) -m py_compile wizard/core/schemas.py
	$(VENV_PYTHON) -m py_compile wizard/core/config.py
	$(VENV_PYTHON) -m py_compile wizard/core/db.py
	@echo "All core modules compile clean"

# ─── Maintenance ─────────────────────────────────────────────────────────────

reset: ## Drop wizard.db + vector stores and re-init (DESTRUCTIVE)
	@echo "WARNING: This will delete all data. Ctrl-C to cancel."
	@sleep 3
	rm -f data/wizard.db data/sessions.db
	rm -rf data/lancedb data/chromadb
	$(VENV_PYTHON) -c "from wizard.core.db import init_db; init_db()"
	@echo "Reset complete. Run make gen-data to regenerate."

# ─── Code quality ─────────────────────────────────────────────────────────────

lint: ## Run ruff linter + mypy type checker
	$(VENV)/bin/ruff check wizard/ tests/
	$(VENV)/bin/mypy wizard/ --ignore-missing-imports

format: ## Auto-format with ruff
	$(VENV)/bin/ruff format wizard/ tests/

# ─── Pre-submission ───────────────────────────────────────────────────────────

check-secrets: ## Ensure no API keys are committed (pre-submission gate)
	@echo "Scanning for committed secrets..."
	@if grep -rE 'sk-ant|AIza[0-9A-Za-z\-_]{35}|sk-[a-zA-Z0-9]{48}' . \
	    --include="*.py" --include="*.toml" --include="*.json" \
	    --exclude-dir=".venv" --exclude-dir=".git" 2>/dev/null; then \
	    echo "ERROR: Secrets found! Remove before submission."; exit 1; \
	else \
	    echo "No secrets found."; \
	fi
