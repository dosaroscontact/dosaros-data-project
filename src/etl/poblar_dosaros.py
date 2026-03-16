import json
import sqlite3
import re
from pathlib import Path
from datetime import datetime
from tqdm import tqdm

# ── CONFIGURACIÓN ──────────────────────────────────────────────────────────────
SCRIPT_DIR  = Path(__file__).parent
JSON_FOLDER = SCRIPT_DIR / ".." / ".." / "data" / "raw"
DB_PATH     = Path("/mnt/nba_data/dosaros_local.db")
# ───────────────────────────────────────────────────────────────────────────────

# Tablas existentes y sus esquemas reales (NO se tocan las NBA):
#
# players          → id, name, position, height, nationality, image_url, current_team_code
# teams            → code (PK), name, logo_url, is_active
# player_season_stats → id, player_id, season_code, team_code, competition,
#                       total_games, total_points, total_rebounds, total_assists, total_pir
# venues           → id (PK), name, capacity, city
# euro_games       → game_id (PK), date, home_team, away_team, score_home, score_away
# euro_players     → player_id (PK), player_name, position, height, club_name, nationality, image_url
# euro_players_games → game_id, player_id, team_id, pts, reb, ast
# euro_players_ref → player_id, player_name
# euro_standings   → team_code (PK), rank, wins, losses, points_diff, last_updated
# euro_stats_career → player_id, season_code, team_name, games_played, pts, reb, ast, pir, is_euroleague
# euro_teams       → team_code (PK), team_name, tv_code, logo_url, primary_color, arena
#
# Tablas NUEVAS que añade este script (solo si no existen):
# euro_games_extended → extiende euro_games con cuartos, coaches, venue, árbitros, audience
# euro_rounds         → calendario completo de jornadas

DDL_NEW_TABLES = """
CREATE TABLE IF NOT EXISTS euro_games_extended (
    game_id          TEXT PRIMARY KEY,
    identifier       TEXT,
    season_code      TEXT,
    comp_code        TEXT,
    phase_code       TEXT,
    round_number     INTEGER,
    home_coach       TEXT,
    away_coach       TEXT,
    home_q1          INTEGER,
    home_q2          INTEGER,
    home_q3          INTEGER,
    home_q4          INTEGER,
    home_ot1         INTEGER,
    away_q1          INTEGER,
    away_q2          INTEGER,
    away_q3          INTEGER,
    away_q4          INTEGER,
    away_ot1         INTEGER,
    venue_id         TEXT,
    audience         INTEGER,
    referee_1        TEXT,
    referee_2        TEXT,
    referee_3        TEXT
);

CREATE TABLE IF NOT EXISTS euro_rounds (
    id              TEXT PRIMARY KEY,
    season_code     TEXT,
    phase_code      TEXT,
    round_number    INTEGER,
    name            TEXT,
    date_start      TEXT,
    date_end        TEXT,
    dates_formatted TEXT
);

CREATE INDEX IF NOT EXISTS idx_euro_games_home   ON euro_games(home_team);
CREATE INDEX IF NOT EXISTS idx_euro_games_away   ON euro_games(away_team);
CREATE INDEX IF NOT EXISTS idx_pss_player        ON player_season_stats(player_id);
CREATE INDEX IF NOT EXISTS idx_pss_season        ON player_season_stats(season_code);
CREATE INDEX IF NOT EXISTS idx_euro_stats_player ON euro_stats_career(player_id);
"""


# ── HELPERS ───────────────────────────────────────────────────────────────────

def safe_int(v):
    if v is None or v == "" or str(v).lower() == "none":
        return None
    try:
        return int(float(str(v).replace(",", "")))
    except Exception:
        return None


def safe_float(v):
    if v is None or v == "" or str(v).lower() == "none":
        return None
    try:
        return float(str(v).replace("%", "").replace(",", ""))
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
    try:
        conn.execute(sql, values)
    except sqlite3.Error as e:
        # INSERT OR IGNORE como fallback silencioso
        try:
            conn.execute(
                f"INSERT OR IGNORE INTO {table} ({','.join(keys)}) VALUES ({placeholders})",
                values
            )
        except sqlite3.Error:
            pass


def extract_section_values(sections: list, row_index: int) -> dict:
    """Combina todas las secciones de una tabla EuroLeague en {heading: value} para la fila row_index."""
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


# ── PROCESAR JSON DE JUGADOR (XXXXXX.json) ────────────────────────────────────

