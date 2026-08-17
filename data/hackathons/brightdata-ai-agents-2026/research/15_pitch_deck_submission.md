# Pitch Deck + Submission Package Strategy

## Style Decision: YC-minimal, 11 slides, dark mode

BCG/McKinsey style (dense data tables) = "consultant built this." YC-minimal = "founder who knows what they're building." Dark background reads better on screen + video.

**Slide count:** 11. Ten is floor, twelve is ceiling before skimming.

---

## Slide-by-Slide Spec

### Slide 1 — Title / Cover

```
AltBrief

Live web intelligence → institutional-grade investment briefs, in seconds.

Ujjawal Shrivastava
BrightData × lablab.ai — Web Data UNLOCKED Hackathon 2026

[lablab.ai logo]    [BrightData logo]
GitHub: ... | Live Demo: ...
```

### Slide 2 — Problem

Visual: 60% text, 40% two-panel comparison (Bloomberg terminal rich vs empty CSV).

```
LLMs are blind to what just happened.

Training cutoff: months or years ago.
Bloomberg Terminal: $25,000/year.
Quiver Quantitative: $30-75/month — raw tables, no synthesis.

94% of fund managers increasing AI spending in 2026.
0% of that budget reaches the indie researcher or solo fund analyst.

The insight gap is not intelligence. It's data access.
```

### Slide 3 — Solution

Left: one-sentence solution. Right: real screenshot/GIF of agent producing brief.

```
AltBrief is an AI agent that scrapes live public web data
via BrightData, then synthesizes it into a structured
investment brief — the kind a hedge fund analyst would write.

Any ticker. Any sector. Real-time. Free to run.
```

### Slide 4 — Architecture Diagram

```
[User: Ticker Input]
        ↓
[Orchestrator Agent — LangGraph]
        ↓ (parallel tool calls)
┌─────────────────────────────────────────────────┐
│  BrightData SERP API        → News, analyst sentiment  │
│  BrightData Web Unlocker    → SEC filings, transcripts │
│  BrightData Scraping Browser → Reddit, StockTwits      │
│  Free APIs (Polygon, Yahoo) → Price, volume, fundamentals │
└─────────────────────────────────────────────────┘
        ↓
[Data Normalization + Dedup]
        ↓
[LLM Synthesis — Claude Sonnet]
        ↓
[Structured Output: Investment Brief JSON/PDF]
```

**Caption:** "4 data sources → 1 synthesized brief. Total wall-clock time: < 45 seconds."

### Slide 5 — Live Demo

Full-bleed. Embedded GIF + large QR code linking to live URL.

```
This output was generated live — not pre-scripted.

Ticker: NVDA
Sources pulled: 12 live web pages via BrightData
Brief generated: 47 seconds

[QR code → live URL]
```

### Slide 6 — Data Sources Matrix

| Data Type | Source | BrightData Product |
|---|---|---|
| News & Press Releases | Google News, Reuters | SERP API |
| SEC Filings (10-K, 8-K) | SEC EDGAR | Web Unlocker API |
| Social Sentiment | Reddit WSB, StockTwits | Scraping Browser |
| Analyst Reports | Seeking Alpha | Web Unlocker API |
| Earnings Transcripts | Motley Fool | Web Unlocker API |
| Price / Volume | Yahoo Finance, Polygon | Free API (direct) |

**Caption:** "BrightData handles anti-bot, geo-blocks, JS rendering — we focus on analysis."

### Slide 7 — Differentiation

| | Bloomberg | Quiver Quant | Yipit | **AltBrief** |
|---|---|---|---|---|
| Real-time web scraping | Partial | No | Enterprise | **Yes** |
| LLM synthesis | No | No | No | **Yes** |
| Open / free tier | No | Partial | No | **Yes** |
| Setup time | Weeks | Minutes | Weeks | **< 5 min** |
| Cost | $25K/yr | $30-75/mo | $15K+/yr | **Free** |

