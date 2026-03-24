"""
================================================================================
GENERADOR DE PERLAS - Proyecto Dos Aros
================================================================================
Detecta actuaciones destacadas ("perlas") de NBA y Euroliga:

NBA:
  - Triple-dobles (10+ en PTS, REB y AST)
  - 40+ puntos en un partido
  - +/- extremo (+25 o mejor, -25 o peor)
  - Remontadas (diferencia de cuartos vs resultado final)
  - Récords de temporada o históricos
  - Explosión anotadora 50+, dominio reboteador 20+, asistidor élite 15+
  - Partido perfecto (FG 100% con 10+ intentos)
  - Récord personal en pts/reb/ast
  - Partido histórico combinado (pts+reb+ast >= 60)
  - Defensa élite (5+ robos o 5+ tapones)
  - Equipo imparable (150+ puntos)
  - Remontada épica (diferencia 20+ superada)

Euroliga:
  - Mejores actuaciones individuales (pts, reb, ast)
  - Partidos con remontada (usando parciales de euro_games_extended)
  - Próximos partidos si no hubo acción ayer
  - Explosión anotadora 30+, dominio reboteador 15+, asistidor élite 10+
  - Récord personal en pts/reb/ast
  - Partido histórico combinado (pts+reb+ast >= 40)
  - Equipo imparable (100+ puntos)
  - Remontada épica (diferencia 15+ superada)

Diseño multiidioma: preparado para ES/EN/CAT en futuras versiones.
================================================================================
"""

import sqlite3
import pandas as pd
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("LOCAL_DB", "/mnt/nba_data/dosaros_local.db")

# Idioma activo (preparado para futuras versiones)
IDIOMA = "es"

TEXTOS = {
    "es": {
        "triple_doble": "Triple-doble",
        "puntos_record": "Explosión anotadora",
        "plus_minus": "Dominio total",
        "remontada_nba": "Remontada NBA",
        "remontada_euro": "Remontada Euroliga",
        "record_temp": "Récord de temporada",
        "record_hist": "Récord histórico",
        "perla_euro": "Actuación destacada Euroliga",
        "proximos_euro": "Próximos partidos Euroliga",
        # Nuevas categorías
        "explosion_50": "Explosión anotadora 50+",
        "dominio_reboteador": "Dominio reboteador",
        "asistidor_elite": "Asistidor élite",
        "partido_perfecto": "Partido perfecto",
        "record_personal": "Récord personal",
        "historico_combinado": "Partido histórico combinado",
        "defensa_elite": "Defensa élite",
        "equipo_imparable": "Equipo imparable",
        "remontada_epica": "Remontada épica",
    }
}


def get_connection():
    return sqlite3.connect(DB_PATH)


# ============================================================================
# PERLAS NBA — CATEGORÍAS ORIGINALES
# ============================================================================

def detectar_triple_dobles_nba(fecha):
    """Detecta triple-dobles en NBA."""
    try:
        conn = get_connection()
        query = """
            SELECT PLAYER_NAME, TEAM_ABBREVIATION, PTS, REB, AST, MATCHUP
            FROM nba_players_games
            WHERE GAME_DATE = ?
              AND PTS >= 10 AND REB >= 10 AND AST >= 10
            ORDER BY PTS DESC
        """
        df = pd.read_sql_query(query, conn, params=[fecha])
        conn.close()

        perlas = []
        for _, r in df.iterrows():
            perlas.append({
                "tipo": TEXTOS[IDIOMA]["triple_doble"],
                "liga": "NBA",
                "jugador": r["PLAYER_NAME"],
                "equipo": r["TEAM_ABBREVIATION"],
                "detalle": f"{int(r['PTS'])} pts / {int(r['REB'])} reb / {int(r['AST'])} ast",
                "partido": r["MATCHUP"],
                "peso": 10
            })
        return perlas
    except Exception as e:
        print(f"⚠️ Error triple-dobles NBA: {e}")
        return []


def detectar_explosion_anotadora_nba(fecha, umbral=40):
    """Detecta jugadores con 40+ puntos."""
    try:
        conn = get_connection()
        query = """
            SELECT PLAYER_NAME, TEAM_ABBREVIATION, PTS, FGM, FGA, FG3M, MATCHUP
            FROM nba_players_games
            WHERE GAME_DATE = ? AND PTS >= ?
            ORDER BY PTS DESC
        """
        df = pd.read_sql_query(query, conn, params=[fecha, umbral])
        conn.close()

        perlas = []
        for _, r in df.iterrows():
            perlas.append({
                "tipo": TEXTOS[IDIOMA]["puntos_record"],
                "liga": "NBA",
                "jugador": r["PLAYER_NAME"],
                "equipo": r["TEAM_ABBREVIATION"],
                "detalle": f"{int(r['PTS'])} pts ({int(r['FGM'])}/{int(r['FGA'])} en campo, {int(r['FG3M'])} triples)",
                "partido": r["MATCHUP"],
                "peso": 9
            })
        return perlas
    except Exception as e:
        print(f"⚠️ Error explosión anotadora NBA: {e}")
        return []


