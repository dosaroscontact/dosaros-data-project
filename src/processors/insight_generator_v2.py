"""
================================================================================
GENERADOR DE PERLAS v2 — Proyecto Dos Aros (24 categorías + cooldown 21 días)
================================================================================
Cambios vs v1:
  - 24 categorías (9 NBA + 7 Euro + 8 nuevas)
  - Tabla published_insights (tracking + cooldown)
  - Lógica: generar → validar cooldown → registrar → retornar

Entry point: buscar_perlas(fecha, enviar_telegram)
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

# ============================================================================
# CATEGORÍAS (24 total)
# ============================================================================

CATEGORIAS_24 = {
    # NBA (9)
    "explosion_anotadora_nba": "Jugador NBA con actuación anotadora excepcional (>25pts)",
    "triple_doble_nba": "NBA triple-doble o estadística combinada extrema",
    "defensa_standout_nba": "NBA robo/tapón/defensa destacada",
    "banco_explosivo_nba": "NBA equipo con banco anotador fuerte",
    "rookie_standout_nba": "NBA rookie con actuación notable",
    "paliza_nba": "NBA victoria con diferencia >20 puntos",
    "comeback_nba": "NBA remontada o partido cerrado",
    "eficiencia_trio_nba": "NBA 3 jugadores combinan eficiencia extrema",
    "record_rareza_nba": "NBA stat rara/histórica para jugador/equipo",

    # EuroLeague (7)
    "explosion_anotadora_euro": "Euroliga jugador con >20pts performance",
    "defensa_intenso_euro": "Euroliga intensidad defensiva extrema",
    "batalla_rebotes_euro": "Euroliga control de rebotes decisivo",
    "sorpresa_euro": "Euroliga equipo o jugador contra pronóstico",
    "joven_talento_euro": "Euroliga talento emergente (sub-23 años)",
    "veterano_clasico_euro": "Euroliga veterano con actuación clásica",
    "teamplay_euro": "Euroliga jugada colectiva / asistencias",

    # Análisis (8)
    "ofensiva_equipo_analisis": "Análisis ofensivo: equipo rompió esquema",
    "defensiva_equipo_analisis": "Análisis defensivo: equipo fue impermeable",
    "comp_historica_nba": "NBA comparativa histórica (vs same day/season)",
    "comp_historica_euro": "Euro comparativa histórica (vs años previos)",
    "proyeccion_playoff": "Análisis: implicancia para playoffs",
    "tanking_race": "NBA análisis tanking/draft lottery implications",
    "cruces_playoff": "Euro análisis: cruces playoff posibles",
    "stat_sorprendente": "Dato estadístico contra expectativas (sin liga)"
}

# ============================================================================
# DATABASE HELPERS
# ============================================================================

def get_connection():
    return sqlite3.connect(DB_PATH)


def _init_published_insights_table(conn):
    """Asegura que la tabla existe (usa schema existente en Pi)."""
    # Tabla ya existe en Pi con columnas: id, category, insight_text, published_date, league
    # No necesitamos crear, solo verificar que existe
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM published_insights LIMIT 1")
        cursor.fetchone()
    except sqlite3.OperationalError:
        # Si no existe, crearla
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS published_insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                insight_text TEXT,
                published_date DATE DEFAULT CURRENT_DATE,
                league TEXT,
                UNIQUE(category, published_date)
            )
        """)
        conn.commit()


def _puede_generar_categoria(conn, categoria):
    """
    Verifica si una categoría está disponible (fuera de cooldown 21 días).
    Usa schema actual: category, published_date
    Retorna (puede_generar, proxima_fecha_disponible)
    """
    cursor = conn.cursor()
    cursor.execute("""
        SELECT published_date
        FROM published_insights
        WHERE category = ?
        ORDER BY published_date DESC
        LIMIT 1
    """, (categoria,))
    resultado = cursor.fetchone()

    if not resultado:
        # Nunca se ha generado
        return (True, None)

    ultima_pub = datetime.strptime(resultado[0], '%Y-%m-%d').date()
    proxima_disponible = ultima_pub + timedelta(days=21)
    hoy = datetime.now().date()

    if hoy >= proxima_disponible:
        return (True, None)
    else:
        return (False, proxima_disponible)


def _registrar_perla_publicada(conn, categoria, fecha_publicacion, insight_text="", league=""):
    """
    Registra que una categoría fue publicada.
    Usa schema actual: category, insight_text, published_date, league
    """
    cursor = conn.cursor()
    fecha_pub = datetime.strptime(fecha_publicacion, '%Y-%m-%d').date()

    cursor.execute("""
        INSERT OR IGNORE INTO published_insights
        (category, insight_text, published_date, league)
        VALUES (?, ?, ?, ?)
    """, (categoria, insight_text, fecha_pub.isoformat(), league))
    conn.commit()


def _obtener_categorias_disponibles(conn, fecha):
    """
    Retorna lista de categorías disponibles (fuera de cooldown).
    """
    disponibles = []
    for categoria in CATEGORIAS_24.keys():
        puede, _ = _puede_generar_categoria(conn, categoria)
        if puede:
            disponibles.append(categoria)
    return disponibles


