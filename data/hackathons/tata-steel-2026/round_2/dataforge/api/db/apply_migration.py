"""
Apply DB migration 001_init.sql to live Supabase Postgres.
Run: /home/ujjwal/Documents/J.A.R.V.I.S./.venv/bin/python db/apply_migration.py
"""
from __future__ import annotations
import os
import sys
from pathlib import Path

# Load .env from api/ directory
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

import psycopg2
from psycopg2.extras import RealDictCursor


def get_conn():
    return psycopg2.connect(
        host="db.odzpjbwpiidickjilkkf.supabase.co",
        port=5432,
        user="postgres",
        password=os.environ["SUPABASE_DB_PASSWORD"],
        dbname="postgres",
        sslmode="require",
    )


def apply_migration():
    sql_path = Path(__file__).parent / "migrations" / "001_init.sql"
    sql = sql_path.read_text()

    print(f"Applying migration: {sql_path.name}")
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
        print("Migration applied successfully.")

        # Verify: list created tables
        cur.execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
            """
        )
        tables = [r[0] for r in cur.fetchall()]
        print(f"Tables in public schema: {tables}")

        # Verify RLS is enabled
        cur.execute(
            """
            SELECT relname, relrowsecurity
            FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE n.nspname = 'public' AND c.relkind = 'r'
            ORDER BY relname
            """
        )
        rls_rows = cur.fetchall()
        print("RLS status:")
        for name, rls in rls_rows:
            print(f"  {name}: RLS={'ON' if rls else 'OFF'}")

        # Verify functions
        cur.execute(
            """
            SELECT routine_name
            FROM information_schema.routines
            WHERE routine_schema = 'public' AND routine_type = 'FUNCTION'
            ORDER BY routine_name
            """
        )
        funcs = [r[0] for r in cur.fetchall()]
        print(f"Functions: {funcs}")

        cur.close()
    except Exception as e:
        conn.rollback()
        print(f"ERROR: {e}")
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    apply_migration()
