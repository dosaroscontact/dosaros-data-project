import pandas as pd
import sqlite3
from euroleague_api.boxscore_data import BoxScoreData
from euroleague_api.play_by_play_data import PlayByPlay
from src.utils.mapper import map_euro_to_canonical

# Configuración según documentación nueva
DB_PATH = "/mnt/nba_data/dosaros_local.db"
COMPETITION = "E" # E para EuroLeague 

def fetch_game_data(season, game_code):
    """Extrae boxscore usando la clase BoxScoreData con competición."""
    try:
        bx = BoxScoreData(COMPETITION)
        data = bx.get_boxscore_data(int(season), int(game_code))
        return pd.DataFrame(data) if data else None
    except Exception as e:
        print(f"Error en boxscore: {e}")
        return None

def fetch_pbp_data(season, game_code):
    """Extrae play-by-play usando la clase PlayByPlay."""
    try:
        pbp_inst = PlayByPlay(COMPETITION)
        data = pbp_inst.get_game_play_by_play_data(int(season), int(game_code))
        return pd.DataFrame(data) if data else None
    except Exception as e:
        print(f"Error en PBP: {e}")
        return None

def process_and_save(df_players, season, game_code):
    """Procesa y guarda estadísticas de jugadores[cite: 2]."""
    if df_players is None or df_players.empty: return
    
    df_clean = df_players.copy()
    # Mapeo de columnas según el ejemplo de BoxScoreData
    df_clean['game_id'] = f"E{season}_{game_code}"
    
    conn = sqlite3.connect(DB_PATH)
    # Nota: Asegúrate de que las columnas coincidan con tu tabla local
    df_clean.to_sql("euro_players_games", conn, if_exists="append", index=False)
    conn.close()

def process_pbp(df_pbp, season, game_code):
    """Procesa y guarda eventos con coordenadas[cite: 3]."""
    if df_pbp is None or df_pbp.empty: return
    
    # El mapper usará COORD_X y COORD_Y del ejemplo 3 [cite: 3]
    df_canonical = map_euro_to_canonical(df_pbp, data_type="pbp")
    df_canonical['game_id'] = f"E{season}_{game_code}"
    
    conn = sqlite3.connect(DB_PATH)
    cols = ['game_id', 'NUMBER', 'PERIOD', 'MARKERTIME', 'PLAYTYPE', 'PLAYER_ID', 'COORD_X', 'COORD_Y']
    # Filtramos solo las columnas presentes para evitar errores de pandas
    df_final = df_canonical[[c for c in cols if c in df_canonical.columns]]
    df_final.to_sql("euro_pbp", conn, if_exists="append", index=False)
    conn.close()