import sqlite3
import json
import os

DB_PATH = "/mnt/nba_data/dosaros_local.db"
JSON_INPUT = "src/etl/all_eureleague_web.json"

def procesar_datos():
    if not os.path.exists(JSON_INPUT):
        print(f"❌ No existe el archivo {JSON_INPUT}")
        return

    print(f"Abriendo {JSON_INPUT}...")
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

    registros_totales = 0

    for nodo in nodos:
        bloque_data = nodo.get('data', {})
        
        # CASO 1: El contenido del archivo es una LISTA (Consola)
        if isinstance(bloque_data, list):
            for player in bloque_data:
                p_id = player.get('player_id')
                nombre = player.get('player_name')
                if not p_id: continue
                
                cursor.execute("""
                    INSERT OR REPLACE INTO euro_players_bio (player_id, player_name, image_url)
                    VALUES (?, ?, ?)
                """, (p_id, nombre, player.get('image_url')))
                registros_totales += 1

        # CASO 2: El contenido es un DICCIONARIO (API / Ficha completa)
        elif isinstance(bloque_data, dict):
            props = bloque_data.get('pageProps', {})
            inner_data = props.get('data', {})
            hero = inner_data.get('hero', {})
            
            if not hero: continue

            p_id = hero.get('id')
            nombre = f"{hero.get('firstName')} {hero.get('lastName')}"
            
            cursor.execute("""
                INSERT OR REPLACE INTO euro_players_bio 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                p_id,
                nombre,
                hero.get('position'),
                hero.get('height'),
                hero.get('clubName'),
                hero.get('nationality'),
                hero.get('photo')
            ))
            registros_totales += 1

    conn.commit()
    conn.close()
    print(f"✅ Proceso terminado. Se han cargado/actualizado {registros_totales} registros.")

if __name__ == "__main__":
    procesar_datos()