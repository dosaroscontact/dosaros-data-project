import sqlite3
import json
import os

DB_PATH = "/mnt/nba_data/dosaros_local.db"
# Prueba primero con el archivo que tenga más información (el bruto)
JSON_INPUT = "src/utils/all_eureleague_web.json" 

def cargar_datos():
    if not os.path.exists(JSON_INPUT):
        print(f"❌ Error: No se encuentra {JSON_INPUT}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Crear tablas con toda la artillería
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

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS euro_stats_summary (
            player_id TEXT,
            season TEXT,
            points REAL,
            rebounds REAL,
            assists REAL,
            pir REAL,
            PRIMARY KEY (player_id, season)
        )
    """)

    try:
        with open(JSON_INPUT, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        
        count_bio = 0
        count_stats = 0

        for item in datos:
            # --- LÓGICA DE DETECCIÓN DE ESTRUCTURA ---
            # Caso A: Estructura Bruta (all_eureleague_web.json)
            if 'data' in item and 'pageProps' in item['data']:
                main = item['data']['pageProps'].get('data', {})
                hero = main.get('hero', {})
                stats_block = main.get('stats', {})
                
                p_id = hero.get('id')
                nombre = f"{hero.get('firstName')} {hero.get('lastName')}"
                pos = hero.get('position')
                alt = hero.get('height')
                club = hero.get('clubName')
                nac = hero.get('nationality')
                img = hero.get('photo')

                # Carga de estadísticas si existen
                current = stats_block.get('currentSeason', {}).get('widget', [])
                if current:
                    s_list = current[0].get('stats', [])
                    def get_val(name):
                        return next((s['value'][0]['statValue'] for s in s_list if s['name'] == name), 0)
                    
                    cursor.execute("INSERT OR REPLACE INTO euro_stats_summary VALUES (?,?,?,?,?,?)",
                                 (p_id, "2024-25", get_val('PTS'), get_val('REB'), get_val('AST'), get_val('PIR')))
                    count_stats += 1

            # Caso B: Estructura Básica (players_manual.json)
            else:
                p_id = item.get('player_id')
                nombre = item.get('player_name')
                img = item.get('image_url')
                # El resto de campos no existen en este formato
                pos, alt, club, nac = None, None, None, None

            # --- INSERCIÓN EN BIO ---
            if p_id and nombre:
                cursor.execute("""
                    INSERT OR REPLACE INTO euro_players_bio 
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (p_id, nombre, pos, alt, club, nac, img))
                count_bio += 1

        conn.commit()
        print(f"✅ Éxito: {count_bio} bios y {count_stats} tablas de stats cargadas.")

    except Exception as e:
        print(f"❌ Error crítico: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    cargar_datos()