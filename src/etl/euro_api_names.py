import sqlite3
import pandas as pd
from euroleague_api.player_stats import PlayerStats

DB_PATH = "/mnt/nba_data/dosaros_local.db"

def debug_mapeo():
    conn = sqlite3.connect(DB_PATH)
    # Probamos con UN solo partido para ver el error real
    g_id = conn.execute("SELECT game_id FROM euro_pbp LIMIT 1").fetchone()[0]
    conn.close()

    print(f"DEBUG: Probando con el partido {g_id}")
    ps = PlayerStats()
    
    # Desglosamos el ID: E2024_1 -> season=2024, game_code=1
    parts = g_id.replace('E', '').split('_')
    season = int(parts[0])
    game_code = int(parts[1])

    # Lanzamos la petición SIN try/except para ver el error en consola
    df = ps.get_game_player_stats(season=season, game_code=game_code)
    
    print("Resultado del DataFrame:")
    print(df)

if __name__ == "__main__":
    debug_mapeo()