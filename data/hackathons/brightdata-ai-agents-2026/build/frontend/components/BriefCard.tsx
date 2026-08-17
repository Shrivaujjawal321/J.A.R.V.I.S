"use client";

/**
 * BriefCard — Sell-side investment note layout
 * Research ref: research/07_fintech_ui_references_2026.md (Morgan Stanley / Goldman note structure)
 * Layout:
 *   1. Cover header (ticker, rating, price target, thesis hook)
 *   2. Investment thesis (bull/bear bullets)
 *   3. Alt-data signals dashboard
 *   4. Cross-source contradictions (NOVELTY ANCHOR)
 *   5. Risk factors
 *   6. Brief narrative
 *   7. Metadata footer
 */

import { motion } from "framer-motion";
import { TrendingUp, TrendingDown, Minus, AlertTriangle, Shield, Clock } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import { ConfidenceMeter } from "@/components/ConfidenceMeter";
import { SignalCard } from "@/components/SignalCard";
import { ContradictionSection } from "@/components/ContradictionCard";
import {
  cn,
  directionLabel,
  directionColorClass,
  directionArrow,
  formatUSD,
  formatPercent,
  formatRelativeTime,
  formatLatency,
  formatCost,
  qualityLabel,
  qualityColorClass,
} from "@/lib/utils";
import type { InvestmentBrief } from "@/lib/types";

interface BriefCardProps {
  brief: InvestmentBrief;
  className?: string;
}

function DirectionIcon({
  direction,
}: {
  direction: InvestmentBrief["overall_direction"];
}) {
  switch (direction) {
    case "bullish":
      return (
        <TrendingUp size={18} className="text-[var(--color-bullish)]" aria-hidden="true" />
      );
    case "bearish":
      return (
        <TrendingDown size={18} className="text-[var(--color-bearish)]" aria-hidden="true" />
      );
    default:
      return (
        <Minus size={18} className="text-[var(--color-neutral)]" aria-hidden="true" />
      );
  }
}

function BullBearList({
  items,
  type,
}: {
  items: string[];
  type: "bull" | "bear";
}) {
  const color =
    type === "bull"
      ? "var(--color-bullish)"
      : "var(--color-bearish)";
  const dot = type === "bull" ? "▲" : "▼";

  return (
    <ul className="space-y-2.5" role="list">
      {items.map((item, i) => (
        <motion.li
          key={i}
          initial={{ opacity: 0, x: -8 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.25, delay: i * 0.06 }}
          className="flex items-start gap-2.5 text-sm leading-relaxed"
        >
          <span
            className="shrink-0 mt-0.5 text-xs font-mono font-bold"
            style={{ color }}
            aria-hidden="true"
          >
            {dot}
          </span>
          <span className="text-[var(--color-text-secondary)]">{item}</span>
        </motion.li>
      ))}
    </ul>
  );
}

