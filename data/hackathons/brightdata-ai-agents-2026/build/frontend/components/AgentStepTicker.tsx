"use client";

/**
 * AgentStepTicker — Live SSE event progress display
 * Research ref: research/07_fintech_ui_references_2026.md (Hebbia + Perplexity agent step pattern)
 * Shows: numbered step list, pulsing dot → checkmark (200ms ease-out), live data preview
 */

import { motion, AnimatePresence } from "framer-motion";
import { CheckCircle2, Circle, Loader2, AlertCircle } from "lucide-react";
import { cn, getSourceIcon, formatLatency } from "@/lib/utils";
import type { SSEEvent } from "@/lib/sse";

interface AgentStepTickerProps {
  steps: SSEEvent[];
  isConnected: boolean;
  isStreaming: boolean;
  className?: string;
}

const SOURCE_LABELS: Record<string, string> = {
  sec: "SEC EDGAR (Form 4 + 10-K)",
  yahoo: "Yahoo Finance",
  news: "News (Reuters + SERP)",
  reddit: "Reddit (WSB/investing)",
  linkedin: "LinkedIn Hiring Trends",
  glassdoor: "Glassdoor Reviews",
  gdelt: "GDELT News Tone",
  satellite: "Satellite / NASA FIRMS",
};

const SOURCE_ICONS: Record<string, string> = {
  sec: "📋",
  yahoo: "📊",
  news: "📰",
  reddit: "💬",
  linkedin: "💼",
  glassdoor: "⭐",
  gdelt: "🌐",
  satellite: "🛰️",
};

interface StepState {
  source: string;
  label: string;
  icon: string;
  status: "pending" | "running" | "done" | "error";
  latency_ms?: number;
  summary?: string;
  fromCache?: boolean;
}

function buildStepStates(steps: SSEEvent[]): StepState[] {
  const states: Record<string, StepState> = {};

  for (const event of steps) {
    if (event.type === "source_started") {
      const key = event.data.source;
      if (!states[key]) {
        states[key] = {
          source: key,
          label: SOURCE_LABELS[key] ?? key,
          icon: SOURCE_ICONS[key] ?? "📡",
          status: "running",
        };
      }
    } else if (event.type === "source_completed") {
      const key = event.data.source;
      if (states[key]) {
        states[key] = {
          ...states[key]!,
          status: event.data.status === "ok" ? "done" : "error",
          latency_ms: event.data.latency_ms,
          summary: event.data.summary,
          fromCache: event.data.from_cache,
        };
      }
    }
  }

  return Object.values(states);
}

function hasSynthesisChunks(steps: SSEEvent[]): boolean {
  return steps.some((s) => s.type === "synthesis_chunk");
}

function isDone(steps: SSEEvent[]): boolean {
  return steps.some((s) => s.type === "done");
}

