"""
DataForge API — Dataset Quality Scoring for Industrial/Steel/Predictive-Maintenance Data
v2: Relevance gate + ranking + security hardening (01/02/03 architecture docs).
v2.1: Supabase auth + Postgres persistence + private Storage bucket.

Port: 8011 (local dev)

Feature flags (env vars in .env — all default to local so live demo never breaks):
  EDITH_AUTH_REQUIRED=0        0=allow anon (back-compat), 1=enforce JWT
  EDITH_STORAGE_BACKEND=local  "local" | "supabase"
  EDITH_PERSISTENCE_BACKEND=local "local" | "supabase"

New endpoints added in v2.1 (Supabase-backed, always available):
  POST /api/datasets          — auth + quota + score + persist (replaces /api/audit for new uploads)
  GET  /api/datasets          — leaderboard from Postgres (cursor-paginated, filters, search)
  GET  /api/datasets/{id}     — full audit report from Postgres
  GET  /api/datasets/{id}/file — signed URL from Supabase Storage
  GET  /api/me/quota          — authenticated user quota (used/remaining/max=5)
  DELETE /api/datasets/{id}   — owner-only soft-delete

Legacy endpoints kept for back-compat:
  POST /api/audit             — original JSONL-backed audit (unchanged)
  GET  /api/datasets (old)    — now superseded by new GET /api/datasets above

Run:
  /home/ujjwal/Documents/J.A.R.V.I.S./.venv/bin/uvicorn main:app --port 8011 --reload
"""

from __future__ import annotations
import hashlib
import io
import json
import os
import re
import time
import uuid as _uuid_mod
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, File, Form, HTTPException, Query, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

# Load .env before any supa imports (they read os.environ at import time)
load_dotenv(Path(__file__).parent / ".env")

from scorer.agent import run_audit
from scorer.models import AuditResult, AuditSummary, RelevanceResult, RankingResult
from scorer.relevance.gate import score_dataset as relevance_score_dataset
from scorer.relevance.embeddings import load_embeddings_model, precompute_query_embeddings
from scorer.ranking.factors import compute_feature_richness, compute_ps_alignment
from scorer.ranking.overall import compute_overall_score
from scorer.ranking.leaderboard import assign_ranks, recompute_ranks_jsonl

# Supabase integration layer (lazy — only imported when flags are set)
from supa.auth import UserContext, get_current_user, require_user, ANONYMOUS_USER
import supa.repo as repo
import supa.storage as storage_supa
from supa.client import pg_conn as _pg_conn

# ---------------------------------------------------------------------------
# Feature flags  (re-read from env so dotenv values take effect)
# ---------------------------------------------------------------------------
AUTH_REQUIRED = os.environ.get("EDITH_AUTH_REQUIRED", "0").lower() in ("1", "true", "yes")
STORAGE_BACKEND = os.environ.get("EDITH_STORAGE_BACKEND", "local")  # "local" | "supabase"
PERSISTENCE_BACKEND = os.environ.get("EDITH_PERSISTENCE_BACKEND", "local")  # "local" | "supabase"

# ---------------------------------------------------------------------------
# File-type validation constants
# ---------------------------------------------------------------------------
MAX_BYTES = 50 * 1024 * 1024  # 50 MB hard cap
MAX_ROWS = 200_000
MAX_COLS = 2_000
ZIP_BOMB_RATIO = 100
ZIP_BOMB_MAX_UNCOMPRESSED = 500 * 1024 * 1024  # 500 MB

ALLOWED_EXT = {".csv", ".xlsx", ".json"}
# python-magic sniff results considered acceptable per extension
SNIFF_OK: dict = {
    ".csv": {
        "text/plain", "text/csv", "application/csv", "application/octet-stream",
        "application/x-csv", "text/x-csv",
    },
    ".json": {
        "text/plain", "application/json", "application/x-json",
    },
    ".xlsx": {
        "application/zip",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/octet-stream",  # some systems report this for XLSX
    },
}

# ---------------------------------------------------------------------------
# Formula-injection neutralization
# ---------------------------------------------------------------------------
DANGEROUS_PREFIX = ("=", "+", "-", "@", "\t", "\r")


def neutralize_cell(v: object) -> object:
    """Neutralize CSV/Excel formula injection (CWE-1236)."""
    if isinstance(v, str) and v[:1] in DANGEROUS_PREFIX:
        return "'" + v  # force text interpretation in Excel/Sheets
    return v


def sanitize_string(s: Optional[str], max_len: int = 2000) -> Optional[str]:
    """Sanitize user-supplied strings — strip control chars, cap length."""
    if s is None:
        return None
    # Strip null bytes and other dangerous control chars
    s = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", s)
    return s[:max_len]


# ---------------------------------------------------------------------------
# CORS — exact-origin allow-list (not wildcard regex)
# ---------------------------------------------------------------------------
_DEFAULT_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
    "https://dataforge-delta.vercel.app",  # known prod origin
]
_ALLOWED_ORIGINS = [
    o.strip()
    for o in os.environ.get("EDITH_ALLOWED_ORIGINS", ",".join(_DEFAULT_ORIGINS)).split(",")
    if o.strip()
]

# ---------------------------------------------------------------------------
# Rate limiter (slowapi) — in-memory, per-IP
# ---------------------------------------------------------------------------
limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------
app = FastAPI(
    title="E.D.I.T.H DataForge",
    description="Dataset quality scoring for industrial / steel / predictive-maintenance data",
    version="2.0.0",
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_ALLOWED_ORIGINS,
    # No wildcard regex + credentials — exact list only (CWE-942 fix)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Startup — load embeddings once
# ---------------------------------------------------------------------------
@app.on_event("startup")
async def startup_event() -> None:
    load_embeddings_model()
    precompute_query_embeddings()
    # Eagerly test Supabase DB connection if persistence backend is supabase
    if PERSISTENCE_BACKEND == "supabase":
        try:
            from supa.client import get_pool
            get_pool()  # initialises pool, raises if DB unreachable
            print("[startup] Supabase Postgres pool initialised OK")
        except Exception as exc:
            print(f"[startup] WARNING: Supabase Postgres pool failed: {exc}")
    # Re-queue any orphaned jobs from a previous run
    if PERSISTENCE_BACKEND == "supabase":
        try:
            orphans = repo.get_orphaned_jobs()
            if orphans:
                print(f"[startup] Re-queuing {len(orphans)} orphaned jobs")
                for j in orphans:
                    await _job_queue.put(j["id"])
        except Exception as exc:
            print(f"[startup] Orphan re-queue failed: {exc}")


# ---------------------------------------------------------------------------
# Persistence (local JSONL + files — kept for live demo compatibility)
# ---------------------------------------------------------------------------
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)
AUDITS_FILE = DATA_DIR / "audits.jsonl"
FILES_DIR = DATA_DIR / "files"
FILES_DIR.mkdir(exist_ok=True)


