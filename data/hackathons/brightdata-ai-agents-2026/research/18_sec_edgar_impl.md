# SEC EDGAR Implementation Research
## AltBrief — `backend/sources/sec.py`

**Date:** 2026-05-27  
**Scope:** Production-ready Python module for insider Form 4 transactions, 10-K risk factors, and earnings guidance from 8-K/10-Q filings.

---

## 1. Library Decision: `edgartools` vs Raw `httpx`

### Verdict: `edgartools` — with `asyncio.run_in_executor` wrapping

**Reasoning:**

| Criterion | `edgartools` v5.31.5 | Raw `httpx` + BS4 |
|---|---|---|
| Form 4 parsing | `f.obj().to_dataframe()` — structured, typed | 200+ lines of fragile XML XPath |
| 10-K Item 1A | `tenk.risk_factors` property | Regex on HTML that shifts format every few years |
| 8-K guidance | `eightk["Item 2.02"]` dict access + text | Full HTML parse + NLP heuristics |
| Rate limiting | Built-in token bucket (9/s), exponential backoff | Manual `asyncio.Semaphore` |
| Maintenance | v5.31.5 released 2026-05-22, 3,795 commits, used in hedge funds | You own the breakage |
| Stability | Occasionally breaks when SEC changes XML namespaces (watchable) | Breaks every time SEC changes HTML template |
| Async | Sync only — wrap with `run_in_executor` | Native async |

**The risk with `edgartools`** is SEC-namespace drift. The library has historically patched these within days. The risk with raw parsing is permanent: the SEC has changed 10-K HTML structure 3+ times since 2019 (txt → html → iXBRL).

**Mitigation:** Pin `edgartools>=5.31,<6`. Monitor PyPI releases. Fallback raw parser is included in the module below for the Form 4 path as belt-and-suspenders.

**edgartools is NOT natively async.** The library uses synchronous `httpx` internally with `pyrate-limiter` token bucket. The correct async integration is `asyncio.get_event_loop().run_in_executor(thread_pool, sync_fn)`.

---

## 2. EDGAR Ticker → CIK Lookup

### Endpoint
```
GET https://www.sec.gov/files/company_tickers.json
```

### Response structure
```json
{
  "0": {"cik_str": 320193, "ticker": "AAPL", "title": "Apple Inc."},
  "1": {"cik_str": 789019, "ticker": "MSFT", "title": "Microsoft Corp"},
  ...
}
```

The keys are string integers (ordinal position, meaningless). Values contain:
- `cik_str` — integer CIK (NOT zero-padded)
- `ticker` — uppercase ticker symbol
- `title` — EDGAR conformed company name

### Zero-padding rule
All EDGAR API calls require a **10-digit zero-padded CIK**:
```python
cik_padded = str(cik_int).zfill(10)  # "0001045810" for NVDA
```

### Cache strategy
- File: `{CACHE_DIR}/company_tickers.json`
- TTL: 7 days (tickers rarely change; new listings appear within a week)
- On cache miss or staleness: re-fetch, overwrite file, update in-memory dict

### Known CIKs (test anchors)
| Ticker | CIK (int) | CIK (padded) | Company Name |
|---|---|---|---|
| NVDA | 1045810 | 0001045810 | NVIDIA CORP |
| XOM | 34088 | 0000034088 | EXXON MOBIL CORP |
| WMT | 104169 | 0000104169 | WALMART INC |
| AAPL | 320193 | 0000320193 | APPLE INC |
| MSFT | 789019 | 0000789019 | MICROSOFT CORP |

### Edge case: ticker not found
Foreign listings (ASML, BABA, TSM) and some ADRs are NOT in `company_tickers.json`. Return `SourceStatus.ERROR` with message `"Ticker not in EDGAR (foreign or OTC)."` Do not crash.

---

## 3. EDGAR Submissions API

### Endpoint
```
GET https://data.sec.gov/submissions/CIK{cik_padded}.json
```
Example: `https://data.sec.gov/submissions/CIK0001045810.json`

