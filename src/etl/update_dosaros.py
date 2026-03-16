"""
update_dosaros.py
=================
Orquestador de actualización de dosaros_local.db.
Descarga los JSONs necesarios y actualiza la BD.

Modos de uso:
  python update_dosaros.py              # Actualización estándar (jornada actual + equipos)
  python update_dosaros.py --full       # Descarga todo desde cero (todas las jornadas + todos los jugadores)
  python update_dosaros.py --teams      # Solo equipos
  python update_dosaros.py --players    # Solo jugadores (solo los nuevos)
  python update_dosaros.py --games      # Solo jornada actual del game-center
  python update_dosaros.py --dry-run    # Descarga JSONs pero no actualiza la BD

Cron sugerido (todos los días de partido a las 23:30):
  30 23 * * 1,2,4,5 cd /home/pi/dosaros-data-project && \
    /home/pi/dosaros-data-project/venv/bin/python src/etl/update_dosaros.py >> logs/update.log 2>&1

Cron semanal completo (cada lunes a las 06:00 para actualizar jugadores):
  0 6 * * 1 cd /home/pi/dosaros-data-project && \
    /home/pi/dosaros-data-project/venv/bin/python src/etl/update_dosaros.py --players >> logs/update.log 2>&1
"""

import sys
import json
import sqlite3
import re
import time
import argparse
import logging
import requests
from datetime import datetime
from pathlib import Path

# ── RUTAS ─────────────────────────────────────────────────────────────────────
SCRIPT_DIR  = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR / ".." / ".."
DATA_DIR    = PROJECT_DIR / "data" / "raw"
DB_PATH     = Path("/mnt/nba_data/dosaros_local.db")
LOG_DIR     = PROJECT_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

TEAMS_JSON      = DATA_DIR / "teams" / "teams.json"
TEAMS_DIR       = DATA_DIR / "teams"
PLAYERS_REF     = DATA_DIR / "players_manual.json"
PLAYERS_DIR     = DATA_DIR / "players"
GAME_CENTER_DIR = DATA_DIR / "game-center"

for d in [TEAMS_DIR, PLAYERS_DIR, GAME_CENTER_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ── LOGGING ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_DIR / "update.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ]
)
log = logging.getLogger("dosaros")

# ── CONSTANTES ────────────────────────────────────────────────────────────────
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
SEASON_CODE    = "E2025"
PHASE_CODE     = "RS"
SLEEP_STD      = 1.5
SLEEP_RATE     = 6.0


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS COMPARTIDOS
# ══════════════════════════════════════════════════════════════════════════════

def get_build_id():
    """Obtiene el buildId de Next.js — mismo método que download_teams.py."""
    url = "https://www.euroleaguebasketball.net/euroleague/"
    try:
        response = requests.get(url, headers=HEADERS)
        match = re.search(r'"buildId":"(.*?)"', response.text)
        if match:
            return match.group(1)
        log.error("buildId no encontrado en el HTML de la home.")
        return None
    except Exception as e:
        log.error(f"Error obteniendo buildId: {e}")
        return None


def fetch_json(url):
    """GET con reintentos básicos. Retorna (data_dict, status_code)."""
    for attempt in range(3):
        try:
            r = requests.get(url, headers=HEADERS)
            if r.status_code == 200:
                return r.json(), 200
            elif r.status_code == 429:
                log.warning(f"Rate limit en {url} — esperando {SLEEP_RATE}s (intento {attempt+1})")
                time.sleep(SLEEP_RATE)
            else:
                return None, r.status_code
        except Exception as e:
            log.warning(f"Request error en {url}: {e} (intento {attempt+1})")
            time.sleep(SLEEP_STD)
    return None, 0


def safe_int(v):
    if v is None or v == "":
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
    try:
        conn.execute(sql, values)
    except sqlite3.Error:
        try:
            conn.execute(
                f"INSERT OR IGNORE INTO {table} ({','.join(keys)}) VALUES ({placeholders})",
                values
            )
        except sqlite3.Error:
            pass