def _load_summaries() -> List[AuditSummary]:
    summaries = []
    if not AUDITS_FILE.exists():
        return summaries
    with open(AUDITS_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                summaries.append(AuditSummary(**json.loads(line)))
            except Exception:
                pass
    return summaries


def _append_summary(summary: AuditSummary) -> None:
    with open(AUDITS_FILE, "a") as f:
        f.write(summary.model_dump_json() + "\n")


def _update_summary(audit_id: str, update: dict) -> bool:
    """Rewrite the JSONL file with one record updated."""
    summaries = _load_summaries()
    found = False
    for s in summaries:
        if s.audit_id == audit_id:
            for k, v in update.items():
                setattr(s, k, v)
            found = True
    if found:
        with open(AUDITS_FILE, "w") as f:
            for s in summaries:
                f.write(s.model_dump_json() + "\n")
    return found


# ---------------------------------------------------------------------------
# File validation helpers
# ---------------------------------------------------------------------------

async def _read_capped(upload: UploadFile) -> bytes:
    """
    Stream-read upload, abort at MAX_BYTES (50 MB). Prevents RAM-DoS (CWE-400).
    Replaces the insecure `await file.read()` from v1.
    """
    buf = bytearray()
    total = 0
    while True:
        chunk = await upload.read(1 << 20)  # 1 MB chunks
        if not chunk:
            break
        total += len(chunk)
        if total > MAX_BYTES:
            raise HTTPException(
                status_code=413,
                detail={
                    "error": {
                        "code": "file_too_large",
                        "message": f"File exceeds the 50 MB limit. Upload a smaller dataset.",
                        "type": "validation",
                    }
                },
            )
        buf += chunk
    return bytes(buf)


def _validate_file_type(filename: str, head: bytes) -> str:
    """
    Validate extension + magic-bytes MIME sniff.
    Returns cleaned extension or raises HTTPException 415.
    """
    # Extension allow-list (CWE-434 layer 1)
    ext = os.path.splitext(filename.lower())[1]
    if ext not in ALLOWED_EXT:
        raise HTTPException(
            status_code=415,
            detail={
                "error": {
                    "code": "unsupported_file_type",
                    "message": (
                        f"File type '{ext}' is not allowed. "
                        "Upload CSV, XLSX, or JSON files only."
                    ),
                    "type": "validation",
                }
            },
        )

    # Magic-byte sniff (CWE-434 layer 2)
    try:
        import magic  # python-magic
        sniffed = magic.from_buffer(head, mime=True)
        allowed_mimes = SNIFF_OK.get(ext, set())
        if sniffed not in allowed_mimes:
            # Special case: XLSX is a ZIP — accept "application/zip" as valid
            if ext == ".xlsx" and sniffed == "application/zip":
                pass  # OK — OOXML is packaged as ZIP
            else:
                raise HTTPException(
                    status_code=415,
                    detail={
                        "error": {
                            "code": "unsupported_file_type",
                            "message": (
                                f"File declared as {ext} but content looks like {sniffed}. "
                                "Only genuine CSV, XLSX, and JSON files are accepted."
                            ),
                            "type": "validation",
                        }
                    },
                )
    except HTTPException:
        raise
    except Exception:
        # If python-magic or libmagic unavailable, log and proceed (defensive)
        pass

    return ext


def _zipbomb_check(raw_bytes: bytes, ext: str) -> None:
    """
    Guard against decompression bombs in XLSX/ZIP files (CWE-409).
    """
    if ext != ".xlsx":
        return
    try:
        with zipfile.ZipFile(io.BytesIO(raw_bytes)) as z:
            total_uncompressed = sum(info.file_size for info in z.infolist())
            total_compressed = sum(info.compress_size for info in z.infolist()) or 1
            ratio = total_uncompressed / total_compressed
            if total_uncompressed > ZIP_BOMB_MAX_UNCOMPRESSED or ratio > ZIP_BOMB_RATIO:
                raise HTTPException(
                    status_code=422,
                    detail={
                        "error": {
                            "code": "parse_error",
                            "message": "XLSX file appears to be a decompression bomb. Rejected.",
                            "type": "validation",
                        }
                    },
                )
    except HTTPException:
        raise
    except zipfile.BadZipFile:
        raise HTTPException(
            status_code=422,
            detail={
                "error": {
                    "code": "parse_error",
                    "message": "XLSX file is corrupted or not a valid ZIP/XLSX file.",
                    "type": "validation",
                }
            },
        )
    except Exception:
        pass  # non-fatal — let parser handle malformed file


def _safe_parse(content: bytes, filename: str, ext: str) -> pd.DataFrame:
    """
    Safe, sandboxed-style parse with row/col caps and no formula evaluation.
    No pickle, no parquet, no external URL fetch.
    """
    df: Optional[pd.DataFrame] = None
    try:
        if ext == ".xlsx":
            # openpyxl read_only + data_only = no VBA, no formula eval (CWE-502/94)
            import openpyxl
            wb = openpyxl.load_workbook(
                io.BytesIO(content),
                read_only=True,
                data_only=True,   # cached values, never evaluates formulas
                keep_vba=False,
            )
            ws = wb.active
            if ws is None:
                raise ValueError("XLSX has no active sheet")
            rows = list(ws.iter_rows(values_only=True, max_row=MAX_ROWS + 1))
            wb.close()
            if not rows:
                raise ValueError("XLSX sheet is empty")
            headers = [str(h) if h is not None else f"col_{i}" for i, h in enumerate(rows[0])]
            data_rows = rows[1 : MAX_ROWS + 1]
            df = pd.DataFrame(data_rows, columns=headers)

        elif ext == ".json":
            data = json.loads(content.decode("utf-8", errors="replace"))
            if isinstance(data, list):
                df = pd.DataFrame(data[:MAX_ROWS])
            elif isinstance(data, dict):
                df = pd.DataFrame([data]) if not any(
                    isinstance(v, list) for v in data.values()
                ) else pd.DataFrame(data)
                df = df.head(MAX_ROWS)
            else:
                raise ValueError("JSON must be an array of objects or an object of arrays")

        else:
            # CSV — try common separators; caps applied DURING read (nrows param)
            for sep in [",", ";", "\t", "|"]:
                try:
                    parsed = pd.read_csv(
                        io.BytesIO(content),
                        sep=sep,
                        low_memory=False,
                        nrows=MAX_ROWS,      # cap rows DURING read (not after)
                        on_bad_lines="skip",
                    )
                    if parsed.shape[1] > 1:
                        df = parsed
                        break
                    elif df is None:
                        df = parsed
                except Exception:
                    continue

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=422,
            detail={
                "error": {
                    "code": "parse_error",
                    "message": f"Could not parse file: {type(exc).__name__}. "
                               "Upload a valid CSV, XLSX, or JSON file.",
                    "type": "validation",
                }
            },
        )

    if df is None:
        raise HTTPException(
            status_code=422,
            detail={
                "error": {
                    "code": "parse_error",
                    "message": "Could not parse file. Upload a valid CSV, XLSX, or JSON file.",
                    "type": "validation",
                }
            },
        )

    if df.empty or len(df) == 0:
        raise HTTPException(
            status_code=422,
            detail={
                "error": {
                    "code": "empty_dataset",
                    "message": "Uploaded file is empty.",
                    "type": "validation",
                }
            },
        )

    # Column cap (wide-CSV guard)
    if df.shape[1] > MAX_COLS:
        df = df.iloc[:, :MAX_COLS]

    # Sanitise column names
    df.columns = [str(c).strip() for c in df.columns]

    return df


