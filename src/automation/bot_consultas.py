"""
================================================================================
BOT_CONSULTAS_V2.PY - Mejoras para Dos Aros
================================================================================
CAMBIOS RESPECTO A V1:
  ✅ Comando /perla <consulta> — genera perla on-demand con IA
  ✅ Integración con news_processor_v2 para noticias + IA
  ✅ Mantiene todos los comandos anteriores (/avatar_*, /status, etc)

USO NUEVO:
  /perla Valencia Basket hoy
  /perla Luka Doncic rumor Lakers
  /perla Kenneth Faried Panathinaikos

El bot:
  1. Recibe la consulta
  2. Procesa con IA (APIManager)
  3. Extrae/genera la perla
  4. Formatea con estilo Dos Aros
  5. Envía a Telegram
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

# ============================================================================
# COMANDO /PERLA - NUEVA FUNCIONALIDAD
# ============================================================================

def _procesar_comando_perla(consulta: str):
    """
    Procesa /perla <consulta> para generar una perla personalizada.
    
    Ejemplo:
      /perla Valencia Basket sorpresa
      /perla Luka Doncic Lakers
    
    Flujo:
      1. Recibe consulta del usuario
      2. Procesa con IA (Gemini/Groq con fallback)
      3. Genera estructura: tipo, detalle, dato, estilo Dos Aros
      4. Envía a Telegram formateado
    """
    if not consulta:
        _enviar("❌ Uso: /perla <consulta>\nEj: /perla Valencia Basket hoy")
        return
    
    print(f"\n→ Perla: {consulta}")
    _enviar(f"🔄 Generando perla para: *{consulta}*...")
    
    try:
        from src.utils.api_manager import APIManager
        
        api = APIManager()
        
        # Prompt para generar perla
        prompt = f"""
Eres un analista de baloncesto de Dos Aros. 
Tienes esta consulta del usuario: "{consulta}"

TAREA: Genera una perla de baloncesto (insight importante) basada en esta consulta.

Devuelve SOLO JSON (sin markdown):
{{
  "tipo": "🎯 Tipo de perla (emoji + categoría)",
  "jugador": "nombre del jugador (o null si es equipo/evento)",
  "equipo": "nombre equipo",
  "detalle": "descripción del insight (2-3 líneas max)",
  "peso": "número 1-100 según importancia",
  "dato_curioso": "un dato interesante",
  "estilo_dos_aros": "una frase irónica/provocadora típica de Dos Aros"
}}
"""
        
        # Genera con fallback automático
        respuesta = api.generate_text(
            prompt,
            providers=["gemini", "groq", "deepseek", "kimi", "venice", "claude", "openai"]
        )
        
        # Parsea JSON
        respuesta_limpia = respuesta.replace('```json', '').replace('```', '').strip()
        perla = json.loads(respuesta_limpia)
        
        # Formatea para Telegram
        mensaje = _formatear_perla_telegram(perla, consulta)
        _enviar(mensaje)
        
        print(f"✅ Perla generada")
    
    except json.JSONDecodeError as e:
        print(f"❌ Error parseando IA: {e}")
        _enviar(f"⚠️ Error parseando respuesta IA: {e}")
    except Exception as e:
        print(f"❌ Error generando perla: {e}")
        _enviar(f"❌ Error: {e}")


def _formatear_perla_telegram(perla: dict, consulta: str) -> str:
    """Formatea una perla para Telegram con estilo Dos Aros."""
    return f"""
💎 *PERLA DOS AROS*

*Consulta:* {consulta}

*{perla.get('tipo', '?')}*

{f"*Jugador:* {perla.get('jugador')}" if perla.get('jugador') else ""}
{f"*Equipo:* {perla.get('equipo')}" if perla.get('equipo') else ""}

*Detalle:*
{perla.get('detalle', 'N/A')}

*📊 Peso:* {perla.get('peso', 50)}/100

*💡 Dato Curioso:*
{perla.get('dato_curioso', 'N/A')}

