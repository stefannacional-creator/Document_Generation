import os

import psycopg2
from supabase import create_client

BUCKET_NAME = os.getenv("SUPABASE_STORAGE_BUCKET", "documents")

_CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS documents (
    id              uuid primary key default gen_random_uuid(),
    user_id         uuid,
    title           text not null,
    document_type   text not null,
    topic           text not null,
    style           text not null default 'professional',
    file_name       text not null unique,
    storage_url     text not null,
    file_size       integer not null,
    created_at      timestamptz not null default now()
);

CREATE INDEX IF NOT EXISTS documents_user_id_idx ON documents(user_id);
"""


def run_setup() -> None:
    _ensure_bucket()
    _ensure_table()


def _ensure_bucket() -> None:
    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_SERVICE_KEY", "")
    client = create_client(url, key)
    try:
        client.storage.create_bucket(BUCKET_NAME, options={"public": True})
    except Exception:
        pass  # bucket already exists


def _ensure_table() -> None:
    database_url = os.getenv("DATABASE_URL", "")
    conn = psycopg2.connect(database_url)
    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            cur.execute(_CREATE_TABLE_SQL)
    finally:
        conn.close()
