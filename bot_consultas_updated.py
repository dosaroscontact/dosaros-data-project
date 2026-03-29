"""
================================================================================
BOT CONSULTAS - Proyecto Dos Aros (ACTUALIZADO CON AVATARES)
================================================================================
Listener de Telegram con:
  - Consultas en lenguaje natural (SQL)
  - Generación de tweets e imágenes
  - Comando /video para Remotion
  - Comandos de avatares: /avatar_prompt, /avatar_random, /avatar_today
================================================================================
"""

import json
import re
import sqlite3
import os
import time
import requests
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DB_PATH        = os.getenv("LOCAL_DB", "/mnt/nba_data/dosaros_local.db")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
BASE_URL       = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

SYSTEM_PROMPT = """Eres un analista de baloncesto NBA y Euroliga de Dos Aros.
Tienes acceso a una BD SQLite con estas tablas:

- nba_players_games: SEASON_ID, PLAYER_ID, PLAYER_NAME, TEAM_ID, TEAM_ABBREVIATION,
  TEAM_NAME, GAME_ID, GAME_DATE, MATCHUP, WL, MIN, FGM, FGA, FG_PCT, FG3M, FG3A,
  FG3_PCT, FTM, FTA, FT_PCT, OREB, DREB, REB, AST, STL, BLK, TOV, PF, PTS,
  PLUS_MINUS, FANTASY_PTS
- euro_players_games: game_id, player_id, team_id, pts, reb, ast
- nba_games: SEASON_ID, TEAM_ID, TEAM_ABBREVIATION, TEAM_NAME, GAME_ID, GAME_DATE,
  MATCHUP, WL, MIN, PTS, FGM, FGA, FG_PCT, FG3M, FG3A, FG3_PCT, FTM, FTA, FT_PCT,
  OREB, DREB, REB, AST, STL, BLK, TOV, PF, PLUS_MINUS
- euro_games: game_id, date, home_team, away_team, score_home, score_away

Reglas SQL:
- Usa LIKE sobre SEASON_ID en lugar de YEAR() para filtrar por temporada
- GAME_DATE en nba_players_games y nba_games tiene formato YYYY-MM-DD

Cuando el usuario hace una pregunta, devuelves SIEMPRE un JSON con:
{
  "sql": "SELECT ...",
  "explicacion": "Lo que vas a buscar",
  "stat_clave": "PTS/REB/AST/etc",
  "tipo_perla": "descripcion corta del hallazgo"
}
Solo devuelves JSON, sin texto adicional ni bloques markdown.

IMPORTANTE: Siempre incluye TEAM_ABBREVIATION en el SELECT aunque sea una consulta
agregada con GROUP BY. Ejemplo correcto: SELECT PLAYER_NAME, TEAM_ABBREVIATION,
SUM(REB) as total FROM nba_players_games GROUP BY PLAYER_NAME, TEAM_ABBREVIATION
ORDER BY total DESC LIMIT 1"""


# ============================================================================
# UTILIDADES GENERALES
# ============================================================================

def get_connection():
    return sqlite3.connect(DB_PATH)


def _parsear_json_ia(texto):
    """Extrae el JSON de la respuesta de la IA."""
    if not texto:
        return None
    texto = re.sub(r'```(?:json)?\s*', '', texto).strip().rstrip('`').strip()
    match = re.search(r'\{.*\}', texto, re.DOTALL)
    if match:
        texto = match.group(0)
    try:
        return json.loads(texto)
    except json.JSONDecodeError as e:
        print(f"Error parseando JSON de IA: {e}")
        return None


def _enviar(texto, parse_mode="HTML"):
    """Envío directo sin depender de TELEGRAM_CHAT_ID global de bot_manager."""
    from src.automation.bot_manager import enviar_mensaje
    return enviar_mensaje(texto, parse_mode=parse_mode)


# ============================================================================
# FUNCIONES AVATAR
# ============================================================================

