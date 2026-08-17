# DataForge API — Hugging Face Spaces (Docker SDK) image
# Runs the FastAPI dataset-quality scorer on the HF-default port 7860.
FROM python:3.12-slim

# libgomp1 is required by LightGBM at runtime.
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# HF Spaces convention: run as a non-root uid 1000 user named "user".
RUN useradd -m -u 1000 user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PORT=7860 \
    # No `claude` CLI on HF → subscription LLM review can't run; use the
    # deterministic template (fast, reliable). Flip to "subscription" only
    # in an environment that has the Claude CLI + OAuth token.
    EDITH_LLM_REVIEW=off

# Create the app dir + writable upload store and hand it to `user`
# (WORKDIR auto-creates as root, hence the explicit chown before USER).
RUN mkdir -p /home/user/app/data/files && chown -R user:user /home/user/app
WORKDIR /home/user/app
USER user

# Install deps first for layer caching.
COPY --chown=user:user requirements.txt ./
RUN pip install --no-cache-dir --user -r requirements.txt

# App code (data/, __pycache__ excluded via .dockerignore).
COPY --chown=user:user . .

EXPOSE 7860
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
