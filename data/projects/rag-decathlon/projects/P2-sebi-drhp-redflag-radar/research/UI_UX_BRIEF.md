# P2 — SEBI DRHP Red-Flag Radar: UI/UX Brief

**Generated**: 2026-05-14 by ui-ux-designer-agent  
**Phase**: 3.1 (UI/UX Research -> Builder Brief)  
**Consumer**: frontend-engineer-agent  
**Stack**: Next.js 15 App Router - React 19 - Tailwind 4 - shadcn/ui v4 (Luma foundation) - Radix UI

---

## 1. Design Direction

Six principles that every decision flows from:

1. **Audit report, not a product.** The visual DNA is a PwC/Deloitte audit memo rendered as a digital-native interface -- structured, dense, citation-first. Not a fintech consumer app. No sparkles, no gradients, no friendly robot. The product earns trust through structural sobriety, the way a Bloomberg terminal does.

2. **Linear-dense, Stripe-restrained, Screener.in-citation-first.** Information density matches Linear's issue list. Color restraint matches Stripe's docs. Every number that appears on screen traces to a source, the way Screener.in links every ratio to the filing it came from.

3. **Severity is a system, not decoration.** The CRITICAL/HIGH/MODERATE/NONE system -- inspired by Tickertape's SmartScore badge -- is the only place saturated color lives. Everywhere else: monochrome surfaces, blue accents. Severity color is never the sole indicator: always icon + label + color (triple signal for a11y and colorblind users).

4. **Citation is the product.** Every red flag must visually anchor to a source. The citation chip is a first-class UI element. The drill-down path (chip -> hover preview -> PDF viewer -> highlighted page) is the core interaction loop, not a secondary feature.

5. **Extracted fact vs LLM synthesis are visually distinct.** Verbatim quotes from the DRHP appear in monospaced blockquotes with a left border -- they look like evidence. LLM synthesis appears in regular prose with an italicized "Analysis" label. Users must never confuse what the document says with what the AI interpreted.

6. **Motion: sober as the subject matter.** 120ms hover, 220ms state transitions, 320ms modal enter -- and that is all. No parallax, no scroll-jacking, no number tweening. Financial figures appear instantly. `prefers-reduced-motion` collapses all transitions to 0ms/instant.

**Named references:**
- **Screener.in** -- citation philosophy, table density
- **Tickertape SmartScore** -- severity badge anatomy
- **Linear.app** -- citation chip -> hover card -> detail drawer pattern
- **Bloomberg Terminal** -- dark mode color authority, monospaced figures
- **Stripe Docs** -- typographic restraint, neutral surfaces
- **Sensibull** -- SEBI registration number prominence, regulatory trust signals

---

## 2. Reference Landscape -- 2026 India Finance / Regtech UI Bar

### 2.1 Live Products Audited

**Tickertape (tickertape.in)**
URL: https://www.tickertape.in
Takeaway: SmartScore badge is the strongest trust-scoring pattern in Indian retail fintech -- color + icon + number in a contained pill/badge, immediately scannable. Anti-pattern observed: heavy promotional banner ads and excessive footer density. P2 takes the badge system without the promotional noise.

**Screener.in (screener.in)**
URL: https://www.screener.in
Takeaway: Every financial number traces to an attributed source (C-MOTS data + exchange filings). The citation chain is the trust signal, not visual polish. The 2025 design is dated (minimal hover states, no motion, flat tables) but the information architecture is correct -- P2 should match this citation philosophy with modern execution.

**Tijori Finance (tijorifinance.com)**
URL: https://tijorifinance.com
Takeaway: Promoter-buying and insider-tracking as categorical tools. Their card-based groupings (Promoter Buying / Whales / Capex Fundamentals) map well to P2's red-flag categories. Anti-pattern: upgrade prompts interrupt the research flow; P2 is free-tier so this does not apply, but the lesson is: never gate critical disclosure context.

**Sensibull (sensibull.com)**
URL: https://sensibull.com
Takeaway: SEBI RA registration number (INH200006895) displayed prominently in the header alongside product claims. This is the right pattern -- regulatory credential placement signals legitimacy before the user reads a single data point. P2 should display "Analysis based on public SEBI filings" in an equivalent position.

**Zerodha Varsity (zerodha.com/varsity)**
URL: https://zerodha.com/varsity
Takeaway: Author attribution ("created by Karthik Rangappa at Zerodha") + "no signup, no paywall" framing creates institutional trust through transparency. P2 equivalent: "Data sourced from sebi.gov.in public filings" with direct URLs -- no mystery about where the numbers come from.

**Groww (groww.in)**
URL: https://groww.in
Takeaway: Consumer-friendly green palette, clean card layout, optimistic framing. This is the anti-pattern for P2 -- Groww's visual language signals "investing is easy and fun." P2 signals "this is serious analysis." Different product jobs; different visual register.

**Phenomenon Studio Fintech Trust Patterns**
URL: https://phenomenonstudio.com/article/fintech-ux-design-patterns-that-build-trust-and-credibility/
Takeaway: Research confirms that "interfaces adhering to strict grid layouts score 17% higher on perceived professionalism metrics." Consistent grids + whitespace + monochrome surfaces = authority. P2 uses an 8-column desktop grid with consistent 24px gutters.

**shadcn/ui Luma Foundation**
URL: https://ui.shadcn.com/docs/changelog/2026-03-luma
Takeaway: Luma -- released March 2026 -- introduces "softer surfaces, more open spacing, calmer visual rhythm." This is the right starting point for P2's component base. The "breathable layouts + soft elevation" language aligns with audit-report density. P2 uses `--preset luma` as the component baseline, then tightens to Linear-density for data tables.

### 2.2 What Trust-Signaling Patterns These Products Share

| Signal | How it appears | P2 implementation |
|--------|----------------|-------------------|
| Regulatory provenance | Data attribution in footer / header | Persistent "Source: sebi.gov.in" ribbon per report |
| Structured grid layout | 8-12 column grids, consistent gutters | 8-column desktop, 4-column tablet, 1-column mobile |
| Monospaced financial figures | font-variant-numeric tabular-nums | All INR/percentage figures use Geist Mono |
| Minimal saturated color | Color only for alerts / gains / losses | Color only on severity badges and status indicators |
| Explicit disclaimer placement | Footer + inline near risky content | Sticky banner + every card footer + first-run modal |
| Source URL availability | Links to exchange filings | Every citation chip links to sebi.gov.in source |

### 2.3 Where They All Fail (P2 must fix)

- **Zero distinction between extracted fact and AI synthesis.** Screener.in and Tickertape display data as if it were unmediated truth. P2 must visually separate verbatim DRHP quotes from LLM-generated analysis.
- **No drill-down to source page.** None of these products let you click a number and land on the exact page of the filing that produced it. P2's PDF viewer with highlighted chunk is a category-level UX improvement.
- **Dismissable disclaimers.** Several products have cookie-banner-style disclaimers users dismiss on first visit and never see again. P2's disclaimer is sticky, non-dismissable, always visible.
- **Severity without context.** Tickertape's SmartScore gives you a number (6.2/10) without explaining what components drove it. P2 shows the severity badge AND the specific finding that earned that severity AND the source page.

---

## 3. Design Tokens

### 3.1 Light Mode

