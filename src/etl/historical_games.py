import time
import json
import pandas as pd
from nba_api.stats.endpoints import leaguegamefinder
from src.database.supabase_client import get_supabase_client

def fetch_historical_games(start_year=1970):
    supabase = get_supabase_client()
    current_year = 2026 
    
    for year in range(start_year, current_year):
        season_str = f"{year}-{str(year+1)[2:]}"
        print(f"Extrayendo temporada: {season_str}...")
        
        try:
            # Forzamos LeagueID='00' para evitar los avisos de "No hay datos"
            game_finder = leaguegamefinder.LeagueGameFinder(
                season_nullable=season_str,
                league_id_nullable='00'
            )
            games = game_finder.get_data_frames()[0]
            
            if not games.empty:
                # 1. Eliminar duplicados que confunden al UPSERT de Supabase
                games = games.drop_duplicates(subset=['GAME_ID', 'TEAM_ID'])
                
                # 2. Limpieza de NaN e Infinitos
                games = games.replace([float('inf'), float('-inf')], None)
                games = games.where(pd.notnull(games), None)
                
                # 3. Solución al error "32.0": Convertimos columnas estadísticas a numérico
                # Esto asegura que "32.0" se envíe como 32
                cols_to_fix = ['MIN', 'PTS', 'FGM', 'FGA', 'FG3M', 'FG3A', 'FTM', 'FTA', 
                               'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF']
                
                for col in cols_to_fix:
                    if col in games.columns:
                        games[col] = pd.to_numeric(games[col], errors='coerce')

                # 4. Doble conversión JSON para limpiar tipos de numpy/pandas
                clean_json = games.to_json(orient='records', date_format='iso')
                data = json.loads(clean_json)
                
                # 5. Envío a Supabase
                supabase.table("nba_games").upsert(data).execute()
                print(f"Exito: {len(data)} partidos cargados de la temporada {season_str}")
            else:
                print(f"Aviso: No hay datos para {season_str}")
            
            time.sleep(2) 
            
        except Exception as e:
            print(f"Error en temporada {season_str}: {e}")
            time.sleep(5)

if __name__ == "__main__":
    print("Iniciando carga blindada de Proyecto Dos Aros...")
    fetch_historical_games(1970)