def detectar_plus_minus_extremo_nba(fecha, umbral=25):
    """Detecta +/- extremos (dominio total o desastre individual)."""
    try:
        conn = get_connection()
        query = """
            SELECT PLAYER_NAME, TEAM_ABBREVIATION,
                   CAST(PLUS_MINUS AS INTEGER) as PLUS_MINUS, PTS, MIN, MATCHUP
            FROM nba_players_games
            WHERE GAME_DATE = ? AND (CAST(PLUS_MINUS AS INTEGER) >= ? OR CAST(PLUS_MINUS AS INTEGER) <= -?)
            ORDER BY ABS(CAST(PLUS_MINUS AS INTEGER)) DESC
            LIMIT 3
        """
        df = pd.read_sql_query(query, conn, params=[fecha, umbral, umbral])
        conn.close()

        perlas = []
        for _, r in df.iterrows():
            signo = "+" if r["PLUS_MINUS"] > 0 else ""
            perlas.append({
                "tipo": TEXTOS[IDIOMA]["plus_minus"],
                "liga": "NBA",
                "jugador": r["PLAYER_NAME"],
                "equipo": r["TEAM_ABBREVIATION"],
                "detalle": f"{signo}{int(r['PLUS_MINUS'])} de +/- en {r['MIN']} minutos ({int(r['PTS'])} pts)",
                "partido": r["MATCHUP"],
                "peso": 7
            })
        return perlas
    except Exception as e:
        print(f"⚠️ Error +/- extremo NBA: {e}")
        return []


def detectar_remontadas_nba(fecha, diferencia_min=15):
    """
    Detecta remontadas NBA comparando marcador final.
    Sin datos de parciales usamos diferencia final como proxy.
    """
    try:
        conn = get_connection()
        query = """
            SELECT home_team, away_team, home_score, away_score, winner
            FROM nba_daily_results
            WHERE game_date = ?
              AND ABS(home_score - away_score) >= ?
        """
        df = pd.read_sql_query(query, conn, params=[fecha, diferencia_min])
        conn.close()

        perlas = []
        for _, r in df.iterrows():
            diff = abs(int(r["home_score"]) - int(r["away_score"]))
            ganador = r["winner"]
            perlas.append({
                "tipo": TEXTOS[IDIOMA]["remontada_nba"],
                "liga": "NBA",
                "jugador": None,
                "equipo": ganador,
                "detalle": f"{r['home_team']} {int(r['home_score'])} - {int(r['away_score'])} {r['away_team']} (diferencia: {diff} pts)",
                "partido": f"{r['home_team']} vs {r['away_team']}",
                "peso": 6
            })
        return perlas
    except Exception as e:
        print(f"⚠️ Error remontadas NBA: {e}")
        return []


def detectar_records_nba(fecha):
    """
    Detecta si alguna actuación de ayer es récord de temporada o histórica.
    Compara con el máximo histórico de la DB.
    """
    perlas = []
    try:
        conn = get_connection()

        # Récord de puntos en un partido (histórico en DB)
        query_record_pts = """
            SELECT
                hoy.PLAYER_NAME, hoy.TEAM_ABBREVIATION, hoy.PTS, hoy.MATCHUP,
                hist.max_pts
            FROM nba_players_games hoy
            JOIN (
                SELECT PLAYER_NAME, MAX(PTS) as max_pts
                FROM nba_players_games
                GROUP BY PLAYER_NAME
            ) hist ON hoy.PLAYER_NAME = hist.PLAYER_NAME
            WHERE hoy.GAME_DATE = ?
              AND hoy.PTS >= hist.max_pts
              AND hoy.PTS >= 35
        """
        df_pts = pd.read_sql_query(query_record_pts, conn, params=[fecha])
        for _, r in df_pts.iterrows():
            perlas.append({
                "tipo": TEXTOS[IDIOMA]["record_hist"],
                "liga": "NBA",
                "jugador": r["PLAYER_NAME"],
                "equipo": r["TEAM_ABBREVIATION"],
                "detalle": f"Récord personal con {int(r['PTS'])} puntos (máximo en DB)",
                "partido": r["MATCHUP"],
                "peso": 10
            })

        # Récord de triples en un partido
        query_record_3p = """
            SELECT
                hoy.PLAYER_NAME, hoy.TEAM_ABBREVIATION, hoy.FG3M, hoy.MATCHUP,
                hist.max_3pm
            FROM nba_players_games hoy
            JOIN (
                SELECT PLAYER_NAME, MAX(FG3M) as max_3pm
                FROM nba_players_games
                GROUP BY PLAYER_NAME
            ) hist ON hoy.PLAYER_NAME = hist.PLAYER_NAME
            WHERE hoy.GAME_DATE = ?
              AND hoy.FG3M >= hist.max_3pm
              AND hoy.FG3M >= 7
        """
        df_3p = pd.read_sql_query(query_record_3p, conn, params=[fecha])
        for _, r in df_3p.iterrows():
            perlas.append({
                "tipo": TEXTOS[IDIOMA]["record_hist"],
                "liga": "NBA",
                "jugador": r["PLAYER_NAME"],
                "equipo": r["TEAM_ABBREVIATION"],
                "detalle": f"Récord personal con {int(r['FG3M'])} triples anotados",
                "partido": r["MATCHUP"],
                "peso": 9
            })

        conn.close()
    except Exception as e:
        print(f"⚠️ Error récords NBA: {e}")

    return perlas


# ============================================================================
# PERLAS NBA — NUEVAS CATEGORÍAS
# ============================================================================

