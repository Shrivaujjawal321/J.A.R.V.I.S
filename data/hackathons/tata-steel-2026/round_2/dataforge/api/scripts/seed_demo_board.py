"""
scripts/seed_demo_board.py
==========================
Idempotent demo-board seeder for EDITH DataForge.

What it does (safe to run multiple times):
  1. CLEAR  — delete all rows owned by LEGACY_USER_ID and DEMO_USER_ID from
              public.datasets (CASCADE wipes public.audit_reports), then remove
              their files from the Supabase Storage 'datasets' bucket.
  2. ENSURE  — create auth.users row for DEMO_USER_ID if not present.
  3. SEED (accepted) — run 8-10 genuine steel/PdM CSVs through the FULL v2
              pipeline (relevance gate → quality scoring → ranking factors →
              overall_score → insert dataset + audit_report + upload to Storage).
  4. SEED (rejected) — run iris + generic tabular through the pipeline so they
              land with status='rejected', relevance_score=0, rank=0, to
              showcase the gate in the "Rejected" tab.
  5. RECOMPUTE ranks for accepted rows.
  6. VERIFY  — print final table of filename / status / relevance / overall /
              rank / tags.

Usage:
    /home/ujjwal/Documents/J.A.R.V.I.S./.venv/bin/python \\
        /home/ujjwal/Documents/J.A.R.V.I.S./data/hackathons/tata-steel-2026/round_2/dataforge/api/scripts/seed_demo_board.py

    Add --dry-run to see what would happen without writing.

Design:
  - All Postgres ops via the existing supa.client pool (service-role, bypasses RLS).
  - Storage uploads via supa.storage.upload_file (same service-key pattern).
  - Scoring via scorer.agent.run_audit (async, wrapped in asyncio.run).
  - Relevance gate via scorer.relevance.gate.score_dataset.
  - Ranking via scorer.ranking.factors + scorer.ranking.overall.
  - No FastAPI dependency — this is a plain sync/async script.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import io
import os
import sys
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Path setup — ensure api/ is importable
# ---------------------------------------------------------------------------
API_DIR = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(API_DIR))

from dotenv import load_dotenv
load_dotenv(API_DIR / ".env")

import httpx
import pandas as pd
import psycopg2
import psycopg2.extras

from supa.client import pg_conn
import supa.repo as repo
import supa.storage as storage_supa

from scorer.relevance.gate import score_dataset as relevance_score_dataset
from scorer.relevance.embeddings import load_embeddings_model, precompute_query_embeddings
from scorer.ranking.factors import compute_feature_richness, compute_ps_alignment
from scorer.ranking.overall import compute_overall_score
from scorer.agent import run_audit

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
LEGACY_USER_ID = os.environ.get("EDITH_LEGACY_USER_ID", "d0000000-0000-0000-0000-000000000099")
DEMO_USER_ID = "b0000000-0000-0000-0000-000000000001"
DEMO_EMAIL = "demo@edith.app"
DEMO_DISPLAY = "EDITH Demo Board"

SUPABASE_URL = os.environ["SUPABASE_URL"]
SERVICE_KEY = os.environ["SUPABASE_SERVICE_KEY"]

FLAGSHIP_BY_EQ = API_DIR.parent / "datasets" / "steel-maintenance-flagship" / "condition_monitoring" / "by_equipment"
SAMPLES_DIR = API_DIR.parent / "samples"

# Steel files to seed as accepted (pick diverse equipment classes)
STEEL_ACCEPTED_FILES: List[Path] = []

# We'll build this list dynamically — use by_equipment CSVs first, then samples
_BY_EQ_CANDIDATES = [
    "bf_sinter_fan_blower__BF_BLW_FAN01.csv",
    "rolling_mill_work_roll_bearing.csv",
    "cooling_descaling_pump__HSM_DSC_PMP01.csv",
    "hot_strip_mill_stand.csv",
    "hydraulics_agc_servo.csv",
    "mill_gearbox.csv",
    "reheating_furnace.csv",
    "large_induction_motor_vfd.csv",
]
_SAMPLE_CANDIDATES = [
    "steel_good_runtofailure.csv",
    "steel_demo_episode.csv",
    "steel_weak_dirty.csv",
]

STORAGE_HEADERS = {
    "Authorization": f"Bearer {SERVICE_KEY}",
    "apikey": SERVICE_KEY,
    "Content-Type": "application/json",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _checksum(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _safe_read_csv(path: Path) -> Optional[pd.DataFrame]:
    """Read a CSV into a DataFrame, returning None on failure."""
    try:
        df = pd.read_csv(path, low_memory=False, nrows=50_000)
        if df.empty or df.shape[1] < 2:
            return None
        return df
    except Exception as exc:
        print(f"  WARN: could not parse {path.name}: {exc}")
        return None


def _make_synthetic_iris_csv() -> Tuple[str, bytes]:
    """Return (filename, csv_bytes) for a small Iris-like dataset."""
    data = """sepal_length,sepal_width,petal_length,petal_width,species
