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

Euroliga:
  - Mejores actuaciones individuales (pts, reb, ast)
  - Partidos con remontada (usando parciales de euro_games_extended)
  - Próximos partidos si no hubo acción ayer

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
    }
}


def get_connection():
    return sqlite3.connect(DB_PATH)


# ============================================================================
# PERLAS NBA
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
                "peso": 10  # para ordenar por importancia
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
            SELECT PLAYER_NAME, TEAM_ABBREVIATION, PLUS_MINUS, PTS, MIN, MATCHUP
            FROM nba_players_games
            WHERE GAME_DATE = ? AND (PLUS_MINUS >= ? OR PLUS_MINUS <= -?)
            ORDER BY ABS(PLUS_MINUS) DESC
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
            perdedor = r["away_team"] if ganador == r["home_team"] else r["home_team"]
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
# PERLAS EUROLIGA
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

    # Ordenar por peso (importancia) y eliminar duplicados de jugador
    perlas_nba = sorted(perlas_nba, key=lambda x: x["peso"], reverse=True)

    # ── EUROLIGA ─────────────────────────────────────────────────────────────
    perlas_euro = []
    perlas_euro += detectar_perlas_euroliga(fecha)
    perlas_euro += detectar_remontadas_euroliga(fecha)
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
            from automation.bot_manager import enviar_mensaje
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