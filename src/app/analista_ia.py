import sqlite3
import pandas as pd
from google import genai

# 1. CONFIGURACIÓN
API_KEY = "AIzaSyAnz9CXRL3Fyjjz8wWqH4lowmeAkeM_cy4" 
DB_PATH = "/mnt/nba_data/dosaros_local.db"

client = genai.Client(api_key=API_KEY)
# Usamos el 1.5-flash porque el 2.0 suele tener el límite 0 en Europa más a menudo
MODELO_ACTIVO = "gemini-1.5-flash" 

# 3. EL "CEREBRO" (Instrucciones que pegaremos al principio de cada pregunta)
instrucciones = """
Instrucciones: Eres un experto en SQLite para la tabla 'nba_games'.
Columnas: SEASON_ID, GAME_DATE, PTS, WL, REB, AST.
Reglas:
- No uses YEAR(), usa strftime.
- Regular Season: SEASON_ID LIKE '2%'
- Playoffs: SEASON_ID LIKE '4%'
- Año 1987: SEASON_ID LIKE '%1987'
- Devuelve SOLO el código SQL plano.
"""

def preguntar_a_gemini(pregunta_usuario):
    # Metemos las instrucciones dentro del contenido para evitar el error 400
    prompt_completo = f"{instrucciones}\n\nPregunta: {pregunta_usuario}"
    
    try:
        response = client.models.generate_content(
            model=MODELO_ACTIVO,
            contents=prompt_completo
        )
        # Limpieza básica
        sql = response.text.replace("```sql", "").replace("```", "").strip()
        return sql
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
        return f"Error SQL: {e}\nQuery: {sql}"

if __name__ == "__main__":
    print(f"--- Laboratorio Dos Aros (Motor: {MODELO_ACTIVO}) ---")
    pregunta = "¿Cual es el promedio de puntos en temporada regular vs playoffs en 1987?"
    sql = preguntar_a_gemini(pregunta)
    print(f"SQL Generado: {sql}")
    print(ejecutar_en_hdd(sql))