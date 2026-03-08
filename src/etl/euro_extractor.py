import pandas as pd
import sqlite3
from euroleague_api.boxscore_data import BoxScoreData
from euroleague_api.play_by_play_data import PlayByPlay
from src.utils.mapper import map_euro_to_canonical

DB_PATH = "/mnt/nba_data/dosaros_local.db"
COMPETITION = "E" 

def fetch_game_data(season, game_code):
    try:
        bx = BoxScoreData(COMPETITION)
        data = bx.get_boxscore_data(int(season), int(game_code))
        return pd.DataFrame(data) if data else None
    except Exception as e:
        print(f"Error en boxscore: {e}")
        return None

def fetch_pbp_data(season, game_code):
    try:
        pbp_inst = PlayByPlay(COMPETITION)
        data = pbp_inst.get_game_play_by_play_data(int(season), int(game_code))
        return pd.DataFrame(data) if data else None
    except Exception as e:
        print(f"Error en PBP: {e}")
        return None

def process_and_save(df_players, season, game_code):
    if df_players is None or df_players.empty: return
    
    # MAPEADO CRÍTICO: Convertimos lo que da la API a lo que tiene tu DB
    mapping = {
        'Player_ID': 'player_id',
        'Team': 'team_id',
        'Points': 'pts',
        'TotalRebounds': 'reb',
        'Assists': 'ast'
    }
    
    # Creamos un nuevo DF solo con las columnas que existen en la tabla
    df_to_db = df_players.rename(columns=mapping)
    df_to_db['game_id'] = f"E{season}_{game_code}"
    
    # Solo nos quedamos con las columnas que tu tabla 'euro_players_games' acepta
    valid_cols = ['game_id', 'player_id', 'team_id', 'pts', 'reb', 'ast']
    df_final = df_to_db[[c for c in valid_cols if c in df_to_db.columns]]
    
    conn = sqlite3.connect(DB_PATH)
    df_final.to_sql("euro_players_games", conn, if_exists="append", index=False)
    conn.close()

def process_pbp(df_pbp, season, game_code):
    if df_pbp is None or df_pbp.empty: return
    
    df_canonical = map_euro_to_canonical(df_pbp, data_type="pbp")
    df_canonical['game_id'] = f"E{season}_{game_code}"
    
    conn = sqlite3.connect(DB_PATH)
    # x e y son los nombres que pusimos con el ALTER TABLE
    cols = ['game_id', 'event_num', 'period', 'clock', 'action_type', 'player_id', 'x', 'y']
    df_final = df_canonical[[c for c in cols if c in df_canonical.columns]]
    
    df_final.to_sql("euro_pbp", conn, if_exists="append", index=False)
    conn.close()