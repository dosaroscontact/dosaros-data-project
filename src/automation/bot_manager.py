import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Tu centro de control en la Pi
def enviar_a_revision(imagen_path, pie_de_foto):
    # El bot te envía la imagen generada por la Pi a tu móvil
    keyboard = [
        [InlineKeyboardButton("✅ Publicar en X/IG", callback_data='publish'),
         InlineKeyboardButton("❌ Descartar", callback_data='discard')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # Aquí iría el envío a tu ID de Telegram
    pass

# Si pulsas publicar, la Pi dispara hacia las APIs de redes sociales