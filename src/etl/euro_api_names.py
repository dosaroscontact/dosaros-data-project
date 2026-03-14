import sqlite3
import pandas as pd
import requests

DB_PATH = "/mnt/nba_data/dosaros_local.db"

def mapear_nombres_resiliencia():
    conn = sqlite3.connect(DB_PATH)
    # Extraemos temporadas de los datos que ya tienes (ej: E2024)
    seasons = [s[0] for s in conn.execute("SELECT DISTINCT substr(game_id, 1, 5) FROM euro_pbp").fetchall()]
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    mapeo = []

    for season in seasons:
        print(f"Intentando obtener jugadores de la temporada: {season}...")
        # Endpoint de cabeceras de jugadores (más ligero y menos restrictivo)
        url = f"https://api-live.euroleague.net/v1/players/headers?seasonCode={season}"
        
        try:
            r = requests.get(url, headers=headers, timeout=15)
            if r.status_code == 200:
                data = r.json()
                for p in data:
                    mapeo.append({'player_id': p['personId'], 'player_name': p['playerName']})
            else:
                # Intento secundario sin la 'E' (ej: 2024 en lugar de E2024)
                alt_season = season.replace('E', '')
                url_alt = f"https://api-live.euroleague.net/v1/players/headers?seasonCode={alt_season}"
                r_alt = requests.get(url_alt, headers=headers, timeout=15)
                if r_alt.status_code == 200:
                    for p in r_alt.json():
                        mapeo.append({'player_id': p['personId'], 'player_name': p['playerName']})
        except Exception as e:
            print(f"Error en {season}: {e}")

    if mapeo:
        df = pd.DataFrame(mapeo).drop_duplicates(subset=['player_id'])
        df.to_sql('euro_players_ref', conn, if_exists='replace', index=False)
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_pid ON euro_players_ref (player_id);")
        print(f"✅ ÉXITO: {len(df)} jugadores registrados en euro_players_ref.")
    else:
        print("❌ Fallo crítico: Los endpoints de la API no responden. ¿Tienes conexión a internet en la Pi?")
    
    conn.close()

if __name__ == "__main__":
    mapear_nombres_resiliencia()