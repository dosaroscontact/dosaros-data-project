import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

try:
    response = client.models.generate_content(
        model="gemini-1.5-flash", 
        contents="Hola, soy el Proyecto Dos Aros. ¿Me recibes?"
    )
    print(f"Respuesta de Gemini: {response.text}")
except Exception as e:
    print(f"Error de conexión: {e}")