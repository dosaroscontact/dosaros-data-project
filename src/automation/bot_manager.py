"""
================================================================================
BOT MANAGER - Proyecto Dos Aros
================================================================================
Gestiona la comunicación con Telegram.
Funciones principales:
  - enviar_mensaje: envía texto al chat de control
  - enviar_grafico: envía imagen con caption
  - escuchar_confirmacion: espera "sí" del usuario antes de ejecutar acción
================================================================================
"""

import time
import requests
import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"


# ============================================================================
# ENVIAR MENSAJE DE TEXTO
# ============================================================================

def enviar_mensaje(texto: str, chat_id: str = None, parse_mode: str = "Markdown"):
    """
    Envía un mensaje de texto a Telegram.

    Args:
        texto: Texto del mensaje (soporta Markdown)
        chat_id: ID del chat destino (por defecto usa TELEGRAM_CHAT_ID del .env)
        parse_mode: Formato del texto ('Markdown' o 'HTML')

    Returns:
        dict: Respuesta de la API de Telegram
    """
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ TELEGRAM_TOKEN o TELEGRAM_CHAT_ID no configurados en .env")
        return None

    destino = chat_id or TELEGRAM_CHAT_ID

    try:
        r = requests.post(
            f"{BASE_URL}/sendMessage",
            json={
                "chat_id": destino,
                "text": texto,
                "parse_mode": parse_mode
            },
            timeout=15
        )
        result = r.json()
        if not result.get("ok"):
            print(f"⚠️ Error Telegram: {result.get('description')}")
        return result
    except Exception as e:
        print(f"❌ Error enviando mensaje Telegram: {e}")
        return None


# ============================================================================
# ENVIAR IMAGEN / GRÁFICO
# ============================================================================

def enviar_grafico(imagen, caption: str = "", chat_id: str = None):
    """
    Envía una imagen a Telegram.

    Args:
        imagen: URL de la imagen o path local al archivo
        caption: Texto que acompaña la imagen
        chat_id: ID del chat destino

    Returns:
        dict: Respuesta de la API de Telegram
    """
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ TELEGRAM_TOKEN o TELEGRAM_CHAT_ID no configurados en .env")
        return None

    destino = chat_id or TELEGRAM_CHAT_ID

    try:
        # Si es una URL
        if isinstance(imagen, str) and imagen.startswith("http"):
            r = requests.post(
                f"{BASE_URL}/sendPhoto",
                json={
                    "chat_id": destino,
                    "photo": imagen,
                    "caption": caption,
                    "parse_mode": "Markdown"
                },
                timeout=30
            )
        # Si es un archivo local
        else:
            with open(imagen, "rb") as f:
                r = requests.post(
                    f"{BASE_URL}/sendPhoto",
                    data={
                        "chat_id": destino,
                        "caption": caption,
                        "parse_mode": "Markdown"
                    },
                    files={"photo": f},
                    timeout=30
                )

        result = r.json()
        if not result.get("ok"):
            print(f"⚠️ Error Telegram foto: {result.get('description')}")
        return result
    except Exception as e:
        print(f"❌ Error enviando gráfico Telegram: {e}")
        return None


# ============================================================================
# ENVIAR DOCUMENTO / ARCHIVO
# ============================================================================

def enviar_documento(path: str, caption: str = "", chat_id: str = None):
    """
    Envía un archivo (PDF, CSV, etc.) a Telegram.

    Args:
        path: Path local al archivo
        caption: Texto que acompaña el archivo
        chat_id: ID del chat destino
    """
    destino = chat_id or TELEGRAM_CHAT_ID

    try:
        with open(path, "rb") as f:
            r = requests.post(
                f"{BASE_URL}/sendDocument",
                data={"chat_id": destino, "caption": caption},
                files={"document": f},
                timeout=30
            )
        return r.json()
    except Exception as e:
        print(f"❌ Error enviando documento Telegram: {e}")
        return None


# ============================================================================
# ESCUCHAR CONFIRMACIÓN
# ============================================================================

def escuchar_confirmacion(timeout_minutos=5):
    """
    Limpia mensajes viejos y espera una confirmación nueva del usuario.

    Args:
        timeout_minutos: Tiempo máximo de espera

    Returns:
        bool: True si el usuario responde "sí", False si timeout
    """
    url = f"{BASE_URL}/getUpdates"

    # Limpieza inicial: ignorar mensajes anteriores
    res_inicio = requests.get(url, timeout=10).json()
    ultimo_id = 0
    if res_inicio.get("ok") and res_inicio.get("result"):
        ultimo_id = res_inicio["result"][-1]["update_id"]

    start_time = time.time()
    print(f"👂 Esperando confirmación (timeout: {timeout_minutos} min)...")

    while (time.time() - start_time) < (timeout_minutos * 60):
        try:
            res = requests.get(
                url,
                params={"offset": ultimo_id + 1},
                timeout=10
            ).json()

            if res.get("ok") and res.get("result"):
                for update in res["result"]:
                    ultimo_id = update["update_id"]
                    texto = update.get("message", {}).get("text", "").lower()
                    if "si" in texto or "sí" in texto:
                        return True
            time.sleep(5)
        except Exception:
            time.sleep(10)

    print("⏱️ Timeout esperando confirmación")
    return False


# ============================================================================
# ENVIAR VIDEO
# ============================================================================

def enviar_video(path: str, caption: str = "", chat_id: str = None):
    """
    Envía un archivo de video MP4 a Telegram.

    Args:
        path:     Path local al archivo MP4
        caption:  Texto que acompaña el video
        chat_id:  ID del chat destino (usa TELEGRAM_CHAT_ID por defecto)
    """
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ TELEGRAM_TOKEN o TELEGRAM_CHAT_ID no configurados en .env")
        return None

    destino = chat_id or TELEGRAM_CHAT_ID

    try:
        with open(path, "rb") as f:
            r = requests.post(
                f"{BASE_URL}/sendVideo",
                data={
                    "chat_id":           destino,
                    "caption":           caption,
                    "parse_mode":        "HTML",
                    "supports_streaming": "true",
                },
                files={"video": f},
                timeout=120,
            )
        result = r.json()
        if not result.get("ok"):
            print(f"⚠️ Error Telegram video: {result.get('description')}")
        return result
    except Exception as e:
        print(f"❌ Error enviando video Telegram: {e}")
        return None


# ============================================================================
# EJECUCIÓN DIRECTA (TEST)
# ============================================================================

if __name__ == "__main__":
    print("🧪 Test bot_manager...")
    print(f"Token configurado: {'✅' if TELEGRAM_TOKEN else '❌'}")
    print(f"Chat ID configurado: {'✅' if TELEGRAM_CHAT_ID else '❌'}")

    resultado = enviar_mensaje("🧪 *Test Dos Aros* — bot_manager funcionando correctamente.")
    if resultado and resultado.get("ok"):
        print("✅ Mensaje enviado correctamente")
    else:
        print(f"❌ Error: {resultado}")