def process_player_json(conn, data: dict):
    p_data = data.get("pageProps", {}).get("data", {})
    hero   = p_data.get("hero", {})
    if not hero:
        return

    player_id = safe_str(str(hero.get("id", "")))
    if not player_id:
        return

    team_code = safe_str(hero.get("clubCode"))
    full_name = f"{hero.get('firstName', '')} {hero.get('lastName', '')}".strip()

    # ── teams (esquema real: code, name, logo_url, is_active) ──
    if team_code:
        upsert(conn, "teams", {
            "code":      team_code,
            "name":      safe_str(hero.get("clubName")),
            "logo_url":  safe_str(hero.get("clubCrest")),
            "is_active": 1,
        }, pk_name="code")

    # ── players (esquema real: id, name, position, height, nationality, image_url, current_team_code) ──
    upsert(conn, "players", {
        "id":                player_id,
        "name":              full_name,
        "position":          safe_str(hero.get("position")),
        "height":            str(hero.get("height")) if hero.get("height") else None,
        "nationality":       safe_str(hero.get("nationality")),
        "image_url":         safe_str(hero.get("photo")),
        "current_team_code": team_code,
    })

    # ── euro_players (esquema real: player_id, player_name, position, height, club_name, nationality, image_url) ──
    upsert(conn, "euro_players", {
        "player_id":   player_id,
        "player_name": full_name,
        "position":    safe_str(hero.get("position")),
        "height":      safe_int(hero.get("height")),
        "club_name":   safe_str(hero.get("clubName")),
        "nationality": safe_str(hero.get("nationality")),
        "image_url":   safe_str(hero.get("photo")),
    }, pk_name="player_id")

    # ── euro_players_ref ──
    try:
        conn.execute(
            "INSERT OR IGNORE INTO euro_players_ref (player_id, player_name) VALUES (?, ?)",
            [player_id, full_name]
        )
    except sqlite3.Error:
        pass

    # ── Stats por temporada → player_season_stats + euro_stats_career ──
    alltime     = p_data.get("stats", {}).get("alltime", {})
    stat_tables = alltime.get("statTables", [])

    for st_block in stat_tables:
        competition  = safe_str(st_block.get("comp", "Euroleague"))
        is_euro      = 1 if competition and "euroleague" in competition.lower() else 0
        tables       = st_block.get("tables", {})
        if not tables:
            continue

        head_section = tables.get("headSection", {})
        sections     = tables.get("sections", [])
        head_stats   = head_section.get("stats", [])
        data_rows    = max(0, len(head_stats) - 2)  # últimas 2 = Total y Average

        for row_idx in range(data_rows):
            stat_sets = head_stats[row_idx].get("statSets", [])
            if len(stat_sets) < 2:
                continue

            s_code = safe_str(stat_sets[0].get("seasonCode") or stat_sets[0].get("value"))
            t_code = safe_str(stat_sets[1].get("value"))
            if not s_code or not t_code:
                continue

            vals = extract_section_values(sections, row_idx)

            g     = safe_int(vals.get("G"))
            pts   = safe_int(vals.get("TimeAndPoints_Pts") or vals.get("Pts"))
            reb   = safe_int(vals.get("T"))
            ast   = safe_int(vals.get("As"))
            pir   = safe_int(vals.get("PIR"))

            # player_season_stats (esquema real: id, player_id, season_code, team_code,
            #                      competition, total_games, total_points, total_rebounds,
            #                      total_assists, total_pir)
            upsert(conn, "player_season_stats", {
                "id":             f"{player_id}_{s_code}_{t_code}",
                "player_id":      player_id,
                "season_code":    s_code,
                "team_code":      t_code,
                "competition":    competition,
                "total_games":    g,
                "total_points":   pts,
                "total_rebounds": reb,
                "total_assists":  ast,
                "total_pir":      pir,
            })

            # euro_stats_career (esquema real: player_id, season_code, team_name,
            #                    games_played, pts, reb, ast, pir, is_euroleague)
            # Buscar nombre del equipo si existe
            row_team = conn.execute(
                "SELECT name FROM teams WHERE code = ?", [t_code]
            ).fetchone()
            team_name = row_team[0] if row_team else t_code

            try:
                conn.execute("""
                    INSERT INTO euro_stats_career
                        (player_id, season_code, team_name, games_played, pts, reb, ast, pir, is_euroleague)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(player_id, season_code, team_name) DO UPDATE SET
                        games_played=excluded.games_played,
                        pts=excluded.pts, reb=excluded.reb,
                        ast=excluded.ast, pir=excluded.pir,
                        is_euroleague=excluded.is_euroleague
                """, [player_id, s_code, team_name, g, pts, reb, ast, pir, is_euro])
            except sqlite3.Error:
                pass


# ── PROCESAR JSON DE EQUIPO (oly.json, bar.json…) ────────────────────────────

