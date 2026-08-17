import type { AuditResult, AuditFormData, DatasetCard, UploadQuota, DatasetType } from "./types";
import { MOCK_AUDIT_RESULT, MOCK_DATASETS, MOCK_QUOTA } from "./mock-data";
import { supabase } from "./supabase";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8011";
const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK === "1";

// ─── v2 API response shapes ───────────────────────────────────────────────────
interface V2Envelope<T> {
  data: T;
  meta: Record<string, unknown>;
}

/**
 * Raw row shape returned by GET /api/v2/datasets.
 * DB column names differ from DatasetCard field names in several places:
 *   id          → dataset_id + audit_id
 *   upload_date → created_at
 *   size_bytes  → file_size_bytes
 *   owner_id    → used to compute is_own, not exposed on DatasetCard
 *   status      "accepted" (DB enum) → "scored" (UI enum) via normalizeStatus()
 */
interface V2DatasetRow {
  id: string;
  owner_id: string;
  filename: string;
  dataset_type: string;
  n_rows: number | null;
  n_cols: number | null;
  composite_score: number | null;
  overall_score: number | null;
  grade: string | null;
  rank: number | null;
  download_count: number;
  upload_date: string;
  status: string;
  tags: string[] | null;
  description: string | null;
  size_bytes: number | null;
  relevance_score: number | null;
}

interface V2FileResponse {
  data: {
    download_url: string;
    expires_at: string;
    filename: string;
    size_bytes: number | null;
  };
  meta: Record<string, unknown>;
}

// ─── POST /api/datasets response shapes ──────────────────────────────────────
/** Union of all three possible `data` shapes from POST /api/datasets. */
interface PostDatasetsData {
  status: string;                // "rejected" | "processing" | varies on duplicate
  dataset_id: string;
  // processing path (HTTP 202)
  job_id?: string;
  poll_url?: string;
  // rejected path
  rejection_reason?: string;
  relevance_score?: number;
  suggestion?: string;
  // duplicate path
  composite_score?: number;
  rank?: number | null;
  duplicate?: boolean;
}

/** GET /api/jobs/{job_id} data shape. */
interface JobData {
  id: string;
  dataset_id: string;
  status: string;               // "queued" | "running" | "completed" | "failed"
  error_code?: string | null;
  error_message?: string | null;
}

/**
 * GET /api/v2/datasets/{id} data shape.
 * Combines the `datasets` table row with the joined `audit_reports` columns.
 * The `full_report` JSONB field contains the scorer's AuditResult model_dump().
 */
interface V2DatasetWithReport {
  id: string;
  filename: string;
  dataset_type: string;
  n_rows: number | null;
  n_cols: number | null;
  composite_score: number | null;
  grade: string | null;
  rank: number | null;
  relevance_score: number | null;
  status: string;
  tags: string[] | null;
  size_bytes: number | null;
  rejection_reason?: string | null;
  // from audit_reports join (may be null while job is still running)
  full_report: Partial<AuditResult> | null;
  readiness_pct: number | null;
  baseline_auc: number | null;
}

/**
 * DB status 'accepted' maps to the UI status 'scored'.
 * 'processing' and 'rejected' pass through unchanged.
 * Any unknown value falls back to 'processing' (safe display default).
 */
function normalizeStatus(dbStatus: string): DatasetCard["status"] {
  if (dbStatus === "accepted") return "scored";
  if (dbStatus === "processing") return "processing";
  if (dbStatus === "rejected") return "rejected";
  return "processing";
}

/**
 * Map a raw v2 board row → DatasetCard.
 * relevance_score is stored as NUMERIC(6,4) in the range 0–100 (e.g. 87.8600).
 * No normalization required — the RelevanceBar expects 0–100.
 */