# ============================================================================
# EXTRACCIÓN DE DATOS (igual que v1)
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
    """Extrae resultados NBA del día desde nba_games."""
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
# CONSULTA IA (igual que v1)
# ============================================================================

def _preparar_datos_para_ia(df_nba, df_euro, df_res_nba, df_res_euro, categorias_disponibles):
    """Serializa datos a texto CSV para el prompt, mencionando categorías disponibles."""
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


def _consultar_ia(fecha, datos_texto, categorias_disponibles):
    """Envía datos a IA pidiendo perlas de categorías disponibles."""
    from src.utils.api_manager import APIManager
    api = APIManager()

    cats_str = ", ".join(categorias_disponibles[:15])  # Top 15 categorías disponibles

    prompt = f"""Eres analista de baloncesto de Dos Aros. Dados estos datos del {fecha}:

{datos_texto}

CATEGORÍAS DISPONIBLES HOY (sin repetir últimos 21 días):
{cats_str}

Identifica 2-3 actuaciones destacadas que encajen en estas categorías.
Para cada una devuelve un JSON con:
- jugador (nombre exacto o null si es perla de equipo)
- equipo (código exacto)
- liga (NBA o Euroliga)
- categoria (UNA de las disponibles arriba)
- stat_clave (PTS, REB, AST, STL, BLK, FG_PCT o null)
- valor (número exacto o null)
- razon (por qué, máx 20 palabras)

Responde SOLO con JSON array, sin texto adicional."""

    respuesta = api.generate_text(prompt=prompt, providers=['gemini', 'groq'])
    print(f"  Respuesta IA ({len(respuesta)} chars)")
    return _parsear_json_ia(respuesta)


# ============================================================================
# VERIFICACIÓN (igual que v1)
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
    """Verifica que el dato exacto existe en la DB."""
    liga = str(perla.get('liga', '')).upper()
    jugador = perla.get('jugador')
    stat = str(perla.get('stat_clave', '')).upper() if perla.get('stat_clave') else None
    valor_ia = perla.get('valor')

    # Perlas sin valor concreto: dejar pasar
    if jugador is None or valor_ia is None or not stat:
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
                print(f"  [DESCARTADA] '{jugador}' no en datos NBA")
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
                print(f"  [DESCARTADA] '{jugador}' no en datos Euro")
                return False
            actual = float(df_euro.loc[mask, col].max())
            if abs(actual - valor_ia) > 1:
                print(f"  [DESCARTADA] {jugador} {stat}: IA={valor_ia}, DB={actual}")
                return False
        return True

    return True


# ============================================================================
# FORMATO (igual que v1)
# ============================================================================

def obtener_proximos_partidos_euroliga(n=5):
    """Obtiene próximos partidos de Euroliga."""
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
    """Formatea las perlas en mensaje HTML para Telegram."""
    lineas = [f"💎 <b>Perlas Dos Aros — {fecha_display}</b>\n"]

    if perlas_nba:
        lineas.append("🏀 <b>NBA</b>")
        for p in perlas_nba[:5]:
            jugador = p.get('jugador') or p.get('equipo', '')
            equipo = p.get('equipo', '')
            categoria = p.get('categoria', 'perla').replace('_', ' ').title()
            stat = p.get('stat_clave', '')
            valor = p.get('valor', '')
            razon = p.get('razon', '')
            detalle = f"{stat} {valor} — {razon}" if stat and valor else razon
            if jugador and jugador != equipo:
                lineas.append(f"• <b>{categoria}</b> — {jugador} ({equipo}): {detalle}")
            else:
                lineas.append(f"• <b>{categoria}</b> — {equipo}: {detalle}")
        lineas.append("")

    if perlas_euro:
        lineas.append("🌍 <b>Euroliga</b>")
        for p in perlas_euro[:5]:
            jugador = p.get('jugador') or p.get('equipo', '')
            equipo = p.get('equipo', '')
            categoria = p.get('categoria', 'perla').replace('_', ' ').title()
            stat = p.get('stat_clave', '')
            valor = p.get('valor', '')
            razon = p.get('razon', '')
            detalle = f"{stat} {valor} — {razon}" if stat and valor else razon
            if jugador and jugador != equipo:
                lineas.append(f"• <b>{categoria}</b> — {jugador} ({equipo}): {detalle}")
            else:
                lineas.append(f"• <b>{categoria}</b> — {equipo}: {detalle}")
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
# ENTRY POINT (NUEVO: con lógica de cooldown)
# ============================================================================

