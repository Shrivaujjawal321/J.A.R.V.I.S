"use client";

import { motion, useReducedMotion } from "framer-motion";
import { TrendingUp, Zap, Clock } from "lucide-react";
import { priorityColor, effortColor, DIMENSION_LABELS } from "@/lib/utils";
import { cn } from "@/lib/utils";
import type { Improvement } from "@/lib/types";

interface ImprovementCardsProps {
  improvements: Improvement[];
}

const EFFORT_ICONS = {
  low: Zap,
  medium: Clock,
  high: Clock,
};

export function ImprovementCards({ improvements }: ImprovementCardsProps) {
  const prefersReduced = useReducedMotion();
  const sorted = [...improvements].sort((a, b) => {
    const priorityOrder = { P0: 0, P1: 1, P2: 2 };
    return priorityOrder[a.priority] - priorityOrder[b.priority];
  });

  return (
    <div className="flex flex-col gap-3">
      <h2 className="text-lg font-semibold text-[var(--color-fg)]">
        How to improve your score
      </h2>
      <p className="text-sm text-[var(--color-fg-muted)] -mt-1">
        Ordered by impact. Fix P0 items first.
      </p>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-1">
        {sorted.map((imp, i) => {
          const EffortIcon = EFFORT_ICONS[imp.effort];
          return (
            <motion.article
              key={`${imp.dimension}-${i}`}
              initial={prefersReduced ? false : { opacity: 0, y: 12, filter: "blur(4px)" }}
              animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
              transition={{
                duration: 0.4,
                delay: 0.07 * i,
                ease: [0.16, 1, 0.3, 1],
              }}
              className={cn(
                "rounded-xl bg-[var(--color-surface)] p-5 flex flex-col gap-3",
                "border border-transparent hover:border-[var(--color-border-subtle)] transition-colors duration-150"
              )}
              aria-label={`${imp.priority} improvement: ${imp.title}`}
            >
              {/* Header row */}
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-center gap-2 flex-wrap">
                  {/* Priority badge */}
                  <span
                    className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-mono font-bold"
                    style={{
                      color: priorityColor(imp.priority),
                      backgroundColor: `${priorityColor(imp.priority)}18`,
                      borderColor: `${priorityColor(imp.priority)}30`,
                      border: "1px solid",
                    }}
                  >
                    {imp.priority}
                  </span>
                  {/* Dimension tag */}
                  <span className="text-xs text-[var(--color-fg-faint)] font-mono bg-[var(--color-surface-2)] px-2 py-0.5 rounded-md">
                    {DIMENSION_LABELS[imp.dimension] ?? imp.dimension}
                  </span>
                </div>

                {/* Score impact */}
                <div
                  className="flex items-center gap-1 flex-shrink-0 text-xs font-mono font-bold rounded-full px-2.5 py-1"
                  style={{
                    color: "var(--color-ok)",
                    backgroundColor: "oklch(72% 0.15 155 / 0.1)",
                  }}
                  aria-label={`Estimated impact: plus ${imp.estimated_score_delta} points`}
                >
                  <TrendingUp className="w-3 h-3" aria-hidden="true" />
                  +{imp.estimated_score_delta} pts
                </div>
              </div>

              {/* Title */}
              <h3 className="text-sm font-semibold text-[var(--color-fg)] leading-snug">
                {imp.title}
              </h3>

              {/* Description */}
              <p className="text-xs text-[var(--color-fg-muted)] leading-relaxed">
                {imp.description}
              </p>

              {/* Effort footer */}
              <div className="flex items-center gap-1.5 mt-auto pt-1">
                <EffortIcon
                  className="w-3 h-3 flex-shrink-0"
                  style={{ color: effortColor(imp.effort) }}
                  aria-hidden="true"
                />
                <span
                  className="text-xs font-medium capitalize"
                  style={{ color: effortColor(imp.effort) }}
                >
                  {imp.effort} effort
                </span>
              </div>
            </motion.article>
          );
        })}
      </div>
    </div>
  );
}