def detectar_explosion_50_nba(fecha):
    """Detecta jugadores con 50+ puntos (actuación histórica)."""
    try:
        conn = get_connection()
        query = """
            SELECT PLAYER_NAME, TEAM_ABBREVIATION, PTS, FGM, FGA, FG3M, MATCHUP
            FROM nba_players_games
            WHERE GAME_DATE = ? AND PTS >= 50
            ORDER BY PTS DESC
        """
        df = pd.read_sql_query(query, conn, params=[fecha])
        conn.close()

        perlas = []
        for _, r in df.iterrows():
            perlas.append({
                "tipo": TEXTOS[IDIOMA]["explosion_50"],
                "liga": "NBA",
                "jugador": r["PLAYER_NAME"],
                "equipo": r["TEAM_ABBREVIATION"],
                "detalle": f"{int(r['PTS'])} pts ({int(r['FGM'])}/{int(r['FGA'])} en campo, {int(r['FG3M'])} triples)",
                "partido": r["MATCHUP"],
                "peso": 12
            })
        return perlas
    except Exception as e:
        print(f"⚠️ Error explosión 50+ NBA: {e}")
        return []


def detectar_dominio_reboteador_nba(fecha, umbral=20):
    """Detecta jugadores con 20+ rebotes en un partido."""
    try:
        conn = get_connection()
        query = """
            SELECT PLAYER_NAME, TEAM_ABBREVIATION, REB, OREB, DREB, PTS, MATCHUP
            FROM nba_players_games
            WHERE GAME_DATE = ? AND REB >= ?
            ORDER BY REB DESC
        """
        df = pd.read_sql_query(query, conn, params=[fecha, umbral])
        conn.close()

        perlas = []
        for _, r in df.iterrows():
            perlas.append({
                "tipo": TEXTOS[IDIOMA]["dominio_reboteador"],
                "liga": "NBA",
                "jugador": r["PLAYER_NAME"],
                "equipo": r["TEAM_ABBREVIATION"],
                "detalle": f"{int(r['REB'])} reb ({int(r['OREB'])} of / {int(r['DREB'])} def) — {int(r['PTS'])} pts",
                "partido": r["MATCHUP"],
                "peso": 10
            })
        return perlas
    except Exception as e:
        print(f"⚠️ Error dominio reboteador NBA: {e}")
        return []


def detectar_asistidor_elite_nba(fecha, umbral=15):
    """Detecta jugadores con 15+ asistencias en un partido."""
    try:
        conn = get_connection()
        query = """
            SELECT PLAYER_NAME, TEAM_ABBREVIATION, AST, PTS, TOV, MATCHUP
            FROM nba_players_games
            WHERE GAME_DATE = ? AND AST >= ?
            ORDER BY AST DESC
        """
        df = pd.read_sql_query(query, conn, params=[fecha, umbral])
        conn.close()

        perlas = []
        for _, r in df.iterrows():
            perlas.append({
                "tipo": TEXTOS[IDIOMA]["asistidor_elite"],
                "liga": "NBA",
                "jugador": r["PLAYER_NAME"],
                "equipo": r["TEAM_ABBREVIATION"],
                "detalle": f"{int(r['AST'])} ast / {int(r['PTS'])} pts / {int(r['TOV'])} pér",
                "partido": r["MATCHUP"],
                "peso": 10
            })
        return perlas
    except Exception as e:
        print(f"⚠️ Error asistidor élite NBA: {e}")
        return []


def detectar_partido_perfecto_nba(fecha, min_intentos=10):
    """Detecta tiro de campo perfecto (FG% = 100% con mínimo 10 intentos)."""
    try:
        conn = get_connection()
        query = """
            SELECT PLAYER_NAME, TEAM_ABBREVIATION, PTS, FGM, FGA, FG_PCT, MATCHUP
            FROM nba_players_games
            WHERE GAME_DATE = ?
              AND FG_PCT >= 1.0
              AND FGA >= ?
            ORDER BY FGA DESC
        """
        df = pd.read_sql_query(query, conn, params=[fecha, min_intentos])
        conn.close()

        perlas = []
        for _, r in df.iterrows():
            perlas.append({
                "tipo": TEXTOS[IDIOMA]["partido_perfecto"],
                "liga": "NBA",
                "jugador": r["PLAYER_NAME"],
                "equipo": r["TEAM_ABBREVIATION"],
                "detalle": f"{int(r['FGM'])}/{int(r['FGA'])} en campo (100%) — {int(r['PTS'])} pts",
                "partido": r["MATCHUP"],
                "peso": 11
            })
        return perlas
    except Exception as e:
        print(f"⚠️ Error partido perfecto NBA: {e}")
        return []


def detectar_record_personal_nba(fecha):
    """Detecta récords personales en pts (30+), reb (12+) y ast (10+)."""
    perlas = []
    try:
        conn = get_connection()

        for stat, col_hist, umbral in [
            ("pts", "PTS", 30),
            ("reb", "REB", 12),
            ("ast", "AST", 10),
        ]:
            query = f"""
                SELECT
                    hoy.PLAYER_NAME, hoy.TEAM_ABBREVIATION,
                    hoy.{col_hist} as valor_hoy, hoy.PTS, hoy.REB, hoy.AST, hoy.MATCHUP,
                    hist.max_val
                FROM nba_players_games hoy
                JOIN (
                    SELECT PLAYER_NAME, MAX({col_hist}) as max_val
                    FROM nba_players_games
                    GROUP BY PLAYER_NAME
                ) hist ON hoy.PLAYER_NAME = hist.PLAYER_NAME
                WHERE hoy.GAME_DATE = ?
                  AND hoy.{col_hist} >= hist.max_val
                  AND hoy.{col_hist} >= ?
            """
            df = pd.read_sql_query(query, conn, params=[fecha, umbral])
            for _, r in df.iterrows():
                perlas.append({
                    "tipo": TEXTOS[IDIOMA]["record_personal"],
                    "liga": "NBA",
                    "jugador": r["PLAYER_NAME"],
                    "equipo": r["TEAM_ABBREVIATION"],
                    "detalle": f"Récord personal en {stat.upper()}: {int(r['valor_hoy'])} "
                               f"({int(r['PTS'])} pts / {int(r['REB'])} reb / {int(r['AST'])} ast)",
                    "partido": r["MATCHUP"],
                    "peso": 10
                })

        conn.close()
    except Exception as e:
        print(f"⚠️ Error récord personal NBA: {e}")

    return perlas