# ══════════════════════════════════════════════════════════════════════════════
# DESCARGA
# ══════════════════════════════════════════════════════════════════════════════

def download_teams(build_id):
    """Descarga JSONs de los 20 equipos. Siempre sobreescribe (datos volátiles)."""
    log.info("▶ Descargando equipos...")
    if not TEAMS_JSON.exists():
        log.error(f"  No se encontró {TEAMS_JSON}")
        return 0

    with open(TEAMS_JSON, encoding="utf-8") as f:
        master = json.load(f)

    clubs = master.get("headerData", {}).get("euroleague", {}).get("clubs", {}).get("clubs", [])
    ok = 0
    for club in clubs:
        url_path = club.get("url", "")
        parts    = [p for p in url_path.split("/") if p]
        if len(parts) < 5:
            continue
        slug = parts[2]
        code = parts[4]
        name = club.get("name", code)

        url = (
            f"https://www.euroleaguebasketball.net/_next/data/{build_id}"
            f"/en/euroleague/teams/{slug}/{code}.json"
        )
        data, status = fetch_json(url)
        if data:
            out = TEAMS_DIR / f"{code.lower()}.json"
            with open(out, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            ok += 1
            log.info(f"  ✅ {name}")
        else:
            log.warning(f"  ❌ {name} → HTTP {status}")
        time.sleep(SLEEP_STD)

    log.info(f"  Equipos descargados: {ok}/{len(clubs)}")
    return ok


def download_players(build_id, force=False):
    """Descarga JSONs de jugadores. Por defecto solo los que no existen."""
    log.info("▶ Descargando jugadores...")
    if not PLAYERS_REF.exists():
        log.error(f"  No se encontró {PLAYERS_REF}")
        return 0

    with open(PLAYERS_REF, encoding="utf-8") as f:
        players = json.load(f)

    ok = skipped = errors = 0
    for p in players:
        pid  = str(p.get("player_id", "")).strip()
        name = p.get("player_name", pid)
        if not pid:
            continue

        out = PLAYERS_DIR / f"{pid}.json"
        if out.exists() and not force:
            skipped += 1
            continue

        url = (
            f"https://www.euroleaguebasketball.net/_next/data/{build_id}"
            f"/en/euroleague/players/{pid}.json"
        )
        data, status = fetch_json(url)
        if data:
            with open(out, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            ok += 1
        else:
            log.warning(f"  ❌ {name} ({pid}) → HTTP {status}")
            errors += 1
        time.sleep(SLEEP_STD)

    log.info(f"  Jugadores → descargados: {ok}  omitidos: {skipped}  errores: {errors}")
    return ok


def download_game_center(build_id, download_all=False, force=False):
    """Descarga el game-center. Por defecto solo la jornada actual."""
    log.info("▶ Descargando game-center...")

    # Obtener jornada actual
    base_url = (
        f"https://www.euroleaguebasketball.net/_next/data/{build_id}"
        f"/en/euroleague/game-center.json"
    )
    data, _ = fetch_json(base_url)
    if not data:
        log.error("  ❌ No se pudo obtener el game-center base.")
        return 0

    pp            = data.get("pageProps", {})
    current_round = pp.get("currentRound")
    season_code   = pp.get("currentSeasonCode", SEASON_CODE)

    if not current_round:
        log.error("  ❌ No se encontró currentRound.")
        return 0

    rounds = range(1, current_round + 1) if download_all else [current_round]
    ok = 0

    for rnd in rounds:
        out = GAME_CENTER_DIR / f"{season_code}_round_{rnd:02d}.json"
        if out.exists() and not force and rnd != current_round:
            continue  # no re-descargar jornadas pasadas ya guardadas

        url = f"{base_url}?seasonCode={season_code}&phaseTypeCode={PHASE_CODE}&round={rnd}"
        rdata, status = fetch_json(url)

        if rdata:
            games = rdata.get("pageProps", {}).get("games", [])
            if games:
                with open(out, "w", encoding="utf-8") as f:
                    json.dump(rdata, f, indent=2, ensure_ascii=False)
                ok += 1
                log.info(f"  ✅ Jornada {rnd:02d} ({len(games)} partidos)")
            else:
                log.info(f"  ⚪ Jornada {rnd:02d} — sin partidos")
        else:
            log.warning(f"  ❌ Jornada {rnd:02d} → HTTP {status}")

        time.sleep(SLEEP_STD)

    log.info(f"  Jornadas descargadas: {ok}")
    return ok


# ══════════════════════════════════════════════════════════════════════════════
# ACTUALIZACIÓN DE BD
# ══════════════════════════════════════════════════════════════════════════════

def extract_section_values(sections, row_index):
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


def update_from_team_json(conn, data):
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

    upsert(conn, "teams", {
        "code": team_code, "name": team_name,
        "logo_url": crest_url, "is_active": 1,
    }, pk_name="code")

    upsert(conn, "euro_teams", {
        "team_code":     team_code,
        "team_name":     team_name,
        "tv_code":       safe_str(team_info.get("abbreviatedName")),
        "logo_url":      crest_url,
        "primary_color": safe_str(team_info.get("primaryColour")),
        "arena":         safe_str(bottom.get("arena")),
    }, pk_name="team_code")

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

    # Fixture del equipo → euro_games
    fixture = club.get("fixture", {})
    if isinstance(fixture, dict) and "id" in fixture:
        update_game(conn, fixture)


def update_game(conn, g):
    game_id   = safe_str(g.get("id"))
    if not game_id:
        return

    season_d = g.get("season") or {}
    phase_d  = g.get("phaseType") or {}
    round_d  = g.get("round") or {}
    home_d   = g.get("home") or {}
    away_d   = g.get("away") or {}
    venue_d  = g.get("venue") or {}

    home_code  = safe_str(home_d.get("code"))
    away_code  = safe_str(away_d.get("code"))
    game_date  = safe_str(g.get("date", ""))[:10] if g.get("date") else None

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

    v_code = safe_str(venue_d.get("code"))
    if v_code:
        address = safe_str(venue_d.get("address") or "")
        city    = address.split(",")[-1].strip() if address and "," in address else address
        upsert(conn, "venues", {
            "id": v_code, "name": safe_str(venue_d.get("name")),
            "capacity": safe_int(venue_d.get("capacity")), "city": city or None,
        })

    upsert(conn, "euro_games", {
        "game_id":    game_id,
        "date":       game_date,
        "home_team":  home_code,
        "away_team":  away_code,
        "score_home": safe_int(home_d.get("score")),
        "score_away": safe_int(away_d.get("score")),
    }, pk_name="game_id")

    hq   = home_d.get("quarters") or {}
    aq   = away_d.get("quarters") or {}
    refs = g.get("referees") or []
    rnames = [safe_str((r or {}).get("name")) for r in refs[:3]]
    while len(rnames) < 3:
        rnames.append(None)

    upsert(conn, "euro_games_extended", {
        "game_id":      game_id,
        "identifier":   safe_str(g.get("identifier")),
        "season_code":  safe_str(season_d.get("code")),
        "comp_code":    safe_str((g.get("competition") or {}).get("code")),
        "phase_code":   safe_str(phase_d.get("code")),
        "round_number": safe_int(round_d.get("round")) if isinstance(round_d, dict) else None,
        "home_coach":   safe_str((home_d.get("coach") or {}).get("name")),
        "away_coach":   safe_str((away_d.get("coach") or {}).get("name")),
        "home_q1": safe_int(hq.get("q1")), "home_q2": safe_int(hq.get("q2")),
        "home_q3": safe_int(hq.get("q3")), "home_q4": safe_int(hq.get("q4")),
        "home_ot1": safe_int(hq.get("ot1")),
        "away_q1": safe_int(aq.get("q1")), "away_q2": safe_int(aq.get("q2")),
        "away_q3": safe_int(aq.get("q3")), "away_q4": safe_int(aq.get("q4")),
        "away_ot1": safe_int(aq.get("ot1")),
        "venue_id":  v_code,
        "audience":  safe_int(g.get("audience")),
        "referee_1": rnames[0], "referee_2": rnames[1], "referee_3": rnames[2],
    }, pk_name="game_id")


def update_from_game_center(conn, data):
    pp       = data.get("pageProps", {})
    s_code   = safe_str(pp.get("currentSeasonCode"))

    for g in pp.get("games", []):
        update_game(conn, g)

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

    standings = pp.get("teamStandingsTable", {})
    if isinstance(standings, dict):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for team_code, position in standings.items():
            upsert(conn, "euro_standings", {
                "team_code":    team_code,
                "rank":         safe_int(position),
                "last_updated": now,
            }, pk_name="team_code")


def update_from_player_json(conn, data):
    p_data = data.get("pageProps", {}).get("data", {})
    hero   = p_data.get("hero", {})
    if not hero:
        return

    player_id = safe_str(str(hero.get("id", "")))
    if not player_id:
        return

    team_code = safe_str(hero.get("clubCode"))
    full_name = f"{hero.get('firstName', '')} {hero.get('lastName', '')}".strip()

    if team_code:
        upsert(conn, "teams", {
            "code": team_code, "name": safe_str(hero.get("clubName")),
            "logo_url": safe_str(hero.get("clubCrest")), "is_active": 1,
        }, pk_name="code")

    upsert(conn, "players", {
        "id": player_id, "name": full_name,
        "position":    safe_str(hero.get("position")),
        "height":      str(hero.get("height")) if hero.get("height") else None,
        "nationality": safe_str(hero.get("nationality")),
        "image_url":   safe_str(hero.get("photo")),
        "current_team_code": team_code,
    })

    upsert(conn, "euro_players", {
        "player_id":   player_id, "player_name": full_name,
        "position":    safe_str(hero.get("position")),
        "height":      safe_int(hero.get("height")),
        "club_name":   safe_str(hero.get("clubName")),
        "nationality": safe_str(hero.get("nationality")),
        "image_url":   safe_str(hero.get("photo")),
    }, pk_name="player_id")

    # Stats por temporada
    alltime     = p_data.get("stats", {}).get("alltime", {})
    for st_block in alltime.get("statTables", []):
        competition = safe_str(st_block.get("comp", "Euroleague"))
        is_euro     = 1 if competition and "euroleague" in competition.lower() else 0
        tables      = st_block.get("tables", {})
        if not tables:
            continue

        head_stats = tables.get("headSection", {}).get("stats", [])
        sections   = tables.get("sections", [])
        data_rows  = max(0, len(head_stats) - 2)

        for row_idx in range(data_rows):
            stat_sets = head_stats[row_idx].get("statSets", [])
            if len(stat_sets) < 2:
                continue
            s_code = safe_str(stat_sets[0].get("seasonCode") or stat_sets[0].get("value"))
            t_code = safe_str(stat_sets[1].get("value"))
            if not s_code or not t_code:
                continue

            vals = extract_section_values(sections, row_idx)
            g    = safe_int(vals.get("G"))
            pts  = safe_int(vals.get("TimeAndPoints_Pts") or vals.get("Pts"))
            reb  = safe_int(vals.get("T"))
            ast  = safe_int(vals.get("As"))
            pir  = safe_int(vals.get("PIR"))

            upsert(conn, "player_season_stats", {
                "id":             f"{player_id}_{s_code}_{t_code}",
                "player_id":      player_id, "season_code": s_code,
                "team_code":      t_code, "competition": competition,
                "total_games":    g, "total_points": pts,
                "total_rebounds": reb, "total_assists": ast, "total_pir": pir,
            })

            row_team  = conn.execute("SELECT name FROM teams WHERE code=?", [t_code]).fetchone()
            team_name = row_team[0] if row_team else t_code
            try:
                conn.execute("""
                    INSERT INTO euro_stats_career
                        (player_id, season_code, team_name, games_played, pts, reb, ast, pir, is_euroleague)
                    VALUES (?,?,?,?,?,?,?,?,?)
                    ON CONFLICT(player_id, season_code, team_name) DO UPDATE SET
                        games_played=excluded.games_played, pts=excluded.pts,
                        reb=excluded.reb, ast=excluded.ast, pir=excluded.pir,
                        is_euroleague=excluded.is_euroleague
                """, [player_id, s_code, team_name, g, pts, reb, ast, pir, is_euro])
            except sqlite3.Error:
                pass


def update_db(do_teams=True, do_players=True, do_games=True):
    log.info("▶ Actualizando base de datos...")
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=OFF")

    n_teams = n_players = n_games = 0

    if do_teams:
        for f in sorted(TEAMS_DIR.glob("*.json")):
            if f.name == "teams.json":
                continue
            try:
                with open(f, encoding="utf-8") as fh:
                    data = json.load(fh)
                update_from_team_json(conn, data)
                n_teams += 1
            except Exception as e:
                log.warning(f"  Error en {f.name}: {e}")
        conn.commit()
        log.info(f"  Equipos actualizados: {n_teams}")

    if do_games:
        for f in sorted(GAME_CENTER_DIR.glob("*.json")):
            try:
                with open(f, encoding="utf-8") as fh:
                    data = json.load(fh)
                update_from_game_center(conn, data)
                n_games += 1
            except Exception as e:
                log.warning(f"  Error en {f.name}: {e}")
        conn.commit()
        log.info(f"  Jornadas actualizadas: {n_games}")

    if do_players:
        for f in sorted(PLAYERS_DIR.glob("*.json")):
            try:
                with open(f, encoding="utf-8") as fh:
                    data = json.load(fh)
                update_from_player_json(conn, data)
                n_players += 1
            except Exception as e:
                log.warning(f"  Error en {f.name}: {e}")
            if n_players % 50 == 0:
                conn.commit()
        conn.commit()
        log.info(f"  Jugadores actualizados: {n_players}")

    conn.execute("PRAGMA foreign_keys=ON")
    conn.close()


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Actualiza dosaros_local.db con datos de EuroLeague")
    parser.add_argument("--full",     action="store_true", help="Descarga completa (todas las jornadas + todos los jugadores)")
    parser.add_argument("--teams",    action="store_true", help="Solo actualiza equipos")
    parser.add_argument("--players",  action="store_true", help="Solo actualiza jugadores (nuevos)")
    parser.add_argument("--games",    action="store_true", help="Solo actualiza jornada actual")
    parser.add_argument("--dry-run",  action="store_true", help="Solo descarga JSONs, no actualiza BD")
    parser.add_argument("--force",    action="store_true", help="Re-descarga aunque los ficheros existan")
    args = parser.parse_args()

    # Si no se especifica nada, modo estándar (equipos + jornada actual)
    mode_default = not any([args.full, args.teams, args.players, args.games])
    do_teams   = args.full or args.teams  or mode_default
    do_players = args.full or args.players
    do_games   = args.full or args.games  or mode_default

    start = datetime.now()
    log.info("=" * 60)
    log.info(f"INICIO actualización — {start.strftime('%Y-%m-%d %H:%M:%S')}")
    log.info(f"Modo: {'FULL' if args.full else 'ESTÁNDAR' if mode_default else 'PARCIAL'}")
    log.info("=" * 60)

    build_id = get_build_id()
    if not build_id:
        log.error("❌ No se pudo obtener el buildId. Abortando.")
        sys.exit(1)
    log.info(f"BuildId: {build_id}")

    # ── Descarga ──
    if do_teams:
        download_teams(build_id)

    if do_players:
        download_players(build_id, force=args.force)

    if do_games:
        download_game_center(build_id, download_all=args.full, force=args.force)

    # ── Actualización BD ──
    if not args.dry_run:
        update_db(do_teams=do_teams, do_players=do_players, do_games=do_games)
    else:
        log.info("▶ --dry-run: BD no modificada.")

    elapsed = (datetime.now() - start).seconds
    log.info(f"✅ Actualización completada en {elapsed}s")
    log.info("=" * 60)


if __name__ == "__main__":
    main()
