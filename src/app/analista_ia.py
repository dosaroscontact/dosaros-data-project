import sqlite3
import pandas as pd
import os
from google import genai
from dotenv import load_dotenv

# Carga la clave desde el archivo oculto .env
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
DB_PATH = "/mnt/nba_data/dosaros_local.db"

client = genai.Client(api_key=API_KEY)
MODELO_ACTIVO = "gemini-flash-latest"

contexto_sql = """
Instrucciones: Eres experto en SQLite. Tabla: 'nba_games'.
Reglas: No uses YEAR(). Filtra año con SEASON_ID LIKE '%1987'.
Fase: Regular (LIKE '2%'), Playoffs (LIKE '4%').
Salida: Solo SQL plano.
"""

def preguntar_a_gemini(pregunta_usuario):
    prompt_final = f"{contexto_sql}\n\nPregunta: {pregunta_usuario}"
    try:
        response = client.models.generate_content(
            model=MODELO_ACTIVO,
            contents=prompt_final
        )
        return response.text.replace("```sql", "").replace("```", "").strip()
    except Exception as e:
        return f"Error API: {e}"

def ejecutar_en_hdd(sql):
    if "Error" in sql: return sql
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(sql, conn)
        conn.close()
        return df
    except Exception as e:
        return f"Error SQL: {e}"

if __name__ == "__main__":
    print(f"--- Laboratorio Dos Aros (Seguro) ---")
    pregunta = "¿Cual es el promedio de puntos en temporada regular vs playoffs en 1987?"
    sql = preguntar_a_gemini(pregunta)
    print(f"SQL: {sql}")
    print(ejecutar_en_hdd(sql))