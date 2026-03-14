import sqlite3
import pandas as pd
import requests

DB_PATH = "/mnt/nba_data/dosaros_local.db"

def mapear_nombres_temporada():
    conn = sqlite3.connect(DB_PATH)
    # Identificamos qué temporadas tenemos en la base de datos (ej: E2023, E2024)
    seasons = conn.execute("SELECT DISTINCT substr(game_id, 1, 5) FROM euro_pbp").fetchall()
    seasons = [s[0] for s in seasons]
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    mapeo = []

    for season in seasons:
        print(f"Descargando lista de jugadores para {season}...")
        # Endpoint masivo: trae a todos los jugadores de la temporada de una vez
        url = f"https://api-live.euroleague.net/v1/players?seasonCode={season}&showAll=true"
        try:
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code == 200:
                data = r.json()
                for p in data.get('players', []):
                    mapeo.append({'player_id': p['personId'], 'player_name': p['playerName']})
            else:
                print(f"⚠️ {season} no disponible (Status {r.status_code})")
        except Exception as e:
            continue

    if mapeo:
        df = pd.DataFrame(mapeo).drop_duplicates(subset=['player_id'])
        df.to_sql('euro_players_ref', conn, if_exists='replace', index=False)
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_pid ON euro_players_ref (player_id);")
        print(f"✅ ¡CONSEGUIDO! {len(df)} jugadores mapeados.")
    else:
        print("❌ La API sigue sin responder. Pasamos al Objetivo 3 para no frenar la jornada.")
    
    conn.close()

if __name__ == "__main__":
    mapear_nombres_temporada()