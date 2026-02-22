import time
from nba_api.stats.endpoints import leaguegamefinder
from src.database.supabase_client import get_supabase_client

def fetch_historical_games(start_year=1970):
    supabase = get_supabase_client()
    # Obtenemos el año actual dinámicamente
    current_year = 2026 
    
    for year in range(start_year, current_year):
        season_str = f"{year}-{str(year+1)[2:]}"
        print(f"Extrayendo temporada: {season_str}...")
        
        try:
            # Buscamos los partidos de esa temporada específica
            game_finder = leaguegamefinder.LeagueGameFinder(season_nullable=season_str)
            games = game_finder.get_data_frames()[0]
            
            if not games.empty:
                # Convertimos a formato lista de diccionarios para Supabase
                data = games.to_dict(orient='records')
                # .upsert evita duplicados si el proceso se reinicia
                supabase.table("nba_games").upsert(data).execute()
                print(f"Cargados {len(data)} partidos de {season_str}")
            
            # Pausa obligatoria para no ser baneado
            time.sleep(2) 
            
        except Exception as e:
            print(f"Error en temporada {season_str}: {e}")
            time.sleep(10) # Pausa más larga si hay error

if __name__ == "__main__":
    fetch_historical_games(1970)