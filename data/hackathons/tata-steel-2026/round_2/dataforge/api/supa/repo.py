"""
supa/repo.py — Postgres persistence layer for EDITH DataForge.

All writes use the service-role psycopg2 pool (bypasses RLS since the API
server is a trusted backend). Board reads also go through the pool so we
can use typed queries and cursor-based pagination easily.

Key design choices:
  - psycopg2 ThreadedConnectionPool (shared, lazily initialised)
  - Named placeholders via %s positional params (psycopg2 style)
  - Every function returns typed dicts / None; no ORM
  - Quota check uses the DB function get_user_quota() for atomicity
"""
from __future__ import annotations

import base64
import hashlib
import json
import uuid as _uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from psycopg2.extras import RealDictCursor, Json

from .client import pg_conn


# ── helpers ───────────────────────────────────────────────────────────────────
def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _encode_cursor(data: dict) -> str:
    return base64.urlsafe_b64encode(json.dumps(data).encode()).decode()


def _decode_cursor(cursor: str) -> dict:
    try:
        return json.loads(base64.urlsafe_b64decode(cursor.encode()).decode())
    except Exception:
        return {}


# ── users ─────────────────────────────────────────────────────────────────────
def upsert_user(user_id: str, email: Optional[str], display_name: Optional[str] = None) -> None:
    """
    Upsert a user profile row (called after JWT verify on first upload).
    """
    with pg_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO public.users (id, email, display_name, updated_at)
            VALUES (%s, %s, %s, now())
            ON CONFLICT (id) DO UPDATE
                SET email        = EXCLUDED.email,
                    display_name = COALESCE(EXCLUDED.display_name, public.users.display_name),
                    updated_at   = now()
            """,
            (user_id, email, display_name),
        )


# ── quota ─────────────────────────────────────────────────────────────────────
MAX_DATASETS_PER_USER = 5


def get_user_quota_used(owner_id: str) -> int:
    """Return count of active (processing + accepted) datasets for this owner."""
    with pg_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT public.get_user_quota(%s)", (owner_id,))
        row = cur.fetchone()
        return row[0] if row else 0


# ── checksum dedup ────────────────────────────────────────────────────────────
def find_by_checksum(checksum: str, owner_id: str) -> Optional[Dict]:
    """
    Return existing dataset record if same file was already uploaded by this owner.
    Matches on checksum + owner_id, excluding deleted/rejected.
    """
    with pg_conn() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(
            """
            SELECT id, filename, status, composite_score, overall_score, rank, upload_date
            FROM   public.datasets
            WHERE  checksum  = %s
              AND  owner_id  = %s
              AND  status    NOT IN ('rejected', 'deleted')
            LIMIT 1
            """,
            (checksum, owner_id),
        )
        row = cur.fetchone()
        return dict(row) if row else None


# ── datasets ──────────────────────────────────────────────────────────────────
def insert_dataset(
    owner_id: str,
    filename: str,
    mime_type: str,
    size_bytes: int,
    checksum: str,
    n_rows: int,
    n_cols: int,
    dataset_type: str,
    tags: List[str],
    description: Optional[str],
    storage_path: Optional[str],
    status: str = "processing",
    rejection_reason: Optional[str] = None,
    composite_score: Optional[float] = None,
    grade: Optional[str] = None,
    relevance_score: Optional[float] = None,
    overall_score: Optional[float] = None,
    dataset_id: Optional[str] = None,
) -> str:
    """Insert a new dataset row. Returns the row UUID.

    Pass an explicit `dataset_id` so the caller's id stays consistent across
    the dataset row, its storage path, the jobs FK, and the upload buffer.
    Without this, the job INSERT violated jobs_dataset_id_fkey (datasets row
    had a different auto-generated id) and scoring never ran.
    """
    dataset_id = dataset_id or str(_uuid.uuid4())
    with pg_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO public.datasets (
                id, owner_id, filename, mime_type, size_bytes, checksum,
                n_rows, n_cols, dataset_type, tags, description,
                storage_path, status, rejection_reason,
                composite_score, grade, relevance_score, overall_score,
                upload_date
            ) VALUES (
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s, %s,
                now()
            )
            """,
            (
                dataset_id, owner_id, filename, mime_type, size_bytes, checksum,
                n_rows, n_cols, dataset_type, tags, description,
                storage_path, status, rejection_reason,
                composite_score, grade, relevance_score, overall_score,
            ),
        )
    return dataset_id


