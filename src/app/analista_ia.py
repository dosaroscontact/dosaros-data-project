import sqlite3
import pandas as pd
from google import genai
from google.genai import types

# 1. CONFIGURACIÓN DEL LABORATORIO
API_KEY = "AIzaSyAnz9CXRL3Fyjjz8wWqH4lowmeAkeM_cy4" 
DB_PATH = "/mnt/nba_data/dosaros_local.db"

# Inicializamos el cliente con el modelo más avanzado de tu lista
client = genai.Client(api_key=API_KEY)
MODELO_ACTIVO = "gemini-2.0-flash" 

# 2. DEFINICIÓN DE LA "GEMA" (Instrucciones maestras)
# Aquí es donde le explicamos a la IA cómo es tu mundo de datos
instruccion_sistema = """
Eres el motor de investigación del Proyecto Dos Aros. 
Tu misión es traducir preguntas de lenguaje natural a SQL para SQLite.

DATOS DISPONIBLES (Tabla 'nba_games'):
- SEASON_ID: Identificador de temporada. 
  * '2' + año (ej: '21987') para Temporada Regular.
  * '4' + año (ej: '41987') para Playoffs.
- GAME_DATE: Fecha del partido.
- PTS: Puntos anotados.
- PLUS_MINUS: Diferencial de puntos.
- WL: Resultado (W/L).

REGLAS DE ORO:
1. No inventes columnas. Usa solo las mencionadas.
2. PROHIBIDO usar la función YEAR(). Para filtrar por año usa SEASON_ID LIKE '%1987'.
3. Responde ÚNICAMENTE con el código SQL plano, sin explicaciones ni markdown.
"""

def preguntar_a_gemini(pregunta_usuario):
    """Envía la pregunta a la Gema y extrae el SQL."""
    try:
        response = client.models.generate_content(
            model=MODELO_ACTIVO,
            contents=pregunta_usuario,
            config=types.GenerateContentConfig(
                system_instruction=instruccion_sistema,
                temperature=0.0  # Creatividad cero para evitar errores
            )
        )
        # Limpiamos el resultado por si Gemini añade formato markdown
        sql = response.text.replace("```sql", "").replace("```", "").strip()
        return sql
    except Exception as e:
        return f"Error en la petición: {e}"

def ejecutar_en_hdd(sql):
    """Lanza la consulta contra el disco duro externo."""
    if "Error" in sql: return sql
    
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(sql, conn)
        conn.close()
        return df
    except Exception as e:
        return f"Error SQL: {e}\nQuery intentada: {sql}"

# 3. EJECUCIÓN DE PRUEBA
if __name__ == "__main__":
    print(f"--- Laboratorio Dos Aros (Motor: {MODELO_ACTIVO}) ---")
    pregunta = "¿Cuál es el promedio de puntos en temporada regular vs playoffs en 1987?"
    
    print(f"Analizando: {pregunta}")
    sql_generado = preguntar_a_gemini(pregunta)
    
    print(f"SQL Generado: {sql_generado}")
    
    resultado = ejecutar_en_hdd(sql_generado)
    print("\n--- Resultado de la Investigación ---")
    print(resultado)