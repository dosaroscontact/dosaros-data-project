"""
Ejecutar en la Pi para ver qué endpoints funcionan:
  python explore_api.py
"""
from euroleague_api.game_stats import GameStats
from euroleague_api.player_stats import PlayerStats
from euroleague_api.team_stats import TeamStats
from euroleague_api.standings import Standings
from euroleague_api.EuroLeagueData import EuroLeagueData

SEASON = 2025  # E2025
COMP   = "E"   # Euroleague

print("=== GameStats - partido E2025 round 31 game 1 ===")
try:
    gs = GameStats(COMP)
    df = gs.get_game_stats(SEASON, 1, "boxscore")
    print(f"  OK → {df.shape} | cols: {list(df.columns[:8])}")
except Exception as e:
    print(f"  ERROR: {e}")

print("\n=== PlayerStats - stats temporada ===")
try:
    ps = PlayerStats(COMP)
    df = ps.get_players_stats_single_season(SEASON)
    print(f"  OK → {df.shape} | cols: {list(df.columns[:8])}")
    print(f"  Muestra:\n{df.head(2).to_string()}")
except Exception as e:
    print(f"  ERROR: {e}")

print("\n=== TeamStats ===")
try:
    ts = TeamStats(COMP)
    df = ts.get_teams_stats_single_season(SEASON)
    print(f"  OK → {df.shape} | cols: {list(df.columns[:8])}")
except Exception as e:
    print(f"  ERROR: {e}")

print("\n=== Standings ===")
try:
    st = Standings(COMP)
    df = st.get_standings(SEASON)
    print(f"  OK → {df.shape} | cols: {list(df.columns)}")
    print(df.to_string())
except Exception as e:
    print(f"  ERROR: {e}")

print("\n=== EuroLeagueData - game by round ===")
try:
    el = EuroLeagueData(COMP)
    df = el.get_game_metadata_season(SEASON)
    print(f"  OK → {df.shape} | cols: {list(df.columns[:10])}")
    print(df.head(3).to_string())
except Exception as e:
    print(f"  ERROR: {e}")
