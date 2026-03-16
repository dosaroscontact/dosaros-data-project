"""
update_dosaros.py
=================
Actualiza dosaros_local.db usando la API oficial de EuroLeague.
Sin buildId, sin scraping, sin bloqueos.

Uso:
  python update_dosaros.py              # jornada actual + standings
  python update_dosaros.py --full       # todas las jornadas de la temporada
  python update_dosaros.py --standings  # solo clasificación
  python update_dosaros.py --round 31   # jornada concreta

Cron sugerido:
  # Días de partido (L,M,J,V) a las 23:30
  30 23 * * 1,2,4,5 cd /home/pi/dosaros-data-project && venv/bin/python src/etl/update_dosaros.py >> logs/update.log 2>&1

  # Lunes a las 06:00 para actualizar standings semanales
  0 6 * * 1 cd /home/pi/dosaros-data-project && venv/bin/python src/etl/update_dosaros.py --standings >> logs/update.log 2>&1
"""

import sys
import sqlite3
import argparse
import logging
from datetime import datetime
from pathlib import Path

from euroleague_api.game_stats import GameStats
from euroleague_api.standings import Standings

# ── CONFIGURACIÓN ─────────────────────────────────────────────────────────────
SCRIPT_DIR  = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR / ".." / ".."
DB_PATH     = Path("/mnt/nba_data/dosaros_local.db")
LOG_DIR     = PROJECT_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

COMP        = "E"       # Euroleague
SEASON      = 2025      # E2025 → año 2025
# ─────────────────────────────────────────────────────────────────────────────

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


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def safe_int(v):
    if v is None:
        return None
    try:
        return int(float(str(v)))
    except Exception:
        return None


def safe_float(v):
    if v is None:
        return None
    try:
        return float(str(v).replace("%", ""))
    except Exception:
        return None


def safe_str(v):
    if v is None:
        return None
    s = str(v).strip()
    return s if s and s.lower() not in ("none", "nan", "") else None


def upsert(conn, table, data, pk):
    keys         = list(data.keys())
    values       = list(data.values())
    placeholders = ",".join(["?"] * len(keys))
    set_clause   = ",".join([f"{k}=excluded.{k}" for k in keys if k != pk])
    sql = (
        f"INSERT INTO {table} ({','.join(keys)}) VALUES ({placeholders})"
        f" ON CONFLICT({pk}) DO UPDATE SET {set_clause}"
    )
    try:
        conn.execute(sql, values)
    except sqlite3.Error as e:
        log.debug(f"  upsert error en {table}: {e}")
        try:
            conn.execute(
                f"INSERT OR IGNORE INTO {table} ({','.join(keys)}) VALUES ({placeholders})",
                values
            )
        except sqlite3.Error:
            pass


def get_current_round(gs: GameStats) -> int:
    """Obtiene la jornada más reciente con partidos jugados."""
    try:
        df = gs.get_gamecodes_season(SEASON)
        # La última jornada con partidos jugados
        if "Round" in df.columns:
            return int(df["Round"].max())
        elif "round" in df.columns:
            return int(df["round"].max())
    except Exception as e:
        log.warning(f"  No se pudo obtener la jornada actual: {e}")
    return 31  # fallback


# ══════════════════════════════════════════════════════════════════════════════
# ACTUALIZAR PARTIDOS Y STATS DE UNA JORNADA
# ══════════════════════════════════════════════════════════════════════════════

