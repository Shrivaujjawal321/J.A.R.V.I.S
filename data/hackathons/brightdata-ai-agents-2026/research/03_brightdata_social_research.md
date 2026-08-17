# BrightData Social + Research Tools — Investment Signal Extraction

## Quick Answer
7+ directly relevant scrapers for alt-data: Reddit (4 variants), X/Twitter (6 endpoints), StockTwits (native bull/bear labels — highest signal), News Scraper, Reuters, Wikipedia, GitHub, Hacker News. Sentiment is raw text — FinBERT batch + Claude Haiku is recommended extraction stack. Volume spike via client-side rolling Z-score.

---

## Reddit Scraper

**Variants:** by subreddit URL, keyword search, author, batch.

```json
{
  "post_id", "url", "user_posted", "title", "description",
  "num_comments", "num_upvotes", "date_posted", "tag",
  "community_name", "community_rank",
  "related_posts", "comments"
}
```

**Ticker filtering:** Not server-side. Pass `"$NVDA OR NVIDIA"` as keyword.
**Pricing:** $1.50/1K PAYG | $499/mo for 384K base.

---

## X / Twitter Scraper

**Endpoint:** `POST /datasets/v3/scrape` with `dataset_id: "gd_lwxkxvnf1cynvib9co"`

```json
{
  "post_id", "url", "user_posted", "name", "description", "date_posted",
  "replies", "reposts", "likes", "views",
  "external_urls", "hashtags", "photos", "videos"
}
```

**Cashtag search:** Pass `https://twitter.com/search?q=%24NVDA&f=live` as input URL.
**MCP integration available** — directly relevant to hackathon agentic architecture.

---

## News Scrapers

**General News** (BBC, CNN, Google News, Yahoo Finance):
```json
{ "id", "url", "headline", "author", "topics", "date_published", "db_source" }
```

**Yahoo Finance**: Returns `stock_ticker` natively — highest-fidelity news-to-ticker mapping.

**MarketWatch / Seeking Alpha [unverified]:** No dedicated scrapers. Use Web Unlocker.

**Deduplication:** Implement MinHash on normalized headlines within 4-hour window.

---

## Wikipedia Scraper

**Fields:** article text, links, categories. Bulk: 5,000 URLs/batch.

**Investment use:** Entity enrichment layer. Pull `https://en.wikipedia.org/wiki/NVIDIA` → founding year, HQ, revenue history, executives. Critical for company name disambiguation ("Apple" → `AAPL`).

---

## GitHub Scraper

**Schema:** `url, repo_id, language, stars, forks, watchers, contributors, commits`

**Investment signals:** Star velocity, issue ratio, contributor growth, commit frequency. Useful for tech-heavy companies (NVDA CUDA, MSFT Copilot, META PyTorch).

**Limitation [unverified]:** Point-in-time snapshots. Schedule daily + compute deltas.

---

## StockTwits Scraper

**Schema:** `ticker, message, sentiment ("Bullish"/"Bearish"/null), timestamp, user_profile, likes, replies, trending_tickers`

**Key advantage:** Users self-label posts as bullish/bearish at post time. `sentiment` populated natively — **no NLP required for directional signal**. `trending_tickers` = built-in volume spike indicator. **Highest signal-to-noise source in the catalog.**

---

## Hacker News Dataset

Managed custom dataset. Use for enterprise tech adoption sentiment — AI frameworks, cloud provider health, developer tooling relevant to public companies.

---

## Ticker Mention Detection

**Step 1 — Cashtag regex (Twitter/StockTwits):**
```python
CASHTAG_RE = re.compile(r'\$([A-Z]{1,5})\b')
tickers = CASHTAG_RE.findall(text)
```
Precision ~95%.

**Step 2 — NER + disambiguation (Reddit/News):**
1. Run `dslim/bert-base-NER` → extract ORG entities
2. Match against company_name → ticker lookup with fuzzy matching
3. Disambiguate using 10-token context window
4. Normalize to `EXCHANGE:TICKER`

---

## Sentiment Scoring Options

| Method | Accuracy | Latency | Cost | Best For |
|---|---|---|---|---|
| **StockTwits native label** | user-labeled | 0ms | Free | StockTwits posts |
| **VADER** | ~56% on fin. text | 0.5ms/text | OSS | High-freq pre-filter |
| **FinBERT** (`ProsusAI/finbert`) | ~93% F1 | 50-200ms/text | $0.003-0.01/1K | News headlines |
| **Claude Haiku** | Best on nuance | 500ms-2s/call | ~$0.25/1M tokens | Brief synthesis |

**Recommended hackathon stack:**
- StockTwits → native label (no NLP cost)
- Reddit/X → VADER pre-filter (abs > 0.3) → FinBERT batch on GPU
- News → Claude Haiku (nuance required)
- Final brief → Claude Sonnet

---

## Volume Spike Detection

- 30-day rolling window of daily mention counts
- 7-day rolling sum current vs prior
- W/W % change: `(current - prior) / prior * 100`
- Z-score: `(today - mean_30d) / std_30d`
- **Spike threshold:** Z > 2.0 OR W/W > 40%
- **Velocity:** Rank position change > absolute count (#50 → #5 = stronger than holding #1)

---

## Influencer Weighting

```python
follower_score = log10(max(followers, 10)) / 7.0
verified_bonus = 0.2 if verified else 0.0
weight = min(1.0, follower_score + verified_bonus)
# Bio keywords (CFA, analyst, PM): +0.1
```

Engagement rate as resonance proxy: `(likes + reposts) / max(followers, 1)`.

---

## Gaps — Build Yourself

| Gap | Build Plan |
|---|---|
| Ticker-level aggregation | Extract → bucket → aggregate per ticker per time window |
| Cross-source news dedup | MinHash on headline within 4h window |
| Volume spike alerts | Rolling Z-score (DuckDB) |
| Historical baseline | Store daily mention counts every run |
| Real-time streaming | BrightData is pull-only; poll every 5-15 min |
| Author credibility | Build from scraped `followers + verified` fields |

---

## MCP Integration

BrightData MCP free tier: 5,000 req/month, auto-renews. Exposes social media as JSON tool calls. **Use MCP-first** — eliminates dispatch overhead, keeps agent loop clean. Supports ~50 ticker runs at 100 req each.

---

## Sources

- [Reddit Scrapers Docs](https://docs.brightdata.com/scraping-automation/web-scraper-api/social-media-apis/reddit)
- [Twitter API Scrapers](https://docs.brightdata.com/api-reference/web-scraper-api/social-media-apis/twitter)
- [StockTwits Scraper](https://brightdata.com/products/web-scraper/stocktwits)
- [Wikipedia Scraper](https://brightdata.com/products/web-scraper/wikipedia)
- [GitHub Scraper](https://brightdata.com/products/web-scraper/github)
- [MCP Server for Social Media](https://brightdata.com/ai/mcp-server/social-media)
- [WSB Sentiment Methodology — SwaggySocks](https://swaggystocks.com/dashboard/wallstreetbets/how-it-works)
- [FinBERT Paper](https://arxiv.org/pdf/1908.10063)
- [LLMs for Financial Sentiment 2025](https://arxiv.org/pdf/2510.15929)

**Confidence: Medium-High** — Schema fields cited directly from product pages.