def _apply_formula_injection_sanitization(df: pd.DataFrame) -> pd.DataFrame:
    """
    Neutralize formula-injection in all string cells (CWE-1236).
    Applied before any response that could re-export or serve cell values.
    """
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].map(neutralize_cell)
    return df


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/api/health")
async def health():
    from scorer.relevance.embeddings import EMBEDDINGS_AVAILABLE
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "embeddings_available": EMBEDDINGS_AVAILABLE,
        "version": "2.0.0",
    }


@app.post("/api/audit", response_model=AuditResult)
@limiter.limit("10/minute")
async def audit_dataset(
    request: Request,  # required by slowapi
    file: UploadFile = File(...),
    label_col: Optional[str] = Form(default=None),
    timestamp_col: Optional[str] = Form(default=None),
    target_auc: float = Form(default=0.80),
):
    """
    Main audit endpoint. Accepts CSV, XLSX, or JSON.
    v2: relevance gate runs BEFORE quality scoring.
    Rejected datasets return score=0, rank=0, status=rejected.
    """
    filename = sanitize_string(file.filename, 255) or "upload"

    # [1] Streamed size cap (CWE-400 fix)
    content = await _read_capped(file)

    # [2] File type validation: ext allow-list + magic-bytes (CWE-434)
    ext = _validate_file_type(filename, content[:8192])

    # [3] Zip-bomb guard for XLSX (CWE-409)
    _zipbomb_check(content, ext)

    # [4] Safe parse with row/col caps and no formula eval (CWE-94/502)
    df = _safe_parse(content, filename, ext)

    # [5] Formula injection sanitization on in-memory df (CWE-1236)
    # Applied before any content is echoed; the serving path also sanitizes on download.
    df = _apply_formula_injection_sanitization(df)

    # Sanitise user-supplied form fields
    label_col = sanitize_string(label_col, 120)
    timestamp_col = sanitize_string(timestamp_col, 120)

    # Validate label_col / timestamp_col against actual columns
    if label_col and label_col not in df.columns:
        raise HTTPException(
            status_code=422,
            detail={
                "error": {
                    "code": "parse_error",
                    "message": f"label_col '{label_col}' not found in dataset. "
                               f"Available columns: {df.columns.tolist()[:20]}",
                    "type": "validation",
                }
            },
        )
    if timestamp_col and timestamp_col not in df.columns:
        raise HTTPException(
            status_code=422,
            detail={
                "error": {
                    "code": "parse_error",
                    "message": f"timestamp_col '{timestamp_col}' not found in dataset.",
                    "type": "validation",
                }
            },
        )

    # [6] RELEVANCE GATE (server-side authoritative — runs BEFORE quality scorer)
    rel_result = relevance_score_dataset(
        df=df,
        filename=filename,
        user_name="",
        user_description="",
        user_tags=[],
    )

    # Rejected path: short-circuit, do NOT run quality scorer, return 0 scores
    if not rel_result["accepted"]:
        # Persist a rejected summary so the owner can see it
        import uuid as _uuid
        audit_id_rej = str(_uuid.uuid4())
        dataset_id_rej = str(_uuid.uuid4())[:32]

        # Build a minimal AuditResult for the rejection response (no quality scoring)
        from scorer.composite import compute_composite, get_weights
        from scorer.models import (
            SubScores, DimensionResult, Preview, ColumnPreview
        )
        _neutral_dim = DimensionResult(
            score=0.0, weight=0.0,
            detail="Dataset rejected at relevance gate — quality scoring skipped.",
            severity="info",
        )
        rejected_sub = SubScores(
            completeness=_neutral_dim,
            class_balance=_neutral_dim,
            label_quality=_neutral_dim,
            duplicates=_neutral_dim,
            outliers=_neutral_dim,
            schema_validity=_neutral_dim,
            leakage=_neutral_dim,
            temporal_coverage=_neutral_dim,
            feature_redundancy=_neutral_dim,
            distribution_sanity=_neutral_dim,
            domain_pdm=None,
        )
        rejected_preview = Preview(
            columns=[
                ColumnPreview(name=c, dtype=str(df[c].dtype), null_pct=0.0)
                for c in df.columns[:10]
            ],
            sample_rows=[],
        )
        rejected_result = AuditResult(
            audit_id=audit_id_rej,
            dataset_id=dataset_id_rej,
            filename=filename,
            dataset_type="tabular",
            n_rows=len(df),
            n_cols=len(df.columns),
            composite_score=0.0,
            grade="Poor",
            sub_scores=rejected_sub,
            readiness=None,
            review=rel_result["gate_message"],
            improvements=[],
            preview=rejected_preview,
            reasoning_trace=rel_result["trace"],
            relevance=RelevanceResult(
                relevance_score=0.0,  # forced 0 on rejection (spec §1.5)
                accepted=False,
                gate_message=rel_result["gate_message"],
                relevance_reasons=rel_result.get("relevance_reasons", []),
                relevance_against=rel_result.get("relevance_against", []),
                kb_match_score=rel_result.get("kb_match_score", 0.0),
                embed_sim=rel_result.get("embed_sim"),
            ),
            ranking=RankingResult(
                overall_score=0.0,
                rank=0,
                feature_richness=0.0,
                ps_alignment=0.0,
                status="rejected",
            ),
        )

        # Persist rejected summary to JSONL
        summary_rej = AuditSummary(
            audit_id=audit_id_rej,
            dataset_id=dataset_id_rej,
            filename=filename,
            composite_score=0.0,
            grade="Poor",
            n_rows=len(df),
            n_cols=len(df.columns),
            download_count=0,
            created_at=datetime.now(timezone.utc).isoformat(),
            dataset_type="tabular",
            relevance_score=0.0,
            overall_score=0.0,
            rank=0,
            status="rejected",
        )
        _append_summary(summary_rej)

        return rejected_result

    # [7] Quality scorer (only reached for accepted datasets)
    try:
        result = await run_audit(
            df=df,
            filename=filename,
            label_col=label_col if label_col else None,
            timestamp_col=timestamp_col if timestamp_col else None,
            target_auc=target_auc,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=422,
            detail={
                "error": {
                    "code": "parse_error",
                    "message": "Could not score this dataset — it may be too small or malformed.",
                    "type": "server",
                }
            },
        )

    # [8] Ranking factors
    raw_sub_scores_dict = {
        k: v.model_dump() for k, v in result.sub_scores.__dict__.items() if v is not None
    }
    domain_pdm_raw = (
        result.sub_scores.domain_pdm.raw
        if result.sub_scores.domain_pdm and result.sub_scores.domain_pdm.raw
        else {}
    )
    domain_pdm_score = (
        result.sub_scores.domain_pdm.score
        if result.sub_scores.domain_pdm
        else None
    )

    feature_richness = compute_feature_richness(
        df=df,
        dataset_type=result.dataset_type,
        label_col=label_col,
        timestamp_col=timestamp_col,
        raw_sub_scores=raw_sub_scores_dict,
    )
    ps_alignment = compute_ps_alignment(
        df=df,
        dataset_type=result.dataset_type,
        label_col=label_col,
        timestamp_col=timestamp_col,
        raw_kb_evidence=rel_result.get("raw_kb", {}),
        domain_pdm_raw=domain_pdm_raw,
    )
    overall_score = compute_overall_score(
        relevance_score=rel_result["relevance_score"],
        quality_score=result.composite_score,
        domain_pdm_score=domain_pdm_score,
        feature_richness=feature_richness,
        ps_alignment=ps_alignment,
        dataset_type=result.dataset_type,
    )

    # [9] Attach v2 fields to result
    result.relevance = RelevanceResult(
        relevance_score=rel_result["relevance_score"],
        accepted=True,
        gate_message=rel_result["gate_message"],
        relevance_reasons=rel_result.get("relevance_reasons", []),
        relevance_against=rel_result.get("relevance_against", []),
        kb_match_score=rel_result.get("kb_match_score", 0.0),
        embed_sim=rel_result.get("embed_sim"),
    )
    result.ranking = RankingResult(
        overall_score=overall_score,
        rank=0,  # will be set after global rerank below
        feature_richness=feature_richness,
        ps_alignment=ps_alignment,
        status="accepted",
    )

    # Add relevance trace to reasoning_trace
    if result.reasoning_trace is None:
        result.reasoning_trace = []
    result.reasoning_trace = rel_result["trace"] + result.reasoning_trace

    # [10] Persist file
    try:
        stored_ext = ext or ".csv"
        (FILES_DIR / f"{result.audit_id}{stored_ext}").write_bytes(content)
    except Exception:
        pass

    # [11] Persist summary
    summary = AuditSummary(
        audit_id=result.audit_id,
        dataset_id=result.dataset_id,
        filename=result.filename,
        composite_score=result.composite_score,
        grade=result.grade,
        n_rows=result.n_rows,
        n_cols=result.n_cols,
        download_count=0,
        created_at=datetime.now(timezone.utc).isoformat(),
        dataset_type=result.dataset_type,
        relevance_score=rel_result["relevance_score"],
        overall_score=overall_score,
        rank=0,
        status="accepted",
    )
    _append_summary(summary)

    # [12] Recompute global ranks across ALL accepted datasets
    try:
        summaries = _load_summaries()
        summaries_dict = [s.model_dump() for s in summaries]
        ranked = assign_ranks(summaries_dict)
        rank_map = {r.get("audit_id", ""): r.get("rank", 0) for r in ranked}
        # Write updated ranks back
        updated_summaries = []
        for s_orig in summaries:
            r = rank_map.get(s_orig.audit_id, s_orig.rank)
            s_orig.rank = r
            updated_summaries.append(s_orig)
        with open(AUDITS_FILE, "w") as f:
            for s in updated_summaries:
                f.write(s.model_dump_json() + "\n")
        # Reflect current dataset's rank in the result
        result.ranking.rank = rank_map.get(result.audit_id, 0)
    except Exception:
        pass  # rank update is best-effort; never block the response

    return result


