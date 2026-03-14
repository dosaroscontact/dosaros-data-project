import sqlite3
import pandas as pd
import requests
import re

DB_PATH = "/mnt/nba_data/dosaros_local.db"

def extraer_nombres_har_source():
    # 1. Detectamos el identificador de la base de datos dinámica (buildId)
    url_base = "https://www.euroleaguebasketball.net/euroleague/players/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    print("Sincronizando con la base de datos de la Euroliga...")
    try:
        r_base = requests.get(url_base, headers=headers, timeout=10)
        # Buscamos el buildId en el código fuente
        match = re.search(r'"buildId":"(.*?)"', r_base.text)
        if not match:
            print("❌ No se pudo detectar el buildId dinámico.")
            return
        
        build_id = match.group(1)
        print(f"Versión de datos detectada: {build_id}")

        # 2. Construimos la URL del JSON maestro descubierta en el HAR
        url_json = f"https://www.euroleaguebasketball.net/_next/data/{build_id}/en/euroleague/players.json?seasonCode=E2024&pageType=all"
        
        print("Descargando diccionario completo de jugadores...")
        r_json = requests.get(url_json, headers=headers, timeout=15)
        data = r_json.json()

        # 3. Navegamos por la estructura del JSON (pageProps -> players -> items)
        players = data.get('pageProps', {}).get('players', {}).get('items', [])
        
        mapeo = []
        for p in players:
            # personId y playerName son los campos que vimos en el HAR
            mapeo.append({
                'player_id': str(p.get('personId')).strip(),
                'player_name': p.get('playerName').strip().title()
            })

        if mapeo:
            conn = sqlite3.connect(DB_PATH)
            df = pd.DataFrame(mapeo).drop_duplicates(subset=['player_id'])
            df.to_sql('euro_players_ref', conn, if_exists='replace', index=False)
            conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_pid ON euro_players_ref (player_id);")
            print(f"✅ ¡CONSEGUIDO! {len(df)} jugadores registrados en la tabla 'euro_players_ref'.")
            conn.close()
        else:
            print("❌ El diccionario de la API volvió vacío.")

    except Exception as e:
        print(f"❌ Error en la extracción técnica: {e}")

if __name__ == "__main__":
    extraer_nombres_har_source()