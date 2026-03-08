import pandas as pd
import sqlite3
from euroleague_api.boxscore_data import BoxScoreData
from euroleague_api.play_by_play_data import PlayByPlay
from src.utils.mapper import map_euro_to_canonical

DB_PATH = "/mnt/nba_data/dosaros_local.db"

def fetch_game_data(season, game_code):
    """Extrae boxscore del partido usando el método validado."""
    try:
        bx = BoxScoreData()
        # Según dir(), el método correcto para un partido es get_boxscore_data
        return bx.get_boxscore_data(season=int(season), game_code=game_code)
    except Exception as e:
        print(f"Error en boxscore: {e}")
        return None

def fetch_pbp_data(season, game_code):
    """Extrae play-by-play del partido."""
    try:
        pbp_inst = PlayByPlay()
        # Nota: Aquí el método suele ser get_game_play_by_play_data o similar
        # Si falla, haremos dir(PlayByPlay) en el siguiente paso
        return pbp_inst.get_game_play_by_play_data(season=int(season), game_code=game_code)
    except Exception as e:
        print(f"Error en PBP: {e}")
        return None

def process_and_save(df_players, season, game_code):
    """Procesa y guarda estadísticas de jugadores."""
    if df_players is None or df_players.empty: 
        return
    
    # La columna 'Team' a veces viene como código, normalizamos
    df_clean = df_players.copy()
    
    # Mapeo manual para asegurar que entra en euro_players_games
    mapping = {
        'Player_ID': 'player_id',
        'Team': 'team_id',
        'Points': 'pts',
        'TotalRebounds': 'reb',
        'Assists': 'ast'
    }
    
    df_clean = df_clean.rename(columns=mapping)
    df_clean['game_id'] = f"E{season}_{game_code}"
    
    # Seleccionamos solo las que tenemos en el esquema
    cols_to_keep = ['game_id', 'player_id', 'team_id', 'pts', 'reb', 'ast']
    df_final = df_clean[[c for c in cols_to_keep if c in df_clean.columns]]
    
    conn = sqlite3.connect(DB_PATH)
    df_final.to_sql("euro_players_games", conn, if_exists="append", index=False)
    conn.close()

def process_pbp(df_pbp, season, game_code):
    """Procesa y guarda eventos (Play-by-Play)."""
    if df_pbp is None or df_pbp.empty: 
        return
    
    df_canonical = map_euro_to_canonical(df_pbp, data_type="pbp")
    df_canonical['game_id'] = f"E{season}_{game_code}"
    
    conn = sqlite3.connect(DB_PATH)
    # x e y son los nombres que pusimos en el ALTER TABLE
    cols = ['game_id', 'event_num', 'period', 'clock', 'action_type', 'player_id', 'x', 'y']
    df_final = df_canonical[[c for c in cols if c in df_canonical.columns]]
    
    df_final.to_sql("euro_pbp", conn, if_exists="append", index=False)
    conn.close()