from nba_api.stats.static import teams
from src.database.supabase_client import get_supabase_client

def run_nba_teams_sync():
    # 1. Obtener datos de la API
    nba_teams = teams.get_teams()
    
    # 2. Conectar a Supabase
    supabase = get_supabase_client()
    
    # 3. Subir datos
    for team in nba_teams:
        data = {
            "id": team["id"],
            "full_name": team["full_name"],
            "abbreviation": team["abbreviation"],
            "city": team["city"],
            "conference": "N/A" # La API base no da la conferencia directamente aquí
        }
        supabase.table("nba_teams").upsert(data).execute()
    
    print(f"Sincronizados {len(nba_teams)} equipos de la NBA.")

if __name__ == "__main__":
    run_nba_teams_sync()