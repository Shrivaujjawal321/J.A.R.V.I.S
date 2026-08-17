# Competitor Landscape — Web Data UNLOCKED Hackathon

## Quick Answer

3 prior BrightData hackathon waves (Dec 2024, May 2025, Aug 2025) → highly predictable patterns. ~60-70% of builds = monitoring dashboards, news aggregators, brand/social listeners. **Finance submissions exist but universally shallow** — single-source text summarizers with BUY/SELL tags, no structured output, no alt-data. **Zero confirmed submission in ANY prior BrightData event has combined satellite imagery + web alt-data + multi-source financial synthesis. That gap is our moat.**

---

## Submission Table (18 Proxy Submissions)

| Project | Archetype | Tech | Notes |
|---------|-----------|------|-------|
| **Reputato** | Company OSINT | LinkedIn/Glassdoor/Crunchbase + LLM | $3K winner May 2025. Output = 1-5 "potato" rating |
| **SOC-CERT** | Cybersec feed | n8n + BrightData + CISA/OTX + Slack | $1K Aug 2025. 100+ CVEs/day |
| **BrandGuard AI** | Brand monitoring | n8n + BrightData + Slack + dashboard | $1K Aug 2025 |
| **Event Butler** | Event aggregator | n8n + BrightData + Eventbrite + Gemini | $1K Aug 2025. Classic archetype |
| **Release Sentinel** | DevOps monitoring | n8n + BrightData + 18+ vendors | $1K Aug 2025 |
| **Pixie** | Voice → website | n8n + BrightData + Lovable.dev + voice | $1K Aug 2025. Creative outlier |
| **Cheaperr** | Price comparison | JS + BrightData + Amazon/eBay/AliExpress | $1K Dec 2024. Textbook |
| **Tech Trend Tracker** | News summarizer | Python + BrightData + Reuters | $1K Dec 2024 |
| **Reddit Recap** | Social summarizer | Scraping + AI → audio briefings | $1K Dec 2024 |
| **Industry AI Watchdog** | BI dashboard | Deno + Fresh + OpenAI + BrightData | Custom KPI indices |
| **Wall Street Sentiment** | Finance — sentiment | n8n + BrightData + Gemini + X | Output = "word summary." Extremely shallow |
| **Startup Funding Monitor** | Finance — funding | n8n + BrightData + GPT-4 mini + Slack | 30-min cron, alert-only |
| **Financial Signals Dashboard** | Finance — stock signals | Strands Agents + BrightData MCP + Streamlit | **Most complete finance sub found.** BUY/SELL + RSI. Single-ticker, no alt-data |
| **Equity Fundamental Octo Researcher** | Finance — RAG | n8n + BrightData + Docling + Pinecone + Claude | India-only, RAG on filings, no macro/alt-data |
| **VEIN.intel** | GTM/sales intel (this event) | BrightData + hiring + SaaS pricing | B2B SaaS focus — not finance |
| **TrapScan** | AI agent security (this event) | BrightData + Gemma 4 + browser | Detects prompt injections |
| **LaunchPilot AI** | GTM strategy | BrightData SERP + Claude | B2B SaaS, GTM enterprise-ready |

---

## Saturation Zones

- **Zone A (~30%):** "Streamlit + 3 URLs + GPT." 3 news/social sources, BrightData SERP, GPT-4o summary, Streamlit. All identical after 50th. No agent loop, no synthesis, no confidence.
- **Zone B (~20%):** n8n workflow screenshots. Aug 2025 DEV challenge specifically rewarded n8n; this event's rubric doesn't. Expect lower scoring here.
- **Zone C (~15%):** Lead gen / LinkedIn / recruiter tools. Reputato set template; dozens of copycats.
- **Zone D (~10%):** Finance news summarizers with BUY/SELL tags. Wall Street Sentiment + Startup Funding Monitor archetype. All stop at "collect + tag sentiment."
- **Zone E (~10%):** Price comparison / e-commerce. Cheaperr template. Table stakes.

---

## White Space (Underrepresented)

- **W1: Multi-layer alt-data synthesis for investment decisions [HIGH].** No prior BrightData submission combined: web-scraped filings + news sentiment + non-text signals (satellite, app downloads, job velocity). Financial Signals Dashboard closest but text-only single-ticker.
- **W2: Structured investment brief output format [HIGH].** All finance subs output Slack messages, emails, charts. None produce formatted investment-memo a fund analyst could use. Output format = differentiator.
- **W3: Claude Vision + Satellite as named capability [HIGH novelty].** Satellite imagery via Claude Vision + web-scraped financial data appears in Orbital Insight/SpaceKnow but **never as a hackathon submission** in any lablab/DEV event indexable. Confirmed white space.
- **W4: Temporal signal tracking — change over time [MEDIUM].** All submissions point-in-time. None track "hiring at X up 40% MoM vs competitor Y cutting → divergence signal." How real alt-data platforms operate.
- **W5: Portfolio-level cross-company view [MEDIUM].** All prior finance subs analyze one company/sector at a time.

---

## Finance Submission Failure Mode Analysis

| Submission | Strength | Critical Gap |
|------------|----------|--------------|
| Financial Signals Dashboard | Best tech; Streamlit polish; BrightData MCP | Single-ticker, text-news-only, no alt-data, no structured output |
| Equity Fundamental Octo | RAG on actual filings; Claude Q&A | India-only, no macro, no satellite |
| Wall Street Sentiment | Multi-source (X + news) | Output = "summary for a blog." Not actionable |
| Startup Funding Monitor | Structured entity extraction | Monitoring/alert only, no analysis |
| Industry AI Watchdog | Custom KPI indices | No finance signals, no actionable output |

