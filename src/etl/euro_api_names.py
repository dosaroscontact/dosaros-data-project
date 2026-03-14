import sqlite3
import pandas as pd
from euroleague_api import player_stats

DB_PATH = "/mnt/nba_data/dosaros_local.db"

def mapear_nombres():
    conn = sqlite3.connect(DB_PATH)
    # Obtenemos IDs de partidos
    game_ids = pd.read_sql("SELECT DISTINCT game_id FROM euro_pbp", conn)['game_id'].tolist()
    
    mapeo = []
    print(f"Extrayendo nombres de {len(game_ids)} partidos...")
    
    for g_id in game_ids:
        try:
            # Formato esperado por la api: season y game_code
            season, code = g_id.split('_')
            # La función devuelve un DataFrame directo
            df_game = player_stats.get_game_player_stats(int(season), int(code))
            
            for _, row in df_game.iterrows():
                mapeo.append({
                    'player_id': row['Player_ID'], 
                    'player_name': row['Player']
                })
        except Exception:
            continue

    if mapeo:
        df_final = pd.DataFrame(mapeo).drop_duplicates(subset=['player_id'])
        df_final.to_sql('euro_players_ref', conn, if_exists='replace', index=False)
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_pid ON euro_players_ref (player_id);")
        print(f"Proceso finalizado: {len(df_final)} jugadores en tabla euro_players_ref.")
    else:
        print("No se recuperaron datos. Revisa la conexión o los game_ids.")
    
    conn.close()

if __name__ == "__main__":
    mapear_nombres()