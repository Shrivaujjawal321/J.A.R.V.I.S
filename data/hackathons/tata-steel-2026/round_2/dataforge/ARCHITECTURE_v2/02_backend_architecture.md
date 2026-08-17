# EDITH DataForge — Backend Architecture v2

**Document type:** Architecture + API Design + Database Schema  
**Target:** Production-grade Supabase migration from local-JSONL / HF-ephemeral model  
**Deadline constraint:** 15 Jun 2026 hackathon demo

---

## 1. Backend Architecture

### 1.1 Component Map

```
┌──────────────────────────────────────────────────────────────────┐
│  Client (Next.js 15 on Vercel)                                   │
│  - Drag-drop upload with XHR progress events                     │
│  - Polling loop on job status                                     │
│  - Board page with cursor pagination + Supabase Realtime (opt.)  │
└────────────────────────┬─────────────────────────────────────────┘
                         │ HTTPS (REST)
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│  API Layer  (FastAPI, Uvicorn, single worker)                    │
│                                                                  │
│  ┌─────────────────┐  ┌────────────────────┐  ┌──────────────┐  │
│  │ Auth Middleware  │  │ Quota Middleware    │  │ Rate Limiter │  │
│  │ Supabase JWT     │  │ ≤5 datasets/user   │  │ slowapi      │  │
│  │ verify + inject  │  │ server-side check  │  │ per-user-IP  │  │
│  │ user_id to ctx  │  │                    │  │              │  │
│  └─────────────────┘  └────────────────────┘  └──────────────┘  │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  Route Handlers                                             │ │
│  │  POST /api/datasets  GET /api/datasets  GET /api/me/quota   │ │
│  │  GET /api/datasets/{id}  GET /api/datasets/{id}/file        │ │
│  │  DELETE /api/datasets/{id}  GET /api/jobs/{job_id}          │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌──────────────────────────┐  ┌──────────────────────────────┐  │
│  │  Upload Pipeline         │  │  Background Task Pool         │  │
│  │  1. Parse + validate     │  │  asyncio.Queue (n=3 workers)  │  │
│  │  2. Relevance gate       │  │  Pulls job_ids, runs scorer,  │  │
│  │  3. Checksum dedup       │  │  writes result to Postgres,   │  │
│  │  4. Enqueue job          │  │  recalculates global ranks,   │  │
│  │  5. Return 202 + job_id  │  │  updates Storage path.        │  │
│  └──────────────────────────┘  └──────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────┐  ┌──────────────────────────────┐  │
│  │  Relevance Gate          │  │  Cache Layer                  │  │
│  │  Fast heuristic (rule-   │  │  - Board list: 60s in-process │  │
│  │  based keyword/col check │  │    TTLCache (cachetools)      │  │
│  │  + optional LLM signal)  │  │  - Per-dataset report: warm  │  │
│  │  < 200ms target          │  │    from Postgres on first hit │  │
│  └──────────────────────────┘  └──────────────────────────────┘  │
└──────────────────────────┬───────────────────────────────────────┘
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  Supabase    │  │  Supabase    │  │  Supabase    │
│  Auth        │  │  Postgres    │  │  Storage     │
│  (JWT issue, │  │  (schema     │  │  (private    │
│  Google SSO) │  │  below)      │  │  bucket:     │
│              │  │              │  │  datasets)   │
└──────────────┘  └──────────────┘  └──────────────┘
```

### 1.2 Data Flow — Upload + Score

```
POST /api/datasets (multipart)
  │
  ├─ 1. JWT verify → extract user_id
  ├─ 2. Quota check → SELECT count FROM datasets WHERE owner_id=$1 AND status IN ('accepted','processing')
  │      if count >= 5 → 429 { error.code: "quota_exceeded" }
  ├─ 3. Read file bytes (up to 50MB hard cap → 413 on exceed)
  ├─ 4. Parse DataFrame (pandas, CSV/XLSX/JSON)
  │      failure → 422 { error.code: "parse_error" }
  ├─ 5. Compute checksum (SHA-256 of raw bytes) → idempotency key
  │      SELECT id FROM datasets WHERE checksum=$1 AND owner_id=$2 AND status != 'rejected'
  │      if found → 200 { existing record, idempotent }
  ├─ 6. Relevance gate (< 200ms) → see §1.4
  │      if rejected → INSERT dataset(status='rejected') → 200 { status:'rejected', reason:... }
  │      (rejected datasets do NOT count toward quota)
  ├─ 7. Upload raw file to Supabase Storage
  │      Path: {user_id}/{dataset_id_hash}/{filename}
  ├─ 8. INSERT datasets(status='processing'), INSERT jobs(status='queued')
  ├─ 9. Enqueue job_id to asyncio.Queue
  └─ 10. Return 202 { job_id, dataset_id, status:'processing' }

Background Worker (asyncio task, runs alongside FastAPI):
  │
  ├─ Dequeue job_id
  ├─ Re-read file from Supabase Storage (or from in-memory buffer passed via queue)
  ├─ run_audit() → AuditResult (existing scorer, unchanged)
  ├─ INSERT audit_reports (full JSON)
  ├─ UPDATE datasets SET status='accepted', composite_score=..., rank=NULL, ...
  ├─ Recalculate global ranks:
  │    UPDATE datasets SET rank = sub.rank
  │    FROM (SELECT id, RANK() OVER (ORDER BY composite_score DESC)
  │          FROM datasets WHERE status='accepted') sub
  │    WHERE datasets.id = sub.id
  ├─ UPDATE jobs SET status='completed'
  └─ Invalidate board cache
```

### 1.3 Where to Host the Backend

