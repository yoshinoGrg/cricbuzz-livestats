"""
utils/cricbuzz_api.py
------------------------
Wrapper around the "Cricket Live Line" API on RapidAPI.
Host: cricket-live-line1.p.rapidapi.com

Confirmed endpoints (tested directly in the RapidAPI playground):
  GET /home          -> general homepage feed
  GET /liveMatches   -> live matches, response shape:
                         {"msg": "...", "status": true, "data": [ {match}, {match}, ... ]}

Best-guess endpoints (same naming convention as /liveMatches -- verify in the
RapidAPI sidebar and fix the ENDPOINT constants below if any of these 404):
  GET /recentMatches
  GET /upcomingMatches
  GET /matchScorecard   (likely needs ?match_id=... -- check the "Params" tab)
  GET /playerRanking/{id}   (rankings list -- id may select batting/bowling/ODI/Test etc.)

Every function returns (data, error). data is already unwrapped to the
"data" field of the {msg, data, status} envelope this API uses, or None
plus an error string if something went wrong.
"""

import os
import requests
import streamlit as st

API_HOST = "cricket-live-line1.p.rapidapi.com"
BASE_URL = f"https://{API_HOST}"

ENDPOINTS = {
    "home": "/home",
    "live_matches": "/liveMatches",
    "recent_matches": "/recentMatches",
    "upcoming_matches": "/upcomingMatches",
    "match_scorecard": "/matchScorecard",
    "player_ranking": "/playerRanking/1",
}


def _get_api_key():
    try:
        return st.secrets["CRICBUZZ_API_KEY"]
    except Exception:
        return os.getenv("CRICBUZZ_API_KEY", "")


def _headers():
    return {
        "Content-Type": "application/json",
        "x-rapidapi-host": API_HOST,
        "x-rapidapi-key": _get_api_key(),
    }


def _get(endpoint: str, params: dict = None):
    key = _get_api_key()
    if not key:
        return None, "No Cricbuzz API key configured. Add CRICBUZZ_API_KEY to .env or Streamlit secrets."
    try:
        resp = requests.get(f"{BASE_URL}{endpoint}", headers=_headers(), params=params or {}, timeout=10)
        resp.raise_for_status()
        payload = resp.json()
        if isinstance(payload, dict) and "data" in payload:
            if payload.get("status") is False:
                return None, payload.get("msg", "API returned status: false")
            return payload["data"], None
        return payload, None
    except requests.exceptions.HTTPError as e:
        return None, f"API request failed ({e.response.status_code}): endpoint may be wrong or subscription inactive."
    except requests.exceptions.RequestException as e:
        return None, f"API request failed: {e}"


def get_home_feed():
    """GET /home -- general homepage feed."""
    return _get(ENDPOINTS["home"])


def get_live_matches():
    """GET /liveMatches -- confirmed working. Returns a list of live match dicts."""
    return _get(ENDPOINTS["live_matches"])


def get_recent_matches():
    """GET /recentMatches -- recently completed matches."""
    return _get(ENDPOINTS["recent_matches"])


def get_upcoming_matches():
    """GET /upcomingMatches -- upcoming scheduled matches."""
    return _get(ENDPOINTS["upcoming_matches"])


def get_match_scorecard(match_id):
    """GET /matchScorecard -- full scorecard. Tries match_id as a query param."""
    return _get(ENDPOINTS["match_scorecard"], params={"match_id": match_id})


def get_top_batting_stats(ranking_id: str = "1"):
    """GET /playerRanking/{id} -- leaderboard/rankings list."""
    return _get(f"/playerRanking/{ranking_id}")
