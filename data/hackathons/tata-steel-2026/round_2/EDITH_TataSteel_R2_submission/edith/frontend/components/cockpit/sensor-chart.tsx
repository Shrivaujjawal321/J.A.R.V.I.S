"use client";

import React, { useEffect, useRef, useCallback } from "react";
import { cn } from "@/lib/utils";
import type { SensorBuffer } from "@/store/edith-store";

// uPlot is ESM — import dynamically; module-level cache for the constructor
// The class is `declare class uPlot` — ctor typed as new(…)=>UPlotInstance via the local type below.
// eslint-disable-next-line @typescript-eslint/no-explicit-any
let uPlotCtor: ((opts: uPlot.Options, data: uPlot.AlignedData, container: HTMLElement) => any) | null = null;

type UPlotInstance = {
  destroy(): void;
  setData(data: uPlot.AlignedData, resetScales?: boolean): void;
  root: HTMLElement;
};

// Status → stroke colour
const STATUS_STROKE: Record<string, string> = {
  normal:   "oklch(72% 0.16 213)",
  warning:  "oklch(78% 0.17 78)",
  alarm:    "oklch(72% 0.21 48)",
  critical: "oklch(64% 0.23 27)",
};

const STATUS_GLOW: Record<string, string> = {
  warning:  "0 0 8px oklch(78% 0.17 78 / 0.30)",
  alarm:    "0 0 10px oklch(72% 0.21 48 / 0.35)",
  critical: "0 0 12px oklch(64% 0.23 27 / 0.40)",
};

interface SensorChartProps {
  buffer: SensorBuffer;
  height?: number;
  className?: string;
}

