# AltBrief — Architecture Spec (Final)

**Project:** Alt-Data Investment Brief Agent
**Hackathon:** BrightData × lablab.ai "Web Data UNLOCKED" (May 25–31, 2026)
**Deadline:** May 31 ~12:29 PM IST

---

## Product Thesis (Verbatim Pitch)

> *"Bloomberg charges $24K/year and won't show its sources. We're free, conversational, and every signal links to the peer-reviewed paper behind it."*

User enters a stock ticker → agent fans out across **8 parallel data sources** (BrightData web scrapes + free finance APIs + optional satellite layer) → Claude Sonnet synthesizes into a **structured 1-page investment brief** with cited signals + confidence scoring → SSE-streamed to dashboard in ~30-45 seconds.

---

## What Makes This Win (Combined Findings from 15 Research Agents)

1. **White space confirmed** — Zero hackathon submissions in any indexable BrightData event have combined satellite + web alt-data + structured investment brief output. Top-right of 2×2 (novelty × technical depth) is uncrowded except for one academic paper.
2. **BrightData "depth" = 4 tool groups** — Use SERP + Web Unlocker + Scraping Browser + Datasets API. Single-tool usage = baseline. Four = standout.
3. **Cross-source contradiction detection** — Agent flags when LinkedIn hiring contradicts SEC guidance, or Reddit sentiment contradicts analyst consensus. This is the novelty anchor.
4. **3 peer-reviewed alpha signals foregrounded** — Insider Form 4 buys (Cohen-Malloy-Pomorski JoF 2012, 82bps/mo), Glassdoor rating Δ (Green et al JFE 2019), satellite parking (Berkeley study). Demoted signals (Reddit, Trends) in "interpret with caution" tab.
5. **Live overlay log during demo** — Highest single-ROI judge signal. Shows real BrightData tool calls executing.
6. **"$24K Bloomberg → $0 us" displacement frame** — Specific buyer + pricing tier + 2 displacement vectors.

---

## System Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│  FRONTEND (Next.js 15 + Tailwind 4 + shadcn)                         │
│  • Ticker input (mono-font terminal-style)                           │
│  • SSE stream consumer → live agent step ticker                      │
│  • Brief card (sell-side note layout)                                │
│  • Signal cards with citation chips                                  │
│  • Source overlay log (judge bait)                                   │
│  • Comparison table (Bloomberg/Quiver/AltBrief)                      │
└──────────────────┬───────────────────────────────────────────────────┘
                   │ SSE
                   ▼
