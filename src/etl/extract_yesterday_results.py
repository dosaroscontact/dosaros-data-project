import pandas as pd
from datetime import datetime, timedelta
from nba_api.stats.endpoints import scoreboardv3 # Cambiado a V3
from src.database.db_utils import get_db_connection

def get_nba_results_yesterday():
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    try:
        # ScoreboardV3 es la recomendada para la temporada actual
        board = scoreboardv3.ScoreboardV3(game_date=yesterday)
        df_games = board.get_data_frames()[0] 
        
        if df_games.empty:
            return f"No hubo partidos de NBA el {yesterday}."

        # En V3, la información de ambos equipos viene en la misma fila o estructurada diferente
        # Vamos a preparar los datos para tu tabla nba_games
        results = []
        for _, row in df_games.iterrows():
            # Registro Equipo Local
            results.append({
                'GAME_ID': row['gameId'],
                'TEAM_ID': row['homeTeamId'],
                'TEAM_ABBREVIATION': row['homeTeamTriCode'],
                'TEAM_NAME': row['homeTeamName'],
                'GAME_DATE': yesterday,
                'PTS': row['homeScore'],
                # Añadimos campos básicos para no dejar la fila vacía
                'WL': 'W' if row['homeScore'] > row['awayScore'] else 'L'
            })
            # Registro Equipo Visitante
            results.append({
                'GAME_ID': row['gameId'],
                'TEAM_ID': row['awayTeamId'],
                'TEAM_ABBREVIATION': row['awayTeamTriCode'],
                'TEAM_NAME': row['awayTeamName'],
                'GAME_DATE': yesterday,
                'PTS': row['awayScore'],
                'WL': 'W' if row['awayScore'] > row['homeScore'] else 'L'
            })
        
        df_to_save = pd.DataFrame(results)
        conn = get_db_connection()
        
        # Guardado incremental
        df_to_save.to_sql('nba_games', conn, if_exists='append', index=False)
        conn.close()
        
        return f"Éxito: {len(df_to_save)} registros guardados en nba_games usando V3."

    except Exception as e:
        if "UNIQUE constraint failed" in str(e):
            return "Aviso: Los resultados ya estaban registrados."
        return f"Error: {e}"

if __name__ == "__main__":
    print(get_nba_results_yesterday())