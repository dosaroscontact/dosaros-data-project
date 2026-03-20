import os
from google import genai
from dotenv import load_dotenv

# Cargamos el .env donde tienes tu GEMINI_API_KEY
load_dotenv()

# Forzamos al cliente a leer la clave del entorno
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

try:
    print("Enviando petición a Gemini 1.5 Flash...")
    # Usamos 1.5 Flash que es el estándar de oro para estabilidad en Free Tier
    response = client.models.generate_content(
        model="gemini-1.5-flash", 
        contents="Dame una frase corta sobre baloncesto."
    )
    print(f"\nRespuesta: {response.text}")
except Exception as e:
    print(f"\nError detallado:\n{e}")