| Option | Pros | Cons | Verdict |
|---|---|---|---|
| **HF Spaces (current)** | Free, zero config, already live | Sleeps after 30 min inactivity; async jobs can die mid-flight; ephemeral disk (solved by Supabase but sleep still kills in-flight jobs) | Acceptable for demo if combined with UptimeRobot ping + in-memory job re-queue on startup |
| **Render (free tier)** | Persistent container, no ephemeral disk issue | Free tier sleeps after 15 min inactivity (same problem) | Same problem as HF |
| **Render (paid, $7/mo)** | Never sleeps, persistent, easy deploy, managed TLS | $7/mo | **RECOMMENDED for post-hackathon** |
| **Fly.io (free allowance)** | 3 shared VMs free, never sleeps on paid, good CLI | Slightly more ops overhead | Good alternative to Render |

**Decision for hackathon deadline (15 Jun):** Stay on HF Space with these two mitigations:
1. Add UptimeRobot to ping `/api/health` every 5 min → prevents sleep during judging window.
2. On app startup, re-queue any `jobs` with `status='queued'` or `status='processing'` (orphaned by restart) → jobs survive container restarts.

After hackathon: migrate to Render paid ($7/mo) for clean production operation.

### 1.4 Relevance Gate Design

The gate runs synchronously before any file is stored. Target: < 200ms.

**Heuristic pass (no ML, instant):**
- Column name scan: if ≥ 2 of these match → `relevant`:  
  `["temperature", "vibration", "pressure", "speed", "current", "voltage", "flow",  
   "torque", "bearing", "rpm", "sensor", "machine", "failure", "fault", "defect",  
   "timestamp", "cycle", "wear", "tool", "steel", "thickness", "coil", "roll"]`
- If file name contains industrial keywords → boost signal
- If n_cols ≥ 8 AND n_rows ≥ 100 → likely a real dataset (not a test file)

**Fallback LLM gate (when heuristic is ambiguous, score=0.3-0.7):**
- Send first 5 column names + dataset metadata to Claude Haiku (via existing subscription auth)
- Prompt: "Is this dataset from industrial manufacturing, steel plant, predictive maintenance, or similar? Answer YES or NO only."
- Timeout: 3s. If timeout or error → treat as `relevant` (fail-open to avoid blocking real uploads)

**Decision:**
- `relevance_score >= 0.4` → accepted into scoring pipeline
- `relevance_score < 0.4` → rejected; INSERT to `datasets` with `status='rejected'`; return structured error

### 1.5 Caching Strategy

| Resource | Strategy | TTL | Invalidation trigger |
|---|---|---|---|
| Board list (`/api/datasets`) | In-process `TTLCache` (cachetools) | 60s | New dataset accepted / deleted |
| Per-dataset report (`/api/datasets/{id}`) | Postgres + FastAPI response (no extra layer) | None needed — data is immutable post-processing | N/A |
| Signed download URLs | Generated per-request | 1h (Supabase signed URL TTL) | N/A |
| Quota count | Computed per-request; no cache | N/A | Runs on small query with index |

---

## 2. Database Schema (Postgres / Supabase)

### 2.1 Full DDL

