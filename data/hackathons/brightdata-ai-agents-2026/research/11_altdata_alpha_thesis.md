# Alt-Data Alpha Thesis — Research Brief

**For:** BrightData × lablab.ai "Web Data UNLOCKED" Hackathon · Alt-Data Investment Brief Agent

---

## Executive Summary

- Alt-data is real, growing — credible 2024 baseline ~$11B, $2.5B+ specifically buy-side, 30-40% CAGR → ~$13-21B by 2026. Variation wide; treat any single figure with skepticism.
- Across 7 core signal families, only **3 have replicated peer-reviewed alpha:**
  1. Opportunistic insider trades (Cohen-Malloy-Pomorski 2012 → ~82 bps/month abnormal)
  2. Satellite parking-lot counts vs retailer comp-sales (Berkeley/Kentucky study)
  3. Glassdoor employee-rating CHANGES (Green-Huang-Wen-Zhou 2019 JFE)
- Rest (Reddit/WSB, Google Trends, hiring, web traffic) show mixed / regime-dependent / vendor-claimed alpha that decays after public exposure.
- Bloomberg moat ($24K-32K/seat/year) attacked at 3 price points — Koyfin/Fiscal.ai ($39-79/mo), Quiver Quant ($12.50-25/mo), free-tier scraped (our zone).
- **Output spec implication:** foreground 3 high-replication signals. Demote weaker/buzzier signals (Reddit volume, WSB mentions, Trends spikes) to "Crowd Buzz — interpret with caution" depth tab. This is the differentiator vs Quiver's flat-table approach.

---

## Industry Map

**Market size (2024 → 2026):**

| Source | 2024 | 2026 | Notes |
|---|---|---|---|
| TenderAlpha (AltData.org) | ~$11B | — | Broadest, +$1.7B in 12 mo |
| Coalition Greenwich (buy-side) | $2.5B+ | — | Investment mgmt only |
| Future Market Insights | — | $5.2B | Conservative |
| KBV Research | — | $11.1B | — |
| Business Research Co. | — | $13.45B | 39.7% CAGR |
| Mordor Intelligence | — | $17.78B | — |
| Precedence Research | — | $21.61B | Most aggressive |

**Pitch line:** "$10B+ category growing 30-40% CAGR" — anything more precise invites fact-check fight.

**Eagle Alpha taxonomy:** 16 primary categories, 56 sub-categories, 2,000+ vendor datasets — consumer transaction, app usage, social media, geo-location, satellite, web-scraped, ESG, sentiment, weather, hiring/HR, pricing, public records, IoT, advertising, B2B, crowd-sourced.

**Adoption:**
- 85% leading hedge funds use ≥2 alt-data sets; 54% use ≥7
- 63% of investors plan to increase alt-data spend in 2025 (driven by gen-AI cheaper ingestion)
- Hedge funds = ~70% revenue share (2021)

**Why-now narrative:** Same gen-AI wave letting big funds ingest more alt-data lets retail-side agent compete. Marginal cost of parsing 10K Reddit posts / 100 SEC filings collapsed. Institutional spend rising, retail still locked out — that gap is what our agent monetizes.

---

## Commercial Provider Landscape

| Provider | Category | Pricing |
|---|---|---|
| **Yipit Data** | E-comm + transaction | Not published; "most expensive." 150+ HF clients. |
| **Orbital Insight** (Privateer) | Satellite/geospatial | Custom-quote |
| **RS Metrics** | Satellite retail/mining | Custom; Bloomberg EAP |
| **Thinknum** | Web-scraped (hiring, headcount) | Custom-quote enterprise [unverified] |
| **Earnest Analytics** | Transaction/receipt | Custom; row-level feed |
| **SimilarWeb** | Web + app traffic | Enterprise custom |
| **Vortexa** | Commodity flows (AIS) | Custom; 99% waterborne oil/gas/LNG |
| **Kpler** | Commodity + analytics | Custom; ICE Developer Portal |
| **Quiver Quantitative** | Retail-tier omnibus | **Free | $12.50-25/mo | $300/yr** |

