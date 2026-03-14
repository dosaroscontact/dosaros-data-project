import sqlite3
import pandas as pd
from euroleague_api.player_stats import PlayerStats # Importación por clase

DB_PATH = "/mnt/nba_data/dosaros_local.db"

def mapear_nombres():
    conn = sqlite3.connect(DB_PATH)
    game_ids = pd.read_sql("SELECT DISTINCT game_id FROM euro_pbp", conn)['game_id'].tolist()
    
    # Instanciamos la clase para la EuroLeague (competencia 'E')
    ps = PlayerStats(competition_code='E')
    
    mapeo = []
    print(f"Procesando {len(game_ids)} partidos para mapear jugadores...")

    for g_id in game_ids:
        try:
            # g_id es 'E2024_1'. Quitamos la 'E', separamos por '_'
            parts = g_id.replace('E', '').split('_')
            season = int(parts[0])
            game_code = int(parts[1])
            
            # Llamada al método de la clase
            df_game = ps.get_game_player_stats(season, game_code)
            
            for _, row in df_game.iterrows():
                mapeo.append({
                    'player_id': row['Player_ID'], 
                    'player_name': row['Player']
                })
        except Exception as e:
            # Silenciamos errores de partidos individuales para no frenar el proceso
            continue

    if mapeo:
        df_final = pd.DataFrame(mapeo).drop_duplicates(subset=['player_id'])
        df_final.to_sql('euro_players_ref', conn, if_exists='replace', index=False)
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_pid ON euro_players_ref (player_id);")
        print(f"✅ ¡Conseguido! {len(df_final)} jugadores mapeados en 'euro_players_ref'.")
    else:
        print("❌ Error: No se pudo extraer ningún nombre. Verifica la conexión.")
    
    conn.close()

if __name__ == "__main__":
    mapear_nombres()