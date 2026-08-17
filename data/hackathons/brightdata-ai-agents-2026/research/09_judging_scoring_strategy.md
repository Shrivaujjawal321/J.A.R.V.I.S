# Judging & Scoring Strategy — BrightData "Web Data UNLOCKED"

Target: podium (top 3). Opinionated playbook.

---

## The 4 Named Criteria

### 1. Application of Technology

**7→9 moves:**
- **Composability:** Agent *decides* which BrightData tool per context — SERP for discovery, Web Unlocker for paywalled Reuters, Scraping Browser for JS-heavy dashboards, Dataset API for structured bulk.
- **Visible error handling** in demo — bad URL retried, rate-limited source flagged with confidence note.
- **Justified tech choices** — one sentence voiceover on "why Claude Sonnet over GPT" scores higher than silence.
- **Speed instrumented in UI** — "Sources gathered: 43s | Brief generated: 12s."

**Score killers:**
- Hardcoded JSON pretending to be live scraping
- Single-tool usage
- API key visible in plaintext during recording

---

### 2. Presentation

**7→9 moves:**
- Problem felt before solution shown. **Do not start with "Hi, we built…"**
- Visual callouts (zoom, arrows, text overlays) — judges watch at 1.25x
- No dead air
- Close with roadmap slide
- **Video length: 3:30–4:00 min** (under 2 = rushed, over 5 = patience-testing)

**Score killers:**
- Reading slides verbatim
- Code on screen >30s total
- Demo crash with no narrated recovery
- 720p recording, fast mouse movement

---

### 3. Business Value

**7→9 moves:**
- **Specific buyer named:** "Tier-2 hedge funds with AUM $50M–$500M that can't afford Bloomberg + research team"
- **Pricing hypothesis on screen:** "$29/mo individual | $299/mo team | $2,000/mo white-label API"
- **Two displacement vectors:** "$24K Bloomberg/year → $0" + "Analyst at $120K/year, 30% time on data gathering = $36K/year reclaimed"
- **BrightData as compliance moat:** "Legal scraping layer lets us serve regulated financial clients that can't use grey scrapers"

**Score killers:**
- "Anyone interested in investing can use this"
- No monetization mentioned
- Overstating accuracy without methodology

---

### 4. Originality

**7→9 moves:**
- **Name novelty explicitly** — one slide: "What's genuinely new here"
- **Alt-data framing throughout** — use the term "alt-data" in title + narration
- **Pipeline stages named:** "Discovery → Extraction → Cross-source validation → Brief synthesis with confidence scoring"
- **Comparison slide:** Bloomberg/FactSet behavior vs. our agent

**Score killers:**
- "Like ChatGPT but for stocks" — never say this
- No architecture diagram
- Solving same problem as 12 other submissions

---

## The Implicit 5th Criterion: BrightData Infrastructure Depth

Sponsor judges directly assess how much of their stack you used. **1 tool = baseline. 4 tool groups = standout.**

**The 4 tool groups + how to use:**

1. **SERP API** — discovery: "[TICKER] earnings surprise 2026," "[TICKER] Reddit sentiment"
2. **Web Unlocker** — paywall bypass: SEC EDGAR, Reuters, WSJ rendered without CAPTCHA interruption
3. **Scraping Browser** — JS-heavy dashboards: Yahoo Finance interactive charts, Seeking Alpha, Glassdoor
4. **Dataset API** — structured bulk: pre-built LinkedIn company headcount + Amazon consumer sentiment

**Proving depth in demo (in order of ROI):**

1. **Scrolling overlay log in UI corner.** Shows real-time:
   ```
   Calling BrightData SERP API... [43 results]
   Invoking Web Unlocker: reuters.com/article/... [success]
   Scraping Browser: glassdoor.com/TICKER reviews... [127 reviews]
   Dataset API: LinkedIn headcount... [loaded]
   ```
   Single highest-ROI element.

2. **Architecture diagram** — one slide, 4 BrightData product boxes + arrows. Judges screenshot. BrightData judges share internally.

3. **15 seconds of terminal output** — endpoint URL + tool type visible. Engineers recognize as real.

---

## The First 60 Seconds Rule

Judges score within first 60-90s. Rest confirms or weakly revises.

**Recommended script:**

**0-10s — Problem Hook:**
> "Every morning, thousands of investors try to make a $50,000 decision based on 3-day-old news, a Reddit thread, and a gut feeling. Bloomberg Terminal costs $24,000/year. They can't afford it. We fixed that."

NO "Hi I'm [name], we built an agent that…"

**10-30s — Promise + flash of output:**
> "Our Alt-Data Investment Brief Agent pulls from 7 live sources — financial news, SEC filings, Reddit sentiment, job postings, employee reviews, web traffic, competitor mentions — delivers a structured brief in under 60 seconds."
Cut immediately to: finished brief on screen.

**30-60s — Magic Moment, live agent run:**
> "Let me show you. I type 'NVDA'. The agent calls BrightData SERP... 40 sources queued... Web Unlocker on Reuters... Scraping Browser on Glassdoor... brief ready. 47 seconds."

Show elapsed timer + overlay log.

**60s+:** tech depth → business case → roadmap

---

## Quantification Frame

Numbers are credibility anchors:

| Metric | Framing |
|--------|---------|
| Bloomberg cost | $24,000/year → $0 with our agent |
| Analyst time saved | 4 hrs/brief → 47 sec = 97% reduction |
| Source coverage | 7 parallel alt-data categories, 40+ URLs |
| Brief generation | 47 seconds end-to-end |
| Data freshness | Pulled live, no stale DB |
| BrightData breadth | 4 distinct product categories |

Build a "numbers slide" + weave each into narration once. Goal: judge can cite 3 specific numbers to co-judges from memory.

---

## Originality Trap Escape

Median submissions: News summarizer with LLM / Stock price + sentiment scorer / Earnings call analyzer. **None are alt-data.**

**3 escape moves:**
1. Use "alt-data" explicitly — professional concept signaling domain expertise
2. Name non-obvious sources — Glassdoor reviews = management quality proxy. Job velocity = growth signal. Web traffic = revenue leading indicator.
3. **Name cross-source contradiction detection** — "Agent flags when Reddit sentiment contradicts analyst consensus, or job posting velocity contradicts company's stated growth narrative." That reasoning layer is the novel contribution.

---

## Business Value Framing

**4-tier pricing slide:**

| Persona | Pain | Price |
|---------|------|-------|
| Retail investor | Manual 4-hr research | $15-29/mo |
| Small RIA / family office | Bloomberg too expensive | $99-299/mo |
| Fintech app embedding | Needs data layer | $500-2,000/mo API |
| Tier-2 hedge fund | Bloomberg + alt-data too expensive | $5K-20K/yr enterprise |

VC judge wants plausible revenue path. B2C tier resonates with non-finance judge. B2B API resonates with engineer judge. Both on screen = both archetypes covered.

---

## Anti-Pattern List

**Video:**
- Name/intro before problem hook
- >5 min length
- No live URL in submission
- Coding montage >20s
- No roadmap / CTA close

**Technical:**
- Single BrightData tool usage
- Hardcoded responses
- No visible error handling
- LLM prompt never shown (even 5s flash of system prompt signals depth)

**Narrative:**
- "We used BrightData for data collection" — 90% of submissions say exactly this
- "AI-powered solution leverages cutting-edge LLMs" — filler
- Comparing to Bloomberg without explaining moat (Bloomberg won't democratize; we will. BrightData compliance enables regulated clients.)

---

## Remote Disadvantage Compensation

No onsite SF presence offset:

- **Video quality as proxy for in-person energy.** Clean background, decent mic (no echo), 1080p minimum, tight edits.
- **GitHub README as the lobby.** Open with: problem → live demo URL → 1-command launch → architecture diagram. Run-in-5-min beats onsite presence.
- **Live deployment non-negotiable.** Vercel / Hugging Face Spaces / Railway. URL in video + README + submission form.
- **Async polish advantage.** SF teams sleep-deprived Day 5 morning. Use time difference to polish.

---

## Judge Archetypes

**A: BrightData PM/DevRel** — Cares about infra depth, # tools, creative use cases, compliance moat. Wants: architecture diagram with BrightData labeled, live API calls visible, non-obvious sources. Docks: SERP-only, ignoring legal moat.

**B: VC / Investor** — Cares about business value, market size, defensibility, pricing. Wants: specific buyer, displacement economics, monetization tiers. Docks: "everyone could use this," no monetization, tech-first.

**C: Senior AI/ML Engineer** — Cares about multi-step pipeline, demo realness. Wants: multi-tool orchestration, error handling, justified models, live demo doesn't break. Docks: ChatGPT wrapper feel, hardcoded responses.

**Three-move combo covering all:**
Architecture diagram (A+C) + pricing/buyer slide (B) + working live demo URL (A+B+C).

---

## Submission Timing

**Submit working version by Day 3, update through deadline.**

- lablab allows submission updates until deadline
- Early submissions indexed first → reviewed when judge attention fresh
- Forces working live demo by Day 3 → Day 4-5 is polish not panic
- Psychological shift from "finish" to "polish" → measurably better video

**Day 3:** Working agent + rough video + live URL
**Day 5:** Polished video + full README + architecture diagram + pricing slide

Don't wait until last 2 hours — last-hour submissions reviewed last by fatigued judges, no time for them to try live URL.

---

## The Podium Checklist

| Signal | Target |
|--------|--------|
| Live URL in submission | Non-negotiable |
| BrightData tool categories | 4 (SERP + Unlocker + Browser + Dataset API) |
| Scrolling overlay log | Highest single ROI |
| Elapsed timer visible | Primary quantification anchor |
| Architecture diagram | One slide, screenshot-worthy |
| Buyer + pricing slide | Covers VC archetype |
| "Alt-data" in title + narration | Primary originality anchor |
| Video length | 3:30–4:00 min |
| First 10s problem hook | First-60-sec rule |
| README 1-cmd launch | Remote disadvantage offset |
| Cross-source contradiction named | Differentiates from "news summarizer" |
| Submit working by Day 3 | Timing strategy |

---

## Top 3 Highest-Leverage Moves

1. **Scrolling BrightData tool overlay in UI** — hits 3 judge archetypes simultaneously (tech depth + infra depth + proof of live)
2. **0-10s problem hook replacing "hi we built"** — mental score set in first 60s, most teams waste it
3. **Architecture diagram with 4 BrightData products labeled** — 30 min to make, pays dividends across all archetypes; judges screenshot it