```sql
-- ============================================================
-- Forward migration: EDITH DataForge v2
-- ============================================================

-- Extension for UUID generation (Supabase enables this by default)
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================
-- users: lightweight profile record linked to auth.users
-- Supabase auth.users is the source of truth; this table
-- only stores EDITH-specific profile data.
-- ============================================================
CREATE TABLE IF NOT EXISTS public.users (
    id            UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email         TEXT,
    display_name  TEXT,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS users_email_idx ON public.users (email);

-- ============================================================
-- datasets: core record per uploaded dataset
-- ============================================================
CREATE TYPE dataset_status AS ENUM ('processing', 'accepted', 'rejected', 'deleted');
CREATE TYPE dataset_type   AS ENUM ('tabular', 'time_series');
CREATE TYPE grade_enum     AS ENUM ('Excellent', 'Good', 'Fair', 'Needs Work', 'Poor');

CREATE TABLE IF NOT EXISTS public.datasets (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id            UUID        NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

    -- File metadata
    filename            TEXT        NOT NULL,
    mime_type           TEXT        NOT NULL,   -- text/csv | application/vnd.openxmlformats... | application/json
    size_bytes          BIGINT      NOT NULL,
    checksum            CHAR(64)    NOT NULL,   -- SHA-256 of raw file bytes (idempotency key)
    storage_path        TEXT,                   -- Supabase Storage path: {owner_id}/{dataset_id}/{filename}

    -- Structural metadata (populated after parse, before scoring)
    n_rows              INT,
    n_cols              INT,
    dataset_type        dataset_type,
    tags                TEXT[]      DEFAULT '{}',

    -- Scoring outputs (populated when status → accepted)
    composite_score     NUMERIC(6,2),
    grade               grade_enum,
    rank                INT,                    -- global leaderboard rank (1 = best), NULL until scored
    relevance_score     NUMERIC(4,3),           -- 0.0 – 1.0 from gate

    -- Status
    status              dataset_status NOT NULL DEFAULT 'processing',
    rejection_reason    TEXT,                   -- populated when status='rejected'

    -- Timestamps
    upload_date         TIMESTAMPTZ NOT NULL DEFAULT now(),
    scored_at           TIMESTAMPTZ,
    deleted_at          TIMESTAMPTZ,

    -- Download tracking
    download_count      INT NOT NULL DEFAULT 0,

    -- Soft-delete: don't physically remove, just hide from board
    CONSTRAINT chk_deleted_at CHECK (
        (status = 'deleted' AND deleted_at IS NOT NULL)
        OR (status != 'deleted' AND deleted_at IS NULL)
    )
);

-- Primary access patterns
CREATE INDEX IF NOT EXISTS datasets_owner_idx     ON public.datasets (owner_id, status);
CREATE INDEX IF NOT EXISTS datasets_board_idx     ON public.datasets (composite_score DESC NULLS LAST)
    WHERE status = 'accepted';                   -- partial index — board queries only hit accepted rows
CREATE INDEX IF NOT EXISTS datasets_checksum_idx  ON public.datasets (checksum, owner_id);
CREATE INDEX IF NOT EXISTS datasets_rank_idx      ON public.datasets (rank ASC NULLS LAST)
    WHERE status = 'accepted';
CREATE INDEX IF NOT EXISTS datasets_upload_idx    ON public.datasets (upload_date DESC);

-- ============================================================
-- audit_reports: full scoring result (1:1 with datasets)
-- Kept separate to avoid loading large JSON on board queries
-- ============================================================
CREATE TABLE IF NOT EXISTS public.audit_reports (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    dataset_id      UUID        NOT NULL UNIQUE REFERENCES public.datasets(id) ON DELETE CASCADE,

    -- All 10+1 dimension scores as typed columns for fast filtering
    score_completeness          NUMERIC(6,2),
    score_class_balance         NUMERIC(6,2),
    score_label_quality         NUMERIC(6,2),
    score_duplicates            NUMERIC(6,2),
    score_outliers              NUMERIC(6,2),
    score_schema_validity       NUMERIC(6,2),
    score_leakage               NUMERIC(6,2),
    score_temporal_coverage     NUMERIC(6,2),
    score_feature_redundancy    NUMERIC(6,2),
    score_distribution_sanity   NUMERIC(6,2),
    score_domain_pdm            NUMERIC(6,2),   -- NULL for non-PdM time-series

    -- Readiness
    readiness_pct               NUMERIC(5,2),
    baseline_auc                NUMERIC(5,4),

    -- Full AuditResult JSON (AuditResult pydantic model → model_dump_json())
    -- Stored as JSONB for partial indexing if needed
    full_report                 JSONB       NOT NULL,

    created_at                  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS audit_reports_dataset_id_idx ON public.audit_reports (dataset_id);
-- JSONB GIN index — only if you later need full-text search within reports
-- CREATE INDEX IF NOT EXISTS audit_reports_gin ON public.audit_reports USING GIN (full_report);

-- ============================================================
-- jobs: async scoring job tracking
-- ============================================================
CREATE TYPE job_status AS ENUM ('queued', 'running', 'completed', 'failed');

CREATE TABLE IF NOT EXISTS public.jobs (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    dataset_id      UUID        NOT NULL REFERENCES public.datasets(id) ON DELETE CASCADE,
    owner_id        UUID        NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

    status          job_status  NOT NULL DEFAULT 'queued',
    queued_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    started_at      TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,

    -- Error detail on failure
    error_code      TEXT,
    error_detail    TEXT,

    -- Attempt counter for re-queue logic
    attempt         SMALLINT    NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS jobs_dataset_idx  ON public.jobs (dataset_id);
CREATE INDEX IF NOT EXISTS jobs_status_idx   ON public.jobs (status) WHERE status IN ('queued', 'running');
CREATE INDEX IF NOT EXISTS jobs_owner_idx    ON public.jobs (owner_id, queued_at DESC);

-- ============================================================
-- upload_audit_log: security + audit trail
-- Write-only from application. Never UPDATE/DELETE.
-- ============================================================
CREATE TYPE audit_event_type AS ENUM (
    'upload_started',
    'relevance_rejected',
    'quota_exceeded',
    'scoring_started',
    'scoring_completed',
    'scoring_failed',
    'download',
    'delete_requested',
    'auth_error'
);

CREATE TABLE IF NOT EXISTS public.upload_audit_log (
    id              BIGSERIAL   PRIMARY KEY,
    event_type      audit_event_type NOT NULL,
    owner_id        UUID,           -- NULL for unauthenticated events (e.g. auth_error)
    dataset_id      UUID,           -- NULL for pre-dataset events (e.g. quota_exceeded)
    ip_address      INET,
    user_agent      TEXT,
    detail          JSONB,          -- event-specific payload (rejection reason, error code, etc.)
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Retention: this table is append-only; archive rows older than 90 days via pg_cron
CREATE INDEX IF NOT EXISTS audit_log_owner_idx   ON public.upload_audit_log (owner_id, created_at DESC);
CREATE INDEX IF NOT EXISTS audit_log_event_idx   ON public.upload_audit_log (event_type, created_at DESC);
CREATE INDEX IF NOT EXISTS audit_log_dataset_idx ON public.upload_audit_log (dataset_id) WHERE dataset_id IS NOT NULL;

-- ============================================================
-- Rank recalculation function (called by background worker
-- after each job completion)
-- ============================================================
CREATE OR REPLACE FUNCTION recalculate_dataset_ranks()
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    UPDATE public.datasets AS d
    SET    rank = sub.new_rank
    FROM (
        SELECT id,
               RANK() OVER (ORDER BY composite_score DESC NULLS LAST) AS new_rank
        FROM   public.datasets
        WHERE  status = 'accepted'
    ) sub
    WHERE d.id = sub.id
      AND d.status = 'accepted';
END;
$$;

-- ============================================================
-- Rollback migration
-- ============================================================
-- DROP FUNCTION IF EXISTS recalculate_dataset_ranks();
-- DROP TABLE IF EXISTS public.upload_audit_log;
-- DROP TABLE IF EXISTS public.jobs;
-- DROP TABLE IF EXISTS public.audit_reports;
-- DROP TABLE IF EXISTS public.datasets;
-- DROP TABLE IF EXISTS public.users;
-- DROP TYPE IF EXISTS audit_event_type;
-- DROP TYPE IF EXISTS job_status;
-- DROP TYPE IF EXISTS grade_enum;
-- DROP TYPE IF EXISTS dataset_type;
-- DROP TYPE IF EXISTS dataset_status;
```

