import sqlite3
import pandas as pd
import requests
import json
from bs4 import BeautifulSoup

DB_PATH = "/mnt/nba_data/dosaros_local.db"

def extraer_via_json_blob():
    # URL con el parámetro de "todos los jugadores"
    url = "https://www.euroleaguebasketball.net/euroleague/players/?seasonCode=E2024&pageType=all"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    print("Buscando el bloque de datos maestro...")
    try:
        r = requests.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # Buscamos el script que contiene el JSON de Next.js
        next_data_script = soup.find('script', id='__NEXT_DATA__')
        
        if not next_data_script:
            print("❌ No se encontró el bloque __NEXT_DATA__. El sitio tiene una protección mayor.")
            return

        # Parseamos el JSON
        all_data = json.loads(next_data_script.string)
        
        # Navegamos por la estructura del JSON (esta ruta es estándar en Next.js)
        # Nota: La ruta exacta puede variar, pero suele estar en props -> pageProps
        players_list = all_data.get('props', {}).get('pageProps', {}).get('players', {}).get('items', [])
        
        if not players_list:
            # Intento de ruta alternativa si la estructura cambió
            players_list = all_data.get('props', {}).get('pageProps', {}).get('data', {}).get('players', [])

        mapeo = []
        for p in players_list:
            # Según tu HTML: Melvin Ajinca -> ID 010316
            pid = p.get('personId')
            name = p.get('playerName') or f"{p.get('firstName', '')} {p.get('lastName', '')}"
            
            if pid and name:
                mapeo.append({
                    'player_id': str(pid).strip(), 
                    'player_name': name.strip().title()
                })

        if mapeo:
            conn = sqlite3.connect(DB_PATH)
            df = pd.DataFrame(mapeo).drop_duplicates(subset=['player_id'])
            df.to_sql('euro_players_ref', conn, if_exists='replace', index=False)
            conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_pid ON euro_players_ref (player_id);")
            print(f"✅ ¡CONSEGUIDO! {len(df)} jugadores registrados.")
            conn.close()
        else:
            print("❌ El bloque JSON estaba vacío o la ruta ha cambiado.")
            # Debug: imprimimos las llaves para ver dónde están los datos
            print("Estructura detectada:", all_data.get('props', {}).get('pageProps', {}).keys())

    except Exception as e:
        print(f"❌ Error técnico: {e}")

if __name__ == "__main__":
    extraer_via_json_blob()