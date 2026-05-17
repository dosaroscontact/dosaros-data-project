"""
================================================================================
INSIGHT_GENERATOR_V2.PY - Detección de Perlas con Scraping Web
================================================================================
Detecta perlas (insights destacados) de NBA y EuroLeague:
  • Primero: Busca en BD local (si hay partidos ayer)
  • Si no: Scrapeea webs de referencia + X/Twitter
  • Procesa con IA (Gemini/Groq) para extraer insights

Retorna lista de perlas con: tipo, jugador, equipo, detalle, peso
================================================================================
"""

import sqlite3
import pandas as pd
import json
import requests
from datetime import datetime, timedelta
from typing import List, Dict
import os
import logging

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración
DB_PATH = os.getenv('LOCAL_DB', '/mnt/nba_data/dosaros_local.db')

# Cuentas X/Twitter a monitorear
X_ACCOUNTS = [
    "UrbonasS",  # Donatas Urbonas (BasketNews/Euroliga)
    "ArisBarkas",  # Aris Barkas (Eurohoops)
    "chemadelucas",  # Chema de Lucas (rastreador español)
    "ShamsCharania",  # Shams (NBA insider)
    "BobbyMarks42",  # Bobby Marks (NBA salary cap)
    "StatMuse",  # StatMuse (NBA stats)
]

# Webs a scrapear
WEBS = {
    "basketnews": "https://www.basketnews.com/news",
    "eurohoops": "https://www.eurohoops.net",
    "encestando": "https://www.encestando.net",
}


# ============================================================================
# PASO 1: PERLAS DE BD LOCAL
# ============================================================================

def obtener_perlas_nba_bd(fecha: str = None) -> List[Dict]:
    """Obtiene perlas NBA de la BD local para ayer."""
    if fecha is None:
        fecha = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    perlas = []
    try:
        conn = sqlite3.connect(DB_PATH)
        
        # Cazadores de triples (7+ intentos, 60%+ accuracy)
        query_triples = """
            SELECT PLAYER_NAME, TEAM_ABBREVIATION, FG3M, FG3A, FG3_PCT, PTS
            FROM nba_players_games
            WHERE GAME_DATE = ? AND FG3A >= 7 AND FG3_PCT >= 0.50
            ORDER BY FG3M DESC
            LIMIT 3
        """
        df_triples = pd.read_sql_query(query_triples, conn, params=[fecha])
        
        for _, row in df_triples.iterrows():
            perlas.append({
                "tipo": "🎯 Cazador de Triples",
                "jugador": row["PLAYER_NAME"],
                "equipo": row["TEAM_ABBREVIATION"],
                "detalle": f"{int(row['FG3M'])}/{int(row['FG3A'])} triples ({row['FG3_PCT']:.0%}), {int(row['PTS'])} pts",
                "peso": 85,
                "fuente": "BD_NBA"
            })
        
        # Explosiones anotadoras (35+ pts)
        query_explosion = """
            SELECT PLAYER_NAME, TEAM_ABBREVIATION, PTS, REB, AST
            FROM nba_players_games
            WHERE GAME_DATE = ? AND PTS >= 35
            ORDER BY PTS DESC
            LIMIT 3
        """
        df_explosion = pd.read_sql_query(query_explosion, conn, params=[fecha])
        
        for _, row in df_explosion.iterrows():
            perlas.append({
                "tipo": "💥 Explosión Anotadora",
                "jugador": row["PLAYER_NAME"],
                "equipo": row["TEAM_ABBREVIATION"],
                "detalle": f"{int(row['PTS'])} puntos, {int(row['REB'])} rebotes, {int(row['AST'])} asistencias",
                "peso": 90,
                "fuente": "BD_NBA"
            })
        
        conn.close()
    except Exception as e:
        logger.warning(f"⚠️ Error obteniendo perlas NBA BD: {e}")
    
    return perlas


def obtener_perlas_euro_bd(fecha: str = None) -> List[Dict]:
    """Obtiene perlas Euroliga de la BD local para ayer."""
    if fecha is None:
        fecha = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    perlas = []
    try:
        conn = sqlite3.connect(DB_PATH)
        
        # Top performers Euroliga (20+ pts)
        query = """
            SELECT player_id, team_id, pts, reb, ast, game_id
            FROM euro_players_games
            WHERE game_id IN (
                SELECT game_id FROM euro_games WHERE date = ?
            )
            AND pts >= 20
            ORDER BY pts DESC
            LIMIT 3
        """
        df = pd.read_sql_query(query, conn, params=[fecha])
        
        for _, row in df.iterrows():
            perlas.append({
                "tipo": "🌍 Top Euroliga",
                "jugador": row["player_id"],
                "equipo": row["team_id"],
                "detalle": f"{int(row['pts'])} puntos, {int(row['reb'])} rebotes, {int(row['ast'])} asistencias",
                "peso": 80,
                "fuente": "BD_EURO"
            })
        
        conn.close()
    except Exception as e:
        logger.warning(f"⚠️ Error obteniendo perlas Euro BD: {e}")
    
    return perlas


# ============================================================================
# PASO 2: SCRAPING WEB (Fallback si no hay datos en BD)
# ============================================================================

def scrapear_basketnews() -> List[Dict]:
    """Scrapeea noticias recientes de BasketNews."""
    perlas = []
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        resp = requests.get(f"{WEBS['basketnews']}/feed/", headers=headers, timeout=10)
        if resp.status_code == 200:
            if "triple" in resp.text.lower() or "record" in resp.text.lower():
                perlas.append({
                    "tipo": "📰 BasketNews",
                    "jugador": None,
                    "equipo": None,
                    "detalle": "Noticia destacada de BasketNews (verificar manualmente)",
                    "peso": 50,
                    "fuente": "BASKETNEWS_WEB"
                })
    except Exception as e:
        logger.warning(f"⚠️ Error scrapear BasketNews: {e}")
    
    return perlas


