"use client";

import React, { useState, useId } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";
import { StatusBadge } from "./status-badge";
import type { StatusBand } from "@/lib/types";

interface OutputCardProps {
  heading: string;
  brief: string;
  enhancedBrief?: React.ReactNode;
  citations?: string[];
  rul?: number | null;
  riskBand?: string;
  defaultExpanded?: boolean;
}

function toStatusBandSafe(rb: string | undefined): StatusBand | undefined {
  if (!rb) return undefined;
  const map: Record<string, StatusBand> = {
    healthy: "healthy", low: "healthy",
    warning: "warning", medium: "warning",
    alarm: "alarm", high: "alarm",
    critical: "critical",
  };
  return map[rb.toLowerCase()] ?? "unknown";
}

export function OutputCard({
  heading,
  brief,
  enhancedBrief,
  citations,
  rul,
  riskBand,
  defaultExpanded = false,
}: OutputCardProps) {
  const [expanded, setExpanded] = useState(defaultExpanded);
  const bodyId = useId();
  const band = toStatusBandSafe(riskBand);

  return (
    <div className={cn("output-card", expanded && "output-card--expanded")}>
      <button
        type="button"
        aria-expanded={expanded}
        aria-controls={bodyId}
        onClick={() => setExpanded((v) => !v)}
        className="output-card-header"
      >
        <div className="flex items-start gap-3 min-w-0">
          <motion.span
            animate={{ rotate: expanded ? 90 : 0 }}
            transition={{ duration: 0.15, ease: [0.16, 1, 0.3, 1] }}
            className="flex-shrink-0 mt-0.5"
            style={{ color: "var(--color-fg-tertiary)" }}
            aria-hidden="true"
          >
            <ChevronRight size={15} />
          </motion.span>
          <div className="min-w-0 text-left">
            <div
              className="text-sm font-medium mb-1 leading-snug"
              style={{ color: "var(--color-fg-primary)" }}
            >
              {heading}
            </div>
            <p
              className="text-xs leading-relaxed line-clamp-2"
              style={{ color: "var(--color-fg-secondary)" }}
            >
              {brief}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 flex-shrink-0 ml-2">
          {rul != null && (
            <span
              className="mono-data text-xs"
              style={{ color: "var(--color-fg-tertiary)" }}
            >
              {rul} cy
            </span>
          )}
          {band && <StatusBadge status={band} compact />}
        </div>
      </button>

      <AnimatePresence initial={false}>
        {expanded && (
          <motion.div
            id={bodyId}
            role="region"
            aria-label={`Details for ${heading}`}
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{
              height: { type: "spring", stiffness: 260, damping: 30 },
              opacity: { duration: 0.15 },
            }}
            style={{ overflow: "hidden" }}
          >
            <div className="output-card-body pt-3">
              {enhancedBrief && (
                <div
                  className="text-sm leading-relaxed mb-3"
                  style={{ color: "var(--color-fg-primary)" }}
                >
                  {enhancedBrief}
                </div>
              )}
              {citations && citations.length > 0 && (
                <div className="flex flex-wrap gap-1 mt-2" aria-label="Source citations">
                  <span className="label-caps mr-1 self-center">Sources:</span>
                  {citations.map((c, i) => (
                    <span key={i} className="cite-pill" aria-label={`Source: ${c}`}>
                      {c}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