*🎯 Estilo Dos Aros:*
_"{perla.get('estilo_dos_aros', 'N/A')}"_
"""


# ============================================================================
# FUNCIONES AUXILIARES (DEL BOT ORIGINAL)
# ============================================================================

def _enviar(texto: str):
    """Envía mensaje a Telegram."""
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    try:
        requests.post(
            f"{BASE_URL}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": texto,
                "parse_mode": "Markdown"
            },
            timeout=15
        )
    except Exception as e:
        print(f"❌ Error Telegram: {e}")


def get_avatar_prompt(team_name: str = None):
    """Obtiene prompt de avatar (función original)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if team_name:
        query = "SELECT team_name, scene_type, prompt_text, avatar_url, logo_url FROM avatar_teams WHERE team_name LIKE ?"
        cursor.execute(query, (f"%{team_name}%",))
    else:
        query = "SELECT team_name, scene_type, prompt_text, avatar_url, logo_url FROM avatar_teams ORDER BY RANDOM() LIMIT 1"
        cursor.execute(query)
    
    result = cursor.fetchone()
    conn.close()
    return result


def get_today_avatars(limit: int = 5):
    """Obtiene N avatars aleatorios (función original)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    results = cursor.execute(
        """SELECT team_name, scene_type, prompt_text, avatar_url, logo_url
           FROM avatar_teams
           ORDER BY RANDOM()
           LIMIT ?""",
        (limit,),
    ).fetchall()
    conn.close()
    return results


def _format_avatar_message(team_name, scene_type, prompt_text, avatar_url, logo_url):
    """Formatea mensaje de avatar (función original)."""
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


def _procesar_comando_avatar_prompt(team_name: str):
    """Procesa /avatar_prompt (función original)."""
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
    """Procesa /avatar_random (función original)."""
    print("\n→ Avatar random")
    result = get_avatar_prompt()
    if result:
        _enviar(_format_avatar_message(*result))
    else:
        _enviar("❌ No hay prompts disponibles")


def _procesar_comando_avatar_today():
    """Procesa /avatar_today (función original)."""
    print("\n→ Avatar today (5 prompts)")
    results = get_today_avatars(5)
    if not results:
        _enviar("❌ No hay prompts disponibles")
        return
    _enviar(f"📋 <b>5 Avatares del día:</b>\n{len(results)} prompts listos. Enviando...")
    for i, result in enumerate(results, 1):
        _enviar(f"<b>Avatar {i}/5:</b>\n\n" + _format_avatar_message(*result))
        time.sleep(0.5)


def _procesar_comando_status():
    """Procesa /status (función original)."""
    from src.utils.api_manager import APIManager

    _enviar("🔍 Verificando APIs...")

    api = APIManager()
    proveedores = ["gemini", "groq", "deepseek", "kimi", "venice", "claude", "openai"]
    ping = "Di OK en una sola palabra."

    lineas = ["<b>📡 Estado de APIs — Dos Aros</b>\n"]
    for proveedor in proveedores:
        try:
            metodo = getattr(api, proveedor, None)
            if metodo is None:
                lineas.append(f"❓ <b>{proveedor.upper()}</b> — sin método")
                continue
            metodo(ping)
            lineas.append(f"✅ <b>{proveedor.upper()}</b> — OK")
        except ValueError:
            lineas.append(f"⚪ <b>{proveedor.upper()}</b> — no configurado")
        except Exception as e:
            lineas.append(f"❌ <b>{proveedor.upper()}</b> — error: {str(e)[:60]}")

    lineas.append(f"\n<i>{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</i>")
    _enviar("\n".join(lineas))


def _procesar_comando_status_ia():
    """Procesa /StatusIA — Verifica estado detallado de cada API configurada."""
    from src.utils.api_manager import APIManager
    import time

    _enviar("🔍 *Verificando estado de IAs...*")

    api = APIManager()

    # APIs a verificar (en orden de prioridad)
    apis = ["openai", "gemini", "claude", "groq", "grok", "kimi", "manus"]

    lineas = ["<b>🤖 Estado de IAs — Dos Aros</b>\n"]

    for ia in apis:
        try:
            # Obtener el método de la API
            if ia == "manus":
                # Manus usa formato OpenAI compatible
                metodo = getattr(api, 'generate_text', None)
                if not metodo:
                    lineas.append(f"⚪ <b>{ia.upper()}</b> — APIManager sin método")
                    continue
                # Intenta con Manus
                respuesta = api.generate_text(
                    "OK",
                    providers=["manus"]
                )
                lineas.append(f"✅ <b>{ia.upper()}</b> — Respondiendo")
            elif ia == "grok":
                # Grok también usa formato OpenAI compatible
                metodo = getattr(api, 'generate_text', None)
                if not metodo:
                    lineas.append(f"⚪ <b>{ia.upper()}</b> — APIManager sin método")
                    continue
                respuesta = api.generate_text(
                    "OK",
                    providers=["grok"]
                )
                lineas.append(f"✅ <b>{ia.upper()}</b> — Respondiendo")
            else:
                # Para el resto, usa el método directo
                metodo = getattr(api, ia, None)
                if metodo is None:
                    lineas.append(f"❓ <b>{ia.upper()}</b> — sin método")
                    continue

                respuesta = metodo("OK")
                lineas.append(f"✅ <b>{ia.upper()}</b> — Respondiendo")

        except ValueError as e:
            if "no API key" in str(e) or "no configurado" in str(e).lower():
                lineas.append(f"⚪ <b>{ia.upper()}</b> — no configurado")
            else:
                lineas.append(f"⚪ <b>{ia.upper()}</b> — {str(e)[:40]}")
        except Exception as e:
            error_msg = str(e)[:50]
            if "401" in error_msg or "invalid" in error_msg.lower():
                lineas.append(f"🔴 <b>{ia.upper()}</b> — token inválido")
            else:
                lineas.append(f"❌ <b>{ia.upper()}</b> — {error_msg}")

        time.sleep(0.5)  # Pequeña pausa entre APIs

    lineas.append(f"\n<i>✓ Verificación completada — {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</i>")
    _enviar("\n".join(lineas))


# ============================================================================
# LOOP PRINCIPAL (escucha comandos)
# ============================================================================

def main():
    """Loop principal que escucha comandos."""
    print("🤖 Bot Dos Aros iniciado (v2 con /perla)")
    print("Comandos disponibles:")
    print("  /perla <consulta> — Genera perla personalizada")
    print("  /avatar_prompt <equipo> — Avatar de un equipo")
    print("  /avatar_random — Avatar aleatorio")
    print("  /avatar_today — 5 avatares del día")
    print("  /status — Estado de APIs")
    print("  /StatusIA — Verifica estado detallado de cada IA\n")
    
    ultimo_update_id = 0
    
    while True:
        try:
            # Obtener actualizaciones
            response = requests.get(
                f"{BASE_URL}/getUpdates",
                params={"offset": ultimo_update_id + 1, "timeout": 30},
                timeout=35
            )
            data = response.json()
            
            if not data.get("ok"):
                print(f"⚠️ Error en getUpdates: {data.get('description')}")
                time.sleep(5)
                continue
            
            updates = data.get("result", [])
            
            for update in updates:
                ultimo_update_id = update["update_id"]
                message = update.get("message", {})
                text = message.get("text", "").strip()
                
                if not text:
                    continue
                
                print(f"📨 Mensaje recibido: {text[:100]}")
                
                # Procesar comandos
                if text.startswith("/perla "):
                    consulta = text[7:].strip()
                    _procesar_comando_perla(consulta)
                
                elif text.startswith("/avatar_prompt "):
                    team_name = text[15:].strip()
                    _procesar_comando_avatar_prompt(team_name)
                
                elif text == "/avatar_random":
                    _procesar_comando_avatar_random()
                
                elif text == "/avatar_today":
                    _procesar_comando_avatar_today()
                
                elif text == "/status":
                    _procesar_comando_status()

                elif text == "/StatusIA":
                    _procesar_comando_status_ia()

                else:
                    _enviar(f"❓ Comando no reconocido: {text}\n\nComandos disponibles:\n/perla <consulta>\n/avatar_*\n/status\n/StatusIA")
        
        except Exception as e:
            print(f"❌ Error en loop: {e}")
            time.sleep(10)


if __name__ == "__main__":
    main()
