"""
app.py — Main entry point for the Cricbuzz LiveStats Streamlit app.

Run with:  streamlit run app.py
"""

import streamlit as st
from dotenv import load_dotenv

load_dotenv()  # reads .env in the project root and sets env vars from it

st.set_page_config(
    page_title="Cricbuzz LiveStats",
    page_icon="🏏",
    layout="wide",
)

home_page = st.Page("pages/home.py", title="Home", icon="🏠", default=True)
live_page = st.Page("pages/live_matches.py", title="Live Matches", icon="⚡")
stats_page = st.Page("pages/top_stats.py", title="Top Player Stats", icon="📊")
sql_page = st.Page("pages/sql_queries.py", title="SQL Queries & Analytics", icon="🔍")
crud_page = st.Page("pages/crud_operations.py", title="CRUD Operations", icon="🛠")

pg = st.navigation([home_page, live_page, stats_page, sql_page, crud_page])
pg.run()