def buscar_perlas(fecha=None, enviar_telegram=True):
    """
    Función principal con sistema de cooldown.

    Flujo:
    1. Extraer datos del día
    2. Obtener categorías disponibles (sin cooldown activo)
    3. Consultar IA (restringido a categorías disponibles)
    4. Verificar perlas
    5. Registrar categorías usadas con next_available_date
    6. Formatear y enviar

    Args:
        fecha          : 'YYYY-MM-DD', por defecto ayer
        enviar_telegram: si True, envía resultado a Telegram

    Returns:
        dict con claves: nba, euroliga, proximos_euro, mensaje
    """
    if fecha is None:
        fecha = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    fecha_display = datetime.strptime(fecha, '%Y-%m-%d').strftime('%d/%m/%Y')
    print(f"\n[PERLAS v2] Buscando del {fecha_display}...")

    conn = get_connection()
    _init_published_insights_table(conn)

    # ── PASO 1: Extraer datos ────────────────────────────────────────────────
    df_nba      = _extraer_stats_nba(fecha, conn)
    df_euro     = _extraer_stats_euro(fecha, conn)
    df_res_nba  = _extraer_resultados_nba(fecha, conn)
    df_res_euro = _extraer_resultados_euro(fecha, conn)

    print(f"  NBA: {len(df_nba)} jugadores | Euro: {len(df_euro)} | "
          f"Resultados NBA: {len(df_res_nba)} | Euro: {len(df_res_euro)}")

    if df_nba.empty and df_euro.empty:
        print("  Sin datos para este día.")
        proximos_euro = obtener_proximos_partidos_euroliga()
        mensaje = formatear_perlas(fecha_display, [], [], proximos_euro)
        conn.close()
        return {"nba": [], "euroliga": [], "proximos_euro": proximos_euro, "mensaje": mensaje}

    # ── PASO 2: Obtener categorías disponibles ───────────────────────────────
    categorias_disponibles = _obtener_categorias_disponibles(conn, fecha)
    print(f"  Categorías disponibles: {len(categorias_disponibles)}/24")
    if not categorias_disponibles:
        print("  ⚠️  Todas las categorías están en cooldown. Esperando 21 días.")
        proximos_euro = obtener_proximos_partidos_euroliga()
        mensaje = "⚠️ Todas las categorías están en cooldown. Vuelve mañana."
        conn.close()
        return {"nba": [], "euroliga": [], "proximos_euro": proximos_euro, "mensaje": mensaje}

    # ── PASO 3: Consultar IA (restringido a categorías disponibles) ─────────
    try:
        datos_texto = _preparar_datos_para_ia(df_nba, df_euro, df_res_nba, df_res_euro, categorias_disponibles)
        perlas_ia = _consultar_ia(fecha, datos_texto, categorias_disponibles)
        print(f"  IA identificó {len(perlas_ia)} perlas candidatas")
    except Exception as e:
        print(f"  Error en consulta IA: {e}")
        perlas_ia = []

    # ── PASO 4: Verificar ────────────────────────────────────────────────────
    perlas_verificadas = [
        p for p in perlas_ia
        if _verificar_perla(p, df_nba, df_euro)
    ]
    print(f"  Verificadas: {len(perlas_verificadas)}/{len(perlas_ia)}")

    # ── PASO 5: Registrar categorías usadas (cooldown) ──────────────────────
    categorias_usadas = set()
    for p in perlas_verificadas:
        cat = p.get('categoria')
        if cat and cat not in categorias_usadas:
            liga = p.get('liga', '')
            razon = p.get('razon', '')
            _registrar_perla_publicada(conn, cat, fecha, razon, liga)
            categorias_usadas.add(cat)
            print(f"  ✓ Categoría '{cat}' registrada (próxima: {(datetime.strptime(fecha, '%Y-%m-%d') + timedelta(days=21)).strftime('%d/%m')})")

    # ── PASO 6: Separar por liga ─────────────────────────────────────────────
    perlas_nba  = [p for p in perlas_verificadas if str(p.get('liga', '')).upper() == 'NBA']
    perlas_euro = [p for p in perlas_verificadas if str(p.get('liga', '')).upper() == 'EUROLIGA']

    proximos_euro = pd.DataFrame()
    if not perlas_euro:
        proximos_euro = obtener_proximos_partidos_euroliga()

    # ── PASO 7: Formatear ────────────────────────────────────────────────────
    mensaje = formatear_perlas(fecha_display, perlas_nba, perlas_euro, proximos_euro)
    print(mensaje)

    # ── Enviar a Telegram ────────────────────────────────────────────────────
    if enviar_telegram and (perlas_nba or perlas_euro or not proximos_euro.empty):
        try:
            from src.automation.bot_manager import enviar_mensaje
            enviar_mensaje(mensaje, parse_mode="HTML")
            print("✓ Perlas enviadas a Telegram")
        except Exception as e:
            print(f"✗ No se pudo enviar a Telegram: {e}")

    conn.close()

    return {
        "nba": perlas_nba,
        "euroliga": perlas_euro,
        "proximos_euro": proximos_euro,
        "mensaje": mensaje
    }


# Alias para compatibilidad con master_sync.py
def buscar_perlas_nba(enviar_telegram=True):
    """Alias para compatibilidad con llamadas existentes."""
    resultado = buscar_perlas(enviar_telegram=enviar_telegram)
    return resultado["mensaje"]


# ============================================================================
# EJECUCIÓN DIRECTA
# ============================================================================

if __name__ == "__main__":
    buscar_perlas()