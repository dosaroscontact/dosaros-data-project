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
    CREATE TABLE IF NOT EXISTS competitions (
        code TEXT PRIMARY KEY,
        name TEXT
    );

    CREATE TABLE IF NOT EXISTS seasons (
        code        TEXT PRIMARY KEY,
        name        TEXT,
        alias       TEXT,
        year        INTEGER,
        comp_code   TEXT REFERENCES competitions(code)
    );

    CREATE TABLE IF NOT EXISTS venues (
        code     TEXT PRIMARY KEY,
        name     TEXT,
        capacity INTEGER,
        address  TEXT
    );

    CREATE TABLE IF NOT EXISTS teams (
        code     TEXT PRIMARY KEY,
        name     TEXT,
        logo_url TEXT,
        is_active INTEGER DEFAULT 1
    );

    CREATE TABLE IF NOT EXISTS players (
        id                 TEXT PRIMARY KEY,
        name               TEXT,
        position           TEXT,
        height             TEXT,
        nationality        TEXT,
        image_url          TEXT,
        current_team_code  TEXT REFERENCES teams(code)
    );

    CREATE TABLE IF NOT EXISTS rounds (
        id              TEXT PRIMARY KEY,
        season_code     TEXT REFERENCES seasons(code),
        phase_code      TEXT,
        round_number    INTEGER,
        name            TEXT,
        date_start      TEXT,
        date_end        TEXT,
        dates_formatted TEXT
    );

    CREATE TABLE IF NOT EXISTS games (
        id               TEXT PRIMARY KEY,
        identifier       TEXT UNIQUE,
        season_code      TEXT REFERENCES seasons(code),
        comp_code        TEXT REFERENCES competitions(code),
        phase_code       TEXT,
        round_number     INTEGER,
        game_date        TEXT,
        status           TEXT,
        home_team_code   TEXT REFERENCES teams(code),
        away_team_code   TEXT REFERENCES teams(code),
        home_score       INTEGER,
        away_score       INTEGER,
        home_q1          INTEGER,
        home_q2          INTEGER,
        home_q3          INTEGER,
        home_q4          INTEGER,
        home_ot1         INTEGER,
        home_ot2         INTEGER,
        away_q1          INTEGER,
        away_q2          INTEGER,
        away_q3          INTEGER,
        away_q4          INTEGER,
        away_ot1         INTEGER,
        away_ot2         INTEGER,
        home_coach       TEXT,
        away_coach       TEXT,
        venue_code       TEXT REFERENCES venues(code),
        audience         INTEGER,
        audience_confirmed INTEGER
    );

    CREATE TABLE IF NOT EXISTS referees (
        id          TEXT PRIMARY KEY,
        game_id     TEXT REFERENCES games(id),
        code        TEXT,
        name        TEXT,
        number      INTEGER,
        country     TEXT
    );

    CREATE TABLE IF NOT EXISTS standings (
        id          TEXT PRIMARY KEY,
        season_code TEXT REFERENCES seasons(code),
        team_code   TEXT REFERENCES teams(code),
        position    INTEGER
    );

    CREATE TABLE IF NOT EXISTS player_season_stats (
        id              TEXT PRIMARY KEY,
        player_id       TEXT REFERENCES players(id),
        season_code     TEXT,
        team_code       TEXT,
        competition     TEXT,
        total_games     INTEGER,
        total_points    INTEGER,
        total_rebounds  INTEGER,
        total_assists   INTEGER,
        total_pir       INTEGER
    );

    CREATE INDEX IF NOT EXISTS idx_games_season   ON games(season_code);
    CREATE INDEX IF NOT EXISTS idx_games_home     ON games(home_team_code);
    CREATE INDEX IF NOT EXISTS idx_games_away     ON games(away_team_code);
    CREATE INDEX IF NOT EXISTS idx_games_round    ON games(round_number);
    CREATE INDEX IF NOT EXISTS idx_pss_player     ON player_season_stats(player_id);
    CREATE INDEX IF NOT EXISTS idx_standings_seas ON standings(season_code);
    """
    conn.executescript(schema)
    conn.commit()


# ── HELPERS ───────────────────────────────────────────────────────────────────

def safe_int(v):
    if v is None or v == "" or str(v).lower() == "none":
        return None
    try:
        return int(float(str(v).replace(",", "")))
    except Exception:
        return None


def safe_str(v):
    if v is None:
        return None
    s = str(v).strip()
    return s if s and s.lower() != "none" else None


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
                key = f"{group}_{heading}" if group else heading
                result[key] = stat_sets[j].get("value")
    return result


# ── PROCESAR PARTIDO (usado tanto en game-center como en JSONs numerados) ─────

def process_game(conn, g: dict, season_code: str = None, comp_code: str = None):
    game_id    = safe_str(g.get("id"))
    identifier = safe_str(g.get("identifier"))
    if not game_id:
        return

    season_d = g.get("season", {})
    comp_d   = g.get("competition", {})
    phase_d  = g.get("phaseType", {})
    round_d  = g.get("round", {})
    home_d   = g.get("home", {})
    away_d   = g.get("away", {})
    venue_d  = g.get("venue", {})

    s_code = safe_str(season_d.get("code")) or season_code
    c_code = safe_str(comp_d.get("code"))   or comp_code

    # Competición y temporada
    if c_code:
        upsert(conn, "competitions", {"code": c_code, "name": safe_str(comp_d.get("name"))})
    if s_code:
        upsert(conn, "seasons", {
            "code":      s_code,
            "name":      safe_str(season_d.get("name")),
            "alias":     safe_str(season_d.get("alias")),
            "year":      safe_int(season_d.get("year")),
            "comp_code": c_code,
        })

    # Venue
    v_code = safe_str(venue_d.get("code"))
    if v_code:
        upsert(conn, "venues", {
            "code":     v_code,
            "name":     safe_str(venue_d.get("name")),
            "capacity": safe_int(venue_d.get("capacity")),
            "address":  safe_str(venue_d.get("address")),
        })

    # Equipos
    for td in [home_d, away_d]:
        tc = safe_str(td.get("code"))
        if tc:
            upsert(conn, "teams", {
                "code":     tc,
                "name":     safe_str(td.get("name")),
                "logo_url": td.get("imageUrls", {}).get("crest") if isinstance(td.get("imageUrls"), dict) else None,
            })

    # Cuartos
    hq = home_d.get("quarters", {}) or {}
    aq = away_d.get("quarters", {}) or {}

    # Entrenadores
    home_coach = safe_str((home_d.get("coach") or {}).get("name"))
    away_coach = safe_str((away_d.get("coach") or {}).get("name"))

    upsert(conn, "games", {
        "id":                game_id,
        "identifier":        identifier,
        "season_code":       s_code,
        "comp_code":         c_code,
        "phase_code":        safe_str(phase_d.get("code")),
        "round_number":      safe_int(round_d.get("round")) if isinstance(round_d, dict) else None,
        "game_date":         safe_str(g.get("date")),
        "status":            safe_str(g.get("status")),
        "home_team_code":    safe_str(home_d.get("code")),
        "away_team_code":    safe_str(away_d.get("code")),
        "home_score":        safe_int(home_d.get("score")),
        "away_score":        safe_int(away_d.get("score")),
        "home_q1":           safe_int(hq.get("q1")),
        "home_q2":           safe_int(hq.get("q2")),
        "home_q3":           safe_int(hq.get("q3")),
        "home_q4":           safe_int(hq.get("q4")),
        "home_ot1":          safe_int(hq.get("ot1")),
        "home_ot2":          safe_int(hq.get("ot2")),
        "away_q1":           safe_int(aq.get("q1")),
        "away_q2":           safe_int(aq.get("q2")),
        "away_q3":           safe_int(aq.get("q3")),
        "away_q4":           safe_int(aq.get("q4")),
        "away_ot1":          safe_int(aq.get("ot1")),
        "away_ot2":          safe_int(aq.get("ot2")),
        "home_coach":        home_coach,
        "away_coach":        away_coach,
        "venue_code":        v_code,
        "audience":          safe_int(g.get("audience")),
        "audience_confirmed": 1 if g.get("audienceConfirmed") else 0,
    })

    # Árbitros
    for ref in (g.get("referees") or []):
        if not isinstance(ref, dict):
            continue
        ref_id = f"{game_id}_{safe_str(ref.get('code'))}"
        upsert(conn, "referees", {
            "id":      ref_id,
            "game_id": game_id,
            "code":    safe_str(ref.get("code")),
            "name":    safe_str(ref.get("name")),
            "number":  safe_int(ref.get("number")),
            "country": safe_str((ref.get("country") or {}).get("name")),
        })


# ── PROCESAR game-center.json ─────────────────────────────────────────────────

def process_game_center(conn, data: dict):
    pp = data.get("pageProps", data)
    if not isinstance(pp, dict):
        return

    s_code = safe_str(pp.get("currentSeasonCode"))
    c_code = "E"

    # Partidos de la jornada
    for g in pp.get("games", []):
        process_game(conn, g, s_code, c_code)

    # Calendario completo de rondas
    for rd in pp.get("allAvailableRounds", []):
        rd_id = f"{rd.get('seasonCode')}_{rd.get('round')}"
        upsert(conn, "rounds", {
            "id":             rd_id,
            "season_code":    safe_str(rd.get("seasonCode")),
            "phase_code":     safe_str(rd.get("phaseTypeCode")),
            "round_number":   safe_int(rd.get("round")),
            "name":           safe_str(rd.get("name")),
            "date_start":     safe_str(rd.get("minGameStartDate")),
            "date_end":       safe_str(rd.get("maxGameStartDate")),
            "dates_formatted": safe_str(rd.get("datesFormmated")),
        })

    # Clasificación actual
    standings = pp.get("teamStandingsTable", {})
    if isinstance(standings, dict):
        for team_code, position in standings.items():
            upsert(conn, "standings", {
                "id":         f"{s_code}_{team_code}",
                "season_code": s_code,
                "team_code":  team_code,
                "position":   safe_int(position),
            })


# ── PROCESAR JSON NUMÉRICO (jornada individual si es game-center) ─────────────

def is_game_center_page(data: dict) -> bool:
    """Detecta si un JSON numérico es una página de game-center con partidos."""
    pp = data.get("pageProps", {})
    return isinstance(pp, dict) and "games" in pp and "currentSeasonCode" in pp


# ── PROCESAR JSON DE JUGADOR ──────────────────────────────────────────────────

def process_player_json(conn, data: dict):
    p_data = data.get("pageProps", {}).get("data", {})
    hero   = p_data.get("hero", {})
    if not hero:
        return

    player_id = safe_str(str(hero.get("id", "")))
    if not player_id:
        return

    team_code = safe_str(hero.get("clubCode"))
    if team_code:
        upsert(conn, "teams", {
            "code":     team_code,
            "name":     safe_str(hero.get("clubName")),
            "logo_url": safe_str(hero.get("clubCrest")),
        })

    upsert(conn, "players", {
        "id":                player_id,
        "name":              f"{hero.get('firstName', '')} {hero.get('lastName', '')}".strip(),
        "position":          safe_str(hero.get("position")),
        "height":            str(hero.get("height")) if hero.get("height") else None,
        "nationality":       safe_str(hero.get("nationality")),
        "image_url":         safe_str(hero.get("photo")),
        "current_team_code": team_code,
    })

    alltime     = p_data.get("stats", {}).get("alltime", {})
    stat_tables = alltime.get("statTables", [])

    for st_block in stat_tables:
        competition  = safe_str(st_block.get("comp", "Euroleague"))
        tables       = st_block.get("tables", {})
        if not tables:
            continue

        head_section = tables.get("headSection", {})
        sections     = tables.get("sections", [])
        head_stats   = head_section.get("stats", [])
        data_rows    = max(0, len(head_stats) - 2)

        for row_idx in range(data_rows):
            stat_sets = head_stats[row_idx].get("statSets", [])
            if len(stat_sets) < 2:
                continue

            s_code = safe_str(stat_sets[0].get("seasonCode") or stat_sets[0].get("value"))
            t_code = safe_str(stat_sets[1].get("value"))
            if not s_code or not t_code:
                continue

            vals = extract_section_values(sections, row_idx)

            upsert(conn, "player_season_stats", {
                "id":             f"{player_id}_{s_code}_{t_code}",
                "player_id":      player_id,
                "season_code":    s_code,
                "team_code":      t_code,
                "competition":    competition,
                "total_games":    safe_int(vals.get("G")),
                "total_points":   safe_int(vals.get("TimeAndPoints_Pts") or vals.get("Pts")),
                "total_rebounds": safe_int(vals.get("T")),
                "total_assists":  safe_int(vals.get("As")),
                "total_pir":      safe_int(vals.get("PIR")),
            })


# ── PROCESAR JSON DE EQUIPO ───────────────────────────────────────────────────

def process_team_json(conn, data: dict):
    pp        = data.get("pageProps", {})
    team_info = pp.get("hero", {}).get("teamInfo", {})
    team_code = safe_str(pp.get("clubCode", "")).upper() or safe_str(team_info.get("teamCode"))
    if not team_code:
        return

    upsert(conn, "teams", {
        "code":     team_code,
        "name":     safe_str(team_info.get("name") or pp.get("clubName")),
        "logo_url": safe_str(team_info.get("teamCrestUrl")),
        "is_active": 1,
    })

    # Próximo partido del equipo (fixture)
    club    = pp.get("club", {})
    fixture = club.get("fixture", {}) if isinstance(club, dict) else {}
    if isinstance(fixture, dict) and "id" in fixture:
        process_game(conn, fixture)


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=OFF")
    create_tables(conn)

    files = list(JSON_FOLDER.rglob("*.json"))
    print(f"Poblando datos desde {len(files)} archivos...\n")

    counters = {"players": 0, "teams": 0, "game_center": 0, "games_from_numbered": 0, "errors": []}

    for path in tqdm(files):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                continue

            props = data.get("pageProps", {})
            stem  = path.stem

            # game-center.json principal
            if stem == "game-center":
                process_game_center(conn, data)
                counters["game_center"] += 1

            # JSONs numéricos: pueden ser jugador O jornada de game-center
            elif re.match(r"^\d{5,6}$", stem):
                if is_game_center_page(data):
                    process_game_center(conn, data)
                    counters["games_from_numbered"] += 1
                else:
                    process_player_json(conn, data)
                    counters["players"] += 1

            # JSONs de equipo
            elif "club" in props and "hero" in props:
                process_team_json(conn, data)
                counters["teams"] += 1

        except Exception as e:
            counters["errors"].append((path.name, str(e)))
            continue

        # Commit cada 100 archivos para no perder progreso
        if (counters["players"] + counters["games_from_numbered"]) % 100 == 0:
            conn.commit()

    conn.commit()
    conn.execute("PRAGMA foreign_keys=ON")

    print("\n--- RESUMEN FINAL ---")
    tables = ["competitions", "seasons", "rounds", "venues", "teams",
              "players", "games", "referees", "standings", "player_season_stats"]
    for t in tables:
        n = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        print(f"  {t:<25} {n:>6} registros")

    print(f"\n  JSONs procesados:")
    print(f"    Jugadores            {counters['players']:>6}")
    print(f"    Equipos              {counters['teams']:>6}")
    print(f"    game-center.json     {counters['game_center']:>6}")
    print(f"    Jornadas numeradas   {counters['games_from_numbered']:>6}")

    if counters["errors"]:
        print(f"\n  ⚠️  {len(counters['errors'])} errores:")
        for name, err in counters["errors"][:10]:
            print(f"    {name}: {err}")

    conn.close()


if __name__ == "__main__":
    main()
