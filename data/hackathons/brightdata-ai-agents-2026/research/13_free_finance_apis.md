# Free & Open Finance APIs — Comprehensive Catalog

## Quick Answer

17 free/open APIs cover every signal layer: price/OHLCV (yfinance, Tiingo, Polygon), fundamentals (FMP, Alpha Vantage, SEC EDGAR), macro (FRED), news/sentiment (Finnhub, GDELT, NewsAPI), entity (Wikipedia, OpenCorporates, OpenFIGI), insider (OpenInsider, SEC Form 4), crypto (CoinGecko, DefiLlama). Stack in 8 parallel layers per ticker query.

---

## Quick Comparison

| API | Auth | Free Limit | Best Signal | Reliability |
|-----|------|------------|-------------|-------------|
| **yfinance** | None | Unofficial | OHLCV, fundamentals, options | Medium — breaks on Yahoo changes |
| **SEC EDGAR** | User-Agent only | 10 req/sec | 10-K/10-Q/8-K/Form 4 | High |
| **FRED** | Free key | ~120/min | 800K+ macro series | High |
| **Alpha Vantage** | Free key | **25/day**, 5/min | Technicals + fundamentals | Medium |
| **Finnhub** | Free key | 60/min | News, earnings, insider | High |
| **Polygon.io** | Free key | 5/min, 15-min delay | OHLCV | High |
| **Tiingo** | Free key | ~500/hr, 20K/day | Historical OHLCV + news | High |
| **FMP** | Free key | 250/day | Fundamentals, DCF, ratios | Medium-High |
| **NewsAPI** | Free key | 100/day, 24h delay | News headlines | Medium |
| **GDELT** | None | Unlimited | Global news tone + GKG | High |
| **Wikipedia/Wikidata** | None | Polite crawl | Entity, exec bios | High |
| **OpenFIGI** | Optional | Generous | ISIN/CUSIP → ticker | High |
| **OpenCorporates** | Free token | 50/day | Global company registry | High |
| **OpenInsider** | None | Scrape HTML | Insider buys/sells | Medium |
| **CoinGecko** | Demo key | 30/min, 10K/mo | Crypto prices | High |
| **DefiLlama** | None | No stated | DeFi TVL | High |

---

## yfinance

```python
import yfinance as yf
t = yf.Ticker("AAPL")
hist = t.history(period="1y")   # OHLCV DataFrame
info = t.info                    # marketCap, trailingPE, debtToEquity, etc.
fs = t.financials                # income statement annual
chain = t.option_chain("2025-06-20")  # .calls / .puts DataFrames
```

**Key issue:** Breaks 2-3×/year on Yahoo changes. Add `time.sleep(0.5)` between bulk calls. Use as fast primary; fallback to Tiingo on `{}` or 429.

---

## SEC EDGAR

**Must send `User-Agent: "App contact@email.com"`** in every request. 403 if missing. 10 req/sec limit.

```python
import requests, time
HEADERS = {"User-Agent": "MyApp me@example.com"}

def get_xbrl_facts(cik: str) -> dict:
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik.zfill(10)}.json"
    time.sleep(0.125)
    return requests.get(url, headers=HEADERS).json()

# Better: edgartools wrapper
# pip install edgartools
from edgar import Company, set_identity
set_identity("me@example.com")
aapl = Company("AAPL")
filing = aapl.get_filings(form="10-K").latest(1)[0]
form4s = aapl.get_filings(form="4").latest(20)
```

**Key endpoints:**
- `https://data.sec.gov/submissions/CIK{10-digit}.json` — filing history
- `https://data.sec.gov/api/xbrl/companyfacts/CIK{10-digit}.json` — all XBRL facts
- `https://efts.sec.gov/LATEST/search-index?q=...` — full-text search
- Form 4 ATOM: `https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type=4&output=atom`

---

## FRED

```python
from fredapi import Fred
fred = Fred(api_key="YOUR_KEY")

# Key series
cpi = fred.get_series("CPIAUCSL")        # CPI
fed_funds = fred.get_series("FEDFUNDS")  # Fed Funds rate
yield_spread = fred.get_series("T10Y2Y") # 10Y-2Y spread (recession signal)
vix = fred.get_series("VIXCLS")
hy_spread = fred.get_series("BAMLH0A0HYM2")
```

---

## Alpha Vantage (25/day only)

```python
import requests
BASE = "https://www.alphavantage.co/query"
def av_get(function, **kwargs):
    return requests.get(BASE, params={"function": function, "apikey": KEY, **kwargs}).json()

overview = av_get("OVERVIEW", symbol="MSFT")   # P/E, EPS, 52w, target
income = av_get("INCOME_STATEMENT", symbol="MSFT")
news = av_get("NEWS_SENTIMENT", tickers="MSFT", limit=50)
```

