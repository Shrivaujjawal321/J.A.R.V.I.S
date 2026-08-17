"use client";

import { motion, useReducedMotion } from "framer-motion";
import { XCircle, ChevronRight } from "lucide-react";
import Link from "next/link";

const RELEVANT_EXAMPLES = [
  "Steel manufacturing sensor streams (blast furnace, rolling mill, caster)",
  "Industrial time-series with operational labels or defect flags",
  "Condition monitoring data (vibration, temperature, pressure readings)",
  "Quality defect datasets from steel production processes",
  "Predictive maintenance event logs from heavy industrial equipment",
];

interface RejectedBannerProps {
  filename: string;
  reason?: string;
}

export function RejectedBanner({ filename, reason }: RejectedBannerProps) {
  const prefersReduced = useReducedMotion();

  return (
    <motion.div
      initial={prefersReduced ? false : { opacity: 0, y: -8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ type: "spring", stiffness: 380, damping: 24 }}
      className="rounded-xl overflow-hidden"
      style={{
        background: "var(--color-status-critical-bg)",
        border: "1px solid var(--color-status-critical-border)",
        borderLeft: "4px solid var(--color-status-critical-fg)",
      }}
      role="alert"
      aria-labelledby="rejection-heading"
    >
      <div className="p-6 flex flex-col gap-5">
        {/* Header */}
        <div className="flex items-start gap-3">
          <XCircle
            className="w-6 h-6 flex-shrink-0 mt-0.5"
            style={{ color: "var(--color-status-critical-fg)" }}
            aria-hidden="true"
          />
          <div className="flex flex-col gap-1">
            <h2
              id="rejection-heading"
              className="text-xl font-semibold"
              style={{ color: "var(--color-fg-primary)" }}
            >
              Dataset not matched to hackathon scope
            </h2>
            <p className="text-sm" style={{ color: "var(--color-fg-secondary)" }}>
              <span className="font-mono">{filename}</span>
              {" — "}
              {reason ?? "Dataset is not relevant to the Tata Steel Hackathon. Relevance Score: 0."}
            </p>
          </div>
        </div>

        {/* Divider */}
        <div className="hud-divider" aria-hidden="true" />

        {/* What IS relevant */}
        <div className="flex flex-col gap-3">
          <p className="label-caps">
            What qualifies for this hackathon
          </p>
          <ul className="flex flex-col gap-2" aria-label="Accepted dataset types">
            {RELEVANT_EXAMPLES.map((example) => (
              <li
                key={example}
                className="flex items-start gap-2 text-sm"
                style={{ color: "var(--color-fg-secondary)" }}
              >
                <ChevronRight
                  className="w-4 h-4 flex-shrink-0 mt-0.5"
                  style={{ color: "var(--color-accent-400)" }}
                  aria-hidden="true"
                />
                {example}
              </li>
            ))}
          </ul>
        </div>

        {/* CTAs */}
        <div className="flex gap-3 flex-wrap">
          <Link href="/" className="btn-primary">
            Try a different dataset
          </Link>
          <Link href="/datasets" className="btn-secondary">
            Browse accepted datasets
          </Link>
        </div>
      </div>
    </motion.div>
  );
}