def process_team_json(conn, data: dict):
    pp        = data.get("pageProps", {})
    team_info = pp.get("hero", {}).get("teamInfo", {})
    club      = pp.get("club", {}) if isinstance(pp.get("club"), dict) else {}
    bottom    = club.get("bottomBlock", {}) or {}
    team_stat = pp.get("hero", {}).get("teamStat", {})

    team_code = safe_str(pp.get("clubCode", "")).upper() or safe_str(team_info.get("teamCode"))
    if not team_code:
        return

    team_name = safe_str(team_info.get("name") or pp.get("clubName"))
    crest_url = safe_str(team_info.get("teamCrestUrl"))

    # teams
    upsert(conn, "teams", {
        "code":      team_code,
        "name":      team_name,
        "logo_url":  crest_url,
        "is_active": 1,
    }, pk_name="code")

    # euro_teams (esquema real: team_code, team_name, tv_code, logo_url, primary_color, arena)
    upsert(conn, "euro_teams", {
        "team_code":     team_code,
        "team_name":     team_name,
        "tv_code":       safe_str(team_info.get("abbreviatedName")),
        "logo_url":      crest_url,
        "primary_color": safe_str(team_info.get("primaryColour")),
        "arena":         safe_str(bottom.get("arena")),
    }, pk_name="team_code")

    # euro_standings (esquema real: team_code, rank, wins, losses, points_diff, last_updated)
    wins   = safe_int(team_stat.get("wins"))
    losses = safe_int(team_stat.get("losses"))
    rank   = safe_int(team_stat.get("position"))
    if rank is not None:
        upsert(conn, "euro_standings", {
            "team_code":    team_code,
            "rank":         rank,
            "wins":         wins,
            "losses":       losses,
            "points_diff":  None,
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }, pk_name="team_code")

    # Próximo partido → euro_games + euro_games_extended
    fixture = club.get("fixture", {})
    if isinstance(fixture, dict) and "id" in fixture:
        process_game(conn, fixture)


# ── PROCESAR UN PARTIDO ───────────────────────────────────────────────────────

def process_game(conn, g: dict):
    game_id    = safe_str(g.get("id"))
    identifier = safe_str(g.get("identifier"))  # ej: "E2025_304"
    if not game_id:
        return

    season_d = g.get("season", {}) or {}
    phase_d  = g.get("phaseType", {}) or {}
    round_d  = g.get("round", {}) or {}
    home_d   = g.get("home", {}) or {}
    away_d   = g.get("away", {}) or {}
    venue_d  = g.get("venue", {}) or {}

    home_code  = safe_str(home_d.get("code"))
    away_code  = safe_str(away_d.get("code"))
    home_score = safe_int(home_d.get("score"))
    away_score = safe_int(away_d.get("score"))
    game_date  = safe_str(g.get("date", ""))
    if game_date:
        game_date = game_date[:10]  # solo YYYY-MM-DD

    # Equipos
    for td in [home_d, away_d]:
        tc = safe_str(td.get("code"))
        if tc:
            upsert(conn, "teams", {
                "code":     tc,
                "name":     safe_str(td.get("name")),
                "logo_url": (td.get("imageUrls") or {}).get("crest"),
                "is_active": 1,
            }, pk_name="code")
            upsert(conn, "euro_teams", {
                "team_code": tc,
                "team_name": safe_str(td.get("name")),
                "tv_code":   safe_str(td.get("tla")),
                "logo_url":  (td.get("imageUrls") or {}).get("crest"),
            }, pk_name="team_code")

    # venue → venues (esquema real: id, name, capacity, city)
    v_code = safe_str(venue_d.get("code"))
    if v_code:
        address = safe_str(venue_d.get("address") or "")
        # Intentar extraer ciudad del address
        city = address.split(",")[-1].strip() if address and "," in address else address
        upsert(conn, "venues", {
            "id":       v_code,
            "name":     safe_str(venue_d.get("name")),
            "capacity": safe_int(venue_d.get("capacity")),
            "city":     city or None,
        })

    # euro_games (esquema real: game_id, date, home_team, away_team, score_home, score_away)
    upsert(conn, "euro_games", {
        "game_id":    game_id,
        "date":       game_date,
        "home_team":  home_code,
        "away_team":  away_code,
        "score_home": home_score,
        "score_away": away_score,
    }, pk_name="game_id")

    # euro_games_extended (tabla nueva con el detalle extra)
    hq = home_d.get("quarters") or {}
    aq = away_d.get("quarters") or {}
    refs = g.get("referees") or []
    ref_names = [safe_str((r or {}).get("name")) for r in refs[:3]]
    while len(ref_names) < 3:
        ref_names.append(None)

    upsert(conn, "euro_games_extended", {
        "game_id":      game_id,
        "identifier":   identifier,
        "season_code":  safe_str(season_d.get("code")),
        "comp_code":    safe_str((g.get("competition") or {}).get("code")),
        "phase_code":   safe_str(phase_d.get("code")),
        "round_number": safe_int(round_d.get("round")) if isinstance(round_d, dict) else None,
        "home_coach":   safe_str((home_d.get("coach") or {}).get("name")),
        "away_coach":   safe_str((away_d.get("coach") or {}).get("name")),
        "home_q1":      safe_int(hq.get("q1")),
        "home_q2":      safe_int(hq.get("q2")),
        "home_q3":      safe_int(hq.get("q3")),
        "home_q4":      safe_int(hq.get("q4")),
        "home_ot1":     safe_int(hq.get("ot1")),
        "away_q1":      safe_int(aq.get("q1")),
        "away_q2":      safe_int(aq.get("q2")),
        "away_q3":      safe_int(aq.get("q3")),
        "away_q4":      safe_int(aq.get("q4")),
        "away_ot1":     safe_int(aq.get("ot1")),
        "venue_id":     v_code,
        "audience":     safe_int(g.get("audience")),
        "referee_1":    ref_names[0],
        "referee_2":    ref_names[1],
        "referee_3":    ref_names[2],
    }, pk_name="game_id")


