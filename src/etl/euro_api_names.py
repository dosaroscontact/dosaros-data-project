import sqlite3
import pandas as pd
import requests
import re

DB_PATH = "/mnt/nba_data/dosaros_local.db"
# ID recuperado de tu fichero HAR
BUILD_ID_HAR = "hvGIyKafFCKSt6G5KJbO-" 

def extraer_nombres_definitivo():
    url_base = "https://www.euroleaguebasketball.net/euroleague/players/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    print("Sincronizando con la infraestructura de Euroliga...")
    try:
        r_base = requests.get(url_base, headers=headers, timeout=10)
        
        # Intento 1: Buscar buildId en el JSON interno
        match = re.search(r'"buildId":"(.*?)"', r_base.text)
        # Intento 2: Buscar en las rutas de los scripts (donde lo vimos en el HAR)
        if not match:
            match = re.search(r'/_next/static/(.*?)/_buildManifest\.js', r_base.text)
            
        build_id = match.group(1) if match else BUILD_ID_HAR
        print(f"Usando buildId: {build_id}")

        # URL maestra detectada en tus logs
        url_json = f"https://www.euroleaguebasketball.net/_next/data/{build_id}/en/euroleague/players.json?seasonCode=E2024&pageType=all"
        
        r_json = requests.get(url_json, headers=headers, timeout=15)
        if r_json.status_code != 200:
            print(f"⚠️ Error de acceso (Status {r_json.status_code}). Probando con buildId del HAR...")
            url_json = f"https://www.euroleaguebasketball.net/_next/data/{BUILD_ID_HAR}/en/euroleague/players.json?seasonCode=E2024&pageType=all"
            r_json = requests.get(url_json, headers=headers, timeout=15)

        data = r_json.json()
        players = data.get('pageProps', {}).get('players', {}).get('items', [])
        
        mapeo = []
        for p in players:
            mapeo.append({
                'player_id': str(p.get('personId')).strip(),
                'player_name': p.get('playerName', '').strip().title()
            })

        if mapeo:
            conn = sqlite3.connect(DB_PATH)
            df = pd.DataFrame(mapeo).drop_duplicates(subset=['player_id'])
            df.to_sql('euro_players_ref', conn, if_exists='replace', index=False)
            conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_pid ON euro_players_ref (player_id);")
            print(f"✅ ¡OBJETIVO 2 COMPLETADO! {len(df)} jugadores en 'euro_players_ref'.")
            conn.close()
        else:
            print("❌ No se encontraron datos en el JSON.")

    except Exception as e:
        print(f"❌ Error técnico: {e}")

if __name__ == "__main__":
    extraer_nombres_definitivo()