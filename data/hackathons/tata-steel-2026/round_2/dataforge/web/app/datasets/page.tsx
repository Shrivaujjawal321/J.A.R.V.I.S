"use client";

import { useState, useMemo, useEffect, useCallback } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { motion, useReducedMotion, AnimatePresence } from "framer-motion";
import { Search, Grid, List, Upload, AlertCircle, Trash2 } from "lucide-react";
import Link from "next/link";
import { DatasetCardItem, DatasetCardSkeleton } from "@/components/audit/dataset-card";
import { RankBadge } from "@/components/ui/rank-badge";
import { ScoreRing } from "@/components/ui/score-ring";
import { fetchDatasets, deleteDataset } from "@/lib/api";
import { gradeColor, formatNumber, formatFileSize } from "@/lib/utils";
import { cn } from "@/lib/utils";
import { useAuth } from "@/providers/auth-provider";
import type { DatasetCard, DatasetStatus } from "@/lib/types";

type SortKey = "rank" | "score" | "date" | "size";
type StatusFilter = "all" | DatasetStatus;

// ── Leaderboard table row ──────────────────────────────────────────────────────
function LeaderboardRow({
  dataset,
  rank,
  index,
  onDelete,
}: {
  dataset: DatasetCard;
  rank: number;
  index: number;
  onDelete?: (id: string) => void;
}) {
  const prefersReduced = useReducedMotion();

  return (
    <motion.tr
      initial={prefersReduced ? false : { opacity: 0, x: -8 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.3, delay: 0.04 * index }}
      className="border-b border-[var(--color-border-subtle)] last:border-0 hover:bg-[var(--color-surface-2)] transition-colors duration-75 group"
    >
      <td className="px-4 py-3.5 w-12">
        {rank <= 3 ? (
          <RankBadge rank={rank} size="sm" />
        ) : (
          <span
            className="font-mono text-sm tabular-nums"
            style={{ color: "var(--color-fg-tertiary)" }}
          >
            #{rank}
          </span>
        )}
      </td>
      <td className="px-4 py-3.5 max-w-xs">
        <div className="flex items-center gap-2">
          <span
            className="font-mono text-sm truncate"
            style={{ color: "var(--color-fg-primary)" }}
          >
            {dataset.filename}
          </span>
          {dataset.is_own && (
            <span
              className="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-mono flex-shrink-0"
              style={{
                backgroundColor: "var(--color-accent-tint)",
                color: "var(--color-accent-400)",
                border: "1px solid oklch(72% 0.16 213 / 0.30)",
                fontSize: "10px",
              }}
              aria-label="Your dataset"
            >
              you
            </span>
          )}
        </div>
        {dataset.description && (
          <span
            className="text-xs block truncate mt-0.5"
            style={{ color: "var(--color-fg-tertiary)" }}
          >
            {dataset.description}
          </span>
        )}
        {dataset.is_own && onDelete && (
          <button
            onClick={() => onDelete(dataset.audit_id)}
            className="mt-1 flex items-center gap-1 text-xs transition-colors duration-100 focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-status-critical-fg)] rounded"
            style={{ color: "var(--color-fg-faint)" }}
            aria-label={`Delete ${dataset.filename}`}
          >
            <Trash2 className="w-3 h-3" aria-hidden="true" />
            <span className="hidden group-hover:inline">Delete</span>
          </button>
        )}
      </td>
      <td className="px-4 py-3.5 hidden sm:table-cell">
        {/* Relevance mini-bar */}
        <div className="flex items-center gap-2 w-28">
          <div
            className="flex-1 h-1 rounded-full overflow-hidden"
            style={{ backgroundColor: "var(--color-bg-elevated)" }}
            aria-label={`Relevance: ${dataset.relevance_score ?? 0}`}
          >
            <div
              className="h-full rounded-full transition-all duration-700"
              style={{
                width: `${dataset.relevance_score ?? 0}%`,
                backgroundColor:
                  (dataset.relevance_score ?? 0) >= 70
                    ? "var(--color-accent-400)"
                    : (dataset.relevance_score ?? 0) >= 40
                    ? "var(--color-status-warning-fg)"
                    : "var(--color-status-critical-fg)",
              }}
            />
          </div>
          <span
            className="font-mono text-xs tabular-nums w-6 text-right"
            style={{ color: "var(--color-fg-tertiary)" }}
          >
            {dataset.relevance_score ?? 0}
          </span>
        </div>
      </td>
      <td className="px-4 py-3.5">
        <div className="flex items-center gap-2">
          <ScoreRing score={dataset.composite_score} size="sm" />
          <span
            className="font-mono text-sm tabular-nums"
            style={{ color: "var(--color-fg-secondary)" }}
          >
            {dataset.composite_score}
          </span>
        </div>
      </td>
      <td className="px-4 py-3.5 hidden md:table-cell">
        <span
          className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-mono font-bold"
          style={{
            color: gradeColor(dataset.grade),
            backgroundColor: `${gradeColor(dataset.grade)}15`,
          }}
          aria-label={`Grade: ${dataset.grade}`}
        >
          {dataset.grade}
        </span>
      </td>
      <td className="px-4 py-3.5 hidden lg:table-cell font-mono tabular-nums text-sm" style={{ color: "var(--color-fg-tertiary)" }}>
        {formatNumber(dataset.n_rows)}
      </td>
      <td className="px-4 py-3.5 hidden lg:table-cell font-mono tabular-nums text-sm" style={{ color: "var(--color-fg-tertiary)" }}>
        {dataset.file_size_bytes != null ? formatFileSize(dataset.file_size_bytes) : "—"}
      </td>
      <td className="px-4 py-3.5 hidden sm:table-cell text-xs" style={{ color: "var(--color-fg-tertiary)" }}>
        <time dateTime={dataset.created_at}>
          {new Date(dataset.created_at).toLocaleDateString("en-US", { month: "short", day: "numeric" })}
        </time>
      </td>
    </motion.tr>
  );
}

