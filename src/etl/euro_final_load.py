import sqlite3
import json
import os

DB_PATH = "/mnt/nba_data/dosaros_local.db"
JSON_INPUT = "src/etl/all_info_euroleague_web.json" # El unificado de 20 archivos

def setup_db(cursor):
    """Crea el esquema basado en tu análisis"""
    # 1. Equipos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS euro_teams (
            code TEXT PRIMARY KEY, name TEXT, tv_code TEXT, 
            primary_color TEXT, crest_url TEXT
        )""")
    # 2. Jugadores (Bio)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS euro_players (
            id TEXT PRIMARY KEY, first_name TEXT, last_name TEXT, 
            club_code TEXT, position TEXT, height INTEGER, 
            nationality TEXT, photo_url TEXT
        )""")
    # 3. Partidos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS euro_games (
            identifier TEXT PRIMARY KEY, date TEXT, round TEXT, 
            home_code TEXT, away_code TEXT, home_score INTEGER, 
            away_score INTEGER, status TEXT
        )""")

def cargar_todo():
    if not os.path.exists(JSON_INPUT):
        print("❌ Fichero no encontrado.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    setup_db(cursor)

    with open(JSON_INPUT, 'r', encoding='utf-8') as f:
        ficheros = json.load(f)

    for fichero in ficheros:
        name = fichero.get('name_file', '').lower()
        data = fichero.get('data', {})
        
        # --- CASO 1: EQUIPOS (teams.json) ---
        if 'teams' in name or 'clubs' in str(data)[:100]:
            clubs = data.get('pageProps', {}).get('clubs', {}).get('clubs', [])
            for c in clubs:
                cursor.execute("INSERT OR REPLACE INTO euro_teams VALUES (?,?,?,?,?)",
                             (c.get('code'), c.get('name'), c.get('tvCode'), 
                              c.get('primaryColour'), c.get('logo', {}).get('image')))

        # --- CASO 2: JUGADORES (Listado masivo o individual) ---
        # Si es el listado de 42 o los individuales 008104...
        props = data.get('pageProps', {}).get('data', {})
        hero = props.get('hero', {})
        
        if hero: # Es un perfil individual
            cursor.execute("INSERT OR REPLACE INTO euro_players VALUES (?,?,?,?,?,?,?,?)",
                         (hero.get('id'), hero.get('firstName'), hero.get('lastName'),
                          hero.get('clubCode'), hero.get('position'), hero.get('height'),
                          hero.get('nationality'), hero.get('photo')))
        
        # --- CASO 3: PARTIDOS (game-center.json) ---
        if 'game' in name:
            games = data.get('pageProps', {}).get('games', [])
            for g in games:
                cursor.execute("INSERT OR REPLACE INTO euro_games VALUES (?,?,?,?,?,?,?,?)",
                             (g.get('identifier'), g.get('date'), g.get('round', {}).get('round'),
                              g.get('home', {}).get('code'), g.get('away', {}).get('code'),
                              g.get('home', {}).get('score'), g.get('away', {}).get('score'),
                              g.get('status')))

    conn.commit()
    print(f"✅ ¡Carga masiva completada! Equipos, jugadores y partidos sincronizados.")
    conn.close()

if __name__ == "__main__":
    cargar_todo()