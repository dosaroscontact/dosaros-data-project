from google import genai
import os

client = genai.Client(api_key="AIzaSyAnz9CXRL3Fyjjz8wWqH4lowmeAkeM_cy4")

print("Modelos disponibles para tu clave:")
for m in client.models.list():
    print(f"- {m.name}")