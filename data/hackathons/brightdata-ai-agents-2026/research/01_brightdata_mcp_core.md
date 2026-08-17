# BrightData MCP Server — Complete Technical Deep-Dive

> Research output for the Alt-Data Investment Brief Agent (BrightData × lablab.ai Hackathon, May 25–31, 2026)

---

## 1. Installation + Auth Pattern

### NPM (local subprocess — recommended for Agent SDK)

```bash
# Prerequisite: Node.js 18+. No global install needed — npx lazy-installs on first run.
npx -y @brightdata/mcp
```

### MCP client config (Claude Desktop / Claude Code)

```json
{
  "mcpServers": {
    "Bright Data": {
      "command": "npx",
      "args": ["-y", "@brightdata/mcp"],
      "env": {
        "API_TOKEN": "YOUR_BRIGHTDATA_API_TOKEN"
      }
    }
  }
}
```

### Remote hosted server (no Node.js required)

```
https://mcp.brightdata.com/mcp?token=YOUR_API_TOKEN
```

SSE transport via Claude Code CLI:

```bash
claude mcp add --transport sse brightdata \
  "https://mcp.brightdata.com/sse?token=YOUR_API_TOKEN"

claude mcp list   # should show "✓ Connected"
```

### Getting your API token

1. Create account at brightdata.com
2. Go to **User Settings → API Token** — [brightdata.com/cp/setting/users](https://brightdata.com/cp/setting/users)
3. Token shown **once only** — save to `.env` immediately
4. Set permission level (5 levels) + optional expiration date at creation time

---

## 2. Environment Variables (Complete Reference)

| Variable | Required | Default | Description |
|---|---|---|---|
| `API_TOKEN` | **Yes** | — | Auth credential |
| `PRO_MODE` | No | `false` | `true` = all 60+ tools enabled |
| `GROUPS` | No | — | Comma-separated group IDs e.g. `social,finance,business,research` |
| `TOOLS` | No | — | Comma-separated exact tool names (additive on top of GROUPS) |
| `WEB_UNLOCKER_ZONE` | No | `mcp_unlocker` | Custom Web Unlocker zone |
| `BROWSER_ZONE` | No | `mcp_browser` | Custom Scraping Browser zone |
| `POLLING_TIMEOUT` | No | `600` | Seconds to wait for `web_data_*` async polling |
| `BASE_TIMEOUT` | No | Unlimited | Max seconds for search/scrape calls |
| `BASE_MAX_RETRIES` | No | `0` | Retry attempts on transient errors (0–3) |
| `RATE_LIMIT` | No | Unlimited | Self-imposed cap e.g. `100/1h`, `50/30m` |

**Mode priority (highest wins):** `PRO_MODE=true` > `GROUPS`/`TOOLS` > default Rapid mode

---

## 3. Free vs. Paid Tiers

| Tier | Monthly Req | Tools | Cost |
|---|---|---|---|
| **Free / Rapid** | 5,000/month | Base tools only | $0 |
| **Pay-as-you-go** | Unlimited | All 60+ Pro | $1.50/1K search+scrape+extract; $8/GB browser |
| **Starter** | Unlimited | All Pro | $499/mo + $1.30/1K; $7/GB browser |
| **Professional** | Unlimited | All Pro | $999/mo + $1.10/1K; $6/GB browser |
| **Business** | Unlimited | All Pro | $1,999/mo + $1.00/1K; $5/GB browser |

**Sign-up incentive:** Dollar-for-dollar match on first deposit up to $500. Source: [brightdata.com/pricing/mcp-server](https://brightdata.com/pricing/mcp-server)

**"$250 free credit" figure** — [unverified] — not on official pricing page. Confirmed free allocation is 5,000 req/month Rapid mode.

**Billable requests:** Each `search_engine`, `scrape_as_markdown`, `extract`, `scrape_as_html` call = 1 request. Browser usage billed by GB bandwidth. `web_data_*` structured tools billed per result [unverified — success-only billing not explicitly confirmed]. Monitor via `session_stats` tool.

---

## 4. Complete Tool Inventory by Group

### Base Tools — Free Tier (always enabled)

| Tool | Capability |
|---|---|
| `search_engine` | Google/Bing/Yandex SERP — JSON for Google, Markdown for Bing/Yandex; pagination |
| `scrape_as_markdown` | Any URL → clean Markdown; handles CAPTCHA + bot protection |
| `discover` | AI-ranked intent-aware search — ranks by semantic relevance not SEO |
| `search_engine_batch` | Up to 10 queries in parallel |
| `scrape_batch` | Up to 10 URLs in parallel |

### Group: `advanced_scraping`

| Tool | Capability |
|---|---|
| `scrape_as_html` | URL → raw HTML with bot detection bypass |
| `extract` | URL → structured JSON using AI + custom extraction prompt |
| `session_stats` | Request count + tool usage report |

### Group: `social`

**LinkedIn (critical for alt-data):**

| Tool | Capability |
|---|---|
| `web_data_linkedin_person_profile` | Title, skills, experience, education |
| `web_data_linkedin_company_profile` | Headcount, industry, description, follower count |
| `web_data_linkedin_job_listings` | Open roles by company or keyword |
| `web_data_linkedin_posts` | Recent posts from a profile or company |
| `web_data_linkedin_people_search` | Find people by keyword/company/title |

**Reddit:** `web_data_reddit_posts` — title, upvotes, comments, awards, flair

**X/Twitter:** `web_data_x_posts`, `web_data_x_profile_posts`

**YouTube / Instagram / TikTok / Facebook:** Full profile + post + comment tools for each (~16 tools total in group).

### Group: `finance`

| Tool | Capability |
|---|---|
| `web_data_yahoo_finance_business` | Company financial profile: ticker data, key metrics, description |

### Group: `business`

| Tool | Capability |
|---|---|
| `web_data_crunchbase_company` | Funding rounds, investors, founding date, valuation signals |
| `web_data_zoominfo_company_profile` | Size, revenue, tech stack signals |
| `web_data_google_maps_reviews` | Location-level customer sentiment |
| `web_data_zillow_properties_listing` | Real estate listings |

### Group: `research`

| Tool | Capability |
|---|---|
| `web_data_reuter_news` | Reuters news: headline, body, date, author — structured |
| `web_data_github_repository_file` | GitHub file content extraction |

### Group: `geo` (LLM brand visibility)

| Tool | Capability |
|---|---|
| `web_data_chatgpt_ai_insights` | How ChatGPT describes a company/brand |
| `web_data_grok_ai_insights` | Grok's brand mentions/sentiment |
| `web_data_perplexity_ai_insights` | Perplexity's brand knowledge |

### Group: `browser`

Navigate, snapshot, click, type, wait, screenshot, get_text, get_html, scroll, network_requests — full headless Chrome via BrightData's Scraping Browser. Billed by bandwidth.

### Group: `ecommerce`

11 tools: Amazon, Walmart, eBay, Home Depot, Zara, Etsy, Best Buy, Google Shopping.

### Group: `app_stores`

`web_data_google_play_store`, `web_data_apple_app_store`

### Group: `code`

`web_data_npm_package`, `web_data_pypi_package`

**Full authoritative tool list:** [github.com/brightdata/brightdata-mcp/blob/main/assets/Tools.md](https://github.com/brightdata/brightdata-mcp/blob/main/assets/Tools.md)

---

## 5. `discover` vs `search_engine` vs `scrape_as_markdown` — Decision Tree

```
Have a specific URL?
├── YES → scrape_as_markdown  (or scrape_as_html if you need DOM)
└── NO → Need to find URLs
    Is semantic relevance > SEO ranking?
    ├── YES → discover  (AI intent-ranked; better for research queries)
    └── NO  → search_engine  (standard SERP; brand/news searches)
              └── Then scrape_as_markdown on result URLs

Is the page JS-rendered / behind auth / needs interaction?
└── browser group (navigate + get_text) — costs bandwidth

Is the target a known platform (LinkedIn / Reddit / Reuters / Yahoo Finance)?
└── Use web_data_{platform}_* directly — faster + cheaper + pre-structured
```

**Alt-Data brief mapping:**
- Company search by ticker → `search_engine` → get LinkedIn URL → `web_data_linkedin_company_profile`
- Reddit sentiment → `web_data_reddit_posts` (WSB, r/stocks, r/investing)
- News flow → `web_data_reuter_news` (find URL via `search_engine` first)
- Funding signals → `web_data_crunchbase_company`
- Financial snapshot → `web_data_yahoo_finance_business`
- Glassdoor signals → no native tool; use `scrape_as_markdown` or `discover`

---

## 6. Claude Agent SDK Integration — Python

```python
import asyncio, os
from dotenv import load_dotenv
from claude_agent_sdk import query, ClaudeAgentOptions
from claude_agent_sdk.types import StreamEvent

load_dotenv()
BD_KEY = os.getenv("BRIGHT_DATA_API_KEY")

options = ClaudeAgentOptions(
    mcp_servers={
        "bright_data": {
            "command": "npx",
            "args": ["-y", "@brightdata/mcp"],
            "env": {
                "API_TOKEN": BD_KEY,
                "GROUPS": "social,finance,business,research",
            }
        }
    },
    allowed_tools=["mcp__bright_data__*"],
    model="claude-sonnet-4-5",
    permission_mode="acceptEdits",
    max_buffer_size=10 * 1024 * 1024,
)

async def run(prompt: str) -> str:
    parts = []
    async for msg in query(prompt=prompt, options=options):
        if isinstance(msg, StreamEvent):
            ev = msg.event
            if ev.get("type") == "content_block_start":
                blk = ev.get("content_block", {})
                if blk.get("type") == "tool_use":
                    print(f"[Tool: {blk.get('name')}]", flush=True)
            elif ev.get("type") == "content_block_delta":
                d = ev.get("delta", {})
                if d.get("type") == "text_delta":
                    parts.append(d.get("text", ""))
    return "".join(parts)
```

### Parallel fan-out (for the hackathon multi-source brief)

```python
async def parallel_alt_data(ticker: str):
    tasks = [
        run(f"Get LinkedIn company profile for {ticker}"),
        run(f"Get Reddit posts mentioning ${ticker} from r/stocks and r/investing"),
        run(f"Get Reuters news articles about {ticker} from last 30 days"),
        run(f"Get Crunchbase company profile for {ticker}"),
        run(f"Get Yahoo Finance business profile for {ticker}"),
    ]
    return await asyncio.gather(*tasks, return_exceptions=True)
```

### Remote endpoint via Anthropic SDK (no npx needed)

```python
from anthropic import Anthropic
client = Anthropic()
res = client.beta.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=4096,
    tools=[{
        "type": "mcp",
        "server": {
            "type": "url",
            "url": f"https://mcp.brightdata.com/mcp?token={BD_KEY}",
        }
    }],
    messages=[{"role": "user", "content": "Get Reuters news for Tesla from last 30 days"}],
    betas=["mcp-client-2025-04-04"],
)
```

---

## 7. Rate Limits, Concurrency, Retry Semantics

- **Free tier hard cap:** 5,000 req/month, server-enforced
- **Configurable self-throttle:** `RATE_LIMIT=100/1h` or `50/30m`
- **Web Unlocker auto-handles 429s** from target sites via IP rotation
- **`BASE_MAX_RETRIES=0` default** — set to `2` in dev, `3` in prod for network blips
- **`POLLING_TIMEOUT=600` default** — `web_data_*` tools poll async
- **`BASE_TIMEOUT=120`** recommended; `180` for JS-heavy sites

**Error codes:**

| Code/Error | Cause | Fix |
|---|---|---|
| `spawn npx ENOENT` | Node not on PATH | Full path: `/usr/local/bin/node` |
| `401 Unauthorized` | Bad/expired `API_TOKEN` | Regenerate at user settings |
| `429` from BrightData | Free tier exhausted | Upgrade or wait |
| `POLLING_TIMEOUT exceeded` | Async job timed out | Raise `POLLING_TIMEOUT` |
| `422 Unprocessable` | Malformed URL | Must be full `https://` URL |

---

## 8. Streaming Response Patterns

BrightData MCP tools do **not** stream internally — `web_data_*` use async polling. The LLM response text streams via Agent SDK's `StreamEvent`. Tool call progress visible in `content_block_start` events. This lets the hackathon demo show a live progress feed while sources are gathered.

---

## 9. Security + Credential Management

```bash
# .env — never commit to git
BRIGHT_DATA_API_KEY=your_token_here
ANTHROPIC_API_KEY=your_claude_token_here
```

```
# .gitignore
.env
*.env
```

**Token hygiene:**
- Token shown once at creation — save immediately
- Set short expiration for hackathon tokens (7–14 days)
- Use minimal permission level for scraping agents
- Prefer `env.API_TOKEN` over URL-embedded token
- Separate `WEB_UNLOCKER_ZONE` per project

**Prompt injection defense:** Scraped web content is untrusted. Sanitize before LLM injection — strip HTML comments, truncate to ~8K chars, never pass raw HTML as system context.

---

## 10. Known Gotchas

| Gotcha | Fix |
|---|---|
| `spawn npx ENOENT` | Use `which npx`; set full path as `command` |
| `web_data_*` never returns | Raise `POLLING_TIMEOUT=1200` |
| Claude confused by too many tools | Use `GROUPS` not `PRO_MODE=true` |
| LinkedIn tool returns empty | URL must be full `https://linkedin.com/in/...` |
| Reddit tool returns old posts | No built-in date filter — add "last 7 days" in prompt |
| Reuters tool 422 error | Pass direct article URL, not homepage |
| Browser session costs spike | Sessions bill until closed |
| Free tier burns in testing | Set `RATE_LIMIT=50/1h` during dev |
| `batch` tools not free | `search_engine_batch` may require `advanced_scraping` [unverified] |

---

## Optimal GROUPS Config for Alt-Data Brief Agent

```bash
GROUPS=social,finance,business,research
```

Exposes ~30 tools covering LinkedIn, Reddit, X, Yahoo Finance, Crunchbase, ZoomInfo, Reuters without 60+ tool context overhead.

---

## Sources

- [GitHub: brightdata/brightdata-mcp](https://github.com/brightdata/brightdata-mcp)
- [GitHub: Tools.md](https://github.com/brightdata/brightdata-mcp/blob/main/assets/Tools.md)
- [Bright Data Blog: Claude Agent SDK + Web MCP](https://brightdata.com/blog/ai/claude-agent-sdk-with-web-mcp)
- [Bright Data Docs: MCP Server Tools](https://docs.brightdata.com/ai/mcp-server/tools)
- [Bright Data Docs: MCP FAQ](https://docs.brightdata.com/mcp-server/faqs)
- [Bright Data Docs: Claude Code Integration](https://docs.brightdata.com/ai/mcp-server/integrations/claude-code)
- [Bright Data Pricing](https://brightdata.com/pricing/mcp-server)
- [Bright Data Docs: API Token](https://docs.brightdata.com/general/account/api-token)

**Confidence: High** — All major claims sourced from official BrightData docs, GitHub, first-party blog. Two items [unverified]: batch tool free-tier status, success-only billing for `web_data_*`.
