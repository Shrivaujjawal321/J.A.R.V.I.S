"""
supa/client.py — Supabase server-side clients.

Two clients:
  - service_client(): service-role key, bypasses RLS (privileged background ops)
  - anon_client(): anon key (used as request context; most auth ops go via JWT verify)

Connection pool for raw Postgres (psycopg2) is also provided here so all modules
share one pool instead of opening/closing connections per request.
"""
from __future__ import annotations

import os
from threading import Lock
from typing import Optional

from dotenv import load_dotenv
from pathlib import Path

# Load .env from api/ directory — safe to call multiple times (idempotent)
load_dotenv(Path(__file__).parent.parent / ".env")

# ── Supabase REST clients ────────────────────────────────────────────────────
from supabase import create_client, Client

_service_client: Optional[Client] = None
_anon_client: Optional[Client] = None
_client_lock = Lock()


def service_client() -> Client:
    """
    Supabase client using the service-role key.
    Bypasses RLS — ONLY use for server-side privileged operations
    (background scorer writes, admin reads, storage ops).
    NEVER expose this client to untrusted input paths.
    """
    global _service_client
    if _service_client is None:
        with _client_lock:
            if _service_client is None:
                _service_client = create_client(
                    os.environ["SUPABASE_URL"],
                    os.environ["SUPABASE_SERVICE_KEY"],
                )
    return _service_client


def anon_client() -> Client:
    """
    Supabase client using the anon/publishable key.
    Respects RLS — safe for public reads.
    """
    global _anon_client
    if _anon_client is None:
        with _client_lock:
            if _anon_client is None:
                _anon_client = create_client(
                    os.environ["SUPABASE_URL"],
                    os.environ["SUPABASE_ANON_KEY"],
                )
    return _anon_client


# ── psycopg2 connection pool ─────────────────────────────────────────────────
# Used by repo.py for all direct Postgres queries.
# ThreadedConnectionPool: min=1, max=10 connections.
from psycopg2.pool import ThreadedConnectionPool
from contextlib import contextmanager

_pg_pool: Optional[ThreadedConnectionPool] = None
_pool_lock = Lock()


def _pg_dsn() -> str:
    # Host/port/user are env-overridable so we can point at the IPv4 Supabase
    # pooler (Supavisor) in environments without IPv6 egress (e.g. HF Spaces).
    # Direct host `db.<ref>.supabase.co` is IPv6-only; pooler is IPv4.
    host = os.environ.get("SUPABASE_DB_HOST", "db.odzpjbwpiidickjilkkf.supabase.co")
    port = os.environ.get("SUPABASE_DB_PORT", "5432")
    user = os.environ.get("SUPABASE_DB_USER", "postgres")
    return (
        f"host={host} "
        f"port={port} "
        f"user={user} "
        f"password={os.environ['SUPABASE_DB_PASSWORD']} "
        f"dbname=postgres "
        f"sslmode=require"
    )


def get_pool() -> ThreadedConnectionPool:
    global _pg_pool
    if _pg_pool is None:
        with _pool_lock:
            if _pg_pool is None:
                _pg_pool = ThreadedConnectionPool(1, 10, dsn=_pg_dsn())
    return _pg_pool


@contextmanager
def pg_conn():
    """
    Context manager: acquire a psycopg2 connection from the pool,
    commit on success, rollback on error, return to pool always.

    Usage:
        with pg_conn() as conn:
            cur = conn.cursor()
            cur.execute(...)
            cur.fetchall()
    """
    pool = get_pool()
    conn = pool.getconn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        pool.putconn(conn)
