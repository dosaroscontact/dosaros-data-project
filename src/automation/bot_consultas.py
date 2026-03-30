"""
================================================================================
BOT CONSULTAS - Proyecto Dos Aros
================================================================================
Listener de Telegram para consultas en lenguaje natural sobre la BD de baloncesto.

Flujo por mensaje:
  1. Escucha mensajes via getUpdates (long polling)
  2. La IA (Gemini) traduce la pregunta a SQL
  3. Ejecuta el SQL y devuelve los datos formateados
  4. Pregunta si generar imagen + tweet
  5. Si confirma, genera imagen con generar_imagen_perla y texto con Gemini
  6. Envía ambos a Telegram
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

APODOS COMUNES (mapeo a nombres reales):
- Shai = Gilgeous-Alexander
- Luka = Doncic
- Jokic = Jokic
- Giannis = Antetokounmpo
- LeBron = James
- Steph/Curry = Curry
- KD = Durant
- Kyrie = Irving
- Kawhi = Leonard
- Jimmy = Butler
- Jayson = Tatum
- Jaylen = Brown
- LaMelo = Ball
- Melo = Anthony
- Trae = Young
- Donovan/Mitchell = Mitchell
- Paul/PG = George
- AD = Davis
- Joel/Embiid = Embiid
- Devin/Booker = Booker
- Damian/Dame/Lillard = Lillard
- CJ = McCollum
- Bradley/Beal = Beal
- Scottie = Barnes
- Pascal = Siakam
- Fred = VanVleet
- DeMar = DeRozan
- Alex/Caruso = Caruso

Si el usuario menciona un apodo, usa el nombre real en tu SQL.

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
- La fecha de hoy es 2026-03-30

Cuando el usuario hace una pregunta, devuelves SIEMPRE un JSON con:
{
  "sql": "SELECT ...",
  "explicacion": "Lo que vas a buscar",
  "stat_clave": "PTS/REB/AST/etc",
  "tipo_perla": "descripcion corta del hallazgo"
}

Solo devuelves JSON, sin texto adicional ni bloques markdown.

IMPORTANTE: Siempre incluye TEAM_ABBREVIATION en el SELECT aunque sea una consulta
agregada con GROUP BY.
"""


# ============================================================================
# UTILIDADES
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

    # Intentar extraer equipo y dato principal de la primera fila
    equipo = "DEFAULT"
    dato_principal = ""

    if filas:
        primera = dict(zip(columnas, filas[0]))
        # Subtítulo: "Nombre Jugador — Tipo Perla Legible"
        tipo_legible = tipo_perla.replace('_', ' ').title()
        nombre_jugador = primera.get('PLAYER_NAME') or primera.get('player_name')
        subtitulo = f"{nombre_jugador} — {tipo_legible}" if nombre_jugador else tipo_legible
        subtitulo = subtitulo[:40]
        # Buscar columna de equipo: exacta primero, luego cualquier col con "team"
        for col in ('TEAM_ABBREVIATION', 'team_id', 'equipo'):
            if col in primera and primera[col]:
                equipo = str(primera[col]).upper()
                break
        if equipo == "DEFAULT":
            for col in columnas:
                if 'team' in col.lower() and primera.get(col):
                    equipo = str(primera[col]).upper()
                    break
        # Buscar valor de la stat clave
        for col in columnas:
            if col.upper() == stat_clave.upper() and primera[col] is not None:
                etiqueta = _normalizar_stat(stat_clave)
                dato_principal = f"{_fmt(primera[col])} {etiqueta}"
                break
        if not dato_principal and filas:
            for col, val in primera.items():
                try:
                    float(val)
                    etiqueta = _normalizar_stat(col)
                    dato_principal = f"{_fmt(val)} {etiqueta}"
                    break
                except (TypeError, ValueError):
                    continue

    return {
        "equipo":         equipo,
        "dato_principal": dato_principal,
        "subtitulo":      subtitulo,
        "contexto":       "",
        "fecha":          datetime.now().strftime('%d/%m/%Y'),
        "fuente":         "@dos_aros",
    }


# ============================================================================
# TELEGRAM — ENVÍO Y POLLING
# ============================================================================