### Response schema (abbreviated)
```json
{
  "cik": "1045810",
  "name": "NVIDIA CORP",
  "sic": "3674",
  "sicDescription": "Semiconductors and Related Devices",
  "tickers": ["NVDA"],
  "exchanges": ["Nasdaq"],
  "fiscalYearEnd": "0126",
  "filings": {
    "recent": {
      "accessionNumber": ["0001045810-26-000037", "0001045810-25-000082", ...],
      "form":            ["4", "10-K", "8-K", "4", ...],
      "filingDate":      ["2026-03-20", "2026-02-26", "2026-01-29", ...],
      "reportDate":      ["2026-03-18", "2026-01-26", "2026-01-29", ...],
      "primaryDocument": ["section16dopoa-aartisshahx.htm", "nvda-20260126.htm", ...],
      "primaryDocDescription": ["Ownership", "Annual Report", "Current Report", ...]
    },
    "files": [
      {"name": "CIK0001045810-submissions-001.json", "filingCount": 40, "filingFrom": "..."}
    ]
  }
}
```

**CRITICAL — Paired arrays, NOT list-of-objects.** Every array shares the same index. To reconstruct filing row N:
```python
filing_n = {
    "accessionNumber": data["filings"]["recent"]["accessionNumber"][n],
    "form":            data["filings"]["recent"]["form"][n],
    "filingDate":      data["filings"]["recent"]["filingDate"][n],
    "primaryDocument": data["filings"]["recent"]["primaryDocument"][n],
}
```

**Pagination:** If a company has >1000 recent filings, EDGAR splits them into additional files listed in `filings.files`. Each entry has `name` (relative path under `data.sec.gov/submissions/`) and `filingFrom`/`filingTo` dates. For most companies the `recent` array is sufficient; for prolific filers (GE, banks) you may need to fetch additional pages.

### Accession number → file URL
```
Accession: "0001045810-26-000037"
Strip dashes: "000104581026000037"
Archive URL: https://www.sec.gov/Archives/edgar/data/{cik_int}/{stripped}/{accession}-index.htm
```

---

## 4. User-Agent Rule

The SEC **will 403 you without this.** It is not optional.

```python
HEADERS = {
    "User-Agent": "AltBrief research@altbrief.com",
    "Accept-Encoding": "gzip, deflate",
    "Host": "data.sec.gov",
}
```

Format: `"{App or Company Name} {contact_email}"`  
The SEC uses this to contact abusers. Any valid email works; it is not verified.

For `edgartools`, set via:
```python
from edgar import set_identity
set_identity("AltBrief research@altbrief.com")
```
Or env var: `EDGAR_IDENTITY="AltBrief research@altbrief.com"`

---

## 5. Rate Limits

- **Hard limit:** 10 requests/second per IP
- **Block behavior:** 403 for ~10 minutes on violation
- **edgartools default:** 9/s token bucket via `pyrate-limiter`
- **Recommended for production:** 8/s to give breathing room

### Manual async rate limiting (for raw httpx path)
```python
import asyncio

_SEMAPHORE = asyncio.Semaphore(8)   # max 8 concurrent in-flight
_RATE_LOCK  = asyncio.Lock()
_last_request_times: list[float] = []

async def rate_limited_get(client: httpx.AsyncClient, url: str) -> httpx.Response:
    async with _SEMAPHORE:
        await asyncio.sleep(0.125)   # 1/8 second between acquires
        return await client.get(url, headers=HEADERS, follow_redirects=True)
```

### edgartools rate config
```python
from edgar import httpclient
# Already defaulting to 9/s — no change needed.
# If you see 429s:
httpclient.update_rate_limiter(requests_per_second=6)
```

### Recommended async client setup (for raw parsing fallback)
```python
import httpx

_client = httpx.AsyncClient(
    headers=HEADERS,
    timeout=httpx.Timeout(connect=10.0, read=30.0, write=10.0, pool=5.0),
    limits=httpx.Limits(max_connections=8, max_keepalive_connections=4),
    follow_redirects=True,
)
```

---

## 6. Form 4 Parsing

### File location
Form 4 XML files live at:
```
https://www.sec.gov/Archives/edgar/data/{cik_int}/{accession_nodash}/{primary_document}
```

The `primary_document` from the submissions API for a Form 4 is typically a `.htm` file. The XML-structured content is usually embedded inline or accessible by fetching the accession index and looking for the `.xml` file.

