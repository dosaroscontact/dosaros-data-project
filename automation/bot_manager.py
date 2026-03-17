import requests
import logging
# Importación relativa para que funcione desde cualquier sitio
try:
    from .config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
except ImportError:
    from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

def enviar_mensaje(texto):
    """Envía un mensaje de texto simple."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": texto, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, data=data)
        return response.json()
    except Exception as e:
        logging.error(f"Error enviando Telegram: {e}")
        return None

def enviar_grafico(image_path, pie_de_foto):
    """Envía una imagen con pie de foto."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    try:
        with open(image_path, 'rb') as photo:
            files = {'photo': photo}
            data = {"chat_id": TELEGRAM_CHAT_ID, "caption": pie_de_foto, "parse_mode": "Markdown"}
            response = requests.post(url, files=files, data=data)
            return response.json()
    except Exception as e:
        logging.error(f"Error enviando foto Telegram: {e}")
        return None