### 2.2 Row-Level Security (RLS) Policies

```sql
-- Enable RLS on all application tables
ALTER TABLE public.users         ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.datasets      ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.audit_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.jobs          ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.upload_audit_log ENABLE ROW LEVEL SECURITY;

-- ── users ──────────────────────────────────────────────────
CREATE POLICY "users: self read+write"
ON public.users
FOR ALL
USING  (auth.uid() = id)
WITH CHECK (auth.uid() = id);

-- ── datasets ───────────────────────────────────────────────
-- Public board: anyone (even unauthenticated) can read accepted datasets
CREATE POLICY "datasets: public board read"
ON public.datasets
FOR SELECT
USING (status = 'accepted');

-- Owner can see all their own datasets (any status including rejected/processing)
CREATE POLICY "datasets: owner read all"
ON public.datasets
FOR SELECT
USING (auth.uid() = owner_id);

-- Only authenticated users can insert
CREATE POLICY "datasets: authenticated insert"
ON public.datasets
FOR INSERT
WITH CHECK (auth.uid() = owner_id);

-- Owner can soft-delete (UPDATE status to 'deleted')
CREATE POLICY "datasets: owner soft delete"
ON public.datasets
FOR UPDATE
USING  (auth.uid() = owner_id)
WITH CHECK (auth.uid() = owner_id);

-- Service role (backend worker) can update scores / status
-- (Backend uses Supabase service role key for background writes — bypasses RLS)

-- ── audit_reports ──────────────────────────────────────────
-- Public can read reports for accepted datasets
CREATE POLICY "audit_reports: public read for accepted"
ON public.audit_reports
FOR SELECT
USING (
    EXISTS (
        SELECT 1 FROM public.datasets d
        WHERE d.id = dataset_id
          AND d.status = 'accepted'
    )
);

-- Owner can read their own reports regardless of status
CREATE POLICY "audit_reports: owner read"
ON public.audit_reports
FOR SELECT
USING (
    EXISTS (
        SELECT 1 FROM public.datasets d
        WHERE d.id = dataset_id
          AND d.owner_id = auth.uid()
    )
);

-- ── jobs ───────────────────────────────────────────────────
CREATE POLICY "jobs: owner read"
ON public.jobs
FOR SELECT
USING (auth.uid() = owner_id);

-- ── upload_audit_log ───────────────────────────────────────
-- No user reads on audit log — it is read by service role only
-- (Supabase dashboard / pg_cron archival job accesses via service key)
CREATE POLICY "audit_log: deny all user reads"
ON public.upload_audit_log
FOR SELECT
USING (false);
```

### 2.3 Quota Enforcement Query

```sql
-- Count toward quota: only processing + accepted. Rejected do not count.
SELECT COUNT(*) AS active_datasets
FROM   public.datasets
WHERE  owner_id = $1
  AND  status   IN ('processing', 'accepted');
-- Index hit: datasets_owner_idx(owner_id, status) covers this exactly.
```

### 2.4 Rank Computation Notes

- `rank` is a materialised column (integer) on `datasets`, not computed on the fly.
- Recalculated by calling `SELECT recalculate_dataset_ranks()` after every job completion.
- `RANK()` — not `DENSE_RANK()` — so ties get the same rank and the next rank skips (e.g. two scores of 87 both get rank 3; next is rank 5). This matches conventional leaderboard UX.
- At the scale of a hackathon (hundreds of datasets), a full rank recompute costs microseconds. No partial update needed.

---

## 3. API Design

### 3.1 Standard Envelopes

**Success (single resource):**
```json
{
  "data": { "...resource fields..." },
  "meta": {}
}
```

**Success (list / paginated):**
```json
{
  "data": [ "...items..." ],
  "meta": {
    "total": 142,
    "limit": 20,
    "next_cursor": "eyJpZCI6Ii4uLiJ9"
  }
}
```

**Error:**
```json
{
  "error": {
    "code": "string_enum",
    "message": "human-readable sentence",
    "type": "validation | auth | quota | relevance | server",
    "doc_url": "https://edith.app/docs/errors/{code}"
  }
}
```

**Typed error codes:**

| Code | HTTP | Meaning |
|---|---|---|
| `unauthorized` | 401 | Missing or invalid JWT |
| `forbidden` | 403 | Authenticated but not owner |
| `not_found` | 404 | Resource does not exist or is deleted |
| `parse_error` | 422 | File could not be parsed as CSV/XLSX/JSON |
| `unsupported_file_type` | 415 | File extension not in CSV/XLSX/JSON |
| `file_too_large` | 413 | File exceeds 50MB hard cap |
| `empty_dataset` | 422 | Parsed DataFrame is empty or has 0 rows |
| `quota_exceeded` | 429 | User already has 5 active datasets |
| `relevance_rejected` | 200 | File parsed OK but domain gate rejected it |
| `duplicate_dataset` | 200 | Identical file (same checksum) already exists for this user |
| `job_not_found` | 404 | Job ID does not exist or belongs to another user |
| `server_error` | 500 | Unexpected scorer failure |

Note: `relevance_rejected` and `duplicate_dataset` return HTTP 200 (not errors in the REST sense — the upload was processed, just not accepted into the ranked board).

**Relevance rejection body:**
```json
{
  "data": {
    "status": "rejected",
    "rejection_reason": "No industrial/manufacturing column patterns detected.",
    "relevance_score": 0.18,
    "suggestion": "Upload datasets from steel plants, predictive maintenance, or manufacturing sensors."
  },
  "error": null
}
```

### 3.2 Endpoint Table

#### POST /api/datasets