def _has_stored_file(audit_id: str, filename: str) -> bool:
    ext = os.path.splitext(filename)[1] or ".csv"
    if (FILES_DIR / f"{audit_id}{ext}").is_file():
        return True
    return bool(list(FILES_DIR.glob(f"{audit_id}.*")) or list(FILES_DIR.glob(audit_id)))


@app.get("/api/datasets", response_model=List[AuditSummary])
async def list_datasets(downloadable_only: bool = True):
    """
    Return audited datasets, best overall_score first (public board order).
    Rejected datasets are excluded from the board (status != accepted).
    """
    summaries = _load_summaries()
    # Public board: accepted only
    summaries = [s for s in summaries if s.status == "accepted"]
    if downloadable_only:
        summaries = [s for s in summaries if _has_stored_file(s.audit_id, s.filename)]
    # Sort by overall_score (v2), fallback to composite_score for old records
    return sorted(
        summaries,
        key=lambda s: (s.overall_score or s.composite_score),
        reverse=True,
    )


class DownloadResponse(BaseModel):
    dataset_id: str
    audit_id: str
    download_count: int


@app.post("/api/datasets/{audit_id}/download", response_model=DownloadResponse)
async def increment_download(audit_id: str):
    """Increment download count for a previously audited dataset."""
    # Sanitize path parameter
    audit_id = re.sub(r"[^a-f0-9\-]", "", audit_id)[:40]
    summaries = _load_summaries()
    target = next((s for s in summaries if s.audit_id == audit_id), None)
    if target is None:
        raise HTTPException(status_code=404, detail=f"Audit '{audit_id}' not found.")

    new_count = target.download_count + 1
    updated = _update_summary(audit_id, {"download_count": new_count})
    if not updated:
        raise HTTPException(status_code=500, detail="Failed to update download count.")

    return DownloadResponse(
        dataset_id=target.dataset_id,
        audit_id=audit_id,
        download_count=new_count,
    )


