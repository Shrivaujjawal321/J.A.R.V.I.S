"use client";

import { useEffect, useRef, useState } from "react";
import { motion, useReducedMotion } from "framer-motion";
import { cn } from "@/lib/utils";
import { Filter, ShieldCheck, AlertOctagon } from "lucide-react";

interface FpFunnelProps {
  raw: number;
  fpFiltered: number;
  actionable: number;
  animate?: boolean;
  className?: string;
}

function useCountUp(target: number, duration: number, enabled: boolean) {
  const [count, setCount] = useState(enabled ? 0 : target);
  const rafRef = useRef<number | null>(null);

  useEffect(() => {
    if (!enabled) {
      setCount(target);
      return;
    }
    const start = performance.now();
    const animate = (now: number) => {
      const t = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - t, 3); // ease-out cubic
      setCount(Math.round(eased * target));
      if (t < 1) rafRef.current = requestAnimationFrame(animate);
    };
    rafRef.current = requestAnimationFrame(animate);
    return () => {
      if (rafRef.current !== null) cancelAnimationFrame(rafRef.current);
    };
  }, [target, duration, enabled]);

  return count;
}

export function FpFunnel({
  raw,
  fpFiltered,
  actionable,
  animate = true,
  className,
}: FpFunnelProps) {
  const shouldReduce = useReducedMotion();
  const shouldAnimate = animate && !shouldReduce;

  const rawCount = useCountUp(raw, 800, shouldAnimate);
  const fpCount = useCountUp(fpFiltered, 1000, shouldAnimate);
  const actionableCount = useCountUp(actionable, 1200, shouldAnimate);

  const fpPct = raw > 0 ? (fpFiltered / raw) * 100 : 0;
  const actionablePct = raw > 0 ? (actionable / raw) * 100 : 0;

  return (
    <div
      className={cn("space-y-3", className)}
      aria-label={`FP Funnel: ${raw} raw findings, ${fpFiltered} filtered as false positives, ${actionable} actionable`}
    >
      {/* Header */}
      <div className="flex items-center gap-2 text-xs font-medium text-[var(--text-muted)] uppercase tracking-wider">
        <Filter className="h-3.5 w-3.5" aria-hidden />
        False-Positive Funnel
      </div>

      {/* Three stages */}
      <div className="flex items-center gap-4">
        {/* RAW */}
        <Stage
          icon={<AlertOctagon className="h-4 w-4 text-[var(--text-muted)]" aria-hidden />}
          label="Raw"
          count={rawCount}
          countColor="var(--text)"
        />

        <Arrow label={`${fpFiltered} FP filtered`} />

        {/* FP Filtered */}
        <Stage
          icon={<Filter className="h-4 w-4" style={{ color: "var(--critical)" }} aria-hidden />}
          label="FP Filtered"
          count={fpCount}
          countColor="var(--critical)"
          dim
        />

        <Arrow label={`${actionable} actionable`} />

        {/* Actionable */}
        <Stage
          icon={<ShieldCheck className="h-4 w-4 text-[var(--accent)]" aria-hidden />}
          label="Actionable"
          count={actionableCount}
          countColor="var(--accent)"
          highlight
        />
      </div>

      {/* Segmented bar */}
      <div
        className="relative h-2 w-full overflow-hidden rounded-full"
        style={{ background: "var(--surface-overlay)" }}
        aria-hidden
      >
        {/* FP segment (muted red) */}
        <motion.div
          className="absolute inset-y-0 left-0 rounded-l-full"
          style={{ background: "var(--critical-bg)" }}
          initial={{ width: 0 }}
          animate={{ width: `${fpPct}%` }}
          transition={{ duration: shouldAnimate ? 1.0 : 0, ease: "easeOut" }}
        />
        {/* Actionable segment (accent) */}
        <motion.div
          className="absolute inset-y-0 rounded-r-full"
          style={{
            left: `${fpPct}%`,
            background: "var(--accent)",
            opacity: 0.6,
          }}
          initial={{ width: 0 }}
          animate={{ width: `${actionablePct}%` }}
          transition={{ duration: shouldAnimate ? 1.2 : 0, ease: "easeOut", delay: shouldAnimate ? 0.2 : 0 }}
        />
      </div>

      {/* Legend */}
      <div className="flex items-center gap-4 text-xs text-[var(--text-muted)]">
        <span className="flex items-center gap-1.5">
          <span className="inline-block h-2 w-2 rounded-sm" style={{ background: "var(--critical-bg)", border: "1px solid var(--critical-border)" }} />
          False positives ({fpFiltered})
        </span>
        <span className="flex items-center gap-1.5">
          <span className="inline-block h-2 w-2 rounded-sm" style={{ background: "var(--accent)", opacity: 0.6 }} />
          Actionable ({actionable})
        </span>
      </div>
    </div>
  );
}

function Stage({
  icon,
  label,
  count,
  countColor,
  dim = false,
  highlight = false,
}: {
  icon: React.ReactNode;
  label: string;
  count: number;
  countColor: string;
  dim?: boolean;
  highlight?: boolean;
}) {
  return (
    <div
      className={cn(
        "flex flex-col items-center gap-1 min-w-[4rem]",
        dim && "opacity-70"
      )}
    >
      <div
        className={cn(
          "flex h-9 w-9 items-center justify-center rounded-lg",
          highlight
            ? "bg-[var(--accent-muted)] border border-[var(--accent)]"
            : "bg-[var(--surface-raised)] border border-[var(--border)]"
        )}
      >
        {icon}
      </div>
      <span
        className="text-xl font-bold tabular-nums font-mono"
        style={{ color: countColor }}
        aria-live="polite"
        aria-atomic="true"
      >
        {count}
      </span>
      <span className="text-xs text-[var(--text-muted)] text-center leading-tight">
        {label}
      </span>
    </div>
  );
}

function Arrow({ label }: { label: string }) {
  return (
    <div className="flex flex-col items-center gap-0.5 flex-1 min-w-0">
      <div className="flex w-full items-center">
        <div className="flex-1 h-px bg-[var(--border)]" />
        <div
          className="h-0 w-0"
          style={{
            borderTop: "4px solid transparent",
            borderBottom: "4px solid transparent",
            borderLeft: "5px solid var(--border)",
          }}
        />
      </div>
      <span className="text-xs text-[var(--text-subtle)] truncate max-w-full text-center px-1">
        {label}
      </span>
    </div>
  );
}
