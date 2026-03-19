import pandas as pd
from euroleague_api.game_stats import GameStats
from src.database.db_utils import get_db_connection

def test_extraction(target_date="2026-03-19"):
    print(f"--- Iniciando Test de Euroliga para la fecha: {target_date} ---")
    season = 2025 # Temporada 2025-26
    
    try:
        gs = GameStats("E")
        df_games = gs.get_gamecodes_season(season)
        
        if df_games.empty:
            print("Error: No se han recuperado partidos.")
            return

        # DEBUG: Imprimimos las columnas para ver qué nos da la API realmente
        print(f"Columnas detectadas en la API: {df_games.columns.tolist()}")

        # Limpieza de fecha
        # La columna suele llamarse 'date' o 'Date'
        date_col = 'date' if 'date' in df_games.columns else 'Date'
        df_games['date_clean'] = pd.to_datetime(df_games[date_col]).dt.strftime('%Y-%m-%d')
        
        filtered_games = df_games[df_games['date_clean'] == target_date].copy()

        if filtered_games.empty:
            print(f"Aviso: No hubo partidos el {target_date}. Mostrando fechas disponibles:")
            print(df_games['date_clean'].unique()[:5]) # Muestra las 5 primeras fechas
            return

        results = []
        for _, row in filtered_games.iterrows():
            # Mapeo flexible de columnas
            results.append({
                'game_id': f"E{season}_{row.get('gamecode', row.get('game_code'))}",
                'date': target_date,
                'home_team': row.get('home', row.get('home_team')),
                'away_team': row.get('away', row.get('away_team')),
                'score_home': row.get('score_home', 0),
                'score_away': row.get('score_away', 0)
            })

        df_results = pd.DataFrame(results)
        conn = get_db_connection()
        df_results.to_sql('euro_games', conn, if_exists='append', index=False)
        conn.close()
        
        print(f"✅ Éxito: {len(df_results)} partidos guardados.")

    except Exception as e:
        print(f"❌ Error durante el test: {e}")

if __name__ == "__main__":
    # Asegúrate de usar una fecha que ya haya pasado y tenga partidos
    test_extraction("2026-03-19")