Upload a dataset for analysis.

- **Auth:** Required (Supabase JWT, `Authorization: Bearer {token}`)
- **Content-Type:** `multipart/form-data`
- **Idempotency:** Natural — if `checksum` matches an existing `accepted`/`processing` row for this user, return existing record (no re-score)
- **Rate limit:** 10 uploads/hour per user

**Request fields:**

| Field | Type | Required | Notes |
|---|---|---|---|
| `file` | File | Yes | CSV / XLSX / JSON, max 50MB |
| `label_col` | string | No | Column name containing target variable |
| `timestamp_col` | string | No | Column name containing timestamps |
| `target_auc` | float (0–1) | No | Default 0.80 |
| `description` | string | No | User-provided dataset description |
| `tags` | string | No | Comma-separated tags |

**Pydantic request model (validated before file parse):**
```python
class DatasetUploadMeta(BaseModel):
    label_col:     Optional[str]   = None
    timestamp_col: Optional[str]   = None
    target_auc:    float           = Field(default=0.80, ge=0.5, le=1.0)
    description:   Optional[str]   = Field(default=None, max_length=500)
    tags:          Optional[str]   = None  # comma-separated, split server-side
```

**Response (202 — accepted for processing):**
```json
{
  "data": {
    "job_id": "3f8a2b1c-...",
    "dataset_id": "7e4d9f3a-...",
    "status": "processing",
    "poll_url": "/api/jobs/3f8a2b1c-..."
  },
  "meta": {}
}
```

**Response (200 — relevance rejected):**
```json
{
  "data": {
    "status": "rejected",
    "dataset_id": "7e4d9f3a-...",
    "rejection_reason": "...",
    "relevance_score": 0.12
  },
  "meta": {}
}
```

**Response (200 — duplicate idempotent):**
```json
{
  "data": {
    "status": "accepted",
    "dataset_id": "7e4d9f3a-...",
    "composite_score": 74.5,
    "rank": 3,
    "duplicate": true
  },
  "meta": {}
}
```

---

#### GET /api/jobs/{job_id}

Poll async scoring status.

- **Auth:** Required (owner only)
- **Response (200):**
```json
{
  "data": {
    "job_id": "3f8a2b1c-...",
    "dataset_id": "7e4d9f3a-...",
    "status": "queued | running | completed | failed",
    "queued_at": "2026-06-10T10:00:00Z",
    "started_at": "2026-06-10T10:00:05Z",
    "completed_at": null,
    "error": null
  },
  "meta": {}
}
```

Frontend polling strategy: 1s → 2s → 4s → 8s (exponential backoff, cap at 10s, timeout at 5 min).

---

#### GET /api/datasets

Public leaderboard with search, filter, sort, cursor pagination.

- **Auth:** Optional (public board visible to all; authenticated users also see their own processing/rejected entries)
- **Rate limit:** 60 req/min per IP

**Query parameters:**

| Param | Type | Default | Notes |
|---|---|---|---|
| `limit` | int 1–100 | 20 | Page size |
| `cursor` | string | (none) | Opaque cursor from previous `meta.next_cursor` |
| `sort` | enum | `rank` | `rank \| score \| upload_date \| downloads` |
| `order` | enum | `asc` (for rank), `desc` otherwise | `asc \| desc` |
| `dataset_type` | enum | (all) | `tabular \| time_series` |
| `grade` | enum | (all) | `Excellent \| Good \| Fair \| Needs Work \| Poor` |
| `min_score` | float | 0 | Filter by `composite_score >= min_score` |
| `q` | string | (none) | Full-text search on `filename` (simple ILIKE for now) |
| `my_datasets` | bool | false | Authenticated only — show all user's datasets inc. processing/rejected |

**Response (200):**
```json
{
  "data": [
    {
      "id": "7e4d9f3a-...",
      "filename": "bearing_sensors_v3.csv",
      "dataset_type": "time_series",
      "n_rows": 50000,
      "n_cols": 14,
      "composite_score": 87.4,
      "grade": "Excellent",
      "rank": 1,
      "download_count": 23,
      "upload_date": "2026-06-10T10:05:00Z",
      "status": "accepted",
      "tags": ["steel", "bearing", "vibration"]
    }
  ],
  "meta": {
    "total": 142,
    "limit": 20,
    "next_cursor": "eyJpZCI6Ijdl..."
  }
}
```

Cursor encoding: base64-encode `{"id": "<last_id>", "score": <last_score>, "rank": <last_rank>}` depending on sort key. Decoded server-side, never trusted — validated against schema.

---

#### GET /api/datasets/{id}

Full audit report for a single dataset.

- **Auth:** Optional for `accepted` datasets; required for owner's own `processing`/`rejected` datasets
- **Rate limit:** 120 req/min per IP

