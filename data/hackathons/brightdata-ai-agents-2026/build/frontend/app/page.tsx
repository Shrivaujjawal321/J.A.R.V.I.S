/**
 * Hero page — AltBrief landing
 * Server Component (no interactivity at this level)
 * Client components: TickerInput, ComparisonTable (imported via boundary)
 */

import type { Metadata } from "next";
import Link from "next/link";
import { TickerInput } from "@/components/TickerInput";
import { ComparisonTable } from "@/components/ComparisonTable";

export const metadata: Metadata = {
  title: "AltBrief — AI Investment Brief from Alt-Data",
};

const DEMO_TICKERS = [
  {
    ticker: "NVDA",
    label: "NVDA",
    tagline: "AI supercycle + $47M insider sells",
    colorClass: "bullish",
  },
  {
    ticker: "XOM",
    label: "XOM",
    tagline: "Satellite flaring vs. guided throughput",
    colorClass: "neutral",
  },
  {
    ticker: "WMT",
    label: "WMT",
    tagline: "Glassdoor decline during hiring surge",
    colorClass: "bearish",
  },
] as const;

export default function HomePage() {
  return (
    <div className="min-h-dvh flex flex-col">
      {/* Nav */}
      <nav
        className="sticky top-0 z-40 border-b border-[var(--color-border)] bg-[var(--color-bg-base)]/90 backdrop-blur-sm"
        aria-label="Main navigation"
      >
        <div className="mx-auto max-w-6xl px-4 sm:px-6 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="font-mono text-lg font-bold text-[var(--color-text-primary)] tracking-tight">
              alt<span className="text-[var(--color-accent)]">brief</span>
            </span>
            <span className="hidden sm:inline text-[10px] font-mono uppercase tracking-widest text-[var(--color-text-muted)] border border-[var(--color-border)] px-2 py-0.5 rounded-full">
              Beta — BrightData Hackathon 2026
            </span>
          </div>
          <div className="flex items-center gap-4">
            <a
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs font-mono text-[var(--color-text-muted)] hover:text-[var(--color-text-primary)] transition-colors"
              aria-label="View source on GitHub"
            >
              GitHub
            </a>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <main className="flex-1" id="main-content">
        {/* Hero section */}
        <section
          className="mx-auto max-w-6xl px-4 sm:px-6 pt-16 pb-12 text-center"
          aria-labelledby="hero-headline"
        >
          {/* Badge */}
          <div
            className="inline-flex items-center gap-2 rounded-full border border-[var(--color-border)] bg-[var(--color-surface-1)] px-4 py-1.5 text-xs font-mono text-[var(--color-text-secondary)] mb-8"
            role="note"
          >
            <span className="w-2 h-2 rounded-full bg-[var(--color-bullish)] live-dot" aria-hidden="true" />
            8 alt-data sources · BrightData powered · Free
          </div>

          {/* Headline */}
          <h1
            id="hero-headline"
            className="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight text-[var(--color-text-primary)] mb-4 leading-[1.15]"
          >
            Bloomberg charges{" "}
            <span className="font-mono text-[var(--color-bearish)] line-through decoration-[var(--color-bearish)]">
              $24K/year
            </span>
            <br />
            and{" "}
            <span className="text-[var(--color-text-muted)]">
              won&apos;t show its sources.
            </span>
          </h1>

          <p className="text-lg text-[var(--color-text-secondary)] max-w-2xl mx-auto mb-10 leading-relaxed">
            Enter any ticker. In 30 seconds, AltBrief fans out across 8 alternative data sources
            — SEC filings, LinkedIn hiring trends, Glassdoor employee sentiment, satellite imagery,
            Reddit momentum — and synthesizes a structured investment brief with{" "}
            <strong className="text-[var(--color-text-primary)]">peer-reviewed citations</strong>{" "}
            and{" "}
            <strong className="text-[var(--color-accent)]">
              cross-source contradiction detection.
            </strong>
          </p>

          {/* Ticker input */}
          <div className="max-w-xl mx-auto mb-6">
            <TickerInput
              placeholder="NVDA, XOM, WMT..."
              autoFocus
              aria-label="Enter stock ticker to generate investment brief"
            />
          </div>

          {/* Demo chips */}
          <div className="flex items-center justify-center gap-2 flex-wrap" role="group" aria-label="Demo tickers">
            <span className="text-xs font-mono text-[var(--color-text-muted)] uppercase tracking-widest mr-1">
              Try:
            </span>
            {DEMO_TICKERS.map((t) => (
              <Link
                key={t.ticker}
                href={`/brief/${t.ticker}?demo=true`}
                className={[
                  "inline-flex items-center gap-2 rounded-full border px-3 py-1.5 text-xs font-mono transition-all hover:scale-105 focus-visible:ring-2 focus-visible:ring-[var(--color-accent)]",
                  t.colorClass === "bullish"
                    ? "border-[var(--color-bullish-dim)] bg-[var(--color-bullish-bg)] text-[var(--color-bullish)]"
                    : t.colorClass === "bearish"
                      ? "border-[var(--color-bearish-dim)] bg-[var(--color-bearish-bg)] text-[var(--color-bearish)]"
                      : "border-[var(--color-neutral-dim)] bg-[var(--color-neutral-bg)] text-[var(--color-neutral)]",
                ].join(" ")}
                aria-label={`View demo for ${t.ticker}: ${t.tagline}`}
              >
                <span className="font-bold">{t.label}</span>
                <span className="text-[10px] opacity-80 hidden sm:inline">
                  {t.tagline}
                </span>
              </Link>
            ))}
          </div>
        </section>

        {/* How it works */}
        <section
          className="mx-auto max-w-6xl px-4 sm:px-6 py-12 border-t border-[var(--color-border-subtle)]"
          aria-labelledby="how-it-works"
        >
          <h2
            id="how-it-works"
            className="text-xs font-mono uppercase tracking-widest text-[var(--color-text-muted)] text-center mb-8"
          >
            How it works
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              {
                step: "01",
                title: "Enter Ticker",
                desc: "Type any US stock ticker. NVDA, XOM, WMT — or any S&P 500 name.",
                color: "var(--color-accent)",
              },
              {
                step: "02",
                title: "8 Sources, Parallel",
                desc: "BrightData fans out across SEC, LinkedIn, Glassdoor, Reddit, News, satellite. Simultaneously.",
                color: "var(--color-neutral)",
              },
              {
                step: "03",
                title: "Claude Synthesizes",
                desc: "Claude Sonnet synthesizes into a structured sell-side note with confidence scores.",
                color: "var(--color-bullish)",
              },
              {
                step: "04",
                title: "Contradiction Alert",
                desc: "AltBrief flags when insider trades contradict Reddit hype. No tool does this.",
                color: "var(--color-bearish)",
              },
            ].map((step) => (
              <div
                key={step.step}
                className="rounded-lg border border-[var(--color-border)] bg-[var(--color-surface-1)] p-5 space-y-3"
              >
                <div
                  className="text-3xl font-mono font-bold"
                  style={{ color: step.color }}
                  aria-hidden="true"
                >
                  {step.step}
                </div>
                <h3 className="font-semibold text-[var(--color-text-primary)]">
                  {step.title}
                </h3>
                <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed">
                  {step.desc}
                </p>
              </div>
            ))}
          </div>
        </section>

        {/* Comparison table */}
        <section
          className="mx-auto max-w-6xl px-4 sm:px-6 py-12 border-t border-[var(--color-border-subtle)]"
          aria-labelledby="comparison"
        >
          <ComparisonTable />
        </section>

        {/* Peer-reviewed signals section */}
        <section
          className="mx-auto max-w-6xl px-4 sm:px-6 py-12 border-t border-[var(--color-border-subtle)]"
          aria-labelledby="peer-reviewed"
        >
          <h2
            id="peer-reviewed"
            className="text-xs font-mono uppercase tracking-widest text-[var(--color-text-muted)] mb-8 text-center"
          >
            Powered by peer-reviewed alpha signals — not vibes
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {[
              {
                alpha: "82 bps/month",
                signal: "Insider Form 4 Buys",
                citation: "Cohen, Malloy & Pomorski, Journal of Finance, 2012",
                desc: "Opportunistic insider purchases (non-routine) predict 82bps/month returns. AltBrief classifies routine vs. opportunistic trades automatically.",
              },
              {
                alpha: "84 bps/month",
                signal: "Glassdoor Rating Change",
                citation: "Green, Huang, Wen & Zhou, Journal of Financial Economics, 2019",
                desc: "Firms with improving Glassdoor ratings outperform. Senior Management sub-rating predicts next-quarter earnings surprises.",
              },
              {
                alpha: "4-5% returns",
                signal: "Satellite Operational Data",
                citation: "UC Berkeley Haas School of Business — Orbital Insight",
                desc: "Parking lot fill rates and thermal anomaly counts predict quarterly earnings. AltBrief uses NASA FIRMS as a free proxy for refinery activity.",
              },
            ].map((signal) => (
              <div
                key={signal.signal}
                className="rounded-lg border border-[var(--color-gold-border)] bg-[var(--color-gold-bg)] p-5 space-y-3"
                role="article"
              >
                <div className="flex items-start justify-between gap-2">
                  <span className="text-xs font-mono uppercase tracking-widest text-[var(--color-gold)]">
                    ★ Peer-Reviewed
                  </span>
                  <span className="text-2xl font-mono font-bold text-[var(--color-text-primary)]">
                    {signal.alpha}
                  </span>
                </div>
                <h3 className="font-semibold text-[var(--color-text-primary)]">
                  {signal.signal}
                </h3>
                <p className="text-xs text-[var(--color-text-secondary)] leading-relaxed">
                  {signal.desc}
                </p>
                <p className="text-[10px] font-mono text-[var(--color-text-muted)] italic">
                  {signal.citation}
                </p>
              </div>
            ))}
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer
        className="border-t border-[var(--color-border-subtle)] py-6 mt-auto"
        aria-label="Site footer"
      >
        <div className="mx-auto max-w-6xl px-4 sm:px-6 flex items-center justify-between flex-wrap gap-3 text-xs font-mono text-[var(--color-text-muted)]">
          <span>
            altbrief — BrightData × lablab.ai Hackathon 2026 · MIT License
          </span>
          <span>
            Not financial advice. Educational use only.
          </span>
        </div>
      </footer>
    </div>
  );
}
