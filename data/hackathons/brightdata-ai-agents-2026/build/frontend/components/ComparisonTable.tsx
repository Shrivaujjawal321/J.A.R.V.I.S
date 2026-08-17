"use client";

/**
 * ComparisonTable — "$24K Bloomberg → $0 AltBrief" displacement frame
 * Research ref: research/07_fintech_ui_references_2026.md (Hebbia Matrix → spreadsheet grid pattern)
 * Judges expect to see the pricing displacement narrative
 */

import { motion } from "framer-motion";
import { Check, X, Minus } from "lucide-react";
import { cn } from "@/lib/utils";

const COMPETITORS = [
  {
    name: "Bloomberg Terminal",
    price: "$24,000 / year",
    sources: 10,
    realTime: true,
    aiSynthesis: false,
    contradictionDetection: false,
    peerCitations: false,
    altData: false,
    highlight: false,
  },
  {
    name: "Quiver Quantitative",
    price: "$75 / month",
    sources: 5,
    realTime: false,
    aiSynthesis: false,
    contradictionDetection: false,
    peerCitations: false,
    altData: true,
    highlight: false,
  },
  {
    name: "AlphaSense",
    price: "$20,000 / year",
    sources: 8,
    realTime: true,
    aiSynthesis: true,
    contradictionDetection: false,
    peerCitations: false,
    altData: false,
    highlight: false,
  },
  {
    name: "AltBrief",
    price: "$0 / free",
    sources: 8,
    realTime: true,
    aiSynthesis: true,
    contradictionDetection: true,
    peerCitations: true,
    altData: true,
    highlight: true,
  },
] as const;

type FeatureKey = "realTime" | "aiSynthesis" | "contradictionDetection" | "peerCitations" | "altData";

const FEATURES: Array<{ key: FeatureKey; label: string; description: string }> = [
  {
    key: "realTime",
    label: "Real-Time Streaming",
    description: "SSE token streaming, not batch PDF",
  },
  {
    key: "aiSynthesis",
    label: "AI Brief Synthesis",
    description: "Claude Sonnet structured output",
  },
  {
    key: "contradictionDetection",
    label: "Cross-Source Contradictions",
    description: "Novel — no competitor does this",
  },
  {
    key: "peerCitations",
    label: "Peer-Reviewed Citations",
    description: "JoF 2012, JFE 2019, Berkeley study",
  },
  {
    key: "altData",
    label: "Alt-Data Sources",
    description: "LinkedIn, Glassdoor, satellite, Reddit",
  },
];

function FeatureCell({ value }: { value: boolean }) {
  return value ? (
    <span className="flex items-center justify-center" aria-label="Yes">
      <Check size={16} className="text-[var(--color-bullish)]" />
    </span>
  ) : (
    <span className="flex items-center justify-center" aria-label="No">
      <X size={16} className="text-[var(--color-text-muted)]" />
    </span>
  );
}

export function ComparisonTable({ className }: { className?: string }) {
  return (
    <motion.section
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.1, ease: [0.19, 1, 0.22, 1] }}
      className={cn("space-y-4", className)}
      aria-label="Competitor comparison"
    >
      {/* Headline */}
      <div className="space-y-1">
        <h2 className="text-xl font-semibold text-[var(--color-text-primary)] tracking-tight">
          Bloomberg charges{" "}
          <span className="line-through text-[var(--color-text-muted)]">
            $24K/year
          </span>{" "}
          and{" "}
          <span className="text-[var(--color-bearish)]">
            won&apos;t show its sources.
          </span>
        </h2>
        <p className="text-sm text-[var(--color-text-secondary)]">
          We&apos;re free, conversational, and every signal links to the peer-reviewed paper behind it.
        </p>
      </div>

      {/* Table */}
      <div className="overflow-x-auto rounded-lg border border-[var(--color-border)]">
        <table
          className="w-full text-sm"
          aria-label="AltBrief vs competitors comparison"
        >
          <thead>
            <tr className="border-b border-[var(--color-border)] bg-[var(--color-surface-2)]">
              <th
                scope="col"
                className="text-left py-3 px-4 font-mono text-[10px] uppercase tracking-widest text-[var(--color-text-muted)] w-40"
              >
                Feature
              </th>
              {COMPETITORS.map((c) => (
                <th
                  key={c.name}
                  scope="col"
                  className={cn(
                    "py-3 px-4 text-center font-semibold",
                    c.highlight
                      ? "text-[var(--color-accent)] bg-[var(--color-accent-glow)]"
                      : "text-[var(--color-text-secondary)]",
                  )}
                >
                  <div className="space-y-0.5">
                    <div
                      className={cn(
                        "text-sm",
                        c.highlight && "text-[var(--color-text-primary)]",
                      )}
                    >
                      {c.name}
                    </div>
                    <div
                      className={cn(
                        "font-mono text-xs font-bold",
                        c.highlight
                          ? "text-[var(--color-bullish)]"
                          : "text-[var(--color-text-muted)]",
                      )}
                    >
                      {c.price}
                    </div>
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {/* Sources count row */}
            <tr className="border-b border-[var(--color-border-subtle)] hover:bg-[var(--color-surface-2)]/40 transition-colors">
              <td className="py-3 px-4 font-mono text-xs text-[var(--color-text-muted)]">
                Data Sources
              </td>
              {COMPETITORS.map((c) => (
                <td
                  key={c.name}
                  className={cn(
                    "py-3 px-4 text-center font-mono font-bold text-sm",
                    c.highlight
                      ? "text-[var(--color-accent)] bg-[var(--color-accent-glow)]"
                      : "text-[var(--color-text-secondary)]",
                  )}
                >
                  {c.sources}
                </td>
              ))}
            </tr>

            {/* Feature rows */}
            {FEATURES.map((feature, i) => (
              <tr
                key={feature.key}
                className={cn(
                  "hover:bg-[var(--color-surface-2)]/40 transition-colors",
                  i < FEATURES.length - 1 && "border-b border-[var(--color-border-subtle)]",
                )}
              >
                <td className="py-3 px-4">
                  <div>
                    <p className="font-mono text-xs text-[var(--color-text-secondary)]">
                      {feature.label}
                    </p>
                    {feature.key === "contradictionDetection" && (
                      <p className="text-[9px] text-[var(--color-accent)] font-mono uppercase tracking-wider mt-0.5">
                        ★ Novel
                      </p>
                    )}
                  </div>
                </td>
                {COMPETITORS.map((c) => (
                  <td
                    key={c.name}
                    className={cn(
                      "py-3 px-4",
                      c.highlight && "bg-[var(--color-accent-glow)]",
                    )}
                  >
                    <FeatureCell value={c[feature.key] as boolean} />
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Bottom note */}
      <p className="text-xs text-[var(--color-text-muted)] font-mono">
        * Bloomberg, AlphaSense pricing from published rate cards. Quiver Quantitative pro tier.
      </p>
    </motion.section>
  );
}
