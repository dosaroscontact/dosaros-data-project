import sqlite3
import json
import pandas as pd
import os

DB_PATH = "/mnt/nba_data/dosaros_local.db"
JSON_INPUT = "src/etl/players_manual.json"

def carga_final():
    if not os.path.exists(JSON_INPUT):
        print(f"❌ El archivo {JSON_INPUT} no existe.")
        return

    print(f"Leyendo {JSON_INPUT}...")
    try:
        with open(JSON_INPUT, 'r', encoding='utf-8') as f:
            texto = f.read().strip()
            if not texto:
                print("❌ El archivo está vacío.")
                return
            data = json.loads(texto)
        
        print(f"Estructura detectada: {type(data)}")

        # Lógica para extraer la lista de jugadores según el origen
        players = []
        if isinstance(data, list):
            players = data
        elif isinstance(data, dict):
            # Probar diferentes rutas de la API de Euroliga
            players = data.get('pageProps', {}).get('players', {}).get('items', [])
            if not players:
                players = data.get('pageProps', {}).get('dataPlayers', {}).get('players', [])

        if not players:
            print("❌ No se encontró la lista de jugadores. Primeros caracteres del archivo:")
            print(texto[:200])
            return

        df = pd.DataFrame(players)
        
        # Mapeo de columnas dinámico
        cols = df.columns
        if 'id' in cols: df = df.rename(columns={'id': 'player_id'})
        if 'personId' in cols: df = df.rename(columns={'personId': 'player_id'})
        
        if 'player_name' not in cols:
            if 'playerName' in cols:
                df = df.rename(columns={'playerName': 'player_name'})
            elif 'firstName' in cols and 'lastName' in cols:
                df['player_name'] = df['firstName'] + " " + df['lastName']

        # Limpieza final
        df = df[['player_id', 'player_name']].drop_duplicates()
        df['player_name'] = df['player_name'].str.title()

        conn = sqlite3.connect(DB_PATH)
        df.to_sql('euro_players_ref', conn, if_exists='replace', index=False)
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_pid ON euro_players_ref (player_id);")
        
        print(f"✅ ¡Éxito! {len(df)} jugadores registrados.")
        conn.close()

    except json.JSONDecodeError as e:
        print(f"❌ Error de formato JSON: {e}")
    except Exception as e:
        print(f"❌ Error técnico: {e}")

if __name__ == "__main__":
    carga_final()