export function SensorChart({ buffer, height = 120, className }: SensorChartProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const plotRef = useRef<UPlotInstance | null>(null);
  const mountedRef = useRef(true);
  const roRef = useRef<ResizeObserver | null>(null);

  // Always-fresh buffer ref — avoids stale closure in effects/callbacks
  const bufferRef = useRef<SensorBuffer>(buffer);
  bufferRef.current = buffer;

  const buildOpts = useCallback(
    (width: number): uPlot.Options => {
      const meta = bufferRef.current.meta;
      const warn = meta.warning;
      const alrm = meta.alarm;
      const stroke = STATUS_STROKE[bufferRef.current.status] ?? STATUS_STROKE.normal;

      const series: uPlot.Series[] = [
        {}, // x-axis series (timestamps)
        {
          label: meta.label || meta.quantity || meta.tag,
          stroke,
          width: 1.5,
          spanGaps: true,
          fill: "oklch(72% 0.16 213 / 0.06)",
          paths: undefined,
        },
      ];

      // threshold band plugins via hooks
      const bands: Array<{ lo: number; hi: number; fill: string }> = [];
      if (warn != null && alrm != null) {
        if (meta.direction === "upper") {
          bands.push({ lo: warn, hi: alrm,       fill: "oklch(78% 0.17 78 / 0.08)" });
          bands.push({ lo: alrm, hi: alrm * 1.3, fill: "oklch(72% 0.21 48 / 0.10)" });
        } else {
          bands.push({ lo: alrm * 0.7, hi: alrm, fill: "oklch(72% 0.21 48 / 0.10)" });
          bands.push({ lo: alrm,       hi: warn,  fill: "oklch(78% 0.17 78 / 0.08)" });
        }
      }

      const plugins: uPlot.Plugin[] = [];
      if (bands.length > 0) {
        plugins.push({
          hooks: {
            draw: [(u) => {
              const ctx = u.ctx;
              ctx.save();
              for (const band of bands) {
                const y0 = u.valToPos(band.lo, "y", true);
                const y1 = u.valToPos(band.hi, "y", true);
                const x0 = u.bbox.left;
                const w = u.bbox.width;
                const minY = Math.min(y0, y1);
                const maxY = Math.max(y0, y1);
                ctx.fillStyle = band.fill;
                ctx.fillRect(x0, minY, w, maxY - minY);
              }
              ctx.restore();
            }],
          },
        });
      }

      if (warn != null || alrm != null) {
        plugins.push({
          hooks: {
            draw: [(u) => {
              const ctx = u.ctx;
              ctx.save();
              const x0 = u.bbox.left;
              const w = u.bbox.width;
              if (warn != null) {
                const y = u.valToPos(warn, "y", true);
                ctx.strokeStyle = "oklch(78% 0.17 78 / 0.45)";
                ctx.lineWidth = 1;
                ctx.setLineDash([4, 6]);
                ctx.beginPath();
                ctx.moveTo(x0, y);
                ctx.lineTo(x0 + w, y);
                ctx.stroke();
              }
              if (alrm != null) {
                const y = u.valToPos(alrm, "y", true);
                ctx.strokeStyle = "oklch(72% 0.21 48 / 0.55)";
                ctx.lineWidth = 1;
                ctx.setLineDash([4, 6]);
                ctx.beginPath();
                ctx.moveTo(x0, y);
                ctx.lineTo(x0 + w, y);
                ctx.stroke();
              }
              ctx.restore();
            }],
          },
        });
      }

      return {
        width,
        height,
        plugins,
        series,
        axes: [
          {
            stroke: "oklch(50% 0.010 250)",
            ticks: { stroke: "oklch(50% 0.010 250 / 0.3)", size: 4 },
            grid: { stroke: "oklch(100% 0 0 / 0.06)", dash: [2, 4] },
            font: "11px Geist Mono, monospace",
          },
          {
            stroke: "oklch(50% 0.010 250)",
            ticks: { stroke: "oklch(50% 0.010 250 / 0.3)", size: 4 },
            grid: { stroke: "oklch(100% 0 0 / 0.06)", dash: [2, 4] },
            font: "11px Geist Mono, monospace",
            label: meta.unit ? `${meta.label || meta.quantity || meta.tag} (${meta.unit})` : (meta.label || meta.quantity || meta.tag),
            labelFont: "11px Geist, sans-serif",
          },
        ],
        cursor: {
          drag: { x: false, y: false },
          sync: { key: "edith" },
        },
        scales: {
          x: { time: true },
          y: { auto: true },
        },
      };
    },
    // buildOpts only changes when meta/status/height change — stable across ticks
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [height],
  );

  // ── init / rebuild on mount (or when the sensor tag changes) ──────────────
  useEffect(() => {
    mountedRef.current = true;

    async function init(width: number) {
      if (!containerRef.current || !mountedRef.current) return;

      // Lazy-load uPlot constructor (cached after first load)
      if (!uPlotCtor) {
        const mod = await import("uplot");
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        uPlotCtor = (mod.default ?? mod) as any;
      }

      if (!mountedRef.current || !containerRef.current) return;

      const buf = bufferRef.current;
      const ts = buf.timestamps.slice();
      const vs = buf.values.map((v) => (v == null ? NaN : v));

      const opts = buildOpts(width);
      if (plotRef.current) {
        plotRef.current.destroy();
        plotRef.current = null;
      }

      try {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const plot = new (uPlotCtor as any)(opts, [ts, vs], containerRef.current);
        plotRef.current = plot as unknown as UPlotInstance;
      } catch (e) {
        console.error("[SensorChart] uPlot init failed:", e);
      }
    }

    function handleResize(entries: ResizeObserverEntry[]) {
      const entry = entries[0];
      if (!entry || !mountedRef.current) return;
      const w = Math.floor(entry.contentRect.width);
      if (w > 0) init(w);
    }

    if (containerRef.current) {
      roRef.current = new ResizeObserver(handleResize);
      roRef.current.observe(containerRef.current);
      const w = containerRef.current.clientWidth;
      if (w > 0) init(w);
    }

    return () => {
      mountedRef.current = false;
      roRef.current?.disconnect();
      roRef.current = null;
      plotRef.current?.destroy();
      plotRef.current = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [buffer.meta.tag]);

  // ── data feed: call setData imperatively on each render tick ─────────────
  // Use a layout effect WITHOUT dependency array so it runs after every commit.
  // We read from bufferRef (always fresh) and only call setData when plot exists
  // and data is non-empty. This is the "imperative bridge" pattern for uPlot in React.
  useEffect(() => {
    if (!plotRef.current) return;
    const buf = bufferRef.current;
    if (buf.timestamps.length === 0) return;
    const ts = buf.timestamps;
    const vs = buf.values.map((v) => (v == null ? NaN : v));
    try {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      (plotRef.current as any).setData([ts, vs]);
    } catch {}
  });  // NO dependency array → runs after EVERY committed render

  const glow = STATUS_GLOW[buffer.status] ?? "";

  return (
    <div
      className={cn("chart-canvas", className)}
      style={{ boxShadow: glow || undefined }}
      aria-label={`Live chart for ${buffer.meta.label || buffer.meta.tag}: ${buffer.latest != null ? buffer.latest.toFixed(2) : "—"} ${buffer.meta.unit}`}
      role="img"
    >
      {(() => {
        const st = buffer.status;
        const statusWord =
          st === "alarm" || st === "critical" ? "OVER LIMIT"
          : st === "warning" ? "RISING — WATCH"
          : "NORMAL";
        const statusColor =
          st === "alarm" || st === "critical" ? "var(--color-status-alarm-fg)"
          : st === "warning" ? "var(--color-status-warning-fg)"
          : "var(--color-status-healthy-fg)";
        const lim = buffer.meta.warning;
        const limitText =
          lim != null
            ? `safe ${buffer.meta.direction === "lower" ? "above" : "below"} ${lim}${buffer.meta.unit ? " " + buffer.meta.unit : ""}`
            : "";
        return (
          <div className="flex items-start justify-between mb-2 gap-2">
            <div className="flex flex-col min-w-0">
              <span className="text-xs font-medium truncate"
                    style={{ color: "var(--color-fg-primary)" }}>
                {buffer.meta.label || buffer.meta.quantity || buffer.meta.tag}
              </span>
              <span className="text-[10px] tracking-wide" style={{ color: statusColor }}>
                {statusWord}
                {limitText && (
                  <span style={{ color: "var(--color-fg-faint)" }}> · {limitText}</span>
                )}
              </span>
            </div>
            <div className="flex items-baseline gap-1 shrink-0">
              {buffer.latest != null && (
                <span className="mono-data text-sm font-semibold" style={{ color: statusColor }}>
                  {buffer.latest.toFixed(2)}
                </span>
              )}
              {buffer.meta.unit && (
                <span className="label-caps" style={{ color: "var(--color-fg-faint)" }}>
                  {buffer.meta.unit}
                </span>
              )}
            </div>
          </div>
        );
      })()}
      <div
        ref={containerRef}
        style={{ width: "100%", height }}
        className="overflow-hidden rounded"
      />
    </div>
  );
}
