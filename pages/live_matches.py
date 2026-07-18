import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.cricbuzz_api import get_live_matches, get_recent_matches, get_upcoming_matches, get_match_scorecard

st.title("⚡ Live Matches")
st.caption("Live data pulled from the Cricket Live Line API.")

tab1, tab2, tab3 = st.tabs(["🔴 Live", "✅ Recent", "🗓 Upcoming"])


def render_match_card(m: dict):
    """Render one match dict using this API's real field names."""
    team_a = m.get("team_a", "Team A")
    team_b = m.get("team_b", "Team B")
    status = m.get("match_status", "")
    series = m.get("series", "")
    match_name = m.get("matchs", "")

    header = f"{team_a} vs {team_b} — {status}"
    with st.expander(header):
        if series:
            st.caption(f"{series} · {match_name}")

        col1, col2 = st.columns(2)
        with col1:
            st.metric(team_a, m.get("team_a_scores") or "Yet to bat")
        with col2:
            st.metric(team_b, m.get("team_b_scores") or "Yet to bat")

        if m.get("venue"):
            st.write(f"**Venue:** {m['venue']}")
        if m.get("toss"):
            st.write(f"**Toss:** {m['toss']}")
        if m.get("need_run_ball"):
            st.info(m["need_run_ball"])
        if m.get("result"):
            st.success(m["result"])

        match_id = m.get("match_id")
        if match_id and st.button("View full scorecard", key=f"scard_{match_id}"):
            sc, err = get_match_scorecard(match_id)
            if err:
                st.error(err)
            else:
                st.json(sc)


def render_matches(data, error, empty_msg):
    if error:
        st.warning(error)
        st.markdown("""
        **To enable live data:**
        1. Confirm your Cricket Live Line subscription is active on RapidAPI
        2. Add your key to `.env` as `CRICBUZZ_API_KEY=your_key`
        3. Restart the app
        """)
        return
    if not data:
        st.info(empty_msg)
        return
    if not isinstance(data, list):
        st.warning("Unexpected response shape from the API:")
        st.json(data)
        return

    for m in data:
        render_match_card(m)


with tab1:
    data, error = get_live_matches()
    render_matches(data, error, "No live matches right now.")

with tab2:
    data, error = get_recent_matches()
    render_matches(data, error, "No recent matches found. (Note: /recentMatches path is unverified -- if this errors, check the exact endpoint name in the RapidAPI sidebar.)")

with tab3:
    data, error = get_upcoming_matches()
    render_matches(data, error, "No upcoming matches found. (Note: /upcomingMatches path is unverified -- if this errors, check the exact endpoint name in the RapidAPI sidebar.)")