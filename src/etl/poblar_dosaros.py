import json
import sqlite3
import re
from pathlib import Path
from tqdm import tqdm

# ── CONFIGURACIÓN ──────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent
JSON_FOLDER = SCRIPT_DIR / ".." / ".." / "data" / "raw"
DB_PATH     = Path("/mnt/nba_data/dosaros_local.db")

# Aseguramos que la carpeta de la base de datos exista
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
# ───────────────────────────────────────────────────────────────────────────────

def create_tables(conn):
    """Crea la estructura de la base de datos si no existe."""
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
    
    CREATE TABLE IF NOT EXISTS venues (
        id TEXT PRIMARY KEY,
        name TEXT,
        capacity INTEGER,
        city TEXT
    );
    """
    conn.executescript(schema)
    conn.commit()

def load_json_safe(path: Path):
    for enc in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            with open(path, encoding=enc) as f:
                return json.loads(f.read())
        except Exception:
            continue
    return None

def safe_int(v):
    try:
        return int(v) if v not in (None, "", "None") else None
    except (ValueError, TypeError):
        return None

def upsert(conn, table, data):
    keys = list(data.keys())
    values = list(data.values())
    placeholders = ",".join(["?"] * len(keys))
    set_clause = ",".join([f"{k}=excluded.{k}" for k in keys if k != "id"])
    sql = f"""
    INSERT INTO {table} ({",".join(keys)})
    VALUES ({placeholders})
    ON CONFLICT(id) DO UPDATE SET {set_clause}
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

    stats_obj = p_data.get("stats", {})
    alltime_obj = stats_obj.get("alltime", {})
    for table in alltime_obj.get("statTables", []):
        group_name = table.get("groupName", "")
        for row in table.get("stats", []):
            season_code = row.get("season")
            club_code = row.get("club")
            stat_id = f"{player_id}_{season_code}_{club_code}"
            
            upsert(conn, "player_season_stats", {
                "id": stat_id,
                "player_id": player_id,
                "season_code": season_code,
                "team_code": club_code,
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
    })

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    
    # PASO CLAVE: Crear las tablas antes de insertar
    print("Inicializando esquema de base de datos...")
    create_tables(conn)

    json_files = list(JSON_FOLDER.rglob("*.json"))
    print(f"Procesando {len(json_files)} archivos...")

    for path in tqdm(json_files):
        data = load_json_safe(path)
        if not data: continue

        name = path.stem
        if re.match(r'^\d{5,6}$', name):
            process_player_json(conn, data)
        elif "club" in data.get("pageProps", {}):
            process_team_json(conn, data)

    conn.commit()
    
    print("\nResumen de carga:")
    for table in ["players", "player_season_stats", "teams"]:
        count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table}: {count} registros")
    
    conn.close()

if __name__ == "__main__":
    main()