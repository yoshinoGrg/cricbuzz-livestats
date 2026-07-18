import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.db_connection import test_connection, run_query

st.title("🏏 Cricbuzz LiveStats")
st.subheader("Real-Time Cricket Insights & SQL-Based Analytics")

st.markdown("""
Welcome! This dashboard combines **live data from the Cricbuzz API** with a
**SQL database** of historical match and player data to deliver:

- ⚡ **Live Matches** — real-time scores, scorecards, match status
- 📊 **Top Player Stats** — leaderboards fetched from the Cricbuzz API
- 🔍 **SQL Queries & Analytics** — 25 SQL questions from beginner to advanced
- 🛠 **CRUD Operations** — add, update, delete player records
""")

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🩺 System Status")
    ok, msg = test_connection()
    if ok:
        st.success(msg)
    else:
        st.error(f"Database connection failed: {msg}")

    api_key_set = bool(os.getenv("CRICBUZZ_API_KEY"))
    if not api_key_set:
        try:
            api_key_set = bool(st.secrets.get("CRICBUZZ_API_KEY"))
        except Exception:
            api_key_set = False
    if api_key_set:
        st.success("Cricbuzz API key detected")
    else:
        st.warning("No Cricbuzz API key found — Live Matches / Top Stats pages will show setup instructions. See README.md.")

with col2:
    st.markdown("### 📈 Database Snapshot")
    try:
        teams = run_query("SELECT COUNT(*) AS n FROM teams").iloc[0]["n"]
        players = run_query("SELECT COUNT(*) AS n FROM players").iloc[0]["n"]
        matches = run_query("SELECT COUNT(*) AS n FROM matches").iloc[0]["n"]
        venues = run_query("SELECT COUNT(*) AS n FROM venues").iloc[0]["n"]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Teams", teams)
        c2.metric("Players", players)
        c3.metric("Matches", matches)
        c4.metric("Venues", venues)
    except Exception as e:
        st.error(f"Could not load snapshot: {e}")

st.divider()

st.markdown("### 🗂 Project Structure")
st.code("""
cricbuzz_livestats/
├── app.py                     # Main entry point
├── requirements.txt
├── README.md
├── pages/
│   ├── home.py
│   ├── live_matches.py        # Live data from Cricbuzz API
│   ├── top_stats.py           # Leaderboards from Cricbuzz API
│   ├── sql_queries.py         # 25 SQL analytics questions
│   └── crud_operations.py     # Create / Read / Update / Delete players
├── utils/
│   ├── db_connection.py       # Database-agnostic connection layer
│   ├── cricbuzz_api.py        # Cricbuzz REST API client
│   └── sql_queries.py         # The 25 SQL queries as data
├── data/
│   ├── schema.sql
│   ├── generate_sample_data.py
│   └── cricbuzz_livestats.db
└── notebooks/
    └── data_fetching.ipynb
""", language="text")

st.info("Use the sidebar to navigate between pages.")