export function AgentStepTicker({
  steps,
  isConnected,
  isStreaming,
  className,
}: AgentStepTickerProps) {
  const stepStates = buildStepStates(steps);
  const synthesizing = hasSynthesisChunks(steps);
  const done = isDone(steps);
  const hasSteps = stepStates.length > 0 || isStreaming;

  if (!hasSteps) return null;

  return (
    <aside
      className={cn(
        "rounded-lg border border-[var(--color-border)] bg-[var(--color-surface-1)] overflow-hidden",
        className,
      )}
      aria-label="Agent progress"
      aria-live="polite"
      aria-atomic="false"
    >
      {/* Header */}
      <div className="flex items-center gap-2 px-4 py-3 border-b border-[var(--color-border)] bg-[var(--color-surface-2)]">
        <div className="flex gap-1" aria-hidden="true">
          <span className="w-2.5 h-2.5 rounded-full bg-[var(--color-bearish-dim)]" />
          <span className="w-2.5 h-2.5 rounded-full bg-[var(--color-neutral-dim)]" />
          <span className="w-2.5 h-2.5 rounded-full bg-[var(--color-bullish-dim)]" />
        </div>
        <div className="flex items-center gap-2 ml-1">
          {isConnected && !done && (
            <motion.span
              className="w-2 h-2 rounded-full bg-[var(--color-bullish)] live-dot"
              aria-hidden="true"
            />
          )}
          <span className="text-xs font-mono text-[var(--color-text-muted)] uppercase tracking-widest">
            {done
              ? "altbrief — analysis complete"
              : isConnected
                ? "altbrief — data collection live"
                : "altbrief — connecting..."}
          </span>
        </div>
      </div>

      {/* Steps log */}
      <div
        className="p-4 space-y-2 font-mono text-xs max-h-64 overflow-y-auto terminal-mask"
        aria-label="Data collection steps"
      >
        <AnimatePresence initial={false}>
          {stepStates.map((step, i) => (
            <motion.div
              key={step.source}
              initial={{ opacity: 0, y: 4 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2, ease: "easeOut" }}
              className="flex items-start gap-2.5 group"
            >
              {/* Status icon */}
              <div className="shrink-0 mt-0.5" aria-hidden="true">
                {step.status === "running" && (
                  <Loader2
                    size={12}
                    className="text-[var(--color-accent)] animate-spin"
                  />
                )}
                {step.status === "done" && (
                  <CheckCircle2
                    size={12}
                    className="text-[var(--color-bullish)]"
                  />
                )}
                {step.status === "error" && (
                  <AlertCircle
                    size={12}
                    className="text-[var(--color-bearish)]"
                  />
                )}
                {step.status === "pending" && (
                  <Circle size={12} className="text-[var(--color-text-muted)]" />
                )}
              </div>

              {/* Content */}
              <div className="flex-1 min-w-0 space-y-0.5">
                <div className="flex items-center gap-2 flex-wrap">
                  <span aria-hidden="true">{step.icon}</span>
                  <span
                    className={cn(
                      step.status === "running"
                        ? "text-[var(--color-text-primary)]"
                        : step.status === "done"
                          ? "text-[var(--color-mono-live)]"
                          : step.status === "error"
                            ? "text-[var(--color-bearish)]"
                            : "text-[var(--color-text-muted)]",
                    )}
                  >
                    {step.label}
                  </span>
                  {step.status === "done" && step.latency_ms !== undefined && (
                    <span className="text-[var(--color-text-muted)]">
                      {step.fromCache
                        ? "[cache]"
                        : `[${formatLatency(step.latency_ms / 1000)}]`}
                    </span>
                  )}
                  {step.status === "error" && (
                    <span className="text-[var(--color-bearish)]">[failed — graceful fallback]</span>
                  )}
                </div>

                {/* Data preview */}
                {step.summary && step.status === "done" && (
                  <p className="text-[var(--color-text-muted)] text-[10px] truncate leading-relaxed pl-5">
                    &rarr; {step.summary}
                  </p>
                )}
              </div>

              <span className="sr-only">
                {step.label}: {step.status}
                {step.latency_ms !== undefined
                  ? `, completed in ${step.latency_ms}ms`
                  : ""}
              </span>
            </motion.div>
          ))}
        </AnimatePresence>

        {/* Synthesis phase */}
        <AnimatePresence>
          {synthesizing && !done && (
            <motion.div
              initial={{ opacity: 0, y: 4 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="flex items-center gap-2.5 pt-1 border-t border-[var(--color-border-subtle)] mt-2"
              aria-live="polite"
            >
              <Loader2
                size={12}
                className="text-[var(--color-accent)] animate-spin shrink-0"
                aria-hidden="true"
              />
              <span className="text-[var(--color-accent)] animate-pulse">
                Claude Sonnet synthesizing investment brief
                <span className="cursor-blink"> ▌</span>
              </span>
            </motion.div>
          )}
          {done && (
            <motion.div
              initial={{ opacity: 0, y: 4 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex items-center gap-2.5 pt-1 border-t border-[var(--color-border-subtle)] mt-2"
            >
              <CheckCircle2
                size={12}
                className="text-[var(--color-bullish)] shrink-0"
                aria-hidden="true"
              />
              <span className="text-[var(--color-bullish)]">
                Brief complete — rendered below
              </span>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </aside>
  );
}