// ── Top-3 podium card ──────────────────────────────────────────────────────────
function PodiumCard({
  dataset,
  rank,
  isPrimary,
}: {
  dataset: DatasetCard;
  rank: number;
  isPrimary: boolean;
}) {
  const prefersReduced = useReducedMotion();

  return (
    <motion.div
      initial={prefersReduced ? false : { opacity: 0, y: isPrimary ? -12 : 0, scale: isPrimary ? 0.96 : 0.98 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ type: "spring", stiffness: 280, damping: 28, delay: isPrimary ? 0.1 : rank === 2 ? 0 : 0.2 }}
      className={cn(
        "flex flex-col gap-3 rounded-xl p-5 border flex-1",
        "transition-shadow duration-200",
        isPrimary && "shadow-[var(--shadow-glow-accent)]"
      )}
      style={{
        backgroundColor: isPrimary ? "var(--color-bg-card)" : "var(--color-bg-elevated)",
        borderColor: isPrimary ? "var(--color-glass-border-accent)" : "var(--color-border)",
        borderLeft: rank === 1
          ? "3px solid oklch(72% 0.16 85)"
          : rank === 2
          ? "3px solid oklch(72% 0.08 250)"
          : "3px solid oklch(60% 0.14 40)",
        transform: isPrimary ? "translateY(-8px)" : "none",
      }}
    >
      <div className="flex items-start justify-between gap-2">
        <RankBadge rank={rank} size={isPrimary ? "md" : "sm"} />
        <ScoreRing score={dataset.composite_score} size="sm" showGrade grade={dataset.grade} />
      </div>
      <p
        className="text-sm font-mono font-medium truncate"
        style={{ color: "var(--color-fg-primary)" }}
      >
        {dataset.filename}
      </p>
      <div
        className="flex items-center gap-2 text-xs mono-data tabular-nums"
        style={{ color: "var(--color-fg-tertiary)" }}
      >
        <span>{formatNumber(dataset.n_rows)} rows</span>
        <span aria-hidden="true">·</span>
        <span>{dataset.n_cols} cols</span>
      </div>
    </motion.div>
  );
}

