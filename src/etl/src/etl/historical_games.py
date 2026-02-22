import time
import json
import pandas as pd
from nba_api.stats.endpoints import leaguegamefinder
from src.database.supabase_client import get_supabase_client

def fetch_historical_games(start_year=1970):
    """
    Extrae partidos de la NBA desde 1970 y los sube a Supabase.
    Limpia datos conflictivos (NaN, Inf) mediante doble serialización JSON.
    """
    supabase = get_supabase_client()
    current_year = 2026 
    
    for year in range(start_year, current_year):
        season_str = f"{year}-{str(year+1)[2:]}"
        print(f"Extrayendo temporada: {season_str}...")
        
        try:
            # Petición a la API de la NBA
            game_finder = leaguegamefinder.LeagueGameFinder(season_nullable=season_str)
            games = game_finder.get_data_frames()[0]
            
            if not games.empty:
                # 1. Limpieza inicial de nulos e infinitos con Pandas
                games = games.replace([float('inf'), float('-inf')], None)
                games = games.where(pd.notnull(games), None)
                
                # 2. Doble conversión JSON para limpiar tipos de datos incompatibles (numpy types)
                # Esto garantiza que el envío sea compatible con la API de Supabase
                clean_json = games.to_json(orient='records', date_format='iso')
                data = json.loads(clean_json)
                
                # 3. Carga masiva mediante upsert para evitar duplicados
                supabase.table("nba_games").upsert(data).execute()
                print(f"Exito: {len(data)} partidos cargados de la temporada {season_str}")
            else:
                print(f"Aviso: No hay datos para {season_str}")
            
            # Pausa obligatoria para evitar bloqueos por rate limiting
            time.sleep(2) 
            
        except Exception as e:
            print(f"Error en temporada {season_str}: {e}")
            # Espera extendida tras error antes de continuar
            time.sleep(10)

if __name__ == "__main__":
    print("Iniciando carga historica de Proyecto Dos Aros...")
    fetch_historical_games(1970)