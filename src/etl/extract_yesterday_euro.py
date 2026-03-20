import pandas as pd
from datetime import datetime, timedelta
from euroleague_api.game_stats import GameStats
from src.database.db_utils import get_db_connection

def extract_euro_results_yesterday():
    # Fecha de ayer en formato que usa la Euroliga (ej: "October 24, 2024")
    # Nota: La API de Euroliga a veces usa formatos variables, 
    # ajustamos a la comparación más común.
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    season = 2025  # Temporada 2024-25
    
    try:
        gs = GameStats("E")
        # Obtenemos todos los gamecodes de la temporada
        df_games = gs.get_gamecodes_season(season)
        
        if df_games.empty:
            return "No se encontraron partidos para esta temporada de Euroliga."

        # Filtrar partidos jugados ayer
        # La columna suele ser 'Date' o similar dependiendo de la versión de la API
        # Intentamos estandarizar la fecha para comparar
        df_games['date_clean'] = pd.to_datetime(df_games['date']).dt.strftime('%Y-%m-%d')
        yesterday_games = df_games[df_games['date_clean'] == yesterday].copy()

        if yesterday_games.empty:
            return f"No hubo partidos de Euroliga el {yesterday}."

        # Preparar para la tabla 'euro_games' según tu init_db.py
        # Columnas: game_id, date, home_team, away_team, score_home, score_away
        results = []
        for _, row in yesterday_games.iterrows():
            results.append({
                'game_id': f"E{season}_{row['gamecode']}",
                'date': yesterday,
                'home_team': row['home'],
                'away_team': row['away'],
                'score_home': row['score_home'],
                'score_away': row['score_away']
            })

        df_to_save = pd.DataFrame(results)
        conn = get_db_connection()
        
        # Guardado incremental
        df_to_save.to_sql('euro_games', conn, if_exists='append', index=False)
        conn.close()
        # ... (después de df_to_save.to_sql)
        resumen = "🇪🇺 *Euroliga:*\n"
        for _, row in df_to_save.iterrows():
            resumen += f"• {row['home_team']} {row['score_home']} - {row['score_away']} {row['away_team']}\n"
        
        return resumen
    except Exception as e:
        if "UNIQUE constraint failed" in str(e):
            return "Aviso: Los partidos de Euroliga de ayer ya estaban registrados."
        return f"Error en Euroliga: {e}"

if __name__ == "__main__":
    print(extract_euro_results_yesterday())