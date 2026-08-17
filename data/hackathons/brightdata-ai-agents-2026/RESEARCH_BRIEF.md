# RESEARCH BRIEF — Web Data UNLOCKED Hackathon (BrightData × lablab.ai)
**Prepared:** 2026-05-25 | **Status:** Go/No-Go Decision Document

---

## 1. Basics (One-Glance Facts)

| Field | Detail |
|-------|--------|
| **Full Name** | Web Data UNLOCKED Hackathon |
| **Organizers** | lablab.ai + Bright Data |
| **Start** | May 25, 2026 (TODAY — already started) |
| **End / Awards** | May 31, 2026 |
| **Duration** | 7 days total (≈ 144 hours) |
| **Format** | Hybrid — online + onsite SF |
| **Submission Deadline** | May 30, 2026 (online build phase ends) · Awards May 31 |
| **IST Conversion** | PDT = IST − 12h 30min · May 30 11:59 PM PDT = **May 31, 12:29 PM IST** |
| **Venue (onsite)** | The Web Data Loft, 625 2nd St, San Francisco, CA (Bright Data's new SF space opening) |
| **Platform** | lablab.ai + Discord (community + mentor access) |
| **Registration** | https://lablab.ai/ai-hackathons/brightdata-ai-agents-web-data-hackathon |
| **Team Formation** | Via lablab.ai platform; solo or team both allowed [unverified: exact max team size — standard lablab.ai cap is 5] |
| **Eligibility** | Open globally (hybrid = online from anywhere); onsite requires travel to SF; no age/student restriction stated [unverified] |
| **Cost** | Free to enter |

> **CRITICAL:** The hackathon STARTED TODAY (May 25, 2026). Boss has ~5.5 days left if registering now.

---

## 2. Problem Statement — Vertical Deep Dive

### 2.1 Verbatim Theme

From the lablab.ai event page:

> "Build what was not possible before — when AI agents were locked, throttled, or limited by stale data. Use Bright Data's full infrastructure stack to build AI agents, data systems, and production-ready web data infrastructure powered by **real-time web access.**"

The core thesis: **AI agents are blind without live web data.** Most LLM-based agents reason over training-cutoff knowledge or manually curated context. BrightData's thesis is that a production AI agent must be able to pull live, structured data from the open web on demand — bypassing anti-bot defenses, geo-blocks, and CAPTCHA walls — and reason over it in real time. This hackathon is their proof-of-concept showcase.

### 2.2 Sub-Tracks / Challenge Categories

No formally named sub-tracks are published [unverified via lablab.ai 403]. However, based on Bright Data's own infrastructure offerings and the framing, the implied categories are:

1. **AI Agent + Live Web** — Agents that call BrightData MCP tools dynamically to pull data and act on it
2. **Data Pipeline / Infrastructure** — Production-grade web data ingestion pipelines (scraping → vector store → RAG)
3. **Structured Web Data Intelligence** — Using BrightData's 660+ pre-built site scrapers to extract and analyze specific-domain data (e-commerce, finance, social)

The framing explicitly covers "AI agents, data systems, and production-ready web data infrastructure" — so the judging surface is broad.

### 2.3 BrightData Product Surface — Exact Tools

These are the specific BrightData tools participants can (and should) use. Mandatory vs. nice-to-have flagged below.

| Tool | What It Does | Mandatory? |
|------|-------------|------------|
| **MCP Server** (`@brightdata/mcp` on npm) | All-in-one Model Context Protocol server — lets Claude, GPT, Cursor, VS Code agents call BrightData infrastructure via 60+ named tools. Single `npx @brightdata/mcp` install, configure with `API_TOKEN`. | **Yes — primary integration point** |
| `search_engine` | Web search with AI-optimized results, returns markdown-formatted snippets. Free tier (5,000 req/month). | Likely mandatory baseline |
| `scrape_as_markdown` | Fetches any URL, returns clean markdown (images stripped, JS rendered, anti-bot bypassed). Free tier. | Likely mandatory baseline |
| `discover` | AI-ranked intent-based search — not just SERP, but semantic relevance scoring. | High value |
| `search_engine_batch` / `scrape_batch` | Parallel bulk operations — batch 10-100 URLs in one call. | Nice-to-have for throughput |
| **Web Unlocker API** | Handles proxy rotation + CAPTCHA solving + fingerprint mimicry in one call. 98% claimed success rate. Charges per successful request only. Bypasses Cloudflare, Akamai, DataDome. | Nice-to-have (Pro mode) |
| **SERP API** | Structured JSON extraction from Google/Bing/Yandex SERPs — not raw HTML, real parsed results. $1.50/1K requests. Geo-specific results supported. | Nice-to-have |
| **Scraping Browser** | Cloud-hosted Chromium you drive via Playwright/Puppeteer/Selenium. Built-in CAPTCHA solving, IP rotation, fingerprint management. Supports form-fill, clicks, scrolling — full browser automation for agent tasks. $8/GB pay-as-you-go. | Nice-to-have for browser-agent projects |
| **Web Scraper API** | 660+ pre-built site scrapers (Amazon, LinkedIn, Instagram, TikTok, Crunchbase, Zillow, GitHub, Reuters, Yahoo Finance, etc.) — returns structured JSON, no parser-writing needed. | High value for domain-specific projects |
| **Proxy Network** | 400M+ residential, datacenter, ISP, mobile IPs. Geo-targeting to country/city/ASN. | Nice-to-have (backend infra) |
| **Scraper Studio** | No-code scraper builder — build custom scrapers visually. | Nice-to-have |

**MCP Tool Groups** (configure via `GROUPS=` env var in MCP server):
- `ecommerce` → Amazon, Walmart, eBay, Google Shopping
- `social` → LinkedIn, TikTok, Instagram, Facebook, Reddit, X/Twitter, YouTube
- `browser` → Scraping Browser automation
- `finance` → Yahoo Finance, stock/market data
- `business` → Crunchbase, ZoomInfo, Zillow, Google Maps
- `research` → GitHub repos, Reuters, academic
- `app_stores` → iOS + Google Play
- `geo` → Query ChatGPT/Grok/Perplexity directly for brand visibility tracking
- `code` → npm + PyPI package intelligence
- `advanced_scraping` → Batch extraction + AI-assisted parsing

**Pro Mode activation:** Set `PRO_MODE=true` in MCP config → unlocks all 60+ tools. Default free tier = `search_engine` + `scrape_as_markdown` + `discover` only.

### 2.4 The "AI Agent + Web Data" Thesis — Why BrightData Sponsors This

BrightData is not a pure scraping utility — they're positioning as **the data infrastructure layer for agentic AI**. Their model: every production AI agent that touches real-world data needs a reliable, unblocked, structured data pipe. BrightData is that pipe. The hackathon is a developer-acquisition and ecosystem-building play — they want 500+ developers to build their workflow *on top of* BrightData's MCP server, discover its capabilities, and (if they build something valuable) become paying customers or join the AI Startup Program.

They specifically want to see:
- Agents that **stay current** (not stale training data)
- Agents that **act** on web data (not just retrieve it)
- Projects that showcase real-world use cases BrightData can market (competitive intelligence, lead enrichment, financial monitoring, research automation)

### 2.5 Sub-Problem Angles — 10 Brainstormed Attack Points

1. **Real-time competitive price monitoring agent** — E-commerce merchant agent that scrapes Amazon/Flipkart/Meesho for competitor prices hourly, triggers restock/repricing alerts, Claude reasons over trends. BrightData `ecommerce` group + SERP API.

2. **LinkedIn lead qualification agent** — Pulls LinkedIn company + person profiles via BrightData `business` group, scores ICP fit via Claude, drafts personalized outreach. Strong BrightData showcase (LinkedIn is explicitly in their scrapers).

3. **AI research assistant with live citation graphs** — Given a topic/paper, agent discovers related papers on Google Scholar + GitHub + Reuters, builds a citation graph, summarizes gaps, identifies hot researchers. `research` group + `discover`.

4. **Alternative financial data agent** — Pulls earnings call transcripts + analyst reports + Reddit/X sentiment + Yahoo Finance structured data, synthesizes investment thesis. `finance` + `social` groups.

5. **Talent intelligence agent** — Recruiters paste a JD; agent scrapes LinkedIn, GitHub, and Stack Overflow to identify qualified passive candidates; scores and ranks them. `business` + `code` groups.

6. **E-commerce brand monitoring agent** — Tracks brand mentions, product reviews, and competitor positioning across Amazon/Reddit/TikTok/Instagram in near-real-time. `ecommerce` + `social`.

7. **AI-powered news intelligence briefing** — Given a watchlist of companies/topics, agent pulls Reuters + X/Twitter + Reddit + Google News hourly, deduplicates, clusters by narrative, delivers a structured Telegram/Slack briefing. `research` + `social`.

8. **Regulatory / compliance monitoring agent** — Monitors government portals, court records, and industry news for regulatory changes that affect a business vertical. `research` + custom scraping.

9. **GEO (Generative Engine Optimization) audit agent** — Uses BrightData's `geo` group to query ChatGPT/Grok/Perplexity for brand mentions, compares vs. competitors, identifies what content would improve AI-generated brand visibility. *This is a genuinely novel angle* — BrightData just launched this group.

10. **AI app store intelligence agent** — Tracks app rankings, reviews, updates, and competitor feature launches across App Store + Google Play (`app_stores` group), generates competitive product reports. Underexplored vertical.

### 2.6 Technical Requirements — Mandatory vs. Nice-to-Have

**Mandatory (clearly expected):**
- Use at least one BrightData product/API (MCP server, Web Unlocker, SERP API, or Scraper API) — the entire hackathon premise
- Working prototype with a live demo URL
- Video presentation (max 5 minutes, under 300MB)
- GitHub repository
- Pitch deck

**Nice-to-Have / Competitive edge:**
- Multiple BrightData tool groups integrated
- Production-grade architecture (not just a Streamlit demo)
- Clear business value articulation
- Agent framework (LangChain, CrewAI, Claude Computer Use, Google ADK, n8n) on top of BrightData MCP
- Measurable outcome (speed vs. manual, accuracy, cost savings)

---

## 3. Sponsor & Mandatory Tech

### 3.1 BrightData — Full Tool Stack Available

As detailed in §2.3 above. Summary of what participants get:

- **Free on Day 1:** $250 in Bright Data API credits distributed at the Kick-off stream on Discord/live
- **Additional credits:** Can be requested on-site (SF) or via the hackathon Discord channel
- **Free tier baseline:** 5,000 MCP requests/month (search + scrape)
- **Pro mode:** Requires BrightData account + API token (free credits cover this)
- **AI Startup Program fast-track:** Winners get access to Web Scraper API + MCP Server + Web Unlocker + SERP API + Scraping Browser + Proxies + Scraper Studio + up to **$20,000 in additional Bright Data credits**

### 3.2 Other Sponsors / Partners

No other sponsors explicitly named on the lablab.ai page in search results [unverified — lablab.ai often includes model provider partners like Anthropic, OpenAI, or Groq on hackathon pages; check Discord on registration].

lablab.ai platform itself provides:
- Community Discord with mentors
- Workshops and live demos
- Project submission infrastructure

### 3.3 Framework Compatibility (confirmed by BrightData docs)

BrightData MCP works with:
- **Claude Desktop / Claude Code** (Anthropic — Boss's stack, perfect fit)
- **Cursor, VS Code, Windsurf** (coding agents)
- **LangChain, CrewAI** (agent orchestration)
- **Google ADK** (Agent Development Kit — confirmed via GitHub example)
- **n8n** (workflow automation)
- **OpenAI SDK**
- **NVIDIA NeMo**

---

## 4. Judging & Scoring

### 4.1 Judging Criteria

lablab.ai uses a standard framework across all hackathons (BrightData-specific weights not disclosed [unverified]):

| Criterion | What Judges Evaluate |
|-----------|---------------------|
| **Application of Technology** | How effectively BrightData + AI models are integrated; depth of tool usage vs. surface-level call |
| **Presentation** | Clarity of video + pitch deck; can judges understand the value in 5 minutes? |
| **Business Value** | Real-world impact; is this something a company would pay for? |
| **Originality** | Uniqueness of approach; not another generic chatbot; novel data use case |

**Implicit 5th criterion (inferred from BrightData sponsorship):** Use of BrightData infrastructure depth — projects that use only `scrape_as_markdown` will score lower than projects that orchestrate multiple tool groups, use the Scraping Browser for interactive workflows, or showcase the Web Scraper API's structured output for a real domain.

### 4.2 Judges

No judge names/bios were publicly surfaced in search results at time of research [unverified]. At similar lablab.ai hackathons, judges have been founders + engineers from the sponsoring company + lablab.ai staff. Given the SF onsite element, likely includes BrightData's SF-based team and possibly VC/advisor connections from their investor network.

### 4.3 Past lablab.ai Winners — What "Winning" Looks Like

Analysis of recent lablab.ai winning projects (across different hackathons) reveals consistent patterns:

- **Autonomous, multi-step agents** win over single-call demos (e.g., xStocks trading agent with backtesting + risk controls won at AI Agent Olympics 2026)
- **Polished video pitch** matters — the video IS the presentation for async judging
- **Real data + real results** — projects that show actual scraped/processed data in the demo beat pure architecture slides
- **Novel verticals** — the Luna "hormonal biology → executive decisions" project and OlympusOS "city emergency coordination" won because they picked underexplored problem spaces
- **Quantified impact** — "10x faster than manual research" or "found 50 qualified leads in 3 minutes" beats "this could potentially help companies"

BrightData-specific: A GitHub repo (`arjunprabhulal/brightdata-mcp-adk-hackathon`) exists showing a previous participant built a full web scraping + data extraction platform using BrightData MCP + Google ADK — this is the execution bar for a serious submission.

---

## 5. Prizes

| Prize | Details |
|-------|---------|
| **Grand Prize (Cash)** | **$5,000** (single winner across all projects) |
| **BrightData AI Startup Program** | Fast-track access for winning teams: Web Scraper API + MCP Server + Web Unlocker + SERP API + Scraping Browser + Proxies + Scraper Studio + up to **$20,000 additional credits** |
| **Day-1 Credits (all participants)** | **$250 in BrightData API credits** distributed at Kick-off stream |
| **Onsite perks (SF only)** | Free food, drinks, networking, workshops, mentorship, live demos at The Web Data Loft |
| **Additional credits** | Available on-request via Discord or onsite |

**Total potential value for a winner:** $5,000 cash + $20,000 BrightData credits + AI Startup Program support (co-marketing, office hours with CEO, technical training). For a project that becomes a real product, the $20K credits and startup program fast-track is the bigger prize.

No "best use of specific tool" category prizes were identified [unverified — lablab.ai sometimes adds sponsor-specific prizes; check Discord].

---

## 6. Submission Requirements

Based on lablab.ai's standard submission framework (hackathon-specific overrides may exist — verify on Discord after registration):

| Requirement | Spec |
|-------------|------|
| **Working prototype** | Live demo URL required — must be accessible by judges online |
| **Video** | Max 5 minutes, max 300MB file size |
| **GitHub repo** | Required — at least one team member needs a GitHub account |
| **Pitch deck** | Required |
| **Submission form fields** | Title (max 50 chars), short description (max 255 chars), long description (min 100 words), technologies used, live app URL |
| **Anti-cheat** | Project must be built during the hackathon window (May 25-31); pre-existing codebases flagged as disqualifying |
| **Demo format** | Async video-first; SF onsite demos on May 31 for shortlisted teams |
| **License** | Open-source not explicitly required [unverified]; lablab.ai does not mandate MIT/Apache licenses but GitHub repo must be accessible to judges |

**Submission deadline (best estimate):** May 30 EOD PDT (May 31, 12:29 PM IST) for the online build phase. Awards/live demos May 31.

---

## 7. Strategic Angle — Boss's Decision Intelligence

### 7.1 The "Obvious" Idea Everyone Will Submit

A news/article summarization agent that:
1. Takes a topic or URL from the user
2. Calls `scrape_as_markdown` on a few pages
3. Passes to Claude/GPT for summarization
4. Shows the output in a Streamlit UI

This will constitute ~40% of all submissions. It's the lowest-friction, most-templated approach. Judges have seen 500 of these. **Avoid.**

A close second: a generic "research assistant" that wraps `search_engine` + Claude summarization with no domain specificity. Also crowded.

### 7.2 Underexplored Angles Aligned With BrightData's Monetization

BrightData's biggest enterprise customers are in **e-commerce intelligence, financial alternative data, and B2B lead enrichment** — these are their highest-margin use cases. A project that demonstrably solves one of these problems with their stack is something they will promote as a case study regardless of whether it wins.

**Highest-signal picks for Boss's stack (Claude Code + Gemini + FastAPI + Next.js):**

**Option A — GEO Audit Agent** (most novel, least crowded)
- Problem: Companies have no idea if ChatGPT, Grok, or Perplexity mention them favorably vs. competitors
- Build: BrightData `geo` group queries 3 AI search engines for "best [product category]" → Claude analyzes results → identifies what content/schema changes improve AI brand visibility → generates actionable recommendations
- Why it wins: BrightData literally *just launched* the `geo` tool group. Fewer than 100 people globally have built with it. Judges will recognize novelty immediately.
- Boss's stack fit: FastAPI backend + Next.js dashboard, Claude as reasoning layer, BrightData MCP as data layer. 3-4 days to a polished demo.

**Option B — Talent Intelligence Agent** (high business value, clear BrightData showcase)
- Problem: Recruiters manually search LinkedIn for 2-3 hours per hire; 90% of candidates are never surfaced because Boolean searches are crude
- Build: JD input → BrightData `business` group scrapes LinkedIn profiles → BrightData `code` group scrapes GitHub activity → Claude scores ICP fit + generates ranked shortlist with personalized outreach drafts
- Why it wins: Directly uses LinkedIn scraper (BrightData's premium data source), quantifiable output ("found 12 qualified candidates in 4 minutes vs. 3 hours manual"), clear enterprise ROI
- Boss's stack fit: Jarvis already has LinkedIn pipeline infrastructure. Reuse patterns. 2-3 days to demo.

**Option C — Alternative Data Financial Brief Agent** (technical depth, sophisticated audience)
- Problem: Retail investors and analysts lack a structured way to pull alternative signals (Reddit sentiment + earnings call tone + LinkedIn hiring trends + product review velocity) into one research brief
- Build: Ticker input → BrightData `finance` + `social` + `business` + `research` groups → Claude synthesizes cross-signal narrative → structured investment brief PDF/dashboard
- Why it wins: Uses the most BrightData tool groups (judges reward depth of integration), technically sophisticated, clear business use case (FinTech is a hot market)
- Boss's stack fit: All Python/FastAPI, Claude as synthesizer, Next.js dashboard. 4-5 days.

### 7.3 Realistic Time-to-Build for Boss

Boss's stack: Claude Code + Jarvis multi-agent system + FastAPI + Next.js + Python. With Jarvis spinning parallel agents for research + code:

| Project | Core Build Time | Polish + Demo Video | Total |
|---------|----------------|--------------------|----|
| GEO Audit Agent | 1.5 days | 1 day | **~2.5 days** |
| Talent Intelligence Agent | 2 days | 1 day | **~3 days** |
| Alt Data Financial Brief | 3 days | 1.5 days | **~4.5 days** |

Given the hackathon runs until May 30 (5.5 days from today), **all three are feasible**. The GEO agent is the fastest path to a polished submission.

**Boss's specific advantage:** He already has BrightData MCP integration patterns available through his Jarvis stack. The LinkedIn pipeline (`scripts/linkedin/`) provides direct pattern-reuse for the Talent Intelligence Agent. The FastAPI + Next.js stack is production-ready.

### 7.4 Red Flags

- **Prize pool is modest ($5K cash)** — the real prize is the $20K credits + AI Startup Program fast-track. If Boss cares about cash, this is a $5K opportunity, not a $25K one.
- **Hackathon STARTED TODAY** — Boss is registering mid-stream. Day 1 Kick-off (with $250 credits distribution) may have already happened. Need to check Discord to claim credits.
- **SF onsite advantage** — Onsite teams get mentorship, networking, and direct judge access that online participants don't. Boss is in India, so he's at a structural disadvantage for the onsite judging on May 31. Pure async video submission is the path.
- **No confirmed judge bios** — Can't reverse-engineer what impresses specific judges. Standard lablab.ai criteria apply.
- **Competition level** — lablab.ai hackathons attract 500-2000+ participants. BrightData has been running multiple parallel hackathon campaigns (DEV.to challenge, MLOps Community challenge, this one) — experienced builders are already in the pipeline.
- **No "must be open source" confirmation** — [unverified]. If Boss wants to keep the IP, verify the license requirement on Discord before building.

---

## 8. Top 5 Reference Sources

1. **[Web Data UNLOCKED Hackathon — lablab.ai](https://lablab.ai/ai-hackathons/brightdata-ai-agents-web-data-hackathon)** — Primary source; event page with dates, prizes, format. Returned 403 for direct fetch but full details surfaced via search snippets.

2. **[BrightData MCP GitHub Repository](https://github.com/brightdata/brightdata-mcp)** — Authoritative technical reference. Full tool list, configuration options, pricing tiers, installation instructions. Highest-trust source for tool capabilities.

3. **[BrightData Web MCP Free Tier](https://brightdata.com/blog/ai/web-mcp-free-tier)** — Official BrightData blog. Exact free tier limits (5,000 req/month), tool inclusions, Pro mode activation. Credible first-party source.

4. **[BrightData AI Startup Program](https://brightdata.com/ai/ai-startups-program)** — Official program page. Exact benefits ($20K credits), eligibility (pre-seed to Series A, AI-native), 3-step onboarding, 7-day approval timeline.

5. **[Lablab.ai Hackathon Guidelines](https://lablab.ai/blog/hackathon-guidelines)** — Authoritative submission requirements. 5-min video cap, 300MB limit, GitHub repo required, pitch deck required, live demo URL required.

**Additional sources consulted:**
- [DEV.to BrightData Real-Time AI Agents Challenge](https://dev.to/devteam/join-the-bright-data-real-time-ai-agents-challenge-3000-in-prizes-cog) — parallel BrightData hackathon with overlapping rules structure
- [BrightData Web Unlocker API Docs](https://docs.brightdata.com/scraping-automation/web-unlocker/introduction) — 98% success rate claim, pricing model, exclusions
- [BrightData Scraping Browser](https://brightdata.com/products/scraping-browser) — Playwright/Puppeteer/Selenium integration details
- [BrightData MCP Launch Week Day 1](https://brightdata.com/ai/mcp-server/launch-week/day1) — Tool Groups feature, `geo` group details

---

## Confidence Assessment

**Overall: Medium-High**

- Dates, prizes, format, and credit amounts: **High confidence** (confirmed across 3+ independent search results)
- BrightData tool capabilities and names: **High confidence** (directly from GitHub repo + official docs)
- Judging criteria: **Medium confidence** (lablab.ai standard framework; BrightData-specific weights unconfirmed)
- Judge names: **Low confidence** (not publicly surfaced — check Discord)
- Submission deadline exact time: **Medium** (May 30 EOD PDT strongly implied; IST conversion = May 31 ~12:29 PM IST)
- Team size limit: **Unverified** (lablab.ai standard is 5; this hackathon may differ)
- Open-source license requirement: **Unverified**

**Verify on Discord immediately after registration:** Day-1 credits claim process, exact submission deadline time, judge names, whether additional sponsor tech (OpenAI API credits etc.) is available.