5.1,3.5,1.4,0.2,Iris-setosa
4.9,3.0,1.4,0.2,Iris-setosa
4.7,3.2,1.3,0.2,Iris-setosa
4.6,3.1,1.5,0.2,Iris-setosa
5.0,3.6,1.4,0.2,Iris-setosa
7.0,3.2,4.7,1.4,Iris-versicolor
6.4,3.2,4.5,1.5,Iris-versicolor
6.9,3.1,4.9,1.5,Iris-versicolor
5.5,2.3,4.0,1.3,Iris-versicolor
6.5,2.8,4.6,1.5,Iris-versicolor
6.3,3.3,6.0,2.5,Iris-virginica
5.8,2.7,5.1,1.9,Iris-virginica
7.1,3.0,5.9,2.1,Iris-virginica
6.3,2.9,5.6,1.8,Iris-virginica
6.5,3.0,5.8,2.2,Iris-virginica
"""
    return "clean_iris.csv", data.encode()


def _make_generic_tabular_csv() -> Tuple[str, bytes]:
    """Return (filename, csv_bytes) for a generic non-industrial dataset."""
    data = """name,age,salary,department,years_experience,performance_rating
Alice,28,55000,Engineering,3,4.2
Bob,35,72000,Marketing,8,3.8
Carol,42,89000,Finance,15,4.5
David,31,61000,Engineering,5,3.9
Eve,27,48000,HR,2,4.1
Frank,39,95000,Management,12,4.7
Grace,33,67000,Engineering,7,4.0
Henry,45,110000,Finance,20,4.8
"""
    return "employee_data.csv", data.encode()


def _auto_tags(df: pd.DataFrame, rel_result: dict) -> List[str]:
    """
    Produce meaningful display tags from:
      1. Column-name sensor keywords (vibration, temperature, etc.)
      2. Detected sensor types from the KB (e.g. 'vibration', 'temperature')
      3. Equipment class names from KB hits
    Explicitly excludes internal KB bookkeeping keys.
    """
    SENSOR_KEYWORDS = {
        "temperature", "vibration", "pressure", "speed", "current", "voltage",
        "flow", "torque", "bearing", "rpm", "sensor", "machine", "failure",
        "fault", "defect", "timestamp", "cycle", "wear", "tool", "steel",
        "thickness", "coil", "roll", "furnace", "motor", "pump", "conveyor",
    }
    # Internal KB keys to never include as display tags
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
    # Add detected sensor types (list of strings like ['vibration','temperature'])
    raw_kb = rel_result.get("raw_kb", {})
    for sensor in raw_kb.get("detected_sensors", []):
        if isinstance(sensor, str) and len(sensor) < 30:
            tags.add(sensor.lower())
    # Add equipment class names (dict like {'rolling_mill_bearing': ..., 'motor': ...})
    for eq_class in raw_kb.get("equipment_hits", {}):
        if isinstance(eq_class, str) and len(eq_class) < 40 and eq_class not in _INTERNAL_KB_KEYS:
            tags.add(eq_class.lower().replace("_", "-"))
    # Add maintenance vocab group names (fault_labels, maintenance_ops, etc.)
    for maint_grp in raw_kb.get("maintenance_hits", {}):
        if isinstance(maint_grp, str) and len(maint_grp) < 40 and maint_grp not in _INTERNAL_KB_KEYS:
            tags.add(maint_grp.lower().replace("_", "-"))
    return sorted(list(tags))[:10]


def _auto_description(df: pd.DataFrame, rel_result: dict, n_rows: int, n_cols: int) -> str:
    """Reproduce the auto-description logic from main.py."""
    reasons = rel_result.get("relevance_reasons", [])
    base = reasons[0] if reasons else "Industrial dataset"
    return f"{base}. {n_rows:,} rows x {n_cols} columns."


def _mime_for_ext(ext: str) -> str:
    return {".csv": "text/csv", ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ".json": "application/json"}.get(ext, "text/csv")


# ---------------------------------------------------------------------------
# Step 1: Clear legacy + demo rows from DB and Storage
# ---------------------------------------------------------------------------

def clear_legacy_and_demo(dry_run: bool) -> int:
    """
    Delete all datasets (+ audit_reports via CASCADE) owned by LEGACY_USER_ID
    or DEMO_USER_ID, and remove their Storage bucket files.
    Returns count of deleted DB rows.
    """
    with pg_conn() as conn:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Fetch storage_paths BEFORE deletion so we can clean Storage
        cur.execute(
            """
            SELECT id, filename, storage_path
            FROM public.datasets
            WHERE owner_id IN (%s, %s)
              AND status != 'deleted'
            """,
            (LEGACY_USER_ID, DEMO_USER_ID),
        )
        rows = cur.fetchall()
        storage_paths = [r["storage_path"] for r in rows if r.get("storage_path")]

        if dry_run:
            print(f"  [DRY] Would delete {len(rows)} dataset rows and {len(storage_paths)} storage objects")
            return len(rows)

        # Hard-delete from DB (CASCADE handles audit_reports)
        cur.execute(
            "DELETE FROM public.datasets WHERE owner_id IN (%s, %s)",
            (LEGACY_USER_ID, DEMO_USER_ID),
        )
        deleted = cur.rowcount

    # Remove from Storage (best-effort, ignore individual failures)
    removed_storage = 0
    for sp in storage_paths:
        try:
            ok = storage_supa.delete_file(sp)
            if ok:
                removed_storage += 1
        except Exception as exc:
            print(f"  WARN: storage delete failed for {sp}: {exc}")

    print(f"  Deleted {deleted} DB rows; removed {removed_storage}/{len(storage_paths)} storage objects")
    return deleted


# ---------------------------------------------------------------------------
# Step 2: Ensure demo auth user exists
# ---------------------------------------------------------------------------

def ensure_demo_user(dry_run: bool) -> None:
    """Create the DEMO_USER_ID in auth.users if absent."""
    with pg_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM auth.users WHERE id = %s", (DEMO_USER_ID,))
        exists = cur.fetchone() is not None
        if exists:
            print(f"  Demo user {DEMO_USER_ID} already in auth.users")
            return
        if dry_run:
            print(f"  [DRY] Would create auth.users row for {DEMO_USER_ID}")
            return
        cur.execute(
            """
            INSERT INTO auth.users (
                id, email, created_at, updated_at, aud, role,
                confirmation_token, recovery_token,
                email_change_token_new, email_change,
                raw_app_meta_data, raw_user_meta_data
            ) VALUES (%s, %s, now(), now(), %s, %s, %s, %s, %s, %s, %s::jsonb, %s::jsonb)
            ON CONFLICT (id) DO NOTHING
            """,
            (
                DEMO_USER_ID, DEMO_EMAIL,
                "authenticated", "authenticated",
                "", "", "", "",
                "{}", "{}",
            ),
        )
    print(f"  Created demo user {DEMO_USER_ID} ({DEMO_EMAIL})")


# ---------------------------------------------------------------------------
# Step 3: Score and seed one dataset (async)
# ---------------------------------------------------------------------------

async def _score_and_insert(
    filename: str,
    content: bytes,
    dry_run: bool,
) -> Optional[Dict]:
    """
    Run the full v2 pipeline on one dataset.
    Returns a result dict for reporting, or None on hard failure.
    """
    ext = Path(filename).suffix.lower() or ".csv"

    # Parse
    try:
        df = pd.read_csv(io.BytesIO(content), low_memory=False, nrows=50_000, on_bad_lines="skip")
        if df.empty or df.shape[1] < 2:
            print(f"  SKIP (empty/single-col): {filename}")
            return None
        df.columns = [str(c).strip() for c in df.columns]
    except Exception as exc:
        print(f"  SKIP (parse error): {filename}: {exc}")
        return None

    n_rows, n_cols = len(df), len(df.columns)

    # Relevance gate (always run — this is the gate showcase)
    rel_result = relevance_score_dataset(
        df=df,
        filename=filename,
        user_name=DEMO_DISPLAY,
        user_description="",
        user_tags=[],
    )
    relevance_score = rel_result["relevance_score"]
    accepted = rel_result["accepted"]

    if dry_run:
        gate_verdict = "ACCEPTED" if accepted else f"REJECTED (relevance={relevance_score:.1f})"
        print(f"  [DRY] {filename}: {gate_verdict}")
        return {"filename": filename, "accepted": accepted, "relevance_score": relevance_score}

    dataset_id = str(uuid.uuid4())
    checksum = _checksum(content)
    mime = _mime_for_ext(ext)
    tags: List[str] = []
    description: str = ""
    overall_score = 0.0
    composite_score = 0.0
    grade = "Poor"
    storage_path: Optional[str] = None
    audit_result = None

    if not accepted:
        # Rejected path — insert with status='rejected', all scores=0
        repo.insert_dataset(
            owner_id=DEMO_USER_ID,
            filename=filename,
            mime_type=mime,
            size_bytes=len(content),
            checksum=checksum,
            n_rows=n_rows,
            n_cols=n_cols,
            dataset_type="tabular",
            tags=[],
            description=rel_result["gate_message"][:300],
            storage_path=None,
            status="rejected",
            rejection_reason=rel_result["gate_message"],
            composite_score=0.0,
            grade="Poor",
            relevance_score=0.0,
            overall_score=0.0,
        )
        print(f"  [REJECTED] {filename} | relevance={relevance_score:.1f}")
        return {
            "filename": filename,
            "status": "rejected",
            "relevance_score": 0.0,
            "overall_score": 0.0,
            "rank": 0,
            "tags": [],
        }

    # Accepted path — full quality scoring
    try:
        audit_result = await run_audit(
            df=df,
            filename=filename,
            label_col=None,
            timestamp_col=None,
            target_auc=0.80,
        )
    except Exception as exc:
        print(f"  WARN: scorer failed for {filename}: {exc}")
        # Insert as accepted but without full audit (best-effort)
        composite_score = 50.0
        grade = "Fair"
        audit_result = None

    if audit_result:
        composite_score = audit_result.composite_score
        grade = audit_result.grade

    # Ranking factors
    raw_sub: Dict = {}
    domain_pdm_raw: Dict = {}
    domain_pdm_score: Optional[float] = None
    dataset_type_str = "tabular"

    if audit_result:
        raw_sub = {k: v.model_dump() for k, v in audit_result.sub_scores.__dict__.items() if v is not None}
        domain_pdm_score = (
            audit_result.sub_scores.domain_pdm.score
            if audit_result.sub_scores.domain_pdm else None
        )
        domain_pdm_raw = (
            audit_result.sub_scores.domain_pdm.raw
            if audit_result.sub_scores.domain_pdm and audit_result.sub_scores.domain_pdm.raw
            else {}
        )
        dataset_type_str = audit_result.dataset_type

    feature_richness = compute_feature_richness(
        df=df,
        dataset_type=dataset_type_str,
        label_col=None,
        timestamp_col=None,
        raw_sub_scores=raw_sub,
    )
    ps_alignment = compute_ps_alignment(
        df=df,
        dataset_type=dataset_type_str,
        label_col=None,
        timestamp_col=None,
        raw_kb_evidence=rel_result.get("raw_kb", {}),
        domain_pdm_raw=domain_pdm_raw,
    )
    overall_score = compute_overall_score(
        relevance_score=relevance_score,
        quality_score=composite_score,
        domain_pdm_score=domain_pdm_score,
        feature_richness=feature_richness,
        ps_alignment=ps_alignment,
        dataset_type=dataset_type_str,
    )

    # Auto-tags + description
    tags = _auto_tags(df, rel_result)
    description = _auto_description(df, rel_result, n_rows, n_cols)

    # Upload to Storage
    try:
        storage_path = storage_supa.upload_file(
            owner_id=DEMO_USER_ID,
            dataset_id=dataset_id,
            filename=filename,
            content=content,
            mime_type=mime,
        )
    except Exception as exc:
        print(f"  WARN: storage upload failed for {filename}: {exc}")
        storage_path = None

    # Insert dataset row (with pre-computed scores)
    with pg_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO public.datasets (
                id, owner_id, filename, mime_type, size_bytes, checksum,
                n_rows, n_cols, dataset_type, tags, description,
                storage_path, status,
                composite_score, grade, relevance_score, overall_score,
                upload_date, scored_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s,
                %s, %s, %s, %s,
                now(), now()
            )
            """,
            (
                dataset_id, DEMO_USER_ID, filename, mime, len(content), checksum,
                n_rows, n_cols, dataset_type_str, tags, description,
                storage_path, "accepted",
                composite_score, grade, relevance_score, overall_score,
            ),
        )

    # Insert audit_report
    if audit_result:
        ss = audit_result.sub_scores
        repo.insert_audit_report(
            dataset_id=dataset_id,
            full_report=audit_result.model_dump(),
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
            readiness_pct=audit_result.readiness.readiness_pct if audit_result.readiness else None,
            baseline_auc=audit_result.readiness.baseline_auc if audit_result.readiness else None,
        )

    print(
        f"  [ACCEPTED] {filename} | rel={relevance_score:.1f} | "
        f"q={composite_score:.1f} | overall={overall_score:.2f} | "
        f"tags={tags[:4]}"
    )
    return {
        "filename": filename,
        "status": "accepted",
        "relevance_score": relevance_score,
        "overall_score": overall_score,
        "composite_score": composite_score,
        "rank": 0,  # filled after recalculate
        "tags": tags,
        "dataset_id": dataset_id,
        "storage_path": storage_path,
    }


