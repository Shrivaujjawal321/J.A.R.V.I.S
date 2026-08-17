# =============================================================================
# AltBrief — Makefile
# Usage: make <target>
# Requires: fly CLI, vercel CLI, python 3.12, node 20, npm
# =============================================================================

.PHONY: help dev dev-backend dev-frontend deploy-backend deploy-frontend \
        prewarm health-probe test test-backend test-frontend lint \
        docker-build docker-run clean

# Default target: show help
help:
	@echo "AltBrief — Available targets:"
	@echo ""
	@echo "  make dev              Start backend + frontend concurrently (requires concurrently)"
	@echo "  make dev-backend      Start FastAPI backend only (uvicorn --reload)"
	@echo "  make dev-frontend     Start Next.js frontend only (npm run dev)"
	@echo ""
	@echo "  make docker-build     Build Docker image locally (smoke test)"
	@echo "  make docker-run       Run Docker image locally (port 8000)"
	@echo ""
	@echo "  make deploy-backend   Deploy to Fly.io (requires: fly auth login)"
	@echo "  make deploy-frontend  Deploy to Vercel (requires: vercel link)"
	@echo ""
	@echo "  make prewarm          Pre-warm NVDA + XOM + WMT cache post-deploy"
	@echo "  make health-probe     Probe /health every 10s for 60s (pre-recording)"
	@echo ""
	@echo "  make test             Run all tests (backend pytest + frontend typecheck)"
	@echo "  make test-backend     pytest only"
	@echo "  make test-frontend    TypeScript + ESLint only"
	@echo ""
	@echo "  make clean            Remove __pycache__, .cache, .next build artefacts"

# ---------------------------------------------------------------------------
# Dev
# ---------------------------------------------------------------------------

dev-backend:
	@echo "Starting FastAPI backend on :8000..."
	. .venv/bin/activate && uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	@echo "Starting Next.js frontend on :3000..."
	cd frontend && npm run dev

# Concurrent start — requires 'concurrently' (npm install -g concurrently)
# Or install via: pip install honcho  and rename to Procfile
dev:
	@which concurrently > /dev/null 2>&1 || (echo "Install concurrently: npm install -g concurrently" && exit 1)
	concurrently \
		--names "backend,frontend" \
		--prefix-colors "blue,green" \
		"make dev-backend" \
		"make dev-frontend"

# ---------------------------------------------------------------------------
# Docker
# ---------------------------------------------------------------------------

docker-build:
	@echo "Building Docker image altbrief:test..."
	docker build -t altbrief:test .
	@echo "Build complete. Run: make docker-run"

docker-run:
	@echo "Running altbrief:test on :8000..."
	docker run --rm -p 8000:8000 \
		--env-file .env \
		altbrief:test

# ---------------------------------------------------------------------------
# Deploy
# ---------------------------------------------------------------------------

deploy-backend:
	@echo "Deploying backend to Fly.io..."
	@echo "Make sure you have run: fly auth login"
	@echo "Make sure secrets are set: fly secrets set ANTHROPIC_API_KEY=... BRIGHTDATA_API_TOKEN=..."
	fly deploy --app altbrief-api --config fly.toml
	@echo ""
	@echo "Deploy complete. Verifying health..."
	@sleep 10
	@BACKEND_URL=https://altbrief-api.fly.dev $(MAKE) health-probe || true

deploy-frontend:
	@echo "Deploying frontend to Vercel..."
	@echo "Make sure you have run: vercel link (from frontend/ dir)"
	@echo "Make sure NEXT_PUBLIC_API_URL is set in Vercel dashboard."
	cd frontend && vercel --prod

# ---------------------------------------------------------------------------
# Pre-warm + health probe
# ---------------------------------------------------------------------------

prewarm:
	@echo "Pre-warming demo tickers (NVDA, XOM, WMT)..."
	. .venv/bin/activate && python scripts/prewarm.py

prewarm-prod:
	@echo "Pre-warming against production..."
	. .venv/bin/activate && BACKEND_URL=https://altbrief-api.fly.dev python scripts/prewarm.py

health-probe:
	@chmod +x scripts/health_probe.sh
	./scripts/health_probe.sh

health-probe-prod:
	BACKEND_URL=https://altbrief-api.fly.dev ./scripts/health_probe.sh

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

test: test-backend test-frontend

test-backend:
	@echo "Running backend tests..."
	. .venv/bin/activate && python -m pytest tests/ -v --tb=short

test-frontend:
	@echo "Running frontend type check + lint..."
	cd frontend && npm run typecheck && npm run lint

# ---------------------------------------------------------------------------
# Clean
# ---------------------------------------------------------------------------

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .pytest_cache .ruff_cache .mypy_cache
	rm -rf frontend/.next frontend/node_modules
	@echo "Clean complete."
