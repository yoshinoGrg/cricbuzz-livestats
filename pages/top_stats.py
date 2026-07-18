import streamlit as st
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.cricbuzz_api import get_top_batting_stats

st.title("📊 Top Player Stats")
st.caption("Player rankings fetched live from the Cricket Live Line API.")

st.info("Note: the /playerRanking/{id} endpoint's id parameter meaning (format/discipline) is unverified -- adjust ranking_id below once confirmed in the RapidAPI docs.")

ranking_id = st.text_input("Ranking ID", value="1", help="Try different values (1, 2, 3...) to see which ranking list each one returns.")

data, error = get_top_batting_stats(ranking_id)

if error:
    st.warning(error)
    st.markdown("""
    **To enable this page:**
    1. Confirm your Cricket Live Line subscription is active on RapidAPI
    2. Add your key to `.env` as `CRICBUZZ_API_KEY=your_key`
    3. Restart the app

    Meanwhile, explore similar leaderboards using the bundled sample database on the
    **SQL Queries & Analytics** page (e.g. Question 3: *Top 10 ODI run scorers*).
    """)
else:
    if isinstance(data, list) and data:
        df = pd.DataFrame(data)
        # Keep the most relevant columns first if they exist
        preferred_cols = [c for c in ["rank", "name", "country", "rating", "player_id"] if c in df.columns]
        other_cols = [c for c in df.columns if c not in preferred_cols and c != "img"]
        df = df[preferred_cols + other_cols]
        st.dataframe(df, width='stretch')
    else:
        st.info("No ranking data returned for this ID.")
        st.json(data)