```json
{
  "color": {
    "bg": {
      "base": "oklch(0.985 0.003 240)",
      "comment": "Off-white with cool blue cast. Almost white, never stark white."
    },
    "surface": {
      "default": "oklch(0.976 0.004 240)",
      "elevated": "oklch(1.000 0.000 0)",
      "comment": "Cards sit on base. Modals/dropdowns use pure white for separation."
    },
    "border": {
      "default": "oklch(0.906 0.007 240)",
      "strong": "oklch(0.820 0.012 240)"
    },
    "fg": {
      "primary": "oklch(0.160 0.010 245)",
      "secondary": "oklch(0.380 0.008 245)",
      "muted": "oklch(0.520 0.006 240)",
      "subtle": "oklch(0.680 0.004 240)"
    },
    "accent": {
      "default": "oklch(0.520 0.155 248)",
      "subtle": "oklch(0.940 0.040 248)",
      "fg": "oklch(1.000 0.000 0)"
    },
    "severity": {
      "critical": {
        "card-bg": "oklch(0.968 0.018 25)",
        "card-border": "oklch(0.868 0.075 25)",
        "badge-bg": "oklch(0.456 0.195 25)",
        "badge-fg": "oklch(0.975 0.005 0)",
        "contrast-ratio": "~9:1 AAA"
      },
      "high": {
        "card-bg": "oklch(0.968 0.022 48)",
        "card-border": "oklch(0.868 0.085 48)",
        "badge-bg": "oklch(0.496 0.185 48)",
        "badge-fg": "oklch(0.975 0.005 0)",
        "contrast-ratio": "~8:1 AAA"
      },
      "moderate": {
        "card-bg": "oklch(0.968 0.022 78)",
        "card-border": "oklch(0.870 0.082 78)",
        "badge-bg": "oklch(0.540 0.160 78)",
        "badge-fg": "oklch(0.975 0.005 0)",
        "contrast-ratio": "~5.5:1 AA"
      },
      "none": {
        "card-bg": "oklch(0.968 0.018 148)",
        "card-border": "oklch(0.862 0.070 148)",
        "badge-bg": "oklch(0.456 0.148 148)",
        "badge-fg": "oklch(0.975 0.005 0)",
        "contrast-ratio": "~9:1 AAA"
      }
    },
    "disclaimer": {
      "bg": "oklch(0.974 0.016 78)",
      "border": "oklch(0.860 0.082 78)",
      "fg": "oklch(0.380 0.082 78)"
    },
    "refusal": {
      "bg": "oklch(0.972 0.010 25)",
      "border": "oklch(0.840 0.060 25)",
      "fg": "oklch(0.420 0.140 25)"
    },
    "extracted-fact": {
      "bg": "oklch(0.972 0.006 240)",
      "border-left": "oklch(0.520 0.155 248)",
      "fg": "oklch(0.160 0.010 245)"
    },
    "skeleton": {
      "base": "oklch(0.920 0.006 240)",
      "shimmer": "oklch(0.948 0.004 240)"
    }
  },
  "type": {
    "scale": {
      "display":  { "size": "24px", "line": "28px", "weight": "600", "family": "Inter Variable" },
      "title-lg": { "size": "18px", "line": "24px", "weight": "600", "family": "Inter Variable" },
      "title-md": { "size": "15px", "line": "20px", "weight": "500", "family": "Inter Variable" },
      "body":     { "size": "14px", "line": "20px", "weight": "400", "family": "Inter Variable" },
      "body-sm":  { "size": "13px", "line": "18px", "weight": "400", "family": "Inter Variable" },
      "caption":  { "size": "12px", "line": "16px", "weight": "400", "family": "Inter Variable" },
      "label":    { "size": "11px", "line": "14px", "weight": "600", "family": "Inter Variable", "tracking": "0.5px", "transform": "uppercase" },
      "figure-lg": { "size": "16px", "line": "24px", "weight": "500", "family": "Geist Mono", "numeric": "tabular-nums lining-nums" },
      "figure-md": { "size": "14px", "line": "20px", "weight": "400", "family": "Geist Mono", "numeric": "tabular-nums lining-nums" },
      "figure-sm": { "size": "12px", "line": "16px", "weight": "400", "family": "Geist Mono", "numeric": "tabular-nums lining-nums" }
    },
    "family": {
      "sans": "'Inter Variable', system-ui, -apple-system, sans-serif",
      "mono": "'Geist Mono', 'IBM Plex Mono', ui-monospace, monospace"
    },
    "note": "font-feature-settings: 'tnum' 1, 'lnum' 1 on all figure-* elements. Never tween numbers."
  },
  "space": [0, 2, 4, 6, 8, 10, 12, 16, 20, 24, 32, 40, 48, 56, 64, 80, 96, 128],
  "radius": {
    "none": "0px",
    "sm": "4px",
    "md": "6px",
    "lg": "10px",
    "xl": "14px",
    "full": "9999px"
  },
  "shadow": {
    "sm": "0 1px 2px oklch(0.15 0.010 240 / 0.05)",
    "md": "0 2px 6px oklch(0.15 0.010 240 / 0.07), 0 1px 2px oklch(0.15 0.010 240 / 0.04)",
    "lg": "0 8px 20px oklch(0.15 0.010 240 / 0.09), 0 2px 6px oklch(0.15 0.010 240 / 0.05)",
    "xl": "0 16px 40px oklch(0.15 0.010 240 / 0.12), 0 4px 10px oklch(0.15 0.010 240 / 0.07)"
  },
  "motion": {
    "duration": {
      "fast": "120ms",
      "base": "220ms",
      "slow": "320ms",
      "progress": "600ms"
    },
    "easing": {
      "standard":    "cubic-bezier(0.4, 0, 0.2, 1)",
      "decelerate":  "cubic-bezier(0.0, 0.0, 0.2, 1)",
      "accelerate":  "cubic-bezier(0.4, 0, 1.0, 1)"
    },
    "forbidden": [
      "Number tweening -- financial figures must appear instantly",
      "Parallax scrolling",
      "Scroll-jacking",
      "Spring physics",
      "Bounce easing",
      "Confetti / celebration animations"
    ]
  }
}
```

### 3.2 Dark Mode Tokens (Bloomberg Terminal)

```json
{
  "dark": {
    "bg-base":         "oklch(0.120 0.012 242)",
    "surface-default": "oklch(0.162 0.012 242)",
    "surface-elevated":"oklch(0.200 0.012 242)",
    "border-default":  "oklch(0.272 0.014 242)",
    "border-strong":   "oklch(0.360 0.016 242)",
    "fg-primary":      "oklch(0.935 0.006 240)",
    "fg-secondary":    "oklch(0.740 0.008 240)",
    "fg-muted":        "oklch(0.560 0.008 240)",
    "fg-subtle":       "oklch(0.400 0.006 240)",
    "accent-default":  "oklch(0.650 0.150 250)",
    "accent-subtle":   "oklch(0.220 0.040 248)",
    "severity": {
      "critical": { "card-bg": "oklch(0.178 0.032 25)",  "card-border": "oklch(0.340 0.120 25)",  "badge-bg": "oklch(0.520 0.200 25)",  "badge-fg": "oklch(0.975 0.005 0)" },
      "high":     { "card-bg": "oklch(0.178 0.036 48)",  "card-border": "oklch(0.344 0.120 48)",  "badge-bg": "oklch(0.560 0.185 48)",  "badge-fg": "oklch(0.975 0.005 0)" },
      "moderate": { "card-bg": "oklch(0.178 0.034 78)",  "card-border": "oklch(0.346 0.115 78)",  "badge-bg": "oklch(0.610 0.160 78)",  "badge-fg": "oklch(0.120 0.012 242)" },
      "none":     { "card-bg": "oklch(0.178 0.030 148)", "card-border": "oklch(0.338 0.112 148)", "badge-bg": "oklch(0.516 0.158 148)", "badge-fg": "oklch(0.975 0.005 0)" }
    },
    "disclaimer": { "bg": "oklch(0.192 0.028 78)", "border": "oklch(0.380 0.100 78)", "fg": "oklch(0.780 0.100 78)" },
    "extracted-fact": { "bg": "oklch(0.188 0.012 242)", "border-left": "oklch(0.650 0.150 250)", "fg": "oklch(0.880 0.008 240)" },
    "skeleton": { "base": "oklch(0.220 0.012 242)", "shimmer": "oklch(0.256 0.012 242)" }
  }
}
```