Spend 1/25 daily on OVERVIEW only. Cache forever per ticker.

---

## Finnhub (60/min — workhorse)

```python
import finnhub
client = finnhub.Client(api_key=KEY)

news = client.company_news("AAPL", _from="2026-05-01", to="2026-05-25")
earnings = client.company_earnings("AAPL", limit=8)  # surprise %
sentiment = client.stock_insider_sentiment("AAPL", _from="2026-01-01", to="2026-05-25")
recs = client.recommendation_trends("AAPL")
metrics = client.company_basic_financials("AAPL", "all")
quote = client.quote("AAPL")
```

---

## Polygon.io (5/min — tight)

```python
from polygon import RESTClient
client = RESTClient(api_key=KEY)
aggs = client.get_aggs("AAPL", 1, "day", "2026-01-01", "2026-05-25", limit=200)
news = list(client.list_ticker_news("AAPL", limit=20))
```

Cache OHLCV aggressively. Data quality excellent when you hit.

---

## Tiingo (workhorse — high free limit)

```python
from tiingo import TiingoClient
client = TiingoClient({"api_key": KEY, "session": True})

prices = client.get_ticker_price("AAPL", startDate="2026-01-01",
                                  endDate="2026-05-25", frequency="daily")
news = client.get_news(tickers=["AAPL", "MSFT"], limit=30)
```

---

## FMP (250/day)

```python
import requests
def fmp(endpoint, **params):
    params["apikey"] = KEY
    return requests.get(f"https://financialmodelingprep.com/api/v3/{endpoint}",
                        params=params).json()

income = fmp("income-statement/AAPL", limit=4)
ratios = fmp("key-metrics/AAPL", limit=4)
dcf = fmp("discounted-cash-flow/AAPL")
earnings = fmp("earnings-surprises/AAPL")
filings = fmp("sec_filings/AAPL", type="10-K", limit=5)
```

Budget: ~6 calls per brief = 2.4% of daily.

---

## GDELT (unlimited, free, no auth)

```python
from gdeltdoc import GdeltDoc, Filters

gd = GdeltDoc()
f = Filters(keyword="NVIDIA earnings",
            start_date="2026-05-01",
            end_date="2026-05-25",
            num_records=250)

articles = gd.article_search(f)               # DataFrame
timeline = gd.timeline_search("timelinevol", f)  # coverage volume
```

**Best use:** 30-day coverage volume + tone trend. Rising negative tone pre-earnings = bearish.

---

## Wikipedia / Wikidata

```python
# Wikipedia summary
r = requests.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{name}",
                 headers={"User-Agent": "App/1.0 me@example.com"})
summary = r.json().get("extract", "")

# Wikidata SPARQL — CEO, founded, ISIN
SPARQL = """
SELECT ?companyLabel ?ceoLabel ?founded ?isin WHERE {
  ?company wdt:P31 wd:Q6881511;
           rdfs:label "Apple Inc."@en;
           wdt:P169 ?ceo;
           wdt:P571 ?founded;
           wdt:P946 ?isin.
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
"""
```

**Wikidata properties:** P169 CEO · P571 founded · P414 exchange · P946 ISIN · P749 parent

---

## OpenFIGI (V3 endpoint — V2 retires July 2026)

```python
def map_to_figi(id_type: str, id_value: str):
    r = requests.post("https://api.openfigi.com/v3/mapping",
                      json=[{"idType": id_type, "idValue": id_value}],
                      headers={"X-OPENFIGI-APIKEY": KEY})
    return r.json()

# id_type: 'ID_ISIN', 'ID_CUSIP', 'TICKER', 'ID_SEDOL'
result = map_to_figi("ID_ISIN", "US0378331005")
```

---

## OpenInsider + SEC Form 4

```python
from bs4 import BeautifulSoup

def openinsider_ticker(ticker, last_n=30):
    url = f"http://openinsider.com/screener?s={ticker}&sortcol=0&cnt={last_n}"
    soup = BeautifulSoup(requests.get(url, timeout=10).text, "html.parser")
    rows = soup.select("table.tinytable tbody tr")
    trades = []
    for row in rows:
        cells = [td.get_text(strip=True) for td in row.find_all("td")]
        if len(cells) >= 12:
            trades.append({
                "filing_date": cells[1], "trade_date": cells[2],
                "ticker": cells[3], "insider_name": cells[5],
                "title": cells[6], "trade_type": cells[7],
                "price": cells[8], "qty": cells[9],
                "value": cells[12],
            })
    return trades
```

