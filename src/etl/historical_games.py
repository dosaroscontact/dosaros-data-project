import time
import sqlite3
import pandas as pd
from nba_api.stats.endpoints import leaguegamefinder

# Ruta a tu base de datos local en la Raspberry Pi
LOCAL_DB_PATH = "dosaros_local.db"

def fetch_historical_games(start_year=1983):
    # Conexión local: velocidad máxima
    conn = sqlite3.connect(LOCAL_DB_PATH)
    current_year = 2026 
    
    for year in range(start_year, current_year):
        season_str = f"{year}-{str(year+1)[2:]}"
        print(f"Procesando temporada: {season_str}...")
        
        try:
            # Extracción de datos
            game_finder = leaguegamefinder.LeagueGameFinder(season_nullable=season_str, league_id_nullable='00')
            games = game_finder.get_data_frames()[0]
            
            if not games.empty:
                # Limpieza rápida con Pandas
                games = games.drop_duplicates(subset=['GAME_ID', 'TEAM_ID'], keep='first')
                
                # Inserción masiva en SQLite
                # 'append' añade los datos si la tabla ya existe
                games.to_sql('nba_games', conn, if_exists='append', index=False)
                
                print(f"Éxito: {len(games)} partidos guardados localmente ({season_str})")
            
            # Respetamos la API de la NBA para evitar baneos de IP
            time.sleep(2) 
            
        except Exception as e:
            print(f"Error en temporada {season_str}: {e}")
            time.sleep(5)

    conn.close()
    print("Carga histórica local finalizada.")

if __name__ == "__main__":
    fetch_historical_games(1983)