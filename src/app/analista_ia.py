import google.generativeai as genai
import sqlite3
import pandas as pd
import os

# Configuración
API_KEY = "AIzaSyAnz9CXRL3Fyjjz8wWqH4lowmeAkeM_cy4"
DB_PATH = "/mnt/nba_data/dosaros_local.db"

genai.configure(api_key=API_KEY)

# Instrucciones para que Gemini sea un experto en tu base de datos
instruccion_sistema = """
Eres el motor SQL del Proyecto Dos Aros. 
Tu única función es traducir preguntas a SQL para SQLite.
Tabla: 'nba_games'
Columnas: SEASON_ID, GAME_DATE, TEAM_ABBREVIATION, WL, PTS, REB, AST, PLUS_MINUS.
Lógica de filtros:
- Temporada Regular: SEASON_ID LIKE '2%'
- Playoffs: SEASON_ID LIKE '4%'
- Año: El formato es 'X1987' (ejemplo: 21987 para regular de 1987).
Reglas: No uses YEAR(). Usa solo columnas existentes. Responde solo con el SQL.
"""

model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction=instruccion_sistema
)

def preguntar_a_gemini(pregunta):
    response = model.generate_content(pregunta)
    return response.text.replace("```sql", "").replace("```", "").strip()

def ejecutar_en_hdd(sql):
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(sql, conn)
        conn.close()
        return df
    except Exception as e:
        return f"Error en la base de datos: {e}"

if __name__ == "__main__":
    pregunta = "¿Cual es el promedio de puntos en temporada regular vs playoffs en 1987?"
    sql = preguntar_a_gemini(pregunta)
    print(f"SQL generado: {sql}")
    print("\n--- Resultado de la Investigación ---")
    print(ejecutar_en_hdd(sql))