### 3.3 Tailwind 4 CSS Variables (globals.css)

```css
@import "tailwindcss";
@import "tw-animate-css";

@theme inline {
  --font-sans: "Inter Variable", system-ui, -apple-system, sans-serif;
  --font-mono: "Geist Mono", "IBM Plex Mono", ui-monospace, monospace;

  --color-bg:              var(--bg-base);
  --color-surface:         var(--surface-default);
  --color-surface-elevated:var(--surface-elevated);
  --color-border:          var(--border-default);
  --color-fg:              var(--fg-primary);
  --color-fg-secondary:    var(--fg-secondary);
  --color-fg-muted:        var(--fg-muted);
  --color-fg-subtle:       var(--fg-subtle);
  --color-accent:          var(--accent-default);
  --color-accent-subtle:   var(--accent-subtle);

  --duration-fast:     120ms;
  --duration-base:     220ms;
  --duration-slow:     320ms;
  --duration-progress: 600ms;
  --ease-standard:   cubic-bezier(0.4, 0, 0.2, 1);
  --ease-decelerate: cubic-bezier(0.0, 0.0, 0.2, 1);
  --ease-accelerate: cubic-bezier(0.4, 0, 1.0, 1);

  --radius-sm:   4px;
  --radius-md:   6px;
  --radius-lg:   10px;
  --radius-xl:   14px;
  --radius-full: 9999px;
}

:root {
  --bg-base:         oklch(0.985 0.003 240);
  --surface-default: oklch(0.976 0.004 240);
  --surface-elevated:oklch(1.000 0.000 0);
  --border-default:  oklch(0.906 0.007 240);
  --border-strong:   oklch(0.820 0.012 240);
  --fg-primary:      oklch(0.160 0.010 245);
  --fg-secondary:    oklch(0.380 0.008 245);
  --fg-muted:        oklch(0.520 0.006 240);
  --fg-subtle:       oklch(0.680 0.004 240);
  --accent-default:  oklch(0.520 0.155 248);
  --accent-subtle:   oklch(0.940 0.040 248);

  --severity-critical-card-bg:    oklch(0.968 0.018 25);
  --severity-critical-card-border:oklch(0.868 0.075 25);
  --severity-critical-badge-bg:   oklch(0.456 0.195 25);
  --severity-critical-badge-fg:   oklch(0.975 0.005 0);
  --severity-high-card-bg:        oklch(0.968 0.022 48);
  --severity-high-card-border:    oklch(0.868 0.085 48);
  --severity-high-badge-bg:       oklch(0.496 0.185 48);
  --severity-high-badge-fg:       oklch(0.975 0.005 0);
  --severity-moderate-card-bg:    oklch(0.968 0.022 78);
  --severity-moderate-card-border:oklch(0.870 0.082 78);
  --severity-moderate-badge-bg:   oklch(0.540 0.160 78);
  --severity-moderate-badge-fg:   oklch(0.975 0.005 0);
  --severity-none-card-bg:        oklch(0.968 0.018 148);
  --severity-none-card-border:    oklch(0.862 0.070 148);
  --severity-none-badge-bg:       oklch(0.456 0.148 148);
  --severity-none-badge-fg:       oklch(0.975 0.005 0);

  --disclaimer-bg:     oklch(0.974 0.016 78);
  --disclaimer-border: oklch(0.860 0.082 78);
  --disclaimer-fg:     oklch(0.380 0.082 78);
  --refusal-bg:        oklch(0.972 0.010 25);
  --refusal-border:    oklch(0.840 0.060 25);
  --refusal-fg:        oklch(0.420 0.140 25);
  --extracted-fact-bg: oklch(0.972 0.006 240);
  --extracted-fact-border: oklch(0.520 0.155 248);
  --skeleton-base:     oklch(0.920 0.006 240);
  --skeleton-shimmer:  oklch(0.948 0.004 240);
}

.dark {
  --bg-base:         oklch(0.120 0.012 242);
  --surface-default: oklch(0.162 0.012 242);
  --surface-elevated:oklch(0.200 0.012 242);
  --border-default:  oklch(0.272 0.014 242);
  --border-strong:   oklch(0.360 0.016 242);
  --fg-primary:      oklch(0.935 0.006 240);
  --fg-secondary:    oklch(0.740 0.008 240);
  --fg-muted:        oklch(0.560 0.008 240);
  --fg-subtle:       oklch(0.400 0.006 240);
  --accent-default:  oklch(0.650 0.150 250);
  --accent-subtle:   oklch(0.220 0.040 248);

  --severity-critical-card-bg:    oklch(0.178 0.032 25);
  --severity-critical-card-border:oklch(0.340 0.120 25);
  --severity-critical-badge-bg:   oklch(0.520 0.200 25);
  --severity-critical-badge-fg:   oklch(0.975 0.005 0);
  --severity-high-card-bg:        oklch(0.178 0.036 48);
  --severity-high-card-border:    oklch(0.344 0.120 48);
  --severity-high-badge-bg:       oklch(0.560 0.185 48);
  --severity-high-badge-fg:       oklch(0.975 0.005 0);
  --severity-moderate-card-bg:    oklch(0.178 0.034 78);
  --severity-moderate-card-border:oklch(0.346 0.115 78);
  --severity-moderate-badge-bg:   oklch(0.610 0.160 78);
  --severity-moderate-badge-fg:   oklch(0.120 0.012 242);
  --severity-none-card-bg:        oklch(0.178 0.030 148);
  --severity-none-card-border:    oklch(0.338 0.112 148);
  --severity-none-badge-bg:       oklch(0.516 0.158 148);
  --severity-none-badge-fg:       oklch(0.975 0.005 0);

  --disclaimer-bg:     oklch(0.192 0.028 78);
  --disclaimer-border: oklch(0.380 0.100 78);
  --disclaimer-fg:     oklch(0.780 0.100 78);
  --refusal-bg:        oklch(0.196 0.020 25);
  --refusal-border:    oklch(0.360 0.090 25);
  --refusal-fg:        oklch(0.720 0.120 25);
  --extracted-fact-bg: oklch(0.188 0.012 242);
  --extracted-fact-border: oklch(0.650 0.150 250);
  --skeleton-base:     oklch(0.220 0.012 242);
  --skeleton-shimmer:  oklch(0.256 0.012 242);
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

---

## 4. Flow Maps

### F1 -- Upload DRHP PDF (new corpus)

```
[Landing page -- two panels side-by-side]
  Left:  UploadDropzone (empty state)
  Right: Pre-indexed corpus browse (always available, instant)

