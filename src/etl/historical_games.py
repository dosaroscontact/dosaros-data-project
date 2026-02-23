import time
import json
import pandas as pd
from nba_api.stats.endpoints import leaguegamefinder
from src.database.supabase_client import get_supabase_client

def fetch_historical_games(start_year=1983):
    supabase = get_supabase_client()
    current_year = 2026 
    
    for year in range(start_year, current_year):
        season_str = f"{year}-{str(year+1)[2:]}"
        print(f"Procesando temporada: {season_str}...")
        
        try:
            game_finder = leaguegamefinder.LeagueGameFinder(season_nullable=season_str, league_id_nullable='00')
            games = game_finder.get_data_frames()[0]
            
            if not games.empty:
                # Limpieza de duplicados y nulos
                games = games.drop_duplicates(subset=['GAME_ID', 'TEAM_ID'], keep='first')
                games = games.replace([float('inf'), float('-inf')], None)
                games = games.where(pd.notnull(games), None)
                
                # Conversión limpia a tipos Python
                data = json.loads(games.to_json(orient='records', date_format='iso'))
                
                # Intento de carga masiva
                try:
                    supabase.table("nba_games").upsert(data).execute()
                    print(f"Exito: {len(data)} partidos cargados ({season_str})")
                except Exception as batch_error:
                    print(f"Fallo en carga masiva de {season_str}, intentando modo fila a fila...")
                    for record in data:
                        try:
                            supabase.table("nba_games").upsert(record).execute()
                        except:
                            continue # Si una fila falla, la ignoramos para no frenar el proyecto
            
            time.sleep(2) 
            
        except Exception as e:
            print(f"Error en temporada {season_str}: {e}")
            time.sleep(10)

if __name__ == "__main__":
    print("Iniciando carga de Proyecto Dos Aros...")
    fetch_historical_games(1983) # Empezamos en 83 donde los datos son más fiables