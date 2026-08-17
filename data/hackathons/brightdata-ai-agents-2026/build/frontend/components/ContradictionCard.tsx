"use client";

/**
 * ContradictionCard — THE NOVELTY ANCHOR
 * Per research/19_contradiction_confidence_algo.md §7
 * These must POP visually — judges will look here.
 * High severity = red glow + animated border
 * Medium = amber
 * Low = emerald
 */

import { motion } from "framer-motion";
import { AlertTriangle, ArrowLeftRight } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { cn, severityColorClass } from "@/lib/utils";
import type { Contradiction } from "@/lib/types";

interface ContradictionCardProps {
  contradiction: Contradiction;
  index?: number;
}

const SEVERITY_STYLES = {
  high: {
    border: "border-[var(--color-bearish-dim)]",
    bg: "bg-[var(--color-bearish-bg)]",
    glow: "shadow-[0_0_20px_var(--color-bearish-bg)]",
    badgeText: "HIGH",
    icon: "text-[var(--color-bearish)]",
    labelColor: "text-[var(--color-bearish)]",
  },
  medium: {
    border: "border-[var(--color-neutral-dim)]",
    bg: "bg-[var(--color-neutral-bg)]",
    glow: "shadow-[0_0_12px_var(--color-neutral-bg)]",
    badgeText: "MEDIUM",
    icon: "text-[var(--color-neutral)]",
    labelColor: "text-[var(--color-neutral)]",
  },
  low: {
    border: "border-[var(--color-bullish-dim)]",
    bg: "bg-[var(--color-bullish-bg)]",
    glow: "",
    badgeText: "LOW",
    icon: "text-[var(--color-bullish)]",
    labelColor: "text-[var(--color-bullish)]",
  },
};

const TYPE_LABELS: Record<Contradiction["contradiction_type"], string> = {
  guidance_vs_hiring: "Guidance vs. Hiring",
  sentiment_divergence: "Sentiment Divergence",
  insider_vs_crowd: "Insider vs. Crowd",
  operational_vs_guided: "Operational vs. Guided",
  employee_vs_growth: "Employee Sentiment vs. Growth",
  other: "Cross-Source Contradiction",
};

export function ContradictionCard({
  contradiction,
  index = 0,
}: ContradictionCardProps) {
  const styles = SEVERITY_STYLES[contradiction.severity];

  return (
    <motion.article
      initial={{ opacity: 0, scale: 0.97, y: 12 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      transition={{
        duration: 0.35,
        delay: index * 0.08,
        ease: [0.34, 1.56, 0.64, 1],
      }}
      className={cn(
        "relative rounded-lg border-2 p-5 flex flex-col gap-4 overflow-hidden",
        styles.border,
        styles.bg,
        contradiction.severity === "high" ? styles.glow : "",
      )}
      role="alert"
      aria-label={`${contradiction.severity} severity contradiction: ${contradiction.signal_a_source} vs ${contradiction.signal_b_source}`}
    >
      {/* Animated border glow for high severity */}
      {contradiction.severity === "high" && (
        <motion.div
          className="absolute inset-0 rounded-lg border-2 border-[var(--color-bearish)]"
          animate={{ opacity: [0.3, 0.7, 0.3] }}
          transition={{ duration: 2.5, repeat: Infinity, ease: "easeInOut" }}
          aria-hidden="true"
        />
      )}

      {/* Header */}
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <div className="flex items-center gap-2">
          <AlertTriangle
            size={16}
            className={cn(styles.icon, "shrink-0")}
            aria-hidden="true"
          />
          <span
            className={cn(
              "text-[10px] font-mono uppercase tracking-widest font-bold",
              styles.labelColor,
            )}
          >
            CONTRADICTION DETECTED
          </span>
        </div>
        <div className="flex items-center gap-2">
          <Badge
            variant={
              contradiction.severity === "high"
                ? "bearish"
                : contradiction.severity === "medium"
                  ? "neutral"
                  : "bullish"
            }
            className="text-[9px] font-mono"
          >
            {styles.badgeText}
          </Badge>
          <span
            className={cn(
              "text-[9px] font-mono uppercase tracking-wider",
              severityColorClass(contradiction.severity),
            )}
          >
            {TYPE_LABELS[contradiction.contradiction_type]}
          </span>
        </div>
      </div>

      {/* Versus display — the key visual */}
      <div className="flex items-stretch gap-3 flex-col sm:flex-row">
        {/* Signal A */}
        <div className="flex-1 rounded-md border border-[var(--color-border)] bg-[var(--color-surface-1)]/60 p-3 space-y-1.5">
          <p className="text-[10px] font-mono uppercase tracking-widest text-[var(--color-text-muted)]">
            {contradiction.signal_a_source}
          </p>
          <p className="text-xs text-[var(--color-text-primary)] leading-snug">
            {contradiction.signal_a_brief}
          </p>
        </div>

        {/* VS divider */}
        <div className="flex items-center justify-center shrink-0 py-2 sm:py-0">
          <div className="flex items-center gap-1">
            <ArrowLeftRight
              size={14}
              className={cn(styles.icon)}
              aria-hidden="true"
            />
            <span
              className={cn(
                "text-[10px] font-mono font-bold uppercase",
                styles.labelColor,
              )}
            >
              VS
            </span>
          </div>
        </div>

        {/* Signal B */}
        <div className="flex-1 rounded-md border border-[var(--color-border)] bg-[var(--color-surface-1)]/60 p-3 space-y-1.5">
          <p className="text-[10px] font-mono uppercase tracking-widest text-[var(--color-text-muted)]">
            {contradiction.signal_b_source}
          </p>
          <p className="text-xs text-[var(--color-text-primary)] leading-snug">
            {contradiction.signal_b_brief}
          </p>
        </div>
      </div>

      {/* Explanation */}
      <div className="flex gap-2 items-start">
        <div
          className={cn(
            "shrink-0 w-0.5 self-stretch rounded-full",
            contradiction.severity === "high"
              ? "bg-[var(--color-bearish)]"
              : contradiction.severity === "medium"
                ? "bg-[var(--color-neutral)]"
                : "bg-[var(--color-bullish)]",
          )}
          aria-hidden="true"
        />
        <p className="text-xs text-[var(--color-text-secondary)] leading-relaxed italic">
          {contradiction.explanation}
        </p>
      </div>
    </motion.article>
  );
}

// ── Section wrapper ────────────────────────────────────────────────────────────

interface ContradictionSectionProps {
  contradictions: Contradiction[];
}

export function ContradictionSection({
  contradictions,
}: ContradictionSectionProps) {
  if (contradictions.length === 0) {
    return (
      <div className="flex items-center gap-2 text-[var(--color-bullish)] text-sm font-mono py-4">
        <span aria-hidden="true">✓</span>
        <span>No cross-source contradictions detected — signals are consistent</span>
      </div>
    );
  }

  return (
    <section aria-label="Cross-source contradictions" className="space-y-4">
      <div className="flex items-center gap-2 mb-1">
        <AlertTriangle
          size={14}
          className="text-[var(--color-bearish)]"
          aria-hidden="true"
        />
        <h3 className="text-xs font-mono uppercase tracking-widest text-[var(--color-text-muted)]">
          Cross-Source Contradictions —{" "}
          <span className="text-[var(--color-bearish)]">
            {contradictions.length} flagged
          </span>
        </h3>
      </div>
      <div className="space-y-3">
        {contradictions.map((c, i) => (
          <ContradictionCard
            key={`${c.signal_a_source}-${c.signal_b_source}-${i}`}
            contradiction={c}
            index={i}
          />
        ))}
      </div>
    </section>
  );
}
