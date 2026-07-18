"""
app.py — Main entry point for the Cricbuzz LiveStats Streamlit app.

Run with:  streamlit run app.py
"""

import streamlit as st
import os, subprocess, sys, sqlite3
from dotenv import load_dotenv

load_dotenv()  # reads .env in the project root and sets env vars from it

st.set_page_config(
    page_title="Cricbuzz LiveStats",
    page_icon="🏏",
    layout="wide",
)

# On a fresh deploy (e.g. Streamlit Community Cloud), the repo won't include
# the generated .db file (it's in .gitignore). Build it automatically the
# first time the app starts so the SQL/CRUD pages have data to work with.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "cricbuzz_livestats.db")
GENERATOR_SCRIPT = os.path.join(BASE_DIR, "data", "generate_sample_data.py")


def _database_needs_build(db_path: str) -> bool:
    """
    Check the *content* of the database, not just whether the file exists.
    A stray/empty .db file (e.g. from a prior failed run) would pass a plain
    os.path.exists() check but still have no tables -- so check for the
    'teams' table specifically.
    """
    if not os.path.exists(db_path):
        return True
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='teams'")
        found = cur.fetchone() is not None
        conn.close()
        return not found
    except Exception:
        return True


if _database_needs_build(DB_PATH):
    with st.spinner("First-time setup: building sample database..."):
        result = subprocess.run(
            [sys.executable, GENERATOR_SCRIPT],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            st.error("Failed to build the sample database on startup. Details below:")
            st.code((result.stdout or "") + "\n" + (result.stderr or ""))
            st.stop()

home_page = st.Page("pages/home.py", title="Home", icon="🏠", default=True)
live_page = st.Page("pages/live_matches.py", title="Live Matches", icon="⚡")
stats_page = st.Page("pages/top_stats.py", title="Top Player Stats", icon="📊")
sql_page = st.Page("pages/sql_queries.py", title="SQL Queries & Analytics", icon="🔍")
crud_page = st.Page("pages/crud_operations.py", title="CRUD Operations", icon="🛠")

pg = st.navigation([home_page, live_page, stats_page, sql_page, crud_page])
pg.run()
