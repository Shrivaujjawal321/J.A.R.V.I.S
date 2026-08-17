# 2026 SOTA Fintech / Investment / Agent Dashboard UI References

## Quick Answer

The 2026 bar for finance agent UI: **dark navy-black base + monospace numbers + semantic color (green/red/amber) + Perplexity-style inline citations + agent step progress disclosure + Hebbia-style structured brief output.** Amateur tells: Bootstrap-grey backgrounds, chat-bubble research output, spinner with no progress context.

---

## Pro-Tier Finance Terminals

### Bloomberg Terminal
- **Color:** Pure black + amber (`#FF6B00`) + red/blue CVD-safe
- **Type:** Monospace only — fixed-width columns
- **Density:** Extreme — 4-6 columns simultaneously
- **Steal:** Amber terminal widget for ticker input. Fixed-width mono for all live numbers. Columnar key metrics (P/E, EV/EBITDA, Price Target, Upside).

### Koyfin (https://koyfin.com)
- Dark `#0F1117` + muted blue accents
- Three-panel: watchlist | chart | sidebar
- **Steal:** Multi-panel resizable layout. Fundamental rows below chart with YoY delta arrows. Sortable comparable companies table.

### AlphaSense
- Dark navy `#0D1B2A` + electric blue
- Oct 2025: Single conversational interface combining quant data + research + expert calls
- **Steal:** Split-pane (query left, output right). Inline citation chips `[Source: GS Research, Mar 2026]`. Coverage meter: "47 mentions across 1,200 documents."

---

## Modern Retail Finance Apps

### StockAnalysis.com
- Restraint = premium signal. Zero pop-ups, zero upsells.
- **Steal:** Revenue waterfall table. EPS Actual vs Estimate with Beat/Miss badge. Simple bold price header: `$142.37 ▲ 2.4%`.

### Fiscal.ai (formerly FinChat.io)
- Dark mode + teal/cyan accents. Streaming tokens.
- **Steal:** AI answer + auto-generated chart as single atomic card. Metric pills below input. Company comparison mode with synthesis paragraph.

### Wealthfront
- Light mode + green `#00C805`
- **Steal:** Hero portfolio value as massive centered number. Allocation donut (not pie) with color-coded legend.

---

## Crypto Dashboards

### Dune Analytics
- Dark `#1A1A2E` + neon protocol brand colors
- **Steal:** Color-per-source legend. Apply to alt-data: Web Traffic = teal, News Sentiment = amber, Job Postings = violet. "Last updated X min ago" timestamps. Full-width area chart with 0.2 fill opacity.

### DefiLlama
- High density. Sticky table headers. Sparkline mini-charts in cells.
- **Steal:** Sparklines inline in table rows — exact pattern for competitor comparison.

### Messari Pro / Artemis Analytics
- Standardised metrics across protocols
- **Steal (Artemis):** Protocol comparison matrix (rows = metrics, cols = assets) — exact pattern for alt-data competitor table. Sector heat map.

---

## AI-Finance Products

### Hebbia Matrix
- **Rejected chat UI entirely.** Output is spreadsheet grid — documents = rows, questions = cols, AI = cells with inline citations.
- **Steal:** Brief-as-table for competitor comparison. Inline `[Source]` chip per cell. Agent task decomposition visible: `1. Fetching web traffic... 2. Analysing sentiment... 3. Synthesising brief...`

---

## Agent UIs

### Perplexity Deep Research
- Answer block 720px max-width column
- Source cards as horizontal scrollable strip (favicon + domain + excerpt)
- Follow-up pill chips below answer
- Numbered inline citations `[1] [2]` with hoverable preview
- **Steal:** Source strip showing BrightData provenance. Numbered citations in brief prose. Follow-up chips: `"Compare to sector peers"` `"Show 12-month trend"` `"Export PDF"`.

### ChatGPT / Gemini Deep Research
- **Research plan step BEFORE output** — "I'll investigate X, then Y, then Z"
- Live step progress with checkmarks
- **Steal:** Research plan disclosure card. Live step progress with checkmark animation (200ms ease-out). Intermediate data preview (3 sample headlines, job count) — removes "magic black box" feel.

### Linear.app
- Near-black `#0F0F0F` + minimal purple
- Near-monochrome 2025 redesign
- "Calm design" — absence of clutter IS the premium signal
- **Steal:** Tight sidebar nav. Status badges as minimal pills (4px dot + text). Keyboard shortcut tooltips.

### Vercel Dashboard
- Near-black + animated gradient mesh (CSS, not WebGL)
- "The product is the demo"
- **Steal:** Subtle gradient mesh on brief output card (slow hue shift). Streaming log line animation. Status indicator pulse on state change.

### Runway Financial (Awwwards SOTD)
- **Steal:** Scenario comparison toggle — Base | Bull | Bear. Confidence meter as linear progress bar with deadline marker.

---

## Canonical Brief Layout (Sell-Side Note Structure)

Real Morgan Stanley / Goldman notes follow this — our UI should mirror:

```
COVER HEADER
  ├── Company Name | Ticker | Exchange
  ├── Rating badge (BUY/HOLD/SELL) — color coded
  ├── Price Target: $XXX | Current: $XXX | Upside: +XX%
  ├── Analyst + Date + Data Sources
  └── 1-sentence thesis hook

INVESTMENT THESIS
  └── 3-4 bullets: WHY this is buy/avoid

ALT-DATA SIGNALS DASHBOARD [our unique layer]
  ├── Web Traffic Trend (sparkline + delta badge)
  ├── News Sentiment Score (gauge + color)
  ├── Job Postings Velocity (sparkline + net change)
  ├── Satellite Signals (image preview + verdict)
  └── Signal Consensus: BULLISH / NEUTRAL / BEARISH

FINANCIAL OVERVIEW
  ├── Revenue, EBITDA, Net Income (8-quarter table)
  └── Key ratios: P/E, EV/EBITDA, P/S

COMPETITIVE POSITION
  └── Comparison table: 3-5 comps × same alt-data signals

RISKS
  └── Bulleted list with severity badges (HIGH/MEDIUM/LOW)

APPENDIX — RAW DATA SOURCES
  └── Source cards with BrightData endpoint + timestamp per signal
```

---

## Design Language Synthesis

**Target:** "Bloomberg Terminal for the AI age" — sweet spot between Perplexity (citation trust) + AlphaSense (dual-pane) + Linear (calm SaaS polish).

**Color system:**
```css
--bg-base:        #0A0E1A;   /* navy-black */
--surface-1:      #111827;   /* cards */
--surface-2:      #1F2937;   /* hover */
--border:         #374151;

--accent:         #3B82F6;   /* blue — trust, data */
--bullish:        #10B981;   /* emerald-500 */
--bearish:        #EF4444;   /* red-500 */
--neutral:        #F59E0B;   /* amber-500 */

--text-primary:   #F9FAFB;
--text-secondary: #9CA3AF;
--mono-live:      #6EE7B7;   /* emerald-300 — terminal feel */
```

**Typography:**
- Tickers/live numbers: `font-mono` (JetBrains Mono)
- Headings: Inter or Geist, tight tracking at display sizes
- Brief prose: Inter 16px, 1.6 line-height
- Labels/badges: 10-11px uppercase, 0.1em letter-spacing

**Motion language:**
- Token streaming on brief generation
- Agent step ticker: numbered list, pulsing dot → checkmark (200ms ease-out)
- Chart entrance: line draws left-to-right, 600ms
- Card mount: `opacity 0→1` + `translateY(8px)→0`, 150ms staggered
- Number update: digit roll/counter animation
- **No:** scroll-jacking, particle systems, WebGL — this is a data product

---

## Signal Card Pattern (primary reusable component)

```
┌────────────────────────────────────────┐
│  WEB TRAFFIC               ▲ BULLISH   │
│  [sparkline chart 80px tall]           │
│  +14.2% MoM    |    3.2M visits/mo     │
│  vs. 6mo avg: +2.1%  [delta badge]     │
│  Source: BrightData SERP · 2h ago      │
└────────────────────────────────────────┘
```

- Verdict badge top-right: BULLISH (green pill) / NEUTRAL (amber) / BEARISH (red)
- Sparkline full-width, 0.15 fill opacity
- Source attribution 11px muted

---

## Anti-Patterns ("Amateur Hackathon" Tells)

1. **Light grey background + blue Bootstrap buttons** — `#F5F5F5` + `#007BFF` reads as "opened a template"
2. **Y-axis truncation on charts** — starting at $90k to make 5% move look 10x. Zero-baseline always.
3. **Rainbow multi-color with no semantic system** — green = bullish everywhere, red = bearish everywhere, amber = caution. Violation breaks trust instantly.
4. **Chat-bubble UI for research output** — Hebbia explicitly rejected this. Research output should look like a document, not WhatsApp.
5. **Spinner with no progress context** — In 2026, agent UIs show live step progress. Blank spinner signals dev didn't think.

---

## Sources

- [Fintech UX Patterns 2026 — Eleken](https://www.eleken.co/blog-posts/modern-fintech-design-guide)
- [Fiscal.ai Review — WallStreetZen](https://www.wallstreetzen.com/blog/finchat-io-fiscal-ai-review/)
- [Hebbia Matrix Blog](https://www.hebbia.com/blog/introducing-matrix-the-interface-to-agi)
- [Perplexity: Citation-Forward Answers — Unusual.ai](https://www.unusual.ai/blog/perplexity-platform-guide-design-for-citation-forward-answers)
- [Agent UX 2026 — FuseLab](https://fuselabcreative.com/ui-design-for-ai-agents/)
- [Linear Design — LogRocket](https://blog.logrocket.com/ux-design/linear-design/)
- [Runway Financial — Awwwards](https://www.awwwards.com/sites/runway-financial)
- [Equity Research Report Format — Wall Street Prep](https://www.wallstreetprep.com/knowledge/sample-equity-research-report/)
- [Bloomberg Color Accessibility](https://www.bloomberg.com/company/stories/designing-the-terminal-for-color-accessibility/)

**Confidence: Medium-High** — Visual palettes synthesised from published brand resources + design analysis. Structural patterns from converging sources.
