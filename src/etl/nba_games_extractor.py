from nba_api.stats.endpoints import leaguegamefinder
from src.database.supabase_client import get_supabase_client
import pandas as pd

def sync_nba_games(season_id='2025-26'):
    supabase = get_supabase_client()
    
    # 1. Obtener IDs de equipos locales
    teams_resp = supabase.table("nba_teams").select("id").execute()
    valid_team_ids = [t['id'] for t in teams_resp.data]

    # 2. Petición a la API con la temporada elegida
    game_finder = leaguegamefinder.LeagueGameFinder(
        season_nullable=season_id, 
        league_id_nullable='00'
    )
    all_games = game_finder.get_data_frames()[0]
    
    # Filtro de equipos y separación local/visitante
    all_games = all_games[all_games['TEAM_ID'].isin(valid_team_ids)]
    home_games = all_games[all_games['MATCHUP'].str.contains('vs.')].copy()
    visitor_games = all_games[all_games['MATCHUP'].str.contains('@')].copy()

    # Año para la columna season
    year_int = int(season_id.split('-')[0])

    for _, home in home_games.iterrows():
        visitor = visitor_games[visitor_games['GAME_ID'] == home['GAME_ID']]
        if not visitor.empty:
            visitor_row = visitor.iloc[0]
            data = {
                "game_id": str(home["GAME_ID"]),
                "game_date": str(home["GAME_DATE"]),
                "home_team_id": int(home["TEAM_ID"]),
                "visitor_team_id": int(visitor_row["TEAM_ID"]),
                "home_points": int(home["PTS"]),
                "visitor_points": int(visitor_row["PTS"]),
                "season": year_int
            }
            supabase.table("nba_games").upsert(data).execute()