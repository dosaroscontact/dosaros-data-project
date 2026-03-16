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
    Actualiza euro_games, euro_players_games y euro_players
    para todos los partidos de una jornada.
    """
    log.info(f"  Procesando jornada {round_number}...")

    try:
        # Obtener game_codes de la jornada
        gamecodes_df = gs.get_gamecodes_round(SEASON, round_number)
        if gamecodes_df.empty:
            log.info(f"  Jornada {round_number} — sin partidos")
            return 0

        game_codes = gamecodes_df["Gamecode"].tolist() if "Gamecode" in gamecodes_df.columns else []
        if not game_codes:
            log.warning(f"  No se encontraron game codes para jornada {round_number}")
            return 0

        log.info(f"  {len(game_codes)} partidos en jornada {round_number}")

    except Exception as e:
        log.warning(f"  Error obteniendo game codes jornada {round_number}: {e}")
        return 0

    games_ok = 0
    for game_code in game_codes:
        try:
            df = gs.get_game_stats(SEASON, int(game_code))
            if df.empty:
                continue

            row = df.iloc[0]

            # IDs
            game_id     = f"E{SEASON}_{int(game_code)}"
            season_code = f"E{SEASON}"

            # Equipos local y visitante
            home_code = safe_str(row.get("local.team.code") or row.get("local.coach.code", "")[:3])
            away_code = safe_str(row.get("road.team.code")  or row.get("road.coach.code", "")[:3])

            # Buscar códigos de equipo dentro de los players si no están directamente
            local_players = row.get("local.players", [])
            road_players  = row.get("road.players", [])

            if local_players and isinstance(local_players, list) and local_players:
                home_code = safe_str(local_players[0].get("player", {}).get("club", {}).get("code"))
            if road_players and isinstance(road_players, list) and road_players:
                away_code = safe_str(road_players[0].get("player", {}).get("club", {}).get("code"))

            home_score = safe_int(row.get("local.team.points"))
            away_score = safe_int(row.get("road.team.points"))

            # euro_games
            upsert(conn, "euro_games", {
                "game_id":    game_id,
                "date":       None,
                "home_team":  home_code,
                "away_team":  away_code,
                "score_home": home_score,
                "score_away": away_score,
            }, pk="game_id")

            # euro_games_extended (si existe la tabla)
            try:
                upsert(conn, "euro_games_extended", {
                    "game_id":      game_id,
                    "identifier":   f"E{SEASON}_{int(game_code)}",
                    "season_code":  season_code,
                    "comp_code":    COMP,
                    "round_number": round_number,
                    "home_coach":   safe_str(row.get("local.coach.name")),
                    "away_coach":   safe_str(row.get("road.coach.name")),
                    "home_q1": None, "home_q2": None, "home_q3": None, "home_q4": None, "home_ot1": None,
                    "away_q1": None, "away_q2": None, "away_q3": None, "away_q4": None, "away_ot1": None,
                    "venue_id": None, "audience": None,
                    "referee_1": None, "referee_2": None, "referee_3": None,
                }, pk="game_id")
            except Exception:
                pass

            # Stats de jugadores del partido
            players_updated = 0
            for side, players_list in [("home", local_players), ("away", road_players)]:
                team_code = home_code if side == "home" else away_code
                for entry in (players_list or []):
                    if not isinstance(entry, dict):
                        continue
                    person = entry.get("player", {}).get("person", {})
                    stats  = entry.get("stats", {})
                    player_code = safe_str(person.get("code"))
                    if not player_code:
                        continue

                    # euro_players
                    upsert(conn, "euro_players", {
                        "player_id":   player_code,
                        "player_name": safe_str(person.get("name")),
                        "position":    safe_str(entry.get("player", {}).get("positionName")),
                        "height":      safe_int(person.get("height")),
                        "club_name":   safe_str(entry.get("player", {}).get("club", {}).get("name")),
                        "nationality": safe_str((person.get("country") or {}).get("name")),
                        "image_url":   safe_str((entry.get("player", {}).get("images") or {}).get("headshot")),
                    }, pk="player_id")

                    # players
                    upsert(conn, "players", {
                        "id":                player_code,
                        "name":              safe_str(person.get("name")),
                        "position":          safe_str(entry.get("player", {}).get("positionName")),
                        "height":            safe_str(person.get("height")),
                        "nationality":       safe_str((person.get("country") or {}).get("name")),
                        "image_url":         safe_str((entry.get("player", {}).get("images") or {}).get("headshot")),
                        "current_team_code": team_code,
                    }, pk="id")

                    # euro_players_games
                    upsert(conn, "euro_players_games", {
                        "game_id":   game_id,
                        "player_id": player_code,
                        "team_id":   team_code,
                        "pts":       safe_int(stats.get("points")),
                        "reb":       safe_int(stats.get("totalRebounds")),
                        "ast":       safe_int(stats.get("assistances")),
                    }, pk="game_id")

                    players_updated += 1

            games_ok += 1
            log.info(f"    ✅ Partido {game_id} ({home_code} {home_score}-{away_score} {away_code}) — {players_updated} jugadores")

        except Exception as e:
            log.warning(f"    ❌ Error en game_code {game_code}: {e}")

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