def _enviar(texto, parse_mode="HTML"):
    """Envío directo sin depender de TELEGRAM_CHAT_ID global de bot_manager."""
    from src.automation.bot_manager import enviar_mensaje
    return enviar_mensaje(texto, parse_mode=parse_mode)


def _esperar_confirmacion(ultimo_id, timeout_seg=300):
    """
    Espera respuesta sí/no del usuario a partir de ultimo_id.
    Retorna (bool_confirmado, nuevo_ultimo_id).
    """
    url = f"{BASE_URL}/getUpdates"
    start = time.time()

    while (time.time() - start) < timeout_seg:
        try:
            res = requests.get(url, params={"offset": ultimo_id + 1}, timeout=15).json()
            if res.get("ok") and res.get("result"):
                for upd in res["result"]:
                    ultimo_id = upd["update_id"]
                    texto = upd.get("message", {}).get("text", "").lower().strip()
                    if texto in ("sí", "si", "s", "yes", "y"):
                        return True, ultimo_id
                    if texto in ("no", "n"):
                        return False, ultimo_id
        except Exception:
            pass
        time.sleep(3)

    print("  Timeout esperando confirmación.")
    return False, ultimo_id


# ============================================================================
# PROCESAMIENTO DE UN MENSAJE
# ============================================================================

def _procesar_mensaje(texto_usuario, ultimo_id):
    """
    Procesa una pregunta en lenguaje natural:
      1. IA → SQL
      2. Ejecuta SQL
      3. Envía resultado
      4. Pide confirmación para imagen + tweet
      5. Si confirma, genera y envía ambos

    Retorna el ultimo_id actualizado tras posible confirmación.
    """
    print(f"\n→ Consulta: {texto_usuario}")

    # ── 1. IA: pregunta → SQL ──────────────────────────────────────────────
    _enviar("🔍 Consultando datos...")
    ia_json = _consultar_ia(texto_usuario)

    if not ia_json or not ia_json.get('sql'):
        _enviar("No pude generar una consulta SQL para esa pregunta. ¿Puedes reformularla?")
        return ultimo_id

    sql         = ia_json['sql']
    explicacion = ia_json.get('explicacion', 'Resultados')
    print(f"  SQL: {sql}")

    # ── 2. Ejecutar SQL ────────────────────────────────────────────────────
    try:
        columnas, filas = _ejecutar_sql(sql)
    except Exception as e:
        print(f"  Error SQL: {e}")
        _enviar(f"Error ejecutando la consulta:\n<code>{e}</code>\n\n¿Puedes reformular la pregunta?")
        return ultimo_id

    # ── 3. Enviar resultado ────────────────────────────────────────────────
    resultado_txt = _formatear_resultado(columnas, filas, explicacion)
    _enviar(resultado_txt)

    if not filas:
        return ultimo_id

    # ── 4. Pedir confirmación ──────────────────────────────────────────────
    _enviar("¿Genero imagen y tweet con este dato? (sí/no)")
    confirmado, ultimo_id = _esperar_confirmacion(ultimo_id)

    if not confirmado:
        print("  Usuario no confirmó generación.")
        return ultimo_id

    # ── 5a. Generar tweet ──────────────────────────────────────────────────
    _enviar("⚙️ Generando imagen y tweet...")
    try:
        tipo_perla = ia_json.get('tipo_perla', texto_usuario[:40])
        tweet = _generar_tweet(texto_usuario, columnas, filas, tipo_perla)
        _enviar(f"🐦 <b>Tweet:</b>\n{tweet}")
    except Exception as e:
        print(f"  Error generando tweet: {e}")
        _enviar(f"No pude generar el tweet: {e}")

    # ── 5b. Generar imagen ─────────────────────────────────────────────────
    try:
        from src.processors.image_generator import generar_imagen_perla
        from src.automation.bot_manager import enviar_grafico

        perla_dict = _construir_perla_imagen(columnas, filas, ia_json, texto_usuario)
        path_imagen = generar_imagen_perla(perla_dict)
        caption_raw = tweet[:200] if tweet else tipo_perla
        caption_limpio = re.sub(r'[*_`~]', '', caption_raw)
        enviar_grafico(path_imagen, caption=caption_limpio)
        print("  Imagen enviada.")
    except Exception as e:
        print(f"  Error generando imagen: {e}")
        _enviar(f"No pude generar la imagen: {e}")

    return ultimo_id


