"""
generate_sample_data.py
------------------------
Populates cricbuzz_livestats.db with realistic synthetic cricket data
so the whole app (SQL Analytics + CRUD pages) works out of the box.

Run once:  python data/generate_sample_data.py
"""

import sqlite3
import random
from datetime import date, timedelta
import os

random.seed(42)

DB_PATH = os.path.join(os.path.dirname(__file__), "cricbuzz_livestats.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")

TEAMS = [
    ("India", "India"), ("Australia", "Australia"), ("England", "England"),
    ("New Zealand", "New Zealand"), ("Pakistan", "Pakistan"), ("South Africa", "South Africa"),
    ("Sri Lanka", "Sri Lanka"), ("Bangladesh", "Bangladesh"), ("West Indies", "West Indies"),
    ("Afghanistan", "Afghanistan"),
]

VENUES = [
    ("Wankhede Stadium", "Mumbai", "India", 33000),
    ("Melbourne Cricket Ground", "Melbourne", "Australia", 100024),
    ("Lord's", "London", "England", 30000),
    ("Eden Park", "Auckland", "New Zealand", 50000),
    ("Gaddafi Stadium", "Lahore", "Pakistan", 27000),
    ("Newlands", "Cape Town", "South Africa", 25000),
    ("R.Premadasa Stadium", "Colombo", "Sri Lanka", 35000),
    ("Sher-e-Bangla Stadium", "Dhaka", "Bangladesh", 26000),
    ("Kensington Oval", "Bridgetown", "West Indies", 28000),
    ("Narendra Modi Stadium", "Ahmedabad", "India", 132000),
    ("Sydney Cricket Ground", "Sydney", "Australia", 48000),
    ("The Oval", "London", "England", 25500),
    ("M. Chinnaswamy Stadium", "Bangalore", "India", 40000),
    ("Eden Gardens", "Kolkata", "India", 68000),
    ("Old Trafford", "Manchester", "England", 26000),
]

FIRST_NAMES = ["Virat","Rohit","Shubman","Rishabh","Jasprit","Ravindra","Hardik","KL","Mohammed",
    "Steve","David","Pat","Mitchell","Glenn","Travis","Marnus","Josh","Adam",
    "Joe","Ben","Jos","Harry","Jofra","Mark","Jonny","Moeen",
    "Kane","Tom","Trent","Devon","Daryl","Mitchell","Tim",
    "Babar","Shaheen","Mohammad","Shadab","Fakhar","Naseem",
    "Quinton","Kagiso","Temba","Aiden","Anrich","David",
    "Dimuth","Kusal","Wanindu","Dushmantha",
    "Shakib","Litton","Mustafizur","Mehidy",
    "Nicholas","Shai","Jason","Alzarri","Kyle",
    "Rashid","Mohammad","Rahmanullah","Gulbadin"]

LAST_NAMES = ["Kohli","Sharma","Gill","Pant","Bumrah","Jadeja","Pandya","Rahul","Shami",
    "Smith","Warner","Cummins","Starc","Maxwell","Head","Labuschagne","Hazlewood","Zampa",
    "Root","Stokes","Buttler","Brook","Archer","Wood","Bairstow","Ali",
    "Williamson","Latham","Boult","Conway","Mitchell","Santner","Southee",
    "Azam","Afridi","Rizwan","Khan","Zaman","Shah",
    "de Kock","Rabada","Bavuma","Markram","Nortje","Miller",
    "Karunaratne","Mendis","Hasaranga","Chameera",
    "Al Hasan","Das","Rahman","Hasan",
    "Pooran","Hope","Holder","Joseph","Mayers",
    "Khan","Nabi","Zadran","Naib"]

ROLES = ["Batsman","Bowler","All-rounder","Wicket-keeper"]
BAT_STYLES = ["Right-hand bat","Left-hand bat"]
BOWL_STYLES = ["Right-arm fast","Left-arm fast","Right-arm off-break","Left-arm orthodox",
               "Right-arm leg-break","Left-arm chinaman", None]
FORMATS = ["Test","ODI","T20I"]

conn = sqlite3.connect(DB_PATH)
conn.executescript(open(SCHEMA_PATH).read())
cur = conn.cursor()

# ---------- Teams ----------
team_ids = {}
for name, country in TEAMS:
    cur.execute("INSERT INTO teams (team_name, country) VALUES (?,?)", (name, country))
    team_ids[name] = cur.lastrowid

# ---------- Venues ----------
venue_ids = []
for v in VENUES:
    cur.execute("INSERT INTO venues (venue_name, city, country, capacity) VALUES (?,?,?,?)", v)
    venue_ids.append(cur.lastrowid)

# ---------- Players (15 per team) ----------
players_by_team = {t: [] for t in team_ids}
name_pool = list(set([(f, l) for f in FIRST_NAMES for l in LAST_NAMES]))
random.shuffle(name_pool)
idx = 0
for team_name, team_id in team_ids.items():
    for i in range(15):
        fname, lname = name_pool[idx]; idx += 1
        full_name = f"{fname} {lname}"
        role = random.choices(ROLES, weights=[35, 30, 25, 10])[0]
        bat_style = random.choice(BAT_STYLES)
        bowl_style = None if role == "Batsman" or role == "Wicket-keeper" else random.choice(BOWL_STYLES[:-1])
        dob = date(1988, 1, 1) + timedelta(days=random.randint(0, 365*15))
        cur.execute("""INSERT INTO players (full_name, country, playing_role, batting_style,
                       bowling_style, date_of_birth, team_id) VALUES (?,?,?,?,?,?,?)""",
                    (full_name, TEAMS[[t[0] for t in TEAMS].index(team_name)][1], role, bat_style,
                     bowl_style, dob.isoformat(), team_id))
        players_by_team[team_name].append(cur.lastrowid)

