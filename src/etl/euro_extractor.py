import pandas as pd
import sqlite3
from euroleague_api.boxscore_data import BoxScoreData
from euroleague_api.play_by_play_data import PlayByPlay
from src.utils.mapper import map_euro_to_canonical

DB_PATH = "/mnt/nba_data/dosaros_local.db"

def fetch_game_data(season, game_code):
    """Extrae boxscore usando el argumento validado: gamecode."""
    try:
        bx = BoxScoreData()
        # La librería requiere gamecode (sin guion bajo)
        data = bx.get_boxscore_data(season=int(season), gamecode=int(game_code))
        return pd.DataFrame(data) if data else None
    except Exception as e:
        print(f"Error en boxscore: {e}")
        return None

def fetch_pbp_data(season, game_code):
    """Extrae play-by-play usando gamecode."""
    try:
        pbp_inst = PlayByPlay()
        # Asumimos que PlayByPlay sigue el mismo patrón que BoxScoreData
        data = pbp_inst.get_game_play_by_play_data(season=int(season), gamecode=int(game_code))
        return pd.DataFrame(data) if data else None
    except Exception as e:
        print(f"Error en PBP: {e}")
        return None

def process_and_save(df_players, season, game_code):
    """Guarda estadísticas de jugadores."""
    if df_players is None or df_players.empty: return
    
    df_clean = df_players.copy()
    mapping = {'Player_ID': 'player_id', 'Team': 'team_id', 'Points': 'pts', 'TotalRebounds': 'reb', 'Assists': 'ast'}
    df_clean = df_clean.rename(columns=mapping)
    df_clean['game_id'] = f"E{season}_{game_code}"
    
    conn = sqlite3.connect(DB_PATH)
    df_clean.to_sql("euro_players_games", conn, if_exists="append", index=False)
    conn.close()

def process_pbp(df_pbp, season, game_code):
    """Guarda eventos de Play-by-Play."""
    if df_pbp is None or df_pbp.empty: return
    
    df_canonical = map_euro_to_canonical(df_pbp, data_type="pbp")
    df_canonical['game_id'] = f"E{season}_{game_code}"
    
    conn = sqlite3.connect(DB_PATH)
    cols = ['game_id', 'event_num', 'period', 'clock', 'action_type', 'player_id', 'x', 'y']
    df_final = df_canonical[[c for c in cols if c in df_canonical.columns]]
    df_final.to_sql("euro_pbp", conn, if_exists="append", index=False)
    conn.close()