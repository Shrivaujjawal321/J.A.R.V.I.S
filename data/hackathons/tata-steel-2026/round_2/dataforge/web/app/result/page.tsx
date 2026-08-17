"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { motion, useReducedMotion } from "framer-motion";
import { ArrowLeft, RefreshCw } from "lucide-react";
import Link from "next/link";
import { useAuditStore } from "@/lib/audit-store";
import { ScoreHero } from "@/components/audit/score-hero";
import { SubScores } from "@/components/audit/sub-scores";
import { EdithReview } from "@/components/audit/edith-review";
import { ImprovementCards } from "@/components/audit/improvement-cards";
import { DataPreview } from "@/components/audit/data-preview";
import { RejectedBanner } from "@/components/audit/rejected-banner";
import { RankBadge } from "@/components/ui/rank-badge";
import { Skeleton } from "@/components/ui/skeleton";
import { MOCK_AUDIT_RESULT } from "@/lib/mock-data";

function ResultSkeleton() {
  return (
    <div className="max-w-4xl mx-auto px-6 py-12 flex flex-col gap-8">
      <Skeleton className="h-56 w-full" />
      <div className="grid grid-cols-2 gap-4">
        <Skeleton className="h-72" />
        <Skeleton className="h-72" />
      </div>
      <Skeleton className="h-40" />
      <div className="grid grid-cols-2 gap-4">
        <Skeleton className="h-48" />
        <Skeleton className="h-48" />
      </div>
    </div>
  );
}

// ── Relevance accepted badge (inline, above score hero) ────────────────────────
function RelevanceAcceptedBadge({
  score,
  rank,
}: {
  score: number | null | undefined;
  rank: number | null | undefined;
}) {
  return (
    <div className="flex items-center gap-3 flex-wrap">
      <div className="status-badge status-badge--healthy inline-flex items-center gap-2">
        <span className="status-dot status-dot--healthy" aria-hidden="true" />
        Accepted — Relevant to Tata Steel
      </div>
      {rank != null && <RankBadge rank={rank} size="md" />}
      {score != null && (
        <span
          className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-mono border"
          style={{
            color: "var(--color-accent-400)",
            backgroundColor: "var(--color-accent-tint)",
            borderColor: "oklch(72% 0.16 213 / 0.30)",
          }}
        >
          Relevance {score}/100
        </span>
      )}
    </div>
  );
}