# ── PROCESAR game-center.json ─────────────────────────────────────────────────

def is_game_center_page(pp: dict) -> bool:
    return "games" in pp and "currentSeasonCode" in pp


def process_game_center(conn, data: dict):
    pp = data.get("pageProps", {})
    if not isinstance(pp, dict):
        return

    s_code = safe_str(pp.get("currentSeasonCode"))

    # Partidos de la jornada
    for g in pp.get("games", []):
        process_game(conn, g)

    # Calendario de rondas → euro_rounds
    for rd in pp.get("allAvailableRounds", []):
        rd_id = f"{rd.get('seasonCode')}_{rd.get('round')}"
        upsert(conn, "euro_rounds", {
            "id":             rd_id,
            "season_code":    safe_str(rd.get("seasonCode")),
            "phase_code":     safe_str(rd.get("phaseTypeCode")),
            "round_number":   safe_int(rd.get("round")),
            "name":           safe_str(rd.get("name")),
            "date_start":     safe_str(rd.get("minGameStartDate")),
            "date_end":       safe_str(rd.get("maxGameStartDate")),
            "dates_formatted": safe_str(rd.get("datesFormmated")),
        })

    # Clasificación → euro_standings
    standings = pp.get("teamStandingsTable", {})
    if isinstance(standings, dict):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for team_code, position in standings.items():
            upsert(conn, "euro_standings", {
                "team_code":    team_code,
                "rank":         safe_int(position),
                "wins":         None,
                "losses":       None,
                "points_diff":  None,
                "last_updated": now,
            }, pk_name="team_code")


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=OFF")

    # Crear solo las tablas NUEVAS (no toca las existentes)
    conn.executescript(DDL_NEW_TABLES)
    conn.commit()

    files = list(JSON_FOLDER.rglob("*.json"))
    print(f"Poblando datos desde {len(files)} archivos...\n")

    counters = {"players": 0, "teams": 0, "game_center": 0, "errors": []}

    for path in tqdm(files):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                continue

            props = data.get("pageProps", {})
            stem  = path.stem

            if stem == "game-center":
                process_game_center(conn, data)
                counters["game_center"] += 1

            elif re.match(r"^\d{5,6}$", stem):
                if isinstance(props, dict) and is_game_center_page(props):
                    process_game_center(conn, data)
                    counters["game_center"] += 1
                else:
                    process_player_json(conn, data)
                    counters["players"] += 1

            elif isinstance(props, dict) and "club" in props and "hero" in props:
                process_team_json(conn, data)
                counters["teams"] += 1

        except Exception as e:
            counters["errors"].append((path.name, str(e)))
            continue

        if (counters["players"] % 100) == 0:
            conn.commit()

    conn.commit()
    conn.execute("PRAGMA foreign_keys=ON")

    # ── Resumen ──
    print("\n--- RESUMEN FINAL ---")
    all_tables = [
        "players", "teams", "player_season_stats",
        "euro_players", "euro_players_ref", "euro_teams",
        "euro_games", "euro_games_extended", "euro_rounds",
        "euro_standings", "euro_stats_career", "venues",
        "nba_games", "nba_players_games", "nba_pbp",
    ]
    for t in all_tables:
        try:
            n = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
            print(f"  {t:<25} {n:>8,} registros")
        except Exception:
            pass

    print(f"\n  JSONs procesados:")
    print(f"    Jugadores      {counters['players']:>6}")
    print(f"    Equipos        {counters['teams']:>6}")
    print(f"    Game-center    {counters['game_center']:>6}")

    if counters["errors"]:
        print(f"\n  ⚠️  {len(counters['errors'])} errores:")
        for name, err in counters["errors"][:10]:
            print(f"    {name}: {err}")

    conn.close()


if __name__ == "__main__":
    main()