**Common pattern:** All stop at "collect + summarize." None execute the synthesis: raw data → investment decision framework. That jump is where all prior finance subs fall off.

---

## Satellite + Web Scraping + Finance — Prior Art Scan

**Academic:** SAIFIN (MDPI, Feb 2026). Multi-agent trading fusing OHLC + news sentiment + satellite indicators. Master Agent coordinating Market/News/Satellite domain agents. [Source](https://www.mdpi.com/2571-9394/8/1/17). No GitHub repo. Academic, not applied.

**Hackathon prior art:** **ZERO.** Exhaustive search across lablab.ai, DEV.to brightdata/n8nbrightdata tags, GitHub topics, hackathon DBs found **no submissions combining satellite imagery + web scraping + financial investment** in any hackathon context.

---

## Quality Bar — Winners

Based on 9 confirmed winners across 3 BrightData challenges:

- **UI:** 3/5 Aug 2025 winners = n8n chat or Slack bot. Winners with custom frontends stood out. Working Streamlit or React = top 20%.
- **Demo:** 2-4 min Loom-style narrated screen recording with live agent. No cinematic editing. Separates top submissions.
- **README:** Structured: problem + architecture diagram + setup + example outputs. Architecture diagram = top quartile table stakes.
- **Code:** Clean GitHub repo with actual agent code scores above n8n-only JSON gists.

---

## 2×2 Positioning Map

```
                    HIGH NOVELTY
                         |
        SAIFIN (academic)|  *** OUR PROJECT ***
        satellite trading|  Alt-Data Investment Brief
             signals     |  Claude Vision + Satellite
                         |  + Multi-source Web Alt-Data
                         |  + Structured Brief Output
                         |
LOW TECHNICAL ───────────┼─────────────── HIGH TECHNICAL
DEPTH                    |                 DEPTH
                         |
  Wall Street Sentiment  |  Financial Signals Dashboard
  (email digest)         |  (Streamlit, RSI/MA, one ticker)
                         |
  "Scrape 3 URLs + GPT"  |  Equity Fundamental Octo
  news summarizer        |  (RAG on filings)
                         |
                    LOW NOVELTY
```

Top-right is uncrowded. Only academic competitor. Crowded quadrant (bottom-left) is where 40-50% of submissions cluster.

---

## Positioning Recommendation

**Own:** "The first Alt-Data Investment Brief agent that sees what traditional data can't."

While every other finance submission reads same Reuters/Yahoo text Bloomberg already shows, this agent reads:
1. Satellite imagery — parking lots, container yards, construction (via Claude Vision)
2. Job posting velocity as hiring signal (BrightData LinkedIn/Indeed)
3. Consumer sentiment Reddit/product reviews (BrightData SERP)
4. Web-scraped supply chain (shipping rates, port congestion)

Synthesizes into structured investment brief — not Slack message, not chart, but **document a fund analyst would recognize**.

**Do NOT:**
- Another "summarize 3 news URLs"
- Slack/email digest as primary deliverable
- Only publicly available price/news data
- UI as centerpiece

**DO:**
- Name specific non-obvious sources (which BrightData datasets, which satellite API)
- Show synthesis step explicitly — not just collection
- Produce structured output: bull/bear thesis, signals section, confidence, source attribution
- Live demo multi-step agent chain in video
- Cite SAIFIN in README — signals domain awareness

**Risk:** Financial Signals Dashboard archetype (Streamlit + BrightData MCP + multi-indicator) is closest competitor. Differentiation via: (a) satellite as novel non-text signal, (b) structured brief format vs chart output, (c) multi-company/portfolio vs single-ticker.

---

## Trade-offs

- Satellite adds technical complexity — needs satellite API (Planet/Sentinel Hub/NASA GIBS free). Building Claude Vision parsing in 5 days is ambitious. **Fallback:** Use pre-existing dataset OR mock satellite signal with parking-lot proxy from Google Maps historical.
- If satellite too heavy by May 31: W2 (structured brief format) + W4 (temporal tracking) alone still differentiate from every finance submission found.
- n8n probably wrong here — lablab audiences + judges are agent-framework native. LangGraph / CrewAI / Claude SDK reads as more serious.

---

## Sources

- [DEV BrightData May 2025 — Reputato](https://dev.to/devteam/congratulations-to-the-winner-of-the-bright-data-real-time-ai-agents-challenge-h92)
- [DEV n8n + BrightData Aug 2025 Winners](https://dev.to/devteam/congrats-to-the-winners-of-the-real-time-ai-agents-challenge-powered-by-n8n-and-bright-data-104c)
- [DEV Web Scraping Challenge Dec 2024 Winners](https://dev.to/devteam/congrats-to-the-bright-data-web-scraping-challenge-winners-46nf)
- [Financial Signals Dashboard — DEV](https://dev.to/aws-builders/financial-signals-dashboard-ai-powered-stock-analysis-with-bright-data-mcp-server-strands-agents-11ed)
- [Equity Fundamental Octo — DEV](https://dev.to/bikash119/equity-fundamental-octo-researcher-next-gen-stock-research-3a4n)
- [Wall Street Sentiment — DEV](https://dev.to/indika_wimalasuriya/i-built-an-ai-agent-that-reveals-wall-street-sentiment-in-seconds-4ma2)
- [Web Data UNLOCKED Hackathon](https://lablab.ai/ai-hackathons/brightdata-ai-agents-web-data-hackathon)
- [SAIFIN paper — MDPI](https://www.mdpi.com/2571-9394/8/1/17)
- [BrightData Alternative Data in Finance](https://brightdata.com/use-cases/financial)

**Confidence: Medium-High** — Prior-event corpus 18 confirmed submissions. Saturation % inferred from pattern. "Zero satellite hackathon" finding from exhaustive negative search.