USER DROPS FILE or CLICKS TO BROWSE
  Client validation:
    - Not a PDF     -> error: "Please upload a PDF file"
    - > 200 MB      -> error: "File too large. Max 200 MB."
  File uploads to Vercel Edge -> Supabase Storage -> returns job_id

[UploadDropzone: uploading state]
  File name + size
  LinearProgress aria-valuenow
  Cancel button

UPLOAD COMPLETE (< 5s) -- API returns { job_id, company_name_guess, page_count }

[UploadDropzone: parsing-in-progress]
  Company name (from Docling first-pass or filename)
  Multi-step progress:
    Step 1 "Parsing document" (active, ~8-12 min)
    Step 2 "Extracting sections" (pending)
    Step 3 "Generating embeddings" (pending)
    Step 4 "Analysis ready" (pending)
  aria-live="assertive" announces each step transition
  "Notify me by email when ready" inline input
  Polling: GET /api/job/[id]/status every 10s

BACKGROUND (Modal.com):
  Docling -> chunk -> contextual prefix -> voyage-3-large -> pgvector upsert -> webhook

INGESTION COMPLETE
[UploadDropzone: parsed state]
  CheckCircle icon + "Analysis ready"
  Company name, page count, section count, filing date
  Primary CTA: "View Red-Flag Report" -> /report/[drhp_id]
  Secondary: "Upload another"

ERROR STATES:
  Network failure  -> "Upload failed" + retry + copy error
  Docling failure  -> "Unable to parse this PDF. Try the SEBI source directly: [link]"
  Partial parse    -> Proceed with warning badge: "Analysis may be incomplete"
```

### F2 -- Pre-indexed Corpus Browse (instant)

```
[Landing: Browse section]
  Command search: "Search by company, sector, or filing year..."
  DRHPCard grid (2-col desktop, 1-col mobile)
    Card fields: company name, sector badge, filing date, pages, "Instant" badge
    SME flag shown with orange badge + tooltip disclaimer
  CLICK -> /report/[drhp_id]
  Report renders in < 3s (data already in pgvector)
```

### F3 -- View Red-Flag Report

```
/report/[drhp_id]

[DisclaimerBanner -- sticky top, always visible]

[Report Header]
  Company name (display) | Sector badge | SME badge?
  DRHP filed: Sep 2024  |  Analysis: 14 May 2026  |  Pages: 800
  Source ribbon: sebi.gov.in/... [external link]
  Summary pills: 2 CRITICAL  3 HIGH  4 MODERATE  1 NONE

[Layout: sidebar 240px + main flex-1]
  SIDEBAR:
    Severity Filter (group): CRITICAL(2) / HIGH(3) / MODERATE(4) / NONE(1)
    Section Navigation: -> Promoter Risk / Litigation / Fund Use / Revenue

  MAIN:
    TABS: Promoter Risk | Litigation | Fund Use | Revenue Concentration
    Content: RedFlagCards sorted CRITICAL first
    Streaming: per-section Skeleton (3 cards) while agent runs
    aria-live="polite" announces "Promoter Risk analysis complete -- 2 findings."

[Footer] -- "Not investment advice. Not affiliated with SEBI."
```

### F4 -- Citation -> PDF Viewer

```
CitationChip [Page 187]
  HOVER (300ms delay) -> HoverCard:
    "Swiggy DRHP * Objects of Issue * Page 187"
    First 200 chars of chunk text
    [View in document ->]

  CLICK / "View in document":
    Desktop >= 768px -> Dialog opens (max-w 960px)
    Mobile < 768px   -> Sheet opens (bottom, 85dvh)
    
    Dialog/Sheet content:
      [X] Close  |  Page 187 of 800  |  [<- Prev] [2 of 5] [Next ->]
      react-pdf-highlighter-extended renders PDF
      Yellow highlight: oklch(0.95 0.12 90 / 0.6)
      [Open SEBI source ->]

  Focus management:
    Opens  -> focus on close button
    Closes -> focus returns to triggering CitationChip
    Keyboard: Escape = close, Arrow keys = prev/next highlight
```

### F5 -- Cross-DRHP Comparison (v2 stretch)

```
/compare?a=[id1]&b=[id2]
  Comparison table: 8 metrics x 2 columns
  Metrics: Promoter Pledge % / Litigation Count / Contingent Liability /
           OFS % / Promoter Debt Repayment % / Top Customer Concentration /
           SEBI Investigations / Aggregate Risk Level
  Higher-risk cell: severity token bg applied
  No sparklines, no charts -- audit table only
```

### F6 -- Out-of-Scope Query Refusal

```
TRIGGER: query matches PROHIBITED_QUERY_PATTERNS regex
  ("should i invest", "target price", "overvalued", "listing gain", etc.)

RESPONSE: RefusalCard (never LLM output)
  [StopCircle icon] "This query is outside this tool's scope"
  Explanation of scope
  List: what the tool CAN analyze (3 bullets)
  "SEBI helpline: 1800-266-7575"

Visual: refusal-* tokens (soft red). NOT an error card. Deliberate.
```

---

## 5. Component Specifications

### 5.1 UploadDropzone -- 6 States

| State | Border | Background | Copy | Interactive |
|-------|--------|------------|------|-------------|
| empty | dashed border-default 2px | bg-base | "Drag & drop DRHP PDF" | click/drop |
| hovered (drag-over) | solid accent 2px | accent-subtle | "Drop to begin analysis" | drop |
| uploading | solid border-default | surface | filename + "Uploading 67%" + Cancel | cancel |
| parsing-in-progress | solid border-default | surface | step labels + ETA + email notify | email input |
| parsed/complete | solid none-card-border 2px | none-card | "Analysis ready" + metadata | CTA to report |
| error | solid critical-card-border 2px | critical-card | error message | retry |

Keyboard alt for drag: `<input type="file" accept="application/pdf">` triggered by click/Enter/Space.

ARIA:
```
<div role="button" aria-label="Upload DRHP PDF. Click or drag and drop." tabIndex={0}>
<div role="progressbar" aria-valuenow={n} aria-valuemin={0} aria-valuemax={100} aria-label="Ingestion progress">
<p aria-live="assertive">{currentStepLabel} -- {etaMinutes} minutes remaining</p>
```

### 5.2 DRHPCard -- 6 States

| State | Shadow | Border | Background | Special |
|-------|--------|--------|------------|---------|
| default | sm | border-default | surface | -- |
| hovered | md | border-strong | surface | scale 1.0 (no transform on finance cards) |
| selected | md | accent 2px | accent-subtle | -- |
| pre-indexed | sm | none-card-border | none-card | "Instant" green pill badge |
| sme-ipo | sm | moderate-card-border | moderate-card | "SME IPO" amber + tooltip |
| loading | none | border-default | surface | Skeleton fills content area |

Transition: border-color 120ms, box-shadow 120ms, background-color 120ms -- all ease-standard.

### 5.3 ReportShell

Desktop layout:
```
sticky top: DisclaimerBanner (40px)
header:     company + source provenance ribbon
layout:     sidebar(240px fixed) | main(flex-1)
sidebar:    severity filter (checkboxes) + section nav
main:       Tabs (tablist/tab/tabpanel) + RedFlagCard grid + streaming skeletons
footer:     disclaimer repeat
```

Mobile (<768px): sidebar becomes bottom Drawer. Tabs scroll horizontally. Filter = "Filter" button bottom drawer. No sticky sidebar.

ARIA:
```
<div role="tablist" aria-label="Report sections">
  <button role="tab" aria-selected aria-controls="panel-promoter">Promoter Risk</button>