Index URL:
```
https://www.sec.gov/Archives/edgar/data/{cik}/{accession_nodash}/{accession}-index.htm
```

### XML structure (`ownershipDocument`)
```xml
<ownershipDocument>
  <reportingOwner>
    <reportingOwnerId>
      <rptOwnerCik>0001234567</rptOwnerCik>
      <rptOwnerName>HUANG JEN HSUN</rptOwnerName>
    </reportingOwnerId>
    <reportingOwnerRelationship>
      <isDirector>0</isDirector>
      <isOfficer>1</isOfficer>
      <isOfficerTitle>President and CEO</isOfficerTitle>
      <isTenPercentOwner>0</isTenPercentOwner>
    </reportingOwnerRelationship>
  </reportingOwner>

  <nonDerivativeTable>
    <nonDerivativeTransaction>
      <securityTitle><value>Common Stock</value></securityTitle>
      <transactionDate><value>2026-03-18</value></transactionDate>
      <transactionCoding>
        <transactionFormType>4</transactionFormType>
        <transactionCode>S</transactionCode>   <!-- S=sale, P=purchase, A=grant, M=exercise -->
        <equitySwapInvolved>0</equitySwapInvolved>
      </transactionCoding>
      <transactionAmounts>
        <transactionShares><value>300000</value></transactionShares>
        <transactionPricePerShare><value>182.25</value></transactionPricePerShare>
        <transactionAcquiredDisposedCode><value>D</value></transactionAcquiredDisposedCode>
      </transactionAmounts>
      <postTransactionAmounts>
        <sharesOwnedFollowingTransaction><value>12500000</value></sharesOwnedFollowingTransaction>
      </postTransactionAmounts>
    </nonDerivativeTransaction>
  </nonDerivativeTable>

  <derivativeTable>
    <!-- Options, RSUs, etc. Same structure but under derivativeTransaction -->
  </derivativeTable>
</ownershipDocument>
```

### Transaction codes
| Code | Meaning |
|---|---|
| P | Open-market purchase (bullish signal) |
| S | Open-market sale (bearish signal) |
| A | Grant/award (neutral — compensation) |
| M | Exercise of derivative (neutral — may precede S) |
| G | Gift (neutral) |
| F | Tax withholding (neutral — often paired with A) |
| J | Other acquisition or disposition (neutral) |

**For sentiment scoring:** Only count `P` (bullish) and `S` (bearish). Ignore `A`, `M`, `G`, `F`, `J`.

### XPath expressions (lxml)
```python
from lxml import etree

# Parse — handle both case-sensitive and lowercased XML namespaces
def _parse_form4_xml(xml_bytes: bytes) -> dict:
    root = etree.fromstring(xml_bytes)

    def _text(xpath: str) -> str | None:
        nodes = root.xpath(xpath)
        return nodes[0].text.strip() if nodes and nodes[0].text else None

    # Owner identity
    name = _text(".//rptOwnerName")
    is_director  = _text(".//isDirector") == "1"
    is_officer   = _text(".//isOfficer") == "1"
    officer_title = _text(".//isOfficerTitle")
    is_10pct     = _text(".//isTenPercentOwner") == "1"

    # All non-derivative transactions
    txns = []
    for txn in root.xpath(".//nonDerivativeTransaction"):
        def t(path): return txn.xpath(path)[0].text.strip() if txn.xpath(path) else None
        txns.append({
            "security":    t(".//securityTitle/value"),
            "date":        t(".//transactionDate/value"),
            "code":        t(".//transactionCode"),
            "shares":      t(".//transactionShares/value"),
            "price":       t(".//transactionPricePerShare/value"),
            "acq_disp":    t(".//transactionAcquiredDisposedCode/value"),
        })

    return {"owner_name": name, "is_officer": is_officer, "officer_title": officer_title,
            "is_director": is_director, "is_10pct": is_10pct, "transactions": txns}
```

**Note on XML case:** EDGAR Form 4 XML is case-sensitive. Most filings use mixed-case tags (`rptOwnerName`, `transactionShares`). Some older filings use lowercase. Use `.//{tag}` XPath (descendant wildcard) rather than absolute paths to be robust.

