import sqlite3
import pandas as pd
from google import genai

# 1. CONFIGURACIÓN
API_KEY = "AIzaSyAnz9CXRL3Fyjjz8wWqH4lowmeAkeM_cy4" 
DB_PATH = "/mnt/nba_data/dosaros_local.db"

# Inicializamos el cliente de forma estándar
client = genai.Client(api_key=API_KEY)

# Usamos el alias que aparece en tu lista para evitar el 404
MODELO_ACTIVO = "gemini-flash-latest" 

# 2. INSTRUCCIONES INTEGRADAS
# Al ponerlas aquí, evitamos el error 400 (systemInstruction no encontrado)
contexto_sql = """
Instrucciones Técnicas:
Eres un experto en SQL para SQLite. Tu tabla es 'nba_games'.
Columnas: SEASON_ID, GAME_DATE, TEAM_ABBREVIATION, WL, PTS, REB, AST, PLUS_MINUS.

Reglas Críticas:
1. No uses la función YEAR(). Para filtrar años usa: SEASON_ID LIKE '%1987'.
2. Temporada Regular: SEASON_ID LIKE '2%'.
3. Playoffs: SEASON_ID LIKE '4%'.
4. Responde ÚNICAMENTE con el código SQL plano, sin explicaciones ni markdown.
"""

def preguntar_a_gemini(pregunta_usuario):
    """Envía instrucciones + pregunta en un solo bloque para máxima compatibilidad."""
    prompt_final = f"{contexto_sql}\n\nPregunta: {pregunta_usuario}"
    
    try:
        response = client.models.generate_content(
            model=MODELO_ACTIVO,
            contents=prompt_final
        )
        # Limpieza de etiquetas si el modelo las incluye
        sql = response.text.replace("```sql", "").replace("```", "").strip()
        return sql
    except Exception as e:
        return f"Error API: {e}"

def ejecutar_en_hdd(sql):
    """Lanza la consulta contra el disco duro externo."""
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
    pregunta = "¿Cuál es el promedio de puntos en temporada regular vs playoffs en 1987?"
    
    sql = preguntar_a_gemini(pregunta)
    print(f"SQL Generado: {sql}")
    
    resultado = ejecutar_en_hdd(sql)
    print("\n--- Resultado de la Investigación ---")
    print(resultado)