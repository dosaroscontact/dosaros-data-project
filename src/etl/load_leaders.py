import json
import os
import sqlite3
import glob

DB_PATH = "/mnt/nba_data/dosaros_local.db"
# Ruta absoluta basada en tu comando find
DATA_PATH = "/home/pi/dosaros-data-project/src/etl/players/players_data/*.json"

def cargar_jugadores():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    archivos = glob.glob(DATA_PATH)
    if not archivos:
        print(f"❌ No se encontraron archivos en {DATA_PATH}")
        return

    print(f"Encontrados {len(archivos)} archivos. Procesando...")

    p_count = 0
    s_count = 0

    for ruta in archivos:
        with open(ruta, 'r', encoding='utf-8') as f:
            try:
                datos = json.load(f)
                # Intentamos ruta estándar: pageProps -> data
                p_props = datos.get('pageProps', {})
                p_data = p_props.get('data', {})
                
                hero = p_data.get('hero')
                if not hero:
                    continue

                p_id = hero.get('id')
                nombre = f"{hero.get('firstName')} {hero.get('lastName')}"
                
                # Inserción Jugador
                cursor.execute("""
                    INSERT OR REPLACE INTO euro_players 
                    (player_id, player_name, position, height, club_name, nationality, image_url)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (p_id, nombre, hero.get('position'), hero.get('height'), 
                      hero.get('club', {}).get('code'), hero.get('nationality'), hero.get('photo')))
                p_count += 1

                # Inserción Estadísticas (alltime puede estar en p_data o en p_props)
                alltime = p_data.get('alltime', p_props.get('alltime', {}))
                stat_tables = alltime.get('statTables', [])

                for table in stat_tables:
                    g_name = table.get('groupName', "")
                    # Marcamos si es Euroliga para el Dashboard
                    es_euro = "EuroLeague" in g_name
                    
                    for row in table.get('stats', []):
                        cursor.execute("""
                            INSERT OR REPLACE INTO euro_stats_career
                            (player_id, season_code, team_name, games_played, pts, reb, ast, pir, is_euroleague)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (p_id, row.get('season'), row.get('club'), row.get('gamesPlayed'),
                              row.get('points'), row.get('rebounds'), row.get('assists'), 
                              row.get('pir'), es_euro))
                        s_count += 1
                
            except Exception as e:
                print(f"Error en {os.path.basename(ruta)}: {e}")

    conn.commit()
    conn.close()
    print(f"✅ Finalizado. Jugadores: {p_count} | Registros de carrera: {s_count}")

if __name__ == "__main__":
    cargar_jugadores()