┌──────────────────────────────────────────────────────────────────────┐
│  BACKEND (FastAPI + asyncio + Pydantic v2)                           │
│                                                                      │
│  GET /brief/stream/{ticker}                                          │
│         │                                                            │
│         ▼                                                            │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ ORCHESTRATOR — asyncio.gather(return_exceptions=True)       │    │
│  │ asyncio.as_completed_with_names() for streaming SSE events  │    │
│  └────┬──────────┬──────────┬──────────┬──────────┬───────────┘    │
│       │          │          │          │          │                 │
│       ▼          ▼          ▼          ▼          ▼                 │
│   sources/   sources/   sources/   sources/   sources/              │
│   sec.py     reddit.py  linkedin.py news.py   yahoo.py              │
│   (EDGAR)    (BD MCP)   (BD MCP)    (BD SERP) (yfinance)            │
│       │          │          │          │          │                 │
│       └──────────┴──────────┴──────────┴──────────┘                 │
│                              │                                      │
│                              ▼                                      │
│              ┌──────────────────────────────────┐                   │
│              │  SYNTHESIZER (synthesizer.py)    │                   │
│              │  Claude Sonnet 4.6 via tool-use  │                   │
│              │  Pydantic InvestmentBrief schema │                   │
│              │  Prompt caching (ephemeral)      │                   │
│              └──────────────────────────────────┘                   │
│                              │                                      │
│                              ▼                                      │
│              ┌──────────────────────────────────┐                   │
│              │  CONFIDENCE ROLLUP                │                   │
│              │  source quality weights           │                   │
│              │  coverage penalty                 │                   │
│              └──────────────────────────────────┘                   │
└──────────────────────────────────────────────────────────────────────┘
        │                                                  │
        ▼                                                  ▼
  ┌──────────────┐                              ┌────────────────┐
  │ FILE CACHE   │                              │ COST TRACKER   │
  │ .cache/*.json│                              │ data/cost.json │
  │ 1h TTL       │                              │ $5/day cap     │
  └──────────────┘                              └────────────────┘
```

---

## Data Source Stack (Final 8 Sources)

| # | Source | Tool | Cost | Reliability | Signal Quality |
|---|---|---|---|---|---|
| 1 | **SEC EDGAR** (Form 4 + 10-K) | direct REST | $0 | High | **GOLD** — peer-reviewed |
| 2 | **Yahoo Finance** | yfinance | $0 | Medium (fallback Tiingo) | High |
| 3 | **News (Reuters + general)** | BrightData SERP API | $0.0015/req | High | High |
| 4 | **Reddit WSB/stocks/investing** | BrightData Scraping Browser | $8/GB | High | Medium (decayed) |
| 5 | **LinkedIn hiring trends** | BrightData LinkedIn scraper | $1.50/1K | High | Medium |
| 6 | **Glassdoor reviews** | BrightData Scraping Browser | $1.50/1K | High | **GOLD** — peer-reviewed |
| 7 | **GDELT news tone** | gdeltdoc | $0 | High | Medium |
| 8 | **Satellite/FIRMS (optional V2)** | NASA FIRMS + Claude Vision | $0 + Vision tokens | Medium | Novel for demo wow |

**Free finance API stack (always-on, no BrightData budget burn):** SEC EDGAR, yfinance, FRED, Finnhub, GDELT, Wikipedia.

**BrightData tool groups:** `social,finance,business,research` (~30 tools — token-optimal).

---

## Brief Schema (Pydantic v2)

```python
class Signal(BaseModel):
    source: str
    direction: Literal["bullish", "bearish", "neutral"]
    summary: str = Field(max_length=200)
    confidence: float = Field(ge=0.0, le=1.0)
    raw_evidence: str = Field(max_length=500)
    citation_url: str | None = None

class InvestmentBrief(BaseModel):
    ticker: str
    company_name: str
    sector: str
    generated_at: datetime
    signals: list[Signal]
    risk_factors: list[str]
    bull_thesis: list[str]  # 3-4 bullets
    bear_case: list[str]    # 3-4 bullets
    overall_direction: Literal["bullish", "bearish", "neutral"]
    overall_confidence: float
    price_target_range: dict | None  # {"low": X, "base": Y, "high": Z}
    brief_narrative: str
    data_quality_flag: Literal["full", "partial", "minimal"]
    sources_used: list[str]
    sources_unavailable: list[str]
    cross_source_contradictions: list[str]  # NOVELTY ANCHOR
    latency_seconds: float
    cost_usd: float
```

---

## Backend Stack

- **Runtime:** Python 3.12 + uvicorn (FastAPI ASGI)
- **Async:** asyncio.gather + as_completed (no LangGraph for V1)
- **LLM:** Claude Sonnet 4.6 via Anthropic SDK + tool-use
- **Data:** BrightData MCP via `@brightdata/mcp` (npx subprocess) + direct REST clients
- **Schemas:** Pydantic v2
- **Caching:** File-based JSON (`.cache/{source}_{ticker}.json`, 1h TTL)
- **Observability:** structlog → Langfuse OTel (free cloud)
- **Cost tracking:** File ledger `data/cost.json`, $5/day cap

## Frontend Stack

- **Framework:** Next.js 15 (App Router) + React 19
- **Styling:** Tailwind 4 + shadcn/ui v4
- **Streaming:** EventSource API for SSE
- **State:** TanStack Query for cached briefs
- **Motion:** Framer Motion (subtle — token streaming, card mount)
- **Charts:** Recharts (sparklines in signal cards)

## Deployment

- **Backend:** Fly.io (`auto_stop_machines = false` — critical for demo)
- **Frontend:** Vercel (free hobby tier)
- **Observability:** Langfuse cloud (free tier)
- **Repo:** GitHub MIT licensed

---

## Demo Tickers (Pre-cached)

| Ticker | Why | Killer Signal |
|---|---|---|
| **NVDA** | Tech everyone knows | LinkedIn engineering hiring + Reddit sentiment |
| **XOM** | Energy + satellite | NASA FIRMS flaring at Baytown refinery |
| **WMT** | Retail + foot-traffic proxy | Glassdoor employee sentiment + LinkedIn hiring |

Pre-cache all three so demo is instant. Live URL never cold-starts.

---

## Critical Build Decisions (Locked)

1. **No LangGraph for V1** — pure asyncio simpler, 5-day build
2. **Hardcode source list** — no Claude orchestration round-trip
3. **Tool-use synthesis, not JSON mode** — guaranteed schema compliance
4. **Prompt caching ephemeral** — saves $0.006/req
5. **File cache, not Redis** — zero infra
6. **Fly.io backend always-on** — no cold start during pitch
7. **Pre-cache demo tickers** — judges see instant response

---

## Risk Mitigations

| Risk | Mitigation |
|---|---|
| BrightData rate limit during demo | File cache + pre-cache demo tickers + degraded-mode brief |
| yfinance breaks mid-build | Tiingo fallback wired from day 1 |
| Claude Vision satellite costs spike | Cap to 1 ticker (XOM) + cache forever for demo AOIs |
| Fly.io cold start kills demo | `auto_stop_machines = false` + min_machines = 1 |
| Vercel cold start on judge click | Pre-warm before pitch + GIF backup on Slide 5 |
| Live URL 404 at judging | Submit Day 3, update through Day 5 |

---

## Build Plan (Hours, not days)

**T+0 to T+2h: Backend core**
- schemas.py + cache.py + cost_tracker.py
- sources/sec.py (EDGAR — most reliable, build first)
- sources/yahoo.py (yfinance)
- orchestrator.py with safe_scrape pattern
- main.py FastAPI + SSE endpoint

**T+2h to T+4h: BrightData sources**
- sources/brightdata_client.py (MCP wrapper)
- sources/reddit.py + linkedin.py + news.py + glassdoor.py

**T+4h to T+5h: Synthesizer**
- synthesizer.py with Claude tool-use
- confidence.py weighted rollup
- prompts/synthesis_system.txt with NVDA few-shot

**T+5h to T+8h: Frontend**
- Next.js scaffold with ticker input
- SSE consumer hook
- Brief card + signal cards
- Source overlay log
- 2026 dark fintech palette

**T+8h to T+10h: Deploy**
- Dockerfile + fly.toml
- Vercel deploy frontend
- .env.example
- Pre-warm cache for NVDA + XOM + WMT

**T+10h to T+12h: Polish**
- README with 1-cmd launch
- Architecture diagram PNG
- Lablab form copy + Gamma pitch deck

**T+12h+: Demo video record**

---

## File Tree

```
altbrief/
├── README.md
├── ARCHITECTURE.md
├── pyproject.toml
├── requirements.txt
├── Dockerfile
├── fly.toml
├── .env.example
├── .gitignore
├── LICENSE                   # MIT
├── assets/
│   ├── demo.gif
│   ├── architecture.png
│   └── thumbnail.png
├── backend/
│   ├── main.py               # FastAPI + SSE
│   ├── orchestrator.py       # asyncio fan-out
│   ├── synthesizer.py        # Claude tool-use synthesis
│   ├── schemas.py            # Pydantic v2 models
│   ├── confidence.py         # weighted rollup
│   ├── cache.py              # file-based TTL
│   ├── cost_tracker.py       # $/day cap
│   ├── observability.py      # structlog + Langfuse
│   ├── sources/
│   │   ├── __init__.py
│   │   ├── sec.py            # EDGAR REST direct
│   │   ├── yahoo.py          # yfinance
│   │   ├── fred.py           # macro context
│   │   ├── gdelt.py          # news tone
│   │   ├── brightdata.py     # MCP wrapper
│   │   ├── reddit.py         # via BrightData
│   │   ├── linkedin.py       # via BrightData
│   │   ├── glassdoor.py      # via BrightData
│   │   ├── news.py           # BrightData SERP + Reuters
│   │   └── satellite.py      # NASA FIRMS + Claude Vision (V2)
│   └── prompts/
│       └── synthesis_system.txt
├── frontend/
│   ├── package.json
│   ├── next.config.mjs
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx          # Hero + ticker input
│   │   ├── brief/[ticker]/page.tsx
│   │   └── globals.css
│   ├── components/
│   │   ├── TickerInput.tsx
│   │   ├── BriefCard.tsx
│   │   ├── SignalCard.tsx
│   │   ├── SourceOverlay.tsx # judge bait
│   │   ├── AgentStepTicker.tsx
│   │   └── ui/               # shadcn primitives
│   └── lib/
│       ├── sse.ts            # EventSource hook
│       └── types.ts
├── data/
│   ├── evals/
│   │   ├── golden_set.yaml
│   │   └── mocks/
│   └── cache/                # gitignored
└── tests/
    ├── test_orchestrator.py
    ├── test_synthesizer.py
    └── test_confidence.py
```
