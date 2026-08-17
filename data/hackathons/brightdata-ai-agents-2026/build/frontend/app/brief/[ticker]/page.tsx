"use client";

/**
 * Brief streaming page — /brief/[ticker]
 * Client Component: needs useSSE, useQueryClient, router hooks
 *
 * SSE flow per research/16_sse_streaming_patterns.md §2b:
 *   1. useSSE → fetchEventSource → direct Fly.io connection (NO Next.js proxy)
 *   2. On "done" event → queryClient.setQueryData(["brief", ticker], parsed)
 *   3. BriefCard renders from parsed brief
 *
 * ?demo=true → immediate display of cached brief (no backend call, judge-friendly)
 */

import { useState, useCallback, use } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import Link from "next/link";
import { useQueryClient } from "@tanstack/react-query";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowLeft, AlertCircle } from "lucide-react";
import { useSSE, type SSEEvent } from "@/lib/sse";
import { DEMO_BRIEFS } from "@/lib/api";
import type { InvestmentBrief } from "@/lib/types";
import { BriefCard, BriefCardSkeleton } from "@/components/BriefCard";
import { AgentStepTicker } from "@/components/AgentStepTicker";
import { SourceOverlay } from "@/components/SourceOverlay";
import { TickerInput } from "@/components/TickerInput";

interface BriefPageProps {
  params: Promise<{ ticker: string }>;
}

const BRIEF_QUERY_KEY = (ticker: string) => ["brief", ticker] as const;

