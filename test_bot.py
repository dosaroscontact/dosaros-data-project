# test_bot.py
from src.automation.bot_manager import enviar_mensaje

print("Enviando mensaje de prueba...")
resultado = enviar_mensaje("🚀 Prueba de conexión: El sistema Dos Aros está listo.")
print(f"Respuesta de Telegram: {resultado}")