"use client";

import { motion, useReducedMotion } from "framer-motion";
import { ScoreRing } from "@/components/ui/score-ring";
import { gradeColor, scoreRingColor } from "@/lib/utils";
import type { AuditResult } from "@/lib/types";
import { cn } from "@/lib/utils";

interface ScoreHeroProps {
  result: AuditResult;
  previousResult?: AuditResult | null;
}

export function ScoreHero({ result, previousResult }: ScoreHeroProps) {
  const prefersReduced = useReducedMotion();
  const delta = previousResult
    ? result.composite_score - previousResult.composite_score
    : null;

  return (
    <div className="flex flex-col sm:flex-row items-center gap-8 sm:gap-12">
      {/* Main score ring */}
      <div className="relative">
        <motion.div
          initial={prefersReduced ? false : { opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ type: "spring", stiffness: 120, damping: 18, delay: 0.1 }}
        >
          <ScoreRing
            score={result.composite_score}
            grade={result.grade}
            previousScore={previousResult?.composite_score}
            size="hero"
            showGrade={false}
            animateFrom={previousResult?.composite_score ?? 0}
          />
        </motion.div>

        {/* Delta badge */}
        {delta != null && (
          <motion.div
            initial={prefersReduced ? false : { opacity: 0, y: 8, scale: 0.8 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            transition={{ type: "spring", stiffness: 300, damping: 25, delay: 0.6 }}
            className={cn(
              "absolute -top-2 -right-2 font-mono font-bold text-sm px-2.5 py-1 rounded-full tabular-nums",
              delta > 0 && "bg-[oklch(72%_0.15_155/0.15)] text-[var(--color-ok)] border border-[oklch(72%_0.15_155/0.3)]",
              delta < 0 && "bg-[oklch(55%_0.18_25/0.15)] text-[var(--color-critical)] border border-[oklch(55%_0.18_25/0.3)]",
              delta === 0 && "bg-[var(--color-surface-3)] text-[var(--color-fg-muted)]"
            )}
            aria-label={`Score changed by ${delta > 0 ? "+" : ""}${delta} points`}
          >
            {delta > 0 ? "+" : ""}{delta} pts
          </motion.div>
        )}
      </div>

      {/* Score info */}
      <motion.div
        initial={prefersReduced ? false : { opacity: 0, x: 12 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1], delay: 0.2 }}
        className="flex flex-col items-center sm:items-start gap-2"
      >
        {/* Grade */}
        <div className="flex items-center gap-3">
          <span
            className="text-5xl font-bold font-mono"
            style={{ color: gradeColor(result.grade) }}
            aria-label={`Grade: ${result.grade}`}
          >
            {result.grade}
          </span>
          {previousResult && (
            <div className="flex flex-col gap-0.5">
              <span
                className="text-sm font-mono line-through opacity-40"
                style={{ color: gradeColor(previousResult.grade) }}
                aria-label={`Previous grade: ${previousResult.grade}`}
              >
                {previousResult.grade}
              </span>
            </div>
          )}
        </div>

        <p className="text-[var(--color-fg-muted)] text-sm max-w-xs text-center sm:text-left">
          {(result.n_rows ?? 0).toLocaleString()} rows &middot; {result.n_cols ?? 0} columns &middot;{" "}
          <span className="font-mono">{result.dataset_type === "time_series" ? "Time series" : "Tabular"}</span>
        </p>

        <p className="text-xs text-[var(--color-fg-faint)] font-mono">{result.filename}</p>

        {/* Previous vs current indicator */}
        {previousResult && (
          <div className="flex items-center gap-3 mt-1">
            <div className="flex items-center gap-1.5">
              <div
                className="w-3 h-0.5 rounded-full opacity-30"
                style={{ backgroundColor: scoreRingColor(previousResult.composite_score) }}
                aria-hidden="true"
              />
              <span className="text-xs text-[var(--color-fg-faint)] font-mono">v1: {previousResult.composite_score}</span>
            </div>
            <span className="text-[var(--color-fg-faint)] text-xs">→</span>
            <div className="flex items-center gap-1.5">
              <div
                className="w-3 h-0.5 rounded-full"
                style={{ backgroundColor: scoreRingColor(result.composite_score) }}
                aria-hidden="true"
              />
              <span className="text-xs text-[var(--color-fg-muted)] font-mono">v2: {result.composite_score}</span>
            </div>
          </div>
        )}
      </motion.div>

      {/* Readiness gauge */}
      {result.readiness != null && (
        <ReadinessGauge readiness={result.readiness} />
      )}
    </div>
  );
}

interface ReadinessGaugeProps {
  readiness: NonNullable<AuditResult["readiness"]>;
}

function ReadinessGauge({ readiness }: ReadinessGaugeProps) {
  const prefersReduced = useReducedMotion();
  const radius = 54;
  const stroke = 8;
  const circumference = 2 * Math.PI * radius;
  const dashOffset = circumference * (1 - readiness.readiness_pct / 100);

  return (
    <motion.div
      initial={prefersReduced ? false : { opacity: 0, x: 16 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1], delay: 0.35 }}
      className="flex flex-col items-center gap-2"
      aria-label={`ML readiness: ${readiness.readiness_pct}%`}
    >
      <div className="relative">
        <svg
          width={128}
          height={128}
          viewBox="0 0 128 128"
          fill="none"
          style={{ transform: "rotate(-90deg)" }}
          aria-hidden="true"
        >
          <circle cx={64} cy={64} r={radius} strokeWidth={stroke} stroke="oklch(22% 0.008 250)" fill="none" />
          <motion.circle
            cx={64}
            cy={64}
            r={radius}
            strokeWidth={stroke}
            stroke="oklch(55% 0.19 250)"
            strokeDasharray={circumference}
            initial={prefersReduced ? false : { strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: dashOffset }}
            transition={{ duration: 1.2, ease: [0.16, 1, 0.3, 1], delay: 0.5 }}
            strokeLinecap="round"
            fill="none"
            style={{ filter: "drop-shadow(0 0 6px oklch(55% 0.19 250 / 0.4))" }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="font-mono font-bold text-2xl tabular-nums text-[oklch(64%_0.15_250)]">
            {readiness.readiness_pct}%
          </span>
        </div>
      </div>
      <div className="flex flex-col items-center gap-0.5">
        <span className="text-xs font-medium text-[var(--color-fg-muted)]">ML Readiness</span>
        <span className="text-xs font-mono text-[var(--color-fg-faint)]">
          AUC {readiness.baseline_auc.toFixed(2)} / {readiness.target_auc.toFixed(2)}
        </span>
      </div>
    </motion.div>
  );
}
