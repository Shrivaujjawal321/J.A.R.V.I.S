"use client";

import { motion, useReducedMotion } from "framer-motion";

interface EdithReviewProps {
  review: string;
  filename: string;
}

export function EdithReview({ review, filename }: EdithReviewProps) {
  const prefersReduced = useReducedMotion();

  return (
    <motion.div
      initial={prefersReduced ? false : { opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1], delay: 0.1 }}
      className="rounded-xl bg-[var(--color-surface)] p-6 flex flex-col gap-4"
    >
      {/* Header */}
      <div className="flex items-center gap-3">
        <div
          className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 font-bold text-sm"
          style={{
            background: "linear-gradient(135deg, oklch(55% 0.19 250), oklch(46% 0.19 250))",
            color: "white",
          }}
          aria-hidden="true"
        >
          E
        </div>
        <div>
          <p className="text-sm font-semibold text-[var(--color-fg)]">EDITH&apos;s review</p>
          <p className="text-xs text-[var(--color-fg-faint)] font-mono truncate max-w-xs">{filename}</p>
        </div>
      </div>

      {/* Divider */}
      <div className="h-px bg-[var(--color-border-subtle)]" role="separator" />

      {/* Review text */}
      <div className="flex flex-col gap-3">
        {review.split("\n\n").map((paragraph, i) => (
          <p key={i} className="text-sm text-[var(--color-fg-muted)] leading-relaxed">
            {paragraph}
          </p>
        ))}
      </div>
    </motion.div>
  );
}
