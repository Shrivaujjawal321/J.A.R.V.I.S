"""
supa/storage.py — Supabase Storage operations for EDITH DataForge.

All operations use the SERVICE KEY (private bucket requires service-role).
Signed URLs (1h TTL) are returned for downloads instead of proxying bytes.

Bucket: 'datasets' (private, created via apply_migration.py)
Path convention: {owner_id}/{dataset_id}/{filename}
"""
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import httpx

SUPABASE_URL: str = os.environ.get("SUPABASE_URL", "")
SIGNED_URL_EXPIRY_SECONDS = 3600  # 1 hour

BUCKET = "datasets"


def _headers() -> dict:
    service_key = os.environ["SUPABASE_SERVICE_KEY"]
    return {
        "Authorization": f"Bearer {service_key}",
        "apikey": service_key,
    }


def _storage_base() -> str:
    return f"{SUPABASE_URL}/storage/v1"


def upload_file(
    owner_id: str,
    dataset_id: str,
    filename: str,
    content: bytes,
    mime_type: str = "text/csv",
) -> str:
    """
    Upload raw file bytes to the private 'datasets' bucket.
    Returns the storage path: {owner_id}/{dataset_id}/{filename}
    Raises RuntimeError on failure.
    """
    storage_path = f"{owner_id}/{dataset_id}/{filename}"
    url = f"{_storage_base()}/object/{BUCKET}/{storage_path}"

    headers = _headers()
    headers["Content-Type"] = mime_type
    headers["x-upsert"] = "true"  # idempotent on re-upload

    with httpx.Client(timeout=60) as client:
        r = client.post(url, content=content, headers=headers)

    if r.status_code not in (200, 201):
        raise RuntimeError(
            f"Storage upload failed [{r.status_code}]: {r.text[:300]}"
        )

    return storage_path


def get_signed_url(storage_path: str, expiry_seconds: int = SIGNED_URL_EXPIRY_SECONDS) -> dict:
    """
    Generate a signed download URL for a private object.
    Returns: {"signed_url": str, "expires_at": str (ISO-8601)}
    Raises RuntimeError on failure.
    """
    url = f"{_storage_base()}/object/sign/{BUCKET}/{storage_path}"

    with httpx.Client(timeout=15) as client:
        r = client.post(
            url,
            json={"expiresIn": expiry_seconds},
            headers=_headers(),
        )

    if r.status_code != 200:
        raise RuntimeError(
            f"Signed URL generation failed [{r.status_code}]: {r.text[:300]}"
        )

    data = r.json()
    signed_path = data.get("signedURL") or data.get("signedUrl") or ""
    # Supabase returns a relative path; prefix with project URL if needed
    if signed_path.startswith("/"):
        signed_url = f"{SUPABASE_URL}{signed_path}"
    else:
        signed_url = signed_path

    expires_at = (
        datetime.now(timezone.utc) + timedelta(seconds=expiry_seconds)
    ).isoformat()

    return {"signed_url": signed_url, "expires_at": expires_at}


def delete_file(storage_path: str) -> bool:
    """
    Remove an object from the bucket (called on dataset soft-delete).
    Returns True on success, False if not found (idempotent).
    Raises RuntimeError on other errors.
    Uses httpx.request (not client.delete) because httpx DELETE doesn't accept json= param.
    """
    url = f"{_storage_base()}/object/{BUCKET}"
    headers = _headers()
    headers["Content-Type"] = "application/json"
    with httpx.Client(timeout=15) as client:
        r = client.request(
            "DELETE",
            url,
            json={"prefixes": [storage_path]},
            headers=headers,
        )

    if r.status_code == 404:
        return False
    if r.status_code not in (200, 204):
        raise RuntimeError(
            f"Storage delete failed [{r.status_code}]: {r.text[:300]}"
        )
    return True