def scrapear_x_twitter() -> List[Dict]:
    """Scrapeea tweets de cuentas clave (requiere API de X)."""
    perlas = []
    try:
        logger.info("ℹ️ X/Twitter scraping requiere API credentials (TODO)")
    except Exception as e:
        logger.warning(f"⚠️ Error scrapear X/Twitter: {e}")
    
    return perlas


# ============================================================================
# PASO 3: PROCESAMIENTO CON IA (api_manager)
# ============================================================================

def procesar_con_ia(perlas: List[Dict]) -> List[Dict]:
    """
    Procesa perlas con IA para mejorar descripción y peso.
    Usa api_manager para fallback automático entre Gemini, Groq, etc.
    """
    if not perlas:
        return perlas
    
    try:
        from src.utils.api_manager import consultar_llm
        
        perlas_texto = "\n".join([
            f"- {p['tipo']}: {p.get('jugador', 'N/A')} ({p.get('equipo', 'N/A')}) — {p['detalle']}"
            for p in perlas
        ])
        
        # IMPORTANTE: {{ y }} se escapan como {{{{ y }}}} en f-strings
        json_format = """{ "perlas": [ { "tipo": "tipo_original", "detalle": "descripción mejorada", "peso": "número_1_a_100", "estiloDoS_aros": "frase corta" } ] }"""
        
        prompt = f"""
Analiza estas perlas de baloncesto y devuelve JSON con mejoras:
{perlas_texto}

Devuelve SOLO JSON (sin markdown) con este formato aproximado:
{json_format}
"""
        
        respuesta = consultar_llm(prompt, modelo="gemini")
        
        try:
            respuesta_limpia = respuesta.replace('```json', '').replace('```', '').strip()
            datos_ia = json.loads(respuesta_limpia)
            
            for i, p_ia in enumerate(datos_ia.get("perlas", [])):
                if i < len(perlas):
                    perlas[i].update(p_ia)
        except json.JSONDecodeError:
            logger.warning("⚠️ No se pudo parsear respuesta IA, usando perlas originales")
    
    except Exception as e:
        logger.warning(f"⚠️ Error procesando con IA: {e}, usando perlas sin procesar")
    
    return perlas


# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def buscar_perlas_mejorado(fecha: str = None, enviar_telegram: bool = True) -> Dict:
    """
    Función mejorada: Busca perlas en BD → Fallback a webs → Procesa con IA.
    
    Args:
        fecha: 'YYYY-MM-DD', por defecto ayer
        enviar_telegram: si True, envía resultado a Telegram
    
    Returns:
        dict con perlas, mensaje formateado y fuentes
    """
    if fecha is None:
        fecha = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    fecha_display = datetime.strptime(fecha, '%Y-%m-%d').strftime('%d/%m/%Y')
    logger.info(f"\n🔍 Buscando perlas del {fecha_display}...")
    
    # PASO 1: Buscar en BD local
    perlas_nba_bd = obtener_perlas_nba_bd(fecha)
    perlas_euro_bd = obtener_perlas_euro_bd(fecha)
    perlas_todas = perlas_nba_bd + perlas_euro_bd
    
    # PASO 2: Si no hay perlas en BD → scrapear webs
    if not perlas_todas:
        logger.info("📰 Sin datos en BD, buscando en webs de referencia...")
        perlas_todas += scrapear_basketnews()
        perlas_todas += scrapear_x_twitter()
    
    # PASO 3: Procesar con IA para mejorar
    if perlas_todas:
        logger.info("🤖 Procesando perlas con IA...")
        perlas_todas = procesar_con_ia(perlas_todas)
    
    # PASO 4: Ordenar por peso y formatear
    perlas_todas = sorted(perlas_todas, key=lambda x: x.get("peso", 0), reverse=True)
    
    mensaje = formatear_mensaje_telegram(fecha_display, perlas_todas)
    
    logger.info(mensaje)
    
    # PASO 5: Enviar a Telegram
    if enviar_telegram and perlas_todas:
        try:
            from src.automation.bot_manager import enviar_mensaje
            enviar_mensaje(mensaje)
            logger.info("✅ Perlas enviadas a Telegram")
        except Exception as e:
            logger.error(f"⚠️ Error enviando a Telegram: {e}")
    
    return {
        "perlas": perlas_todas,
        "mensaje": mensaje,
        "fecha": fecha,
        "total": len(perlas_todas)
    }


def formatear_mensaje_telegram(fecha_display: str, perlas: List[Dict]) -> str:
    """Formatea perlas para Telegram con estilo Dos Aros."""
    lineas = [f"💎 *Perlas Dos Aros — {fecha_display}*\n"]
    
    for p in perlas[:5]:
        if p.get("jugador"):
            lineas.append(
                f"• *{p['tipo']}* — {p['jugador']} ({p['equipo']})\n"
                f"  {p['detalle']}"
            )
        else:
            lineas.append(f"• *{p['tipo']}*\n  {p['detalle']}")
    
    if not perlas:
        lineas.append("Sin perlas destacadas ayer.")
    
    return "\n".join(lineas)


if __name__ == "__main__":
    resultado = buscar_perlas_mejorado(enviar_telegram=False)
    print(f"\n✅ Total perlas encontradas: {resultado['total']}")
    print(resultado['mensaje'])