**Response (200):**
```json
{
  "data": {
    "id": "7e4d9f3a-...",
    "filename": "bearing_sensors_v3.csv",
    "dataset_type": "time_series",
    "n_rows": 50000,
    "n_cols": 14,
    "composite_score": 87.4,
    "grade": "Excellent",
    "rank": 1,
    "status": "accepted",
    "upload_date": "2026-06-10T10:05:00Z",
    "scored_at": "2026-06-10T10:05:22Z",
    "download_count": 23,
    "report": {
      "sub_scores": {
        "completeness":         { "score": 95.0, "weight": 0.15, "detail": "...", "severity": "ok" },
        "class_balance":        { "score": 88.0, "weight": 0.10, "detail": "...", "severity": "ok" },
        "label_quality":        { "score": 91.0, "weight": 0.12, "detail": "...", "severity": "ok" },
        "duplicates":           { "score": 100.0,"weight": 0.08, "detail": "...", "severity": "ok" },
        "outliers":             { "score": 80.0, "weight": 0.08, "detail": "...", "severity": "info" },
        "schema_validity":      { "score": 95.0, "weight": 0.08, "detail": "...", "severity": "ok" },
        "leakage":              { "score": 92.0, "weight": 0.12, "detail": "...", "severity": "ok" },
        "temporal_coverage":    { "score": 78.0, "weight": 0.10, "detail": "...", "severity": "warning" },
        "feature_redundancy":   { "score": 85.0, "weight": 0.07, "detail": "...", "severity": "ok" },
        "distribution_sanity":  { "score": 90.0, "weight": 0.08, "detail": "...", "severity": "ok" },
        "domain_pdm":           { "score": 83.0, "weight": 0.10, "detail": "...", "severity": "info", "raw": {...} }
      },
      "readiness": {
        "readiness_pct": 78.0,
        "baseline_auc": 0.892,
        "target_auc": 0.80,
        "penalties": { "label_noise": 0.02, "imbalance": 0.05, "temporal_gaps": 0.01 }
      },
      "review": "Your dataset shows excellent completeness...",
      "improvements": [
        {
          "dimension": "temporal_coverage",
          "priority": "P1",
          "title": "Fill Temporal Gaps",
          "description": "...",
          "estimated_score_delta": 3.2,
          "effort": "high"
        }
      ],
      "preview": {
        "columns": [ { "name": "timestamp", "dtype": "object", "null_pct": 0.0 } ],
        "sample_rows": [ {} ]
      },
      "reasoning_trace": [ "STEP 1: Profiling...", "..." ]
    }
  },
  "meta": {}
}
```

Note: `report` is the full `AuditResult` JSON (stored as JSONB in `audit_reports.full_report`) merged with summary fields from `datasets`.

---

#### GET /api/datasets/{id}/file

Get a signed download URL for the raw dataset file.

- **Auth:** Optional for `accepted` datasets
- **Implementation:** Do NOT stream the file through the API. Generate a Supabase Storage signed URL (1h TTL) and return it. This avoids proxying large files through the API container and works within HF Space memory limits.
- **Side effect:** Increments `download_count` (best-effort, no blocking)

**Response (200):**
```json
{
  "data": {
    "download_url": "https://{supabase-project}.supabase.co/storage/v1/object/sign/datasets/...",
    "expires_at": "2026-06-10T11:05:00Z",
    "filename": "bearing_sensors_v3.csv",
    "size_bytes": 2340128
  },
  "meta": {}
}
```

---

#### GET /api/me/quota

Return the authenticated user's upload quota status.

- **Auth:** Required

**Response (200):**
```json
{
  "data": {
    "used": 3,
    "limit": 5,
    "remaining": 2,
    "datasets": [
      {
        "id": "7e4d9f3a-...",
        "filename": "bearing_sensors_v3.csv",
        "status": "accepted",
        "composite_score": 87.4,
        "upload_date": "2026-06-10T10:05:00Z"
      }
    ]
  },
  "meta": {}
}
```

Note: `used` counts `processing` + `accepted` only. `rejected` datasets do not count.

---

#### DELETE /api/datasets/{id}

Soft-delete a dataset (owner only).

- **Auth:** Required (owner only)
- **Behaviour:** Sets `status='deleted'`, `deleted_at=now()`. Removes file from Supabase Storage. Triggers rank recalculation. Decrements effective `used` count.
- **Idempotent:** DELETE on an already-deleted dataset returns 204 without error.

**Response (204):** No body.

---

### 3.3 Auth Middleware (FastAPI Dependency)

```python
# middleware/auth.py
from fastapi import Depends, HTTPException, Header
from supabase import create_client
import jwt as pyjwt  # PyJWT

SUPABASE_JWT_SECRET = os.environ["SUPABASE_JWT_SECRET"]  # from Supabase dashboard → Settings → API

async def get_current_user(
    authorization: Optional[str] = Header(default=None)
) -> Optional[UserContext]:
    """
    Returns UserContext if valid JWT, None if no token (allows public routes).
    Raises 401 if token present but invalid.
    """
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.split(" ", 1)[1]
    try:
        payload = pyjwt.decode(
            token,
            SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated",
        )
        return UserContext(
            user_id=payload["sub"],
            email=payload.get("email"),
            role=payload.get("role", "authenticated"),
        )
    except pyjwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail_error_code="unauthorized", msg="Token expired")
    except pyjwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail_error_code="unauthorized", msg="Invalid token")

async def require_auth(
    user: Optional[UserContext] = Depends(get_current_user)
) -> UserContext:
    if user is None:
        raise HTTPException(status_code=401, ...)
    return user
```

### 3.4 Rate Limit Headers

All responses include:

```
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 7
X-RateLimit-Reset: 1749550800
Retry-After: 3600   (only on 429)
```

Implementation: `slowapi` library (FastAPI-native, drop-in Starlette middleware). Keyed by `user_id` when authenticated, by IP otherwise.

---

## 4. Migration Plan

### 4.1 Phase Map (by criticality)

| Step | Action | Demo-critical | Risk | When |
|---|---|---|---|---|
| **M1** | Create Supabase project, run DDL, enable RLS | No (local still works) | Low | Day 0 |
| **M2** | Add Supabase env vars to HF Space + `.env` | No | Low | Day 0 |
| **M3** | Wire Supabase Auth (JWT middleware) — new uploads require auth | YES — breaks public upload | Medium | Day 1, feature-flagged |
| **M4** | Migrate storage: new uploads → Supabase Storage instead of `FILES_DIR` | YES | Low | Day 1, alongside M3 |
| **M5** | Migrate persistence: new audit results INSERT to Postgres instead of JSONL | YES | Low | Day 1 |
| **M6** | Backfill existing JSONL records to Postgres (one-off script) | Yes — board continuity | Medium | Day 1, after M5 |
| **M7** | Switch board endpoint to Postgres query (remove JSONL reader) | YES | Low | After M6 verified |
| **M8** | Add async job queue (BackgroundTasks → asyncio.Queue with 3 workers) | Nice-to-have | Low | Day 2 |
| **M9** | Add quota enforcement + `/api/me/quota` endpoint | Nice-to-have | Low | Day 2 |
| **M10** | Add relevance gate | Nice-to-have | Low | Day 2 |
| **M11** | Signed URL for downloads (replace FileResponse with signed URL redirect) | Nice-to-have | Low | Day 2 |