def update_round(conn, gs: GameStats, round_number: int):
    """
    Actualiza euro_games, euro_games_extended, venues y players_games
    para todos los partidos de una jornada usando get_gamecodes_round
    que ya incluye marcadores, cuartos, venue y árbitros.
    Para las stats por jugador usa get_game_stats partido a partido.
    """
    log.info(f"  Procesando jornada {round_number}...")

    try:
        games_df = gs.get_gamecodes_round(SEASON, round_number)
        if games_df.empty:
            log.info(f"  Jornada {round_number} — sin partidos")
            return 0
        log.info(f"  {len(games_df)} partidos en jornada {round_number}")
    except Exception as e:
        log.warning(f"  Error obteniendo jornada {round_number}: {e}")
        return 0

    season_code = f"E{SEASON}"
    games_ok    = 0

    for _, row in games_df.iterrows():
        try:
            game_code   = int(row["gameCode"])
            game_id     = safe_str(row.get("identifier")) or f"E{SEASON}_{game_code}"
            home_code   = safe_str(row.get("local.club.code"))
            away_code   = safe_str(row.get("road.club.code"))
            home_score  = safe_int(row.get("local.score"))
            away_score  = safe_int(row.get("road.score"))
            game_date   = safe_str(row.get("date", ""))[:10] if row.get("date") else None
            played      = bool(row.get("played", False))

            # Equipos
            for code, name, tv, logo in [
                (home_code, row.get("local.club.name"), row.get("local.club.tvCode"), row.get("local.club.images.crest")),
                (away_code, row.get("road.club.name"),  row.get("road.club.tvCode"),  row.get("road.club.images.crest")),
            ]:
                if code:
                    upsert(conn, "teams",      {"code": code, "name": safe_str(name), "logo_url": safe_str(logo), "is_active": 1}, pk="code")
                    upsert(conn, "euro_teams", {"team_code": code, "team_name": safe_str(name), "tv_code": safe_str(tv), "logo_url": safe_str(logo)}, pk="team_code")

            # Venue
            v_code = safe_str(row.get("venue.code"))
            if v_code:
                addr = safe_str(row.get("venue.address") or "")
                city = addr.split(",")[-1].strip() if addr and "," in addr else addr
                upsert(conn, "venues", {
                    "id": v_code, "name": safe_str(row.get("venue.name")),
                    "capacity": safe_int(row.get("venue.capacity")), "city": city or None,
                })

            # euro_games
            upsert(conn, "euro_games", {
                "game_id":    game_id,
                "date":       game_date,
                "home_team":  home_code,
                "away_team":  away_code,
                "score_home": home_score if played else None,
                "score_away": away_score if played else None,
            }, pk="game_id")

            # euro_games_extended — cuartos y árbitros incluidos
            try:
                upsert(conn, "euro_games_extended", {
                    "game_id":      game_id,
                    "identifier":   game_id,
                    "season_code":  season_code,
                    "comp_code":    COMP,
                    "round_number": round_number,
                    "home_coach":   None,
                    "away_coach":   None,
                    "home_q1":  safe_int(row.get("local.partials.partials1")),
                    "home_q2":  safe_int(row.get("local.partials.partials2")),
                    "home_q3":  safe_int(row.get("local.partials.partials3")),
                    "home_q4":  safe_int(row.get("local.partials.partials4")),
                    "home_ot1": None,
                    "away_q1":  safe_int(row.get("road.partials.partials1")),
                    "away_q2":  safe_int(row.get("road.partials.partials2")),
                    "away_q3":  safe_int(row.get("road.partials.partials3")),
                    "away_q4":  safe_int(row.get("road.partials.partials4")),
                    "away_ot1": None,
                    "venue_id":   v_code,
                    "audience":   safe_int(row.get("audience")),
                    "referee_1":  safe_str(row.get("referee1.name")),
                    "referee_2":  safe_str(row.get("referee2.name")),
                    "referee_3":  safe_str(row.get("referee3.name")),
                }, pk="game_id")
            except Exception:
                pass

            # Stats por jugador — solo si el partido está jugado
            players_updated = 0
            if played:
                try:
                    stats_df = gs.get_game_stats(SEASON, game_code)
                    if not stats_df.empty:
                        stats_row     = stats_df.iloc[0]
                        local_players = stats_row.get("local.players", [])
                        road_players  = stats_row.get("road.players", [])

                        for team_code, players_list in [(home_code, local_players), (away_code, road_players)]:
                            for entry in (players_list or []):
                                if not isinstance(entry, dict):
                                    continue
                                person      = entry.get("player", {}).get("person", {})
                                stats       = entry.get("stats", {})
                                player_code = safe_str(person.get("code"))
                                if not player_code:
                                    continue

                                upsert(conn, "euro_players", {
                                    "player_id":   player_code,
                                    "player_name": safe_str(person.get("name")),
                                    "position":    safe_str(entry.get("player", {}).get("positionName")),
                                    "height":      safe_int(person.get("height")),
                                    "club_name":   safe_str(team_code),
                                    "nationality": safe_str((person.get("country") or {}).get("name")),
                                    "image_url":   safe_str((entry.get("player", {}).get("images") or {}).get("headshot")),
                                }, pk="player_id")

                                upsert(conn, "players", {
                                    "id":                player_code,
                                    "name":              safe_str(person.get("name")),
                                    "position":          safe_str(entry.get("player", {}).get("positionName")),
                                    "height":            safe_str(person.get("height")),
                                    "nationality":       safe_str((person.get("country") or {}).get("name")),
                                    "image_url":         safe_str((entry.get("player", {}).get("images") or {}).get("headshot")),
                                    "current_team_code": team_code,
                                }, pk="id")

                                upsert(conn, "euro_players_games", {
                                    "game_id":   game_id,
                                    "player_id": player_code,
                                    "team_id":   team_code,
                                    "pts":       safe_int(stats.get("points")),
                                    "reb":       safe_int(stats.get("totalRebounds")),
                                    "ast":       safe_int(stats.get("assistances")),
                                }, pk="game_id")

                                players_updated += 1
                except Exception as e2:
                    log.debug(f"    Stats jugadores {game_id}: {e2}")

            games_ok += 1
            status = f"{home_score}-{away_score}" if played else "pendiente"
            log.info(f"    ✅ {game_id}  {home_code} {status} {away_code}  jugadores: {players_updated}")

        except Exception as e:
            log.warning(f"    ❌ Error en fila {row.get('identifier','?')}: {e}")

    return games_ok