**Cluster buy** (multiple insiders buying same stock short window) = high-conviction signal. Use `openinsider.com/cluster-buys`.

---

## Crypto: CoinGecko + DefiLlama

```python
# CoinGecko
def cg(endpoint, **params):
    params["x_cg_demo_api_key"] = KEY
    return requests.get(f"https://api.coingecko.com/api/v3/{endpoint}", params=params).json()

price = cg("simple/price", ids="bitcoin,ethereum", vs_currencies="usd",
           include_market_cap="true", include_24hr_change="true")
ohlcv = cg("coins/bitcoin/ohlc", vs_currency="usd", days=30)

# DefiLlama (no auth)
protocols = requests.get("https://api.llama.fi/protocols").json()
uniswap = requests.get("https://api.llama.fi/protocol/uniswap").json()
```

---

## The 8-Layer Stacking Recipe

```
Layer 1 — Identity (once, cache forever)
  OpenFIGI: ticker → FIGI + ISIN + exchange (join key)

Layer 2 — Macro (once per session, cache 24h)
  FRED: T10Y2Y, FEDFUNDS, VIXCLS, BAMLH0A0HYM2, CPIAUCSL

Layer 3 — Price + Volume
  PRIMARY: yfinance hist(1y) + fast_info
  BACKUP:  Tiingo daily OHLCV (if yfinance 429/empty)

Layer 4 — Fundamentals (quarterly, cache per earnings)
  FMP:           income-statement + key-metrics + dcf + earnings  [6/250 daily]
  Alpha Vantage: OVERVIEW                                          [1/25 daily]
  SEC EDGAR:     latest 10-K + XBRL facts                          [no cost]

Layer 5 — Insider
  OpenInsider:  last 30 trades (HTML scrape)
  Finnhub:      insider_sentiment (monthly MSPR)
  SEC Form 4:   ATOM feed (authoritative)

Layer 6 — News + Sentiment
  Finnhub:      company_news last 7 days   [60/min]
  GDELT:        30-day tone timeline       [unlimited]
  Tiingo:       curated financial news
  NewsAPI:      fallback                   [100/day]

Layer 7 — Entity Enrichment (once per company)
  Wikipedia REST:   summary paragraph
  Wikidata SPARQL:  CEO, founded, ISIN
  OpenCorporates:   M&A flags only         [50/day]

Layer 8 — Crypto (only if multi-asset)
  CoinGecko:  price + market cap + 24h
  DefiLlama:  TVL trend
```

**Per-brief budget:**
- FMP: 6/250 (2.4%)
- Alpha Vantage: 1/25 (4%)
- SEC EDGAR: 3-4 calls, safe at 8/sec
- FRED: 5 calls, negligible
- Finnhub: 5 calls, negligible at 60/min

**Redundancy:** yfinance primary OHLCV. If 429/`{}` → Tiingo (OHLCV) + FMP (fundamentals). Never block on single source.

---

## Reliability Tiers

| Tier | APIs |
|------|------|
| **Bulletproof** | SEC EDGAR, FRED, Wikipedia, Wikidata, DefiLlama |
| **High** | Finnhub, Tiingo, FMP, Polygon, CoinGecko |
| **Use with fallback** | yfinance (Yahoo changes), GDELT (burst slow) |
| **Sparingly (tight limits)** | Alpha Vantage 25/day, NewsAPI 100/day, OpenCorporates 50/day |
| **Skip** | Intrinio (sandbox = synthetic data) |

---

## Sources

- [SEC EDGAR API Guide 2026](https://tldrfiling.com/blog/sec-edgar-api-guide/)
- [edgartools GitHub](https://github.com/dgunning/edgartools)
- [FRED API Docs](https://fred.stlouisfed.org/docs/api/fred/)
- [Alpha Vantage Guide 2026](https://alphalog.ai/blog/alphavantage-api-complete-guide)
- [Finnhub Rate Limits](https://finnhub.io/docs/api/rate-limit)
- [Polygon Python Client](https://github.com/polygon-io/client-python)
- [tiingo-python](https://github.com/hydrosquall/tiingo-python)
- [FMP Free Docs](https://site.financialmodelingprep.com/developer/docs)
- [GDELT Project](https://www.gdeltproject.org/)
- [gdeltdoc](https://github.com/alex9smith/gdelt-doc-api)
- [OpenFIGI API](https://www.openfigi.com/api/overview)
- [OpenInsider](http://www.openinsider.com/)
- [CoinGecko API](https://www.coingecko.com/en/api)
- [DefiLlama API](https://api-docs.defillama.com/)
- [Best Financial Data APIs 2026](https://www.nb-data.com/p/best-financial-data-apis-in-2026)