</div>
<div role="tabpanel" id="panel-promoter" aria-labelledby="tab-promoter">...</div>
<div aria-live="polite" aria-atomic="false" className="sr-only">{streamingAnnouncement}</div>
<div aria-live="polite" aria-atomic="true" className="sr-only">Showing {count} findings</div>
```

### 5.4 RedFlagCard -- 8 States

| State | Description |
|-------|-------------|
| collapsed-default | SeverityBadge + headline + 2-line summary + citation chips |
| collapsed-hovered | md shadow, border more opaque |
| expanded | full detail: verbatim block + analysis prose + all citations + agent attribution |
| loading/streaming | 3-line Skeleton for headline + summary |
| error | "Finding could not be extracted. Agent returned error." |
| cited-active | CitationChip active, PDF viewer triggered |
| no-finding (NONE) | "No material risk identified in this category" |
| sme-warning | additional disclaimer overlay if is_sme_ipo |

Key structural rule: SeverityBadge lives OUTSIDE AccordionTrigger. It must be visible at all times, collapsed or expanded.

Verbatim quote block:
```
bg:          --extracted-fact-bg
border-left: 3px solid --extracted-fact-border (accent blue)
font:        mono, body-sm
label:       "DRHP Source (verbatim)" in label type (caption/600/uppercase)
page ref:    right-aligned in figure-sm Geist Mono
```

LLM analysis:
```
label: "Analysis" italic in label type
text:  body italic, fg-secondary
NEVER mixed with verbatim block in same paragraph
```

ARIA:
```
<article aria-label="{severity} severity: {headline}">
  <button aria-expanded aria-controls="detail-{id}" aria-label="Expand: {headline}">
  <div id="detail-{id}" hidden={!expanded}>
```

### 5.5 CitationChip -- 5 States

| State | Behavior |
|-------|----------|
| default | page number in figure-sm Geist Mono, border-default |
| hovered | HoverCard opens after 300ms, border accent, bg accent-subtle |
| active (HoverCard open) | HoverCard visible |
| clicked | PDF viewer triggered (Sheet mobile / Dialog desktop) |
| loading | Skeleton inside HoverCard while chunk loads |

HoverCard content: company + section + page + first 200 chars + "View in document" CTA.
Mobile: HoverCard replaced by bottom-sheet mini-preview (separate component).
Min touch target: 44x44px via generous padding.

ARIA:
```
<button aria-label="Citation: {company} DRHP, {section}, page {n}. Press to view in document." aria-haspopup="dialog">
  <span aria-hidden>{icon}</span>
  <span>Page {n}</span>
</button>
```

### 5.6 SeverityBadge -- 4 Variants

Always: icon + color + text label (triple signal for colorblind users and screen readers).

| Variant | Icon (Lucide) | Label | Contrast |
|---------|---------------|-------|----------|
| CRITICAL | AlertTriangle | CRITICAL | ~9:1 AAA |
| HIGH | AlertCircle | HIGH | ~8:1 AAA |
| MODERATE | Info | MODERATE | ~5.5:1 AA |
| NONE | CheckCircle | NONE | ~9:1 AAA |

Shape: rounded-full, px-2 py-0.5, label text 11px/600/uppercase/0.5px tracking.

ARIA: `<span role="img" aria-label="Severity: {level}">` with icon aria-hidden.

### 5.7 PDFViewer (react-pdf-highlighter-extended) -- 5 States

| State | Display |
|-------|---------|
| loading | Skeleton + DocumentText icon centered |
| ready | PDF rendered, chunk highlighted oklch(0.95 0.12 90 / 0.6) |
| multi-highlight | Multiple highlights, prev/next nav |
| error | "Unable to load PDF. SEBI source may be temporarily unavailable." + direct link |
| page-not-found | Graceful: "Page {n} not found in this document" |

Desktop: Dialog max-w-[960px].
Mobile: Sheet side="bottom" height 85dvh, drag handle, swipe-to-dismiss.
Focus: opens -> close button. Closes -> triggering CitationChip.
Keyboard: Escape=close, ArrowLeft/Right=prev/next highlight.

ARIA:
```
<div role="dialog" aria-modal="true"
  aria-label="DRHP PDF viewer: {company}, page {current}"
  aria-describedby="pdf-viewer-desc">
<p id="pdf-viewer-desc" className="sr-only">
  Page {current} of {total}. {count} highlights. Use Previous/Next to navigate.
</p>
```

### 5.8 DisclaimerBanner -- Always Visible

```
position: sticky top-0 z-50
height: 40px min (expands on mobile tap)
bg: --disclaimer-bg
border-bottom: 1px solid --disclaimer-border
color: --disclaimer-fg
icon: Info 14px
```

Exact copy (never shorten):
"Analysis based on public SEBI filings. Educational use only. Not investment advice. Not affiliated with SEBI. Consult a SEBI-registered adviser before investing."

Placement: ReportShell sticky header + every RedFlagCard footer (caption, fg-muted) + first-run modal + page footer.

ARIA: `<aside role="note" aria-label="Legal disclaimer">`
NOT role="alert" -- note is correct for persistent informational content.

Mobile: 1-line truncation visible always, tap to expand full 3-line text, tap to collapse. Never dismissable.

### 5.9 RefusalCard -- 2 States (triggered / not-rendered)

Triggered when: query matches PROHIBITED_QUERY_PATTERNS.

```
border-left: 3px solid --refusal-fg
bg:          --refusal-bg
border:      --refusal-border

Icon: StopCircle (refusal-fg)
Title: "This query is outside this tool's scope"  [body, refusal-fg]
Body: explanation prose                            [body-sm, fg-secondary]
List: 3 bullets of what tool CAN do              [body-sm]
Footer: SEBI helpline in figure-sm mono           [fg-muted]
```

Visual intent: deliberate, not broken. The tool working correctly by declining.
ARIA: `<div role="status" aria-live="polite" aria-label="Query outside tool scope">`

### 5.10 AgentTraceCard (v2) -- 2 States (collapsed / expanded)

Collapsed (single line):
"Identified by Promoter Pledge Extractor * Confidence 0.82 * [Expand]"

Expanded:
Agent name, model (claude-haiku-4-5), confidence meter (linear bar, accent fill),
chunks analyzed, sections queried, run time.

Confidence meter: NOT a percentage number that tweens -- static width bar.
ARIA: confidence bar is `role="meter" aria-valuenow aria-valuemin aria-valuemax aria-label="Confidence: 0.82"`.

---

## 6. WCAG 2.2 AA Accessibility

### 6.1 Contrast Audit

| Combination | Ratio | Level |
|-------------|-------|-------|
| fg-primary on bg-base (light) | ~15:1 | AAA |
| fg-primary on bg-base (dark) | ~16:1 | AAA |
| fg-muted on bg-base (light) | ~5:1 | AA |
| Critical badge-fg on badge-bg | ~9:1 | AAA |
| High badge-fg on badge-bg | ~8:1 | AAA |
| Moderate badge-fg on badge-bg | ~5.5:1 | AA |
| None badge-fg on badge-bg | ~9:1 | AAA |
| accent on surface (links) | ~5.5:1 | AA |
| All financial figures (fg-secondary on surface) | ~6:1 | AA+ |

### 6.2 Focus Order

```
1. Skip-to-main-content (sr-only, visible on focus)
2. DisclaimerBanner aside (non-interactive, SR reads on load)
3. Source link in report header
4. Severity filter checkboxes (CRITICAL -> HIGH -> MODERATE -> NONE)
5. Section tabs (Promoter -> Litigation -> Fund Use -> Revenue)
6. Within active tab:
   Per card: expand/collapse button -> citation chips -> external links
   Between cards: natural document order
