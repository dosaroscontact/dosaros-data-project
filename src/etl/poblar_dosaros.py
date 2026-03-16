import json
import sqlite3
import re
from pathlib import Path
from tqdm import tqdm

# ── CONFIGURACIÓN ──────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent
JSON_FOLDER = SCRIPT_DIR / ".." / ".." / "data" / "raw"
DB_PATH     = Path("/mnt/nba_data/dosaros_local.db")
# ───────────────────────────────────────────────────────────────────────────────

def create_tables(conn):
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
    if v is None or v == "" or str(v).lower() == "none": return 0
    try: return int(float(str(v).replace(',', '')))
    except: return 0

def upsert(conn, table, data, pk_name="id"):
    keys = list(data.keys())
    values = list(data.values())
    placeholders = ",".join(["?"] * len(keys))
    set_clause = ",".join([f"{k}=excluded.{k}" for k in keys if k != pk_name])
    sql = f"INSERT INTO {table} ({','.join(keys)}) VALUES ({placeholders}) ON CONFLICT({pk_name}) DO UPDATE SET {set_clause}"
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

    # Lógica de mapeo dinámico por columnas
    alltime = p_data.get("stats", {}).get("alltime", {})
    for table in alltime.get("statTables", []):
        headers = table.get("tableHeader", [])
        # Mapeamos qué índice tiene cada estadística
        idx = {h.upper(): i for i, h in enumerate(headers)}
        
        for row in table.get("stats", []):
            sets = row.get("statSets", [])
            if not sets: continue
            
            # Extraer valores por su posición en el header
            s_code = sets[idx.get("SEASON", 0)].get("value")
            t_code = sets[idx.get("CLUB", 1)].get("value")
            if not s_code or not t_code: continue

            stat_id = f"{player_id}_{s_code}_{t_code}"
            upsert(conn, "player_season_stats", {
                "id": stat_id,
                "player_id": player_id,
                "season_code": s_code,
                "team_code": t_code,
                "competition": table.get("groupName"),
                "total_games": safe_int(sets[idx.get("G", -1)].get("value")) if "G" in idx else 0,
                "total_points": safe_int(sets[idx.get("PTS", -1)].get("value")) if "PTS" in idx else 0,
                "total_rebounds": safe_int(sets[idx.get("REB", -1)].get("value")) if "REB" in idx else 0,
                "total_assists": safe_int(sets[idx.get("AST", -1)].get("value")) if "AST" in idx else 0,
                "total_pir": safe_int(sets[idx.get("PIR", -1)].get("value")) if "PIR" in idx else 0
            })

def process_team_json(conn, data):
    pp = data.get("pageProps", {})
    club = pp.get("club", {})
    if club:
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
    files = list(JSON_FOLDER.rglob("*.json"))
    print(f"Poblando datos desde {len(files)} archivos...")
    for path in tqdm(files):
        try:
            with open(path, 'r', encoding='utf-8') as f: data = json.load(f)
            if not isinstance(data, dict): continue
            props = data.get("pageProps", {})
            if re.match(r'^\d{5,6}$', path.stem): process_player_json(conn, data)
            elif "club" in props: process_team_json(conn, data)
        except: continue
    conn.commit()
    print("\n--- RESUMEN FINAL ---")
    for t in ["players", "teams", "player_season_stats"]:
        print(f"  {t}: {conn.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0]} registros")
    conn.close()

if __name__ == "__main__": main()