# ---------- Series ----------
series_ids = []
series_names = [
    ("Border-Gavaskar Trophy", "India", "Test", "2024-02-01", 4),
    ("Ashes", "England", "Test", "2024-06-15", 5),
    ("World Cup Warm-up Series", "India", "ODI", "2024-09-10", 6),
    ("Tri-Nation T20 Series", "Sri Lanka", "T20I", "2024-11-01", 6),
    ("Asia Cup", "Pakistan", "ODI", "2025-08-20", 8),
    ("ICC World Test Championship", "England", "Test", "2025-03-05", 6),
    ("Bilateral T20I Series", "New Zealand", "T20I", "2025-01-12", 3),
    ("Champions Trophy", "South Africa", "ODI", "2026-02-01", 10),
]
for s in series_names:
    cur.execute("""INSERT INTO series (series_name, host_country, match_type, start_date, total_matches)
                   VALUES (?,?,?,?,?)""", s)
    series_ids.append(cur.lastrowid)

# ---------- Matches + Player stats ----------
team_names_list = list(team_ids.keys())
match_id_counter = 0
today = date(2026, 7, 14)

for series_row_id, (sname, host, mtype, sdate, total) in zip(series_ids, series_names):
    start = date.fromisoformat(sdate)
    total = total * 3  # more matches per series so repeat-pattern queries (partnerships, venue-bowling) have signal
    # Fix a "playing XI" per team for this series so partnerships/venues repeat meaningfully
    series_squads = {t: random.sample(players_by_team[t], k=min(11, len(players_by_team[t])))
                      for t in team_names_list}
    for m in range(total):
        t1, t2 = random.sample(team_names_list, 2)
        venue_id = random.choice(venue_ids[:6])  # bias toward fewer venues so "3+ matches at same venue" triggers
        match_date = today - timedelta(days=random.randint(1, 1000))
        toss_winner = random.choice([t1, t2])
        toss_decision = random.choice(["bat", "bowl"])
        winner = random.choices([t1, t2, None], weights=[45, 45, 10])[0]  # some no-result
        victory_type = random.choice(["runs", "wickets"]) if winner else None
        victory_margin = (random.randint(5, 250) if victory_type == "runs"
                           else random.randint(1, 9)) if winner else None
        desc = f"{t1} vs {t2}, {sname}"

        cur.execute("""INSERT INTO matches (series_id, match_description, match_type, team1_id, team2_id,
                       venue_id, match_date, toss_winner_id, toss_decision, winning_team_id,
                       victory_margin, victory_type)
                       VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (series_row_id, desc, mtype, team_ids[t1], team_ids[t2], venue_id,
                     match_date.isoformat(), team_ids[toss_winner], toss_decision,
                     team_ids[winner] if winner else None, victory_margin, victory_type))
        match_id = cur.lastrowid
        match_id_counter += 1

        # Use each team's fixed series XI (with small rotation) so batting positions/partnerships repeat
        for team_name in (t1, t2):
            base_squad = series_squads[team_name]
            squad = base_squad[:] 
            if random.random() < 0.3:  # occasional rotation/injury substitute
                sub_pool = [p for p in players_by_team[team_name] if p not in squad]
                if sub_pool:
                    squad[random.randint(0, 10)] = random.choice(sub_pool)
            for pos, player_id in enumerate(squad, start=1):
                runs = max(0, int(random.gauss(28, 25)))
                balls = max(runs, int(runs * random.uniform(0.7, 1.6))) if runs > 0 else random.randint(0, 10)
                is_out = 0 if random.random() < 0.2 else 1
                fours = random.randint(0, max(1, runs // 12))
                sixes = random.randint(0, max(0, runs // 25))
                overs = round(random.choice([0,0,0,2,4,6,8,9,10]) + random.random(), 1) if random.random() > 0.4 else 0
                conceded = int(overs * random.uniform(3, 9)) if overs > 0 else 0
                wickets = random.choices([0,1,2,3,4,5], weights=[45,25,15,8,5,2])[0] if overs > 0 else 0
                catches = random.choices([0,1,2], weights=[70,25,5])[0]
                stumpings = 1 if random.random() < 0.03 else 0

                cur.execute("""INSERT INTO player_match_stats
                    (match_id, player_id, team_id, innings_number, batting_position, runs_scored,
                     balls_faced, is_out, fours, sixes, overs_bowled, runs_conceded, wickets_taken,
                     catches_taken, stumpings)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (match_id, player_id, team_ids[team_name], 1, pos, runs, balls, is_out, fours, sixes,
                     overs, conceded, wickets, catches, stumpings))

conn.commit()
print(f"Database created at {DB_PATH}")
print(f"Teams: {len(team_ids)} | Venues: {len(venue_ids)} | Series: {len(series_ids)} | Matches: {match_id_counter}")
cur.execute("SELECT COUNT(*) FROM players"); print("Players:", cur.fetchone()[0])
cur.execute("SELECT COUNT(*) FROM player_match_stats"); print("Player-match stat rows:", cur.fetchone()[0])
conn.close()