from google import genai
import os
from dotenv import load_dotenv

# Cargar configuración desde .env
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError(
        "ERROR: GEMINI_API_KEY no configurada.\n"
        "1. Copia .env.example a .env\n"
        "2. Añade tu clave: GEMINI_API_KEY=tu_clave_aqui\n"
        "3. Asegúrate de que .env está en .gitignore"
    )

client = genai.Client(api_key=API_KEY)

print("Modelos disponibles para tu clave:")
for m in client.models.list():
    print(f"- {m.name}")