"use client";

import { motion, useReducedMotion } from "framer-motion";
import type { UploadQuota } from "@/lib/types";

const TIERS = {
  plenty: {
    text:   "var(--color-status-healthy-fg)",
    bg:     "var(--color-status-healthy-bg)",
    border: "var(--color-status-healthy-border)",
  },
  low: {
    text:   "var(--color-status-warning-fg)",
    bg:     "var(--color-status-warning-bg)",
    border: "var(--color-status-warning-border)",
  },
  exhausted: {
    text:   "var(--color-status-critical-fg)",
    bg:     "var(--color-status-critical-bg)",
    border: "var(--color-status-critical-border)",
  },
} as const;

interface UploadCounterProps {
  quota: UploadQuota;
}

export function UploadCounter({ quota }: UploadCounterProps) {
  const prefersReduced = useReducedMotion();
  const tier =
    quota.remaining === 0 ? "exhausted"
    : quota.remaining <= 2 ? "low"
    : "plenty";
  const colors = TIERS[tier];

  const ariaLabel =
    quota.remaining === 0
      ? "Upload limit reached — 0 of 5 remaining"
      : `${quota.remaining} of ${quota.max} dataset uploads remaining`;

  return (
    <motion.div
      key={quota.remaining}
      initial={prefersReduced ? false : { scale: 0.9, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ type: "spring", stiffness: 280, damping: 32 }}
      className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border text-xs font-medium"
      style={{
        backgroundColor: colors.bg,
        borderColor: colors.border,
        color: colors.text,
      }}
      aria-label={ariaLabel}
      title={ariaLabel}
    >
      {/* Pip row */}
      <div className="flex gap-0.5" aria-hidden="true">
        {Array.from({ length: quota.max }).map((_, i) => (
          <span
            key={i}
            className="w-1.5 h-1.5 rounded-full transition-opacity duration-200"
            style={{
              backgroundColor: "currentColor",
              opacity: i < quota.used ? 1 : 0.25,
            }}
          />
        ))}
      </div>
      <span className="tabular-nums font-mono">{quota.remaining}</span>
      <span className="hidden sm:inline">remaining</span>
    </motion.div>
  );
}
