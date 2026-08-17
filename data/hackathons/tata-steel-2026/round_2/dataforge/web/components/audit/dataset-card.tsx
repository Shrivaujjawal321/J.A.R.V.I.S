"use client";

import { useState } from "react";
import { motion, useReducedMotion } from "framer-motion";
import { Download, FileSpreadsheet, AlertCircle, Loader2, Trash2 } from "lucide-react";
import { ScoreRing } from "@/components/ui/score-ring";
import { RankBadge } from "@/components/ui/rank-badge";
import { formatNumber, formatFileSize } from "@/lib/utils";
import { downloadDatasetFile } from "@/lib/api";
import { cn } from "@/lib/utils";
import type { DatasetCard as DatasetCardType } from "@/lib/types";

interface DatasetCardProps {
  dataset: DatasetCardType;
  index: number;
  onDelete?: (id: string) => void;
}

// ── Relevance bar ──────────────────────────────────────────────────────────────
function RelevanceBar({ score }: { score: number | null }) {
  const s = score ?? 0;
  const prefersReduced = useReducedMotion();
  const fillColor =
    s >= 70 ? "var(--color-accent-400)"
    : s >= 40 ? "var(--color-status-warning-fg)"
    : "var(--color-status-critical-fg)";

  return (
    <div className="flex items-center gap-2">
      <span className="label-caps w-20 flex-shrink-0">Relevance</span>
      <div
        className="flex-1 h-1.5 rounded-full overflow-hidden"
        style={{ backgroundColor: "var(--color-bg-elevated)" }}
        role="meter"
        aria-valuenow={s}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={`Relevance score: ${s} out of 100`}
      >
        <motion.div
          className="h-full rounded-full"
          style={{ backgroundColor: fillColor }}
          initial={{ width: "0%" }}
          animate={{ width: `${s}%` }}
          transition={
            prefersReduced
              ? { duration: 0 }
              : { duration: 0.8, ease: [0.16, 1, 0.3, 1], delay: 0.2 }
          }
        />
      </div>
      <span
        className="mono-data text-xs tabular-nums w-8 text-right"
        style={{ color: fillColor }}
      >
        {s}
      </span>
    </div>
  );
}

// ── Tag pill ───────────────────────────────────────────────────────────────────
function TagPill({ label }: { label: string }) {
  return (
    <span
      className="inline-flex items-center px-2 py-0.5 rounded"
      style={{
        backgroundColor: "var(--color-bg-elevated)",
        color: "var(--color-fg-tertiary)",
        fontSize: "var(--text-2xs)",
        fontFamily: "var(--font-mono)",
        letterSpacing: "0.06em",
        textTransform: "uppercase",
        border: "1px solid var(--color-border)",
        minHeight: "24px",
      }}
    >
      {label}
    </span>
  );
}

// ── Skeleton card ──────────────────────────────────────────────────────────────
export function DatasetCardSkeleton({ index }: { index: number }) {
  return (
    <div
      className="flex flex-col gap-3 rounded-xl p-5 border"
      style={{
        backgroundColor: "var(--color-bg-card)",
        borderColor: "var(--color-border)",
        animationDelay: `${index * 0.05}s`,
      }}
      aria-hidden="true"
    >
      <div className="h-4 rounded skeleton" style={{ width: "75%" }} />
      <div className="h-3 rounded skeleton" style={{ width: "50%" }} />
      <div className="h-2 rounded skeleton" />
      <div className="flex gap-1.5">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-5 w-16 rounded skeleton" />
        ))}
      </div>
    </div>
  );
}

// ── Status left-border map ─────────────────────────────────────────────────────
const STATUS_LEFT_BORDER: Record<string, string> = {
  scored:     "3px solid var(--color-status-healthy-fg)",
  processing: "3px solid var(--color-status-warning-fg)",
  rejected:   "3px solid var(--color-status-critical-fg)",
};

