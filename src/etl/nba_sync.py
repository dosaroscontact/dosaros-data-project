import time
import logging
import pandas as pd
from nba_api.stats.endpoints import leaguegamefinder, playbyplayv3, leaguegamelog
from src.database.db_utils import get_db_connection

def run_nba_daily():
    """Sincroniza los partidos de la noche anterior en la NBA."""
    conn = get_db_connection()
    
    # 1. Buscar partidos nuevos
    logging.info("Buscando partidos nuevos de la NBA...")
    game_finder = leaguegamefinder.LeagueGameFinder(league_id_nullable='00')
    all_games = game_finder.get_data_frames()[0]
    
    # Filtramos para evitar duplicados comparando con lo que ya tienes en nba_games
    existing_ids = pd.read_sql("SELECT DISTINCT GAME_ID FROM nba_games", conn)['GAME_ID'].tolist()
    new_games = all_games[~all_games['GAME_ID'].isin(existing_ids)]
    
    if new_games.empty:
        logging.info("No hay partidos nuevos de la NBA.")
        conn.close()
        return

    # 2. Guardar partidos y descargar PBP
    new_games.to_sql("nba_games", conn, if_exists="append", index=False)
    
    for game_id in new_games['GAME_ID'].unique():
        logging.info(f"Descargando PBP para el partido {game_id}...")
        try:
            pbp = playbyplayv3.PlayByPlayV3(game_id=game_id)
            pbp.get_data_frames()[0].to_sql("nba_pbp", conn, if_exists="append", index=False)
            time.sleep(2) # Respeto a la API
        except Exception as e:
            logging.error(f"Error descargando PBP {game_id}: {e}")

    # 3. Actualizar estadísticas de jugadores (LeagueGameLog es más eficiente para esto)
    logging.info("Actualizando estadísticas de jugadores (NBA)...")
    try:
        log = leaguegamelog.LeagueGameLog(player_or_team_abbreviation='P')
        df_players = log.get_data_frames()[0]
        df_players.to_sql("nba_players_games", conn, if_exists="append", index=False)
    except Exception as e:
        logging.error(f"Error en estadísticas de jugadores NBA: {e}")

    conn.close()