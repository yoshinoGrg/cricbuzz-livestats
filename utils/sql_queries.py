"""
utils/sql_queries.py
------------------------
All 25 SQL practice questions from the project brief, as a structured list
so the Streamlit SQL Analytics page can list them, run them, and show results.

Each entry: id, level (Beginner/Intermediate/Advanced), title, question, sql
Written for SQLite (window functions + CTEs, SQLite 3.25+).
"""

QUERIES = [

# ---------------- BEGINNER (1-8) ----------------
{
    "id": 1, "level": "Beginner",
    "title": "Players representing India",
    "question": "Find all players who represent India. Display their full name, playing role, batting style, and bowling style.",
    "sql": """
        SELECT full_name, playing_role, batting_style, bowling_style
        FROM players
        WHERE country = 'India'
        ORDER BY full_name;
    """
},
{
    "id": 2, "level": "Beginner",
    "title": "Matches in the last 30 days",
    "question": "Show all cricket matches played in the last 30 days: description, both team names, venue + city, match date. Most recent first.",
    "sql": """
        SELECT m.match_description,
               t1.team_name AS team1,
               t2.team_name AS team2,
               v.venue_name || ', ' || v.city AS venue,
               m.match_date
        FROM matches m
        JOIN teams t1 ON m.team1_id = t1.team_id
        JOIN teams t2 ON m.team2_id = t2.team_id
        JOIN venues v ON m.venue_id = v.venue_id
        WHERE date(m.match_date) >= date('now', '-30 day')
        ORDER BY m.match_date DESC;
    """
},
{
    "id": 3, "level": "Beginner",
    "title": "Top 10 ODI run scorers",
    "question": "List the top 10 highest run scorers in ODI cricket: player name, total runs, batting average, centuries. Highest first.",
    "sql": """
        SELECT p.full_name,
               SUM(pms.runs_scored) AS total_runs,
               ROUND(SUM(pms.runs_scored) * 1.0 / NULLIF(SUM(pms.is_out), 0), 2) AS batting_average,
               SUM(CASE WHEN pms.runs_scored >= 100 THEN 1 ELSE 0 END) AS centuries
        FROM player_match_stats pms
        JOIN players p ON p.player_id = pms.player_id
        JOIN matches m ON m.match_id = pms.match_id
        WHERE m.match_type = 'ODI'
        GROUP BY p.player_id, p.full_name
        ORDER BY total_runs DESC
        LIMIT 10;
    """
},
{
    "id": 4, "level": "Beginner",
    "title": "Venues with capacity > 50,000",
    "question": "Display all venues with seating capacity over 50,000: venue name, city, country, capacity. Largest first.",
    "sql": """
        SELECT venue_name, city, country, capacity
        FROM venues
        WHERE capacity > 50000
        ORDER BY capacity DESC;
    """
},
{
    "id": 5, "level": "Beginner",
    "title": "Total wins per team",
    "question": "Calculate how many matches each team has won. Show team name and total wins, most wins first.",
    "sql": """
        SELECT t.team_name, COUNT(*) AS total_wins
        FROM matches m
        JOIN teams t ON t.team_id = m.winning_team_id
        GROUP BY t.team_id, t.team_name
        ORDER BY total_wins DESC;
    """
},
{
    "id": 6, "level": "Beginner",
    "title": "Player count by playing role",
    "question": "Count how many players belong to each playing role. Show role and count for each.",
    "sql": """
        SELECT playing_role, COUNT(*) AS player_count
        FROM players
        GROUP BY playing_role
        ORDER BY player_count DESC;
    """
},
{
    "id": 7, "level": "Beginner",
    "title": "Highest individual score per format",
    "question": "Find the highest individual batting score in each format (Test, ODI, T20I). Display format and highest score.",
    "sql": """
        SELECT m.match_type AS format, MAX(pms.runs_scored) AS highest_score
        FROM player_match_stats pms
        JOIN matches m ON m.match_id = pms.match_id
        GROUP BY m.match_type;
    """
},
{
    "id": 8, "level": "Beginner",
    "title": "Series started in 2024",
    "question": "Show all series that started in 2024: series name, host country, match type, start date, total matches planned.",
    "sql": """
        SELECT series_name, host_country, match_type, start_date, total_matches
        FROM series
        WHERE strftime('%Y', start_date) = '2024'
        ORDER BY start_date;
    """
},

# ---------------- INTERMEDIATE (9-16) ----------------
{
    "id": 9, "level": "Intermediate",
    "title": "All-rounders: 1000+ runs & 50+ wickets",
    "question": "Find all-rounder players with more than 1000 career runs AND more than 50 career wickets. Show name, total runs, total wickets, format.",
    "sql": """
        SELECT p.full_name, m.match_type AS format,
               SUM(pms.runs_scored) AS total_runs,
               SUM(pms.wickets_taken) AS total_wickets
        FROM players p
        JOIN player_match_stats pms ON pms.player_id = p.player_id
        JOIN matches m ON m.match_id = pms.match_id
        WHERE p.playing_role = 'All-rounder'
        GROUP BY p.player_id, m.match_type
        HAVING SUM(pms.runs_scored) > 1000 AND SUM(pms.wickets_taken) > 50
        ORDER BY total_runs DESC;
    """
},
{
    "id": 10, "level": "Intermediate",
    "title": "Last 20 completed matches",
    "question": "Get details of the last 20 completed matches: description, both teams, winning team, victory margin/type, venue. Most recent first.",
    "sql": """
        SELECT m.match_description,
               t1.team_name AS team1, t2.team_name AS team2,
               tw.team_name AS winning_team,
               m.victory_margin, m.victory_type,
               v.venue_name
        FROM matches m
        JOIN teams t1 ON t1.team_id = m.team1_id
        JOIN teams t2 ON t2.team_id = m.team2_id
        LEFT JOIN teams tw ON tw.team_id = m.winning_team_id
        JOIN venues v ON v.venue_id = m.venue_id
        WHERE m.winning_team_id IS NOT NULL
        ORDER BY m.match_date DESC
        LIMIT 20;
    """
},
{
    "id": 11, "level": "Intermediate",
    "title": "Player performance across formats",
    "question": "For players who played at least 2 formats, show total runs in Test, ODI, T20I, plus overall batting average.",
    "sql": """
        WITH per_format AS (
            SELECT p.player_id, p.full_name, m.match_type,
                   SUM(pms.runs_scored) AS runs,
                   SUM(pms.is_out) AS outs
            FROM player_match_stats pms
            JOIN players p ON p.player_id = pms.player_id
            JOIN matches m ON m.match_id = pms.match_id
            GROUP BY p.player_id, m.match_type
        )
        SELECT full_name,
               SUM(CASE WHEN match_type = 'Test' THEN runs ELSE 0 END) AS test_runs,
               SUM(CASE WHEN match_type = 'ODI'  THEN runs ELSE 0 END) AS odi_runs,
               SUM(CASE WHEN match_type = 'T20I' THEN runs ELSE 0 END) AS t20i_runs,
               ROUND(SUM(runs) * 1.0 / NULLIF(SUM(outs), 0), 2) AS overall_batting_average,
               COUNT(DISTINCT match_type) AS formats_played
        FROM per_format
        GROUP BY player_id, full_name
        HAVING COUNT(DISTINCT match_type) >= 2
        ORDER BY overall_batting_average DESC;
    """
},
{
    "id": 12, "level": "Intermediate",
    "title": "Home vs away performance",
    "question": "Analyze each team's wins at home vs away, where 'home' means venue country = team's country.",
    "sql": """
        SELECT t.team_name,
               SUM(CASE WHEN v.country = t.country AND m.winning_team_id = t.team_id THEN 1 ELSE 0 END) AS home_wins,
               SUM(CASE WHEN v.country != t.country AND m.winning_team_id = t.team_id THEN 1 ELSE 0 END) AS away_wins
        FROM matches m
        JOIN venues v ON v.venue_id = m.venue_id
        JOIN teams t ON t.team_id IN (m.team1_id, m.team2_id)
        GROUP BY t.team_id, t.team_name
        ORDER BY home_wins DESC;
    """
},
{
    "id": 13, "level": "Intermediate",
    "title": "100+ run batting partnerships",
    "question": "Identify consecutive-position batting partnerships that combined for 100+ runs in the same innings.",
    "sql": """
        SELECT a.match_id, a.innings_number,
               p1.full_name AS batter_1, p2.full_name AS batter_2,
               (a.runs_scored + b.runs_scored) AS partnership_runs
        FROM player_match_stats a
        JOIN player_match_stats b
             ON a.match_id = b.match_id
            AND a.innings_number = b.innings_number
            AND b.batting_position = a.batting_position + 1
        JOIN players p1 ON p1.player_id = a.player_id
        JOIN players p2 ON p2.player_id = b.player_id
        WHERE (a.runs_scored + b.runs_scored) >= 100
        ORDER BY partnership_runs DESC;
    """
},
{
    "id": 14, "level": "Intermediate",
    "title": "Bowling performance by venue",
    "question": "For bowlers with 3+ matches at the same venue (bowling 4+ overs each), show average economy, total wickets, matches played at that venue.",
    "sql": """
        SELECT p.full_name, v.venue_name,
               COUNT(*) AS matches_at_venue,
               ROUND(AVG(pms.runs_conceded * 1.0 / NULLIF(pms.overs_bowled,0)), 2) AS avg_economy,
               SUM(pms.wickets_taken) AS total_wickets
        FROM player_match_stats pms
        JOIN players p ON p.player_id = pms.player_id
        JOIN matches m ON m.match_id = pms.match_id
        JOIN venues v ON v.venue_id = m.venue_id
        WHERE pms.overs_bowled >= 4
        GROUP BY p.player_id, v.venue_id
        HAVING COUNT(*) >= 3
        ORDER BY avg_economy ASC;
    """
},
{
    "id": 15, "level": "Intermediate",
    "title": "Performance in close matches",
    "question": "Close match = decided by <50 runs OR <5 wickets. Show each player's avg runs, close matches played, and how many their team won.",
    "sql": """
        WITH close_matches AS (
            SELECT * FROM matches
            WHERE (victory_type = 'runs' AND victory_margin < 50)
               OR (victory_type = 'wickets' AND victory_margin < 5)
        )
        SELECT p.full_name,
               ROUND(AVG(pms.runs_scored), 2) AS avg_runs_in_close_matches,
               COUNT(*) AS close_matches_played,
               SUM(CASE WHEN cm.winning_team_id = pms.team_id THEN 1 ELSE 0 END) AS close_matches_won
        FROM player_match_stats pms
        JOIN close_matches cm ON cm.match_id = pms.match_id
        JOIN players p ON p.player_id = pms.player_id
        GROUP BY p.player_id
        ORDER BY avg_runs_in_close_matches DESC;
    """
},
{
    "id": 16, "level": "Intermediate",
    "title": "Yearly batting trend since 2020",
    "question": "For matches since 2020, show each player's average runs/match and average strike rate per year (players with 5+ matches that year).",
    "sql": """
        SELECT p.full_name,
               strftime('%Y', m.match_date) AS year,
               COUNT(*) AS matches_played,
               ROUND(AVG(pms.runs_scored), 2) AS avg_runs,
               ROUND(AVG(pms.runs_scored * 100.0 / NULLIF(pms.balls_faced,0)), 2) AS avg_strike_rate
        FROM player_match_stats pms
        JOIN players p ON p.player_id = pms.player_id
        JOIN matches m ON m.match_id = pms.match_id
        WHERE date(m.match_date) >= '2020-01-01'
        GROUP BY p.player_id, year
        HAVING COUNT(*) >= 5
        ORDER BY year DESC, avg_runs DESC;
    """
},

# ---------------- ADVANCED (17-25) ----------------
{
    "id": 17, "level": "Advanced",
    "title": "Toss advantage analysis",
    "question": "What percentage of matches are won by the toss-winning team, broken down by toss decision (bat/bowl)?",
    "sql": """
        SELECT toss_decision,
               COUNT(*) AS total_matches,
               SUM(CASE WHEN toss_winner_id = winning_team_id THEN 1 ELSE 0 END) AS toss_winner_also_won,
               ROUND(100.0 * SUM(CASE WHEN toss_winner_id = winning_team_id THEN 1 ELSE 0 END) / COUNT(*), 2) AS win_pct
        FROM matches
        WHERE winning_team_id IS NOT NULL
        GROUP BY toss_decision;
    """
},
{
    "id": 18, "level": "Advanced",
    "title": "Most economical limited-overs bowlers",
    "question": "Most economical bowlers in ODI/T20 (10+ matches, avg 2+ overs/match): economy rate and total wickets.",
    "sql": """
        SELECT p.full_name,
               COUNT(*) AS matches_bowled,
               ROUND(AVG(pms.overs_bowled), 2) AS avg_overs_per_match,
               ROUND(SUM(pms.runs_conceded) * 1.0 / NULLIF(SUM(pms.overs_bowled),0), 2) AS economy_rate,
               SUM(pms.wickets_taken) AS total_wickets
        FROM player_match_stats pms
        JOIN players p ON p.player_id = pms.player_id
        JOIN matches m ON m.match_id = pms.match_id
        WHERE m.match_type IN ('ODI', 'T20I') AND pms.overs_bowled > 0
        GROUP BY p.player_id
        HAVING COUNT(*) >= 10 AND AVG(pms.overs_bowled) >= 2
        ORDER BY economy_rate ASC;
    """
},
{
    "id": 19, "level": "Advanced",
    "title": "Most consistent batsmen",
    "question": "Average runs & standard deviation of runs per player (10+ balls faced/innings, since 2022). Lower stdev = more consistent.",
    "sql": """
        WITH innings AS (
            SELECT p.player_id, p.full_name, pms.runs_scored
            FROM player_match_stats pms
            JOIN players p ON p.player_id = pms.player_id
            JOIN matches m ON m.match_id = pms.match_id
            WHERE pms.balls_faced >= 10 AND date(m.match_date) >= '2022-01-01'
        )
        SELECT full_name,
               COUNT(*) AS innings_count,
               ROUND(AVG(runs_scored), 2) AS avg_runs,
               ROUND(SQRT(AVG(runs_scored*runs_scored) - AVG(runs_scored)*AVG(runs_scored)), 2) AS stddev_runs
        FROM innings
        GROUP BY player_id, full_name
        HAVING COUNT(*) >= 5
        ORDER BY stddev_runs ASC;
    """
},
{
    "id": 20, "level": "Advanced",
    "title": "Format-wise match count & batting average",
    "question": "Count of Test/ODI/T20 matches per player and batting average in each format (20+ total matches across formats).",
    "sql": """
        WITH per_format AS (
            SELECT p.player_id, p.full_name, m.match_type,
                   COUNT(*) AS matches,
                   ROUND(SUM(pms.runs_scored) * 1.0 / NULLIF(SUM(pms.is_out),0), 2) AS batting_avg
            FROM player_match_stats pms
            JOIN players p ON p.player_id = pms.player_id
            JOIN matches m ON m.match_id = pms.match_id
            GROUP BY p.player_id, m.match_type
        )
        SELECT full_name,
               SUM(CASE WHEN match_type='Test' THEN matches ELSE 0 END) AS test_matches,
               SUM(CASE WHEN match_type='Test' THEN batting_avg ELSE NULL END) AS test_avg,
               SUM(CASE WHEN match_type='ODI' THEN matches ELSE 0 END) AS odi_matches,
               SUM(CASE WHEN match_type='ODI' THEN batting_avg ELSE NULL END) AS odi_avg,
               SUM(CASE WHEN match_type='T20I' THEN matches ELSE 0 END) AS t20i_matches,
               SUM(CASE WHEN match_type='T20I' THEN batting_avg ELSE NULL END) AS t20i_avg,
               SUM(matches) AS total_matches
        FROM per_format
        GROUP BY player_id, full_name
        HAVING SUM(matches) >= 20
        ORDER BY total_matches DESC;
    """
},
{
    "id": 21, "level": "Advanced",
    "title": "Composite player performance ranking",
    "question": "Weighted score combining batting, bowling, and fielding performance; rank top performers per format.",
    "sql": """
        WITH agg AS (
            SELECT p.player_id, p.full_name, m.match_type,
                   SUM(pms.runs_scored) AS runs_scored,
                   ROUND(SUM(pms.runs_scored)*1.0/NULLIF(SUM(pms.is_out),0), 2) AS batting_average,
                   ROUND(AVG(pms.runs_scored*100.0/NULLIF(pms.balls_faced,0)), 2) AS strike_rate,
                   SUM(pms.wickets_taken) AS wickets_taken,
                   ROUND(SUM(pms.runs_conceded)*1.0/NULLIF(SUM(pms.wickets_taken),0), 2) AS bowling_average,
                   ROUND(SUM(pms.runs_conceded)*1.0/NULLIF(SUM(pms.overs_bowled),0), 2) AS economy_rate,
                   SUM(pms.catches_taken) AS catches,
                   SUM(pms.stumpings) AS stumpings
            FROM player_match_stats pms
            JOIN players p ON p.player_id = pms.player_id
            JOIN matches m ON m.match_id = pms.match_id
            GROUP BY p.player_id, m.match_type
        )
        SELECT full_name, match_type,
               ROUND(
                   (runs_scored * 0.01) + (COALESCE(batting_average,0) * 0.5) + (COALESCE(strike_rate,0) * 0.3)
                 + (wickets_taken * 2) + ((50 - COALESCE(bowling_average,50)) * 0.5) + ((6 - COALESCE(economy_rate,6)) * 2)
                 + (catches * 3) + (stumpings * 5)
               , 2) AS total_score
        FROM agg
        ORDER BY match_type, total_score DESC;
    """
},
{
    "id": 22, "level": "Advanced",
    "title": "Head-to-head match prediction analysis",
    "question": "For team pairs with 5+ matches in the last 3 years: total matches, wins each, avg victory margin, win % overall.",
    "sql": """
        WITH h2h AS (
            SELECT m.*,
                   CASE WHEN team1_id < team2_id THEN team1_id ELSE team2_id END AS team_a,
                   CASE WHEN team1_id < team2_id THEN team2_id ELSE team1_id END AS team_b
            FROM matches m
            WHERE date(m.match_date) >= date('now', '-3 years')
        )
        SELECT ta.team_name AS team_a, tb.team_name AS team_b,
               COUNT(*) AS total_matches,
               SUM(CASE WHEN winning_team_id = team_a THEN 1 ELSE 0 END) AS team_a_wins,
               SUM(CASE WHEN winning_team_id = team_b THEN 1 ELSE 0 END) AS team_b_wins,
               ROUND(AVG(CASE WHEN winning_team_id = team_a THEN victory_margin END), 1) AS team_a_avg_margin,
               ROUND(AVG(CASE WHEN winning_team_id = team_b THEN victory_margin END), 1) AS team_b_avg_margin,
               ROUND(100.0 * SUM(CASE WHEN winning_team_id = team_a THEN 1 ELSE 0 END) / COUNT(*), 1) AS team_a_win_pct
        FROM h2h
        JOIN teams ta ON ta.team_id = team_a
        JOIN teams tb ON tb.team_id = team_b
        GROUP BY team_a, team_b
        HAVING COUNT(*) >= 5
        ORDER BY total_matches DESC;
    """
},
{
    "id": 23, "level": "Advanced",
    "title": "Recent form & momentum",
    "question": "For each player's last 10 innings: avg runs (last 5 vs last 10), strike-rate trend, scores 50+, consistency; categorize form.",
    "sql": """
        WITH ranked AS (
            SELECT pms.player_id, p.full_name, pms.runs_scored,
                   pms.runs_scored*100.0/NULLIF(pms.balls_faced,0) AS strike_rate,
                   ROW_NUMBER() OVER (PARTITION BY pms.player_id ORDER BY m.match_date DESC) AS rn
            FROM player_match_stats pms
            JOIN players p ON p.player_id = pms.player_id
            JOIN matches m ON m.match_id = pms.match_id
        )
        SELECT full_name,
               ROUND(AVG(CASE WHEN rn <= 5 THEN runs_scored END), 2) AS avg_runs_last_5,
               ROUND(AVG(CASE WHEN rn <= 10 THEN runs_scored END), 2) AS avg_runs_last_10,
               ROUND(AVG(CASE WHEN rn <= 10 THEN strike_rate END), 2) AS recent_strike_rate,
               SUM(CASE WHEN rn <= 10 AND runs_scored >= 50 THEN 1 ELSE 0 END) AS scores_50_plus,
               ROUND(SQRT(AVG(CASE WHEN rn<=10 THEN runs_scored*runs_scored END)
                     - AVG(CASE WHEN rn<=10 THEN runs_scored END)*AVG(CASE WHEN rn<=10 THEN runs_scored END)), 2) AS consistency_stddev,
               CASE
                   WHEN AVG(CASE WHEN rn <= 5 THEN runs_scored END) >= 45 THEN 'Excellent Form'
                   WHEN AVG(CASE WHEN rn <= 5 THEN runs_scored END) >= 30 THEN 'Good Form'
                   WHEN AVG(CASE WHEN rn <= 5 THEN runs_scored END) >= 15 THEN 'Average Form'
                   ELSE 'Poor Form'
               END AS form_category
        FROM ranked
        WHERE rn <= 10
        GROUP BY player_id, full_name
        ORDER BY avg_runs_last_5 DESC;
    """
},
{
    "id": 24, "level": "Advanced",
    "title": "Most successful batting partnerships",
    "question": "For consecutive-position pairs with 5+ partnerships: avg runs, count over 50, highest score, success rate.",
    "sql": """
        WITH partnerships AS (
            SELECT a.player_id AS player1_id, b.player_id AS player2_id,
                   (a.runs_scored + b.runs_scored) AS partnership_runs
            FROM player_match_stats a
            JOIN player_match_stats b
                 ON a.match_id = b.match_id
                AND a.innings_number = b.innings_number
                AND b.batting_position = a.batting_position + 1
        )
        SELECT p1.full_name AS batter_1, p2.full_name AS batter_2,
               COUNT(*) AS partnerships_count,
               ROUND(AVG(partnership_runs), 2) AS avg_partnership_runs,
               SUM(CASE WHEN partnership_runs > 50 THEN 1 ELSE 0 END) AS partnerships_over_50,
               MAX(partnership_runs) AS highest_partnership,
               ROUND(100.0 * SUM(CASE WHEN partnership_runs > 50 THEN 1 ELSE 0 END) / COUNT(*), 1) AS success_rate_pct
        FROM partnerships pt
        JOIN players p1 ON p1.player_id = pt.player1_id
        JOIN players p2 ON p2.player_id = pt.player2_id
        GROUP BY pt.player1_id, pt.player2_id
        HAVING COUNT(*) >= 5
        ORDER BY success_rate_pct DESC, avg_partnership_runs DESC;
    """
},
{
    "id": 25, "level": "Advanced",
    "title": "Career trajectory time-series analysis",
    "question": "Quarterly avg runs/strike-rate per player, quarter-over-quarter comparison, career phase classification (6+ quarters, 3+ matches/quarter).",
    "sql": """
        WITH quarterly AS (
            SELECT p.player_id, p.full_name,
                   strftime('%Y', m.match_date) || '-Q' ||
                   ((CAST(strftime('%m', m.match_date) AS INTEGER) - 1) / 3 + 1) AS quarter,
                   AVG(pms.runs_scored) AS avg_runs,
                   AVG(pms.runs_scored * 100.0 / NULLIF(pms.balls_faced,0)) AS avg_strike_rate,
                   COUNT(*) AS matches_in_quarter
            FROM player_match_stats pms
            JOIN players p ON p.player_id = pms.player_id
            JOIN matches m ON m.match_id = pms.match_id
            GROUP BY p.player_id, quarter
            HAVING COUNT(*) >= 3
        ),
        trended AS (
            SELECT *,
                   LAG(avg_runs) OVER (PARTITION BY player_id ORDER BY quarter) AS prev_quarter_runs
            FROM quarterly
        )
        SELECT full_name,
               COUNT(*) AS quarters_played,
               ROUND(AVG(avg_runs), 2) AS overall_avg_runs,
               ROUND(AVG(avg_strike_rate), 2) AS overall_avg_strike_rate,
               ROUND(AVG(avg_runs - prev_quarter_runs), 2) AS avg_quarter_over_quarter_change,
               CASE
                   WHEN AVG(avg_runs - prev_quarter_runs) > 2 THEN 'Career Ascending'
                   WHEN AVG(avg_runs - prev_quarter_runs) < -2 THEN 'Career Declining'
                   ELSE 'Career Stable'
               END AS career_phase
        FROM trended
        GROUP BY player_id, full_name
        HAVING COUNT(*) >= 6
        ORDER BY avg_quarter_over_quarter_change DESC;
    """
},
]


def get_query_by_id(qid: int):
    return next((q for q in QUERIES if q["id"] == qid), None)