### 4.2 Demo-Continuity Constraints

1. **Do not break the existing `/api/audit` endpoint** — replace persistence backend but keep the same request/response shape. Frontend sees no change.
2. **JSONL backfill (M6)** — run `scripts/migrate_jsonl_to_supabase.py` after M5 is deployed. This script reads `api/data/audits.jsonl`, writes each record to `datasets` + `audit_reports` with `owner_id = EDITH_LEGACY_USER_ID` (a seeded service user). Legacy downloads get storage paths pointing to new Storage bucket after files are copied.
3. **Feature flag for auth** — add `EDITH_AUTH_REQUIRED=true|false` env var. Default `false` during migration. Flip to `true` after demo sign-off. This lets the board remain publicly visible while auth is being wired.
4. **HF Space sleep mitigation** — add UptimeRobot monitor on `/api/health` with 5-min ping interval. Prevents the 30-min sleep timeout during judging window (15 Jun).

### 4.3 Backfill Script Sketch

```python
# scripts/migrate_jsonl_to_supabase.py
# Run once: python scripts/migrate_jsonl_to_supabase.py

import json, uuid, os
from pathlib import Path
from supabase import create_client

sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"])

LEGACY_USER_ID = os.environ["EDITH_LEGACY_USER_ID"]  # pre-seeded auth.users record
JSONL_PATH = Path("api/data/audits.jsonl")
FILES_DIR  = Path("api/data/files")

with open(JSONL_PATH) as f:
    for line in f:
        s = json.loads(line.strip())
        dataset_id = str(uuid.uuid4())
        # Upload file to Storage
        ext = Path(s["filename"]).suffix or ".csv"
        file_path = next(FILES_DIR.glob(f"{s['audit_id']}*"), None)
        storage_path = f"{LEGACY_USER_ID}/{dataset_id}/{s['filename']}"
        if file_path and file_path.is_file():
            sb.storage.from_("datasets").upload(storage_path, file_path.read_bytes())
        # Insert dataset summary row
        sb.table("datasets").insert({
            "id":              dataset_id,
            "owner_id":        LEGACY_USER_ID,
            "filename":        s["filename"],
            "mime_type":       "text/csv",
            "size_bytes":      file_path.stat().st_size if file_path and file_path.is_file() else 0,
            "checksum":        s.get("audit_id", ""),  # audit_id as surrogate; no SHA-256 in JSONL
            "storage_path":    storage_path,
            "n_rows":          s["n_rows"],
            "n_cols":          s["n_cols"],
            "composite_score": s["composite_score"],
            "grade":           s["grade"],
            "status":          "accepted",
            "dataset_type":    s.get("dataset_type", "tabular"),
            "download_count":  s.get("download_count", 0),
            "upload_date":     s["created_at"],
            "scored_at":       s["created_at"],
        }).execute()
        print(f"Migrated: {s['filename']} → {dataset_id}")

# After all rows inserted, compute initial ranks
sb.rpc("recalculate_dataset_ranks", {}).execute()
print("Ranks recalculated.")
```

---

## 5. OpenAPI Spec Excerpt