function mapV2RowToCard(row: V2DatasetRow, currentUserId: string | null): DatasetCard {
  return {
    // Both id aliases point to the same Postgres UUID
    dataset_id: row.id,
    audit_id: row.id,
    filename: row.filename,
    composite_score: row.composite_score ?? 0,
    grade: row.grade ?? "F",
    n_rows: row.n_rows ?? 0,
    n_cols: row.n_cols ?? 0,
    download_count: row.download_count,
    created_at: row.upload_date,
    // v2 fields
    rank: row.rank,
    relevance_score: row.relevance_score,  // 0–100, stored as NUMERIC(6,4)
    status: normalizeStatus(row.status),
    description: row.description ?? undefined,
    tags: row.tags ?? [],
    file_size_bytes: row.size_bytes ?? undefined,
    // is_own: compare owner UUID against authenticated user id
    is_own: currentUserId != null ? row.owner_id === currentUserId : false,
  };
}

// ─── Simulate network delay in mock mode ─────────────────────────────────────
function delay(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// ─── Auth helpers ─────────────────────────────────────────────────────────────
/**
 * Returns the Authorization header value for the current Supabase session.
 * Returns null when the user is not signed in.
 *
 * Code path: supabase.auth.getSession() → session.access_token → Bearer header.
 * The token is a standard Supabase JWT valid for 1 hour (auto-refreshed by the
 * SDK before expiry via getSession()).
 */
async function getAccessToken(): Promise<string | null> {
  const { data } = await supabase.auth.getSession();
  return data.session?.access_token ?? null;
}

/** Builds headers object with optional Authorization. */
async function authHeaders(extra?: Record<string, string>): Promise<Record<string, string>> {
  const token = await getAccessToken();
  const headers: Record<string, string> = { ...extra };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return headers;
}

// ─── Report mapping helpers ───────────────────────────────────────────────────

/**
 * Map a V2DatasetWithReport row (dataset row + joined audit_reports) → flat AuditResult.
 * The scorer's full output is stored in the `full_report` JSONB column;
 * top-level dataset columns (rank, relevance_score, etc.) override/supplement it.
 */
function mapDatasetRowToAuditResult(row: V2DatasetWithReport): AuditResult {
  const report = row.full_report ?? {};

  // Prefer full_report.readiness; fall back to readiness_pct/baseline_auc columns
  let readiness: AuditResult["readiness"] = null;
  if (report.readiness != null) {
    readiness = report.readiness;
  } else if (row.readiness_pct != null && row.baseline_auc != null) {
    readiness = {
      readiness_pct: row.readiness_pct,
      baseline_auc: row.baseline_auc,
      target_auc: 0.80,
      penalties: {},
    };
  }

  return {
    audit_id:         report.audit_id ?? row.id,
    dataset_id:       row.id,
    filename:         row.filename,
    dataset_type:     (report.dataset_type ?? row.dataset_type ?? "tabular") as DatasetType,
    n_rows:           report.n_rows ?? row.n_rows ?? 0,
    n_cols:           report.n_cols ?? row.n_cols ?? 0,
    composite_score:  report.composite_score ?? row.composite_score ?? 0,
    grade:            report.grade ?? row.grade ?? "F",
    sub_scores:       report.sub_scores ?? ({} as AuditResult["sub_scores"]),
    readiness,
    review:           report.review ?? "",
    improvements:     report.improvements ?? [],
    preview:          report.preview ?? { columns: [], sample_rows: [] },
    // v2 fields from the dataset row (authoritative — may differ from full_report snapshot)
    status:           normalizeStatus(row.status),
    rank:             row.rank ?? null,
    relevance_score:  row.relevance_score ?? null,
    rejection_reason: row.rejection_reason ?? undefined,
    tags:             row.tags ?? [],
    file_size_bytes:  row.size_bytes ?? undefined,
  };
}

/**
 * Internal: fetch and map a single dataset report. Accepts pre-built headers so
 * callers (runAudit, fetchDatasetReport) don't need to re-auth.
 */
async function _fetchDatasetReport(
  id: string,
  headers: Record<string, string>,
): Promise<AuditResult> {
  const res = await fetch(`${API_URL}/api/v2/datasets/${id}`, {
    cache: "no-store",
    headers,
  });
  if (!res.ok) {
    let msg = `Report fetch failed (${res.status})`;
    try {
      const body = await res.json() as { error?: { message?: string } };
      msg = body?.error?.message ?? msg;
    } catch { /* ignore */ }
    throw new Error(msg);
  }
  const envelope = await res.json() as V2Envelope<V2DatasetWithReport>;
  return mapDatasetRowToAuditResult(envelope.data);
}

/**
 * Poll GET /api/jobs/{job_id} every intervalMs until the job reaches a
 * terminal state (completed | failed). Throws on failure or timeout.
 */
async function pollJobUntilDone(
  jobId: string,
  headers: Record<string, string>,
  maxAttempts = 40,
  intervalMs = 1500,
): Promise<void> {
  for (let attempt = 0; attempt < maxAttempts; attempt++) {
    if (attempt > 0) await delay(intervalMs);

    const res = await fetch(`${API_URL}/api/jobs/${jobId}`, {
      cache: "no-store",
      headers,
    });
    if (!res.ok) throw new Error(`Job status poll failed (${res.status})`);

    const env = await res.json() as V2Envelope<JobData>;
    const job = env.data;

    if (job.status === "completed") return;
    if (job.status === "failed") {
      throw new Error(
        `Scoring failed: ${job.error_message ?? job.error_code ?? "Unknown error"}`
      );
    }
    // "queued" | "running" → keep polling
  }
  throw new Error(
    "Scoring is taking longer than expected. Please refresh the page to check your result in the leaderboard."
  );
}

/**
 * For the duplicate path: if the existing dataset is still being scored, poll the
 * dataset endpoint until its status leaves "processing".
 * We check the dataset row directly (owner can access own processing datasets).
 */
async function pollDatasetUntilScored(
  datasetId: string,
  headers: Record<string, string>,
  maxAttempts = 30,
  intervalMs = 2000,
): Promise<void> {
  for (let attempt = 0; attempt < maxAttempts; attempt++) {
    if (attempt > 0) await delay(intervalMs);

    const res = await fetch(`${API_URL}/api/v2/datasets/${datasetId}`, {
      cache: "no-store",
      headers,
    });
    if (!res.ok) return; // can't check status — proceed with whatever report exists

    const env = await res.json() as V2Envelope<{ status: string }>;
    const st = env.data?.status;
    if (st === "accepted" || st === "rejected") return;
    // still "processing" — continue
  }
  // timed out — fall through and return whatever partial report exists
}

// ─── Audit ────────────────────────────────────────────────────────────────────
/**
 * Upload a dataset and return the scored AuditResult.
 *
 * Handles all three v2 backend response shapes transparently:
 *   - HTTP 200, status "rejected"   → returns a rejected AuditResult immediately
 *   - HTTP 200, duplicate:true      → fetches the existing report
 *   - HTTP 202, status "processing" → polls the job endpoint until complete,
 *                                     then fetches the full report
 *
 * @param onStatusChange  Optional callback receiving human-readable stage labels
 *   (e.g. "Scoring your dataset…"). Called with null when done or on error.
 */
export async function runAudit(
  data: AuditFormData,
  onStatusChange?: (message: string | null) => void,
): Promise<AuditResult> {
  if (USE_MOCK) {
    await delay(2200);
    return MOCK_AUDIT_RESULT;
  }

  const form = new FormData();
  form.append("file", data.file);

  // Attach auth token so the backend can verify ownership + enforce quota
  const headers = await authHeaders();

  onStatusChange?.("Uploading dataset…");

  const res = await fetch(`${API_URL}/api/datasets`, {
    method: "POST",
    headers,
    body: form,
  });

  if (!res.ok) {
    onStatusChange?.(null);
    let msg = `Upload failed (${res.status})`;
    try {
      const body = await res.json() as { error?: { message?: string } };
      msg = body?.error?.message ?? msg;
    } catch { /* ignore parse errors */ }
    throw new Error(msg);
  }

  // All success paths return { "data": {...}, "meta": {} } — unwrap first.
  const envelope = await res.json() as V2Envelope<PostDatasetsData>;
  const payload = envelope.data;

  // ── Path 1: Relevance-rejected ────────────────────────────────────────────
  if (payload.status === "rejected") {
    onStatusChange?.(null);
    return {
      audit_id:         `rejected_${payload.dataset_id}`,
      dataset_id:       payload.dataset_id,
      filename:         data.file.name,
      dataset_type:     "tabular",
      n_rows:           0,
      n_cols:           0,
      composite_score:  0,
      grade:            "F",
      sub_scores:       {} as AuditResult["sub_scores"],
      readiness:        null,
      review:           "",
      improvements:     [],
      preview:          { columns: [], sample_rows: [] },
      status:           "rejected",
      rank:             null,
      relevance_score:  payload.relevance_score ?? 0,
      rejection_reason: payload.rejection_reason ?? "Dataset is not relevant to the Tata Steel Hackathon.",
    };
  }

  // ── Path 2: Exact duplicate of an already-uploaded dataset ────────────────
  if (payload.duplicate === true) {
    // If the existing dataset is still being scored, wait for it
    if (payload.status === "processing") {
      onStatusChange?.("Dataset detected — waiting for scoring to complete…");
      await pollDatasetUntilScored(payload.dataset_id, headers);
    } else {
      onStatusChange?.("Dataset already scored — loading report…");
    }
    const report = await _fetchDatasetReport(payload.dataset_id, headers);
    onStatusChange?.(null);
    return report;
  }

  // ── Path 3: Accepted → async scoring job (HTTP 202) ───────────────────────
  if (!payload.job_id) {
    onStatusChange?.(null);
    throw new Error("Unexpected response from server: missing job_id. Please try again.");
  }

  onStatusChange?.("Scoring your dataset — this may take ~30 seconds…");
  await pollJobUntilDone(payload.job_id, headers);

  onStatusChange?.("Fetching results…");
  const report = await _fetchDatasetReport(payload.dataset_id, headers);
  onStatusChange?.(null);
  return report;
}

// ─── Datasets ─────────────────────────────────────────────────────────────────
export async function fetchDatasets(): Promise<DatasetCard[]> {
  if (USE_MOCK) {
    await delay(600);
    return MOCK_DATASETS;
  }

  try {
    // Auth is optional for public listing — pass token if available so backend
    // can annotate is_own on the user's own datasets.
    const headers = await authHeaders();

    // Resolve current user id for is_own computation.
    // getUser() is safer than getSession() — verifies against Supabase auth server.
    // Returns null when logged out, which is fine (public board).
    const { data: userData } = await supabase.auth.getUser();
    const currentUserId = userData.user?.id ?? null;

    const res = await fetch(`${API_URL}/api/v2/datasets`, {
      cache: "no-store",
      headers,
    });
    if (!res.ok) throw new Error(`Datasets fetch failed (${res.status})`);

    const envelope = await res.json() as V2Envelope<V2DatasetRow[]>;
    const rows: V2DatasetRow[] = envelope.data ?? [];
    return rows.map((row) => mapV2RowToCard(row, currentUserId));
  } catch {
    // Graceful fallback: return empty array so the board renders "no datasets"
    // rather than crashing the page.
    return [];
  }
}

// ─── Upload quota ─────────────────────────────────────────────────────────────
export async function fetchQuota(): Promise<UploadQuota> {
  if (USE_MOCK) {
    await delay(300);
    return MOCK_QUOTA;
  }

  // Quota is auth-gated — no token → return graceful fallback (unlimited feel for
  // anonymous visitors; real gate is on the upload action itself).
  const token = await getAccessToken();
  if (!token) {
    return { used: 0, max: 5, remaining: 5 };
  }

  const res = await fetch(`${API_URL}/api/me/quota`, {
    cache: "no-store",
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) {
    // Graceful fallback: if endpoint not ready, return unlimited quota
    return { used: 0, max: 5, remaining: 5 };
  }
  // Backend wraps in { data: { used, limit, remaining, ... }, meta: {} }
  const envelope = await res.json() as V2Envelope<{ used: number; limit: number; remaining: number }>;
  const q = envelope.data;
  return { used: q.used, max: q.limit, remaining: q.remaining };
}

// ─── Delete dataset (owner only) ──────────────────────────────────────────────
export async function deleteDataset(id: string): Promise<void> {
  if (USE_MOCK) {
    await delay(400);
    return;
  }

  const headers = await authHeaders();
  const res = await fetch(`${API_URL}/api/v2/datasets/${id}`, {
    method: "DELETE",
    headers,
  });
  if (!res.ok) throw new Error(`Delete failed (${res.status})`);
}

// ─── Download increment ───────────────────────────────────────────────────────
export async function incrementDownload(id: string): Promise<{ download_count: number }> {
  if (USE_MOCK) {
    await delay(200);
    return { download_count: 999 };
  }

  const res = await fetch(`${API_URL}/api/datasets/${id}/download`, {
    method: "POST",
  });
  if (!res.ok) throw new Error(`Download increment failed (${res.status})`);
  return res.json() as Promise<{ download_count: number }>;
}

// ─── File download via v2 signed URL ─────────────────────────────────────────
/**
 * GET /api/v2/datasets/{id}/file returns:
 *   { "data": { "download_url": "...", "expires_at": "...", "filename": "...", "size_bytes": ... }, "meta": {} }
 *
 * Strategy: fetch the endpoint to get the signed URL, then open it in a new tab.
 * Auth token is forwarded so the backend can serve non-public (own) datasets.
 * Falls back to legacy /api/datasets/{id}/file if the v2 call fails (e.g. PERSISTENCE_BACKEND != supabase).
 */
export async function downloadDatasetFile(id: string): Promise<void> {
  if (USE_MOCK) {
    await delay(200);
    return;
  }

  const headers = await authHeaders();
  const res = await fetch(`${API_URL}/api/v2/datasets/${id}/file`, { headers });

  if (!res.ok) {
    // v2 file endpoint not available (legacy backend) — fall back to direct link
    window.open(`${API_URL}/api/datasets/${id}/file`, "_blank", "noopener,noreferrer");
    return;
  }

  const envelope = await res.json() as V2FileResponse;
  const signedUrl = envelope.data?.download_url;
  if (signedUrl) {
    window.open(signedUrl, "_blank", "noopener,noreferrer");
  }
}

/**
 * Legacy synchronous URL helper — kept for any code that still uses it.
 * Points to the v2 file endpoint; the backend returns a signed-URL JSON body
 * (not a redirect), so callers should prefer downloadDatasetFile() instead.
 * @deprecated Use downloadDatasetFile() for correct signed-URL handling.
 */
export function datasetFileUrl(id: string): string {
  return `${API_URL}/api/v2/datasets/${id}/file`;
}

// ─── Full audit report (v2) ───────────────────────────────────────────────────
/**
 * GET /api/v2/datasets/{id} → { "data": <dataset row + full_report JSONB>, "meta": {} }
 * Public for accepted datasets; requires auth token for own non-accepted datasets.
 * Properly maps the nested `full_report` column into a flat AuditResult.
 */
export async function fetchDatasetReport(id: string): Promise<AuditResult> {
  if (USE_MOCK) {
    await delay(500);
    return MOCK_AUDIT_RESULT;
  }

  const headers = await authHeaders();
  return _fetchDatasetReport(id, headers);
}
