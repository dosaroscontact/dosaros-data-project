import requests
import logging
from .config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

def enviar_mensaje(texto):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": texto, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, data=data)
        return response.json()
    except Exception as e:
        logging.error(f"Error enviando Telegram: {e}")

def enviar_grafico(image_path, pie_de_foto):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    files = {'photo': open(image_path, 'rb')}
    data = {"chat_id": TELEGRAM_CHAT_ID, "caption": pie_de_foto, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, files=files, data=data)
        return response.json()
    except Exception as e:
        logging.error(f"Error enviando foto Telegram: {e}")