export function BriefCard({ brief, className }: BriefCardProps) {
  const hasTarget = brief.price_target_range !== null;
  const upside =
    hasTarget && brief.price_target_range
      ? ((brief.price_target_range.base - (brief.price_target_range.low + brief.price_target_range.high) / 2) /
          ((brief.price_target_range.low + brief.price_target_range.high) / 2)) *
        100
      : null;

  // Sort signals: gold first, then by confidence descending
  const sortedSignals = [...brief.signals].sort((a, b) => {
    if (a.alpha_tier === "gold" && b.alpha_tier !== "gold") return -1;
    if (a.alpha_tier !== "gold" && b.alpha_tier === "gold") return 1;
    return b.confidence - a.confidence;
  });

  return (
    <motion.article
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: [0.19, 1, 0.22, 1] }}
      className={cn("space-y-6", className)}
      aria-label={`Investment brief for ${brief.ticker}`}
    >
      {/* ── 1. COVER HEADER ── */}
      <Card className="overflow-hidden">
        <div
          className={cn(
            "h-1 w-full",
            brief.overall_direction === "bullish"
              ? "bg-[var(--color-bullish)]"
              : brief.overall_direction === "bearish"
                ? "bg-[var(--color-bearish)]"
                : "bg-[var(--color-neutral)]",
          )}
          aria-hidden="true"
        />
        <CardHeader className="pb-4">
          <div className="flex items-start justify-between gap-4 flex-wrap">
            {/* Company info */}
            <div className="space-y-1.5">
              <div className="flex items-center gap-3">
                <h1 className="text-3xl font-mono font-bold text-[var(--color-text-primary)] tracking-tight">
                  {brief.ticker}
                </h1>
                <Badge
                  variant={
                    brief.overall_direction === "bullish"
                      ? "bullish"
                      : brief.overall_direction === "bearish"
                        ? "bearish"
                        : "neutral"
                  }
                  className="text-sm px-3 py-1 gap-1.5"
                >
                  <DirectionIcon direction={brief.overall_direction} />
                  {directionLabel(brief.overall_direction)}
                </Badge>
              </div>
              <div>
                <p className="text-lg font-semibold text-[var(--color-text-primary)]">
                  {brief.company_name}
                </p>
                <p className="text-sm text-[var(--color-text-secondary)] font-mono">
                  {brief.sector}
                </p>
              </div>
            </div>

            {/* Confidence meter */}
            <ConfidenceMeter
              confidence={brief.overall_confidence}
              qualityFlag={brief.data_quality_flag}
              size="md"
              aria-label={`Overall confidence ${Math.round(brief.overall_confidence * 100)}%`}
            />
          </div>

          {/* Price target row */}
          {hasTarget && brief.price_target_range && (
            <div className="mt-4 pt-4 border-t border-[var(--color-border-subtle)] grid grid-cols-3 gap-4">
              <div className="text-center">
                <p className="text-[10px] font-mono uppercase tracking-widest text-[var(--color-text-muted)]">
                  Bear Case
                </p>
                <p className="text-xl font-mono font-bold text-[var(--color-bearish)]">
                  {formatUSD(brief.price_target_range.low)}
                </p>
              </div>
              <div className="text-center">
                <p className="text-[10px] font-mono uppercase tracking-widest text-[var(--color-text-muted)]">
                  Base Case
                </p>
                <p className="text-2xl font-mono font-bold text-[var(--color-text-primary)]">
                  {formatUSD(brief.price_target_range.base)}
                </p>
              </div>
              <div className="text-center">
                <p className="text-[10px] font-mono uppercase tracking-widest text-[var(--color-text-muted)]">
                  Bull Case
                </p>
                <p className="text-xl font-mono font-bold text-[var(--color-bullish)]">
                  {formatUSD(brief.price_target_range.high)}
                </p>
              </div>
            </div>
          )}

          {/* Sources + timestamp */}
          <div className="mt-3 flex items-center justify-between text-[10px] font-mono text-[var(--color-text-muted)] flex-wrap gap-2">
            <span>
              Sources: {brief.sources_used.join(" · ")}
              {brief.sources_unavailable.length > 0 && (
                <span className="text-[var(--color-bearish)]">
                  {" "}
                  (unavailable: {brief.sources_unavailable.join(", ")})
                </span>
              )}
            </span>
            <span className="flex items-center gap-1">
              <Clock size={10} aria-hidden="true" />
              {formatRelativeTime(brief.generated_at)} ·{" "}
              {formatLatency(brief.latency_seconds)} · cost:{" "}
              {formatCost(brief.cost_usd)}
            </span>
          </div>
        </CardHeader>
      </Card>

      {/* ── 2. INVESTMENT THESIS ── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Bull thesis */}
        <Card>
          <CardHeader className="pb-3">
            <h2 className="text-xs font-mono uppercase tracking-widest text-[var(--color-bullish)]">
              ▲ Bull Thesis
            </h2>
          </CardHeader>
          <CardContent>
            <BullBearList items={brief.bull_thesis} type="bull" />
          </CardContent>
        </Card>

        {/* Bear case */}
        <Card>
          <CardHeader className="pb-3">
            <h2 className="text-xs font-mono uppercase tracking-widest text-[var(--color-bearish)]">
              ▼ Bear Case
            </h2>
          </CardHeader>
          <CardContent>
            <BullBearList items={brief.bear_case} type="bear" />
          </CardContent>
        </Card>
      </div>

      {/* ── 3. CROSS-SOURCE CONTRADICTIONS (NOVELTY ANCHOR) ── */}
      {brief.contradictions.length > 0 && (
        <Card className="border-[var(--color-bearish-dim)]">
          <CardHeader className="pb-3">
            <div className="flex items-center gap-2">
              <AlertTriangle
                size={14}
                className="text-[var(--color-bearish)]"
                aria-hidden="true"
              />
              <h2 className="text-xs font-mono uppercase tracking-widest text-[var(--color-bearish)]">
                Cross-Source Contradictions — AltBrief Novel Signal
              </h2>
            </div>
          </CardHeader>
          <CardContent>
            <ContradictionSection contradictions={brief.contradictions} />
          </CardContent>
        </Card>
      )}

      {/* ── 4. ALT-DATA SIGNALS ── */}
      <Card>
        <CardHeader className="pb-3">
          <h2 className="text-xs font-mono uppercase tracking-widest text-[var(--color-text-muted)]">
            Alt-Data Signal Dashboard —{" "}
            <span className="text-[var(--color-gold)]">★ = Peer-Reviewed</span>
          </h2>
        </CardHeader>
        <CardContent>
          <div
            className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-3"
            role="list"
            aria-label="Individual data source signals"
          >
            {sortedSignals.map((signal, i) => (
              <div key={signal.source} role="listitem">
                <SignalCard signal={signal} index={i} />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* ── 5. BRIEF NARRATIVE ── */}
      <Card>
        <CardHeader className="pb-3">
          <h2 className="text-xs font-mono uppercase tracking-widest text-[var(--color-text-muted)]">
            Analysis Narrative
          </h2>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed max-w-4xl">
            {brief.brief_narrative}
          </p>
        </CardContent>
      </Card>

      {/* ── 6. RISK FACTORS ── */}
      {brief.risk_factors.length > 0 && (
        <Card>
          <CardHeader className="pb-3">
            <div className="flex items-center gap-2">
              <Shield
                size={14}
                className="text-[var(--color-neutral)]"
                aria-hidden="true"
              />
              <h2 className="text-xs font-mono uppercase tracking-widest text-[var(--color-neutral)]">
                Risk Factors
              </h2>
            </div>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2" role="list">
              {brief.risk_factors.map((risk, i) => (
                <motion.li
                  key={i}
                  initial={{ opacity: 0, x: -4 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.2, delay: i * 0.04 }}
                  className="flex items-start gap-2.5 text-sm text-[var(--color-text-secondary)] leading-relaxed"
                >
                  <span
                    className="shrink-0 mt-0.5 text-xs font-mono text-[var(--color-neutral)]"
                    aria-hidden="true"
                  >
                    ◆
                  </span>
                  {risk}
                </motion.li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {/* ── 7. DATA QUALITY FOOTER ── */}
      <div className="flex items-center justify-between text-[10px] font-mono text-[var(--color-text-muted)] border-t border-[var(--color-border-subtle)] pt-4">
        <span>
          Data quality:{" "}
          <span className={qualityColorClass(brief.data_quality_flag)}>
            {qualityLabel(brief.data_quality_flag)}
          </span>{" "}
          ({brief.sources_used.length}/{8} sources)
        </span>
        <span>
          Generated {formatRelativeTime(brief.generated_at)} · latency{" "}
          {formatLatency(brief.latency_seconds)} · cost{" "}
          {formatCost(brief.cost_usd)}
        </span>
      </div>
    </motion.article>
  );
}

// ── Skeleton loading state ──────────────────────────────────────────────────

export function BriefCardSkeleton() {
  return (
    <div className="space-y-6" aria-label="Loading investment brief" aria-busy="true">
      <Card>
        <CardHeader>
          <div className="flex items-start justify-between gap-4">
            <div className="space-y-3 flex-1">
              <div className="flex items-center gap-3">
                <Skeleton className="h-9 w-24" />
                <Skeleton className="h-6 w-20 rounded-full" />
              </div>
              <Skeleton className="h-6 w-48" />
              <Skeleton className="h-4 w-32" />
            </div>
            <Skeleton className="h-24 w-24 rounded-full" />
          </div>
        </CardHeader>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {[0, 1].map((i) => (
          <Card key={i}>
            <CardHeader>
              <Skeleton className="h-3 w-24" />
            </CardHeader>
            <CardContent className="space-y-3">
              {[0, 1, 2, 3].map((j) => (
                <Skeleton key={j} className="h-4 w-full" />
              ))}
            </CardContent>
          </Card>
        ))}
      </div>

      <Card>
        <CardHeader>
          <Skeleton className="h-3 w-32" />
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-3">
            {[0, 1, 2, 3, 4, 5].map((i) => (
              <Skeleton key={i} className="h-36 w-full rounded-lg" />
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