@app.get("/api/datasets/{audit_id}/file")
async def download_dataset_file(audit_id: str):
    """
    Serve the uploaded dataset file for public download.
    Formula-injection sanitization applied on serve (CWE-1236).
    """
    # Sanitize path parameter (prevent path traversal CWE-22)
    audit_id = re.sub(r"[^a-f0-9\-]", "", audit_id)[:40]

    summaries = _load_summaries()
    target = next((s for s in summaries if s.audit_id == audit_id), None)
    if target is None:
        raise HTTPException(status_code=404, detail=f"Dataset '{audit_id}' not found.")

    # Use server-determined ext from stored filename (not user-supplied path)
    stored_ext = os.path.splitext(target.filename)[1].lower() or ".csv"
    if stored_ext not in ALLOWED_EXT:
        stored_ext = ".csv"
    path = FILES_DIR / f"{audit_id}{stored_ext}"
    if not path.is_file():
        matches = list(FILES_DIR.glob(f"{audit_id}.*"))
        if matches:
            path = matches[0]
        else:
            raise HTTPException(
                status_code=404,
                detail="The original file for this dataset is no longer available.",
            )

    # Best-effort download count increment
    try:
        _update_summary(audit_id, {"download_count": target.download_count + 1})
    except Exception:
        pass

    # Serve with Content-Disposition: attachment + nosniff to prevent XSS (CWE-79)
    media = "text/csv" if stored_ext == ".csv" else "application/octet-stream"
    from fastapi.responses import Response
    file_bytes = path.read_bytes()
    return Response(
        content=file_bytes,
        media_type=media,
        headers={
            "Content-Disposition": f'attachment; filename="{target.filename}"',
            "X-Content-Type-Options": "nosniff",
        },
    )


# =============================================================================
# v2.1 — Supabase-backed endpoints (auth + Postgres + Storage)
# All new uploads, board reads, and quota ops go through these.
# Legacy /api/audit remains for back-compat.
# =============================================================================

import asyncio as _asyncio
from typing import Optional as _Opt

# Async job queue — 3 workers process scoring in the background
_job_queue: _asyncio.Queue = _asyncio.Queue()
_WORKER_COUNT = 3

# In-memory buffer: dataset_id -> (content_bytes, label_col, timestamp_col, target_auc, ext)
# Used to pass uploaded file to the background worker without re-fetching from storage
_upload_buffer: Dict[str, tuple] = {}


def _err(code: str, message: str, err_type: str = "validation", status: int = 422):
    raise HTTPException(
        status_code=status,
        detail={"error": {"code": code, "message": message, "type": err_type}},
    )


