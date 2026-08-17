"""
scripts/migrate_jsonl_to_supabase.py
Backfill existing data/audits.jsonl records into Supabase Postgres + Storage.

Usage:
    /home/ujjwal/Documents/J.A.R.V.I.S./.venv/bin/python scripts/migrate_jsonl_to_supabase.py [--dry-run]

Creates a legacy service user in auth.users (EDITH_LEGACY_USER_ID in .env),
inserts dataset + audit_report rows, uploads files from data/files/ to the bucket.
Idempotent: skips records already present by checksum.

Run this ONCE after the Supabase migration is verified and before flipping
EDITH_PERSISTENCE_BACKEND=supabase.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import uuid
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

import psycopg2
import psycopg2.extras
import httpx

SUPA_URL = os.environ["SUPABASE_URL"]
SERVICE_KEY = os.environ["SUPABASE_SERVICE_KEY"]
DB_PASSWORD = os.environ["SUPABASE_DB_PASSWORD"]
LEGACY_USER_ID = os.environ.get("EDITH_LEGACY_USER_ID", "d0000000-0000-0000-0000-000000000099")
LEGACY_EMAIL = "legacy@edith.app"

API_DIR = Path(__file__).parent.parent
AUDITS_FILE = API_DIR / "data" / "audits.jsonl"
FILES_DIR = API_DIR / "data" / "files"

HEADERS = {"Authorization": f"Bearer {SERVICE_KEY}", "apikey": SERVICE_KEY}


def get_conn():
    return psycopg2.connect(
        host="db.odzpjbwpiidickjilkkf.supabase.co",
        port=5432,
        user="postgres",
        password=DB_PASSWORD,
        dbname="postgres",
        sslmode="require",
    )


def ensure_legacy_user(conn) -> None:
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO auth.users (id, email, created_at, updated_at, aud, role,
            confirmation_token, recovery_token, email_change_token_new, email_change,
            raw_app_meta_data, raw_user_meta_data)
        VALUES (%s, %s, now(), now(), %s, %s, %s, %s, %s, %s, %s::jsonb, %s::jsonb)
        ON CONFLICT (id) DO NOTHING
        """,
        (LEGACY_USER_ID, LEGACY_EMAIL, "authenticated", "authenticated", "", "", "", "", "{}", "{}"),
    )
    conn.commit()
    print(f"Legacy user ensured: {LEGACY_USER_ID}")


def upload_to_storage(storage_path: str, content: bytes, mime: str = "text/csv") -> bool:
    h = dict(HEADERS)
    h["Content-Type"] = mime
    h["x-upsert"] = "true"
    r = httpx.post(
        f"{SUPA_URL}/storage/v1/object/datasets/{storage_path}",
        content=content,
        headers=h,
        timeout=60,
    )
    return r.status_code in (200, 201)


def migrate_record(conn, record: dict, dry_run: bool) -> bool:
    """
    Migrate one JSONL record to Postgres + Storage.
    Returns True on success, False on skip/failure.
    """
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    audit_id = record.get("audit_id", "")
    filename = record.get("filename", "unknown.csv")
    ext = Path(filename).suffix.lower() or ".csv"

    # Find the stored file
    file_path = None
    for p in [
        FILES_DIR / f"{audit_id}{ext}",
        *list(FILES_DIR.glob(f"{audit_id}.*")),
    ]:
        if p.is_file():
            file_path = p
            break

    content = file_path.read_bytes() if file_path else b""
    checksum = hashlib.sha256(content).hexdigest() if content else ("0" * 64)
    size_bytes = len(content)

    # Idempotency: skip if checksum already present
    cur.execute(
        "SELECT id FROM public.datasets WHERE checksum=%s AND owner_id=%s LIMIT 1",
        (checksum, LEGACY_USER_ID),
    )
    if cur.fetchone():
        print(f"  SKIP (already exists): {filename}")
        return False

    dataset_id = str(uuid.uuid4())
    storage_path = f"{LEGACY_USER_ID}/{dataset_id}/{filename}"

    if not dry_run and content:
        if not upload_to_storage(storage_path, content):
            print(f"  WARN: Storage upload failed for {filename}")
            storage_path = None

    grade = record.get("grade", "Fair")
    composite = record.get("composite_score", 0.0)
    overall = record.get("overall_score") or composite
    relevance = record.get("relevance_score", 0.0)
    status = record.get("status", "accepted")
    upload_date = record.get("created_at", "now()")
    n_rows = record.get("n_rows", 0)
    n_cols = record.get("n_cols", 0)
    dataset_type = record.get("dataset_type", "tabular")

    if not dry_run:
        cur.execute(
            """
            INSERT INTO public.datasets (
                id, owner_id, filename, mime_type, size_bytes, checksum,
                n_rows, n_cols, dataset_type, tags, description,
                storage_path, status, composite_score, grade,
                overall_score, relevance_score, upload_date, scored_at
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                dataset_id, LEGACY_USER_ID, filename, "text/csv", size_bytes, checksum,
                n_rows, n_cols, dataset_type, [], f"Migrated legacy dataset: {filename}",
                storage_path, status, composite, grade,
                overall, relevance, upload_date, upload_date,
            ),
        )
        # Minimal audit report (no full_report JSON in old JSONL)
        report_id = str(uuid.uuid4())
        cur.execute(
            """
            INSERT INTO public.audit_reports (id, dataset_id, readiness_pct, full_report)
            VALUES (%s, %s, %s, %s::jsonb)
            """,
            (report_id, dataset_id, 0.0, json.dumps(record)),
        )
        conn.commit()

    print(f"  {'[DRY]' if dry_run else '[OK]'} Migrated: {filename} → {dataset_id}")
    return True


def main():
    parser = argparse.ArgumentParser(description="Backfill JSONL to Supabase")
    parser.add_argument("--dry-run", action="store_true", help="Print what would be done without writing")
    args = parser.parse_args()

    if not AUDITS_FILE.exists():
        print(f"No audits file at {AUDITS_FILE}. Nothing to migrate.")
        return

    conn = get_conn()
    ensure_legacy_user(conn)

    records = []
    with open(AUDITS_FILE) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    pass

    print(f"Found {len(records)} records in {AUDITS_FILE}")
    migrated = 0
    for rec in records:
        try:
            if migrate_record(conn, rec, args.dry_run):
                migrated += 1
        except Exception as exc:
            print(f"  ERROR for {rec.get('filename', '?')}: {exc}")

    if not args.dry_run and migrated > 0:
        cur = conn.cursor()
        cur.execute("SELECT public.recalculate_dataset_ranks()")
        conn.commit()
        print("Ranks recalculated.")

    conn.close()
    print(f"\nDone. Migrated: {migrated}/{len(records)}")
    print("\nAfter verifying, set in .env:")
    print("  EDITH_PERSISTENCE_BACKEND=supabase")
    print("  EDITH_STORAGE_BACKEND=supabase")
    print("  EDITH_AUTH_REQUIRED=1")


if __name__ == "__main__":
    main()
