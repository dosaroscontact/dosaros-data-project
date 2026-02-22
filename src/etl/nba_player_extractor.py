from nba_api.stats.endpoints import boxscoretraditionalv3 # Cambiado a V3
from src.database.supabase_client import get_supabase_client
import pandas as pd
import time

def sync_player_stats(limit_games=200):
    supabase = get_supabase_client()
    
    # 1. Obtener IDs de partidos
    games_resp = supabase.table("nba_games").select("game_id").limit(limit_games).execute()
    game_ids = [g['game_id'] for g in games_resp.data]

    for gid in game_ids:
        print(f"Extrayendo jugadores del partido {gid} (V3)...")
        try:
            # 2. Petición a la API V3
            box = boxscoretraditionalv3.BoxScoreTraditionalV3(game_id=gid)
            player_stats = box.get_data_frames()[0]

            for _, row in player_stats.iterrows():
                # Si el jugador no tiene minutos registrados, saltamos (DNP)
                if pd.isna(row.get('minutes')) or row.get('minutes') == "":
                    continue
                
                # Función auxiliar para convertir a 0 si es NaN
                safe_int = lambda x: int(x) if pd.notna(x) else 0
                safe_float = lambda x: float(x) if pd.notna(x) else 0.0

                data = {
                    "game_id": gid,
                    "player_id": int(row["personId"]),
                    "player_name": f"{row['firstName']} {row['familyName']}",
                    "team_id": int(row["teamId"]),
                    "points": safe_int(row.get("points")),
                    "rebounds": safe_int(row.get("reboundsTotal")),
                    "assists": safe_int(row.get("assists")),
                    "minutes": str(row.get("minutes", "0:00")),
                    "field_goals_pct": safe_float(row.get("fieldGoalsPercentage")),
                    "plus_minus": safe_float(row.get("plusMinusPoints"))
                }
                supabase.table("nba_player_stats").upsert(data).execute()
            
            time.sleep(1) # Un poco más de margen para la API
            
        except Exception as e:
            print(f"Error en partido {gid}: {e}")

if __name__ == "__main__":
    sync_player_stats()