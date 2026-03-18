import sys
import os

# Añadimos la ruta actual al path para que encuentre 'src'
sys.path.append(os.getcwd())

from src.automation.bot_manager import enviar_mensaje

print("🚀 Probando el sistema de mensajería de Dos Aros...")
res = enviar_mensaje("Prueba final: El bot manager funciona sin librerías pesadas.")

if res and res.get('ok'):
    print("✅ ¡Mensaje enviado con éxito!")
else:
    print(f"❌ Fallo en el envío. Respuesta: {res}")