```
Bloomberg gives you data. Quiver gives you tables.
AltBrief gives you the brief.

The synthesis layer is the moat.
```

### Slide 8 — Why BrightData (Sponsor Integration)

3 feature cards with BrightData branding:

**Card 1 — Web Unlocker API**
Our agent hits SEC EDGAR, Seeking Alpha, earnings transcript pages that block standard scrapers. Web Unlocker handles JS rendering + CAPTCHA invisibly — zero infrastructure on our end.

**Card 2 — SERP API**
Real-time news aggregation across Google News per ticker. Markdown output format feeds directly into our LLM prompt — no HTML parsing.

**Card 3 — Scraping Browser**
Reddit WSB + StockTwits require browser-level rendering. Scraping Browser gives us authenticated-looking sessions without maintaining accounts.

**Bottom line:** "We called 3 BrightData products in a single agent workflow. Total cost per brief: < $0.05 in BrightData credits."

### Slide 9 — Tech Stack

```
Data Layer:    BrightData  |  Polygon.io  |  Yahoo Finance
Agent Layer:   asyncio + Pydantic v2  |  Python 3.12
LLM Layer:     Claude Sonnet 4.6 (Anthropic)
Output Layer:  FastAPI  |  Next.js 15  |  JSON/PDF
Dev:           GitHub   |  Docker  |  Fly.io
```

**Caption:** "Open source. Deployable in one command. MIT licensed."

### Slide 10 — Market Sizing

```
TAM: Global alt-data market — $5.2B in 2026 (FMI), 34% CAGR
     (Hedgeweek: 94% of fund managers increasing AI spend)

SAM: Independent fund managers, solo analysts, retail quants
     who cannot afford Bloomberg or Yipit
     ESTIMATED: 200K+ globally

SOM: 1% capture = 2,000 users × $20/mo = $480K ARR Year 1
     (currently free/OSS — this is the freemium conversion path)
```

**Caption:** "Insight gap between institutional and indie investors is worth billions. We're the API layer for the other 99%."

### Slide 11 — Roadmap + Ask (Startup Program Slide)

**Left: What we built in 72 hours**
- Real-time alt-data scraping via 3 BrightData products
- LLM synthesis into structured investment brief
- Working API + UI deployed to Vercel
- Open source, MIT licensed

**Right: With $20K BrightData credits + 6 months**
```
Month 1-2:  Multi-ticker portfolio scanner
            (50 tickers overnight, surface top signals)

Month 3-4:  Sector-level trend reports
            (weekly AI briefings, email delivery)

Month 5-6:  Backtesting integration
            (did the brief signal work? close feedback loop)

$20K BrightData credits = 400K+ brief generations/month
at current cost-per-call = full private beta of 1,000 users.
```

**Close:**
```
AltBrief started as a hackathon project.
The infrastructure for what comes next is already running.

GitHub: [link]      Demo: [link]      Contact: shriva.ujjawal@gmail.com
```

---

## Visual Style

**Palette:**
| Element | Hex |
|---|---|
| Background | `#0D0D0D` |
| Primary text | `#F0F0F0` |
| Accent 1 (BrightData) | `#FF6B35` |
| Accent 2 (fintech) | `#00D4AA` |
| Secondary text | `#9CA3AF` |
| Card backgrounds | `#1A1A2E` |

**Typography:**
- Headline: Inter Bold or Geist
- Body: Inter Regular or Space Grotesk
- Code: JetBrains Mono
- Min: 24pt body, 40pt+ headlines (YC rule)

**Illustration vs photo:** Screenshots + architecture diagrams. Never stock photography. Build architecture in Excalidraw — reads "engineer made this."

---

## Tool: Gamma.app

1. 30-60 sec AI generation from prompt
2. Built-in dark mode templates
3. GIF embed native
4. Shareable link = pitch URL in lablab form
5. PDF export backup
6. Free tier sufficient

