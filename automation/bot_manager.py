import requests
import logging

# Intentamos importar la configuración de forma robusta
try:
    from .config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
except (ImportError, ValueError):
    try:
        from automation.config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
    except ImportError:
        # Último recurso si se lanza desde la misma carpeta
        import config
        TELEGRAM_TOKEN = config.TELEGRAM_TOKEN
        TELEGRAM_CHAT_ID = config.TELEGRAM_CHAT_ID

def enviar_mensaje(texto):
    """Envía un mensaje de texto usando la API de Telegram vía requests."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": texto,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.json()
    except Exception as e:
        logging.error(f"Error en envío de Telegram: {e}")
        return None

def enviar_grafico(image_path, pie_de_foto):
    """Envía una imagen a Telegram."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    try:
        with open(image_path, 'rb') as photo:
            files = {'photo': photo}
            data = {
                "chat_id": TELEGRAM_CHAT_ID,
                "caption": pie_de_foto,
                "parse_mode": "Markdown"
            }
            response = requests.post(url, files=files, data=data, timeout=20)
            return response.json()
    except Exception as e:
        logging.error(f"Error enviando foto: {e}")
        return None