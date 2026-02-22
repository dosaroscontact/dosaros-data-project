from nba_api.stats.static import teams
from src.database.supabase_client import get_supabase_client

# Diccionario de conferencias para enriquecer los datos
EASTERN_CONFERENCE = [
    'Atlanta Hawks', 'Boston Celtics', 'Brooklyn Nets', 'Charlotte Hornets',
    'Chicago Bulls', 'Cleveland Cavaliers', 'Detroit Pistons', 'Indiana Pacers',
    'Miami Heat', 'Milwaukee Bucks', 'New York Knicks', 'Orlando Magic',
    'Philadelphia 76ers', 'Toronto Raptors', 'Washington Wizards'
]

def run_nba_teams_sync():
    nba_teams = teams.get_teams()
    supabase = get_supabase_client()
    
    for team in nba_teams:
        # Determinamos la conferencia basándonos en el nombre
        conf = "East" if team["full_name"] in EASTERN_CONFERENCE else "West"
        
        data = {
            "id": team["id"],
            "full_name": team["full_name"],
            "abbreviation": team["abbreviation"],
            "city": team["city"],
            "conference": conf
        }
        # .upsert actualizará los registros existentes donde coincida el ID
        supabase.table("nba_teams").upsert(data).execute()
    
    print(f"Sincronizados {len(nba_teams)} equipos con su conferencia.")

if __name__ == "__main__":
    run_nba_teams_sync()