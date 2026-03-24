import pandas as pd
from datetime import datetime, timedelta
from euroleague_api.game_stats import GameStats
from src.database.db_utils import get_db_connection

def extract_euro_results_yesterday(fecha=None):
    # 1. Fecha indicada o ayer por defecto
    yesterday_str = fecha if fecha else (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    # Temporada EuroLeague: oct-sep. Si mes >= 10, la temporada empieza ese año; si no, el año anterior
    _dt = datetime.strptime(yesterday_str, '%Y-%m-%d')
    season = _dt.year if _dt.month >= 10 else _dt.year - 1
    
    try:
        gs = GameStats("E")
        df_games = gs.get_gamecodes_season(season)
        
        if df_games.empty:
            return "Error: La API no devolvió partidos para la temporada 2025."

        # 2. Limpieza de nombres de columnas (la API a veces varía entre gameCode y gamecode)
        df_games.columns = [c.lower() for c in df_games.columns]
        
        # 3. Normalización de fechas para la comparación
        # La API suele devolver '2026-03-20T20:00:00' o '20-03-2026'
        df_games['date_clean'] = pd.to_datetime(df_games['date']).dt.strftime('%Y-%m-%d')
        
        # 4. Filtrado
        yesterday_games = df_games[df_games['date_clean'] == yesterday_str].copy()

        if yesterday_games.empty:
            # Esto nos dirá en el log qué fechas sí hay en la DB de la Euroliga
            fechas_disponibles = df_games['date_clean'].unique()[-3:]
            return f"No hubo partidos el {yesterday_str}. Últimas fechas: {fechas_disponibles}"

        results = []
        resumen = "🇪🇺 *Euroliga - Resultados:* \n"
        
        for _, row in yesterday_games.iterrows():            
            gamecode = str(row['gamecode'])
            g_id = gamecode if gamecode.startswith(f'E{season}_') else f"E{season}_{gamecode}"
            results.append({
                'game_id': g_id,
                'date': yesterday_str,
                'time': row.get('time', None),
                'home_team': row['hometeam'],
                'away_team': row['awayteam'],
                'score_home': row['homescore'],
                'score_away': row['awayscore']
            })
            resumen += f"• {row['hometeam']} {row['homescore']} - {row['awayscore']} {row['awayteam']}\n"

        # 5. Guardado en DB
        df_to_save = pd.DataFrame(results)
        conn = get_db_connection()
        # Usamos INSERT OR IGNORE vía SQL manual para evitar que el script muera por duplicados
        df_to_save.to_sql('euro_games', conn, if_exists='append', index=False, method=None)
        conn.close()
        
        return resumen

    except Exception as e:
        return f"Error técnico Euroliga: {str(e)}"