"use client";

import { motion, useReducedMotion } from "framer-motion";
import { RadarChart, PolarGrid, PolarAngleAxis, Radar, ResponsiveContainer } from "recharts";
import { severityColor, DIMENSION_LABELS } from "@/lib/utils";
import { cn } from "@/lib/utils";
import type { AuditResult, SubDimension } from "@/lib/types";

interface SubScoresProps {
  result: AuditResult;
  previousResult?: AuditResult | null;
}

const SEVERITY_ICONS = {
  ok: "●",
  info: "◎",
  warning: "▲",
  critical: "■",
} as const;

export function SubScores({ result, previousResult }: SubScoresProps) {
  const prefersReduced = useReducedMotion();
  // domain_pdm is null for tabular datasets (time-series-only check) — drop any
  // dimension whose value is null/undefined so the map never reads `.score` of null.
  const dimensions = (Object.keys(result.sub_scores) as SubDimension[]).filter(
    (dim) => result.sub_scores[dim] != null
  );

  const radarData = dimensions.map((dim) => ({
    subject: DIMENSION_LABELS[dim] ?? dim,
    score: result.sub_scores[dim].score,
    previous: previousResult?.sub_scores[dim]?.score,
  }));

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Radar chart */}
      <motion.div
        initial={prefersReduced ? false : { opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.1 }}
        className="rounded-xl bg-[var(--color-surface)] p-6"
        role="img"
        aria-label="Radar chart showing scores across all quality dimensions"
      >
        <h3 className="text-sm font-medium text-[var(--color-fg-muted)] mb-4">
          Quality radar
        </h3>
        <div className="h-64" aria-hidden="true">
          <ResponsiveContainer width="100%" height={256} minHeight={256}>
            <RadarChart data={radarData} margin={{ top: 10, right: 30, bottom: 10, left: 30 }}>
              <PolarGrid
                gridType="polygon"
                stroke="oklch(28% 0.01 250 / 0.4)"
              />
              <PolarAngleAxis
                dataKey="subject"
                tick={{ fill: "oklch(55% 0.008 250)", fontSize: 10, fontFamily: "var(--font-mono)" }}
              />
              {previousResult && (
                <Radar
                  dataKey="previous"
                  stroke="oklch(55% 0.008 250)"
                  fill="oklch(55% 0.008 250)"
                  fillOpacity={0.05}
                  strokeOpacity={0.3}
                  strokeWidth={1}
                />
              )}
              <Radar
                dataKey="score"
                stroke="oklch(55% 0.19 250)"
                fill="oklch(55% 0.19 250)"
                fillOpacity={0.12}
                strokeWidth={2}
              />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </motion.div>

      {/* Dimension list */}
      <div className="rounded-xl bg-[var(--color-surface)] p-6 flex flex-col gap-1">
        <h3 className="text-sm font-medium text-[var(--color-fg-muted)] mb-3">
          Dimension breakdown
        </h3>
        {dimensions.map((dim, i) => {
          const sub = result.sub_scores[dim];
          const prev = previousResult?.sub_scores[dim];
          const delta = prev ? sub.score - prev.score : null;

          return (
            <motion.div
              key={dim}
              initial={prefersReduced ? false : { opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3, delay: 0.05 * i }}
              className="group"
            >
              <div className="flex items-center gap-3 py-2.5 px-3 rounded-lg hover:bg-[var(--color-surface-2)] transition-colors duration-100">
                {/* Severity dot */}
                <span
                  className="text-xs flex-shrink-0 w-4 text-center"
                  style={{ color: severityColor(sub.severity) }}
                  aria-label={`Severity: ${sub.severity}`}
                >
                  {SEVERITY_ICONS[sub.severity]}
                </span>

                {/* Name */}
                <span className="flex-1 text-sm text-[var(--color-fg-muted)] group-hover:text-[var(--color-fg)] transition-colors">
                  {DIMENSION_LABELS[dim] ?? dim}
                </span>

                {/* Score bar */}
                <div className="w-20 h-1.5 bg-[var(--color-surface-3)] rounded-full overflow-hidden flex-shrink-0" aria-hidden="true">
                  <motion.div
                    className="h-full rounded-full"
                    style={{ backgroundColor: severityColor(sub.severity) }}
                    initial={prefersReduced ? false : { width: 0 }}
                    animate={{ width: `${sub.score}%` }}
                    transition={{ duration: 0.8, delay: 0.1 * i, ease: [0.16, 1, 0.3, 1] }}
                  />
                </div>

                {/* Score number */}
                <span className="font-mono tabular-nums text-sm w-8 text-right text-[var(--color-fg)]">
                  {sub.score}
                </span>

                {/* Delta */}
                {delta != null && (
                  <span
                    className={cn(
                      "font-mono text-xs w-8 text-right tabular-nums",
                      delta > 0 && "text-[var(--color-ok)]",
                      delta < 0 && "text-[var(--color-critical)]",
                      delta === 0 && "text-[var(--color-fg-faint)]"
                    )}
                    aria-label={`Change: ${delta > 0 ? "+" : ""}${delta}`}
                  >
                    {delta > 0 ? "+" : ""}{delta}
                  </span>
                )}
              </div>

              {/* Detail text (on hover via CSS group) */}
              <p className="text-xs text-[var(--color-fg-faint)] px-10 pb-1 hidden group-hover:block">
                {sub.detail}
              </p>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