def detectar_historico_combinado_nba(fecha, umbral=60):
    """Detecta partidos con pts+reb+ast >= 60."""
    try:
        conn = get_connection()
        query = """
            SELECT PLAYER_NAME, TEAM_ABBREVIATION, PTS, REB, AST,
                   (PTS + REB + AST) as combinado, MATCHUP
            FROM nba_players_games
            WHERE GAME_DATE = ? AND (PTS + REB + AST) >= ?
            ORDER BY combinado DESC
        """
        df = pd.read_sql_query(query, conn, params=[fecha, umbral])
        conn.close()

        perlas = []
        for _, r in df.iterrows():
            perlas.append({
                "tipo": TEXTOS[IDIOMA]["historico_combinado"],
                "liga": "NBA",
                "jugador": r["PLAYER_NAME"],
                "equipo": r["TEAM_ABBREVIATION"],
                "detalle": f"{int(r['combinado'])} combinado — {int(r['PTS'])} pts / {int(r['REB'])} reb / {int(r['AST'])} ast",
                "partido": r["MATCHUP"],
                "peso": 11
            })
        return perlas
    except Exception as e:
        print(f"⚠️ Error histórico combinado NBA: {e}")
        return []


def detectar_defensa_elite_nba(fecha, umbral=5):
    """Detecta 5+ robos o 5+ tapones en un partido."""
    try:
        conn = get_connection()
        query = """
            SELECT PLAYER_NAME, TEAM_ABBREVIATION, STL, BLK, PTS, MATCHUP
            FROM nba_players_games
            WHERE GAME_DATE = ? AND (STL >= ? OR BLK >= ?)
            ORDER BY (STL + BLK) DESC
        """
        df = pd.read_sql_query(query, conn, params=[fecha, umbral, umbral])
        conn.close()

        perlas = []
        for _, r in df.iterrows():
            partes = []
            if r["STL"] >= umbral:
                partes.append(f"{int(r['STL'])} robos")
            if r["BLK"] >= umbral:
                partes.append(f"{int(r['BLK'])} tapones")
            perlas.append({
                "tipo": TEXTOS[IDIOMA]["defensa_elite"],
                "liga": "NBA",
                "jugador": r["PLAYER_NAME"],
                "equipo": r["TEAM_ABBREVIATION"],
                "detalle": " / ".join(partes) + f" — {int(r['PTS'])} pts",
                "partido": r["MATCHUP"],
                "peso": 9
            })
        return perlas
    except Exception as e:
        print(f"⚠️ Error defensa élite NBA: {e}")
        return []


def detectar_equipo_imparable_nba(fecha, umbral=150):
    """Detecta equipos que anotaron 150+ puntos."""
    try:
        conn = get_connection()
        query = """
            SELECT TEAM_NAME, TEAM_ABBREVIATION, PTS, MATCHUP
            FROM nba_games
            WHERE GAME_DATE = ? AND PTS >= ?
            ORDER BY PTS DESC
        """
        df = pd.read_sql_query(query, conn, params=[fecha, umbral])
        conn.close()

        perlas = []
        for _, r in df.iterrows():
            perlas.append({
                "tipo": TEXTOS[IDIOMA]["equipo_imparable"],
                "liga": "NBA",
                "jugador": None,
                "equipo": r["TEAM_ABBREVIATION"],
                "detalle": f"{r['TEAM_NAME']} anotó {int(r['PTS'])} puntos",
                "partido": r["MATCHUP"],
                "peso": 9
            })
        return perlas
    except Exception as e:
        print(f"⚠️ Error equipo imparable NBA: {e}")
        return []


def detectar_remontada_epica_nba(fecha, diferencia_min=20):
    """Detecta victorias con diferencia de 20+ puntos (remontada épica)."""
    try:
        conn = get_connection()
        query = """
            SELECT home_team, away_team, home_score, away_score, winner
            FROM nba_daily_results
            WHERE game_date = ?
              AND ABS(home_score - away_score) >= ?
        """
        df = pd.read_sql_query(query, conn, params=[fecha, diferencia_min])
        conn.close()

        perlas = []
        for _, r in df.iterrows():
            diff = abs(int(r["home_score"]) - int(r["away_score"]))
            ganador = r["winner"]
            perlas.append({
                "tipo": TEXTOS[IDIOMA]["remontada_epica"],
                "liga": "NBA",
                "jugador": None,
                "equipo": ganador,
                "detalle": f"{r['home_team']} {int(r['home_score'])} - {int(r['away_score'])} {r['away_team']} (diferencia: {diff} pts)",
                "partido": f"{r['home_team']} vs {r['away_team']}",
                "peso": 8
            })
        return perlas
    except Exception as e:
        print(f"⚠️ Error remontada épica NBA: {e}")
        return []


# ============================================================================
# PERLAS EUROLIGA — CATEGORÍAS ORIGINALES
# ============================================================================

