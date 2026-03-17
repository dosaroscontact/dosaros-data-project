import logging
from euroleague_api.game_stats import GameStats
from euroleague_api.standings import Standings
from src.database.db_utils import get_db_connection

def run_euro_daily(season=2025):
    """Actualiza los últimos partidos y la clasificación de Euroliga."""
    conn = get_db_connection()
    gs = GameStats("E")
    st = Standings("E")
    
    # 1. Actualizar Clasificación
    logging.info("Actualizando standings de Euroliga...")
    try:
        df_st = st.get_standings(season)
        df_st.to_sql("euro_standings", conn, if_exists="replace", index=False)
    except Exception as e:
        logging.error(f"Error en standings Euroliga: {e}")

    # 2. Actualizar Partidos (Jornada actual)
    # Buscamos la jornada más reciente con resultados
    logging.info("Sincronizando jornada actual...")
    try:
        # Aquí puedes usar la lógica de tu update_dosaros.py para detectar la jornada
        # Por simplicidad, descargamos los últimos resultados disponibles
        df_games = gs.get_gamecodes_season(season)
        if not df_games.empty:
            df_games.to_sql("euro_games", conn, if_exists="append", index=False)
    except Exception as e:
        logging.error(f"Error cargando partidos Euroliga: {e}")
    
    conn.close()