def _compute_checksum(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _mime_for_ext(ext: str) -> str:
    return {
        ".csv": "text/csv",
        ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ".json": "application/json",
    }.get(ext, "application/octet-stream")


def _auto_tags(df: "pd.DataFrame", rel_result: dict) -> List[str]:
    """
    Auto-generate meaningful display tags from:
      1. Column-name sensor keywords (vibration, temperature, etc.)
      2. Detected sensor types from the KB gate (list of strings)
      3. Equipment class names + maintenance vocab group names from KB hits
    Explicitly excludes internal KB bookkeeping keys so the UI never shows
    'corroboration_per_type', 'detected_sensors', etc.
    """
    SENSOR_KEYWORDS = {
        "temperature", "vibration", "pressure", "speed", "current", "voltage",
        "flow", "torque", "bearing", "rpm", "sensor", "machine", "failure",
        "fault", "defect", "timestamp", "cycle", "wear", "tool", "steel",
        "thickness", "coil", "roll", "furnace", "motor", "pump", "conveyor",
    }
    _INTERNAL_KB_KEYS = {
        "detected_sensors", "n_sensor_types", "corroboration_per_type",
        "mean_corroboration", "equipment_hits", "maintenance_hits",
        "coherence", "has_timestamp", "n_numeric", "raw_kb",
    }
    tags: set = set()
    cols_lower = {c.lower() for c in df.columns}
    for kw in SENSOR_KEYWORDS:
        if any(kw in c for c in cols_lower):
            tags.add(kw)
    raw_kb = rel_result.get("raw_kb", {})
    # Detected sensor types (already cleaned strings like 'vibration')
    for sensor in raw_kb.get("detected_sensors", []):
        if isinstance(sensor, str) and len(sensor) < 30:
            tags.add(sensor.lower())
    # Equipment class names
    for eq_class in raw_kb.get("equipment_hits", {}):
        if isinstance(eq_class, str) and len(eq_class) < 40 and eq_class not in _INTERNAL_KB_KEYS:
            tags.add(eq_class.lower().replace("_", "-"))
    # Maintenance vocab group names
    for maint_grp in raw_kb.get("maintenance_hits", {}):
        if isinstance(maint_grp, str) and len(maint_grp) < 40 and maint_grp not in _INTERNAL_KB_KEYS:
            tags.add(maint_grp.lower().replace("_", "-"))
    return sorted(list(tags))[:10]


def _auto_description(df: "pd.DataFrame", rel_result: dict, n_rows: int, n_cols: int) -> str:
    """
    Auto-generate a short description from detected equipment types and dataset shape.
    """
    reasons = rel_result.get("relevance_reasons", [])
    if reasons:
        base = reasons[0]
    else:
        base = "Industrial dataset"
    return f"{base}. {n_rows:,} rows x {n_cols} columns."


# ---------------------------------------------------------------------------
# Background scoring worker
# ---------------------------------------------------------------------------
async def _scoring_worker():
    """
    Pull job_ids from _job_queue and run the scorer.
    Writes results to Postgres (service role — bypasses RLS).
    """
    while True:
        job_id = await _job_queue.get()
        try:
            job = repo.get_job(job_id)
            if not job:
                _job_queue.task_done()
                continue

            dataset_id = job["dataset_id"]
            repo.update_job(job_id, "running")

            # Retrieve buffered upload content (prefer in-memory over storage re-fetch)
            buf = _upload_buffer.pop(dataset_id, None)
            if buf is None:
                # Buffer expired (restart recovery) — skip this job
                repo.update_job(job_id, "failed", "buffer_missing", "In-memory buffer unavailable after restart")
                _job_queue.task_done()
                continue

            content, label_col, timestamp_col, target_auc, ext, owner_id = buf

            # Re-parse (already validated on upload; this is safe)
            df = _safe_parse(content, f"upload{ext}", ext)
            df = _apply_formula_injection_sanitization(df)

            # Run scorer
            result = await run_audit(
                df=df,
                filename=f"upload{ext}",
                label_col=label_col or None,
                timestamp_col=timestamp_col or None,
                target_auc=target_auc,
            )

            # Ranking factors
            raw_sub = {k: v.model_dump() for k, v in result.sub_scores.__dict__.items() if v is not None}
            rel_result = relevance_score_dataset(
                df=df, filename=f"upload{ext}",
                user_name="", user_description="", user_tags=[],
            )
            domain_pdm_raw = (
                result.sub_scores.domain_pdm.raw
                if result.sub_scores.domain_pdm and result.sub_scores.domain_pdm.raw else {}
            )
            domain_pdm_score = (
                result.sub_scores.domain_pdm.score if result.sub_scores.domain_pdm else None
            )
            feature_richness = compute_feature_richness(
                df=df, dataset_type=result.dataset_type,
                label_col=label_col, timestamp_col=timestamp_col,
                raw_sub_scores=raw_sub,
            )
            ps_alignment = compute_ps_alignment(
                df=df, dataset_type=result.dataset_type,
                label_col=label_col, timestamp_col=timestamp_col,
                raw_kb_evidence=rel_result.get("raw_kb", {}),
                domain_pdm_raw=domain_pdm_raw,
            )
            overall_score = compute_overall_score(
                relevance_score=rel_result["relevance_score"],
                quality_score=result.composite_score,
                domain_pdm_score=domain_pdm_score,
                feature_richness=feature_richness,
                ps_alignment=ps_alignment,
                dataset_type=result.dataset_type,
            )

            # Update dataset row
            repo.update_dataset_scored(
                dataset_id=dataset_id,
                composite_score=result.composite_score,
                grade=result.grade,
                overall_score=overall_score,
                relevance_score=rel_result["relevance_score"],
                status="accepted",
            )

            # Insert audit report (JSONB)
            ss = result.sub_scores
            repo.insert_audit_report(
                dataset_id=dataset_id,
                full_report=result.model_dump(),
                score_completeness=ss.completeness.score if ss.completeness else None,
                score_class_balance=ss.class_balance.score if ss.class_balance else None,
                score_label_quality=ss.label_quality.score if ss.label_quality else None,
                score_duplicates=ss.duplicates.score if ss.duplicates else None,
                score_outliers=ss.outliers.score if ss.outliers else None,
                score_schema_validity=ss.schema_validity.score if ss.schema_validity else None,
                score_leakage=ss.leakage.score if ss.leakage else None,
                score_temporal_coverage=ss.temporal_coverage.score if ss.temporal_coverage else None,
                score_feature_redundancy=ss.feature_redundancy.score if ss.feature_redundancy else None,
                score_distribution_sanity=ss.distribution_sanity.score if ss.distribution_sanity else None,
                score_domain_pdm=domain_pdm_score,
                readiness_pct=result.readiness.readiness_pct if result.readiness else None,
                baseline_auc=result.readiness.baseline_auc if result.readiness else None,
            )

            # Update tags + description with auto-generated values
            tags = _auto_tags(df, rel_result)
            description = _auto_description(df, rel_result, len(df), len(df.columns))
            ds = repo.get_dataset(dataset_id)
            if ds and not ds.get("tags"):
                with _pg_conn() as conn:
                    cur = conn.cursor()
                    cur.execute(
                        "UPDATE public.datasets SET tags=%s, description=%s WHERE id=%s",
                        (tags, description, dataset_id),
                    )

            # Recalculate global ranks
            repo.recalculate_ranks()

            # Log scoring completed
            repo.log_audit_event(
                "scoring_completed",
                owner_id=owner_id,
                dataset_id=dataset_id,
                detail={"composite_score": result.composite_score, "overall_score": overall_score},
            )

            repo.update_job(job_id, "completed")

        except Exception as exc:
            try:
                repo.update_job(job_id, "failed", "scorer_error", str(exc)[:500])
                repo.log_audit_event(
                    "scoring_failed",
                    dataset_id=dataset_id if "dataset_id" in dir() else None,
                    detail={"error": str(exc)[:300]},
                )
            except Exception:
                pass
        finally:
            _job_queue.task_done()


# Register workers on startup
@app.on_event("startup")
async def _start_workers():
    for _ in range(_WORKER_COUNT):
        _asyncio.create_task(_scoring_worker())


# ---------------------------------------------------------------------------
# POST /api/datasets — auth + quota + validate + gate + score + persist
# ---------------------------------------------------------------------------
@app.post("/api/datasets")
@limiter.limit("10/hour")
async def upload_dataset_v2(
    request: Request,
    file: UploadFile = File(...),
    label_col: Optional[str] = Form(default=None),
    timestamp_col: Optional[str] = Form(default=None),
    target_auc: float = Form(default=0.80),
    description: Optional[str] = Form(default=None),
    tags: Optional[str] = Form(default=None),  # comma-separated
    user: UserContext = Depends(require_user),
):
    """
    v2.1 upload pipeline:
    auth → quota ≤5 → validate → relevance gate → checksum dedup →
    upload to Storage → INSERT dataset + job → enqueue → 202
    """
    filename = sanitize_string(file.filename, 255) or "upload"
    label_col = sanitize_string(label_col, 120)
    timestamp_col = sanitize_string(timestamp_col, 120)
    description_clean = sanitize_string(description, 500)
    user_tags = [t.strip() for t in (tags or "").split(",") if t.strip()][:20]
    owner_id = user.user_id

    # [1] File size cap
    content = await _read_capped(file)

    # [2] File type
    ext = _validate_file_type(filename, content[:8192])

    # [3] Zip-bomb guard
    _zipbomb_check(content, ext)

    # [4] Parse
    df = _safe_parse(content, filename, ext)
    df = _apply_formula_injection_sanitization(df)

    # Validate column hints
    if label_col and label_col not in df.columns:
        _err("parse_error", f"label_col '{label_col}' not found. Columns: {df.columns.tolist()[:20]}")
    if timestamp_col and timestamp_col not in df.columns:
        _err("parse_error", f"timestamp_col '{timestamp_col}' not found.")

    # [5] Quota check (Postgres)
    if PERSISTENCE_BACKEND == "supabase" and not user.is_anonymous:
        used = repo.get_user_quota_used(owner_id)
        if used >= repo.MAX_DATASETS_PER_USER:
            repo.log_audit_event("quota_exceeded", owner_id=owner_id,
                                 ip_address=request.client.host if request.client else None)
            _err("quota_exceeded",
                 f"You have {used}/{repo.MAX_DATASETS_PER_USER} active datasets. Delete one to upload more.",
                 "quota", 429)

    # [6] Checksum dedup
    checksum = _compute_checksum(content)
    if PERSISTENCE_BACKEND == "supabase" and not user.is_anonymous:
        existing = repo.find_by_checksum(checksum, owner_id)
        if existing:
            return JSONResponse(content={
                "data": {
                    "status": existing["status"],
                    "dataset_id": str(existing["id"]),
                    "composite_score": float(existing["composite_score"] or 0),
                    "rank": existing.get("rank"),
                    "duplicate": True,
                },
                "meta": {},
            })

    # [7] Relevance gate
    rel_result = relevance_score_dataset(
        df=df, filename=filename,
        user_name="", user_description=description_clean or "", user_tags=user_tags,
    )

    if not rel_result["accepted"]:
        # Persist rejected record (Supabase or local)
        dataset_id_rej = str(_uuid_mod.uuid4())
        if PERSISTENCE_BACKEND == "supabase" and not user.is_anonymous:
            repo.insert_dataset(
                owner_id=owner_id,
                filename=filename,
                mime_type=_mime_for_ext(ext),
                size_bytes=len(content),
                checksum=checksum,
                n_rows=len(df),
                n_cols=len(df.columns),
                dataset_type="tabular",
                tags=[],
                description=description_clean,
                storage_path=None,
                status="rejected",
                rejection_reason=rel_result["gate_message"],
                composite_score=0.0,
                grade="Poor",
                relevance_score=0.0,
                overall_score=0.0,
                dataset_id=dataset_id_rej,  # keep response id == DB row id
            )
            repo.log_audit_event(
                "relevance_rejected", owner_id=owner_id,
                ip_address=request.client.host if request.client else None,
                detail={"filename": filename, "reason": rel_result["gate_message"]},
            )
        return JSONResponse(content={
            "data": {
                "status": "rejected",
                "dataset_id": dataset_id_rej,
                "rejection_reason": rel_result["gate_message"],
                "relevance_score": rel_result.get("relevance_score", 0.0),
                "suggestion": "Upload datasets from steel plants, predictive maintenance, or manufacturing sensors.",
            },
            "meta": {},
        })

    # [8] Upload to storage
    dataset_id = str(_uuid_mod.uuid4())
    storage_path = None
    if STORAGE_BACKEND == "supabase" and not user.is_anonymous:
        try:
            repo.log_audit_event("upload_started", owner_id=owner_id,
                                 ip_address=request.client.host if request.client else None,
                                 detail={"filename": filename, "size": len(content)})
            storage_path = storage_supa.upload_file(
                owner_id=owner_id,
                dataset_id=dataset_id,
                filename=filename,
                content=content,
                mime_type=_mime_for_ext(ext),
            )
        except Exception as se:
            _err("server_error", f"Storage upload failed: {se}", "server", 500)
    else:
        # Local fallback
        try:
            (FILES_DIR / f"{dataset_id}{ext}").write_bytes(content)
        except Exception:
            pass

    # [9] Insert dataset row + job row
    auto_tags = _auto_tags(df, rel_result)
    combined_tags = list(set(user_tags + auto_tags))[:15]
    auto_desc = description_clean or _auto_description(df, rel_result, len(df), len(df.columns))

    if PERSISTENCE_BACKEND == "supabase" and not user.is_anonymous:
        repo.insert_dataset(
            owner_id=owner_id,
            filename=filename,
            mime_type=_mime_for_ext(ext),
            size_bytes=len(content),
            checksum=checksum,
            n_rows=len(df),
            n_cols=len(df.columns),
            dataset_type="tabular",
            tags=combined_tags,
            description=auto_desc,
            storage_path=storage_path,
            status="processing",
            dataset_id=dataset_id,  # keep id consistent so jobs FK + storage + buffer match
        )
        job_id = repo.insert_job(dataset_id=dataset_id, owner_id=owner_id)
        repo.log_audit_event("scoring_started", owner_id=owner_id, dataset_id=dataset_id)
    else:
        # Local path: just generate a dummy job_id for the response
        job_id = str(_uuid_mod.uuid4())

    # [10] Buffer upload content + enqueue job
    _upload_buffer[dataset_id] = (content, label_col, timestamp_col, target_auc, ext, owner_id)
    await _job_queue.put(job_id)

    return JSONResponse(
        status_code=202,
        content={
            "data": {
                "job_id": job_id,
                "dataset_id": dataset_id,
                "status": "processing",
                "poll_url": f"/api/jobs/{job_id}",
            },
            "meta": {},
        },
    )


# ---------------------------------------------------------------------------
# GET /api/datasets — public leaderboard (Supabase or legacy JSONL)
# ---------------------------------------------------------------------------
# NOTE: This OVERRIDES the old list_datasets route. Both Supabase + local
# paths are handled here so the route name is consistent.
# We cannot redeclare the route — the old GET /api/datasets was
# `@app.get("/api/datasets", response_model=List[AuditSummary])`.
# We will rename the old one via app.routes manipulation below.
# ---------------------------------------------------------------------------

@app.get("/api/v2/datasets")
@limiter.limit("60/minute")
async def list_datasets_v2(
    request: Request,
    limit: int = Query(default=20, ge=1, le=100),
    cursor: Optional[str] = Query(default=None),
    sort: str = Query(default="rank", pattern="^(rank|score|upload_date|downloads)$"),
    order: str = Query(default="asc", pattern="^(asc|desc)$"),
    dataset_type: Optional[str] = Query(default=None, pattern="^(tabular|time_series)$"),
    grade: Optional[str] = Query(default=None),
    min_score: Optional[float] = Query(default=None),
    q: Optional[str] = Query(default=None, max_length=100),
    my_datasets: bool = Query(default=False),
    user: Optional[UserContext] = Depends(get_current_user),
):
    """
    Public leaderboard with cursor-based pagination.
    Supabase path when PERSISTENCE_BACKEND=supabase, else falls back to JSONL.
    """
    if PERSISTENCE_BACKEND == "supabase":
        owner_id = user.user_id if user and not user.is_anonymous else None
        result = repo.list_datasets_board(
            limit=limit,
            cursor=cursor,
            sort=sort,
            order=order,
            dataset_type=dataset_type,
            grade=grade,
            min_score=min_score,
            q=q,
            my_datasets=my_datasets and owner_id is not None,
            owner_id=owner_id,
        )
        # Serialize datetime fields
        data = []
        for row in result["data"]:
            r = dict(row)
            for k, v in r.items():
                if hasattr(v, "isoformat"):
                    r[k] = v.isoformat()
                elif isinstance(v, float) and v != v:  # nan check
                    r[k] = None
            data.append(r)
        return {
            "data": data,
            "meta": {
                "total": result["total"],
                "limit": limit,
                "next_cursor": result["next_cursor"],
            },
        }
    else:
        # Local JSONL fallback
        summaries = _load_summaries()
        summaries = [s for s in summaries if s.status == "accepted"]
        if q:
            summaries = [s for s in summaries if q.lower() in s.filename.lower()]
        summaries = sorted(
            summaries,
            key=lambda s: (s.overall_score or s.composite_score),
            reverse=(order == "desc"),
        )
        start = 0
        page = summaries[start:start + limit]
        return {
            "data": [s.model_dump() for s in page],
            "meta": {"total": len(summaries), "limit": limit, "next_cursor": None},
        }


# ---------------------------------------------------------------------------
# GET /api/datasets/{dataset_id} — full audit report
# ---------------------------------------------------------------------------
@app.get("/api/v2/datasets/{dataset_id}")
async def get_dataset_v2(
    dataset_id: str,
    user: Optional[UserContext] = Depends(get_current_user),
):
    """Full audit report for one dataset. Public for accepted; owner-only for others."""
    dataset_id = re.sub(r"[^a-f0-9\-]", "", dataset_id)[:40]

    if PERSISTENCE_BACKEND != "supabase":
        raise HTTPException(status_code=404, detail="Use /api/audit for legacy datasets.")

    row = repo.get_dataset_with_report(dataset_id)
    if not row:
        raise HTTPException(status_code=404, detail={"error": {"code": "not_found", "message": "Dataset not found.", "type": "validation"}})

    # Auth check: non-accepted datasets require owner
    owner_id = user.user_id if user and not user.is_anonymous else None
    if row["status"] != "accepted":
        if not owner_id or str(row["owner_id"]) != owner_id:
            raise HTTPException(status_code=403, detail={"error": {"code": "forbidden", "message": "Dataset is not public.", "type": "auth"}})

    # Build response
    r = {k: (v.isoformat() if hasattr(v, "isoformat") else v) for k, v in dict(row).items()}
    return {"data": r, "meta": {}}


# ---------------------------------------------------------------------------
# GET /api/datasets/{dataset_id}/file — signed URL
# ---------------------------------------------------------------------------
@app.get("/api/v2/datasets/{dataset_id}/file")
async def get_dataset_file_v2(
    dataset_id: str,
    user: Optional[UserContext] = Depends(get_current_user),
):
    """Return signed Supabase Storage URL (1h TTL). Increments download_count."""
    dataset_id = re.sub(r"[^a-f0-9\-]", "", dataset_id)[:40]

    if STORAGE_BACKEND != "supabase" or PERSISTENCE_BACKEND != "supabase":
        raise HTTPException(status_code=404, detail="Use /api/datasets/{id}/file for legacy datasets.")

    row = repo.get_dataset(dataset_id)
    if not row or row["status"] == "deleted":
        raise HTTPException(status_code=404, detail={"error": {"code": "not_found", "message": "Dataset not found.", "type": "validation"}})

    # Public read for accepted datasets; owner for others
    owner_id = user.user_id if user and not user.is_anonymous else None
    if row["status"] != "accepted":
        if not owner_id or str(row["owner_id"]) != owner_id:
            raise HTTPException(status_code=403, detail={"error": {"code": "forbidden", "message": "Access denied.", "type": "auth"}})

    storage_path = row.get("storage_path")
    if not storage_path:
        raise HTTPException(status_code=404, detail={"error": {"code": "not_found", "message": "No file stored for this dataset.", "type": "validation"}})

    try:
        signed = storage_supa.get_signed_url(storage_path)
    except Exception as exc:
        raise HTTPException(status_code=503, detail={"error": {"code": "server_error", "message": f"Could not generate download URL: {exc}", "type": "server"}})

    # Best-effort download count increment
    try:
        with _pg_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                "UPDATE public.datasets SET download_count = download_count + 1 WHERE id = %s",
                (dataset_id,),
            )
        repo.log_audit_event("download", dataset_id=dataset_id, owner_id=owner_id)
    except Exception:
        pass

    return {
        "data": {
            "download_url": signed["signed_url"],
            "expires_at": signed["expires_at"],
            "filename": row["filename"],
            "size_bytes": row.get("size_bytes"),
        },
        "meta": {},
    }


