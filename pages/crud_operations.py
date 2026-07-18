import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.db_connection import run_query, run_action

st.title("🛠 CRUD Operations")
st.caption("Create, Read, Update, and Delete player records — form-based UI over the SQL database.")

tab_create, tab_read, tab_update, tab_delete = st.tabs(["➕ Create", "📖 Read", "✏️ Update", "🗑 Delete"])

ROLES = ["Batsman", "Bowler", "All-rounder", "Wicket-keeper"]
BAT_STYLES = ["Right-hand bat", "Left-hand bat"]
BOWL_STYLES = ["Right-arm fast", "Left-arm fast", "Right-arm off-break",
               "Left-arm orthodox", "Right-arm leg-break", "Left-arm chinaman", "None"]

# ---------------- CREATE ----------------
with tab_create:
    st.subheader("Add a new player")
    teams_df = run_query("SELECT team_id, team_name FROM teams ORDER BY team_name")
    with st.form("create_player_form", clear_on_submit=True):
        full_name = st.text_input("Full name*")
        country = st.text_input("Country*")
        role = st.selectbox("Playing role*", ROLES)
        bat_style = st.selectbox("Batting style", BAT_STYLES)
        bowl_style = st.selectbox("Bowling style", BOWL_STYLES)
        dob = st.date_input("Date of birth", value=None)
        team_name = st.selectbox("Team", teams_df["team_name"].tolist())
        submitted = st.form_submit_button("Add player")

        if submitted:
            if not full_name or not country:
                st.error("Full name and country are required.")
            else:
                team_id = int(teams_df.loc[teams_df["team_name"] == team_name, "team_id"].iloc[0])
                run_action(
                    """INSERT INTO players (full_name, country, playing_role, batting_style,
                       bowling_style, date_of_birth, team_id) VALUES (?,?,?,?,?,?,?)""",
                    (full_name, country, role, bat_style,
                     None if bowl_style == "None" else bowl_style,
                     dob.isoformat() if dob else None, team_id)
                )
                st.success(f"Added player: {full_name}")

# ---------------- READ ----------------
with tab_read:
    st.subheader("Browse players")
    col1, col2 = st.columns(2)
    with col1:
        country_filter = st.text_input("Filter by country (optional)")
    with col2:
        role_filter = st.selectbox("Filter by role (optional)", ["All"] + ROLES)

    sql = """SELECT p.player_id, p.full_name, p.country, p.playing_role,
                     p.batting_style, p.bowling_style, t.team_name
              FROM players p LEFT JOIN teams t ON t.team_id = p.team_id WHERE 1=1"""
    params = []
    if country_filter:
        sql += " AND p.country LIKE ?"
        params.append(f"%{country_filter}%")
    if role_filter != "All":
        sql += " AND p.playing_role = ?"
        params.append(role_filter)
    sql += " ORDER BY p.full_name"

    df = run_query(sql, tuple(params))
    st.dataframe(df, width='stretch')
    st.caption(f"{len(df)} player(s) found")

# ---------------- UPDATE ----------------
with tab_update:
    st.subheader("Update a player record")
    players_df = run_query("SELECT player_id, full_name FROM players ORDER BY full_name")
    player_label = st.selectbox(
        "Select player", players_df.apply(lambda r: f"{r['player_id']} — {r['full_name']}", axis=1).tolist()
    )
    if player_label:
        pid = int(player_label.split(" — ")[0])
        current = run_query("SELECT * FROM players WHERE player_id = ?", (pid,)).iloc[0]

        with st.form("update_player_form"):
            new_name = st.text_input("Full name", value=current["full_name"])
            new_country = st.text_input("Country", value=current["country"])
            new_role = st.selectbox("Playing role", ROLES, index=ROLES.index(current["playing_role"]) if current["playing_role"] in ROLES else 0)
            new_bat = st.selectbox("Batting style", BAT_STYLES, index=BAT_STYLES.index(current["batting_style"]) if current["batting_style"] in BAT_STYLES else 0)
            update_submitted = st.form_submit_button("Save changes")

            if update_submitted:
                run_action(
                    """UPDATE players SET full_name=?, country=?, playing_role=?, batting_style=?
                       WHERE player_id=?""",
                    (new_name, new_country, new_role, new_bat, pid)
                )
                st.success(f"Updated player #{pid}")

# ---------------- DELETE ----------------
with tab_delete:
    st.subheader("Delete a player record")
    players_df2 = run_query("SELECT player_id, full_name FROM players ORDER BY full_name")
    del_label = st.selectbox(
        "Select player to delete",
        players_df2.apply(lambda r: f"{r['player_id']} — {r['full_name']}", axis=1).tolist(),
        key="delete_select"
    )
    st.warning("This will permanently delete the player's stats history too.")
    confirm = st.checkbox("I understand this cannot be undone")
    if st.button("Delete player", type="primary", disabled=not confirm):
        pid = int(del_label.split(" — ")[0])
        run_action("DELETE FROM player_match_stats WHERE player_id=?", (pid,))
        run_action("DELETE FROM players WHERE player_id=?", (pid,))
        st.success(f"Deleted player #{pid}")
        st.rerun()