// ── Empty state ────────────────────────────────────────────────────────────────
function EmptyState({
  type,
  query,
  onClear,
}: {
  type: "no-datasets" | "no-results" | "no-filter";
  query?: string;
  onClear?: () => void;
}) {
  if (type === "no-datasets") {
    return (
      <div className="flex flex-col items-center gap-4 py-16 text-center">
        <div
          className="w-12 h-12 rounded-xl flex items-center justify-center"
          style={{ backgroundColor: "var(--color-bg-elevated)" }}
        >
          <Upload className="w-6 h-6" style={{ color: "var(--color-fg-tertiary)" }} aria-hidden="true" />
        </div>
        <div className="flex flex-col gap-1">
          <p className="text-sm font-medium" style={{ color: "var(--color-fg-primary)" }}>
            No datasets yet
          </p>
          <p className="text-xs" style={{ color: "var(--color-fg-tertiary)" }}>
            Be the first to upload one for the hackathon.
          </p>
        </div>
        <Link href="/" className="btn-primary text-sm">
          Upload dataset
        </Link>
      </div>
    );
  }

  if (type === "no-results") {
    return (
      <div className="flex flex-col items-center gap-4 py-16 text-center">
        <div
          className="w-12 h-12 rounded-xl flex items-center justify-center"
          style={{ backgroundColor: "var(--color-bg-elevated)" }}
        >
          <Search className="w-6 h-6" style={{ color: "var(--color-fg-tertiary)" }} aria-hidden="true" />
        </div>
        <div className="flex flex-col gap-1">
          <p className="text-sm font-medium" style={{ color: "var(--color-fg-primary)" }}>
            No datasets match &ldquo;{query}&rdquo;
          </p>
          <p className="text-xs" style={{ color: "var(--color-fg-tertiary)" }}>
            Try different keywords or clear the search.
          </p>
        </div>
        <button onClick={onClear} className="btn-ghost text-sm">
          Clear search
        </button>
      </div>
    );
  }

  // no-filter (filtered but empty)
  return (
    <div className="flex flex-col items-center gap-2 py-16 text-center">
      <p className="text-sm" style={{ color: "var(--color-fg-tertiary)" }}>
        No datasets match this filter.
      </p>
    </div>
  );
}

// ── Datasets skeleton ──────────────────────────────────────────────────────────
function DatasetsSkeleton() {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      {Array.from({ length: 6 }).map((_, i) => (
        <DatasetCardSkeleton key={i} index={i} />
      ))}
    </div>
  );
}

