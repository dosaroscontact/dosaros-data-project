import sqlite3
import pandas as pd
from google import genai
from google.genai import types

# Configuración del Laboratorio
API_KEY = "AIzaSyAnz9CXRL3Fyjjz8wWqH4lowmeAkeM_cy4" 
DB_PATH = "/mnt/nba_data/dosaros_local.db"

# Inicialización del cliente con el nuevo SDK oficial
client = genai.Client(api_key=API_KEY)

# Configuración de la "Gema" mediante Instrucciones del Sistema
instruccion_sistema = """
Eres el motor de traducción SQL para el Proyecto Dos Aros. 
Tu función es convertir preguntas en lenguaje natural en consultas SQL precisas para SQLite.

INFORMACIÓN DEL ESQUEMA:
- Tabla: 'nba_games'
- Columnas clave: SEASON_ID, GAME_DATE, TEAM_ABBREVIATION, WL, PTS, REB, AST, PLUS_MINUS.

LÓGICA DE NEGOCIO:
1. Temporada Regular: SEASON_ID debe empezar por '2' (ej. LIKE '2%').
2. Playoffs: SEASON_ID debe empezar por '4' (ej. LIKE '4%').
3. Año: El formato en SEASON_ID es el año de inicio. Ejemplo: '21987' es Regular Season de 1987.
4. PROHIBIDO: Usar la función YEAR(). Para fechas usa strftime o filtros sobre SEASON_ID.

SALIDA:
- Devuelve ÚNICAMENTE el código SQL plano, sin bloques de código markdown (sin ```sql).
"""

def preguntar_a_gemini(pregunta_usuario):
    """Envía la consulta a Gemini y extrae el SQL."""
    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=pregunta_usuario,
            config=types.GenerateContentConfig(
                system_instruction=instruccion_sistema,
                temperature=0.0
            )
        )
        # Limpieza de posibles etiquetas markdown
        sql = response.text.replace("```sql", "").replace("```", "").strip()
        return sql
    except Exception as e:
        return f"Error en la petición a Gemini: {e}"

def ejecutar_en_hdd(sql):
    """Ejecuta la consulta directamente en el disco duro externo."""
    if "Error" in sql:
        return sql
        
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(sql, conn)
        conn.close()
        return df
    except Exception as e:
        return f"Error de ejecución SQL: {e}\nQuery intentada: {sql}"

if __name__ == "__main__":
    print("--- Analista IA Dos Aros (Gemini Flash) ---")
    pregunta = "¿Cual es el promedio de puntos en temporada regular vs playoffs en 1987?"
    
    print(f"Pregunta: {pregunta}")
    sql_generado = preguntar_a_gemini(pregunta)
    
    print(f"SQL Generado: {sql_generado}")
    
    resultado = ejecutar_en_hdd(sql_generado)
    print("\n--- Resultado del Laboratorio ---")
    print(resultado)