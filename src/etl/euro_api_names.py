import sqlite3
import pandas as pd
from euroleague_api import Boxscore

DB_PATH = "/mnt/nba_data/dosaros_local.db"

def mapear_nombres():
    conn = sqlite3.connect(DB_PATH)
    # Obtenemos los IDs de partidos ya descargados en pbp
    game_ids = pd.read_sql("SELECT DISTINCT game_id FROM euro_pbp", conn)['game_id'].tolist()
    
    mapeo = []
    for g_id in game_ids:
        try:
            season, code = g_id.split('_')
            box = Boxscore(int(season))
            # Extraemos nombres desde el boxscore oficial
            data = box.get_player_stats(int(code))
            for p in data:
                mapeo.append({'player_id': p['Player_ID'], 'player_name': p['Player']})
        except:
            continue

    if mapeo:
        df = pd.DataFrame(mapeo).drop_duplicates(subset=['player_id'])
        df.to_sql('euro_players_ref', conn, if_exists='replace', index=False)
        conn.execute("CREATE UNIQUE INDEX idx_pid ON euro_players_ref (player_id);")
        print(f"Hecho: {len(df)} jugadores registrados.")
    
    conn.close()

if __name__ == "__main__":
    mapear_nombres()