def update_dataset_scored(
    dataset_id: str,
    composite_score: float,
    grade: str,
    overall_score: float,
    relevance_score: float,
    status: str = "accepted",
) -> None:
    """Update a dataset row after background scoring completes."""
    with pg_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE public.datasets
            SET composite_score = %s,
                grade           = %s,
                overall_score   = %s,
                relevance_score = %s,
                status          = %s,
                scored_at       = now()
            WHERE id = %s
            """,
            (composite_score, grade, overall_score, relevance_score, status, dataset_id),
        )


def soft_delete_dataset(dataset_id: str, owner_id: str) -> bool:
    """
    Soft-delete: set status='deleted', deleted_at=now().
    Returns True if row was found and updated, False if not found/forbidden.
    """
    with pg_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE public.datasets
            SET status     = 'deleted',
                deleted_at = now()
            WHERE id = %s AND owner_id = %s
              AND status != 'deleted'
            """,
            (dataset_id, owner_id),
        )
        return cur.rowcount > 0


def get_dataset(dataset_id: str) -> Optional[Dict]:
    """Fetch a single dataset row by ID (any status)."""
    with pg_conn() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(
            "SELECT * FROM public.datasets WHERE id = %s",
            (dataset_id,),
        )
        row = cur.fetchone()
        return dict(row) if row else None


def get_dataset_with_report(dataset_id: str) -> Optional[Dict]:
    """Fetch dataset + audit report joined."""
    with pg_conn() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(
            """
            SELECT d.*,
                   ar.full_report,
                   ar.readiness_pct,
                   ar.baseline_auc
            FROM   public.datasets d
            LEFT JOIN public.audit_reports ar ON ar.dataset_id = d.id
            WHERE  d.id = %s
            """,
            (dataset_id,),
        )
        row = cur.fetchone()
        return dict(row) if row else None


