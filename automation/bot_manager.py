import time
import requests
import logging

# Configuración (Asegúrate de tener estas variables en tu config o entorno)
from .config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

def enviar_mensaje(texto):
    """Envía notificaciones de texto plano."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": texto, "parse_mode": "Markdown"}
    try:
        res = requests.post(url, json=payload, timeout=10)
        return res.json()
    except Exception as e:
        logging.error(f"Error enviando mensaje: {e}")
        return None

def enviar_grafico(image_path, pie_de_foto):
    """Envía el post de Instagram generado en la Pi."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    try:
        with open(image_path, 'rb') as photo:
            files = {'photo': photo}
            data = {"chat_id": TELEGRAM_CHAT_ID, "caption": pie_de_foto, "parse_mode": "Markdown"}
            res = requests.post(url, files=files, data=data, timeout=20)
            return res.json()
    except Exception as e:
        logging.error(f"Error enviando gráfico: {e}")
        return None

def escuchar_confirmacion(timeout_minutos=5):
    """Limpia mensajes viejos y espera una confirmación nueva."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
    
    res_inicio = requests.get(url, timeout=10).json()
    ultimo_id = 0
    if res_inicio.get("ok") and res_inicio.get("result"):
        ultimo_id = res_inicio["result"][-1]["update_id"]

    start_time = time.time()
    print(f"👂 Esperando confirmación (ID > {ultimo_id})...")
    
    while (time.time() - start_time) < (timeout_minutos * 60):
        try:
            res = requests.get(url, params={"offset": ultimo_id + 1}, timeout=10).json()
            if res.get("ok") and res.get("result"):
                for update in res["result"]:
                    ultimo_id = update["update_id"]
                    texto = update.get("message", {}).get("text", "").lower()
                    if "si" in texto or "sí" in texto:
                        return True
            time.sleep(5)
        except Exception:
            time.sleep(10)
    return False