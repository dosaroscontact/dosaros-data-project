import sqlite3
import pandas as pd
from euroleague_api.player_stats import PlayerStats

DB_PATH = "/mnt/nba_data/dosaros_local.db"

def mapear_nombres():
    conn = sqlite3.connect(DB_PATH)
    game_ids = pd.read_sql("SELECT DISTINCT game_id FROM euro_pbp", conn)['game_id'].tolist()
    
    ps = PlayerStats()
    mapeo = []
    
    print(f"Procesando {len(game_ids)} partidos...")

    for g_id in game_ids:
        try:
            # E2024_1 -> season=2024, game_code=1
            parts = g_id.replace('E', '').split('_')
            season = int(parts[0])
            game_code = int(parts[1])
            
            # Nombre del método corregido según el error de Python
            df_game = ps.get_player_stats(season=season, game_code=game_code)
            
            if not df_game.empty:
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
        print(f"✅ ¡Éxito! {len(df_final)} jugadores mapeados en 'euro_players_ref'.")
    else:
        print("❌ Error: El DataFrame volvió vacío. Revisa game_ids.")
    
    conn.close()

if __name__ == "__main__":
    mapear_nombres()