# =============================================================================
# AltBrief API — Dockerfile
# Base: python:3.12-slim + Node 20 (for npx @brightdata/mcp subprocess)
# Strategy: single stage (cold-start not a concern — Fly keeps machine warm)
# Non-root user: altbrief (uid 1001)
# =============================================================================

FROM python:3.12-slim AS base

# ---- System deps + Node 20 ----
# Node required: BrightData MCP runs via `npx @brightdata/mcp` subprocess
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
        ca-certificates \
        gnupg \
        # needed by some Python packages (pydantic-core / aiohttp)
        gcc \
        libffi-dev \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && npm install -g npm@latest \
    # pre-pull brightdata MCP so npx doesn't cold-download on first request
    && npx --yes @brightdata/mcp --version || true \
    && apt-get purge -y --auto-remove gcc libffi-dev gnupg curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ---- Non-root user ----
RUN groupadd --gid 1001 altbrief \
    && useradd --uid 1001 --gid altbrief --no-create-home --shell /bin/false altbrief

# ---- App directories ----
WORKDIR /app
RUN mkdir -p /app/.cache /app/data && chown -R altbrief:altbrief /app

# ---- Python dependencies ----
# Copy requirements first for Docker layer cache (only invalidates on dep change)
COPY --chown=altbrief:altbrief requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ---- Application source ----
COPY --chown=altbrief:altbrief backend/ ./backend/
COPY --chown=altbrief:altbrief data/ ./data/

# ---- Switch to non-root ----
USER altbrief

# ---- Runtime config ----
# Internal port uvicorn listens on (must match fly.toml internal_port)
ENV PORT=8000 \
    # Production logging: JSON lines to stdout
    LOG_JSON=1 \
    LOG_LEVEL=INFO \
    # Python: don't buffer stdout (critical for structured log delivery)
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    # Cache dir writable by non-root user
    CACHE_DIR=/app/.cache \
    DATA_DIR=/app/data

EXPOSE 8000

# ---- Healthcheck ----
# Fly.io uses this; also useful for docker-compose depends_on health checks.
# 30s interval, 5s timeout, 3s start period (let uvicorn boot), 3 retries
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# ---- Entrypoint ----
# uvicorn with 1 worker (Fly scales via machines, not workers)
# --no-access-log: structlog handles structured access logging
CMD ["python", "-m", "uvicorn", "backend.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "1", \
     "--no-access-log"]
