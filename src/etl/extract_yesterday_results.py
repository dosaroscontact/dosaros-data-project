import pandas as pd
from datetime import datetime, timedelta
from nba_api.stats.endpoints import scoreboardv2
# Corregimos la importación para usar tu db_utils
from src.database.db_utils import get_db_connection 

def get_nba_results_yesterday():
    # Ayer en formato NBA API
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    try:
        # Traemos el Scoreboard
        board = scoreboardv2.ScoreboardV2(game_date=yesterday)
        # El dataset [1] (LineScore) contiene las estadísticas por equipo de cada partido
        line_score = board.get_data_frames()[1] 
        
        if line_score.empty:
            return f"No hubo partidos de NBA el {yesterday}."

        # Renombramos columnas para que coincidan con tu tabla 'nba_games'
        # La tabla nba_games espera campos como TEAM_ID, PTS, etc.
        df_to_save = line_score[[
            'TEAM_ID', 'TEAM_ABBREVIATION', 'TEAM_NAME', 'GAME_ID', 
            'GAME_DATE_EST', 'PTS', 'FG_PCT', 'FT_PCT', 'FG3_PCT', 'AST', 'REB', 'TOV'
        ]].copy()
        
        df_to_save.rename(columns={'GAME_DATE_EST': 'GAME_DATE'}, inplace=True)
        
        # Conexión usando tu db_utils
        conn = get_db_connection()
        
        # Guardado incremental: if_exists='append'
        # Nota: Si el partido ya existe, fallará por la PRIMARY KEY (GAME_ID, TEAM_ID)
        # Esto es bueno para evitar duplicados.
        df_to_save.to_sql('nba_games', conn, if_exists='append', index=False)
        conn.close()
        
        return f"Éxito: Se han guardado {len(df_to_save)} registros de equipo en nba_games."

    except Exception as e:
        if "UNIQUE constraint failed" in str(e):
            return "Aviso: Los resultados de ayer ya estaban en la base de datos."
        return f"Error en la extracción: {e}"

if __name__ == "__main__":
    print(get_nba_results_yesterday())