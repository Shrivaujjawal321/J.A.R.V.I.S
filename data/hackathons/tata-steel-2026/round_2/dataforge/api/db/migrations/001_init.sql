-- ============================================================
-- EDITH DataForge v2 — Forward migration 001_init
-- Applied idempotently via psycopg2 (CREATE IF NOT EXISTS,
-- DROP/CREATE on policies which are not IF NOT EXISTS in PG17)
-- ============================================================

-- Extension (Supabase enables pgcrypto by default, but be safe)
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================
-- ENUM types (idempotent via DO block)
-- ============================================================
DO $$ BEGIN
    CREATE TYPE public.dataset_status AS ENUM ('processing','accepted','rejected','deleted');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE public.dataset_type_enum AS ENUM ('tabular','time_series');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE public.grade_enum AS ENUM ('Excellent','Good','Fair','Needs Work','Poor');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE public.job_status AS ENUM ('queued','running','completed','failed');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE public.audit_event_type AS ENUM (
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
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- ============================================================
-- users: EDITH-specific profile, linked to auth.users
-- ============================================================
CREATE TABLE IF NOT EXISTS public.users (
    id            UUID        PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email         TEXT,
    display_name  TEXT,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS users_email_idx ON public.users (email);

-- ============================================================
-- datasets
-- ============================================================
CREATE TABLE IF NOT EXISTS public.datasets (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id            UUID        NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

    -- File metadata
    filename            TEXT        NOT NULL,
    mime_type           TEXT        NOT NULL DEFAULT 'text/csv',
    size_bytes          BIGINT      NOT NULL DEFAULT 0,
    checksum            CHAR(64)    NOT NULL,
    storage_path        TEXT,

    -- Structural metadata
    n_rows              INT,
    n_cols              INT,
    dataset_type        public.dataset_type_enum,
    tags                TEXT[]      DEFAULT '{}',
    description         TEXT,

    -- Scoring outputs
    composite_score     NUMERIC(6,2),
    grade               public.grade_enum,
    rank                INT,
    relevance_score     NUMERIC(6,4),
    overall_score       NUMERIC(6,2),

    -- Status
    status              public.dataset_status NOT NULL DEFAULT 'processing',
    rejection_reason    TEXT,

    -- Timestamps
    upload_date         TIMESTAMPTZ NOT NULL DEFAULT now(),
    scored_at           TIMESTAMPTZ,
    deleted_at          TIMESTAMPTZ,

    -- Download tracking
    download_count      INT NOT NULL DEFAULT 0,

    CONSTRAINT chk_deleted_at CHECK (
        (status = 'deleted' AND deleted_at IS NOT NULL)
        OR (status != 'deleted' AND deleted_at IS NULL)
    )
);

CREATE INDEX IF NOT EXISTS datasets_owner_idx     ON public.datasets (owner_id, status);
CREATE INDEX IF NOT EXISTS datasets_board_idx     ON public.datasets (composite_score DESC NULLS LAST)
    WHERE status = 'accepted';
CREATE INDEX IF NOT EXISTS datasets_checksum_idx  ON public.datasets (checksum, owner_id);
CREATE INDEX IF NOT EXISTS datasets_rank_idx      ON public.datasets (rank ASC NULLS LAST)
    WHERE status = 'accepted';
CREATE INDEX IF NOT EXISTS datasets_upload_idx    ON public.datasets (upload_date DESC);

-- ============================================================
-- audit_reports: 1:1 with datasets, full scoring result
-- ============================================================
CREATE TABLE IF NOT EXISTS public.audit_reports (
    id                          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    dataset_id                  UUID        NOT NULL UNIQUE REFERENCES public.datasets(id) ON DELETE CASCADE,

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
    score_domain_pdm            NUMERIC(6,2),

    readiness_pct               NUMERIC(5,2),
    baseline_auc                NUMERIC(5,4),

    full_report                 JSONB       NOT NULL,

    created_at                  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS audit_reports_dataset_idx ON public.audit_reports (dataset_id);

-- ============================================================
-- jobs: async scoring job tracking
-- ============================================================
CREATE TABLE IF NOT EXISTS public.jobs (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    dataset_id      UUID        NOT NULL REFERENCES public.datasets(id) ON DELETE CASCADE,
    owner_id        UUID        NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

    status          public.job_status NOT NULL DEFAULT 'queued',
    queued_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    started_at      TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,

    error_code      TEXT,
    error_detail    TEXT,
    attempt         SMALLINT    NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS jobs_dataset_idx ON public.jobs (dataset_id);
CREATE INDEX IF NOT EXISTS jobs_status_idx  ON public.jobs (status) WHERE status IN ('queued','running');
CREATE INDEX IF NOT EXISTS jobs_owner_idx   ON public.jobs (owner_id, queued_at DESC);

-- ============================================================
-- upload_audit_log: append-only security audit trail
-- ============================================================
CREATE TABLE IF NOT EXISTS public.upload_audit_log (
    id              BIGSERIAL   PRIMARY KEY,
    event_type      public.audit_event_type NOT NULL,
    owner_id        UUID,
    dataset_id      UUID,
    ip_address      INET,
    user_agent      TEXT,
    detail          JSONB,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS audit_log_owner_idx   ON public.upload_audit_log (owner_id, created_at DESC);
CREATE INDEX IF NOT EXISTS audit_log_event_idx   ON public.upload_audit_log (event_type, created_at DESC);
CREATE INDEX IF NOT EXISTS audit_log_dataset_idx ON public.upload_audit_log (dataset_id)
    WHERE dataset_id IS NOT NULL;

-- ============================================================
-- Rank recalculation function
-- ============================================================
CREATE OR REPLACE FUNCTION public.recalculate_dataset_ranks()
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    UPDATE public.datasets AS d
    SET    rank = sub.new_rank
    FROM (
        SELECT id,
               RANK() OVER (ORDER BY overall_score DESC NULLS LAST, composite_score DESC NULLS LAST) AS new_rank
        FROM   public.datasets
        WHERE  status = 'accepted'
    ) sub
    WHERE d.id = sub.id
      AND d.status = 'accepted';
END;
$$;

-- ============================================================
-- Quota-check function (returns active dataset count for owner)
-- ============================================================
CREATE OR REPLACE FUNCTION public.get_user_quota(p_owner_id UUID)
RETURNS INT
LANGUAGE sql
SECURITY DEFINER
STABLE
AS $$
    SELECT COUNT(*)::INT
    FROM   public.datasets
    WHERE  owner_id = p_owner_id
      AND  status   IN ('processing', 'accepted');
$$;

-- ============================================================
-- RLS: Enable on all tables
-- ============================================================
ALTER TABLE public.users             ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.datasets          ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.audit_reports     ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.jobs              ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.upload_audit_log  ENABLE ROW LEVEL SECURITY;

-- ============================================================
-- RLS Policies — drop then recreate (idempotent)
-- ============================================================

-- ── users ──────────────────────────────────────────────────
DROP POLICY IF EXISTS "users_self_rw"          ON public.users;
CREATE POLICY "users_self_rw"
ON public.users FOR ALL
USING  (auth.uid() = id)
WITH CHECK (auth.uid() = id);

-- ── datasets ───────────────────────────────────────────────
DROP POLICY IF EXISTS "datasets_public_board"  ON public.datasets;
CREATE POLICY "datasets_public_board"
ON public.datasets FOR SELECT
USING (status = 'accepted');

DROP POLICY IF EXISTS "datasets_owner_all"     ON public.datasets;
CREATE POLICY "datasets_owner_all"
ON public.datasets FOR SELECT
USING (auth.uid() = owner_id);

DROP POLICY IF EXISTS "datasets_auth_insert"   ON public.datasets;
CREATE POLICY "datasets_auth_insert"
ON public.datasets FOR INSERT
WITH CHECK (auth.uid() = owner_id);

DROP POLICY IF EXISTS "datasets_owner_update"  ON public.datasets;
CREATE POLICY "datasets_owner_update"
ON public.datasets FOR UPDATE
USING  (auth.uid() = owner_id)
WITH CHECK (auth.uid() = owner_id);

-- ── audit_reports ──────────────────────────────────────────
DROP POLICY IF EXISTS "auditreports_public_accepted" ON public.audit_reports;
CREATE POLICY "auditreports_public_accepted"
ON public.audit_reports FOR SELECT
USING (
    EXISTS (
        SELECT 1 FROM public.datasets d
        WHERE d.id = dataset_id AND d.status = 'accepted'
    )
);

DROP POLICY IF EXISTS "auditreports_owner_read" ON public.audit_reports;
CREATE POLICY "auditreports_owner_read"
ON public.audit_reports FOR SELECT
USING (
    EXISTS (
        SELECT 1 FROM public.datasets d
        WHERE d.id = dataset_id AND d.owner_id = auth.uid()
    )
);

-- ── jobs ───────────────────────────────────────────────────
DROP POLICY IF EXISTS "jobs_owner_read"        ON public.jobs;
CREATE POLICY "jobs_owner_read"
ON public.jobs FOR SELECT
USING (auth.uid() = owner_id);

-- ── upload_audit_log ───────────────────────────────────────
DROP POLICY IF EXISTS "auditlog_deny_user"     ON public.upload_audit_log;
CREATE POLICY "auditlog_deny_user"
ON public.upload_audit_log FOR SELECT
USING (false);

-- ============================================================
-- Rollback (run manually if needed):
-- DROP FUNCTION IF EXISTS public.get_user_quota(UUID);
-- DROP FUNCTION IF EXISTS public.recalculate_dataset_ranks();
-- DROP TABLE IF EXISTS public.upload_audit_log CASCADE;
-- DROP TABLE IF EXISTS public.jobs CASCADE;
-- DROP TABLE IF EXISTS public.audit_reports CASCADE;
-- DROP TABLE IF EXISTS public.datasets CASCADE;
-- DROP TABLE IF EXISTS public.users CASCADE;
-- DROP TYPE IF EXISTS public.audit_event_type;
-- DROP TYPE IF EXISTS public.job_status;
-- DROP TYPE IF EXISTS public.grade_enum;
-- DROP TYPE IF EXISTS public.dataset_type_enum;
-- DROP TYPE IF EXISTS public.dataset_status;
-- ============================================================