```yaml
openapi: "3.1.0"
info:
  title: EDITH DataForge API
  version: "2.0.0"

components:
  securitySchemes:
    supabaseJwt:
      type: http
      scheme: bearer
      bearerFormat: JWT

  schemas:
    ErrorEnvelope:
      type: object
      required: [error]
      properties:
        error:
          type: object
          required: [code, message, type]
          properties:
            code:    { type: string, enum: [unauthorized, forbidden, not_found, parse_error, unsupported_file_type, file_too_large, empty_dataset, quota_exceeded, relevance_rejected, duplicate_dataset, job_not_found, server_error] }
            message: { type: string }
            type:    { type: string, enum: [validation, auth, quota, relevance, server] }
            doc_url: { type: string, format: uri }

    DimensionResult:
      type: object
      required: [score, weight, detail, severity]
      properties:
        score:    { type: number, minimum: 0, maximum: 100 }
        weight:   { type: number }
        detail:   { type: string }
        severity: { type: string, enum: [ok, info, warning, critical] }

    DatasetSummary:
      type: object
      properties:
        id:              { type: string, format: uuid }
        filename:        { type: string }
        dataset_type:    { type: string, enum: [tabular, time_series] }
        n_rows:          { type: integer }
        n_cols:          { type: integer }
        composite_score: { type: number }
        grade:           { type: string, enum: [Excellent, Good, Fair, "Needs Work", Poor] }
        rank:            { type: integer, nullable: true }
        download_count:  { type: integer }
        upload_date:     { type: string, format: date-time }
        status:          { type: string, enum: [processing, accepted, rejected, deleted] }
        tags:            { type: array, items: { type: string } }

paths:
  /api/datasets:
    post:
      summary: Upload dataset for analysis
      security: [{ supabaseJwt: [] }]
      requestBody:
        required: true
        content:
          multipart/form-data:
            schema:
              type: object
              required: [file]
              properties:
                file:          { type: string, format: binary }
                label_col:     { type: string }
                timestamp_col: { type: string }
                target_auc:    { type: number, minimum: 0.5, maximum: 1.0, default: 0.80 }
                description:   { type: string, maxLength: 500 }
                tags:          { type: string }
      responses:
        "202":
          description: Accepted for async processing
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    type: object
                    properties:
                      job_id:     { type: string, format: uuid }
                      dataset_id: { type: string, format: uuid }
                      status:     { type: string, enum: [processing] }
                      poll_url:   { type: string }
        "200":
          description: Rejected (relevance gate) or duplicate
        "413": { description: File too large }
        "415": { description: Unsupported file type }
        "422": { description: Parse or validation error }
        "429": { description: Quota exceeded or rate limit }
        "401": { description: Unauthorized }

    get:
      summary: Public leaderboard with pagination
      parameters:
        - { name: limit, in: query, schema: { type: integer, default: 20, minimum: 1, maximum: 100 } }
        - { name: cursor, in: query, schema: { type: string } }
        - { name: sort, in: query, schema: { type: string, enum: [rank, score, upload_date, downloads], default: rank } }
        - { name: dataset_type, in: query, schema: { type: string, enum: [tabular, time_series] } }
        - { name: grade, in: query, schema: { type: string } }
        - { name: min_score, in: query, schema: { type: number } }
        - { name: q, in: query, schema: { type: string } }
        - { name: my_datasets, in: query, schema: { type: boolean, default: false } }
      responses:
        "200":
          content:
            application/json:
              schema:
                type: object
                properties:
                  data: { type: array, items: { $ref: "#/components/schemas/DatasetSummary" } }
                  meta:
                    type: object
                    properties:
                      total:       { type: integer }
                      limit:       { type: integer }
                      next_cursor: { type: string, nullable: true }

  /api/datasets/{id}/file:
    get:
      summary: Get signed download URL
      parameters:
        - { name: id, in: path, required: true, schema: { type: string, format: uuid } }
      responses:
        "200":
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    type: object
                    properties:
                      download_url: { type: string, format: uri }
                      expires_at:   { type: string, format: date-time }
                      filename:     { type: string }
                      size_bytes:   { type: integer }

  /api/me/quota:
    get:
      summary: Get authenticated user's upload quota
      security: [{ supabaseJwt: [] }]
      responses:
        "200":
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    type: object
                    properties:
                      used:      { type: integer }
                      limit:     { type: integer }
                      remaining: { type: integer }
                      datasets:  { type: array, items: { $ref: "#/components/schemas/DatasetSummary" } }
```

---

## 6. Operational Notes

### 6.1 Expected Performance Profile (Hackathon Scale)

| Endpoint | Expected P50 | P99 | Notes |
|---|---|---|---|
| `POST /api/datasets` (initial response) | < 2s | < 5s | Sync: parse + relevance gate + Storage upload. Scorer is async. |
| Background scoring job | 5–30s | 90s | Depends on n_rows × n_cols. LightGBM readiness is the bottleneck for large datasets. |
| `GET /api/datasets` (board) | < 50ms | < 200ms | Postgres query + TTL cache hit. |
| `GET /api/datasets/{id}` (full report) | < 100ms | < 300ms | JSONB read from Postgres. |
| `GET /api/datasets/{id}/file` (signed URL) | < 200ms | < 500ms | Supabase Storage SDK call. |

### 6.2 Alert Thresholds

| Signal | Warning | Critical |
|---|---|---|
| Job queue depth | > 10 queued | > 50 queued |
| Job failure rate | > 5% | > 20% |
| P99 upload latency | > 8s | > 15s |
| Supabase Postgres error rate | > 1% | > 5% |
| HF Space container restarts | > 2/hour | > 10/hour |

### 6.3 Rollback Steps (if Supabase migration goes wrong)

1. Set `EDITH_AUTH_REQUIRED=false` (auth middleware becomes no-op).
2. Set `EDITH_STORAGE_BACKEND=local` (upload handler writes to `FILES_DIR` instead of Supabase Storage).
3. Set `EDITH_PERSISTENCE_BACKEND=jsonl` (persistence writes to `audits.jsonl` instead of Postgres).
4. All three feature flags are checked at import time — no restart needed on HF (push env var → Space reloads).
5. Supabase Postgres DDL is additive (no columns dropped from existing system) — zero rollback needed at DB layer.

### 6.4 Dependencies + External Services

| Service | Role | Failure mode |
|---|---|---|
| Supabase Auth | JWT verification | If down: all authenticated routes return 503. Public board still served from Postgres. |
| Supabase Postgres | Primary persistence | If down: entire API returns 503. Mitigation: add `tenacity` retry (3×, 500ms backoff) on DB connection. |
| Supabase Storage | File storage | If down: upload fails with `server_error`. Downloads fail gracefully (404 with message). |
| Claude Max subscription (OAuth) | LLM review rewrite | Non-critical path. Falls back to deterministic template on any failure. |
| HF Space container | API host | If sleeping: first request takes 30s wake-up. UptimeRobot ping prevents sleep during judging. |

### 6.5 Security Considerations (hand-off to `security-engineer-agent`)

Items that warrant a full security review before production:
- Supabase RLS policy audit (no policy bypass via service-role key in client-callable paths)
- File upload sandbox: ensure no path traversal via `filename`, no SSRF via uploaded JSON content
- Rate limit bypass: verify IP extraction via `X-Forwarded-For` behind HF Space / Vercel proxy
- JWT algorithm confusion: pin `algorithms=["HS256"]` in PyJWT decode (done in middleware above)
- Signed URL TTL: 1h is appropriate; reduce to 15min for production

---

*Architecture authored for EDITH DataForge v2 — Tata Steel R2 Hackathon, 15 Jun 2026 deadline.*