# ---------------------------------------------------------------------------
# Main seeding loop
# ---------------------------------------------------------------------------

async def seed_all(dry_run: bool) -> List[Dict]:
    # Build file list
    accepted_files: List[Tuple[str, bytes]] = []

    # By-equipment CSVs (primary steel source)
    for name in _BY_EQ_CANDIDATES:
        p = FLAGSHIP_BY_EQ / name
        if p.is_file():
            data = p.read_bytes()
            if len(data) > 100:
                accepted_files.append((name, data))
        else:
            print(f"  INFO: by_equipment file not found: {p}")

    # Steel samples (secondary source)
    for name in _SAMPLE_CANDIDATES:
        p = SAMPLES_DIR / name
        if p.is_file():
            data = p.read_bytes()
            if len(data) > 100:
                accepted_files.append((name, data))
        else:
            print(f"  INFO: sample file not found: {p}")

    # Rejection showcase datasets
    rejected_files: List[Tuple[str, bytes]] = [
        _make_synthetic_iris_csv(),
        _make_generic_tabular_csv(),
    ]
    # Also add good_tabular.csv from samples if it exists
    gt = SAMPLES_DIR / "good_tabular.csv"
    if gt.is_file():
        rejected_files.append(("good_tabular.csv", gt.read_bytes()))

    print(f"\n=== ACCEPTED candidates: {len(accepted_files)} files ===")
    print(f"=== REJECTED showcase:   {len(rejected_files)} files ===\n")

    results: List[Dict] = []

    # Process accepted files
    for fname, content in accepted_files:
        r = await _score_and_insert(fname, content, dry_run)
        if r:
            results.append(r)

    # Process rejection files
    for fname, content in rejected_files:
        r = await _score_and_insert(fname, content, dry_run)
        if r:
            results.append(r)

    return results


