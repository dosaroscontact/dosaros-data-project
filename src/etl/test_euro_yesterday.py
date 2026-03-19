import pandas as pd
from euroleague_api.game_stats import GameStats
from src.database.db_utils import get_db_connection

def test_extraction(target_date="2025-03-14"): # Cambia esta fecha a una con partidos recientes
    print(f"--- Iniciando Test de Euroliga para la fecha: {target_date} ---")
    season = 2026 # Temporada actual 2024-25 (se define por el año de inicio)
    
    try:
        gs = GameStats("E")
        print("Consultando calendario de la temporada...")
        df_games = gs.get_gamecodes_season(season)
        
        if df_games.empty:
            print("Error: No se han recuperado partidos. Revisa la conexión o la temporada.")
            return

        # Limpieza y filtrado
        df_games['date_clean'] = pd.to_datetime(df_games['date']).dt.strftime('%Y-%m-%d')
        filtered_games = df_games[df_games['date_clean'] == target_date].copy()

        if filtered_games.empty:
            print(f"Aviso: No hubo partidos en la fecha {target_date}. Prueba con otra.")
            return

        print(f"Se han encontrado {len(filtered_games)} partidos. Procesando...")

        results = []
        for _, row in filtered_games.iterrows():
            # Usamos tu formato de ID: E2024_123
            results.append({
                'game_id': f"E{season}_{row['gamecode']}",
                'date': target_date,
                'home_team': row['home'],
                'away_team': row['away'],
                'score_home': row['score_home'],
                'score_away': row['score_away']
            })

        df_results = pd.DataFrame(results)
        print("\nDatos a insertar:")
        print(df_results)

        # Prueba de inserción en la base de datos local del HDD
        conn = get_db_connection()
        df_results.to_sql('euro_games', conn, if_exists='append', index=False)
        conn.close()
        
        print(f"\n✅ Test completado. {len(df_results)} partidos guardados en euro_games.")

    except Exception as e:
        if "UNIQUE constraint failed" in str(e):
            print("\nAviso: Los partidos ya existen en la base de datos (Test OK).")
        else:
            print(f"\n❌ Error durante el test: {e}")

if __name__ == "__main__":
    # Pon aquí una fecha reciente en la que sepas que hubo Euroliga
    test_extraction("2026-03-19")