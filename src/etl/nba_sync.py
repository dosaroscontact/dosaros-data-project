import time
import logging
import pandas as pd
from datetime import datetime
from nba_api.stats.endpoints import leaguegamefinder, playbyplayv3, leaguegamelog
from src.database.db_utils import get_db_connection

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def _get_season_actual():
    """Devuelve la temporada NBA actual en formato '2025-26'."""
    now = datetime.now()
    year = now.year
    # La temporada NBA arranca en octubre; antes de octubre es la temp del año anterior
    if now.month >= 10:
        return f"{year}-{str(year + 1)[-2:]}"
    return f"{year - 1}-{str(year)[-2:]}"

def run_nba_daily():
    """Sincroniza partidos nuevos de regular season Y playoffs de la temporada actual."""
    conn = get_db_connection()
    season = _get_season_actual()
    logging.info(f"Sincronizando NBA — temporada {season}")

    existing_ids = pd.read_sql("SELECT DISTINCT GAME_ID FROM nba_games", conn)['GAME_ID'].tolist()
    total_nuevos = 0

    for season_type in ['Regular Season', 'Playoffs']:
        try:
            game_finder = leaguegamefinder.LeagueGameFinder(
                season_nullable=season,
                season_type_nullable=season_type,
                league_id_nullable='00'
            )
            all_games = game_finder.get_data_frames()[0]
            new_games = all_games[~all_games['GAME_ID'].isin(existing_ids)]

            if new_games.empty:
                logging.info(f"  {season_type}: sin partidos nuevos")
                continue

            new_games.to_sql("nba_games", conn, if_exists="append", index=False)
            total_nuevos += len(new_games)
            logging.info(f"  {season_type}: {len(new_games)} registros nuevos guardados")

            # Actualizar existing_ids para evitar duplicados en el siguiente loop
            existing_ids = existing_ids + new_games['GAME_ID'].tolist()

        except Exception as e:
            logging.error(f"  Error en {season_type}: {e}")

    if total_nuevos == 0:
        logging.info("Sin partidos nuevos. BD al día.")
        conn.close()
    logging.info("Sync NBA completado.")


if __name__ == "__main__":
    run_nba_daily()
        return
    
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