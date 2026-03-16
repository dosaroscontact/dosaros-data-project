import json
import sqlite3
import re
from pathlib import Path
from tqdm import tqdm

# ── CONFIGURACIÓN ──────────────────────────────────────────────────────────────
SCRIPT_DIR  = Path(__file__).parent
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
    if v is None or v == "" or str(v).lower() == "none":
        return 0
    try:
        return int(float(str(v).replace(",", "")))
    except Exception:
        return 0


def safe_str(v):
    if v is None:
        return ""
    return str(v).strip()


def upsert(conn, table, data, pk_name="id"):
    keys         = list(data.keys())
    values       = list(data.values())
    placeholders = ",".join(["?"] * len(keys))
    set_clause   = ",".join([f"{k}=excluded.{k}" for k in keys if k != pk_name])
    sql = (
        f"INSERT INTO {table} ({','.join(keys)}) VALUES ({placeholders})"
        f" ON CONFLICT({pk_name}) DO UPDATE SET {set_clause}"
    )
    conn.execute(sql, values)


def extract_section_values(sections: list, row_index: int) -> dict:
    """
    Combina todas las secciones de una tabla EuroLeague en un único dict
    {heading: value} para la fila `row_index`.

    Estructura real de cada sección:
      {
        "headings": ["G", "GS"],
        "groupStatsName": "TimeAndPoints",   # puede estar vacío
        "stats": [
          { "statSets": [{"value": "17"}, {"value": "7"}] },  # fila 0
          { "statSets": [{"value": "17"}, {"value": "7"}] },  # fila 1 (Total)
          { "statSets": [{"value": "1.0"}, {"value": "0.4"}] } # fila 2 (Average)
        ]
      }
    """
    result = {}
    for sec in sections:
        headings  = sec.get("headings", [])
        stats     = sec.get("stats", [])
        group     = sec.get("groupStatsName", "")

        if row_index >= len(stats):
            continue

        stat_sets = stats[row_index].get("statSets", [])
        for j, heading in enumerate(headings):
            if j < len(stat_sets):
                # Clave con prefijo de grupo para evitar colisiones entre secciones
                key = f"{group}_{heading}" if group else heading
                result[key] = stat_sets[j].get("value")
    return result


def process_player_json(conn, data):
    p_data = data.get("pageProps", {}).get("data", {})
    hero   = p_data.get("hero", {})
    if not hero:
        return

    player_id = str(hero.get("id", ""))
    if not player_id:
        return

    # BUG 1 CORREGIDO: clubCode está directamente en hero, no en hero.club
    team_code = hero.get("clubCode")

    upsert(conn, "players", {
        "id":                f"{player_id}",
        "name":              f"{hero.get('firstName', '')} {hero.get('lastName', '')}".strip(),
        "position":          hero.get("position"),
        "height":            str(hero.get("height")) if hero.get("height") else None,
        "nationality":       hero.get("nationality"),
        "image_url":         hero.get("photo"),
        "current_team_code": team_code,
    })

    # BUGS 2 y 3 CORREGIDOS: navegar la estructura real de alltime
    #
    # Estructura real:
    #   stats.alltime.statTables[]
    #     ├── comp: "Euroleague"
    #     └── tables
    #           ├── headSection.stats[i] → season_code y team_code de la fila i
    #           └── sections[]           → stats numéricas de la fila i
    #
    # Las últimas 2 filas de headSection son siempre "Total" y "Average".

    alltime     = p_data.get("stats", {}).get("alltime", {})
    stat_tables = alltime.get("statTables", [])

    for st_block in stat_tables:
        competition  = st_block.get("comp", "Euroleague")
        tables       = st_block.get("tables", {})
        if not tables:
            continue

        head_section = tables.get("headSection", {})
        sections     = tables.get("sections", [])
        head_stats   = head_section.get("stats", [])

        # Excluir las últimas 2 filas (Total y Average)
        n_rows    = len(head_stats)
        data_rows = max(0, n_rows - 2)

        for row_idx in range(data_rows):
            stat_sets = head_stats[row_idx].get("statSets", [])

            # headSection tiene 3 statSets por fila:
            #   [0] → { seasonCode: "E2025", value: "2025-26", statType: "season" }
            #   [1] → { value: "PBB" }   ← team_code
            #   [2] → { value: "https://...", statType: "image" }
            if len(stat_sets) < 2:
                continue

            s_code = stat_sets[0].get("seasonCode") or stat_sets[0].get("value")
            t_code = stat_sets[1].get("value")

            if not s_code or not t_code:
                continue

            # Extraer stats numéricas para esta fila desde las secciones
            vals = extract_section_values(sections, row_idx)

            # Mapeo de claves reales → columnas de la tabla
            # "G" y "GS" están en la sección sin groupStatsName
            # "Pts" está en la sección con groupStatsName="TimeAndPoints"
            # "T" (total rebounds) está en la sección "Rebounds"
            total_games    = safe_int(vals.get("G"))
            total_points   = safe_int(vals.get("TimeAndPoints_Pts") or vals.get("Pts"))
            total_rebounds = safe_int(vals.get("T"))
            total_assists  = safe_int(vals.get("As"))
            total_pir      = safe_int(vals.get("PIR"))

            stat_id = f"{player_id}_{s_code}_{t_code}"
            upsert(conn, "player_season_stats", {
                "id":             stat_id,
                "player_id":      player_id,
                "season_code":    s_code,
                "team_code":      t_code,
                "competition":    competition,
                "total_games":    total_games,
                "total_points":   total_points,
                "total_rebounds": total_rebounds,
                "total_assists":  total_assists,
                "total_pir":      total_pir,
            })


def process_team_json(conn, data):
    pp        = data.get("pageProps", {})
    club      = pp.get("club", {})
    team_info = pp.get("hero", {}).get("teamInfo", {})

    team_code = safe_str(pp.get("clubCode", "")).upper() or team_info.get("teamCode")
    team_name = team_info.get("name") or pp.get("clubName")
    crest_url = team_info.get("teamCrestUrl")

    if not team_code:
        return

    upsert(conn, "teams", {
        "code":      team_code,
        "name":      team_name,
        "logo_url":  crest_url,
        "is_active": 1,
    }, pk_name="code")


def main():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    create_tables(conn)

    files = list(JSON_FOLDER.rglob("*.json"))
    print(f"Poblando datos desde {len(files)} archivos...")

    errors = []
    for path in tqdm(files):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                continue

            props = data.get("pageProps", {})

            if re.match(r"^\d{5,6}$", path.stem):
                process_player_json(conn, data)
            elif "club" in props and "hero" in props:
                process_team_json(conn, data)

        except Exception as e:
            errors.append((path.name, str(e)))
            continue

    conn.commit()

    print("\n--- RESUMEN FINAL ---")
    for t in ["players", "teams", "player_season_stats"]:
        n = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        print(f"  {t}: {n} registros")

    if errors:
        print(f"\n⚠️  {len(errors)} archivos con error:")
        for name, err in errors[:10]:
            print(f"  {name}: {err}")

    conn.close()


if __name__ == "__main__":
    main()