export default function ResultPage() {
  const prefersReduced = useReducedMotion();
  const router = useRouter();
  const { current, previous, hydrated } = useAuditStore();

  const useMock = process.env.NEXT_PUBLIC_USE_MOCK === "1";
  const result = current ?? (useMock ? MOCK_AUDIT_RESULT : null);

  // Only redirect once the store has finished hydrating from localStorage.
  // Without this guard the redirect fires before localStorage is read, causing
  // a false-positive redirect on direct /result navigation with a stored result.
  useEffect(() => {
    if (hydrated && !result && !useMock) {
      router.replace("/");
    }
  }, [hydrated, result, useMock, router]);

  if (!result) return <ResultSkeleton />;

  const status = result.status ?? "scored";
  const isRejected = status === "rejected";
  const hasComparison = previous != null && previous.dataset_id === result.dataset_id;

  return (
    <div className="max-w-4xl mx-auto px-6 py-10 flex flex-col gap-10">
      {/* Back / improve buttons */}
      <div className="flex items-center justify-between">
        <Link
          href="/"
          className="flex items-center gap-2 text-sm text-[var(--color-fg-muted)] hover:text-[var(--color-fg)] transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-accent-400)] rounded"
          aria-label="Go back to upload"
        >
          <ArrowLeft className="w-4 h-4" aria-hidden="true" />
          Back to upload
        </Link>

        {!isRejected && (
          <Link
            href="/"
            className="flex items-center gap-2 text-sm font-medium px-4 py-2 rounded-lg bg-[var(--color-surface)] hover:bg-[var(--color-surface-2)] text-[var(--color-fg)] transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-accent-400)]"
            aria-label="Improve your data and re-upload"
          >
            <RefreshCw className="w-3.5 h-3.5" aria-hidden="true" />
            Improve &amp; re-upload
          </Link>
        )}
      </div>

      {/* Conditional rendering: rejected vs scored */}
      {isRejected ? (
        <>
          <RejectedBanner
            filename={result.filename}
            reason={result.rejection_reason}
          />
          {/* Still show data preview so user can see what was in their file */}
          {(result.preview?.columns?.length ?? 0) > 0 && (
            <section aria-labelledby="preview-heading">
              <h2
                id="preview-heading"
                className="text-xs font-mono font-medium text-[var(--color-fg-faint)] uppercase tracking-widest mb-4"
              >
                Data preview
              </h2>
              <DataPreview preview={result.preview} />
            </section>
          )}
        </>
      ) : (
        <>
          {/* Relevance badge */}
          <motion.div
            initial={prefersReduced ? false : { opacity: 0, y: -4 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
          >
            <RelevanceAcceptedBadge
              score={result.relevance_score}
              rank={result.rank}
            />
          </motion.div>

          {/* Score hero */}
          <motion.section
            initial={prefersReduced ? false : { opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
            aria-labelledby="result-heading"
            className="rounded-2xl bg-[var(--color-surface)] p-8"
          >
            <h1 id="result-heading" className="sr-only">
              Audit result for {result.filename}
            </h1>
            {hasComparison && (
              <div className="mb-5 flex items-center gap-2">
                <span
                  className="inline-flex items-center gap-1.5 text-xs font-medium px-3 py-1 rounded-full"
                  style={{
                    backgroundColor: "var(--color-accent-tint)",
                    color: "var(--color-accent-400)",
                    border: "1px solid oklch(55% 0.19 250 / 0.2)",
                  }}
                >
                  <span
                    className="w-1.5 h-1.5 rounded-full"
                    style={{ backgroundColor: "var(--color-accent-400)" }}
                    aria-hidden="true"
                  />
                  Comparing with previous version
                </span>
              </div>
            )}
            <ScoreHero result={result} previousResult={hasComparison ? previous : null} />
          </motion.section>

          {/* Sub-scores */}
          <section aria-labelledby="sub-scores-heading">
            <h2
              id="sub-scores-heading"
              className="text-xs font-mono font-medium text-[var(--color-fg-faint)] uppercase tracking-widest mb-4"
            >
              Quality dimensions
            </h2>
            <SubScores result={result} previousResult={hasComparison ? previous : null} />
          </section>

          {/* EDITH review */}
          <section aria-labelledby="review-heading">
            <h2
              id="review-heading"
              className="text-xs font-mono font-medium text-[var(--color-fg-faint)] uppercase tracking-widest mb-4"
            >
              E.D.I.T.H analysis
            </h2>
            <EdithReview review={result.review} filename={result.filename} />
          </section>

          {/* Improvement coaching */}
          {(result.improvements?.length ?? 0) > 0 && (
            <section aria-labelledby="improvements-heading">
              <div id="improvements-heading">
                <ImprovementCards improvements={result.improvements} />
              </div>
            </section>
          )}

          {/* Data preview */}
          {(result.preview?.columns?.length ?? 0) > 0 && (
            <section aria-labelledby="preview-heading">
              <h2
                id="preview-heading"
                className="text-xs font-mono font-medium text-[var(--color-fg-faint)] uppercase tracking-widest mb-4"
              >
                Data preview
              </h2>
              <DataPreview preview={result.preview} />
            </section>
          )}

          {/* Bottom CTA */}
          <div className="flex justify-center pb-8">
            <Link
              href="/"
              className="flex items-center gap-2 px-6 py-3 rounded-xl font-semibold text-sm transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2"
              style={{
                backgroundColor: "var(--color-accent-400)",
                color: "var(--color-fg-on-accent)",
              }}
            >
              <RefreshCw className="w-4 h-4" aria-hidden="true" />
              Upload improved dataset
            </Link>
          </div>
        </>
      )}
    </div>
  );
}