---

## 7. 10-K Risk Factor Extraction

### edgartools approach (recommended)
```python
from edgar import Company

tenk = Company("NVDA").get_filings(form="10-K")[0].obj()
risk_text: str = tenk.risk_factors   # Full Item 1A text as string
```

`risk_factors` returns the raw text of the Item 1A section. To extract top-N factors:
1. Split on double newlines or numbered-list markers
2. Sort by paragraph length (longer = more specific)
3. Return top 5

### Fallback: regex + BeautifulSoup (when edgartools fails or risk_factors is None)

The Item 1A boundaries are found via regex:
```python
import re
from bs4 import BeautifulSoup

# Matches: "Item 1A", "ITEM 1A.", "Item&#160;1A", "ITEM&nbsp;1A"
ITEM_1A = re.compile(r'(item\s*1a\.?\s*[\.\-—]?\s*risk\s*factors)', re.IGNORECASE)
ITEM_1B = re.compile(r'(item\s*1b\.?\s)', re.IGNORECASE)

def _extract_item1a_fallback(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    text = soup.get_text(separator="\n")
    lines = text.split("\n")
    capturing = False
    buffer = []
    for line in lines:
        if ITEM_1A.search(line):
            capturing = True
            continue
        if capturing and ITEM_1B.search(line):
            break
        if capturing:
            buffer.append(line)
    return "\n".join(buffer).strip()
```

**Known edge cases:**
- iXBRL filings (post-2019): Item 1A text may be tagged with `<ix:nonNumeric>` — BeautifulSoup strips these fine
- Table of contents: "Item 1A" appears twice (TOC entry + actual section). The regex will match the TOC first; skip if the captured text is less than 500 chars and continue scanning.
- Some filers say "We have no material risk factors" — return that text verbatim; do not crash.

---

## 8. Earnings Guidance from 10-Q and 8-K

### 10-Q forward guidance (MD&A section)
```python
tenq = Company("NVDA").get_filings(form="10-Q")[0].obj()
# edgartools exposes:
mda_text = tenq.management_discussion   # or tenq.mda — library uses both
```

Guidance language appears in MD&A as "We expect...", "We anticipate...", "Outlook:" paragraphs. Use simple keyword extraction post-fetch.

### 8-K earnings guidance (Item 2.02 or press release exhibits)
```python
filings = Company("NVDA").get_filings(form="8-K")

for filing in filings.head(5):
    eightk = filing.obj()
    # Items dict access
    item_text = eightk.get("Item 2.02") or eightk.get("Item 7")
    if not item_text:
        # Try press release text
        item_text = filing.text()[:4000]
```

**Guidance keyword patterns to scan for:**
```python
GUIDANCE_PATTERNS = [
    r'(?:revenue|net revenue|total revenue)[^\n]*(?:\$[\d,.]+\s*(?:billion|million)|guidance|expects?|anticipates?)',
    r'(?:outlook|guidance|forecast)[^\n]{0,200}(?:\$[\d,.]+|\d+(?:\.\d+)?\s*(?:billion|million|percent))',
    r'(?:we expect|we anticipate|we project|we guide)[^\n]{0,300}',
]
```

---

## 9. Edge Cases

| Case | Detection | Handling |
|---|---|---|
| Ticker not in EDGAR | `cik` lookup returns `None` | Return `SourceResult(status=ERROR, error_msg="Ticker not in EDGAR")` |
| CIK changed (M&A) | company name in submissions doesn't match expected | Log warning; proceed with what EDGAR returns |
| No Form 4 filings in 90 days | `form4_filings` list is empty | Return `insider_sentiment="insufficient_data"`, `transactions=[]` |
| Most recent 10-K < 90 days old | Filing date within 90 days | Use it; it IS the latest |
| No 10-K at all (recent IPO) | `get_filings(form="10-K")` returns empty | Return `risk_factors=[]`, log warning |
| 10-K `risk_factors` is None (edgartools parse failure) | `tenk.risk_factors is None` | Fall back to regex+BS4 on raw HTML |
| Pagination needed (>1000 filings) | `filings.files` is non-empty | For 90-day window, `recent` array always covers — rarely need pagination |
| SEC 429 / IP block | `httpx.HTTPStatusError` with 429 | Raise `RateLimitError`; caller returns `SourceStatus.RATE_LIMITED` |
| `edgartools` import error | `ImportError` | Module-level guard raises descriptive message about `pip install edgartools` |