def detectar_perlas_euroliga(fecha):
    """Detecta actuaciones destacadas en Euroliga."""
    try:
        conn = get_connection()

        # Mejores anotadores con nombre de jugador
        query = """
            SELECT
                ep.player_name, epg.team_id, epg.pts, epg.reb, epg.ast,
                eg.home_team, eg.away_team, eg.score_home, eg.score_away
            FROM euro_players_games epg
            JOIN euro_players ep ON epg.player_id = ep.player_id
            JOIN euro_games eg ON epg.game_id = eg.game_id
            WHERE eg.date = ?
              AND (epg.pts >= 20 OR epg.reb >= 10 OR epg.ast >= 8)
            ORDER BY epg.pts DESC
            LIMIT 5
        """
        df = pd.read_sql_query(query, conn, params=[fecha])
        conn.close()

        perlas = []
        for _, r in df.iterrows():
            stats = []
            if r["pts"] and r["pts"] >= 20:
                stats.append(f"{int(r['pts'])} pts")
            if r["reb"] and r["reb"] >= 10:
                stats.append(f"{int(r['reb'])} reb")
            if r["ast"] and r["ast"] >= 8:
                stats.append(f"{int(r['ast'])} ast")

            if stats:
                perlas.append({
                    "tipo": TEXTOS[IDIOMA]["perla_euro"],
                    "liga": "Euroliga",
                    "jugador": r["player_name"],
                    "equipo": r["team_id"],
                    "detalle": " / ".join(stats) + f" — {r['home_team']} {int(r['score_home'] or 0)}-{int(r['score_away'] or 0)} {r['away_team']}",
                    "partido": f"{r['home_team']} vs {r['away_team']}",
                    "peso": 8
                })
        return perlas
    except Exception as e:
        print(f"⚠️ Error perlas Euroliga: {e}")
        return []


def detectar_remontadas_euroliga(fecha):
    """Detecta remontadas en Euroliga usando parciales por cuartos."""
    try:
        conn = get_connection()
        query = """
            SELECT
                eg.home_team, eg.away_team, eg.score_home, eg.score_away,
                ege.home_q1, ege.home_q2, ege.away_q1, ege.away_q2
            FROM euro_games eg
            JOIN euro_games_extended ege ON eg.game_id = ege.game_id
            WHERE eg.date = ?
              AND eg.score_home IS NOT NULL
              AND eg.score_away IS NOT NULL
        """
        df = pd.read_sql_query(query, conn, params=[fecha])
        conn.close()

        perlas = []
        for _, r in df.iterrows():
            try:
                # Marcador al descanso
                home_medio = (r["home_q1"] or 0) + (r["home_q2"] or 0)
                away_medio = (r["away_q1"] or 0) + (r["away_q2"] or 0)
                home_final = int(r["score_home"] or 0)
                away_final = int(r["score_away"] or 0)

                # Ganó el que iba perdiendo al descanso
                if home_medio < away_medio and home_final > away_final:
                    perlas.append({
                        "tipo": TEXTOS[IDIOMA]["remontada_euro"],
                        "liga": "Euroliga",
                        "jugador": None,
                        "equipo": r["home_team"],
                        "detalle": f"{r['home_team']} remontó ({away_medio}-{home_medio} al descanso) y ganó {home_final}-{away_final}",
                        "partido": f"{r['home_team']} vs {r['away_team']}",
                        "peso": 8
                    })
                elif away_medio < home_medio and away_final > home_final:
                    perlas.append({
                        "tipo": TEXTOS[IDIOMA]["remontada_euro"],
                        "liga": "Euroliga",
                        "jugador": None,
                        "equipo": r["away_team"],
                        "detalle": f"{r['away_team']} remontó ({home_medio}-{away_medio} al descanso) y ganó {away_final}-{home_final}",
                        "partido": f"{r['home_team']} vs {r['away_team']}",
                        "peso": 8
                    })
            except Exception:
                continue

        return perlas
    except Exception as e:
        print(f"⚠️ Error remontadas Euroliga: {e}")
        return []


def obtener_proximos_partidos_euroliga(n=5):
    """Obtiene próximos partidos de Euroliga cuando no hubo acción ayer."""
    try:
        conn = get_connection()
        query = """
            SELECT date, home_team, away_team
            FROM euro_games
            WHERE date > date('now')
            ORDER BY date ASC
            LIMIT ?
        """
        df = pd.read_sql_query(query, conn, params=[n])
        conn.close()
        return df
    except Exception as e:
        print(f"⚠️ Error próximos partidos Euro: {e}")
        return pd.DataFrame()


# ============================================================================
# PERLAS EUROLIGA — NUEVAS CATEGORÍAS
# ============================================================================

def _nombre_jugador_euro(conn, player_id):
    """Devuelve el nombre del jugador o player_id como fallback."""
    try:
        df = pd.read_sql_query(
            "SELECT player_name FROM euro_players WHERE player_id = ? LIMIT 1",
            conn, params=[player_id]
        )
        if not df.empty:
            return df.iloc[0]["player_name"]
    except Exception:
        pass
    return str(player_id)


def detectar_explosion_euro(fecha, umbral=30):
    """Detecta jugadores con 30+ puntos en Euroliga."""
    try:
        conn = get_connection()
        query = """
            SELECT epg.player_id, epg.team_id, epg.pts, epg.reb, epg.ast,
                   eg.home_team, eg.away_team
            FROM euro_players_games epg
            JOIN euro_games eg ON epg.game_id = eg.game_id
            WHERE eg.date = ? AND epg.pts >= ?
            ORDER BY epg.pts DESC
        """
        df = pd.read_sql_query(query, conn, params=[fecha, umbral])

        perlas = []
        for _, r in df.iterrows():
            nombre = _nombre_jugador_euro(conn, r["player_id"])
            perlas.append({
                "tipo": TEXTOS[IDIOMA]["explosion_50"],
                "liga": "Euroliga",
                "jugador": nombre,
                "equipo": r["team_id"],
                "detalle": f"{int(r['pts'])} pts / {int(r['reb'])} reb / {int(r['ast'])} ast",
                "partido": f"{r['home_team']} vs {r['away_team']}",
                "peso": 11
            })
        conn.close()
        return perlas
    except Exception as e:
        print(f"⚠️ Error explosión anotadora Euroliga: {e}")
        return []


