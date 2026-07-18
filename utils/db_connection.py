"""
utils/db_connection.py
------------------------
Centralized, database-agnostic connection handling.

Default: SQLite (zero setup — works immediately with the bundled sample DB).
To switch to PostgreSQL or MySQL, set environment variables (see README.md)
and change DB_TYPE below or via .env — the rest of the app doesn't change,
because everything goes through get_connection() / run_query() / run_action().
"""

import os
import sqlite3
import pandas as pd
from contextlib import contextmanager

# ---- Configuration -------------------------------------------------
DB_TYPE = os.getenv("DB_TYPE", "sqlite")   # "sqlite" | "postgresql" | "mysql"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SQLITE_PATH = os.getenv("SQLITE_PATH", os.path.join(BASE_DIR, "data", "cricbuzz_livestats.db"))

PG_CONFIG = {
    "host": os.getenv("PG_HOST", "localhost"),
    "port": os.getenv("PG_PORT", "5432"),
    "dbname": os.getenv("PG_DB", "cricbuzz_livestats"),
    "user": os.getenv("PG_USER", "postgres"),
    "password": os.getenv("PG_PASSWORD", ""),
}

MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "port": os.getenv("MYSQL_PORT", "3306"),
    "database": os.getenv("MYSQL_DB", "cricbuzz_livestats"),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", ""),
}


def get_raw_connection():
    """Return a raw DB-API connection based on DB_TYPE."""
    if DB_TYPE == "sqlite":
        conn = sqlite3.connect(SQLITE_PATH)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    elif DB_TYPE == "postgresql":
        import psycopg2
        return psycopg2.connect(**PG_CONFIG)
    elif DB_TYPE == "mysql":
        import mysql.connector
        return mysql.connector.connect(**MYSQL_CONFIG)
    else:
        raise ValueError(f"Unsupported DB_TYPE: {DB_TYPE}")


@contextmanager
def get_connection():
    """Context-managed connection: `with get_connection() as conn: ...`"""
    conn = get_raw_connection()
    try:
        yield conn
    finally:
        conn.close()


def run_query(sql: str, params: tuple = ()) -> pd.DataFrame:
    """Run a SELECT query and return results as a pandas DataFrame."""
    with get_connection() as conn:
        return pd.read_sql_query(sql, conn, params=params)


def run_action(sql: str, params: tuple = ()) -> int:
    """Run an INSERT/UPDATE/DELETE. Returns affected row count (or new row id for inserts)."""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(sql, params)
        conn.commit()
        rowid = cur.lastrowid if hasattr(cur, "lastrowid") else None
        return rowid if rowid else cur.rowcount


def test_connection() -> tuple[bool, str]:
    """Quick health check used by the Home page."""
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM players")
            count = cur.fetchone()[0]
        return True, f"Connected ({DB_TYPE}) — {count} players in database"
    except Exception as e:
        return False, str(e)