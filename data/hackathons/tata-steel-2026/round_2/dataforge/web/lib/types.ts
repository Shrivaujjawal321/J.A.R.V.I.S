export type Severity = "ok" | "info" | "warning" | "critical";
export type Priority = "P0" | "P1" | "P2";
export type Effort = "low" | "medium" | "high";
export type DatasetType = "tabular" | "time_series";
export type Grade = "A+" | "A" | "B+" | "B" | "C+" | "C" | "D" | "F";

export type SubDimension =
  | "completeness"
  | "class_balance"
  | "label_quality"
  | "duplicates"
  | "outliers"
  | "schema_validity"
  | "leakage"
  | "temporal_coverage"
  | "feature_redundancy"
  | "distribution_sanity";

export interface Sub {
  score: number;
  weight: number;
  detail: string;
  severity: Severity;
}

export interface ReadinessInfo {
  readiness_pct: number;
  baseline_auc: number;
  target_auc: number;
  penalties: Record<string, number>;
}

export interface Improvement {
  dimension: string;
  priority: Priority;
  title: string;
  description: string;
  estimated_score_delta: number;
  effort: Effort;
}

export interface ColumnInfo {
  name: string;
  dtype: string;
  null_pct: number;
}

export interface Preview {
  columns: ColumnInfo[];
  sample_rows: Record<string, unknown>[];
}

// ── v2: dataset status ──────────────────────────────────────────────────────
export type DatasetStatus = "processing" | "scored" | "rejected";

export interface AuditResult {
  // ── existing fields ──
  audit_id: string;
  dataset_id: string;
  filename: string;
  dataset_type: DatasetType;
  n_rows: number;
  n_cols: number;
  composite_score: number;
  grade: string;
  sub_scores: Record<SubDimension, Sub>;
  readiness: ReadinessInfo | null;
  review: string;
  improvements: Improvement[];
  preview: Preview;

  // ── v2 fields ──
  status?: DatasetStatus;            // defaults to "scored" if absent (legacy responses)
  rank?: number | null;
  relevance_score?: number | null;
  rejection_reason?: string;
  tags?: string[];
  file_size_bytes?: number;
}

export interface DatasetCard {
  // ── existing fields ──
  audit_id: string;
  dataset_id: string;
  filename: string;
  composite_score: number;
  grade: string;
  n_rows: number;
  n_cols: number;
  download_count: number;
  created_at: string;

  // ── v2 fields ──
  rank?: number | null;
  relevance_score?: number | null;
  status?: DatasetStatus;
  description?: string;
  tags?: string[];
  file_size_bytes?: number;
  rejection_reason?: string;
  uploaded_by?: string;
  is_own?: boolean;
}

// v2: simplified — Advanced options removed from UI (backend auto-detects)
export interface AuditFormData {
  file: File;
}

// v2: upload quota
export interface UploadQuota {
  used: number;
  max: number;
  remaining: number;
}

export interface ComparisonState {
  previous: AuditResult;
  current: AuditResult;
}
