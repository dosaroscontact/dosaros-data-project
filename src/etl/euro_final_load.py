import sqlite3
import json
import os

DB_PATH = "/mnt/nba_data/dosaros_local.db"
JSON_INPUT = "src/utils/all_eureleague_web.json"

def procesar_datos():
    if not os.path.exists(JSON_INPUT):
        print(f"No existe el archivo {JSON_INPUT}")
        return

    with open(JSON_INPUT, 'r', encoding='utf-8') as f:
        nodos = json.load(f)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Creación de tablas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS euro_players_bio (
            player_id TEXT PRIMARY KEY,
            player_name TEXT,
            position TEXT,
            height INTEGER,
            club_name TEXT,
            nationality TEXT,
            image_url TEXT
        )
    """)

    for nodo in nodos:
        # Navegación por la jerarquía detectada
        bloque_data = nodo.get('data', {})
        props = bloque_data.get('pageProps', {})
        inner_data = props.get('data', {})
        hero = inner_data.get('hero', {})

        if not hero:
            continue

        p_id = hero.get('id')
        nombre = f"{hero.get('firstName')} {hero.get('lastName')}"
        
        datos_bio = (
            p_id,
            nombre,
            hero.get('position'),
            hero.get('height'),
            hero.get('clubName'),
            hero.get('nationality'),
            hero.get('photo')
        )

        cursor.execute("INSERT OR REPLACE INTO euro_players_bio VALUES (?,?,?,?,?,?,?)", datos_bio)
        print(f"Cargado: {nombre}")

    conn.commit()
    conn.close()
    print("Proceso terminado.")

if __name__ == "__main__":
    procesar_datos()