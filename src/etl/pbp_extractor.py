import sqlite3
import pandas as pd
import time
# Cambiamos v2 por v3
from nba_api.stats.endpoints import playbyplayv3

def descargar_pbp_por_temporada(season_id_prefix):
    db_path = "/mnt/nba_data/dosaros_local.db"
    conn = sqlite3.connect(db_path)
    
    # Buscamos partidos que no tengan PBP registrado
    query = f"""
    SELECT DISTINCT GAME_ID 
    FROM nba_games 
    WHERE SEASON_ID LIKE '{season_id_prefix}%'
    AND GAME_ID NOT IN (SELECT DISTINCT gameId FROM nba_pbp)
    """
    try:
        games_to_download = pd.read_sql_query(query, conn)['GAME_ID'].tolist()
    except Exception:
        # Si la tabla nba_pbp no existe, descargamos todos los de la temporada
        query_simple = f"SELECT DISTINCT GAME_ID FROM nba_games WHERE SEASON_ID LIKE '{season_id_prefix}%'"
        games_to_download = pd.read_sql_query(query_simple, conn)['GAME_ID'].tolist()

    print(f"Partidos pendientes de PBP (V3) para temporada {season_id_prefix}: {len(games_to_download)}")

    for i, game_id in enumerate(games_to_download):
        try:
            print(f"[{i+1}/{len(games_to_download)}] Descargando PBP V3 - Partido {game_id}...")
            
            # Usamos PlayByPlayV3
            pbp = playbyplayv3.PlayByPlayV3(game_id=game_id)
            df = pbp.get_data_frames()[0]
            
            if df.empty:
                print(f"Aviso: El partido {game_id} no tiene datos PBP disponibles.")
                continue

            # Guardamos en la tabla nba_pbp
            df.to_sql('nba_pbp', conn, if_exists='append', index=False)
            
            # Pausa de seguridad para la Raspberry Pi y la API
            # Dentro del bucle:
            time.sleep(4)
            
        except Exception as e:
            print(f"Error en partido {game_id}: {e}")
            time.sleep(10)
            
    conn.close()

if __name__ == "__main__":
    # Plan nocturno: Temporadas recientes (más fiables en V3)
    # 2 = Regular, 4 = Playoffs
    anos = [2023, 2024] 
    tipos = ['2', '4']
    
    for ano in anos:
        for t in tipos:
            descargar_pbp_por_temporada(f"{t}{ano}")