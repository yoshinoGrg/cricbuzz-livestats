import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.sql_queries import QUERIES
from utils.db_connection import run_query

st.title("🔍 SQL Queries & Analytics")
st.caption("25 SQL practice questions — from basic SELECTs to window-function analytics.")

levels = ["All", "Beginner", "Intermediate", "Advanced"]
level_filter = st.radio("Filter by level", levels, horizontal=True)

filtered = [q for q in QUERIES if level_filter == "All" or q["level"] == level_filter]

labels = [f"Q{q['id']} — {q['title']} ({q['level']})" for q in filtered]
selected_label = st.selectbox("Choose a question", labels)
selected = filtered[labels.index(selected_label)]

st.markdown(f"#### Q{selected['id']}. {selected['title']}")
st.write(selected["question"])

with st.expander("View SQL"):
    st.code(selected["sql"].strip(), language="sql")

if st.button("▶ Run Query", type="primary"):
    try:
        df = run_query(selected["sql"])
        st.success(f"{len(df)} row(s) returned")
        st.dataframe(df, width='stretch')
        if not df.empty:
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("⬇ Download results as CSV", csv, f"q{selected['id']}_results.csv", "text/csv")
    except Exception as e:
        st.error(f"Query failed: {e}")

st.divider()
st.markdown("### ✍️ Custom SQL Console")
st.caption("Run your own SELECT query against the database (read-only recommended here — use the CRUD page for writes).")
custom_sql = st.text_area("SQL query", value="SELECT * FROM players LIMIT 10;", height=120)
if st.button("Run custom query"):
    try:
        df = run_query(custom_sql)
        st.dataframe(df, width='stretch')
    except Exception as e:
        st.error(f"Query failed: {e}")
