# AltBrief — Alt-Data Investment Brief Agent

> Bloomberg charges $24K/year and won't show its sources. AltBrief is free, conversational, and every signal links to the peer-reviewed paper behind it. Enter any stock ticker — get an institutional-grade investment brief in 45 seconds, pulled from 8 parallel live data streams via BrightData.

**Hackathon:** BrightData x lablab.ai "Web Data UNLOCKED" — May 2026

---

## Live Demo

**Demo URL:** `https://altbrief.vercel.app` ← _fill before submission_

**Video:** [YouTube link] ← _fill before submission_

---

## Architecture

![Architecture Diagram](assets/architecture.png)

```
Browser (Next.js 15)
    │
    │  SSE — direct to Fly.io (bypasses Vercel; avoids 10s timeout)
    ▼
FastAPI (Fly.io — always-on, HTTP/2, IAD region)
    │
    ├── asyncio.gather ──► SEC EDGAR (Form 4 + 10-K)
    │                  ──► Yahoo Finance / Tiingo
    │                  ──► BrightData SERP API (news headlines)
    │                  ──► BrightData Scraping Browser (Reddit WSB)
    │                  ──► BrightData LinkedIn scraper (hiring trends)
    │                  ──► BrightData Scraping Browser (Glassdoor)
    │                  ──► GDELT news tone (free)
    │                  ──► NASA FIRMS satellite / flare (XOM demo)
    │
    └── Claude Sonnet 4.6 synthesis (tool-use → InvestmentBrief schema)
```

---

## Quick Start (1 command)

```bash
git clone https://github.com/YOUR_USERNAME/altbrief
cd altbrief
cp .env.example .env          # fill ANTHROPIC_API_KEY + BRIGHTDATA_API_TOKEN
docker compose up
```

Frontend: `http://localhost:3000`  
Backend API: `http://localhost:8000`  
Health: `http://localhost:8000/health`

---

## Local Development (without Docker)

**Backend:**
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # fill keys
uvicorn backend.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
cp .env.local.example .env.local   # set NEXT_PUBLIC_API_URL=http://localhost:8000
npm install
npm run dev
```

---

## Tech Stack

Python 3.12 + FastAPI + asyncio · Claude Sonnet 4.6 (Anthropic SDK) · BrightData MCP (`@brightdata/mcp` via npx) · Next.js 15 (App Router) + React 19 · Tailwind 4 + shadcn/ui · TanStack Query · `@microsoft/fetch-event-source` · Fly.io + Vercel · Langfuse observability

---

## BrightData Tool Groups Used

| Group | Purpose | Endpoint |
|---|---|---|
| **SERP API** | Real-time news headlines (Reuters + financial press) | `sources/news.py` |
| **Scraping Browser** | Reddit WSB sentiment (JS-heavy, block-resistant) | `sources/reddit.py` |
| **Scraping Browser** | Glassdoor reviews + employee sentiment | `sources/glassdoor.py` |
| **LinkedIn Dataset API** | Hiring velocity — headcount + role trends | `sources/linkedin.py` |

Four tool groups = depth signal. Each is called live during the demo.

---

## Eval Results

See `data/evals/` for golden test set + per-source accuracy benchmarks.

_Eval baseline published post-build: fill from `data/evals/baseline.md`_

---

## Pricing Comparison

| Source | Time to Brief | Annual Cost |
|---|---|---|
| Bloomberg Terminal | 5-10 min (manual) | $27,000 |
| Refinitiv / LSEG brief | 1-2 days | ~$2,000/brief |
| Alt-data broker bundle | Manual synthesis | $50,000+ |
| **AltBrief** | **45 seconds** | **$0.03/run** |

---

## Research Signals (Peer-Reviewed)

| Signal | Source | Academic Backing |
|---|---|---|
| Insider Form 4 buys | SEC EDGAR | Cohen-Malloy-Pomorski, JoF 2012 (82bps/mo alpha) |
| Glassdoor rating change | BrightData | Green et al., JFE 2019 |
| Satellite parking density | NASA FIRMS | Berkeley Haas parking study |

---

## License

MIT — see [LICENSE](LICENSE)

---

_Built for BrightData x lablab.ai "Web Data UNLOCKED" hackathon, May 2026_
