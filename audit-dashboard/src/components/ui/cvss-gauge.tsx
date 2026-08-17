"use client";

import { cn, parseCvssVector, cvssMetricLabel, cvssValueLabel } from "@/lib/utils";

interface CvssGaugeProps {
  score: number;
  vector: string;
  className?: string;
}

function scoreColor(score: number): string {
  if (score >= 9.0) return "var(--critical)";
  if (score >= 7.0) return "var(--high)";
  if (score >= 4.0) return "var(--medium)";
  if (score > 0) return "var(--low)";
  return "var(--info)";
}

function scoreLabel(score: number): string {
  if (score >= 9.0) return "Critical";
  if (score >= 7.0) return "High";
  if (score >= 4.0) return "Medium";
  if (score > 0) return "Low";
  return "Info";
}

export function CvssGauge({ score, vector, className }: CvssGaugeProps) {
  const metrics = parseCvssVector(vector);
  const pct = (score / 10) * 100;
  const color = scoreColor(score);

  return (
    <div className={cn("space-y-3", className)}>
      {/* Score + label */}
      <div className="flex items-center gap-3">
        <span
          className="text-3xl font-semibold font-mono tabular-nums"
          style={{ color }}
        >
          {score.toFixed(1)}
        </span>
        <div className="flex flex-col">
          <span className="text-xs font-semibold uppercase tracking-wide" style={{ color }}>
            {scoreLabel(score)}
          </span>
          <span className="text-xs text-[var(--text-muted)]">CVSS 4.0</span>
        </div>
      </div>

      {/* Gauge bar */}
      <div
        className="relative h-2 w-full overflow-hidden rounded-full"
        style={{ background: "var(--surface-overlay)" }}
        role="progressbar"
        aria-valuenow={score}
        aria-valuemin={0}
        aria-valuemax={10}
        aria-label={`CVSS score: ${score.toFixed(1)} out of 10`}
      >
        {/* Gradient track */}
        <div
          className="absolute inset-0 rounded-full opacity-20"
          style={{
            background:
              "linear-gradient(to right, oklch(0.68 0.15 255), oklch(0.75 0.16 72), oklch(0.68 0.18 45), oklch(0.62 0.22 27))",
          }}
        />
        {/* Score fill */}
        <div
          className="absolute inset-y-0 left-0 rounded-full transition-all duration-500"
          style={{
            width: `${pct}%`,
            background: color,
          }}
        />
      </div>

      {/* Vector string */}
      <div className="text-xs font-mono text-[var(--text-muted)] break-all">
        {vector}
      </div>

      {/* Metric breakdown */}
      <div className="grid grid-cols-2 gap-1">
        {Object.entries(metrics).map(([k, v]) => (
          <div key={k} className="flex items-center gap-1 text-xs">
            <abbr
              title={`${cvssMetricLabel(k)}: ${cvssValueLabel(k, v)}`}
              className="font-mono text-[var(--text-muted)] no-underline cursor-help"
            >
              {k}:{v}
            </abbr>
            <span className="text-[var(--text-subtle)] truncate">
              {cvssValueLabel(k, v)}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