# ══════════════════════════════════════════════════════════════════════════════
# ACTUALIZAR CLASIFICACIÓN
# ══════════════════════════════════════════════════════════════════════════════

def update_standings(conn, round_number: int):
    log.info(f"  Actualizando clasificación (jornada {round_number})...")
    try:
        st  = Standings(COMP)
        df  = st.get_standings(SEASON, round_number)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for _, row in df.iterrows():
            team_code = safe_str(row.get("club.code"))
            if not team_code:
                continue

            # euro_standings
            upsert(conn, "euro_standings", {
                "team_code":    team_code,
                "rank":         safe_int(row.get("position")),
                "wins":         safe_int(row.get("gamesWon")),
                "losses":       safe_int(row.get("gamesLost")),
                "points_diff":  safe_int(str(row.get("pointsDifference", "0")).replace("+", "")),
                "last_updated": now,
            }, pk="team_code")

            # euro_teams
            upsert(conn, "euro_teams", {
                "team_code": team_code,
                "team_name": safe_str(row.get("club.name")),
                "tv_code":   safe_str(row.get("club.tvCode")),
                "logo_url":  safe_str(row.get("club.images.crest")),
            }, pk="team_code")

            # teams
            upsert(conn, "teams", {
                "code":      team_code,
                "name":      safe_str(row.get("club.name")),
                "logo_url":  safe_str(row.get("club.images.crest")),
                "is_active": 1,
            }, pk="code")

        conn.commit()
        log.info(f"  ✅ Clasificación actualizada — {len(df)} equipos")
        return len(df)

    except Exception as e:
        log.error(f"  ❌ Error actualizando clasificación: {e}")
        return 0


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Actualiza dosaros_local.db con la API de EuroLeague")
    parser.add_argument("--full",      action="store_true", help="Actualiza todas las jornadas de la temporada")
    parser.add_argument("--standings", action="store_true", help="Solo actualiza clasificación")
    parser.add_argument("--round",     type=int,            help="Actualiza una jornada concreta (ej: --round 31)")
    args = parser.parse_args()

    start = datetime.now()
    log.info("=" * 60)
    log.info(f"INICIO — {start.strftime('%Y-%m-%d %H:%M:%S')}")
    if args.full:
        log.info("Modo: FULL (todas las jornadas)")
    elif args.standings:
        log.info("Modo: STANDINGS")
    elif args.round:
        log.info(f"Modo: JORNADA {args.round}")
    else:
        log.info("Modo: ESTÁNDAR (jornada actual + standings)")
    log.info("=" * 60)

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=OFF")

    gs = GameStats(COMP)
    current_round = get_current_round(gs)
    log.info(f"Jornada más reciente: {current_round}")

    total_games = 0

    if args.standings:
        update_standings(conn, current_round)

    elif args.round:
        update_standings(conn, args.round)
        total_games = update_round(conn, gs, args.round)
        conn.commit()

    elif args.full:
        # Todas las jornadas desde 1 hasta la actual
        log.info(f"Actualizando jornadas 1 a {current_round}...")
        for rnd in range(1, current_round + 1):
            n = update_round(conn, gs, rnd)
            total_games += n
            conn.commit()
        update_standings(conn, current_round)

    else:
        # Modo estándar: jornada actual + standings
        update_standings(conn, current_round)
        total_games = update_round(conn, gs, current_round)
        conn.commit()

    conn.execute("PRAGMA foreign_keys=ON")

    # Resumen de la BD
    log.info("\n--- RESUMEN BD ---")
    for t in ["euro_games", "euro_players_games", "euro_players", "euro_standings", "euro_teams"]:
        try:
            n = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
            log.info(f"  {t:<25} {n:>8,} registros")
        except Exception:
            pass

    conn.close()

    elapsed = (datetime.now() - start).seconds
    log.info(f"\n✅ Completado en {elapsed}s — {total_games} partidos procesados")
    log.info("=" * 60)


if __name__ == "__main__":
    main()