# ── board / list ──────────────────────────────────────────────────────────────
def list_datasets_board(
    limit: int = 20,
    cursor: Optional[str] = None,
    sort: str = "rank",
    order: str = "asc",
    dataset_type: Optional[str] = None,
    grade: Optional[str] = None,
    min_score: Optional[float] = None,
    q: Optional[str] = None,
    my_datasets: bool = False,
    owner_id: Optional[str] = None,
) -> Dict:
    """
    Public leaderboard query with cursor-based pagination.
    Returns {"data": [...], "total": int, "next_cursor": str|None}
    """
    # Build sort expression
    sort_col_map = {
        "rank":        "rank",
        "score":       "overall_score",
        "upload_date": "upload_date",
        "downloads":   "download_count",
    }
    sort_col = sort_col_map.get(sort, "rank")
    sort_dir = "ASC" if order.lower() == "asc" else "DESC"
    nulls = "NULLS LAST"

    # Base filter
    conditions: List[str] = []
    params: List[Any] = []

    if my_datasets and owner_id:
        # Authenticated: show all own datasets (any status except deleted)
        conditions.append("owner_id = %s AND status != 'deleted'")
        params.append(owner_id)
    else:
        # Public board: accepted only
        conditions.append("status = 'accepted'")

    if dataset_type:
        conditions.append("dataset_type = %s")
        params.append(dataset_type)

    if grade:
        conditions.append("grade = %s")
        params.append(grade)

    if min_score is not None:
        conditions.append("COALESCE(overall_score, composite_score) >= %s")
        params.append(min_score)

    if q:
        conditions.append("filename ILIKE %s")
        params.append(f"%{q}%")

    # Cursor decoding
    if cursor:
        decoded = _decode_cursor(cursor)
        last_val = decoded.get("val")
        last_id = decoded.get("id")
        if last_val is not None and last_id:
            if sort_dir == "ASC":
                conditions.append(
                    f"({sort_col} > %s OR ({sort_col} = %s AND id > %s))"
                )
                params.extend([last_val, last_val, last_id])
            else:
                conditions.append(
                    f"({sort_col} < %s OR ({sort_col} = %s AND id > %s))"
                )
                params.extend([last_val, last_val, last_id])

    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

    with pg_conn() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Count (without cursor filter for pagination meta)
        count_conditions = [c for c in conditions if "cursor" not in c.lower()]
        # Simpler: just re-count without cursor conditions
        count_conds = []
        count_params: List[Any] = []
        if my_datasets and owner_id:
            count_conds.append("owner_id = %s AND status != 'deleted'")
            count_params.append(owner_id)
        else:
            count_conds.append("status = 'accepted'")
        if dataset_type:
            count_conds.append("dataset_type = %s")
            count_params.append(dataset_type)
        if grade:
            count_conds.append("grade = %s")
            count_params.append(grade)
        if min_score is not None:
            count_conds.append("COALESCE(overall_score, composite_score) >= %s")
            count_params.append(min_score)
        if q:
            count_conds.append("filename ILIKE %s")
            count_params.append(f"%{q}%")

        count_where = "WHERE " + " AND ".join(count_conds) if count_conds else ""
        cur.execute(
            f"SELECT COUNT(*) FROM public.datasets {count_where}",
            count_params,
        )
        total = cur.fetchone()["count"]

        # Data query
        query = f"""
            SELECT id, owner_id, filename, dataset_type, n_rows, n_cols,
                   composite_score, overall_score, grade, rank,
                   download_count, upload_date, status, tags, description,
                   size_bytes, relevance_score
            FROM   public.datasets
            {where_clause}
            ORDER  BY {sort_col} {sort_dir} {nulls}, id ASC
            LIMIT  %s
        """
        params.append(limit + 1)  # fetch one extra to detect next page
        cur.execute(query, params)
        rows = [dict(r) for r in cur.fetchall()]

    # Compute next cursor
    has_more = len(rows) > limit
    if has_more:
        rows = rows[:limit]
    next_cursor = None
    if has_more and rows:
        last = rows[-1]
        last_val = last.get(sort_col)
        next_cursor = _encode_cursor({"val": str(last_val) if last_val is not None else None, "id": str(last["id"])})

    return {"data": rows, "total": total, "next_cursor": next_cursor}


# ── audit_reports ─────────────────────────────────────────────────────────────
def insert_audit_report(
    dataset_id: str,
    full_report: dict,
    score_completeness: Optional[float] = None,
    score_class_balance: Optional[float] = None,
    score_label_quality: Optional[float] = None,
    score_duplicates: Optional[float] = None,
    score_outliers: Optional[float] = None,
    score_schema_validity: Optional[float] = None,
    score_leakage: Optional[float] = None,
    score_temporal_coverage: Optional[float] = None,
    score_feature_redundancy: Optional[float] = None,
    score_distribution_sanity: Optional[float] = None,
    score_domain_pdm: Optional[float] = None,
    readiness_pct: Optional[float] = None,
    baseline_auc: Optional[float] = None,
) -> str:
    """Insert a full audit report. Returns the new audit_report UUID."""
    report_id = str(_uuid.uuid4())
    with pg_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO public.audit_reports (
                id, dataset_id,
                score_completeness, score_class_balance, score_label_quality,
                score_duplicates, score_outliers, score_schema_validity,
                score_leakage, score_temporal_coverage, score_feature_redundancy,
                score_distribution_sanity, score_domain_pdm,
                readiness_pct, baseline_auc, full_report
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (dataset_id) DO UPDATE
                SET full_report = EXCLUDED.full_report,
                    score_completeness = EXCLUDED.score_completeness,
                    score_class_balance = EXCLUDED.score_class_balance,
                    score_label_quality = EXCLUDED.score_label_quality,
                    score_duplicates = EXCLUDED.score_duplicates,
                    score_outliers = EXCLUDED.score_outliers,
                    score_schema_validity = EXCLUDED.score_schema_validity,
                    score_leakage = EXCLUDED.score_leakage,
                    score_temporal_coverage = EXCLUDED.score_temporal_coverage,
                    score_feature_redundancy = EXCLUDED.score_feature_redundancy,
                    score_distribution_sanity = EXCLUDED.score_distribution_sanity,
                    score_domain_pdm = EXCLUDED.score_domain_pdm,
                    readiness_pct = EXCLUDED.readiness_pct,
                    baseline_auc = EXCLUDED.baseline_auc
            """,
            (
                report_id, dataset_id,
                score_completeness, score_class_balance, score_label_quality,
                score_duplicates, score_outliers, score_schema_validity,
                score_leakage, score_temporal_coverage, score_feature_redundancy,
                score_distribution_sanity, score_domain_pdm,
                readiness_pct, baseline_auc, Json(full_report),
            ),
        )
    return report_id


# ── jobs ──────────────────────────────────────────────────────────────────────
def insert_job(dataset_id: str, owner_id: str) -> str:
    """Insert a queued scoring job. Returns job UUID."""
    job_id = str(_uuid.uuid4())
    with pg_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO public.jobs (id, dataset_id, owner_id, status, queued_at)
            VALUES (%s, %s, %s, 'queued', now())
            """,
            (job_id, dataset_id, owner_id),
        )
    return job_id


