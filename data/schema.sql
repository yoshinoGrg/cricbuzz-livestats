-- ============================================================
-- Cricbuzz LiveStats — Database Schema
-- Works on SQLite / PostgreSQL / MySQL with minor type tweaks
-- ============================================================

DROP TABLE IF EXISTS player_match_stats;
DROP TABLE IF EXISTS matches;
DROP TABLE IF EXISTS series;
DROP TABLE IF EXISTS venues;
DROP TABLE IF EXISTS players;
DROP TABLE IF EXISTS teams;

-- Teams (international sides)
CREATE TABLE teams (
    team_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    team_name    TEXT NOT NULL UNIQUE,
    country      TEXT NOT NULL
);

-- Players
CREATE TABLE players (
    player_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name      TEXT NOT NULL,
    country        TEXT NOT NULL,
    playing_role   TEXT NOT NULL,      -- Batsman, Bowler, All-rounder, Wicket-keeper
    batting_style   TEXT,               -- Right-hand bat / Left-hand bat
    bowling_style   TEXT,               -- Right-arm fast, Left-arm orthodox, etc.
    date_of_birth  DATE,
    team_id        INTEGER,
    FOREIGN KEY (team_id) REFERENCES teams(team_id)
);

-- Venues
CREATE TABLE venues (
    venue_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    venue_name   TEXT NOT NULL,
    city         TEXT NOT NULL,
    country      TEXT NOT NULL,
    capacity     INTEGER
);

-- Series
CREATE TABLE series (
    series_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    series_name     TEXT NOT NULL,
    host_country    TEXT NOT NULL,
    match_type      TEXT NOT NULL,     -- Test / ODI / T20I
    start_date      DATE,
    total_matches   INTEGER
);

-- Matches
CREATE TABLE matches (
    match_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    series_id        INTEGER,
    match_description TEXT,
    match_type       TEXT NOT NULL,    -- Test / ODI / T20I
    team1_id         INTEGER NOT NULL,
    team2_id         INTEGER NOT NULL,
    venue_id         INTEGER NOT NULL,
    match_date       DATE NOT NULL,
    toss_winner_id   INTEGER,
    toss_decision    TEXT,             -- bat / bowl
    winning_team_id  INTEGER,
    victory_margin   INTEGER,
    victory_type     TEXT,             -- runs / wickets
    FOREIGN KEY (series_id) REFERENCES series(series_id),
    FOREIGN KEY (team1_id) REFERENCES teams(team_id),
    FOREIGN KEY (team2_id) REFERENCES teams(team_id),
    FOREIGN KEY (venue_id) REFERENCES venues(venue_id),
    FOREIGN KEY (toss_winner_id) REFERENCES teams(team_id),
    FOREIGN KEY (winning_team_id) REFERENCES teams(team_id)
);

-- Player performance per match (the core fact table)
CREATE TABLE player_match_stats (
    stat_id           INTEGER PRIMARY KEY AUTOINCREMENT,
    match_id          INTEGER NOT NULL,
    player_id         INTEGER NOT NULL,
    team_id           INTEGER NOT NULL,
    innings_number    INTEGER NOT NULL,   -- 1 or 2 (or up to 4 for Tests)
    batting_position  INTEGER,
    runs_scored       INTEGER DEFAULT 0,
    balls_faced       INTEGER DEFAULT 0,
    is_out            INTEGER DEFAULT 1,   -- 1 = dismissed, 0 = not out
    fours             INTEGER DEFAULT 0,
    sixes             INTEGER DEFAULT 0,
    overs_bowled      REAL DEFAULT 0,
    runs_conceded     INTEGER DEFAULT 0,
    wickets_taken     INTEGER DEFAULT 0,
    catches_taken     INTEGER DEFAULT 0,
    stumpings         INTEGER DEFAULT 0,
    FOREIGN KEY (match_id) REFERENCES matches(match_id),
    FOREIGN KEY (player_id) REFERENCES players(player_id),
    FOREIGN KEY (team_id) REFERENCES teams(team_id)
);

-- Helpful indexes for the analytics queries
CREATE INDEX idx_pms_player   ON player_match_stats(player_id);
CREATE INDEX idx_pms_match    ON player_match_stats(match_id);
CREATE INDEX idx_matches_date ON matches(match_date);
CREATE INDEX idx_matches_type ON matches(match_type);
CREATE INDEX idx_players_country ON players(country);