export default function BriefPage({ params }: BriefPageProps) {
  const { ticker: rawTicker } = use(params);
  const ticker = rawTicker.toUpperCase();
  const searchParams = useSearchParams();
  const router = useRouter();
  const queryClient = useQueryClient();
  const isDemo = searchParams.get("demo") === "true";

  // Demo mode: immediate data, no SSE
  const demoBrief = isDemo ? DEMO_BRIEFS[ticker as keyof typeof DEMO_BRIEFS] : undefined;

  const [steps, setSteps] = useState<SSEEvent[]>([]);
  const [synthesisText, setSynthesisText] = useState("");
  const [brief, setBrief] = useState<InvestmentBrief | null>(demoBrief ?? null);
  const [sseError, setSseError] = useState<string | null>(null);

  const handleEvent = useCallback((event: SSEEvent) => {
    setSteps((prev) => [...prev, event]);

    if (event.type === "synthesis_chunk") {
      setSynthesisText((prev) => prev + event.data.text);
    }
  }, []);

  // Called when "done" event arrives with full brief JSON
  const handleDone = useCallback(
    (rawJson: string) => {
      try {
        const parsed: InvestmentBrief = JSON.parse(rawJson);
        setBrief(parsed);

        // Seed TanStack Query cache — any sibling component can now call
        // useQuery(["brief", ticker]) and get instant data without fetching
        queryClient.setQueryData(BRIEF_QUERY_KEY(ticker), parsed);
      } catch {
        setSseError("Failed to parse brief JSON from server.");
      }
    },
    [ticker, queryClient],
  );

  const handleError = useCallback((err: Error) => {
    setSseError(`Connection error: ${err.message}`);
  }, []);

  // Only connect SSE if not in demo mode and brief not yet loaded
  const { isStreaming, isConnected, abort } = useSSE({
    ticker: isDemo || brief !== null ? null : ticker,
    onEvent: handleEvent,
    onDone: handleDone,
    onError: handleError,
  });

  const hasActivity = steps.length > 0 || isStreaming || isConnected;

  return (
    <div className="min-h-dvh flex flex-col" aria-label={`Investment brief for ${ticker}`}>
      {/* Nav */}
      <nav
        className="sticky top-0 z-40 border-b border-[var(--color-border)] bg-[var(--color-bg-base)]/90 backdrop-blur-sm"
        aria-label="Brief page navigation"
      >
        <div className="mx-auto max-w-6xl px-4 sm:px-6 py-3 flex items-center justify-between gap-4">
          <Link
            href="/"
            className="inline-flex items-center gap-2 text-xs font-mono text-[var(--color-text-muted)] hover:text-[var(--color-text-primary)] transition-colors focus-visible:ring-2 focus-visible:ring-[var(--color-accent)] rounded"
            aria-label="Back to home"
          >
            <ArrowLeft size={12} aria-hidden="true" />
            altbrief
          </Link>

          {/* Compact ticker search */}
          <div className="flex-1 max-w-xs">
            <TickerInput
              placeholder="Search ticker..."
              onSubmit={(t) => {
                router.push(`/brief/${t}`);
              }}
            />
          </div>

          {isDemo && (
            <span className="text-[10px] font-mono uppercase tracking-widest text-[var(--color-neutral)] border border-[var(--color-neutral-dim)] px-2 py-0.5 rounded-full">
              Demo Mode
            </span>
          )}
        </div>
      </nav>

      {/* Page header */}
      <header className="border-b border-[var(--color-border-subtle)] bg-[var(--color-surface-1)]">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 py-4">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-mono font-bold text-[var(--color-text-primary)] tracking-widest">
              {ticker}
            </h1>
            {isStreaming && (
              <div
                className="flex items-center gap-2 text-xs font-mono text-[var(--color-bullish)]"
                aria-live="polite"
                aria-label="Streaming investment brief"
              >
                <span className="w-2 h-2 rounded-full bg-[var(--color-bullish)] live-dot" aria-hidden="true" />
                Collecting alt-data...
              </div>
            )}
            {brief && !isStreaming && (
              <div
                className="flex items-center gap-2 text-xs font-mono text-[var(--color-text-muted)]"
                aria-live="polite"
              >
                <span className="w-2 h-2 rounded-full bg-[var(--color-text-muted)]" aria-hidden="true" />
                {isDemo ? "Demo brief" : "Analysis complete"}
              </div>
            )}
          </div>
        </div>
      </header>

      <main id="main-content" className="flex-1 mx-auto max-w-6xl px-4 sm:px-6 py-6 w-full">
        {/* Error state */}
        <AnimatePresence>
          {sseError && (
            <motion.div
              initial={{ opacity: 0, y: -8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="mb-6 flex items-start gap-3 rounded-lg border border-[var(--color-bearish-dim)] bg-[var(--color-bearish-bg)] p-4"
              role="alert"
              aria-live="assertive"
            >
              <AlertCircle
                size={16}
                className="text-[var(--color-bearish)] shrink-0 mt-0.5"
                aria-hidden="true"
              />
              <div className="space-y-1">
                <p className="text-sm font-semibold text-[var(--color-bearish)]">
                  Connection Error
                </p>
                <p className="text-xs text-[var(--color-text-secondary)]">{sseError}</p>
                <button
                  onClick={() => {
                    setSseError(null);
                    router.refresh();
                  }}
                  className="text-xs font-mono text-[var(--color-accent)] hover:underline mt-1"
                >
                  Try again
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Two-column layout when streaming: left=steps, right=overlay */}
        {hasActivity && !brief && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
            <AgentStepTicker
              steps={steps}
              isConnected={isConnected}
              isStreaming={isStreaming}
              aria-label="Agent data collection progress"
            />
            <SourceOverlay
              steps={steps}
              isStreaming={isStreaming}
              aria-label="BrightData live tool call log"
            />
          </div>
        )}

        {/* Synthesis text preview (streaming, before brief is ready) */}
        {synthesisText && !brief && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mb-6 rounded-lg border border-[var(--color-border)] bg-[var(--color-surface-1)] p-4"
            aria-live="polite"
            aria-label="Claude Sonnet synthesis in progress"
          >
            <p className="text-[10px] font-mono uppercase tracking-widest text-[var(--color-accent)] mb-2">
              Claude Sonnet synthesizing...
            </p>
            <p className="text-sm text-[var(--color-text-secondary)] font-mono whitespace-pre-wrap leading-relaxed">
              {synthesisText}
              <span className="cursor-blink text-[var(--color-accent)]"> ▌</span>
            </p>
          </motion.div>
        )}

        {/* Loading skeleton — while SSE is live but brief not yet done */}
        {isStreaming && !brief && !synthesisText && <BriefCardSkeleton />}

        {/* Full brief */}
        <AnimatePresence>
          {brief && (
            <div>
              {/* Show overlays collapsed/mini when brief is ready */}
              {hasActivity && (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-3 mb-6">
                  <AgentStepTicker
                    steps={steps}
                    isConnected={false}
                    isStreaming={false}
                    className="opacity-70"
                  />
                  <SourceOverlay
                    steps={steps}
                    isStreaming={false}
                    className="opacity-70"
                  />
                </div>
              )}
              <BriefCard brief={brief} />
            </div>
          )}
        </AnimatePresence>

        {/* Initial loading — before any SSE data */}
        {!hasActivity && !brief && !sseError && (
          <div aria-busy="true" aria-label="Connecting to AltBrief backend">
            <BriefCardSkeleton />
          </div>
        )}
      </main>

      {/* Footer */}
      <footer
        className="border-t border-[var(--color-border-subtle)] py-4 mt-auto"
        aria-label="Brief page footer"
      >
        <div className="mx-auto max-w-6xl px-4 sm:px-6 flex items-center justify-between flex-wrap gap-2 text-[10px] font-mono text-[var(--color-text-muted)]">
          <span>altbrief — BrightData × lablab.ai 2026</span>
          <span>Not financial advice. For educational use only.</span>
        </div>
      </footer>
    </div>
  );
}
