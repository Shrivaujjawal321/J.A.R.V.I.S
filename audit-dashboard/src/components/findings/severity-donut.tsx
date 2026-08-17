"use client";

import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts";
import type { Severity } from "@/lib/types";
import { severityLabel } from "@/lib/utils";

const SEVERITY_COLORS: Record<Severity, string> = {
  critical: "oklch(0.62 0.22 27)",
  high: "oklch(0.68 0.18 45)",
  medium: "oklch(0.75 0.16 72)",
  low: "oklch(0.68 0.15 255)",
  info: "oklch(0.58 0 0)",
};

interface SeverityDonutProps {
  data: Record<string, number>;
  onSeverityClick?: (severity: Severity | null) => void;
  activeSeverity?: Severity | null;
}

interface ChartEntry {
  name: Severity;
  value: number;
  color: string;
}

export function SeverityDonut({
  data,
  onSeverityClick,
  activeSeverity,
}: SeverityDonutProps) {
  const entries: ChartEntry[] = (
    ["critical", "high", "medium", "low", "info"] as Severity[]
  )
    .filter((s) => (data[s] ?? 0) > 0)
    .map((s) => ({
      name: s,
      value: data[s] ?? 0,
      color: SEVERITY_COLORS[s],
    }));

  const total = entries.reduce((sum, e) => sum + e.value, 0);

  return (
    <div className="flex items-center gap-4">
      {/* Donut */}
      <div className="relative h-[120px] w-[120px] shrink-0">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={entries}
              cx="50%"
              cy="50%"
              innerRadius={38}
              outerRadius={55}
              paddingAngle={2}
              dataKey="value"
              strokeWidth={0}
              onClick={(entry) => {
                if (onSeverityClick) {
                  const sev = entry.name as Severity;
                  onSeverityClick(activeSeverity === sev ? null : sev);
                }
              }}
              style={{ cursor: onSeverityClick ? "pointer" : "default" }}
            >
              {entries.map((entry) => (
                <Cell
                  key={entry.name}
                  fill={entry.color}
                  opacity={
                    activeSeverity && activeSeverity !== entry.name ? 0.3 : 1
                  }
                />
              ))}
            </Pie>
            <Tooltip
              content={({ active, payload }) => {
                if (!active || !payload?.[0]) return null;
                const entry = payload[0].payload as ChartEntry;
                return (
                  <div
                    className="rounded border px-2 py-1.5 text-xs shadow-lg"
                    style={{
                      background: "var(--surface-raised)",
                      borderColor: "var(--border)",
                      color: "var(--text)",
                    }}
                  >
                    <span className="font-medium" style={{ color: entry.color }}>
                      {severityLabel(entry.name)}
                    </span>
                    <span className="ml-2 text-[var(--text-muted)]">
                      {entry.value}
                    </span>
                  </div>
                );
              }}
            />
          </PieChart>
        </ResponsiveContainer>
        {/* Center label */}
        <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-xl font-bold tabular-nums" style={{ color: "var(--text)" }}>
            {total}
          </span>
          <span className="text-xs text-[var(--text-muted)]">total</span>
        </div>
      </div>

      {/* Legend */}
      <div className="flex flex-col gap-1">
        {entries.map((e) => (
          <button
            key={e.name}
            type="button"
            onClick={() =>
              onSeverityClick?.(activeSeverity === e.name ? null : e.name)
            }
            className="flex items-center gap-2 text-xs text-left transition-opacity"
            style={{
              opacity:
                activeSeverity && activeSeverity !== e.name ? 0.4 : 1,
            }}
            aria-pressed={activeSeverity === e.name}
          >
            <span
              className="h-2.5 w-2.5 shrink-0 rounded-sm"
              style={{ background: e.color }}
              aria-hidden
            />
            <span className="font-medium" style={{ color: "var(--text)" }}>
              {severityLabel(e.name)}
            </span>
            <span className="tabular-nums text-[var(--text-muted)]">
              {e.value}
            </span>
          </button>
        ))}
      </div>
    </div>
  );
}
