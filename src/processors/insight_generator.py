"""
================================================================================
GENERADOR DE PERLAS - Proyecto Dos Aros (v2 — IA-driven)
================================================================================
Flujo de 4 pasos:
  1. Extrae datos del día de la DB (nba_players_games, euro_players_games,
     nba_daily_results, euro_games)
  2. Envía los datos a IA (Gemini → Groq) para identificar actuaciones destacadas
  3. Verifica cada perla contra la DB (valor exacto presente en los datos)
  4. Formatea y retorna las perlas verificadas

Entry point : buscar_perlas(fecha, enviar_telegram)
Alias compat: buscar_perlas_nba()  ← master_sync.py
================================================================================
"""

import json
import re
import sqlite3
import pandas as pd
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("LOCAL_DB", "/mnt/nba_data/dosaros_local.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


# ============================================================================
# PASO 1 — EXTRACCIÓN DE DATOS
# ============================================================================

def _extraer_stats_nba(fecha, conn):
    """Extrae stats completas de todos los jugadores NBA del día."""
    try:
        query = """
            SELECT PLAYER_NAME, TEAM_ABBREVIATION, PTS, REB, AST,
                   STL, BLK, FGM, FGA, FG_PCT,
                   CAST(PLUS_MINUS AS INTEGER) as PLUS_MINUS, MIN
            FROM nba_players_games
            WHERE GAME_DATE = ?
            ORDER BY PTS DESC
        """
        return pd.read_sql_query(query, conn, params=[fecha])
    except Exception as e:
        print(f"Error extrayendo stats NBA: {e}")
        return pd.DataFrame()


def _extraer_stats_euro(fecha, conn):
    """Extrae stats de jugadores Euroliga del día con nombre del jugador."""
    try:
        query = """
            SELECT COALESCE(ep.player_name, epg.player_id) as player_name,
                   epg.team_id, epg.pts, epg.reb, epg.ast,
                   eg.home_team, eg.away_team
            FROM euro_players_games epg
            LEFT JOIN euro_players ep ON epg.player_id = ep.player_id
            JOIN euro_games eg ON epg.game_id = eg.game_id
            WHERE eg.date = ?
            ORDER BY epg.pts DESC
        """
        return pd.read_sql_query(query, conn, params=[fecha])
    except Exception as e:
        print(f"Error extrayendo stats Euro: {e}")
        return pd.DataFrame()


def _extraer_resultados_nba(fecha, conn):
    """Extrae resultados NBA del día desde nba_games, construyendo home/away por GAME_ID."""
    try:
        query = """
            SELECT GAME_ID, TEAM_ABBREVIATION, MATCHUP, WL, PTS
            FROM nba_games
            WHERE GAME_DATE = ?
        """
        df = pd.read_sql_query(query, conn, params=[fecha])
        if df.empty:
            return pd.DataFrame()

        resultados = []
        for game_id, grupo in df.groupby('GAME_ID'):
            if len(grupo) != 2:
                continue
            home = grupo[grupo['MATCHUP'].str.contains('vs\\.', na=False)]
            away = grupo[grupo['MATCHUP'].str.contains('@', na=False)]
            if home.empty or away.empty:
                continue
            home = home.iloc[0]
            away = away.iloc[0]
            winner = home['TEAM_ABBREVIATION'] if home['WL'] == 'W' else away['TEAM_ABBREVIATION']
            resultados.append({
                'home_team':  home['TEAM_ABBREVIATION'],
                'away_team':  away['TEAM_ABBREVIATION'],
                'home_score': home['PTS'],
                'away_score': away['PTS'],
                'winner':     winner,
            })
        return pd.DataFrame(resultados)
    except Exception as e:
        print(f"Error extrayendo resultados NBA: {e}")
        return pd.DataFrame()


def _extraer_resultados_euro(fecha, conn):
    """Extrae resultados Euroliga del día."""
    try:
        query = """
            SELECT home_team, away_team, score_home, score_away
            FROM euro_games
            WHERE date = ?
              AND score_home IS NOT NULL
        """
        return pd.read_sql_query(query, conn, params=[fecha])
    except Exception as e:
        print(f"Error extrayendo resultados Euro: {e}")
        return pd.DataFrame()


# ============================================================================
# PASO 2 — CONSULTA A IA
# ============================================================================

def _preparar_datos_para_ia(df_nba, df_euro, df_res_nba, df_res_euro):
    """Serializa los DataFrames a texto CSV compacto para el prompt."""
    partes = []

    if not df_nba.empty:
        cols = ['PLAYER_NAME', 'TEAM_ABBREVIATION', 'PTS', 'REB', 'AST',
                'STL', 'BLK', 'FGM', 'FGA', 'FG_PCT', 'PLUS_MINUS']
        cols_ok = [c for c in cols if c in df_nba.columns]
        partes.append("=== NBA JUGADORES (top 30 por PTS) ===\n" +
                       df_nba[cols_ok].head(30).to_csv(index=False))

    if not df_res_nba.empty:
        partes.append("=== NBA RESULTADOS ===\n" + df_res_nba.to_csv(index=False))

    if not df_euro.empty:
        cols_e = ['player_name', 'team_id', 'pts', 'reb', 'ast']
        cols_ok = [c for c in cols_e if c in df_euro.columns]
        partes.append("=== EUROLIGA JUGADORES ===\n" +
                       df_euro[cols_ok].head(20).to_csv(index=False))

    if not df_res_euro.empty:
        partes.append("=== EUROLIGA RESULTADOS ===\n" + df_res_euro.to_csv(index=False))

    return "\n\n".join(partes)


def _parsear_json_ia(texto):
    """Extrae y parsea el JSON array de la respuesta de la IA."""
    if not texto:
        return []
    # Eliminar bloques markdown ```json ... ```
    texto = re.sub(r'```(?:json)?\s*', '', texto).strip().rstrip('`').strip()
    # Encontrar el primer [ ... ]
    match = re.search(r'\[.*\]', texto, re.DOTALL)
    if match:
        texto = match.group(0)
    try:
        datos = json.loads(texto)
        return datos if isinstance(datos, list) else []
    except json.JSONDecodeError as e:
        print(f"Error parseando JSON de IA: {e}")
        print(f"Fragmento recibido: {texto[:200]}")
        return []


def _consultar_ia(fecha, datos_texto):
    """Envía los datos a la IA y recibe las perlas identificadas como JSON."""
    from src.utils.api_manager import APIManager
    api = APIManager()

    prompt = f"""Eres analista de baloncesto de Dos Aros. Dados estos datos del {fecha}:

{datos_texto}

Identifica las 3-5 actuaciones más destacadas e inusuales.
Para cada una devuelve un JSON con:
- jugador (nombre exacto como aparece en los datos, o null si es perla de equipo)
- equipo (código o nombre exacto)
- liga (NBA o Euroliga)
- stat_clave (PTS, REB, AST, STL, BLK, FG_PCT o EQUIPO)
- valor (número exacto de la estadística, o puntos del equipo si es colectiva)
- razon (por qué es destacado, máx 20 palabras)
- tipo (explosion_anotadora/rebotes/asistencias/defensa/triple_doble/record/equipo)

Responde SOLO con JSON array, sin texto adicional."""

    respuesta = api.generate_text(prompt=prompt, providers=['gemini', 'groq'])
    print(f"  Respuesta IA ({len(respuesta)} chars)")
    return _parsear_json_ia(respuesta)


# ============================================================================
# PASO 3 — VERIFICACIÓN
# ============================================================================

_STAT_MAP_NBA = {
    'PTS': 'PTS', 'PUNTOS': 'PTS',
    'REB': 'REB', 'REBOTES': 'REB',
    'AST': 'AST', 'ASISTENCIAS': 'AST',
    'STL': 'STL', 'ROBOS': 'STL',
    'BLK': 'BLK', 'TAPONES': 'BLK',
    'FG_PCT': 'FG_PCT',
    'PLUS_MINUS': 'PLUS_MINUS',
}

_STAT_MAP_EURO = {
    'PTS': 'pts', 'PUNTOS': 'pts',
    'REB': 'reb', 'REBOTES': 'reb',
    'AST': 'ast', 'ASISTENCIAS': 'ast',
}


def _verificar_perla(perla, df_nba, df_euro):
    """
    Verifica que el dato exacto existe en la DB.
    Retorna True si se verifica (o no es posible verificar),
    False si la IA contradice los datos reales.
    """
    liga = str(perla.get('liga', '')).upper()
    jugador = perla.get('jugador')
    stat = str(perla.get('stat_clave', '')).upper()
    valor_ia = perla.get('valor')

    # Perlas de equipo o sin valor concreto: dejar pasar
    if jugador is None or valor_ia is None or stat == 'EQUIPO':
        return True

    try:
        valor_ia = float(valor_ia)
    except (TypeError, ValueError):
        return True

    if liga == 'NBA' and not df_nba.empty:
        col = _STAT_MAP_NBA.get(stat)
        if col and col in df_nba.columns:
            mask = df_nba['PLAYER_NAME'].str.upper() == str(jugador).upper()
            if not mask.any():
                print(f"  [DESCARTADA] '{jugador}' no encontrado en datos NBA")
                return False
            actual = float(df_nba.loc[mask, col].max())
            if abs(actual - valor_ia) > 1:
                print(f"  [DESCARTADA] {jugador} {stat}: IA={valor_ia}, DB={actual}")
                return False
        return True

    if liga == 'EUROLIGA' and not df_euro.empty:
        col = _STAT_MAP_EURO.get(stat)
        if col and col in df_euro.columns and 'player_name' in df_euro.columns:
            mask = df_euro['player_name'].str.upper() == str(jugador).upper()
            if not mask.any():
                print(f"  [DESCARTADA] '{jugador}' no encontrado en datos Euroliga")
                return False
            actual = float(df_euro.loc[mask, col].max())
            if abs(actual - valor_ia) > 1:
                print(f"  [DESCARTADA] {jugador} {stat}: IA={valor_ia}, DB={actual}")
                return False
        return True

    return True  # Liga desconocida o sin datos: dejar pasar


# ============================================================================
# PASO 4 — FORMATO Y SALIDA
# ============================================================================

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
        print(f"Error próximos partidos Euro: {e}")
        return pd.DataFrame()


def formatear_perlas(fecha_display, perlas_nba, perlas_euro, proximos_euro):
    """Formatea las perlas en mensaje legible para Telegram (HTML)."""
    lineas = [f"💎 <b>Perlas Dos Aros — {fecha_display}</b>\n"]

    if perlas_nba:
        lineas.append("🏀 <b>NBA</b>")
        for p in perlas_nba[:5]:
            jugador = p.get('jugador') or p.get('equipo', '')
            equipo = p.get('equipo', '')
            stat = p.get('stat_clave', '')
            valor = p.get('valor', '')
            razon = p.get('razon', '')
            tipo = str(p.get('tipo', 'perla')).replace('_', ' ').title()
            detalle = f"{stat} {valor} — {razon}" if stat and valor else razon
            if jugador and jugador != equipo:
                lineas.append(f"• <b>{tipo}</b> — {jugador} ({equipo}): {detalle}")
            else:
                lineas.append(f"• <b>{tipo}</b> — {equipo}: {detalle}")
        lineas.append("")

    if perlas_euro:
        lineas.append("🌍 <b>Euroliga</b>")
        for p in perlas_euro[:5]:
            jugador = p.get('jugador') or p.get('equipo', '')
            equipo = p.get('equipo', '')
            stat = p.get('stat_clave', '')
            valor = p.get('valor', '')
            razon = p.get('razon', '')
            tipo = str(p.get('tipo', 'perla')).replace('_', ' ').title()
            detalle = f"{stat} {valor} — {razon}" if stat and valor else razon
            if jugador and jugador != equipo:
                lineas.append(f"• <b>{tipo}</b> — {jugador} ({equipo}): {detalle}")
            else:
                lineas.append(f"• <b>{tipo}</b> — {equipo}: {detalle}")
        lineas.append("")

    if not proximos_euro.empty:
        lineas.append("📅 <b>Próximos partidos Euroliga</b>")
        for _, r in proximos_euro.iterrows():
            try:
                fecha_partido = datetime.strptime(r["date"], '%Y-%m-%d').strftime('%d/%m')
            except Exception:
                fecha_partido = r["date"]
            lineas.append(f"• {fecha_partido}: {r['home_team']} vs {r['away_team']}")
        lineas.append("")

    if not perlas_nba and not perlas_euro and proximos_euro.empty:
        lineas.append("Sin perlas destacadas ayer.")

    return "\n".join(lineas)


# ============================================================================
# ENTRY POINT
# ============================================================================

def buscar_perlas(fecha=None, enviar_telegram=True):
    """
    Función principal. Detecta perlas del día en 4 pasos:
    extracción → IA → verificación → formato.

    Args:
        fecha          : 'YYYY-MM-DD', por defecto ayer
        enviar_telegram: si True, envía resultado a Telegram

    Returns:
        dict con claves: nba, euroliga, proximos_euro, mensaje
    """
    if fecha is None:
        fecha = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    fecha_display = datetime.strptime(fecha, '%Y-%m-%d').strftime('%d/%m/%Y')
    print(f"\nBuscando perlas del {fecha_display}...")

    # ── PASO 1: Extraer datos ────────────────────────────────────────────────
    conn = get_connection()
    df_nba      = _extraer_stats_nba(fecha, conn)
    df_euro     = _extraer_stats_euro(fecha, conn)
    df_res_nba  = _extraer_resultados_nba(fecha, conn)
    df_res_euro = _extraer_resultados_euro(fecha, conn)
    conn.close()

    print(f"  NBA: {len(df_nba)} jugadores | Euro: {len(df_euro)} jugadores | "
          f"Resultados NBA: {len(df_res_nba)} | Euro: {len(df_res_euro)}")

    if df_nba.empty and df_euro.empty:
        print("  Sin datos para este día.")
        proximos_euro = obtener_proximos_partidos_euroliga()
        mensaje = formatear_perlas(fecha_display, [], [], proximos_euro)
        return {"nba": [], "euroliga": [], "proximos_euro": proximos_euro, "mensaje": mensaje}

    # ── PASO 2: Consultar IA ─────────────────────────────────────────────────
    try:
        datos_texto = _preparar_datos_para_ia(df_nba, df_euro, df_res_nba, df_res_euro)
        perlas_ia = _consultar_ia(fecha, datos_texto)
        print(f"  IA identificó {len(perlas_ia)} perlas candidatas")
    except Exception as e:
        print(f"  Error en consulta IA: {e}")
        perlas_ia = []

    # ── PASO 3: Verificar ────────────────────────────────────────────────────
    perlas_verificadas = [
        p for p in perlas_ia
        if _verificar_perla(p, df_nba, df_euro)
    ]
    print(f"  Verificadas: {len(perlas_verificadas)}/{len(perlas_ia)}")

    # ── Separar por liga ─────────────────────────────────────────────────────
    perlas_nba  = [p for p in perlas_verificadas if str(p.get('liga', '')).upper() == 'NBA']
    perlas_euro = [p for p in perlas_verificadas if str(p.get('liga', '')).upper() == 'EUROLIGA']

    proximos_euro = pd.DataFrame()
    if not perlas_euro:
        proximos_euro = obtener_proximos_partidos_euroliga()

    # ── PASO 4: Formatear ────────────────────────────────────────────────────
    mensaje = formatear_perlas(fecha_display, perlas_nba, perlas_euro, proximos_euro)
    print(mensaje)

    # ── Enviar a Telegram ────────────────────────────────────────────────────
    if enviar_telegram and (perlas_nba or perlas_euro or not proximos_euro.empty):
        try:
            from src.automation.bot_manager import enviar_mensaje
            enviar_mensaje(mensaje, parse_mode="HTML")
            print("Perlas enviadas a Telegram")
        except Exception as e:
            print(f"No se pudo enviar a Telegram: {e}")

    return {
        "nba": perlas_nba,
        "euroliga": perlas_euro,
        "proximos_euro": proximos_euro,
        "mensaje": mensaje
    }


# Alias para compatibilidad con master_sync.py
def buscar_perlas_nba(enviar_telegram=True):
    """Alias para compatibilidad con llamadas existentes en master_sync."""
    resultado = buscar_perlas(enviar_telegram=enviar_telegram)
    return resultado["mensaje"]


# ============================================================================
# EJECUCIÓN DIRECTA
# ============================================================================

if __name__ == "__main__":
    buscar_perlas()
