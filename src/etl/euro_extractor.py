import pandas as pd
import sqlite3
from euroleague_api.boxscore_data import BoxScoreData
from euroleague_api.play_by_play_data import PlayByPlay
from src.utils.mapper import map_euro_to_canonical

DB_PATH = "/mnt/nba_data/dosaros_local.db"

def fetch_game_data(season, game_code):
    """Extrae boxscore del partido."""
    try:
        bx = BoxScoreData()
        return bx.get_game_report(season, game_code)
    except Exception as e:
        print(f"Error en boxscore: {e}")
        return None

def fetch_pbp_data(season, game_code):
    """Extrae play-by-play del partido."""
    try:
        pbp_inst = PlayByPlay()
        return pbp_inst.get_game_play_by_play_data(season, game_code)
    except Exception as e:
        print(f"Error en PBP: {e}")
        return None

def process_and_save(df_players, season, game_code):
    """Procesa y guarda estadísticas de jugadores."""
    if df_players is None or df_players.empty: return
    
    # Usamos el mapper canónico (Paso 4)
    df_clean = df_players[['Player_ID', 'Team', 'Points', 'TotalRebounds', 'Assists']].copy()
    df_clean.columns = ['player_id', 'team_id', 'pts', 'reb', 'ast']
    df_clean['game_id'] = f"E{season}_{game_code}"
    
    conn = sqlite3.connect(DB_PATH)
    df_clean.to_sql("euro_players_games", conn, if_exists="append", index=False)
    conn.close()

def process_pbp(df_pbp, season, game_code):
    """Procesa y guarda eventos (Play-by-Play)."""
    if df_pbp is None or df_pbp.empty: return
    
    # Aplicamos el mapeo y normalización de coordenadas
    df_canonical = map_euro_to_canonical(df_pbp, data_type="pbp")
    df_canonical['game_id'] = f"E{season}_{game_code}"
    
    # Seleccionamos solo columnas que existen en tu tabla euro_pbp
    cols = ['game_id', 'event_num', 'period', 'clock', 'action_type', 'player_id', 'x', 'y']
    df_final = df_canonical[[c for c in cols if c in df_canonical.columns]]
    
    conn = sqlite3.connect(DB_PATH)
    df_final.to_sql("euro_pbp", conn, if_exists="append", index=False)
    conn.close()
    print(f"Cargados {len(df_final)} eventos de PBP.")