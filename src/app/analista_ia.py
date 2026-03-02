import sqlite3
import pandas as pd
from google import genai
from google.genai import types

# 1. CONFIGURACIÓN
API_KEY = "AIzaSyAnz9CXRL3Fyjjz8wWqH4lowmeAkeM_cy4" 
DB_PATH = "/mnt/nba_data/dosaros_local.db"

# Inicializamos el cliente forzando la versión v1 para evitar el 404
client = genai.Client(
    api_key=API_KEY,
    http_options={'api_version': 'v1'}
)

# Usamos el 2.0 Flash que es el que tu clave reconoce
MODELO_ACTIVO = "gemini-2.0-flash" 

instruccion_sistema = """
Eres el motor SQL del Proyecto Dos Aros. 
Tu única función es traducir preguntas a SQL para SQLite.
Tabla: 'nba_games'
Columnas: SEASON_ID, GAME_DATE, TEAM_ABBREVIATION, WL, PTS, REB, AST, PLUS_MINUS.

REGLAS:
- No uses YEAR(), usa strftime.
- Temporada Regular: SEASON_ID LIKE '2%'
- Playoffs: SEASON_ID LIKE '4%'
- Año: SEASON_ID LIKE '%1987'
- Responde SOLO con el SQL plano.
"""

def preguntar_a_gemini(pregunta_usuario):
    try:
        response = client.models.generate_content(
            model=MODELO_ACTIVO,
            contents=pregunta_usuario,
            config=types.GenerateContentConfig(
                system_instruction=instruccion_sistema,
                temperature=0.0
            )
        )
        sql = response.text.replace("```sql", "").replace("```", "").strip()
        return sql
    except Exception as e:
        if "429" in str(e):
            return "ERROR_CUOTA: Tu proyecto de API tiene límite 0. Mira el paso 2 abajo."
        return f"Error en la petición: {e}"

def ejecutar_en_hdd(sql):
    if "ERROR" in sql: return sql
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(sql, conn)
        conn.close()
        return df
    except Exception as e:
        return f"Error SQL: {e}\nQuery: {sql}"

if __name__ == "__main__":
    print(f"--- Laboratorio Dos Aros (Motor: {MODELO_ACTIVO}) ---")
    pregunta = "¿Cuál es el promedio de puntos en temporada regular vs playoffs en 1987?"
    sql = preguntar_a_gemini(pregunta)
    print(f"SQL Generado: {sql}")
    print("\n--- Resultado de la Investigación ---")
    print(ejecutar_en_hdd(sql))