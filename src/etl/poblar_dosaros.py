import json
import os
import re
import sqlite3
import sys
from pathlib import Path
from datetime import datetime

try:
    from tqdm import tqdm
except ImportError:
    os.system("pip install tqdm")
    from tqdm import tqdm

# ── CONFIGURACIÓN ──────────────────────────────────────────────────────────────
# Ajustamos las rutas para que funcionen desde src/etl/
SCRIPT_DIR = Path(__file__).parent
JSON_FOLDER = SCRIPT_DIR / ".." / ".." / "data" / "raw"
DB_PATH     = Path("/mnt/nba_data/dosaros_local.db")

# Aseguramos que la carpeta de la base de datos exista
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
# ───────────────────────────────────────────────────────────────────────────────

def load_json_safe(path: Path):
    """Carga un JSON con manejo de encoding."""
    for enc in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            with open(path, encoding=enc) as f:
                content = f.read().strip()
            return json.loads(content)
        except Exception:
            continue
    return None

def safe_int(v):
    try:
        return int(v) if v not in (None, "", "None") else None
    except (ValueError, TypeError):
        return None

def upsert(conn, table, data):
    """Inserta o actualiza un registro basándose en su ID."""
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

def process_player_json(conn, data, filename):
    """Procesa el JSON de un jugador: Bio + Carrera Completa."""
    p_data = data.get("pageProps", {}).get("data", {})
    hero = p_data.get("hero", {})
    if not hero: return

    player_id = str(hero.get("id"))
    nombre = f"{hero.get('firstName')} {hero.get('lastName')}"

    # 1. Tabla: players (Bio)
    upsert(conn, "players", {
        "id": player_id,
        "name": nombre,
        "position": hero.get("position"),
        "height": hero.get("height"),
        "nationality": hero.get("nationality"),
        "image_url": hero.get("photo"),
        "current_team_code": hero.get("club", {}).get("code")
    })

    # 2. Estadísticas de CARRERA (Historial completo)
    # Ruta corregida: stats -> alltime -> statTables
    stats_obj = p_data.get("stats", {})
    alltime_obj = stats_obj.get("alltime", {})
    stat_tables = alltime_obj.get("statTables", [])

    for table in stat_tables:
        group_name = table.get("groupName", "")
        # Procesamos cada fila de la tabla (una por temporada/equipo)
        for row in table.get("stats", []):
            season_code = row.get("season")
            club_code = row.get("club")
            
            # ID único para la combinación jugador-temporada-equipo
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
    """Procesa el JSON de un equipo."""
    pp = data.get("pageProps", {})
    club = pp.get("club", {})
    if not club: return

    team_code = pp.get("clubCode")
    
    # Tabla: teams
    upsert(conn, "teams", {
        "code": team_code,
        "name": club.get("name"),
        "logo_url": club.get("logo", {}).get("image"),
        "is_active": 1
    })

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    
    # Usamos rglob para encontrar todos los JSONs en las subcarpetas de data/raw
    json_files = list(JSON_FOLDER.rglob("*.json"))
    print(f"Procesando {len(json_files)} archivos en {JSON_FOLDER}...")

    for path in tqdm(json_files):
        data = load_json_safe(path)
        if not data: continue

        # Identificar tipo de archivo por nombre o estructura
        name = path.stem
        if re.match(r'^\d{5,6}$', name):
            process_player_json(conn, data, name)
        elif "club" in data.get("pageProps", {}):
            process_team_json(conn, data)

    conn.commit()
    
    # Verificación final
    print("\nResumen de carga:")
    for table in ["players", "player_season_stats", "teams"]:
        count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table}: {count} registros")
    
    conn.close()

if __name__ == "__main__":
    main()