# ---------------------------------------------------------------------------
# Verification query
# ---------------------------------------------------------------------------

def verify_board() -> List[Dict]:
    """Query the board and return rows for reporting."""
    with pg_conn() as conn:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(
            """
            SELECT filename, status, relevance_score, overall_score, rank, tags,
                   n_rows, n_cols
            FROM public.datasets
            WHERE owner_id = %s
              AND status != 'deleted'
            ORDER BY CASE WHEN status='accepted' THEN rank ELSE 9999 END NULLS LAST,
                     overall_score DESC NULLS LAST
            """,
            (DEMO_USER_ID,),
        )
        return [dict(r) for r in cur.fetchall()]


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Idempotent EDITH DataForge demo board seeder"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print what would happen without writing to DB or Storage"
    )
    args = parser.parse_args()
    dry_run = args.dry_run

    if dry_run:
        print("\n=== DRY RUN MODE — no writes will happen ===\n")
    else:
        print("\n=== LIVE MODE — writing to Supabase ===\n")

    # Boot embeddings model (needed for relevance gate)
    print("[0] Loading embeddings model...")
    load_embeddings_model()
    precompute_query_embeddings()
    print("    Done.")

    # Step 1: Clear legacy + demo rows
    print("\n[1] Clearing legacy backfill + existing demo rows...")
    cleared = clear_legacy_and_demo(dry_run)
    print(f"    Cleared {cleared} rows.")

    # Step 2: Ensure demo user
    print("\n[2] Ensuring demo auth user...")
    ensure_demo_user(dry_run)

    # Step 3 + 4: Seed
    print("\n[3] Seeding datasets...")
    results = asyncio.run(seed_all(dry_run))
    print(f"\n    Processed {len(results)} datasets total.")

    if dry_run:
        print("\n=== DRY RUN complete — no data written ===")
        return

    # Step 5: Recompute ranks
    print("\n[4] Recomputing global ranks...")
    repo.recalculate_ranks()
    print("    Done.")

    # Step 6: Verify
    print("\n[5] Verification query:\n")
    rows = verify_board()
    accepted_rows = [r for r in rows if r["status"] == "accepted"]
    rejected_rows = [r for r in rows if r["status"] == "rejected"]

    print(f"{'Filename':<55} {'Status':<10} {'Rel':>6} {'Overall':>8} {'Rank':>5} {'Tags'}")
    print("-" * 120)
    for r in rows:
        fname = r["filename"][:54]
        status = r["status"]
        rel = float(r["relevance_score"] or 0)
        overall = float(r["overall_score"] or 0)
        rank = r["rank"] or 0
        tags = str(r["tags"] or [])[:40]
        print(f"{fname:<55} {status:<10} {rel:>6.1f} {overall:>8.2f} {rank:>5}  {tags}")

    print(f"\n--- Summary ---")
    print(f"  Accepted rows:  {len(accepted_rows)}")
    print(f"  Rejected rows:  {len(rejected_rows)}")

    # Integrity checks
    ok = True
    # 1. No accepted row with relevance_score = 0
    bad_accepted = [r for r in accepted_rows if float(r["relevance_score"] or 0) < 30]
    if bad_accepted:
        print(f"\n  FAIL: {len(bad_accepted)} accepted row(s) have relevance < 30:")
        for r in bad_accepted:
            print(f"    {r['filename']}: relevance={r['relevance_score']}")
        ok = False
    else:
        print(f"  PASS: all accepted rows have relevance >= 30")

    # 2. All rejected rows have relevance_score = 0 and rank = 0
    bad_rejected = [r for r in rejected_rows if float(r["relevance_score"] or 0) > 0 or (r["rank"] or 0) != 0]
    if bad_rejected:
        print(f"\n  FAIL: {len(bad_rejected)} rejected row(s) have non-zero relevance or rank:")
        for r in bad_rejected:
            print(f"    {r['filename']}: relevance={r['relevance_score']}, rank={r['rank']}")
        ok = False
    else:
        print(f"  PASS: all rejected rows have relevance=0, rank=0")

    # 3. Accepted rows have non-empty tags
    empty_tags_accepted = [r for r in accepted_rows if not r.get("tags")]
    if empty_tags_accepted:
        print(f"\n  WARN: {len(empty_tags_accepted)} accepted row(s) have empty tags")
    else:
        print(f"  PASS: all accepted rows have non-empty tags")

    # 4. Ranks are contiguous (1..N) over accepted rows
    ranks = sorted([r["rank"] for r in accepted_rows if r["rank"]])
    expected = list(range(1, len(ranks) + 1))
    if ranks != expected:
        print(f"\n  WARN: ranks not fully contiguous — got {ranks}, expected {expected}")
    else:
        print(f"  PASS: ranks are contiguous 1..{len(ranks)}")

    # 5. Storage files exist for accepted rows
    print("\n  Checking storage files for accepted rows...")
    with pg_conn() as conn:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(
            "SELECT filename, storage_path FROM public.datasets WHERE owner_id=%s AND status='accepted'",
            (DEMO_USER_ID,),
        )
        accepted_db_rows = [dict(r) for r in cur.fetchall()]

    missing_storage = [r for r in accepted_db_rows if not r.get("storage_path")]
    if missing_storage:
        print(f"  WARN: {len(missing_storage)} accepted row(s) have no storage_path:")
        for r in missing_storage:
            print(f"    {r['filename']}")
    else:
        print(f"  PASS: all {len(accepted_db_rows)} accepted rows have storage_path set")

    if ok:
        print(f"\n=== SEED COMPLETE — board is clean and ready for demo ===")
    else:
        print(f"\n=== SEED COMPLETE — check FAILs above ===")
        sys.exit(1)


if __name__ == "__main__":
    main()