# ============================================================================
# AVATAR — BD Y FORMATEO
# ============================================================================

def get_avatar_prompt(team_name=None):
    """Obtiene prompt de avatar por equipo o aleatorio desde avatar_prompts."""
    conn = get_connection()
    cursor = conn.cursor()
    if team_name:
        result = cursor.execute(
            """SELECT team_name, scene_type, prompt_text, avatar_url, logo_url
               FROM avatar_prompts
               WHERE LOWER(team_name) LIKE LOWER(?)
               LIMIT 1""",
            (f"%{team_name}%",),
        ).fetchone()
    else:
        result = cursor.execute(
            """SELECT team_name, scene_type, prompt_text, avatar_url, logo_url
               FROM avatar_prompts
               ORDER BY RANDOM()
               LIMIT 1"""
        ).fetchone()
    conn.close()
    return result


def get_today_avatars(limit=5):
    """Obtiene N prompts aleatorios."""
    conn = get_connection()
    cursor = conn.cursor()
    results = cursor.execute(
        """SELECT team_name, scene_type, prompt_text, avatar_url, logo_url
           FROM avatar_prompts
           ORDER BY RANDOM()
           LIMIT ?""",
        (limit,),
    ).fetchall()
    conn.close()
    return results


def _format_avatar_message(team_name, scene_type, prompt_text, avatar_url, logo_url):
    """Formatea mensaje de avatar para Telegram (HTML)."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    return (
        f"<b>🎨 DOS AROS - AVATAR GENERATOR</b>\n\n"
        f"<b>📍 Equipo:</b> {team_name}\n"
        f"<b>📊 Tipo:</b> {scene_type}\n"
        f"<b>⏱️ Generado:</b> {timestamp}\n\n"
        f"<b>🖼️ AVATAR REFERENCE:</b>\n{avatar_url}\n\n"
        f"<b>📌 LOGO:</b>\n{logo_url}\n\n"
        f"<b>📝 PROMPT PARA GOOGLE IMAGEFX:</b>\n\n"
        f"<code>{prompt_text}</code>\n\n"
        f"<b>✅ INSTRUCCIONES:</b>\n"
        f"1. Copia el prompt completo\n"
        f"2. Abre Google ImageFX (imagegeneration.dev)\n"
        f"3. Pega el prompt + adjunta avatar URL como imagen de referencia\n"
        f"4. Genera imagen\n"
        f"5. Descarga y publica en redes"
    )


# ============================================================================
# AVATAR — PROCESADORES DE COMANDOS
# ============================================================================

def _procesar_comando_avatar_prompt(team_name: str):
    """Procesa /avatar_prompt [equipo]"""
    if not team_name:
        _enviar("❌ Uso: /avatar_prompt [equipo]\nEj: /avatar_prompt Lakers")
        return
    print(f"\n→ Avatar prompt: {team_name}")
    result = get_avatar_prompt(team_name)
    if result:
        _enviar(_format_avatar_message(*result))
    else:
        _enviar(f"❌ Equipo '{team_name}' no encontrado.\nIntenta con el nombre completo (ej: Los Angeles Lakers)")


def _procesar_comando_avatar_random():
    """Procesa /avatar_random"""
    print("\n→ Avatar random")
    result = get_avatar_prompt()
    if result:
        _enviar(_format_avatar_message(*result))
    else:
        _enviar("❌ No hay prompts disponibles")


def _procesar_comando_avatar_today():
    """Procesa /avatar_today — envía 5 prompts aleatorios"""
    print("\n→ Avatar today (5 prompts)")
    results = get_today_avatars(5)
    if not results:
        _enviar("❌ No hay prompts disponibles")
        return
    _enviar(f"📋 <b>5 Avatares del día:</b>\n{len(results)} prompts listos. Enviando...")
    for i, result in enumerate(results, 1):
        _enviar(f"<b>Avatar {i}/5:</b>\n\n" + _format_avatar_message(*result))
        time.sleep(0.5)


# ============================================================================
# COMANDO /video
# ============================================================================

def _procesar_comando_video(instruccion: str):
    """
    Genera un video MP4 a partir de una instrucción en lenguaje natural
    y lo envía de vuelta al chat de Telegram.

    Args:
        instruccion: Texto tras /video (ej. "Top 3 tiradores 3P NBA esta semana")
    """
    print(f"\n→ Comando /video: {instruccion}")

    _enviar(
        f"⏳ <b>Generando video...</b>\n"
        f"<b>Instrucción:</b> {instruccion[:120]}\n\n"
        f"<i>Puede tardar 2-5 minutos.</i>"
    )

    try:
        from src.integrations.video_generator import VideoGenerator
        gen = VideoGenerator()
        video_path = gen.generar_video(instruccion, usuario_id="telegram")
    except Exception as e:
        print(f"  Error inicializando VideoGenerator: {e}")
        _enviar(f"❌ Error iniciando generador de video:\n<code>{str(e)[:200]}</code>")
        return

    if not video_path:
        _enviar(
            "❌ <b>No se pudo generar el video.</b>\n\n"
            "<i>Posibles causas:</i>\n"
            "• Editor Pro Max no instalado\n"
            "• Error en APIs (Claude/Gemini)\n"
            "• Base de datos sin datos para ese periodo\n\n"
            "Intenta reformular la instrucción."
        )
        return

    try:
        from src.automation.bot_manager import enviar_video
        size_mb = Path(video_path).stat().st_size / 1_048_576
        enviar_video(
            path=video_path,
            caption=(
                f"✅ <b>Video generado</b>\n"
                f"<b>Instrucción:</b> {instruccion[:100]}\n"
                f"<b>Tamaño:</b> {size_mb:.1f} MB"
            ),
        )
        print(f"  Video enviado: {video_path} ({size_mb:.1f} MB)")
    except Exception as e:
        print(f"  Error enviando video: {e}")
        _enviar(f"✅ Video generado pero no se pudo enviar:\n<code>{str(e)[:200]}</code>")


# ============================================================================
# BUCLE PRINCIPAL
# ============================================================================

def escuchar_y_procesar():
    """Bucle infinito que escucha mensajes de Telegram y procesa consultas."""
    url = f"{BASE_URL}/getUpdates"

    # Descartar mensajes anteriores al arranque
    try:
        res = requests.get(url, timeout=10).json()
        ultimo_id = 0
        if res.get("ok") and res.get("result"):
            ultimo_id = res["result"][-1]["update_id"]
        print(f"  Arranque: ignorando mensajes hasta update_id={ultimo_id}")
    except Exception:
        ultimo_id = 0

    while True:
        try:
            res = requests.get(
                url,
                params={"offset": ultimo_id + 1, "timeout": 30},
                timeout=40
            ).json()

            if not res.get("ok"):
                time.sleep(5)
                continue

            for upd in res.get("result", []):
                ultimo_id = upd["update_id"]
                mensaje = upd.get("message", {})
                texto = mensaje.get("text", "").strip()

                if not texto:
                    continue

                lower = texto.lower()

                # Comando /video o /v
                if lower.startswith("/video ") or lower.startswith("/v "):
                    instruccion = texto.split(" ", 1)[1].strip()
                    if instruccion:
                        _procesar_comando_video(instruccion)
                    continue

                # Comandos avatar
                if lower.startswith("/avatar_prompt"):
                    team_name = texto[len("/avatar_prompt"):].strip()
                    _procesar_comando_avatar_prompt(team_name)
                    continue

                if lower in ("/avatar_random", "/avatar"):
                    _procesar_comando_avatar_random()
                    continue

                if lower in ("/avatar_today", "/avatars"):
                    _procesar_comando_avatar_today()
                    continue

                if texto.startswith("/"):
                    continue  # ignorar otros comandos

                ultimo_id = _procesar_mensaje(texto, ultimo_id)

        except requests.exceptions.Timeout:
            continue  # long polling normal, reintentar
        except Exception as e:
            print(f"Error en bucle principal: {e}")
            time.sleep(10)


# ============================================================================
# EJECUCIÓN DIRECTA
# ============================================================================

if __name__ == "__main__":
    print("Bot consultas Dos Aros arrancado...")
    escuchar_y_procesar()