7. Footer links

PDF viewer (focus trap):
  close button -> prev-highlight -> next-highlight -> open-source-link
  Escape: closes, focus returns to triggering CitationChip
```

### 6.3 Screen Reader Narrative (linear)

1. "Note: Analysis based on public SEBI filings. Educational use only. Not investment advice."
2. "Swiggy Limited, Food-tech. DRHP September 2024. Analysis 14 May 2026. 800 pages. Source sebi.gov.in."
3. "Report summary: 2 critical, 3 high, 4 moderate, 1 none."
4. "Filter by severity group. Critical checked. High checked. Moderate checked. None checked."
5. "Promoter Risk, selected tab, 1 of 4."
6. "Critical severity: Promoter entities pledged 78.2% of holdings. [summary]. 3 citations. Expand button collapsed."
7. [user expands] "Expanded. DRHP Source verbatim: [quote] Page 187. Analysis: [prose]. Sources: Page 187, Page 234."

### 6.4 ARIA Live Regions

```
Ingestion progress:    aria-live="assertive" -- user is actively waiting
Streaming report:      aria-live="polite"    -- user not waiting actively
Filter result count:   aria-live="polite"    -- informational update
Refusal card:          aria-live="polite"    -- deliberate, not urgent
```

### 6.5 Touch Targets

All interactive elements: minimum 44x44px (WCAG 2.5.5 AAA).
CitationChips: min-height 32px visible + 6px padding above/below = 44px touch target.
Severity filter checkboxes: size-5 checkbox + gap-3 label = 44px tap zone.
Tab buttons on mobile: explicit min-height 44px.
Expand buttons: size-8 icon + p-2 padding = 48x48px.

### 6.6 Reduced-Motion

```css
@media (prefers-reduced-motion: reduce) {
  .skeleton-shimmer { animation: none; background: var(--skeleton-base); }
  [data-radix-accordion-content] { transition: none; }
  [data-state="open"] { animation: none; }
  .progress-spinner { display: none; }
  .progress-text { display: block; }
}
```

Numbers NEVER tween regardless of motion preference -- they always appear instantly.

---

## 7. shadcn/ui v4 + Radix Mapping

| P2 Component | shadcn/ui Primitive | Notes |
|---|---|---|
| Section tabs | Tabs + TabsList + TabsTrigger + TabsContent | orientation="horizontal", horizontal scroll mobile |
| RedFlagCard expand | Accordion type="multiple" | SeverityBadge OUTSIDE AccordionTrigger |
| DRHP card | Card + CardHeader + CardContent | No footer |
| Severity badges | Badge with cva variants | Custom severity colors via CSS vars |
| Citation hover (desktop) | HoverCard | openDelay=300, side="top" |
| Citation tap (mobile) | Sheet side="bottom" | Separate mobile component |
| PDF viewer (desktop) | Dialog max-w-[960px] | focus-trap |
| PDF viewer (mobile) | Sheet side="bottom" 85dvh | drag handle, swipe-dismiss |
| Severity filter desktop | Checkbox + Label in div[role="group"] | Always visible |
| Severity filter mobile | Drawer (Vaul) side="bottom" | Triggered by "Filter" button |
| Ingestion progress | Progress | aria-valuenow wired |
| Loading states | Skeleton | Per-section, not full-page |
| Disclaimer banner | Alert (modified) | No X button -- non-dismissable |
| DRHP search | Command + CommandInput + CommandList | Client-side filter |
| First-run modal | Dialog | Non-dismissable until "I understand" |
| Refusal card | Alert variant="destructive" (modified) | refusal-* token colors |

Init command: `npx shadcn@latest init --preset luma`
Then override CSS variables with P2 tokens. Keep Luma geometry unchanged.
Geist Mono: `import { Geist_Mono } from "next/font/google"`

---

## 8. Trust Visual Signals

### 8.1 Disclaimer Placement (non-negotiable)

1. Sticky header banner: position sticky, top-0, z-50, always visible, 40px height, never dismissable.
2. Every RedFlagCard footer: 11px caption, fg-muted, "Source: public SEBI filing. Educational use only."
3. First-run DisclaimerModal: fires on first /report/* visit (localStorage key "drhp_disclaimer_v1"). Button: "I understand, proceed to analysis." Not "Accept." Not "Dismiss."
4. PDF Viewer header: single line above PDF: "Showing source document. Not investment advice."
5. Page footer: full disclaimer text.

### 8.2 Source Provenance Ribbon (in report header)

```
[sebi.gov.in icon] Source: SEBI DRHP filing, sebi.gov.in -- public document
                   [View original filing ->] (external link, opens new tab)