Institutional providers have no public pricing — TAM is ~3,000 hedge funds, they price-discriminate per logo. Retail-tier (Quiver) is where pricing is transparent.

---

## Documented Alpha Signals — Signal-to-Citation Table

**LOAD-BEARING TABLE for pitch.**

| # | Signal | Strength | Headline finding | Source |
|---|---|---|---|---|
| 1 | **Opportunistic insider trades (SEC Form 4)** | **STRONG** (JoF) | After stripping ~50% "routine" trades, opportunistic portfolio earns ~82 bps/month abnormal return | Cohen-Malloy-Pomorski, Journal of Finance 2012 |
| 2 | **Satellite parking-lot car counts** | **STRONG** (peer-reviewed) | YoY Δ in store-level car counts reliably predicts quarterly comp-sales for 44 major US retailers (2011-17) | Katona-Painter-Patatoukas-Zeng — UC Berkeley/Kentucky |
| 3 | **Glassdoor rating CHANGES** | **STRONG** (JFE) | Δ in employee ratings predicts one-quarter-ahead earnings surprises. 1M+ reviews, 1,200+ firms, 2008-16. | Green-Huang-Wen-Zhou, JFE 2019 |
| 4 | **Reddit/WSB sentiment & volume** | **MIXED → DECAYED** | Bradley 2021: pre-GameStop alpha. Bradley 2024: post-GameStop alpha vanished. | Bradley 2021/2024; Lyócsa 2022 |
| 5 | **Google Trends search volume** | **WEAK-MEDIUM** | "Now-cast" not "forecast." Choi-Varian 2012: improves nowcasts of auto sales, claims, travel. Stock-direction mixed. | Choi-Varian, Economic Record 2012 |
| 6 | **LinkedIn hiring / Thinknum jobs** | **MEDIUM** (vendor-claimed) | Thinknum positions as leading indicators. No peer-reviewed replication found. | Thinknum case studies |
| 7 | **Oil tanker AIS (Vortexa/Kpler)** | **MEDIUM** (vendor-claimed) | Both claim early supply-demand signal ahead of public balances. No peer-reviewed academic [unverified]. | Vortexa/Kpler materials |
| 8 | **Web traffic (SimilarWeb)** | **VENDOR-CLAIMED** | 96% R² between digital metrics and reported KPIs. No independent peer-review found. | SimilarWeb materials |

**Hard truth:** Of 8 most-marketed categories, only 3 have peer-reviewed alpha. Everything else is vendor case-study OR decayed post-publication. Our agent must communicate this hierarchy honestly — that's the moat vs Quiver (which displays signals as equal-weight).

---

## Feature-Engineering Recipes

1. **Opportunistic insider trades** — classify each Form 4 filer ROUTINE (predictable cadence) vs OPPORTUNISTIC (irregular). Long-only signal = portfolio of stocks with recent opportunistic *buys* by C-suite/10%-owners, weighted by $ value + filer rank.
2. **Satellite parking** — YoY % Δ store-level car-count per retailer, aggregated chain-level weighted by store revenue, vs analyst consensus comp-sales. Signal = (satellite estimate − consensus) standardized.
3. **Glassdoor** — Δ(avg rating) over 90-day rolling vs trailing 12-month baseline; weight by reviewer tenure + review length.
4. **Reddit/WSB** — NOT raw count. Compute: post volume z-score (90-day baseline), sentiment-weighted volume, novelty (first-mention vs sustained). Apply *short* horizon (1-5 day) only; long-horizon alpha negative post-2021.
5. **Google Trends** — De-trend, de-seasonalize, z-score; use as nowcast feature, not standalone signal.
6. **LinkedIn/Thinknum hiring** — net new postings 30d vs 90d baseline, function mix shift (eng vs sales — sales-heavy = growth phase), wage trajectory.
7. **Tanker AIS** — vessel count near loading/discharge ports + cargo-mass + days-at-sea (floating storage proxy). Aggregate to supply-demand vs 5-yr seasonal.
8. **Web traffic** — De-seasonalize, normalize vs category baseline, regress on prior-Q reported revenue → forecast model → flag deltas vs analyst consensus.