def update_job(job_id: str, status: str, error_code: Optional[str] = None, error_detail: Optional[str] = None) -> None:
    """Update job status. Sets started_at / completed_at appropriately."""
    with pg_conn() as conn:
        cur = conn.cursor()
        if status == "running":
            cur.execute(
                "UPDATE public.jobs SET status=%s, started_at=now(), attempt=attempt+1 WHERE id=%s",
                (status, job_id),
            )
        elif status in ("completed", "failed"):
            cur.execute(
                """
                UPDATE public.jobs
                SET status=%s, completed_at=now(), error_code=%s, error_detail=%s
                WHERE id=%s
                """,
                (status, error_code, error_detail, job_id),
            )
        else:
            cur.execute("UPDATE public.jobs SET status=%s WHERE id=%s", (status, job_id))


def get_job(job_id: str, owner_id: Optional[str] = None) -> Optional[Dict]:
    """Fetch a job record. If owner_id provided, restricts to that owner."""
    with pg_conn() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        if owner_id:
            cur.execute(
                "SELECT * FROM public.jobs WHERE id=%s AND owner_id=%s",
                (job_id, owner_id),
            )
        else:
            cur.execute("SELECT * FROM public.jobs WHERE id=%s", (job_id,))
        row = cur.fetchone()
        return dict(row) if row else None


def get_orphaned_jobs() -> List[Dict]:
    """Return queued/running jobs for re-queue on startup."""
    with pg_conn() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(
            "SELECT * FROM public.jobs WHERE status IN ('queued','running') ORDER BY queued_at ASC"
        )
        return [dict(r) for r in cur.fetchall()]


# ── audit log ─────────────────────────────────────────────────────────────────
def log_audit_event(
    event_type: str,
    owner_id: Optional[str] = None,
    dataset_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    detail: Optional[dict] = None,
) -> None:
    """Append an audit event. Never blocks main flow (best-effort)."""
    try:
        with pg_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO public.upload_audit_log
                    (event_type, owner_id, dataset_id, ip_address, user_agent, detail)
                VALUES (%s, %s, %s, %s::inet, %s, %s)
                """,
                (
                    event_type,
                    owner_id,
                    dataset_id,
                    ip_address,
                    user_agent,
                    Json(detail) if detail else None,
                ),
            )
    except Exception:
        pass  # audit log failure must never crash the main request


# ── rank recalculation ────────────────────────────────────────────────────────
def recalculate_ranks() -> None:
    """Call the DB function to recompute global leaderboard ranks."""
    with pg_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT public.recalculate_dataset_ranks()")


# ── quota datasets list (for /api/me/quota) ───────────────────────────────────
def get_owner_datasets(owner_id: str) -> List[Dict]:
    """Return all non-deleted datasets for this owner (for quota endpoint)."""
    with pg_conn() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(
            """
            SELECT id, filename, status, composite_score, overall_score,
                   rank, upload_date, dataset_type, grade
            FROM   public.datasets
            WHERE  owner_id = %s AND status != 'deleted'
            ORDER  BY upload_date DESC
            """,
            (owner_id,),
        )
        return [dict(r) for r in cur.fetchall()]