```

Appears immediately below company name. Every data point downstream traces here.

### 8.3 Extracted Fact vs LLM Synthesis

Verbatim quote block:
- bg: --extracted-fact-bg (cool near-white)
- border-left: 3px --extracted-fact-border (accent blue)
- font: Geist Mono, body-sm
- label: "DRHP Source (verbatim)" -- caption/600/uppercase
- page ref: right-aligned Geist Mono figure-sm

LLM analysis:
- label: "Analysis" -- italic, caption/600/uppercase, fg-muted
- text: body italic, fg-secondary
- these two blocks must NEVER be visually merged

### 8.4 No-Verdict Rule

Strictly prohibited:
- Composite scores ("Risk Score: 3.2/10")
- Overall verdict tiles ("High risk IPO")
- Color-coded company name
- Any chart projecting future price

Acceptable:
- Individual finding severity badges
- "2 CRITICAL, 3 HIGH" finding counts
- Per-metric comparison tables (pledge %, not overall score)

### 8.5 SME IPO Disclaimer

When is_sme_ipo = true, add inline:
"SME IPO: This DRHP is filed on the SME platform. Disclosure obligations differ from main-board listings. Verify directly with SEBI filings."
Placement: DRHPCard + report header + first-run modal for this DRHP.

---

## 9. Anti-Patterns (Strict Prohibition)

### Visual

| Forbidden | Replacement |
|-----------|-------------|
| Gradient backgrounds on data tables | Flat surface background, border separators |
| Tweening/animating financial numbers | Numbers appear instantly, opacity-only (200ms max) |
| Sparklines in RedFlagCards | Tabular text only -- no time-series |
| Composite risk score / verdict badge | Individual finding severities only |
| AI assistant avatar / bot icon | No avatar. Lucide icons only near content. |
| Emoji in interface copy | Plain text. Lucide icons only. |
| Sparkle / star / magic icon | None. Not near analysis content. |
| Confetti on ingestion complete | CheckCircle + "Analysis ready" |
| Dismissable disclaimer | Non-dismissable, sticky, permanent |

### Interaction

| Forbidden | Replacement |
|-----------|-------------|
| Scroll-jacking | Native scroll |
| Parallax | Static layout |
| Chatbot Q&A as primary interface | Structured report with tabs and filters |
| Full-page spinner blocking partial results | Per-section skeletons, stream first result within 3s |
| Skeleton > 5s before first content | Stream first agent result as soon as it completes |

### Copy

| Forbidden | Replacement |
|-----------|-------------|
| "Welcome to your AI IPO assistant!" | "DRHP Red-Flag Analysis" |
| "Our AI thinks..." | "The DRHP states..." / "Analysis suggests..." |
| "Based on my analysis..." (first-person) | Third-person or passive voice |
| "This is a high-risk IPO" | "2 CRITICAL findings in promoter disclosures" |
| "Educational only -- use at your own risk" | Full SEBI-appropriate disclaimer verbatim |

---

## 10. Mobile Responsive

### Breakpoints

| Breakpoint | Width | Key changes |
|------------|-------|-------------|
| base | 0-479px | Single column, sidebar = bottom Drawer, PDF = full-screen Sheet, tabs scroll |
| sm | 480-767px | 2-col browse grid, more whitespace |
| md | 768-1023px | Filter = dropdown, PDF = full-width Dialog, sidebar collapses |
| lg | 1024-1279px | Full layout: 240px sidebar + flex-1 main |
| xl | 1280px+ | max-w-[1440px] centered, report main max-w-[900px] |

### Mobile Component Specifics

PDF Viewer (<768px): Sheet side="bottom", height 85dvh, drag handle 12x4px pill top-center, swipe dismiss.

Severity filter (<768px): "Filter" button with Funnel icon + badge count. Opens Vaul Drawer bottom. Rows 48px height. "Apply" primary + "Reset" ghost. aria-live announces result count.

Tabs (<768px): horizontal scroll, min-width 80px per tab, active = 2px accent bottom border, scroll position preserved.

DisclaimerBanner mobile: 1-line visible always, tap to expand full text, tap to collapse. Never dismissed.

DRHPCard (<480px): full width, risk summary shows highest severity + count only ("2 CRITICAL +").

UploadDropzone mobile: "Tap to select PDF" copy. No drag state. input[type=file] triggered by tap.

### Touch Rules

- All interactive: min 44x44px (WCAG 2.5.5)
- CitationChip: py-2 px-3 + surrounding whitespace = 44px tap zone
- HoverCard on touch: replaced by bottom-sheet mini-preview component
- No hover-only interactions
- Focus rings: min 2px width (WCAG 2.4.11 AA)

---

## 11. Implementation Snippets

### 11.1 SeverityBadge (TSX + Tailwind 4)

```tsx
// components/severity-badge.tsx
import { AlertTriangle, AlertCircle, Info, CheckCircle } from "lucide-react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const badgeVariants = cva(
  "inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[11px] font-semibold uppercase tracking-[0.5px] leading-[14px] select-none shrink-0",
  {
    variants: {
      severity: {
        CRITICAL: "bg-[--severity-critical-badge-bg] text-[--severity-critical-badge-fg]",
        HIGH:     "bg-[--severity-high-badge-bg]     text-[--severity-high-badge-fg]",
        MODERATE: "bg-[--severity-moderate-badge-bg] text-[--severity-moderate-badge-fg]",
        NONE:     "bg-[--severity-none-badge-bg]     text-[--severity-none-badge-fg]",
      },
    },
    defaultVariants: { severity: "NONE" },
  }
)

const ICONS = {
  CRITICAL: AlertTriangle,
  HIGH:     AlertCircle,
  MODERATE: Info,
  NONE:     CheckCircle,
} as const

type Severity = keyof typeof ICONS

export function SeverityBadge({ severity, className }: { severity: Severity; className?: string }) {
  const Icon = ICONS[severity]
  return (
    <span role="img" aria-label={`Severity: ${severity}`} className={cn(badgeVariants({ severity }), className)}>
      <Icon aria-hidden className="size-3 shrink-0" />
      <span>{severity}</span>
    </span>
  )
}
```

### 11.2 RedFlagCard (TSX + Tailwind 4)

```tsx
// components/red-flag-card.tsx
"use client"
import { SeverityBadge } from "./severity-badge"
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion"
import { CitationChip } from "./citation-chip"
import { cn } from "@/lib/utils"
import type { RedFlag } from "@/lib/types"

const CARD_CLASSES: Record<string, string> = {
  CRITICAL: "bg-[--severity-critical-card-bg] border-[--severity-critical-card-border]",
  HIGH:     "bg-[--severity-high-card-bg]     border-[--severity-high-card-border]",
  MODERATE: "bg-[--severity-moderate-card-bg] border-[--severity-moderate-card-border]",
  NONE:     "bg-[--severity-none-card-bg]     border-[--severity-none-card-border]",
}

export function RedFlagCard({ finding, defaultExpanded = false }: { finding: RedFlag; defaultExpanded?: boolean }) {
  const { id, severity, headline, summary, verbatim_quote, analysis, citations, agent_name, confidence } = finding

  return (
    <article
      aria-label={`${severity} severity: ${headline}`}
      className={cn(
        "rounded-md border shadow-[--shadow-sm] transition-shadow duration-[120ms] ease-[--ease-standard] hover:shadow-[--shadow-md]",
        CARD_CLASSES[severity]
      )}
    >
      <Accordion type="single" collapsible defaultValue={defaultExpanded ? id : undefined}>
        <AccordionItem value={id} className="border-0">
          {/* Header: badge + trigger -- badge OUTSIDE trigger */}
          <div className="flex items-start gap-3 px-4 pt-4 pb-2">
            <SeverityBadge severity={severity} className="mt-0.5" />
            <AccordionTrigger className="flex-1 text-left text-[15px] font-medium leading-5 text-[--fg-primary] p-0 hover:no-underline [&>svg]:ml-auto">
              {headline}
            </AccordionTrigger>
          </div>

          {/* Summary -- always visible */}
          <p className="px-4 pb-3 text-[14px] leading-5 text-[--fg-secondary] line-clamp-2">{summary}</p>

          {/* Citations -- always visible */}
          <div className="flex flex-wrap gap-1.5 px-4 pb-4" aria-label="Source citations">
            {citations.slice(0, 3).map((c) => <CitationChip key={c.chunk_id} citation={c} />)}
            {citations.length > 3 && (
              <span className="text-[12px] text-[--fg-muted] self-center">+{citations.length - 3} more</span>
            )}
          </div>

          {/* Expanded content */}
          <AccordionContent className="px-4 pb-0 text-sm">
            {verbatim_quote && (
              <blockquote
                aria-label="Verbatim quote from DRHP"
                className="mb-4 rounded-sm px-3 py-2.5 bg-[--extracted-fact-bg] border-l-[3px] border-l-[--extracted-fact-border] font-mono text-[13px] leading-[18px]"
              >
                <p className="mb-1 font-sans text-[11px] font-semibold uppercase tracking-[0.5px] text-[--fg-muted]">
                  DRHP Source (verbatim)
                </p>
                <p className="text-[--fg-primary]">"{verbatim_quote.text}"</p>
                <p className="mt-1 text-right font-mono text-[12px] text-[--fg-muted]">Page {verbatim_quote.page}</p>
              </blockquote>
            )}

            {analysis && (
              <div className="mb-4">
                <p className="mb-1 text-[11px] font-semibold uppercase tracking-[0.5px] italic text-[--fg-muted]">Analysis</p>
                <p className="italic text-[--fg-secondary] leading-5">{analysis}</p>
              </div>
            )}

            <div className="mb-3">
              <p className="mb-1.5 text-[11px] font-semibold uppercase tracking-[0.5px] text-[--fg-muted]">Sources</p>
              <div className="flex flex-wrap gap-1.5">
                {citations.map((c) => <CitationChip key={c.chunk_id} citation={c} />)}
              </div>
            </div>

            <p className="text-[12px] text-[--fg-subtle] mb-1">
              Identified by {agent_name}
              {confidence && <span className="font-mono ml-2 text-[--fg-muted]"> confidence {confidence.toFixed(2)}</span>}
            </p>

            <div className="border-t border-[--border-default] mt-3 pt-2.5 pb-3">
              <p className="text-[11px] text-[--fg-muted]">
                Source: public SEBI filing. Educational use only. Not investment advice.
              </p>
            </div>
          </AccordionContent>
        </AccordionItem>
      </Accordion>
    </article>
  )
}
```

### 11.3 DisclaimerBanner (TSX)

```tsx
// components/disclaimer-banner.tsx
import { Info } from "lucide-react"