**Hackathon constraint:** Only (1), (3), (4), (5) realistically scrapeable free (SEC EDGAR, Glassdoor scrape, Reddit API, Google Trends API). (2), (7), (8) need paid feeds or proprietary imagery.

---

## Bloomberg Substitution Narrative

**Bloomberg's moat & price:**
- 2026: **$24K-$31,980/seat/year** depending on source; 10+ seat tiers ~$18K-25K. 2-year minimum contract.
- ~325K terminals globally [unverified 2026]
- Moat: real-time data + IB chat + regulatory + ESG content + depth of reference data + *the screen everyone else uses*

**Disruptor ladder:**

| Tier | Product | Price | Pitch |
|---|---|---|---|
| Enterprise AI | **AlphaSense** | Several $K/year | AI search across filings/transcripts |
| Pro analyst | **Koyfin** | Free / $39/$79 mo | Bloomberg-grade charts at 5% price. 500K+ users |
| AI-conversational | **Fiscal.ai** (FinChat) | Freemium → SMB | Conversational; 350K+ retail, 70+ institutions, $10M Series A |
| Retail alt-data | **Quiver Quantitative** | Free / $12.50-25 mo / $300/yr | Congress trades + 30 alt datasets |
| Free indie | Wallmine, Stockbeep, Stockanalysis | Free / freemium | Surface fundamentals |

**Hackathon wedge:** Every tier above except Quiver presents data as *tables*. Conversational + source-cited + signal-hierarchy-aware briefs are white-space. Fiscal.ai is only direct competitor moving there — weakness = closed garden, no transparent reasoning trace.

**Pitch line:** *"Bloomberg charges $24K/year and won't show you its sources. We're free, conversational, and every claim links to the filing."*

---

## Retail Alt-Data Products — Honest Assessment

- **Quiver Quantitative** — strongest retail alt-data; 30+ datasets. Weakness: flat dashboard, no signal-strength weighting, no narrative synthesis, no LLM layer.
- **Wallmine** — fundamentals + insider aggregator; minimal alt-data
- **Stockbeep** — unusual options/volume screener; not really alt-data
- **Stockanalysis.com** — clean fundamentals; no alt-data layer

**Common weakness:** None *interpret* signals. Display raw data, retail user left to figure out what an "$2M insider buy" or "400% WSB spike" means. This is the bridge our agent crosses.

---

## Signal Hierarchy for Our Agent Output

### Tier A — Headline (always shown, citation-required)

1. **Insider activity** — opportunistic Form 4 buys/sells last 30 days, classified per Cohen-Malloy-Pomorski. Show ticker, role, $ value, classification. **Confidence: HIGH.**
2. **Employee sentiment trajectory** — Glassdoor rating Δ rolling 90d vs trailing 12-mo, weighted by length. **Confidence: HIGH** (peer-reviewed JFE).
3. **Satellite/foot-traffic proxy** — if accessible via free scrape (Placer marketing pages, Google Maps "popular times"), show; else mark "Premium-only — see RS Metrics." **Confidence: HIGH** where available.

### Tier B — Secondary insights tab (with caveat)

4. **Hiring trajectory** — LinkedIn/Indeed/Greenhouse job-posting Δ + role mix shift. **Confidence: MEDIUM.**
5. **Web traffic proxy** — SimilarWeb public / Wikipedia pageview Δ. **Confidence: MEDIUM.**

### Tier C — Crowd buzz depth tab (explicit "interpret with caution")

