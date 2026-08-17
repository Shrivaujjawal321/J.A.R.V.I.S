"use client";

import { useState } from "react";
import { motion, useReducedMotion, AnimatePresence } from "framer-motion";
import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { UploadZone } from "@/components/audit/upload-zone";
import { ScoreRing } from "@/components/ui/score-ring";
import { useAuditStore } from "@/lib/audit-store";
import { runAudit, fetchQuota, fetchDatasets } from "@/lib/api";
import { MOCK_DATASETS } from "@/lib/mock-data";
import { gradeColor, formatNumber } from "@/lib/utils";
import { useAuth } from "@/providers/auth-provider";
import type { AuditFormData } from "@/lib/types";

const HOW_IT_WORKS = [
  {
    step: "01",
    title: "Upload your dataset",
    description: "Drop a CSV, XLSX, or JSON file — any industrial, time-series, or tabular data from steel manufacturing.",
  },
  {
    step: "02",
    title: "E.D.I.T.H runs 10 quality checks",
    description:
      "Relevance scoring, completeness, class balance, label quality, leakage, schema validity, outliers — and more.",
  },
  {
    step: "03",
    title: "Get a score + coaching plan",
    description:
      "A 0-100 composite score, a radar breakdown, and a prioritized list of exactly what to fix.",
  },
];