// ── Main card component ────────────────────────────────────────────────────────
export function DatasetCardItem({ dataset, index, onDelete }: DatasetCardProps) {
  const prefersReduced = useReducedMotion();
  const [downloadCount, setDownloadCount] = useState(dataset.download_count);
  const [isDownloading, setIsDownloading] = useState(false);

  const status = dataset.status ?? "scored";
  const isRejected   = status === "rejected";
  const isProcessing = status === "processing";
  const isScored     = status === "scored";

  const cardLabel = isRejected
    ? `Dataset: ${dataset.filename} — Not relevant to Tata Steel Hackathon`
    : `Dataset: ${dataset.filename}${dataset.rank ? `, Rank ${dataset.rank}` : ""}, Score ${dataset.composite_score}, Grade ${dataset.grade}`;

  const handleDownload = async () => {
    if (isDownloading || isProcessing) return;
    setIsDownloading(true);
    setDownloadCount((c) => c + 1);
    try {
      await downloadDatasetFile(dataset.audit_id);
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <motion.article
      initial={prefersReduced ? false : { opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ type: "spring", stiffness: 320, damping: 28, delay: 0.04 * index }}
      whileHover={prefersReduced ? {} : { y: -2 }}
      className={cn(
        "group relative flex flex-col gap-3 rounded-xl p-5",
        "border transition-shadow duration-200",
        "hover:shadow-[var(--shadow-glow-accent)]",
        "focus-within:outline-none",
        isRejected && "opacity-75",
        isProcessing && "opacity-85"
      )}
      style={{
        backgroundColor: "var(--color-bg-card)",
        borderColor: "var(--color-border)",
        borderLeft: STATUS_LEFT_BORDER[status],
      }}
      aria-label={cardLabel}
      tabIndex={0}
    >
      {/* Status / rank row */}
      <div className="flex items-center justify-between gap-2">
        {/* Left: rank badge or status badge */}
        {isScored && dataset.rank != null ? (
          <RankBadge rank={dataset.rank} />
        ) : isProcessing ? (
          <div className="status-badge status-badge--warning inline-flex items-center gap-1.5">
            <Loader2 className="w-3 h-3 animate-spin" aria-hidden="true" style={{ animation: "spin 1s linear infinite" }} />
            Analyzing
          </div>
        ) : isRejected ? (
          <div className="status-badge status-badge--critical inline-flex items-center gap-1.5">
            <AlertCircle className="w-3 h-3" aria-hidden="true" />
            Not Relevant
          </div>
        ) : (
          <div />
        )}

        {/* Right: score ring (hidden for rejected/processing) */}
        {isScored && (
          <ScoreRing score={dataset.composite_score} size="sm" showGrade grade={dataset.grade} />
        )}
      </div>

      {/* File name + description */}
      <div className="flex items-start gap-3">
        <div
          className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
          style={{ backgroundColor: "var(--color-bg-elevated)" }}
        >
          <FileSpreadsheet
            className="w-4 h-4"
            style={{
              color: isRejected
                ? "var(--color-status-critical-fg)"
                : "var(--color-fg-tertiary)",
            }}
            aria-hidden="true"
          />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-1.5 min-w-0">
            <p
              className="text-sm font-mono font-medium truncate"
              style={{ color: "var(--color-fg-primary)" }}
            >
              {dataset.filename}
            </p>
            {dataset.is_own && (
              <span
                className="inline-flex items-center px-1.5 py-0.5 rounded flex-shrink-0"
                style={{
                  backgroundColor: "var(--color-accent-tint)",
                  color: "var(--color-accent-400)",
                  border: "1px solid oklch(72% 0.16 213 / 0.30)",
                  fontSize: "10px",
                  fontFamily: "var(--font-mono)",
                }}
                aria-label="Your dataset"
              >
                you
              </span>
            )}
          </div>
          {dataset.description && (
            <p
              className="text-xs mt-0.5 line-clamp-2"
              style={{ color: "var(--color-fg-secondary)" }}
            >
              {dataset.description}
            </p>
          )}
          {isProcessing && !dataset.description && (
            <p className="text-xs mt-0.5" style={{ color: "var(--color-fg-tertiary)" }}>
              Scoring in progress…
            </p>
          )}
        </div>
      </div>

      {/* Tags */}
      {dataset.tags && dataset.tags.length > 0 && (
        <div className="flex flex-wrap gap-1.5" aria-label="Dataset tags">
          {dataset.tags.slice(0, 4).map((tag) => (
            <TagPill key={tag} label={tag} />
          ))}
        </div>
      )}

      {/* Divider */}
      <div className="hud-divider my-0" aria-hidden="true" />

      {/* Stats row */}
      <div
        className="flex items-center gap-3 text-xs mono-data tabular-nums flex-wrap"
        style={{ color: "var(--color-fg-tertiary)" }}
      >
        {dataset.n_rows > 0 && (
          <>
            <span>{formatNumber(dataset.n_rows)} rows</span>
            <span aria-hidden="true">·</span>
          </>
        )}
        {dataset.n_cols > 0 && (
          <>
            <span>{dataset.n_cols} cols</span>
          </>
        )}
        {dataset.file_size_bytes != null && (
          <>
            <span aria-hidden="true">·</span>
            <span>{formatFileSize(dataset.file_size_bytes)}</span>
          </>
        )}
        <span aria-hidden="true">·</span>
        <time dateTime={dataset.created_at}>
          {new Date(dataset.created_at).toLocaleDateString("en-US", {
            month: "short",
            day: "numeric",
          })}
        </time>
      </div>

      {/* Relevance bar */}
      {!isProcessing && (
        <RelevanceBar score={dataset.relevance_score ?? null} />
      )}

      {/* Download CTA + optional delete */}
      <div className="flex items-center gap-2">
        <button
          onClick={handleDownload}
          disabled={isDownloading || isProcessing}
          className={cn(
            "flex items-center justify-between flex-1 px-3.5 py-2.5 rounded-lg text-xs font-medium",
            "transition-all duration-100 focus:outline-none focus-visible:ring-2",
            "focus-visible:ring-[var(--color-accent-400)]",
            isDownloading || isProcessing
              ? "opacity-40 cursor-not-allowed"
              : "bg-[var(--color-surface-2)] hover:bg-[var(--color-surface-3)] text-[var(--color-fg-muted)] hover:text-[var(--color-fg)]"
          )}
          aria-label={`Download ${dataset.filename}`}
          aria-disabled={isDownloading || isProcessing}
        >
          <span className="flex items-center gap-2">
            <Download className="w-3.5 h-3.5" aria-hidden="true" />
            <span>Download</span>
          </span>
          <span
            className="mono-data tabular-nums text-xs"
            style={{ color: "var(--color-fg-faint)" }}
          >
            {formatNumber(downloadCount)} DLs
          </span>
        </button>

        {/* Delete — only visible for owner */}
        {dataset.is_own && onDelete && (
          <button
            onClick={() => onDelete(dataset.audit_id)}
            className={cn(
              "p-2.5 rounded-lg text-xs transition-all duration-100",
              "focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-status-critical-fg)]",
              "bg-[var(--color-surface-2)] hover:bg-[var(--color-status-critical-bg)]"
            )}
            style={{ color: "var(--color-fg-faint)" }}
            aria-label={`Delete ${dataset.filename}`}
          >
            <Trash2 className="w-3.5 h-3.5" aria-hidden="true" />
          </button>
        )}
      </div>
    </motion.article>
  );
}