**Workflow:** Paste slide-by-slide spec into Gamma AI prompt → accept structure → swap copy → add screenshots/GIFs → apply dark palette. 3-4 hours.

Skip Pitch.com (collaboration friction). Skip Tome (learning curve). Skip Slidesgo (template-tier).

---

## lablab.ai Form Copy

### Title (50 char max)
1. `AltBrief: Live Web Data Investment Briefs` — 41 ⭐
2. `Alt-Data Investment Brief Agent (BrightData)` — 45
3. `Real-Time Alt-Data Investment Brief Agent` — 41

**Pick: Option 1.** Memorable, searchable, avoids "agent" word every other submission will have.

### Short Description (255 char max)

```
AI agent that scrapes live public web data via BrightData (SERP API, Web Unlocker, Scraping Browser) and synthesizes it into structured investment briefs — in <45 seconds. Any ticker. Real-time. Open source.
```

(~208 chars)

### Long Description (100w min)

```
Most investors — from solo analysts to small hedge funds — rely on data that is either months old (LLM training cutoffs) or locked behind $25,000/year Bloomberg subscriptions. AltBrief closes that gap.

The agent takes a stock ticker as input, then triggers parallel data collection across three BrightData products: SERP API for real-time news and analyst headlines, Web Unlocker for SEC filings and earnings transcripts, and Scraping Browser for Reddit and StockTwits social sentiment. All sources are normalized, deduplicated, and fed to an LLM that synthesizes them into a structured investment brief — the kind a professional analyst would write.

Total time from ticker to brief: under 45 seconds. Total infrastructure cost: under $0.05 per brief.

AltBrief is open source, deployable in one command, and designed for the 99% of market participants who cannot afford institutional data access. Built with BrightData's full infrastructure stack, asyncio orchestration, and FastAPI for the API layer.
```

(~160 words)

### Tech Stack

```
BrightData SERP API, BrightData Web Unlocker API, BrightData Scraping Browser, Claude Sonnet 4.6 (Anthropic), Python 3.12, asyncio, FastAPI, Pydantic v2, Next.js 15, Vercel, Polygon.io, Yahoo Finance, Docker, Fly.io
```

---

## GitHub README Template

```markdown
# AltBrief

> Live web intelligence → institutional-grade investment briefs, in seconds.

![Demo GIF](assets/demo.gif)

[![Live Demo](https://img.shields.io/badge/demo-live-brightgreen)](https://altbrief.vercel.app)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Built with BrightData](https://img.shields.io/badge/data-BrightData-orange)](https://brightdata.com)

## What It Does

AltBrief is an AI agent that scrapes live public web data and synthesizes it into
structured investment briefs — the kind a hedge fund analyst would write.
Any ticker. Real-time. Under 45 seconds.

## Demo

[![5-min Demo Video](assets/thumbnail.png)](https://youtube.com/...)

## Quick Start

    git clone https://github.com/ujjawal/altbrief
    cd altbrief
    cp .env.example .env   # add BRIGHTDATA_API_KEY + ANTHROPIC_API_KEY
    pip install -r requirements.txt
    python main.py --ticker NVDA

## Architecture

![Architecture Diagram](assets/architecture.png)

Parallel data collection via 3 BrightData products → normalization → LLM synthesis → structured brief.

| Layer | Technology |
|-------|-----------|
| Data | BrightData SERP API, Web Unlocker, Scraping Browser |
| Agent | asyncio + Pydantic v2 |
| LLM | Claude Sonnet 4.6 (Anthropic) |
| API | FastAPI |
| Frontend | Next.js 15 + Tailwind 4 |
| Deploy | Fly.io (backend) + Vercel (frontend) |

## BrightData Integration

- **SERP API** — real-time news headlines for any ticker
- **Web Unlocker API** — SEC filings, earnings transcripts (anti-bot bypass)
- **Scraping Browser** — Reddit WSB, StockTwits social sentiment

Built for Web Data UNLOCKED Hackathon 2026.

## Sample Output

    {
      "ticker": "NVDA",
      "date": "2026-05-27",
      "overall_direction": "bullish",
      "overall_confidence": 0.82,
      "signals": [...],
      "brief_narrative": "...",
      "sources_used": [...]
    }

## Built By

Ujjawal Shrivastava — [LinkedIn] · [GitHub]
```