def detectar_dominio_reboteador_euro(fecha, umbral=15):
    """Detecta jugadores con 15+ rebotes en Euroliga."""
    try:
        conn = get_connection()
        query = """
            SELECT epg.player_id, epg.team_id, epg.pts, epg.reb, epg.ast,
                   eg.home_team, eg.away_team
            FROM euro_players_games epg
            JOIN euro_games eg ON epg.game_id = eg.game_id
            WHERE eg.date = ? AND epg.reb >= ?
            ORDER BY epg.reb DESC
        """
        df = pd.read_sql_query(query, conn, params=[fecha, umbral])

        perlas = []
        for _, r in df.iterrows():
            nombre = _nombre_jugador_euro(conn, r["player_id"])
            perlas.append({
                "tipo": TEXTOS[IDIOMA]["dominio_reboteador"],
                "liga": "Euroliga",
                "jugador": nombre,
                "equipo": r["team_id"],
                "detalle": f"{int(r['reb'])} reb / {int(r['pts'])} pts / {int(r['ast'])} ast",
                "partido": f"{r['home_team']} vs {r['away_team']}",
                "peso": 10
            })
        conn.close()
        return perlas
    except Exception as e:
        print(f"⚠️ Error dominio reboteador Euroliga: {e}")
        return []


def detectar_asistidor_elite_euro(fecha, umbral=10):
    """Detecta jugadores con 10+ asistencias en Euroliga."""
    try:
        conn = get_connection()
        query = """
            SELECT epg.player_id, epg.team_id, epg.pts, epg.reb, epg.ast,
                   eg.home_team, eg.away_team
            FROM euro_players_games epg
            JOIN euro_games eg ON epg.game_id = eg.game_id
            WHERE eg.date = ? AND epg.ast >= ?
            ORDER BY epg.ast DESC
        """
        df = pd.read_sql_query(query, conn, params=[fecha, umbral])

        perlas = []
        for _, r in df.iterrows():
            nombre = _nombre_jugador_euro(conn, r["player_id"])
            perlas.append({
                "tipo": TEXTOS[IDIOMA]["asistidor_elite"],
                "liga": "Euroliga",
                "jugador": nombre,
                "equipo": r["team_id"],
                "detalle": f"{int(r['ast'])} ast / {int(r['pts'])} pts / {int(r['reb'])} reb",
                "partido": f"{r['home_team']} vs {r['away_team']}",
                "peso": 10
            })
        conn.close()
        return perlas
    except Exception as e:
        print(f"⚠️ Error asistidor élite Euroliga: {e}")
        return []


def detectar_record_personal_euro(fecha):
    """Detecta récords personales en pts (20+), reb (10+) y ast (8+) en Euroliga."""
    perlas = []
    try:
        conn = get_connection()

        for stat, col, umbral in [("pts", "pts", 20), ("reb", "reb", 10), ("ast", "ast", 8)]:
            query = f"""
                SELECT
                    hoy.player_id, hoy.team_id,
                    hoy.{col} as valor_hoy, hoy.pts, hoy.reb, hoy.ast,
                    eg.home_team, eg.away_team,
                    hist.max_val
                FROM euro_players_games hoy
                JOIN euro_games eg ON hoy.game_id = eg.game_id
                JOIN (
                    SELECT player_id, MAX({col}) as max_val
                    FROM euro_players_games
                    GROUP BY player_id
                ) hist ON hoy.player_id = hist.player_id
                WHERE eg.date = ?
                  AND hoy.{col} >= hist.max_val
                  AND hoy.{col} >= ?
            """
            df = pd.read_sql_query(query, conn, params=[fecha, umbral])
            for _, r in df.iterrows():
                nombre = _nombre_jugador_euro(conn, r["player_id"])
                perlas.append({
                    "tipo": TEXTOS[IDIOMA]["record_personal"],
                    "liga": "Euroliga",
                    "jugador": nombre,
                    "equipo": r["team_id"],
                    "detalle": f"Récord personal en {stat.upper()}: {int(r['valor_hoy'])} "
                               f"({int(r['pts'])} pts / {int(r['reb'])} reb / {int(r['ast'])} ast)",
                    "partido": f"{r['home_team']} vs {r['away_team']}",
                    "peso": 10
                })

        conn.close()
    except Exception as e:
        print(f"⚠️ Error récord personal Euroliga: {e}")

    return perlas


