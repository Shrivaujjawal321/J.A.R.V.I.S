import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";
import type { Severity, Priority, Effort } from "./types";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// ─── Score → color (OKLCH) ────────────────────────────────────────────────────
export function scoreColor(score: number): string {
  if (score >= 80) return "var(--color-score-high)";
  if (score >= 55) return "var(--color-score-mid)";
  return "var(--color-score-low)";
}

// ─── Score → ring stroke color ────────────────────────────────────────────────
export function scoreRingColor(score: number): string {
  if (score >= 80) return "oklch(72% 0.15 155)";
  if (score >= 55) return "oklch(72% 0.16 85)";
  return "oklch(55% 0.18 25)";
}

// ─── Grade → label & badge color ─────────────────────────────────────────────
export function gradeColor(grade: string): string {
  const map: Record<string, string> = {
    "A+": "oklch(72% 0.15 155)",
    A: "oklch(68% 0.14 155)",
    "B+": "oklch(72% 0.16 85)",
    B: "oklch(68% 0.14 85)",
    "C+": "oklch(64% 0.15 55)",
    C: "oklch(60% 0.14 55)",
    D: "oklch(58% 0.18 25)",
    F: "oklch(55% 0.2 25)",
  };
  return map[grade] ?? "oklch(60% 0.01 250)";
}

// ─── Severity → color token ───────────────────────────────────────────────────
export function severityColor(severity: Severity): string {
  const map: Record<Severity, string> = {
    ok: "var(--color-ok)",
    info: "var(--color-info)",
    warning: "var(--color-warning)",
    critical: "var(--color-critical)",
  };
  return map[severity];
}

// ─── Priority → color ─────────────────────────────────────────────────────────
export function priorityColor(priority: Priority): string {
  const map: Record<Priority, string> = {
    P0: "var(--color-p0)",
    P1: "var(--color-p1)",
    P2: "var(--color-p2)",
  };
  return map[priority];
}

// ─── Effort → color ───────────────────────────────────────────────────────────
export function effortColor(effort: Effort): string {
  const map: Record<Effort, string> = {
    low: "var(--color-effort-low)",
    medium: "var(--color-effort-med)",
    high: "var(--color-effort-high)",
  };
  return map[effort];
}

// ─── Format large numbers ─────────────────────────────────────────────────────
export function formatNumber(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return n.toLocaleString();
}

// ─── Friendly dimension names ─────────────────────────────────────────────────
export const DIMENSION_LABELS: Record<string, string> = {
  completeness: "Completeness",
  class_balance: "Class Balance",
  label_quality: "Label Quality",
  duplicates: "Duplicates",
  outliers: "Outliers",
  schema_validity: "Schema Validity",
  leakage: "Leakage Check",
  temporal_coverage: "Temporal Coverage",
  feature_redundancy: "Feature Redundancy",
  distribution_sanity: "Distribution Sanity",
};

// ─── File size formatter ──────────────────────────────────────────────────────
export function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}
