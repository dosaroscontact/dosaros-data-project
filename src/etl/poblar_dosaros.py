import json
import sqlite3
import re
from pathlib import Path
from tqdm import tqdm

# ── CONFIGURACIÓN ──────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent
JSON_FOLDER = SCRIPT_DIR / ".." / ".." / "data" / "raw"
DB_PATH     = Path("/mnt/nba_data/dosaros_local.db")

DB_PATH.parent.mkdir(parents=True, exist_ok=True)
# ───────────────────────────────────────────────────────────────────────────────

def create_tables(conn):
    """Prepara el esquema completo de Dos Aros."""
    schema = """
    CREATE TABLE IF NOT EXISTS teams (
        code TEXT PRIMARY KEY,
        name TEXT,
        logo_url TEXT,
        is_active INTEGER DEFAULT 1
    );

    CREATE TABLE IF NOT EXISTS players (
        id TEXT PRIMARY KEY,
        name TEXT,
        position TEXT,
        height TEXT,
        nationality TEXT,
        image_url TEXT,
        current_team_code TEXT,
        FOREIGN KEY (current_team_code) REFERENCES teams(code)
    );

    CREATE TABLE IF NOT EXISTS player_season_stats (
        id TEXT PRIMARY KEY,
        player_id TEXT,
        season_code TEXT,
        team_code TEXT,
        competition TEXT,
        total_games INTEGER,
        total_points INTEGER,
        total_rebounds INTEGER,
        total_assists INTEGER,
        total_pir INTEGER,
        FOREIGN KEY (player_id) REFERENCES players(id)
    );
    """
    conn.executescript(schema)
    conn.commit()

def safe_int(v):
    if v is None or v == "" or str(v).lower() == "none":
        return 0
    try:
        return int(float(v))
    except (ValueError, TypeError):
        return 0

def upsert(conn, table, data, pk_name="id"):
    """Inserta o actualiza detectando la clave primaria correcta."""
    keys = list(data.keys())
    values = list(data.values())
    placeholders = ",".join(["?"] * len(keys))
    set_clause = ",".join([f"{k}=excluded.{k}" for k in keys if k != pk_name])
    
    sql = f"""
    INSERT INTO {table} ({",".join(keys)})
    VALUES ({placeholders})
    ON CONFLICT({pk_name}) DO UPDATE SET {set_clause}
    """
    conn.execute(sql, values)

def process_player_json(conn, data):
    p_data = data.get("pageProps", {}).get("data", {})
    hero = p_data.get("hero", {})
    if not hero: return

    player_id = str(hero.get("id"))
    
    upsert(conn, "players", {
        "id": player_id,
        "name": f"{hero.get('firstName')} {hero.get('lastName')}",
        "position": hero.get("position"),
        "height": hero.get("height"),
        "nationality": hero.get("nationality"),
        "image_url": hero.get("photo"),
        "current_team_code": hero.get("club", {}).get("code")
    })

    # Navegación hacia las estadísticas de carrera
    stats_root = p_data.get("stats", {})
    alltime = stats_root.get("alltime", {})
    stat_tables = alltime.get("statTables", [])

    for table in stat_tables:
        group_name = table.get("groupName", "Unknown")
        
        # Escaneo de filas: intentamos varias claves posibles en el JSON
        rows = []
        for key in ["stats", "tableStats", "rows", "items"]:
            if key in table and isinstance(table[key], list):
                rows = table[key]
                break
        
        for row in rows:
            season = row.get("season")
            club = row.get("club")
            if not season or not club: continue

            stat_id = f"{player_id}_{season}_{club}"
            
            upsert(conn, "player_season_stats", {
                "id": stat_id,
                "player_id": player_id,
                "season_code": season,
                "team_code": club,
                "competition": group_name,
                "total_games": safe_int(row.get("gamesPlayed")),
                "total_points": safe_int(row.get("points")),
                "total_rebounds": safe_int(row.get("rebounds")),
                "total_assists": safe_int(row.get("assists")),
                "total_pir": safe_int(row.get("pir"))
            })

def process_team_json(conn, data):
    pp = data.get("pageProps", {})
    club = pp.get("club", {})
    if not club: return

    upsert(conn, "teams", {
        "code": pp.get("clubCode"),
        "name": club.get("name"),
        "logo_url": club.get("logo", {}).get("image"),
        "is_active": 1
    }, pk_name="code")

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    create_tables(conn)

    json_files = list(JSON_FOLDER.rglob("*.json"))
    print(f"Poblando base de datos desde {len(json_files)} archivos...")

    for path in tqdm(json_files):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except: continue
        
        if not isinstance(data, dict): continue
        
        name = path.stem
        props = data.get("pageProps", {})
        
        if re.match(r'^\d{5,6}$', name):
            process_player_json(conn, data)
        elif "club" in props:
            process_team_json(conn, data)

    conn.commit()
    
    print("\n--- RESUMEN FINAL ---")
    for table in ["players", "teams", "player_season_stats"]:
        res = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"Registros en {table}: {res}")
    conn.close()

if __name__ == "__main__":
    main()