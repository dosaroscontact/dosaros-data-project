import time
import json
import pandas as pd
from nba_api.stats.endpoints import leaguegamefinder
from src.database.supabase_client import get_supabase_client

def fetch_historical_games(start_year=1980):
    """
    Extrae partidos de la NBA fdsjhdskahdesde 1980 y los sube a Supabase.
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
                # 1. LIMPIEZA AGRESIVA DE DUPLICADOS
                # Forzamos que solo exista una fila por cada combinación de partido y equipo.
                # 'keep=first' garantiza que si hay basura, solo nos quedamos con la primera entrada.
                games = games.drop_duplicates(subset=['GAME_ID', 'TEAM_ID'], keep='first')
                
                # 2. LIMPIEZA DE TIPOS Y NULOS
                games = games.replace([float('inf'), float('-inf')], None)
                # Forzamos que GAME_ID sea string (a veces viene mezclado)
                games['GAME_ID'] = games['GAME_ID'].astype(str)
                games = games.where(pd.notnull(games), None)
                
                # 3. CONVERSIÓN A TIPOS NATIVOS
                # El serializador de Supabase es estricto; usamos la doble conversión JSON 
                # para asegurar que los tipos de numpy no se filtren.
                data = json.loads(games.to_json(orient='records', date_format='iso'))
                
                # 4. ENVÍO A SUPABASE
                if data:
                    supabase.table("nba_games").upsert(data).execute()
                    print(f"Exito: {len(data)} partidos cargados de la temporada {season_str}")            
            time.sleep(2) 
            
        except Exception as e:
            print(f"Error en temporada {season_str}: {e}")
            # Espera extendida tras error antes de continuar
            time.sleep(10)

if __name__ == "__main__":
    print("Iniciando carga historica de Proyecto Dos Aros...")
    fetch_historical_games(1980)