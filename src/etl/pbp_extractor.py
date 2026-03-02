import sqlite3
import pandas as pd
import time
from nba_api.stats.endpoints import playbyplayv2

def descargar_pbp_por_temporada(season_id_prefix):
    db_path = "/mnt/nba_data/dosaros_local.db"
    conn = sqlite3.connect(db_path)
    
    # 1. Buscamos los IDs de partidos que ya tenemos pero no tienen PBP
    # Solo buscamos los de una temporada específica para ir paso a paso
    query = f"""
    SELECT DISTINCT GAME_ID 
    FROM nba_games 
    WHERE SEASON_ID LIKE '{season_id_prefix}%'
    AND GAME_ID NOT IN (SELECT DISTINCT GAME_ID FROM nba_pbp)
    """
    try:
        games_to_download = pd.read_sql_query(query, conn)['GAME_ID'].tolist()
    except:
        # Si la tabla pbp no existe aún
        query_simple = f"SELECT DISTINCT GAME_ID FROM nba_games WHERE SEASON_ID LIKE '{season_id_prefix}%'"
        games_to_download = pd.read_sql_query(query_simple, conn)['GAME_ID'].tolist()

    print(f"Partidos pendientes de PBP para temporada {season_id_prefix}: {len(games_to_download)}")

    for i, game_id in enumerate(games_to_download):
        try:
            print(f"[{i+1}/{len(games_to_download)}] Descargando PBP del partido {game_id}...")
            
            pbp = playbyplayv2.PlayByPlayV2(game_id=game_id)
            df = pbp.get_data_frames()[0]
            
            df.to_sql('nba_pbp', conn, if_exists='append', index=False)
            
            # Pausa obligatoria: La NBA es MUY estricta con el PBP
            time.sleep(2.2) 
            
        except Exception as e:
            print(f"Error en partido {game_id}: {e}")
            time.sleep(10)
            
    conn.close()

if __name__ == "__main__":
    # Ejemplo: Empecemos solo con los Playoffs de 1987 (prefijo 41987)
    # para probar la capacidad del HDD
    descargar_pbp_por_temporada('41987')