// ── Main page ──────────────────────────────────────────────────────────────────
export default function DatasetsPage() {
  const prefersReduced = useReducedMotion();
  const { user } = useAuth();
  const [query, setQuery] = useState("");
  const [debouncedQuery, setDebouncedQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<StatusFilter>("all");
  const [sort, setSort] = useState<SortKey>("rank");
  const [view, setView] = useState<"grid" | "table">("grid");

  // Debounce search 200ms
  useEffect(() => {
    const t = setTimeout(() => setDebouncedQuery(query), 200);
    return () => clearTimeout(t);
  }, [query]);

  const queryClient = useQueryClient();

  const { data: datasets, isLoading, error } = useQuery({
    queryKey: ["datasets", user?.id],
    queryFn: fetchDatasets,
  });

  const handleDelete = useCallback(async (id: string) => {
    try {
      await deleteDataset(id);
      // Invalidate the datasets cache so the list refreshes
      queryClient.invalidateQueries({ queryKey: ["datasets"] });
      queryClient.invalidateQueries({ queryKey: ["quota"] });
    } catch {
      // Non-blocking — dataset will disappear on next refresh
    }
  }, [queryClient]);

  // Top-3 podium: scored datasets, sorted by rank
  const podiumDatasets = useMemo(() => {
    if (!datasets) return [];
    return [...datasets]
      .filter(d => (d.status ?? "scored") === "scored")
      .sort((a, b) => (a.rank ?? Infinity) - (b.rank ?? Infinity))
      .slice(0, 3);
  }, [datasets]);

  // Filtered + sorted list
  const filtered = useMemo(() => {
    if (!datasets) return [];
    let result = [...datasets];

    // Status filter
    if (statusFilter !== "all") {
      result = result.filter(d => (d.status ?? "scored") === statusFilter);
    }

    // Search filter
    if (debouncedQuery) {
      const q = debouncedQuery.toLowerCase();
      result = result.filter(d =>
        d.filename.toLowerCase().includes(q) ||
        (d.description?.toLowerCase().includes(q) ?? false) ||
        (d.tags?.some(t => t.toLowerCase().includes(q)) ?? false)
      );
    }

    // Sort
    result.sort((a, b) => {
      switch (sort) {
        case "rank":
          if (a.rank == null && b.rank == null) return 0;
          if (a.rank == null) return 1;
          if (b.rank == null) return -1;
          return a.rank - b.rank;
        case "score":
          return b.composite_score - a.composite_score;
        case "date":
          return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
        case "size":
          return (b.file_size_bytes ?? 0) - (a.file_size_bytes ?? 0);
        default:
          return 0;
      }
    });

    return result;
  }, [datasets, statusFilter, debouncedQuery, sort]);

  const clearSearch = useCallback(() => setQuery(""), []);

  const showPodium = podiumDatasets.length >= 3 && statusFilter === "all" && !debouncedQuery;

  const emptyType = !datasets || datasets.length === 0
    ? "no-datasets"
    : debouncedQuery && filtered.length === 0
    ? "no-results"
    : !debouncedQuery && filtered.length === 0
    ? "no-filter"
    : null;

  return (
    <div className="max-w-5xl mx-auto px-6 py-10 flex flex-col gap-8">
      {/* Page header */}
      <motion.div
        initial={prefersReduced ? false : { opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
        className="flex flex-col sm:flex-row sm:items-end gap-4 justify-between"
      >
        <div className="flex flex-col gap-1">
          <h1 className="text-2xl font-bold" style={{ color: "var(--color-fg-primary)" }}>
            Datasets
          </h1>
          <p className="text-sm" style={{ color: "var(--color-fg-secondary)" }}>
            Graded and ranked by quality score + Tata Steel relevance
          </p>
        </div>
        <Link href="/" className="btn-primary self-start sm:self-auto">
          <Upload className="w-3.5 h-3.5" aria-hidden="true" />
          Upload dataset
        </Link>
      </motion.div>

      {/* Error */}
      {error && (
        <div
          className="flex items-center gap-2 text-sm px-4 py-3 rounded-lg border"
          style={{
            color: "var(--color-status-critical-fg)",
            backgroundColor: "var(--color-status-critical-bg)",
            borderColor: "var(--color-status-critical-border)",
          }}
          role="alert"
        >
          <AlertCircle className="w-4 h-4 flex-shrink-0" aria-hidden="true" />
          Could not load datasets. Check API connection.
        </div>
      )}

      {/* Search + filter row */}
      <div className="flex flex-col sm:flex-row gap-3" role="search">
        {/* Search input */}
        <div className="relative flex-1">
          <Search
            className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 pointer-events-none"
            style={{ color: "var(--color-fg-tertiary)" }}
            aria-hidden="true"
          />
          <input
            type="search"
            placeholder="Search datasets…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2.5 rounded-lg text-sm font-sans transition-colors duration-150"
            style={{
              backgroundColor: "var(--color-bg-card)",
              border: "1px solid var(--color-border)",
              color: "var(--color-fg-primary)",
            }}
            aria-label="Search datasets by name, description, or tag"
          />
        </div>

        {/* Status filter pills */}
        <div className="flex gap-1.5 flex-wrap" role="group" aria-label="Filter by status">
          {(["all", "scored", "processing", "rejected"] as const).map((s) => (
            <button
              key={s}
              onClick={() => setStatusFilter(s)}
              className={cn(
                "px-3.5 py-2 rounded-lg text-xs font-medium capitalize transition-colors duration-100",
                "focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-accent-400)]",
                "min-h-[36px]"
              )}
              style={
                statusFilter === s
                  ? {
                      backgroundColor: "var(--color-accent-400)",
                      color: "var(--color-fg-on-accent)",
                    }
                  : {
                      backgroundColor: "var(--color-bg-elevated)",
                      color: "var(--color-fg-secondary)",
                      border: "1px solid var(--color-border)",
                    }
              }
              aria-pressed={statusFilter === s}
            >
              {s === "all" ? "All" : s.charAt(0).toUpperCase() + s.slice(1)}
            </button>
          ))}
        </div>

        {/* Sort select */}
        <select
          value={sort}
          onChange={(e) => setSort(e.target.value as SortKey)}
          className="px-3 py-2.5 rounded-lg text-xs font-mono transition-colors focus:outline-none"
          style={{
            backgroundColor: "var(--color-bg-card)",
            border: "1px solid var(--color-border)",
            color: "var(--color-fg-secondary)",
            minHeight: "40px",
          }}
          aria-label="Sort datasets by"
        >
          <option value="rank">Sort: Rank</option>
          <option value="score">Sort: Score</option>
          <option value="date">Sort: Date</option>
          <option value="size">Sort: Size</option>
        </select>
      </div>

      {/* Top-3 Podium */}
      <AnimatePresence>
        {showPodium && !isLoading && (
          <motion.section
            initial={prefersReduced ? false : { opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
            aria-labelledby="podium-heading"
          >
            <h2
              id="podium-heading"
              className="text-xs font-mono font-medium uppercase tracking-widest mb-4"
              style={{ color: "var(--color-fg-tertiary)" }}
            >
              Top ranked
            </h2>
            <div className="flex gap-4 items-end">
              {/* #2 left, #1 center, #3 right */}
              {podiumDatasets[1] && (
                <PodiumCard dataset={podiumDatasets[1]} rank={2} isPrimary={false} />
              )}
              {podiumDatasets[0] && (
                <PodiumCard dataset={podiumDatasets[0]} rank={1} isPrimary={true} />
              )}
              {podiumDatasets[2] && (
                <PodiumCard dataset={podiumDatasets[2]} rank={3} isPrimary={false} />
              )}
            </div>
          </motion.section>
        )}
      </AnimatePresence>

      {/* All datasets section */}
      <section aria-labelledby="all-datasets-heading">
        <div className="flex items-center justify-between mb-4">
          <h2
            id="all-datasets-heading"
            className="text-xs font-mono font-medium uppercase tracking-widest"
            style={{ color: "var(--color-fg-tertiary)" }}
          >
            All datasets
            {datasets && (
              <span className="ml-2 font-normal normal-case" style={{ color: "var(--color-fg-faint)" }}>
                {filtered.length}
              </span>
            )}
          </h2>
          {/* Grid/table toggle */}
          <div className="flex gap-1" role="group" aria-label="Switch view">
            {([
              { v: "grid" as const, Icon: Grid, label: "Grid view" },
              { v: "table" as const, Icon: List, label: "Table view" },
            ]).map(({ v, Icon, label }) => (
              <button
                key={v}
                onClick={() => setView(v)}
                className={cn(
                  "p-2 rounded-lg transition-colors duration-100",
                  "focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-accent-400)]"
                )}
                style={
                  view === v
                    ? { backgroundColor: "var(--color-bg-elevated)", color: "var(--color-fg-primary)" }
                    : { color: "var(--color-fg-tertiary)" }
                }
                aria-pressed={view === v}
                aria-label={label}
              >
                <Icon className="w-4 h-4" aria-hidden="true" />
              </button>
            ))}
          </div>
        </div>

        {isLoading ? (
          <DatasetsSkeleton />
        ) : emptyType ? (
          <EmptyState type={emptyType} query={debouncedQuery} onClear={clearSearch} />
        ) : view === "grid" ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {filtered.map((ds, i) => (
              <DatasetCardItem
                key={ds.audit_id}
                dataset={ds}
                index={i}
                onDelete={user ? handleDelete : undefined}
              />
            ))}
          </div>
        ) : (
          /* Table view */
          <div
            className="rounded-xl overflow-hidden"
            style={{ backgroundColor: "var(--color-surface)" }}
          >
            <div className="overflow-x-auto">
              <table className="w-full" aria-label="Dataset quality leaderboard">
                <thead>
                  <tr className="border-b" style={{ borderColor: "var(--color-border-subtle)" }}>
                    {["#", "Name", "Relevance", "Score", "Grade", "Rows", "Size", "Uploaded"].map((col) => (
                      <th
                        key={col}
                        className={cn(
                          "text-left px-4 py-3.5 text-xs font-mono font-medium uppercase tracking-wide",
                          col === "Grade" && "hidden md:table-cell",
                          (col === "Rows" || col === "Size") && "hidden lg:table-cell",
                          (col === "Relevance" || col === "Uploaded") && "hidden sm:table-cell",
                        )}
                        scope="col"
                        style={{ color: "var(--color-fg-tertiary)" }}
                      >
                        {col}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {filtered.map((ds, i) => (
                    <LeaderboardRow
                      key={ds.audit_id}
                      dataset={ds}
                      rank={ds.rank ?? (i + 1)}
                      index={i}
                      onDelete={user ? handleDelete : undefined}
                    />
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </section>
    </div>
  );
}
