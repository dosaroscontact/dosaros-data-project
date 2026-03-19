import pandas as pd
from datetime import datetime, timedelta
from nba_api.stats.endpoints import scoreboardv3
from src.database.db_utils import get_db_connection

def get_nba_results_yesterday():
    # Fecha de ayer
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    try:
        board = scoreboardv3.ScoreboardV3(game_date=yesterday)
        # Usamos el método robusto de acceder al diccionario para evitar el error 'gameId'
        games_dict = board.get_dict()['scoreboard']['games']
        
        if not games_dict:
            return f"No hubo partidos de NBA el {yesterday}."

        results = []
        for game in games_dict:
            # Extraemos la información de cada equipo para cumplir con la PK (GAME_ID, TEAM_ID)
            # de tu archivo init_local_db.py
            game_id = game['gameId']
            home = game['homeTeam']
            away = game['awayTeam']
            
            # Formateamos para que coincida con la tabla nba_games (mayúsculas)
            for team in [home, away]:
                results.append({
                    'GAME_ID': game_id,
                    'TEAM_ID': team['teamId'],
                    'TEAM_ABBREVIATION': team['teamTricode'],
                    'TEAM_NAME': team['teamName'],
                    'GAME_DATE': yesterday,
                    'PTS': team['score'],
                    'WL': 'W' if team['score'] == max(home['score'], away['score']) else 'L'
                })
        
        df_to_save = pd.DataFrame(results)
        conn = get_db_connection()
        
        # Al usar if_exists='append', respetamos tu lógica de almacenamiento incremental
        df_to_save.to_sql('nba_games', conn, if_exists='append', index=False)
        conn.close()
        # ... (después de df_to_save.to_sql)
        resumen = "🏀 *NBA:*\n"
        # Agrupamos por GAME_ID para no repetir el partido por cada equipo
        for gid in df_to_save['GAME_ID'].unique():
            partido = df_to_save[df_to_save['GAME_ID'] == gid]
            home = partido.iloc[0] # Simplificación: la API V3 trae ambos en el dict
            # Si usas el bucle de mi respuesta anterior:
            visitante = partido.iloc[1]
            resumen += f"• {visitante['TEAM_ABBREVIATION']} {visitante['PTS']} - {home['PTS']} {home['TEAM_ABBREVIATION']}\n"
        
        return resumen
    except Exception as e:
        if "UNIQUE constraint failed" in str(e):
            return "Aviso: Los resultados de ayer ya estaban en la base de datos."
        return f"Error en la extracción: {e}"

if __name__ == "__main__":
    print(get_nba_results_yesterday())