export function DisclaimerBanner() {
  return (
    <aside
      role="note"
      aria-label="Legal disclaimer"
      className="sticky top-0 z-50 w-full flex items-center gap-2 px-4 min-h-[40px] py-2 bg-[--disclaimer-bg] border-b border-[--disclaimer-border] text-[--disclaimer-fg] text-[12px] leading-[16px]"
    >
      <Info aria-hidden className="size-3.5 shrink-0 opacity-80" />
      <p>
        Analysis based on public SEBI filings.{" "}
        <strong>Educational use only. Not investment advice.</strong>{" "}
        Not affiliated with SEBI. Consult a SEBI-registered adviser before investing.
      </p>
    </aside>
  )
}
```

### 11.4 RefusalCard (TSX)

```tsx
// components/refusal-card.tsx
import { StopCircle } from "lucide-react"

const CAN_DO = [
  "What percentage of IPO proceeds go to debt repayment?",
  "What is the promoter pledge ratio?",
  "What litigation proceedings are disclosed in the DRHP?",
] as const

export function RefusalCard({ prohibitedQuery }: { prohibitedQuery: string }) {
  return (
    <div
      role="status"
      aria-live="polite"
      aria-label="Query outside tool scope"
      className="rounded-md border border-[--refusal-border] border-l-[3px] border-l-[--refusal-fg] bg-[--refusal-bg] p-4"
    >
      <div className="flex items-start gap-3 mb-3">
        <StopCircle aria-hidden className="size-5 text-[--refusal-fg] shrink-0 mt-0.5" />
        <div>
          <p className="font-medium text-sm text-[--refusal-fg]">This query is outside this tool's scope</p>
          <p className="text-[13px] text-[--fg-secondary] mt-1 leading-5">
            SEBI DRHP Radar analyzes publicly filed documents to surface structural red flags
            -- not investment merit or price outlook.
          </p>
        </div>
      </div>
      <div className="ml-8">
        <p className="text-[12px] font-semibold uppercase tracking-[0.5px] text-[--fg-muted] mb-1.5">
          What this tool can analyze:
        </p>
        <ul className="space-y-1">
          {CAN_DO.map((item) => (
            <li key={item} className="text-[13px] text-[--fg-secondary] flex items-start gap-1.5">
              <span aria-hidden className="text-[--fg-muted] mt-0.5">-</span>
              {item}
            </li>
          ))}
        </ul>
        <p className="text-[12px] text-[--fg-muted] mt-3">
          For investment decisions, consult a SEBI-registered adviser.{" "}
          <span className="font-mono">SEBI helpline: 1800-266-7575</span>
        </p>
      </div>
    </div>
  )
}
```

### 11.5 Skeleton Shimmer CSS

```css
/* Add to globals.css */
@keyframes skeleton-shimmer {
  0%   { background-position: -200% 0; }
  100% { background-position:  200% 0; }
}

.skeleton-shimmer {
  background: linear-gradient(
    90deg,
    var(--skeleton-base) 25%,
    var(--skeleton-shimmer) 50%,
    var(--skeleton-base) 75%
  );
  background-size: 200% 100%;
  animation: skeleton-shimmer 1.4s ease-in-out infinite;
}

@media (prefers-reduced-motion: reduce) {
  .skeleton-shimmer {
    animation: none;
    background: var(--skeleton-base);
  }
}
```

Usage: `<div className="skeleton-shimmer rounded-md h-4 w-full" />`

---

## 12. Open Questions for Engineering

1. **PDF highlight coordinates:** react-pdf-highlighter-extended requires highlight rects in PDF coordinate space, not screen pixels. Backend must store `highlight_rects: [{x, y, width, height, pageIndex}]` from Docling layout output per chunk. Without spatial coordinates, citation drill-down lands on the correct page but shows no highlight -- this degrades trust significantly. Confirm backend schema includes this field before frontend implementation begins.

2. **SSE event schema for streaming report:** Frontend needs the exact event shape:
   ```typescript
   type StreamEvent =
     | { type: "agent_start";    agent: string; section: string }
     | { type: "agent_finding";  agent: string; finding: RedFlag }
     | { type: "agent_complete"; agent: string; finding_count: number }
     | { type: "report_complete" }
     | { type: "agent_error";    agent: string; error: string }
   ```
   Confirm this matches LangGraph SSE output format.

3. **Mobile citation UX (HoverCard -> tap):** Radix HoverCard is hover-only. Decision needed:
   - Option A: tap chip = HoverCard bottom-sheet mini-preview (separate mobile component)
   - Option B: tap chip = directly open PDF viewer Sheet
   - Option C: tap chip = inline text expansion below chip
   Recommendation: Option A. It preserves the preview step that desktop users get, without forcing immediate full-screen PDF.

4. **Ingestion polling vs SSE:** 15-20 min background job (Modal -> webhook) is too long for SSE. Recommendation: client polls /api/job/[id]/status every 10s with exponential backoff + email notification opt-in. The `parsing-in-progress` state must survive page reload: store job_id in localStorage AND URL params (/upload/[job_id]).

5. **DRHP metadata table:** DRHPCard browse needs per-document metadata beyond what per-chunk schema provides. A `drhp_metadata` Supabase table is required:
   `(drhp_id, company_name, sector, filing_date, page_count, is_sme, sebi_filing_url, is_pre_indexed, created_at)`
   Has this table been created? If not, the browse list cannot render.

6. **Dark mode default:** System preference (`prefers-color-scheme`) vs light-only vs manual toggle. Recommendation: system preference default + manual toggle in nav. Test all severity tokens in both modes before ship -- the dark mode moderate badge uses dark text; all others use white text.

7. **Geist Mono availability:** Confirm `import { Geist_Mono } from "next/font/google"` resolves in Next.js 15. Fallback: `import { IBM_Plex_Mono } from "next/font/google"`. Token system already lists both.

8. **DisclaimerModal acknowledgment storage:** Uses `localStorage.setItem("drhp_disclaimer_v1", "true")`. Clearing localStorage re-shows modal -- correct behavior (legal safety). If auth is in scope, consider server-side acknowledgment (user table column) for logged-in users.

9. **SME DRHP detection:** `is_sme_ipo` flag must be set at ingest time (PyMuPDF or Docling metadata pass). Confirm ingestion pipeline sets this flag before frontend consumes it. If missing, all DRHPs default to main-board treatment.

---

*Brief version: 1.0 -- 2026-05-14*
*Consuming agent: frontend-engineer-agent*
*Next: dispatch frontend-engineer-agent with this brief + SOTA_LANDSCAPE.md as current_2026_landscape context block*
