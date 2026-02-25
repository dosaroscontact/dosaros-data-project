import sqlite3
import requests
import json

# Configuración del laboratorio Dos Aros
DB_PATH = "/mnt/nba_data/dosaros_local.db"
MODELO_IA = "deepseek-coder:1.3b"  # Versión 3B optimizada para la RAM de la Pi

def obtener_esquema_db():
    """Extrae la estructura de la tabla para que la IA sepa qué columnas existen."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(nba_games)")
    columnas = [col[1] for col in cursor.fetchall()]
    conn.close()
    return ", ".join(columnas)

def preguntar_al_analista(pregunta_usuario):
    esquema = obtener_esquema_db()
    
    # Definimos la personalidad y el conocimiento técnico de la IA
    prompt_sistema = f"""
    Eres un experto analista de datos de la NBA para el Proyecto Dos Aros. 
    Tu base de datos es SQLite y la tabla se llama 'nba_games'.
    Las columnas disponibles son: {esquema}.
    
    REGLA DE ORO: Responde ÚNICAMENTE con la consulta SQL. Sin explicaciones ni texto adicional.
    Usa LIKE '2%' para Regular Season y LIKE '4%' para Playoffs en la columna SEASON_ID.
    """

    payload = {
        "model": MODELO_IA,
        "prompt": f"{prompt_sistema}\n\nPregunta: {pregunta_usuario}\nSQL:",
        "stream": False
    }

    try:
        response = requests.post("http://localhost:11434/api/generate", json=payload)
        sql_query = response.json().get("response", "").strip()
        
        # Limpiamos posibles etiquetas de markdown que devuelva la IA
        sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
        return sql_query
    except Exception as e:
        return f"Error conectando con Ollama: {e}"

def ejecutar_en_investigacion(sql):
    """Ejecuta la query generada en el HDD externo y devuelve los resultados."""
    try:
        conn = sqlite3.connect(DB_PATH)
        import pandas as pd
        df = pd.read_sql_query(sql, conn)
        conn.close()
        return df
    except Exception as e:
        return f"Error de ejecución SQL: {e}"

if __name__ == "__main__":
    pregunta = "¿Cuál es el promedio de puntos en temporada regular vs playoffs en 1987?"
    print(f"Pregunta: {pregunta}")
    
    query = preguntar_al_analista(pregunta)
    print(f"SQL Generado: {query}")
    
    resultado = ejecutar_en_investigacion(query)
    print("\n--- Resultado del Laboratorio ---")
    print(resultado)