import sqlite3
import json
import pandas as pd

DB_PATH = "/mnt/nba_data/dosaros_local.db"
JSON_INPUT = "src/etl/players_manual.json" # O players_full.json

def carga_final():
    try:
        with open(JSON_INPUT, 'r') as f:
            data = json.load(f)
        
        # Si viene de la consola es una lista, si viene de la URL es un dict
        players = data if isinstance(data, list) else data.get('pageProps', {}).get('players', {}).get('items', [])
        
        if not players:
            print("❌ El archivo está vacío o mal formado.")
            return

        df = pd.DataFrame(players)
        # Normalizar nombres de columnas
        if 'id' in df.columns: df = df.rename(columns={'id': 'player_id'})
        
        # Limpieza rápida
        df['player_id'] = df['player_id'].astype(str)
        df = df[['player_id', 'player_name']].drop_duplicates()

        conn = sqlite3.connect(DB_PATH)
        df.to_sql('euro_players_ref', conn, if_exists='replace', index=False)
        conn.execute("CREATE UNIQUE INDEX idx_pid ON euro_players_ref (player_id);")
        
        print(f"✅ ¡OBJETIVO 2 CERRADO! {len(df)} jugadores en base de datos.")
        conn.close()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    carga_final()