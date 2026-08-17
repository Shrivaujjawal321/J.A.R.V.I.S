# Demo Video Playbook — Alt-Data Investment Brief Agent

**Target runtime:** 4 min 45 sec (hard cap 5:00 / 300 MB)
**Recorder:** Solo Indian dev, laptop, phone earbuds mic — no studio needed.

---

## Reference Winning Demos (Dissected)

1. **RiskWise (MS AI Agents 2025 Best Overall)** — Cold open with supply-chain disruption stat, immediate live agent run, zero intro slide. Architecture diagram at 3:20 with sponsor tech named mid-diagram. **Lesson:** Pain → live run → structured output → architecture → impact.

2. **Autonomous xStocks Trading Agent (lablab.ai Arc/USDC)** — Real-time demo: agent ranking signals, running backtest, P&L. Presenter narrates each step while agent executes. Visible latency becomes feature. **Lesson:** Real-time execution with narrated commentary beats clean pre-recorded run.

3. **TARIFFED! (MS AI Agents 2025 Multi-Track)** — Multi-tool chaining shown explicitly. Voiceover names each tool: "first searches live web data… then grounds against private data… then synthesises." **Lesson:** Show agent's internal steps.

4. **ChatEDU (MS AI Classroom 2024 1st)** — Three use-cases back-to-back, each under 30s. Market size in one sentence. **Lesson:** Multiple use cases fast beats one use case slow.

5. **Bridge-PA (lablab Healthcare PA)** — Opens with "insurance approvals take 3-7 days." Cuts to "with Bridge-PA: 4 minutes." Timer on screen during live run. **Lesson:** One before/after metric visually beats five vague impact claims.

---

## The Proven 5-Minute Structure

```
0:00 - 0:10   HOOK          — Pain. No name. No intro. Start mid-action.
0:10 - 0:30   PROMISE       — What you built. One sentence. Show output not code.
0:30 - 1:30   MAGIC MOMENT  — Live demo Ticker 1 (NVDA).
1:30 - 3:00   DEEP DEMO     — Ticker 2 (XOM satellite). Ticker 3 (WMT parking).
3:00 - 4:00   ARCHITECTURE  — Diagram. BrightData named per scrape type.
4:00 - 4:30   IMPACT/MARKET — Market size + "this brief costs $2,000 from research firm"
4:30 - 4:45   CTA           — GitHub + live URL. Hold on output brief.
```

---

## Full 5-Minute Word-for-Word Script

> Read verbatim. `[ ]` = 1-second pause. **Bold** = emphasis. *(Parens) = screen action.*

### 0:00–0:10 — HOOK
*(Terminal window open, cursor blinking. No title card.)*

**"Professional investors pay $2,000 for a single research brief. [ ] That's absurd — when 90% of the alpha is hiding in public web data."**

*(Cut to: finished brief PDF on screen)*

### 0:10–0:30 — PROMISE

**"I built an agent that inputs any stock ticker [ ] and in 45 seconds delivers a one-page institutional-grade investment brief — [ ] pulling seven parallel live data streams via BrightData."**

*(Show finished NVDA brief 3-4 sec — zoomed legible: Executive Summary, Satellite Signal, Social Sentiment, SEC Risk, Price Target)*

**"Let me show you NVIDIA first."**

### 0:30–1:30 — MAGIC MOMENT (NVDA)

*(Split view: left terminal/agent log, right brief building live)*

**"I'm typing NVDA. [ ] The agent immediately fans out — seven parallel scrapers running right now."**

*(~5 sec pause — narrate)*

**"BrightData's Web Unlocker is pulling Reddit WallStreetBets sentiment — that's hard to scrape without getting blocked. [ ] SERP API is grabbing last 72 hours of news headlines. [ ] Scraping Browser is navigating SEC EDGAR for the most recent 10-K risk factors."**

*(Agent output appearing right pane)*

**"And here it comes — [ ] Executive Summary populating. Bull thesis, bear case, three alt-data signals, price target with confidence range."**

*(Show complete brief full screen 5 sec)*

**"45 seconds. [ ] Bloomberg charges $24 a month just for terminal access — that's before any analyst time."**

### 1:30–2:15 — DEEP DEMO: XOM (Satellite/AIS)

*(Type XOM)*

**"Now ExxonMobil — this is where the satellite and maritime data layer activates."**

*(~10 sec — narrate)*

**"The agent is cross-referencing AIS vessel tracking data — tanker movements near Permian Basin export terminals. [ ] Satellite API is checking refinery operational status. [ ] This is alt-data that professional funds pay tens of thousands of dollars a month to access."**

*(Show XOM brief — zoom Satellite Signal section)*