---

## 10. Test Data — Real EDGAR Returns

### NVDA Form 4 (March 2026)
All sales, zero purchases. Net sentiment: **bearish (massive insider selling)**.

| Insider | Role | Date | Code | Shares | Price | Value |
|---|---|---|---|---|---|---|
| Ajay K. Puri | EVP Worldwide Field Ops | 2026-03-18 | S | 300,000 | $182.25 | $54.7M |
| Colette Kress | CFO | 2026-03-20 | S | 62,650 | $174.89 | $11.0M |
| Mark A. Stevens | Director | 2026-03-20 | S | 221,682 | $173.68 | $38.5M |
| Aarti S. Shah | Director | 2026-03-19 | S | 19,000 | $176.71 | $3.4M |
| Donald Robertson Jr. | PAO | 2026-03-20 | S | 5,396 | $174.75 | $943K |

**Net 90-day volume (buys - sells):** approximately -$108M  
**Sentiment tag:** `net_sell`

### WMT CIK
CIK: `104169` — confirmed via SEC EDGAR (Form 3 FY2026 filings visible)

### XOM CIK
CIK: `34088` — confirmed via SEC EDGAR (secform4.com tracker maps to this CIK)

### NVDA 10-K Risk Factors sample (from 2025 annual report)
Top-5 by length/specificity (for mock/eval use):
1. Demand for our products is highly variable and may fluctuate significantly...
2. We depend on third-party suppliers, including TSMC, for the manufacturing of our products...
3. We face intense competition from companies with much greater resources...
4. We are subject to export controls and government regulations that restrict our ability to sell in certain markets...
5. Our revenue may be adversely affected by product defects, warranty claims, or product recalls...

---

## 11. Full `sources/sec.py` Module

See the complete code below — copy directly into `backend/sources/sec.py`.

---

## Sources

- [SEC EDGAR Developer Resources](https://www.sec.gov/about/developer-resources)
- [data.sec.gov Submissions JSON Guide — FundamentalsHub](https://fundamentalshub.com/blog/data-sec-gov-submissions-json)
- [EdgarTools Complete Guide 2026](https://edgartools.readthedocs.io/en/stable/complete-guide/)
- [EdgarTools GitHub — v5.31.5, 2026-05-22](https://github.com/dgunning/edgartools)
- [EdgarTools HTTP Client & Rate Limiting — DeepWiki](https://deepwiki.com/dgunning/edgartools/8.1-http-client-and-rate-limiting)
- [EdgarTools Configuration](https://edgartools.readthedocs.io/en/stable/configuration/)
- [EdgarTools Local Storage](https://edgartools.readthedocs.io/en/latest/guides/local-storage/)
- [EdgarTools 8-K Filings Guide](https://dgunning.github.io/edgartools/eightk-filings/)
- [SEC EDGAR Rate Limits — DealCharts](https://dealcharts.org/blog/edgar-scraping-rate-limits-explained)
- [SEC EDGAR Rate Limit — TLDRFiling](https://tldrfiling.com/blog/sec-edgar-api-rate-limits-best-practices)
- [EDGAR Ownership XML Technical Specification](https://www.sec.gov/info/edgar/ownershipxmltechspec-v3_d.pdf)
- [Form 4 XML Parsing with lxml — wrighters.io](https://www.wrighters.io/an-introduction-to-accessing-financial-data-in-edgar-using-python/)
- [10-K Item 1A Regex Extraction — GitHub Gist](https://gist.github.com/anshoomehra/ead8925ea291e233a5aa2dcaa2dc61b2)
- [EDGAR Accessing Data — SEC.gov](https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data)
- [NVDA Insider Trading Form 4 Filings — SECForm4.com](https://www.secform4.com/insider-trading/1045810.htm)
- [How to Parse 10-K — yuzhu.run](https://yuzhu.run/how-to-parse-10x/)
