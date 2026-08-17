"use client";

import { motion, useReducedMotion } from "framer-motion";

const MEDAL_STYLES: Record<number, { text: string; bg: string; border: string; label: string }> = {
  1: {
    text:   "oklch(72% 0.16 85)",
    bg:     "oklch(72% 0.16 85 / 0.12)",
    border: "oklch(72% 0.16 85 / 0.40)",
    label:  "1st place",
  },
  2: {
    text:   "oklch(72% 0.08 250)",
    bg:     "oklch(72% 0.08 250 / 0.12)",
    border: "oklch(72% 0.08 250 / 0.35)",
    label:  "2nd place",
  },
  3: {
    text:   "oklch(60% 0.14 40)",
    bg:     "oklch(60% 0.14 40 / 0.12)",
    border: "oklch(60% 0.14 40 / 0.40)",
    label:  "3rd place",
  },
};

const DEFAULT_STYLE = {
  text:   "var(--color-fg-tertiary)",
  bg:     "var(--color-bg-elevated)",
  border: "var(--color-border)",
  label:  "",
};

interface RankBadgeProps {
  rank: number;
  size?: "sm" | "md";
}

export function RankBadge({ rank, size = "sm" }: RankBadgeProps) {
  const prefersReduced = useReducedMotion();
  const style = MEDAL_STYLES[rank] ?? DEFAULT_STYLE;
  const isMedal = rank <= 3;
  const ordinal = rank === 1 ? "st" : rank === 2 ? "nd" : rank === 3 ? "rd" : "th";

  return (
    <motion.div
      initial={prefersReduced ? false : { scale: 0.7, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ type: "spring", stiffness: 400, damping: 22, delay: 0.15 }}
      className="inline-flex items-center gap-1 rounded-full border font-mono font-bold tabular-nums"
      style={{
        color: style.text,
        backgroundColor: style.bg,
        borderColor: style.border,
        fontSize: size === "md" ? "var(--text-sm)" : "var(--text-xs)",
        padding: size === "md" ? "4px 10px" : "2px 8px",
        boxShadow: isMedal ? `0 0 10px ${style.border}` : "none",
      }}
      aria-label={style.label || `Rank ${rank}`}
    >
      {isMedal && (
        <span aria-hidden="true">
          {rank === 1 ? "◆" : rank === 2 ? "◇" : "○"}
        </span>
      )}
      {rank <= 3 ? `${rank}${ordinal}` : `#${rank}`}
    </motion.div>
  );
}