6. **Reddit/WSB mentions** — volume z-score over 90-day baseline (NOT raw count), sentiment-weighted. Label: "Short-horizon attention signal. Predictive power for >5-day returns has decayed post-2021." **Confidence: LOW** swing, **MEDIUM** day-trade liquidity.
7. **Google Trends** — z-score, de-trended. As "nowcast" feature, not return predictor. **Confidence: LOW** direct return.
8. **Congressional trades** — within 45-day disclosure lag, flag "Disclosed with delay, may already be priced in." **Confidence: LOW-MEDIUM.**

### Tier D — Footer / cite-source row

Every signal carries a "Why we show this" tooltip linking to the academic paper or vendor methodology. **The moat vs Quiver Quant.**

---

## Counter-View (Steel-Manned)

Strongest argument against premise: **alt-data alpha is a Red Queen game** — once a signal is documented in JFE/JoF + commercialized, arbitraged away in 3-5 years. Bradley 2024 WSB decay is canonical. Even Cohen-Malloy-Pomorski's 82 bps was a 2012 sample; 2018-24 out-of-sample likely shows decay [unverified magnitude]. Skeptic argues we'd show users *historically-proven* signals that no longer work, with false patina of "academic rigor."

**Defense:**
- We show signal *change*, not raw — change harder to arbitrage
- Explicitly label confidence + decay risk
- Value is *synthesis and interpretation*, not single edge — degraded signals stacked with citations still beat "trust me bro" tips

---

## Open Questions

1. Free-tier data: what's scrapeable inside BrightData MCP without ToS crossing? (SEC Form 4 yes, Glassdoor grey, Reddit yes, X paid, LinkedIn ToS-blocked.)
2. Decay calibration: backtest Tier-A signals on 2022-25 data in-hackathon for live R² OR cite 2012/2019 papers with disclaimer?
3. Latency vs depth: <10s answers (forces caching) or willing to wait 60s for fresh scrape?

---

## Recommended Next Actions

- **Tier-A MVP first:** Form 4 insider parser (EDGAR is easiest data on earth) + Glassdoor scrape + Reddit volume z-score. 3 cited signals in a day.
- **Tier-B via BrightData MCP:** SimilarWeb public, LinkedIn job-postings, Google Trends API.
- **Citation engineering:** every signal in output carries JSON `source: {paper_title, authors, year, journal, url}`. Moat = clickable citations.
- **Pitch headline:** *"Bloomberg charges $24K/year and won't show its sources. We're free, conversational, and every signal links to the peer-reviewed paper."*

---

## Sources

- [Cohen, Malloy, Pomorski — Decoding Inside Information](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1692517)
- [Green, Huang, Wen, Zhou — Crowdsourced Employer Reviews and Stock Returns](https://www.sciencedirect.com/science/article/abs/pii/S0304405X19300662)
- [Berkeley Haas — Satellite Parking Lot Study](https://newsroom.haas.berkeley.edu/how-hedge-funds-use-satellite-images-to-beat-wall-street-and-main-street/)
- [Choi & Varian — Predicting the Present with Google Trends](https://people.ischool.berkeley.edu/~hal/Papers/2011/ptp.pdf)
- [Coalition Greenwich — Alt-Data 2025 AI Revolution](https://www.greenwich.com/market-structure-technology/alternative-data-2025-fueling-ai-driven-investment-revolution)
- [Eagle Alpha — What is Alternative Data](https://www.eaglealpha.com/what-is-alternative-data/)
- [Bloomberg Terminal Cost 2026 — CostBench](https://costbench.com/software/financial-data-terminals/bloomberg-terminal/)
- [Koyfin — Bloomberg Alternatives](https://www.koyfin.com/blog/best-bloomberg-terminal-alternatives/)
- [Quiver Quantitative](https://www.quiverquant.com/)
- [Future Market Insights — Alt Data](https://www.futuremarketinsights.com/reports/alternative-data-market)
- [Mordor Intelligence — Alt Data](https://www.mordorintelligence.com/industry-reports/alternative-data-market)