def get_avatar_prompt(team_name=None):
    """Obtiene prompt de avatar por equipo o aleatorio"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if team_name:
        # Prompt específico
        result = cursor.execute('''
            SELECT team_name, scene_type, prompt_text, avatar_url, logo_url
            FROM avatar_prompts
            WHERE LOWER(team_name) LIKE LOWER(?)
            LIMIT 1
        ''', (f'%{team_name}%',)).fetchone()
    else:
        # Aleatorio
        result = cursor.execute('''
            SELECT team_name, scene_type, prompt_text, avatar_url, logo_url
            FROM avatar_prompts
            ORDER BY RANDOM()
            LIMIT 1
        ''').fetchone()
    
    conn.close()
    return result


def get_today_avatars(limit=5):
    """Obtiene N prompts aleatorios"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    results = cursor.execute('''
        SELECT team_name, scene_type, prompt_text, avatar_url, logo_url
        FROM avatar_prompts
        ORDER BY RANDOM()
        LIMIT ?
    ''', (limit,)).fetchall()
    
    conn.close()
    return results


def format_avatar_message(team_name, scene_type, prompt_text, avatar_url, logo_url):
    """Formatea mensaje de avatar para Telegram"""
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    message = f"""
<b>🎨 DOS AROS - AVATAR GENERATOR</b>

<b>📍 Equipo:</b> {team_name}
<b>📊 Tipo:</b> {scene_type}
<b>⏱️ Generado:</b> {timestamp}

<b>🖼️ AVATAR REFERENCE:</b>
{avatar_url}

<b>📌 LOGO:</b>
{logo_url}

<b>📝 PROMPT PARA GOOGLE IMAGEFX:</b>

<code>{prompt_text}</code>

<b>✅ INSTRUCCIONES:</b>
1. Copia el prompt completo
2. Abre Google ImageFX (imagegeneration.dev)
3. Pega el prompt + adjunta avatar URL como imagen de referencia
4. Genera imagen
5. Descarga y publica en redes
"""
    return message


def _procesar_comando_avatar_prompt(team_name: str):
    """Procesa /avatar_prompt [team]"""
    if not team_name:
        _enviar("❌ Uso: /avatar_prompt [equipo]\nEj: /avatar_prompt Lakers")
        return
    
    print(f"\n→ Avatar prompt: {team_name}")
    result = get_avatar_prompt(team_name)
    
    if result:
        team, scene_type, prompt_text, avatar_url, logo_url = result
        message = format_avatar_message(team, scene_type, prompt_text, avatar_url, logo_url)
        _enviar(message)
    else:
        _enviar(f"❌ Equipo '{team_name}' no encontrado.\n\nIntenta con el nombre completo (ej: Los Angeles Lakers)")


def _procesar_comando_avatar_random():
    """Procesa /avatar_random"""
    print("\n→ Avatar random")
    result = get_avatar_prompt()
    
    if result:
        team, scene_type, prompt_text, avatar_url, logo_url = result
        message = format_avatar_message(team, scene_type, prompt_text, avatar_url, logo_url)
        _enviar(message)
    else:
        _enviar("❌ No hay prompts disponibles")


def _procesar_comando_avatar_today():
    """Procesa /avatar_today"""
    print("\n→ Avatar today (5 prompts)")
    results = get_today_avatars(5)
    
    if not results:
        _enviar("❌ No hay prompts disponibles")
        return
    
    _enviar(f"📋 <b>5 Avatares del día:</b>\n\n{len(results)} prompts listos para generar.\n\nEnviando...")
    
    for i, result in enumerate(results, 1):
        team, scene_type, prompt_text, avatar_url, logo_url = result
        message = f"<b>Avatar {i}/5:</b>\n\n" + format_avatar_message(team, scene_type, prompt_text, avatar_url, logo_url)
        _enviar(message)
        time.sleep(0.5)  # Pequeño delay entre mensajes


# ============================================================================
# RESTO DEL BOT (ORIGINAL)
# ============================================================================

def _consultar_ia(pregunta):
    """Envía la pregunta a Gemini y recibe SQL + metadata como JSON."""
    from src.utils.api_manager import APIManager
    api = APIManager()
    prompt = f"{SYSTEM_PROMPT}\n\nPregunta del usuario: {pregunta}"
    respuesta = api.generate_text(prompt=prompt, providers=['gemini', 'groq'])
    print(f"  Respuesta IA: {respuesta[:200]}")
    return _parsear_json_ia(respuesta)


def _ejecutar_sql(sql):
    """Ejecuta el SQL y devuelve (columnas, filas) o lanza excepción."""
    conn = get_connection()
    try:
        cursor = conn.execute(sql)
        columnas = [d[0] for d in cursor.description]
        filas = cursor.fetchmany(20)  # máx 20 filas
        return columnas, filas
    finally:
        conn.close()


def _formatear_resultado(columnas, filas, explicacion):
    """Convierte columnas + filas en texto legible para Telegram (HTML)."""
    if not filas:
        return f"<b>{explicacion}</b>\n\nSin resultados para esta consulta."

    lineas = [f"<b>{explicacion}</b>\n"]
    # Cabecera
    lineas.append(" | ".join(columnas))
    lineas.append("─" * 40)
    for fila in filas:
        lineas.append(" | ".join(str(v) if v is not None else "—" for v in fila))

    if len(filas) == 20:
        lineas.append("\n<i>(mostrando primeras 20 filas)</i>")

    return "\n".join(lineas)


def _generar_tweet(pregunta, columnas, filas, tipo_perla):
    """Pide a Gemini un tweet de 280 chars con el hallazgo."""
    from src.utils.api_manager import APIManager
    api = APIManager()

    datos_txt = " | ".join(columnas) + "\n"
    datos_txt += "\n".join(" | ".join(str(v) for v in f) for f in filas[:5])

    prompt = f"""Eres el redactor de Dos Aros (@dos_aros), cuenta de análisis NBA y Euroliga.
Escribe UN tweet de máximo 280 caracteres sobre este hallazgo de datos:

Hallazgo: {tipo_perla}
Pregunta original: {pregunta}
Datos:
{datos_txt}

El tweet debe ser directo, con dato concreto, sin hashtags genéricos.
Devuelve solo el texto del tweet, sin comillas."""

    return api.generate_text(prompt=prompt, providers=['gemini', 'groq'])


def _construir_perla_imagen(columnas, filas, ia_json, pregunta):
    """Construye el dict que espera generar_imagen_perla."""
    stat_clave = ia_json.get('stat_clave', '')
    tipo_perla = ia_json.get('tipo_perla', pregunta[:40])

    def _normalizar_stat(nombre):
        n = nombre.lower()
        if 'point' in n or 'pts' in n:   return 'PTS'
        if 'rebound' in n or 'reb' in n: return 'REB'
        if 'assist' in n or 'ast' in n:  return 'AST'
        return nombre[:6].upper()

    def _fmt(val):
        try:
            f = float(val)
            return int(f) if f == int(f) else round(f, 2)
        except (TypeError, ValueError):
            return val