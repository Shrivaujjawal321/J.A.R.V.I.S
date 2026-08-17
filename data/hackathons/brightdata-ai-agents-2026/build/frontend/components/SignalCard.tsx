"use client";

import { motion } from "framer-motion";
import { ExternalLink } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
  cn,
  directionLabel,
  directionArrow,
  formatConfidence,
  getSourceIcon,
  alphaTierLabel,
} from "@/lib/utils";
import type { Signal } from "@/lib/types";

interface SignalCardProps {
  signal: Signal;
  index?: number;
}

export function SignalCard({ signal, index = 0 }: SignalCardProps) {
  const isGold = signal.alpha_tier === "gold";
  const isCaution = signal.alpha_tier === "caution";

  return (
    <motion.article
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{
        duration: 0.25,
        delay: index * 0.05,
        ease: [0.19, 1, 0.22, 1],
      }}
      className={cn(
        "relative rounded-lg border p-4 flex flex-col gap-3 transition-colors",
        isGold
          ? "border-[var(--color-gold-border)] gold-shimmer"
          : isCaution
            ? "border-orange-900/50 bg-orange-950/20"
            : "border-[var(--color-border)] bg-[var(--color-surface-1)] hover:bg-[var(--color-surface-2)]",
      )}
      aria-label={`${signal.source} signal: ${directionLabel(signal.direction)}`}
    >
      {/* Gold tier badge — peer-reviewed */}
      {isGold && (
        <div
          className="absolute -top-2 -right-2 bg-[var(--color-gold)] text-black text-[10px] font-mono font-bold uppercase tracking-widest px-2 py-0.5 rounded-full"
          aria-label="Peer-reviewed signal"
        >
          ★ GOLD
        </div>
      )}

      {/* Header row: source + direction */}
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-2 min-w-0">
          <span className="text-base shrink-0" aria-hidden="true">
            {getSourceIcon(signal.source)}
          </span>
          <div className="min-w-0">
            <p className="text-xs font-mono uppercase tracking-widest text-[var(--color-text-muted)] truncate">
              {signal.source}
            </p>
          </div>
        </div>

        {/* Direction badge */}
        <Badge
          variant={
            signal.direction === "bullish"
              ? "bullish"
              : signal.direction === "bearish"
                ? "bearish"
                : "neutral"
          }
          className="shrink-0"
        >
          {directionArrow(signal.direction)} {directionLabel(signal.direction)}
        </Badge>
      </div>

      {/* Summary */}
      <p className="text-sm text-[var(--color-text-primary)] leading-relaxed">
        {signal.summary}
      </p>

      {/* Confidence bar */}
      <div className="space-y-1.5">
        <div className="flex items-center justify-between">
          <span className="text-[10px] font-mono uppercase tracking-widest text-[var(--color-text-muted)]">
            Confidence
          </span>
          <span className="text-[11px] font-mono text-[var(--color-text-secondary)]">
            {formatConfidence(signal.confidence)}
          </span>
        </div>
        <Progress
          value={Math.round(signal.confidence * 100)}
          className={cn(
            "h-1.5",
            signal.direction === "bullish"
              ? "[&>div]:bg-[var(--color-bullish)]"
              : signal.direction === "bearish"
                ? "[&>div]:bg-[var(--color-bearish)]"
                : "[&>div]:bg-[var(--color-neutral)]",
          )}
          aria-hidden="true"
        />
      </div>

      {/* Footer: alpha tier + citation */}
      <div className="flex items-center justify-between gap-2 pt-1 border-t border-[var(--color-border-subtle)]">
        <div className="flex items-center gap-1.5">
          <Badge
            variant={
              isGold ? "gold" : isCaution ? "caution" : "secondary"
            }
            className="text-[9px] py-0 px-1.5"
          >
            {alphaTierLabel(signal.alpha_tier)}
          </Badge>
        </div>

        {signal.citation_url && (
          <a
            href={signal.citation_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 text-[10px] font-mono text-[var(--color-accent)] hover:text-[var(--color-text-primary)] transition-colors focus-visible:ring-2 focus-visible:ring-[var(--color-accent)] rounded"
            aria-label={`View source for ${signal.source}`}
          >
            <ExternalLink size={10} aria-hidden="true" />
            SOURCE
          </a>
        )}
      </div>

      {/* Caution overlay for Reddit/GDELT */}
      {isCaution && (
        <p className="text-[10px] text-orange-400/70 font-mono mt-0.5">
          Zero alpha in empirical studies (Alpha Architect 2024)
        </p>
      )}
    </motion.article>
  );
}