export default function HomePage() {
  const prefersReduced = useReducedMotion();
  const router = useRouter();
  const { current: currentResult, setCurrent } = useAuditStore();
  const { user } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);

  const useMock = process.env.NEXT_PUBLIC_USE_MOCK === "1";

  // Only fetch quota when signed in — avoids an unauthenticated /api/me/quota call
  const { data: quota } = useQuery({
    queryKey: ["quota", user?.id],
    queryFn: fetchQuota,
    staleTime: 30_000,
    enabled: user != null,
    retry: 1,
  });

  // Live board data for "Top datasets" preview
  const { data: boardDatasets } = useQuery({
    queryKey: ["datasets-board-preview"],
    queryFn: fetchDatasets,
    staleTime: 60_000,
    enabled: !useMock,
  });

  const handleSubmit = async (data: AuditFormData) => {
    setIsLoading(true);
    setError(null);
    setStatusMessage(null);
    try {
      const result = await runAudit(data, setStatusMessage);
      setCurrent(result, currentResult);
      router.push("/result");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong. Please try again.");
    } finally {
      setIsLoading(false);
      setStatusMessage(null);
    }
  };

  const trendingDatasets = (
    useMock ? MOCK_DATASETS : (boardDatasets ?? [])
  ).filter(d => (d.status ?? "scored") === "scored").slice(0, 4);

  return (
    <div className="min-h-[calc(100dvh-3.5rem)] flex flex-col">
      {/* Hero section */}
      <section
        className="flex-1 flex flex-col items-center justify-center px-6 py-16 sm:py-24"
        aria-labelledby="hero-heading"
      >
        <div className="w-full max-w-2xl mx-auto flex flex-col items-center gap-8">
          {/* Heading */}
          <motion.div
            initial={prefersReduced ? false : { opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
            className="flex flex-col items-center gap-3 text-center"
          >
            <h1
              id="hero-heading"
              className="text-4xl sm:text-5xl font-bold text-[var(--color-fg)] tracking-tight leading-tight"
            >
              Know if your data is
              <br />
              <span style={{ color: "var(--color-accent-400)" }}>ready to train on</span>
            </h1>
            <p className="text-lg text-[var(--color-fg-muted)] max-w-md leading-relaxed">
              E.D.I.T.H grades your data — and shows you exactly how to make it better.
            </p>
          </motion.div>

          {/* Upload zone */}
          <motion.div
            initial={prefersReduced ? false : { opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1], delay: 0.1 }}
            className="w-full"
          >
            <UploadZone onSubmit={handleSubmit} isLoading={isLoading} quota={quota} />
          </motion.div>

          {/* Processing status message (shown during upload → poll → fetch) */}
          <AnimatePresence>
            {statusMessage && (
              <motion.p
                initial={{ opacity: 0, y: -4 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                className="flex items-center justify-center gap-2 text-sm w-full text-center"
                style={{ color: "var(--color-fg-muted)" }}
                aria-live="polite"
                aria-atomic="true"
              >
                <span
                  className="w-3.5 h-3.5 border-2 border-current/30 border-t-current rounded-full animate-spin flex-shrink-0"
                  aria-hidden="true"
                />
                {statusMessage}
              </motion.p>
            )}
          </AnimatePresence>

          {/* Error message */}
          <AnimatePresence>
            {error && (
              <motion.p
                initial={{ opacity: 0, y: -4 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                className="text-sm px-4 py-3 rounded-lg w-full text-center"
                style={{
                  color: "var(--color-status-critical-fg)",
                  backgroundColor: "var(--color-status-critical-bg)",
                  border: "1px solid var(--color-status-critical-border)",
                }}
                role="alert"
                aria-live="polite"
              >
                {error}
              </motion.p>
            )}
          </AnimatePresence>
        </div>
      </section>

      {/* How it works */}
      <section
        className="border-t border-[var(--color-border-subtle)] py-16 px-6"
        aria-labelledby="how-it-works-heading"
      >
        <div className="max-w-4xl mx-auto flex flex-col gap-8">
          <h2
            id="how-it-works-heading"
            className="text-xs font-mono font-medium text-[var(--color-fg-faint)] uppercase tracking-widest text-center"
          >
            How it works
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-8">
            {HOW_IT_WORKS.map((item, i) => (
              <motion.div
                key={item.step}
                initial={prefersReduced ? false : { opacity: 0, y: 12 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-50px" }}
                transition={{ duration: 0.4, delay: 0.1 * i, ease: [0.16, 1, 0.3, 1] }}
                className="flex flex-col gap-3"
              >
                <span
                  className="font-mono text-xs font-bold tracking-wider"
                  style={{ color: "var(--color-accent-600)" }}
                >
                  {item.step}
                </span>
                <h3 className="text-sm font-semibold text-[var(--color-fg)]">{item.title}</h3>
                <p className="text-xs text-[var(--color-fg-muted)] leading-relaxed">{item.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Trending datasets preview */}
      <section
        className="border-t border-[var(--color-border-subtle)] py-12 px-6"
        aria-labelledby="trending-heading"
      >
        <div className="max-w-4xl mx-auto flex flex-col gap-6">
          <div className="flex items-center justify-between">
            <h2
              id="trending-heading"
              className="text-sm font-medium text-[var(--color-fg-muted)]"
            >
              Top datasets
            </h2>
            <a
              href="/datasets"
              className="text-xs transition-colors"
              style={{ color: "var(--color-accent-400)" }}
            >
              View all →
            </a>
          </div>
          <div
            className="flex gap-4 overflow-x-auto pb-2 -mx-6 px-6"
            role="list"
            aria-label="Top datasets"
          >
            {trendingDatasets.map((ds, i) => (
              <motion.div
                key={ds.dataset_id}
                initial={prefersReduced ? false : { opacity: 0, x: 12 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.3, delay: 0.05 * i }}
                className="flex-shrink-0 w-56 rounded-xl p-4 flex flex-col gap-3 border border-transparent hover:border-[var(--color-border-subtle)] transition-colors cursor-default"
                style={{ backgroundColor: "var(--color-surface)" }}
                role="listitem"
              >
                <div className="flex items-center justify-between">
                  <span
                    className="text-xs font-mono font-bold"
                    style={{ color: gradeColor(ds.grade) }}
                    aria-label={`Grade: ${ds.grade}`}
                  >
                    {ds.grade}
                  </span>
                  <ScoreRing score={ds.composite_score} size="sm" />
                </div>
                <p className="text-xs font-mono text-[var(--color-fg-muted)] truncate">{ds.filename}</p>
                <p className="text-xs text-[var(--color-fg-faint)] font-mono tabular-nums">
                  {formatNumber(ds.n_rows)} rows &middot; {ds.download_count} DLs
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
