import sqlite3
import json
import os

DB_PATH = "/mnt/nba_data/dosaros_local.db"
# Usamos el archivo que ya tienes con los datos completos
JSON_INPUT = "src/etl/players_manual.json"

def cargar_desde_local():
    if not os.path.exists(JSON_INPUT):
        print(f"El archivo {JSON_INPUT} no esta en la ruta.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Creamos las tablas necesarias
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
            datos_unificados = json.load(f)
        
        for bloque in datos_unificados:
            # Extraemos la data segun la estructura 'bruta' que creamos
            file_data = bloque.get('data', {})
            page_props = file_data.get('pageProps', {})
            main_data = page_props.get('data', {})
            hero = main_data.get('hero', {})
            stats = main_data.get('stats', {})

            if not hero:
                continue

            # 1. Carga de Biografia
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

            # 2. Carga de Estadisticas (Promedios)
            current = stats.get('currentSeason', {}).get('widget', [])
            if current:
                # Buscamos los valores en el array de widgets
                stat_list = current[0].get('stats', [])
                pts = next((s['value'][0]['statValue'] for s in stat_list if s['name'] == 'PTS'), 0)
                reb = next((s['value'][0]['statValue'] for s in stat_list if s['name'] == 'REB'), 0)
                ast = next((s['value'][0]['statValue'] for s in stat_list if s['name'] == 'AST'), 0)
                pir = next((s['value'][0]['statValue'] for s in stat_list if s['name'] == 'PIR'), 0)

                cursor.execute("""
                    INSERT OR REPLACE INTO euro_stats_summary
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (p_id, "2024-25", pts, reb, ast, pir))

            print(f"Procesado: {nombre}")

        conn.commit()
        print("Carga local finalizada con éxito.")

    except Exception as e:
        print(f"Error en el proceso: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    cargar_desde_local()