**"Notice the Satellite Signal — flare activity at XOM's Beaumont refinery is up 18% week-over-week. [ ] That's a production surge indicator. [ ] You're not going to find that on CNBC."**

### 2:15–3:00 — DEEP DEMO: WMT (Foot Traffic)

*(Type WMT)*

**"Walmart — retail is where geospatial alt-data gets interesting."**

*(~10 sec)*

**"BrightData scraping parking lot metadata and foot traffic indices. [ ] Cross-referenced against consumer sentiment from Reddit and Twitter. [ ] The agent correlates parking density trends against quarterly earnings beats — [ ] and right now showing a divergence."**

*(Show WMT brief — zoom Foot Traffic)*

**"Foot traffic up 6% YoY [ ] but online sentiment on Walmart.com reviews trending negative. [ ] Brief flags this as a watch signal — classic brick-and-mortar vs e-commerce friction."**

### 3:00–4:00 — ARCHITECTURE

*(Architecture diagram from Excalidraw, hold 60 sec)*

**"Here is how it works under the hood."**

**"Orchestration layer is Claude Sonnet via Anthropic — decomposes ticker into seven parallel research tasks [ ] and synthesises into the final brief."**

**"Every data node runs through BrightData. [ ] Specifically: Web Unlocker for social — Reddit, Twitter, StockTwits. [ ] SERP API for real-time news. [ ] Scraping Browser for SEC EDGAR filings — needs full browser to navigate authenticated pages. [ ] Datasets API for satellite and AIS maritime. [ ] And residential proxy network to ensure we never get blocked on financial data sites."**

**"Output is structured JSON brief that renders to PDF. [ ] Total cost per run: under three cents in API calls."**

### 4:00–4:30 — IMPACT / MARKET

*(Two-column comparison table on dark background)*

**"Alternative data market is $1.3 billion, growing 30% annually. [ ] Hedge funds, family offices, retail investors — all need this analysis."**

**"Bloomberg Terminal: $27,000/year. [ ] Refinitiv brief: $2,000. [ ] Our agent: open source, 45 seconds, zero subscription."**

**"Real opportunity: embed as MCP server — any AI assistant can call it. [ ] Cursor, Claude Desktop, any agentic workflow. [ ] Alt-data becomes a commodity."**

### 4:30–4:45 — CTA

*(Text overlay showing GitHub URL + live demo URL — hold 10+ sec)*

**"GitHub live — link in description. [ ] Live demo deployed — try with any ticker."**

*(Hold on finished brief as final frame — do NOT fade to black)*

**"That's the Alt-Data Investment Brief Agent. [ ] Built with BrightData. [ ] Thanks."**

---

**Total: ~480 words. At 110 wpm with pauses: ~4 min 40 sec. 20 sec buffer.**

---

## Production Checklist

### Screen Recording: OBS Studio

| Tool | Verdict |
|---|---|
| **OBS Studio** | PICK. Free, no file size cap, split-screen native, MP4 output. |
| Loom | 5 min free cap, compression artifacts on terminal text |
| ScreenStudio | Mac only |

**Settings:**
- 1920x1080, 30 FPS
- x264, CRF 23
- 44100 Hz stereo, 128 kbps, MP4

**Pre-record test:** 30s test, verify terminal legible, audio not clipping, Do Not Disturb on.

### Microphone: Phone Earbuds

- Mic end near mouth (not chest)
- Smallest room with soft furnishings (bedroom > kitchen)
- Speak 110 wpm — slightly slower than normal
- **Don't** use laptop built-in mic — fan + keyboard noise

### Background Music

- freemusicarchive.org or YouTube Audio Library
- Genre: "Ambient Electronic" / "Corporate Technology"
- Volume: -30dB to -35dB relative to voiceover
- Fade out last 10s so CTA clean
- Suggested: "Chill Abstract Intention" by Kevin MacLeod

### Captions: Whisper + ffmpeg

```bash
ffmpeg -i demo_raw.mp4 -q:a 0 -map a demo_audio.mp3
whisper demo_audio.mp3 --model large-v3 --output_format srt --language en
ffmpeg -i demo_raw.mp4 -vf subtitles=demo_audio.srt demo_captioned.mp4
```

Alternative: CapCut auto-captions (~2 min).

Style: White text, black outline, 36pt, bottom-center, max 8 words/frame.

### Editing: CapCut (Boss knows it)

**Workflow:**
1. Import raw OBS recording
2. Auto-caption → fix 2-3 errors → style
3. Text overlays: "7 PARALLEL SCRAPERS" @ 0:35 / "POWERED BY BRIGHTDATA" @ 3:05 / "$0 vs $2,000" @ 4:10
4. BrightData logo PNG bottom-right during 3:00–4:00
5. Auto silence removal
6. Music track at -30dB
7. Export 1080p MP4

---

## Common Video Failures