**Key rules:**
1. Demo GIF first visual — above fold
2. One-line install. No multi-step setup hero
3. Architecture PNG in repo (not Figma link — links rot)
4. BrightData credit section mandatory
5. Sample output with real JSON (not `...`) — "claimed to work" vs "demonstrably works"

---

## AI Startup Program Dual-Framing

This deck serves two audiences:

**Audience 1 — Hackathon judges:** Score idea, execution, tool use, presentation.
**Audience 2 — BrightData AI Startup Program reviewers:** Is this real business? Would credits accelerate? Founder credible?

**Slides serving both:**
- Slide 2 (Problem) — relatable pain + large market pain
- Slide 10 (Market) — big opportunity + capturable TAM
- Slide 11 (Roadmap) — vision + specific ask with specific output

**Why "$20K credits = 400K briefs" works:**
1. Shows unit economics (operating, not just building)
2. Ties ask to BrightData product (credits for scale, not demos)
3. Anchors $20K as specific resource with specific output

This is the difference between hackathon demo and startup application. Infrastructure same. **Framing** changes.

---

## Execution Checklist (4-6 hour build)

**Hour 1: Content**
- Finalize name (AltBrief or chosen)
- Capture 2-3 real brief outputs (Slides 3, 5, README)
- Build architecture diagram in Excalidraw → PNG
- Screenshot working UI

**Hour 2: Gamma deck**
- Create Gamma account
- Paste spec into AI prompt
- Apply dark palette (`#0D0D0D` + `#FF6B35` + `#00D4AA`)
- Insert screenshots/GIFs
- Add BrightData + lablab logos

**Hour 3: README + GitHub**
- `assets/` folder: demo.gif, architecture.png, thumbnail.png
- README per template
- `.env.example` with placeholders
- Verify `pip install && python main.py --ticker TSLA` in clean venv

**Hour 4: Form + submission**
- Title, short desc, long desc copy
- Record 5-min demo video (screen + voiceover)
- Upload to YouTube (unlisted or public)
- Submit lablab form with Gamma link

**Hours 5-6: Buffer**
- Test live URL fresh browser / incognito
- Test QR code Slide 5
- Pre-warm Fly.io deployment

---

## Risk Flags

- **Vercel/Fly.io cold start:** Pre-warm before pitch OR use recorded GIF as primary demo with QR labeled "try after presentation"
- **Satellite imagery (Slide 6):** If not built, remove row OR mark "Roadmap v2" — never claim capabilities you can't demo
- **AI Startup Program flow:** [unverified] — confirm whether separate application or same as hackathon submission

---

## Sources

- [lablab.ai Hackathon Guide](https://lablab.ai/guide)
- [Web Data UNLOCKED](https://lablab.ai/ai-hackathons/brightdata-ai-agents-web-data-hackathon)
- [BrightData Web Unlocker Docs](https://docs.brightdata.com/scraping-automation/web-unlocker/introduction)
- [BrightData SERP API](https://brightdata.com/products/serp-api)
- [Alt-Data Market Size 2026 — FMI](https://www.futuremarketinsights.com/reports/alternative-data-market)
- [Hedgeweek alt-data spending](https://www.hedgeweek.com/hedge-fund-alt-data-spending-set-to-surge-says-new-research/)
- [Bloomberg Terminal Cost 2026](https://tradingtoolshub.com/blog/bloomberg-terminal-cost-features-2026/)
- [Gamma vs Pitch 2026](https://www.fahimai.com/gamma-vs-pitch)
- [YC Pitch Deck Guide](https://www.ycombinator.com/library/2u-how-to-build-your-seed-round-pitch-deck)
