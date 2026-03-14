import sqlite3
import pandas as pd
import requests

DB_PATH = "/mnt/nba_data/dosaros_local.db"

def mapear_nombres_directo():
    conn = sqlite3.connect(DB_PATH)
    # Obtenemos los pares season/game_code de tus datos
    game_ids = pd.read_sql("SELECT DISTINCT game_id FROM euro_pbp", conn)['game_id'].tolist()
    
    mapeo = []
    print(f"Procesando {len(game_ids)} partidos vía API directa...")

    for g_id in game_ids:
        try:
            # E2024_1 -> season=E2024, game_code=1
            season_code, game_code = g_id.split('_')
            
            # URL oficial de la Euroliga para estadísticas de partido
            url = f"https://api-live.euroleague.net/v1/games/traditionalstats?seasonCode={season_code}&gameCode={game_code}"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            # Extraemos jugadores de ambos equipos
            for team in ['home', 'away']:
                for player in data.get(team, {}).get('players', []):
                    mapeo.append({
                        'player_id': player['personId'], 
                        'player_name': player['playerName']
                    })
        except Exception:
            continue

    if mapeo:
        df_final = pd.DataFrame(mapeo).drop_duplicates(subset=['player_id'])
        df_final.to_sql('euro_players_ref', conn, if_exists='replace', index=False)
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_pid ON euro_players_ref (player_id);")
        print(f"✅ ¡POR FIN! {len(df_final)} jugadores mapeados en 'euro_players_ref'.")
    else:
        print("❌ Error: No se pudo obtener información de la API oficial.")
    
    conn.close()

if __name__ == "__main__":
    mapear_nombres_directo()