def detectar_historico_combinado_euro(fecha, umbral=40):
    """Detecta pts+reb+ast >= 40 en Euroliga."""
    try:
        conn = get_connection()
        query = """
            SELECT epg.player_id, epg.team_id, epg.pts, epg.reb, epg.ast,
                   (epg.pts + epg.reb + epg.ast) as combinado,
                   eg.home_team, eg.away_team
            FROM euro_players_games epg
            JOIN euro_games eg ON epg.game_id = eg.game_id
            WHERE eg.date = ? AND (epg.pts + epg.reb + epg.ast) >= ?
            ORDER BY combinado DESC
        """
        df = pd.read_sql_query(query, conn, params=[fecha, umbral])

        perlas = []
        for _, r in df.iterrows():
            nombre = _nombre_jugador_euro(conn, r["player_id"])
            perlas.append({
                "tipo": TEXTOS[IDIOMA]["historico_combinado"],
                "liga": "Euroliga",
                "jugador": nombre,
                "equipo": r["team_id"],
                "detalle": f"{int(r['combinado'])} combinado — {int(r['pts'])} pts / {int(r['reb'])} reb / {int(r['ast'])} ast",
                "partido": f"{r['home_team']} vs {r['away_team']}",
                "peso": 11
            })
        conn.close()
        return perlas
    except Exception as e:
        print(f"⚠️ Error histórico combinado Euroliga: {e}")
        return []


def detectar_equipo_imparable_euro(fecha, umbral=100):
    """Detecta equipos que anotaron 100+ puntos en Euroliga."""
    try:
        conn = get_connection()
        query = """
            SELECT home_team, away_team, score_home, score_away
            FROM euro_games
            WHERE date = ?
              AND (score_home >= ? OR score_away >= ?)
              AND score_home IS NOT NULL
              AND score_away IS NOT NULL
            ORDER BY MAX(score_home, score_away) DESC
        """
        df = pd.read_sql_query(query, conn, params=[fecha, umbral, umbral])
        conn.close()

        perlas = []
        for _, r in df.iterrows():
            if r["score_home"] and int(r["score_home"]) >= umbral:
                perlas.append({
                    "tipo": TEXTOS[IDIOMA]["equipo_imparable"],
                    "liga": "Euroliga",
                    "jugador": None,
                    "equipo": r["home_team"],
                    "detalle": f"{r['home_team']} anotó {int(r['score_home'])} puntos — resultado: {int(r['score_home'])}-{int(r['score_away'])}",
                    "partido": f"{r['home_team']} vs {r['away_team']}",
                    "peso": 9
                })
            if r["score_away"] and int(r["score_away"]) >= umbral:
                perlas.append({
                    "tipo": TEXTOS[IDIOMA]["equipo_imparable"],
                    "liga": "Euroliga",
                    "jugador": None,
                    "equipo": r["away_team"],
                    "detalle": f"{r['away_team']} anotó {int(r['score_away'])} puntos — resultado: {int(r['score_home'])}-{int(r['score_away'])}",
                    "partido": f"{r['home_team']} vs {r['away_team']}",
                    "peso": 9
                })
        return perlas
    except Exception as e:
        print(f"⚠️ Error equipo imparable Euroliga: {e}")
        return []


def detectar_remontada_epica_euro(fecha, diferencia_min=15):
    """Detecta remontadas épicas en Euroliga (diferencia 15+ al descanso superada)."""
    try:
        conn = get_connection()
        query = """
            SELECT
                eg.home_team, eg.away_team, eg.score_home, eg.score_away,
                ege.home_q1, ege.home_q2, ege.away_q1, ege.away_q2
            FROM euro_games eg
            JOIN euro_games_extended ege ON eg.game_id = ege.game_id
            WHERE eg.date = ?
              AND eg.score_home IS NOT NULL
              AND eg.score_away IS NOT NULL
        """
        df = pd.read_sql_query(query, conn, params=[fecha])
        conn.close()

        perlas = []
        for _, r in df.iterrows():
            try:
                home_medio = (r["home_q1"] or 0) + (r["home_q2"] or 0)
                away_medio = (r["away_q1"] or 0) + (r["away_q2"] or 0)
                home_final = int(r["score_home"] or 0)
                away_final = int(r["score_away"] or 0)
                diff_descanso = abs(home_medio - away_medio)

                if diff_descanso < diferencia_min:
                    continue

                if home_medio < away_medio and home_final > away_final:
                    perlas.append({
                        "tipo": TEXTOS[IDIOMA]["remontada_epica"],
                        "liga": "Euroliga",
                        "jugador": None,
                        "equipo": r["home_team"],
                        "detalle": f"{r['home_team']} remontó {diff_descanso} puntos ({away_medio}-{home_medio} al descanso) y ganó {home_final}-{away_final}",
                        "partido": f"{r['home_team']} vs {r['away_team']}",
                        "peso": 10
                    })
                elif away_medio < home_medio and away_final > home_final:
                    perlas.append({
                        "tipo": TEXTOS[IDIOMA]["remontada_epica"],
                        "liga": "Euroliga",
                        "jugador": None,
                        "equipo": r["away_team"],
                        "detalle": f"{r['away_team']} remontó {diff_descanso} puntos ({home_medio}-{away_medio} al descanso) y ganó {away_final}-{home_final}",
                        "partido": f"{r['home_team']} vs {r['away_team']}",
                        "peso": 10
                    })
            except Exception:
                continue

        return perlas
    except Exception as e:
        print(f"⚠️ Error remontada épica Euroliga: {e}")
        return []


# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def buscar_perlas(fecha=None, enviar_telegram=True):
    """
    Función principal. Detecta todas las perlas del día.

    Args:
        fecha: string 'YYYY-MM-DD', por defecto ayer
        enviar_telegram: si True, envía resultado a Telegram

    Returns:
        dict con perlas NBA, perlas Euroliga, próximos Euro si no hubo partidos
    """
    if fecha is None:
        fecha = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    fecha_display = datetime.strptime(fecha, '%Y-%m-%d').strftime('%d/%m/%Y')
    print(f"\n🔍 Buscando perlas del {fecha_display}...")

    # ── NBA ──────────────────────────────────────────────────────────────────
    perlas_nba = []
    perlas_nba += detectar_triple_dobles_nba(fecha)
    perlas_nba += detectar_explosion_anotadora_nba(fecha)
    perlas_nba += detectar_plus_minus_extremo_nba(fecha)
    perlas_nba += detectar_remontadas_nba(fecha)
    perlas_nba += detectar_records_nba(fecha)
    # Nuevas categorías NBA
    perlas_nba += detectar_explosion_50_nba(fecha)
    perlas_nba += detectar_dominio_reboteador_nba(fecha)
    perlas_nba += detectar_asistidor_elite_nba(fecha)
    perlas_nba += detectar_partido_perfecto_nba(fecha)
    perlas_nba += detectar_record_personal_nba(fecha)
    perlas_nba += detectar_historico_combinado_nba(fecha)
    perlas_nba += detectar_defensa_elite_nba(fecha)
    perlas_nba += detectar_equipo_imparable_nba(fecha)
    perlas_nba += detectar_remontada_epica_nba(fecha)

    # Ordenar por peso y deduplicar: un jugador solo aparece en su categoría de mayor peso
    perlas_nba = sorted(perlas_nba, key=lambda x: x["peso"], reverse=True)
    _vistos = {}
    _dedup = []
    for p in perlas_nba:
        clave = p["jugador"] if p["jugador"] else f"__equipo__{p['equipo']}__{p['partido']}"
        if clave not in _vistos:
            _vistos[clave] = True
            _dedup.append(p)
    perlas_nba = _dedup

    # ── EUROLIGA ─────────────────────────────────────────────────────────────
    perlas_euro = []
    perlas_euro += detectar_perlas_euroliga(fecha)
    perlas_euro += detectar_remontadas_euroliga(fecha)
    # Nuevas categorías Euroliga
    perlas_euro += detectar_explosion_euro(fecha)
    perlas_euro += detectar_dominio_reboteador_euro(fecha)
    perlas_euro += detectar_asistidor_elite_euro(fecha)
    perlas_euro += detectar_record_personal_euro(fecha)
    perlas_euro += detectar_historico_combinado_euro(fecha)
    perlas_euro += detectar_equipo_imparable_euro(fecha)
    perlas_euro += detectar_remontada_epica_euro(fecha)

    perlas_euro = sorted(perlas_euro, key=lambda x: x["peso"], reverse=True)

    # Si no hubo partidos Euro ayer → próximos partidos
    proximos_euro = pd.DataFrame()
    if not perlas_euro:
        proximos_euro = obtener_proximos_partidos_euroliga()
        print("ℹ️ Sin partidos Euroliga ayer. Añadiendo próximos partidos.")

    # ── FORMATEAR MENSAJE ─────────────────────────────────────────────────────
    mensaje = formatear_perlas(fecha_display, perlas_nba, perlas_euro, proximos_euro)

    print(mensaje)

    # ── ENVIAR A TELEGRAM ────────────────────────────────────────────────────
    if enviar_telegram and (perlas_nba or perlas_euro or not proximos_euro.empty):
        try:
            from src.automation.bot_manager import enviar_mensaje
            enviar_mensaje(mensaje)
            print("✅ Perlas enviadas a Telegram")
        except Exception as e:
            print(f"⚠️ No se pudo enviar a Telegram: {e}")

    return {
        "nba": perlas_nba,
        "euroliga": perlas_euro,
        "proximos_euro": proximos_euro,
        "mensaje": mensaje
    }


def formatear_perlas(fecha_display, perlas_nba, perlas_euro, proximos_euro):
    """Formatea las perlas en mensaje legible para Telegram."""
    lineas = [f"💎 *Perlas Dos Aros — {fecha_display}*\n"]

    # NBA
    if perlas_nba:
        lineas.append("🏀 *NBA*")
        for p in perlas_nba[:5]:  # máximo 5 perlas NBA
            if p["jugador"]:
                lineas.append(f"• *{p['tipo']}* — {p['jugador']} ({p['equipo']}): {p['detalle']}")
            else:
                lineas.append(f"• *{p['tipo']}*: {p['detalle']}")
        lineas.append("")

    # EUROLIGA
    if perlas_euro:
        lineas.append("🌍 *Euroliga*")
        for p in perlas_euro[:5]:  # máximo 5 perlas Euro
            if p["jugador"]:
                lineas.append(f"• *{p['tipo']}* — {p['jugador']} ({p['equipo']}): {p['detalle']}")
            else:
                lineas.append(f"• *{p['tipo']}*: {p['detalle']}")
        lineas.append("")

    # PRÓXIMOS PARTIDOS EURO (si no hubo partidos ayer)
    if not proximos_euro.empty:
        lineas.append("📅 *Próximos partidos Euroliga*")
        for _, r in proximos_euro.iterrows():
            fecha_partido = datetime.strptime(r["date"], '%Y-%m-%d').strftime('%d/%m')
            lineas.append(f"• {fecha_partido}: {r['home_team']} vs {r['away_team']}")
        lineas.append("")

    if not perlas_nba and not perlas_euro and proximos_euro.empty:
        lineas.append("Sin perlas destacadas ayer.")

    return "\n".join(lineas)


# Compatibilidad con master_sync.py (nombre antiguo)
def buscar_perlas_nba(enviar_telegram=True):
    """Alias para compatibilidad con llamadas existentes en master_sync."""
    resultado = buscar_perlas(enviar_telegram=enviar_telegram)
    return resultado["mensaje"]


# ============================================================================
# EJECUCIÓN DIRECTA
# ============================================================================

if __name__ == "__main__":
    buscar_perlas()
