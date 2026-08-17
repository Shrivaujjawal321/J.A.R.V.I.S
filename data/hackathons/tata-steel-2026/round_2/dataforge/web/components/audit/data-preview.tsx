"use client";

import { useState } from "react";
import { motion, useReducedMotion } from "framer-motion";
import { cn } from "@/lib/utils";
import type { Preview } from "@/lib/types";

interface DataPreviewProps {
  preview: Preview;
}

export function DataPreview({ preview }: DataPreviewProps) {
  const prefersReduced = useReducedMotion();
  const [tab, setTab] = useState<"sample" | "schema">("schema");

  return (
    <motion.div
      initial={prefersReduced ? false : { opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.15 }}
      className="rounded-xl bg-[var(--color-surface)] overflow-hidden"
    >
      {/* Tab bar */}
      <div
        className="flex border-b border-[var(--color-border-subtle)]"
        role="tablist"
        aria-label="Data preview tabs"
      >
        {(["schema", "sample"] as const).map((t) => (
          <button
            key={t}
            role="tab"
            aria-selected={tab === t}
            aria-controls={`tab-panel-${t}`}
            onClick={() => setTab(t)}
            className={cn(
              "px-5 py-3.5 text-sm font-medium transition-colors duration-100 border-b-2 -mb-px",
              tab === t
                ? "border-[var(--color-brand-500)] text-[var(--color-fg)]"
                : "border-transparent text-[var(--color-fg-muted)] hover:text-[var(--color-fg)]"
            )}
          >
            {t === "schema" ? "Column schema" : "Sample rows"}
          </button>
        ))}
      </div>

      {/* Schema panel */}
      {tab === "schema" && (
        <div
          id="tab-panel-schema"
          role="tabpanel"
          aria-label="Column schema"
          className="overflow-x-auto"
        >
          <table className="w-full text-xs font-mono" aria-label="Dataset column schema">
            <thead>
              <tr className="border-b border-[var(--color-border-subtle)]">
                <th className="text-left px-5 py-3 text-[var(--color-fg-faint)] font-medium">column</th>
                <th className="text-left px-5 py-3 text-[var(--color-fg-faint)] font-medium">dtype</th>
                <th className="text-right px-5 py-3 text-[var(--color-fg-faint)] font-medium">null %</th>
              </tr>
            </thead>
            <tbody>
              {preview.columns.map((col) => (
                <tr
                  key={col.name}
                  className={cn(
                    "border-b border-[var(--color-border-subtle)] last:border-0",
                    "hover:bg-[var(--color-surface-2)] transition-colors duration-75"
                  )}
                >
                  <td className="px-5 py-2.5 text-[var(--color-fg)]">{col.name}</td>
                  <td className="px-5 py-2.5 text-[var(--color-brand-400)]">{col.dtype}</td>
                  <td
                    className={cn("px-5 py-2.5 text-right tabular-nums", col.null_pct > 5 ? "text-[var(--color-warning)]" : col.null_pct > 0 ? "text-[var(--color-info)]" : "text-[var(--color-ok)]")}
                    aria-label={`${col.null_pct}% null values`}
                  >
                    {col.null_pct.toFixed(1)}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Sample rows panel */}
      {tab === "sample" && (
        <div
          id="tab-panel-sample"
          role="tabpanel"
          aria-label="Sample rows"
          className="overflow-x-auto"
        >
          <table className="w-full text-xs font-mono" aria-label="Sample dataset rows">
            <thead>
              <tr className="border-b border-[var(--color-border-subtle)]">
                {preview.columns.map((col) => (
                  <th
                    key={col.name}
                    className="text-left px-4 py-3 text-[var(--color-fg-faint)] font-medium whitespace-nowrap"
                  >
                    {col.name}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {preview.sample_rows.map((row, i) => (
                <tr
                  key={i}
                  className="border-b border-[var(--color-border-subtle)] last:border-0 hover:bg-[var(--color-surface-2)] transition-colors duration-75"
                >
                  {preview.columns.map((col) => {
                    const val = row[col.name];
                    return (
                      <td
                        key={col.name}
                        className={cn(
                          "px-4 py-2.5 whitespace-nowrap tabular-nums",
                          val == null ? "text-[var(--color-fg-faint)] italic" : "text-[var(--color-fg-muted)]"
                        )}
                      >
                        {val == null ? "null" : String(val)}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </motion.div>
  );
}