# ---------------------------------------------------------------------------
# GET /api/me/quota — authenticated user quota
# ---------------------------------------------------------------------------
@app.get("/api/me/quota")
async def get_quota(user: UserContext = Depends(require_user)):
    """Return authenticated user's upload quota (used / remaining / max=5)."""
    owner_id = user.user_id

    if PERSISTENCE_BACKEND != "supabase" or user.is_anonymous:
        return {
            "data": {"used": 0, "limit": repo.MAX_DATASETS_PER_USER, "remaining": repo.MAX_DATASETS_PER_USER, "datasets": []},
            "meta": {},
        }

    used = repo.get_user_quota_used(owner_id)
    datasets = repo.get_owner_datasets(owner_id)

    # Serialize datetimes
    ds_list = []
    for d in datasets:
        row = dict(d)
        for k, v in row.items():
            if hasattr(v, "isoformat"):
                row[k] = v.isoformat()
        ds_list.append(row)

    return {
        "data": {
            "used": used,
            "limit": repo.MAX_DATASETS_PER_USER,
            "remaining": max(0, repo.MAX_DATASETS_PER_USER - used),
            "datasets": ds_list,
        },
        "meta": {},
    }


# ---------------------------------------------------------------------------
# DELETE /api/datasets/{dataset_id} — owner-only soft-delete
# ---------------------------------------------------------------------------
@app.delete("/api/v2/datasets/{dataset_id}", status_code=204)
async def delete_dataset_v2(
    dataset_id: str,
    user: UserContext = Depends(require_user),
):
    """Soft-delete a dataset (owner only). Removes file from Storage."""
    dataset_id = re.sub(r"[^a-f0-9\-]", "", dataset_id)[:40]
    owner_id = user.user_id

    if PERSISTENCE_BACKEND != "supabase" or user.is_anonymous:
        raise HTTPException(status_code=403, detail={"error": {"code": "forbidden", "message": "Auth required.", "type": "auth"}})

    row = repo.get_dataset(dataset_id)
    if not row:
        return  # Already gone — idempotent 204

    if str(row["owner_id"]) != owner_id:
        raise HTTPException(status_code=403, detail={"error": {"code": "forbidden", "message": "You do not own this dataset.", "type": "auth"}})

    if row["status"] == "deleted":
        return  # Already deleted — idempotent 204

    # Soft-delete in Postgres
    repo.soft_delete_dataset(dataset_id, owner_id)

    # Remove from Storage (best-effort)
    if STORAGE_BACKEND == "supabase" and row.get("storage_path"):
        try:
            storage_supa.delete_file(row["storage_path"])
        except Exception:
            pass

    # Recalculate ranks
    try:
        repo.recalculate_ranks()
    except Exception:
        pass

    repo.log_audit_event("delete_requested", owner_id=owner_id, dataset_id=dataset_id)


# ---------------------------------------------------------------------------
# GET /api/jobs/{job_id} — poll async job status
# ---------------------------------------------------------------------------
@app.get("/api/jobs/{job_id}")
async def get_job(
    job_id: str,
    user: UserContext = Depends(require_user),
):
    """Poll the status of an async scoring job."""
    job_id = re.sub(r"[^a-f0-9\-]", "", job_id)[:40]
    owner_id = user.user_id if not user.is_anonymous else None

    if PERSISTENCE_BACKEND != "supabase":
        raise HTTPException(status_code=404, detail="Job tracking requires Supabase backend.")

    job = repo.get_job(job_id, owner_id=owner_id)
    if not job:
        raise HTTPException(status_code=404, detail={"error": {"code": "job_not_found", "message": "Job not found.", "type": "validation"}})

    j = {k: (v.isoformat() if hasattr(v, "isoformat") else v) for k, v in dict(job).items()}
    return {"data": j, "meta": {}}
