# 🏏 Cricbuzz LiveStats: Real-Time Cricket Insights & SQL-Based Analytics

A multi-page Streamlit dashboard that combines **live data from the Cricbuzz API**
with a **SQL database** of historical match/player data — live scorecards, player
leaderboards, 25 SQL analytics questions, and full CRUD on player records.

## 1. Setup

```bash
cd cricbuzz_livestats
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Generate the sample database

The app ships **without** a committed database file so you always start fresh.
Build it once:

```bash
python data/generate_sample_data.py
```

This creates `data/cricbuzz_livestats.db` (SQLite) with realistic sample data:
10 teams, 150 players, 15 venues, 8 series, 144 matches, and 3000+ individual
player-match performance rows spanning ~3 years — enough for every one of the
25 SQL questions to return meaningful results.

> Want to point the app at PostgreSQL or MySQL instead? Set `DB_TYPE=postgresql`
> (or `mysql`) plus the connection variables in `.env` — see `.env.example`.
> You'll need to run `data/schema.sql` against that database yourself (the
> generator script currently targets SQLite).

## 3. Configure your Cricbuzz API key (optional but recommended)

The **Live Matches** and **Top Player Stats** pages call the real Cricbuzz API.

1. Create a free account at [RapidAPI](https://rapidapi.com/hub)
2. Search for **"Cricbuzz Cricket"** and subscribe to the free tier
3. Copy your key
4. Copy `.env.example` to `.env` and set `CRICBUZZ_API_KEY=your_key`
   (or, if deploying to Streamlit Community Cloud, add it under **Settings → Secrets**)

Without a key, those two pages show setup instructions instead of crashing —
everything else (SQL Analytics, CRUD) works fully offline against the sample DB.

## 4. Run the app

```bash
streamlit run app.py
```

Open the URL Streamlit prints (usually `http://localhost:8501`).

## Project structure

```
cricbuzz_livestats/
├── app.py                     # Main entry point (page navigation)
├── requirements.txt
├── .env.example
├── README.md
├── pages/
│   ├── home.py                # Overview + system status
│   ├── live_matches.py        # Live/recent/upcoming matches (Cricbuzz API)
│   ├── top_stats.py           # Batting/bowling leaderboards (Cricbuzz API)
│   ├── sql_queries.py         # 25 SQL questions, run + download results
│   └── crud_operations.py     # Create / Read / Update / Delete players
├── utils/
│   ├── db_connection.py       # Database-agnostic connection layer
│   ├── cricbuzz_api.py        # Cricbuzz REST API client (graceful failures)
│   └── sql_queries.py         # The 25 SQL queries, as structured data
├── data/
│   ├── schema.sql             # Table definitions + indexes
│   ├── generate_sample_data.py  # Builds the sample SQLite DB
│   └── cricbuzz_livestats.db  # (generated — not committed)
└── notebooks/
    └── data_fetching.ipynb    # Scratchpad for testing API calls
```

## Database schema

| Table | Purpose |
|---|---|
| `teams` | International sides |
| `players` | Player bio + role + team |
| `venues` | Stadiums (city, country, capacity) |
| `series` | Tours/tournaments |
| `matches` | One row per match: teams, venue, toss, result |
| `player_match_stats` | One row per player per match: runs, balls, wickets, overs, catches, etc. — the fact table nearly every SQL question joins against |

## The 25 SQL questions

Organized Beginner (1–8) → Intermediate (9–16) → Advanced (17–25), covering:
basic filtering/sorting → JOINs/subqueries/aggregates → window functions, CTEs,
and multi-metric analytical scoring. All 25 are implemented in
`utils/sql_queries.py` and run live from the **SQL Queries & Analytics** page.

> Note: Question 9 (all-rounders with 1000+ career runs *and* 50+ wickets)
> returns 0 rows against the bundled sample data — those thresholds assume
> real, multi-year career totals. The query itself is correct; swap in a
> larger/real dataset and it will populate.

## Notes on the sample data

Data is synthetically generated (`data/generate_sample_data.py`) with real
team, venue, and city names but randomized results — it exists so you can run
and demo the entire app (SQL analytics, CRUD, charts) without needing live API
access. Re-run the generator anytime to reset the database; it's fully
reproducible (seeded with `random.seed(42)`).

## Extending to a real API-backed pipeline

`notebooks/data_fetching.ipynb` is a scratchpad for testing real Cricbuzz API
calls and, if you want to go further, writing a script that fetches live
match/player data and upserts it into the `matches` / `player_match_stats`
tables — turning this from a demo into a live-updating analytics pipeline.
