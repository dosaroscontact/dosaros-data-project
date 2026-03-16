"""
Ejecutar en la Pi:  python explore_api.py
"""
import inspect
from euroleague_api.game_stats import GameStats
from euroleague_api.player_stats import PlayerStats
from euroleague_api.team_stats import TeamStats
from euroleague_api.standings import Standings
from euroleague_api.EuroLeagueData import EuroLeagueData

SEASON = 2025
COMP   = "E"

classes = {
    "GameStats":      GameStats(COMP),
    "PlayerStats":    PlayerStats(COMP),
    "TeamStats":      TeamStats(COMP),
    "Standings":      Standings(COMP),
    "EuroLeagueData": EuroLeagueData(COMP),
}

# Listar todos los métodos con su firma
for name, obj in classes.items():
    print(f"\n{'='*50}")
    print(f"{name}")
    print('='*50)
    for m in dir(obj):
        if m.startswith("_"):
            continue
        try:
            sig = inspect.signature(getattr(obj, m))
            print(f"  .{m}{sig}")
        except Exception:
            print(f"  .{m}")

# Probar llamadas reales con los métodos que parecen más relevantes
print("\n\n" + "="*50)
print("PRUEBAS REALES")
print("="*50)

print("\n--- Standings.get_standings(season, round) ---")
try:
    df = Standings(COMP).get_standings(SEASON, 31)
    print(f"  shape: {df.shape}")
    print(f"  cols:  {list(df.columns)}")
    print(df.head(3).to_string())
except Exception as e:
    print(f"  ERROR: {e}")

print("\n--- GameStats.get_game_stats(season, game_code) ---")
try:
    df = GameStats(COMP).get_game_stats(SEASON, 1)
    print(f"  shape: {df.shape}")
    print(f"  cols:  {list(df.columns[:10])}")
    print(df.head(2).to_string())
except Exception as e:
    print(f"  ERROR: {e}")

print("\n--- EuroLeagueData - buscar metodo de partidos ---")
try:
    el = EuroLeagueData(COMP)
    # Probar get_season_games o similar
    for m in ["get_season_games", "get_games", "get_game_metadata",
              "get_season_game_stats", "get_game_teams_data"]:
        if hasattr(el, m):
            sig = inspect.signature(getattr(el, m))
            print(f"  Encontrado: .{m}{sig}")
            try:
                df = getattr(el, m)(SEASON)
                print(f"    shape: {df.shape} | cols: {list(df.columns[:8])}")
                print(df.head(2).to_string())
            except Exception as e2:
                print(f"    ERROR al llamar: {e2}")
except Exception as e:
    print(f"  ERROR: {e}")