1. **Talking head only.** Face must not exceed 30% of runtime. Screen is king.
2. **No live demo.** Static output screenshot vs running agent = massive credibility gap.
3. **Bad audio.** Audio quality beats video. Test first.
4. **Music at conversation volume.** -30dB or mute.
5. **Terminal text too small.** Zoom to 125-150%. Font 18pt minimum.
6. **Over-edited transitions.** Slick animations signal "polish, not product." Cut cuts only.
7. **CTA buried.** GitHub URL on-screen text 8+ sec.
8. **Opening with name/intro.** "Hi my name is X" = lost 10s. Start with pain or mid-demo.

---

## Architecture Diagram (Excalidraw)

```
[User Input: Ticker Symbol]
        ↓
[Claude Sonnet — Orchestrator]
        ↓ (7 parallel tracks)

[BrightData Web Unlocker]      → Reddit/Twitter/StockTwits Sentiment
[BrightData SERP API]          → News Headlines (72h)
[BrightData Scraping Browser]  → SEC EDGAR 10-K/10-Q Filings
[BrightData Datasets API]      → Satellite + AIS Maritime
[BrightData Residential Proxy] → Financial Data Sites
[Yahoo Finance API]            → Price/Volume/Options (free)
[Alpha Vantage API]            → Earnings History (free tier)

        ↓ (converge)
[Claude Sonnet — Synthesis]
        ↓
[Structured JSON Output]
        ↓
[One-Page PDF Investment Brief]
```

**Colors:** BrightData = electric blue (#00B2FF). Claude = Anthropic purple (~#7B3FF2). Free APIs = neutral gray. Font 14pt min.

---

## Comparison Slide (Impact 4:00–4:30)

Google Slides / Canva → PNG → CapCut at 4:05.

| Source | Time | Cost |
|---|---|---|
| Bloomberg Terminal | 5-10 min | $27K/yr |
| Refinitiv Brief | 1-2 days | $2,000+ |
| Alt-Data Broker | Manual | $50K+/yr |
| **Our Agent** | **45 sec** | **$0.03** |

---

## Pre-Recording Checklist

**45 min before:**
- Close all unneeded browser tabs
- Enable Do Not Disturb / Focus Assist
- Terminal font ≥18pt
- Browser zoom 125% on web pages
- Disable screen saver
- **Pre-warm agent:** Run NVDA once so first API latency cleared
- OBS test 30s: audio -12 to -6 dB
- Architecture diagram open in browser, ready to alt-tab

**15 min before:**
- Read script aloud once, timed
- If >4:50, cut one Impact sentence
- Water nearby — dry mouth audible
- Test agent each ticker — no API errors

**During:**
- 2-3 complete takes. Pick best. Don't do 10 — fatigue.
- Mistake mid-segment: say "let me redo" and continue — CapCut cuts it

**Post:**
- Watch raw at 1.5x, flag cuts
- Verify terminal + brief legible
- Auto-caption → fix → style
- 3 text overlays + BrightData logo + comparison slide
- Music -30dB
- Export 1080p MP4
- File size 80-180 MB normal (cap 300 MB)
- Watch final on phone — judges often view mobile

---

## The Three Things That Win

1. **Real agent running live on screen for 2+ minutes** — visible logs, output populating real-time. Not screenshots. The running agent IS the product demo.

2. **BrightData named per capability** — "Web Unlocker for Reddit… SERP API for news… Scraping Browser for SEC." Each product name spoken during architecture hits sponsor-criteria scoring.

3. **One before/after metric held on screen for 30 seconds** — "45 seconds vs $2,000 per brief." That number is what judges carry into the scoring session.

Everything else (music, transitions, captions) is polish. Get these three right first.

---

## Sources

- [Recent AI Hackathons Winners — lablab.ai](https://lablab.ai/apps/recent-winners)
- [AI Agents Hackathon 2025 Winners — Microsoft](https://techcommunity.microsoft.com/blog/azuredevcommunityblog/ai-agents-hackathon-2025-%E2%80%93-category-winners-showcase/4415088)
- [6 Tips for Winning Hackathon Demo Video — Devpost](https://info.devpost.com/blog/6-tips-for-making-a-hackathon-demo-video)
- [How I Win Hackathons — szeyusim](https://szeyusim.medium.com/how-i-win-most-hackathons-stories-pro-tips-from-a-serial-hacker-1969c6470f82)
- [Web Data UNLOCKED Hackathon](https://lablab.ai/ai-hackathons/brightdata-ai-agents-web-data-hackathon)
- [CapCut vs Descript 2026](https://www.fahimai.com/capcut-vs-descript)
- [Whisper AutoCaption](https://blog.paperspace.com/automatic-video-subtitles-with-whisper-autocaption/)
