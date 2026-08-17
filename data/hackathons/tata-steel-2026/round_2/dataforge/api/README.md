---
title: DataForge API
emoji: 🏭
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
short_description: Dataset quality scoring for industrial / steel PdM data
---

# DataForge API

Backend scoring engine for industrial dataset quality auditing (EDITH · Tata Steel R2).
Deployed as a Docker Space; serves on port `7860`.

## Endpoints

```bash
# Health
curl https://<space>.hf.space/api/health

# Audit a dataset
curl -X POST https://<space>.hf.space/api/audit \
  -F "file=@your.csv" -F "label_col=failure"

# Public dataset board
curl https://<space>.hf.space/api/datasets
```

## Scoring

Composite = weighted mean of 10 dimensions with penalty caps + a domain-aware
PdM dimension (12 sensor types · 17 equipment classes · 200 fault→reading
signatures). Grades: Excellent ≥85 · Good ≥70 · Fair ≥55 · Needs Work ≥35 · Poor <35.

> Note: free Spaces have ephemeral storage — uploaded files on the public board
> reset when the Space restarts. Attach persistent storage or an external object
> store for durable uploads.

## Architecture

```
scorer/
  agent.py           ← decision graph + reasoning trace
  composite.py       ← weighted scoring + penalty caps
  readiness.py       ← LightGBM 3-fold CV → readiness %
  dimensions/        ← 10 base dims + domain_pdm (domain_knowledge.py)
```
