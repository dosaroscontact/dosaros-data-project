import sqlite3
import requests
import json
import pandas as pd # Importado arriba para evitar retrasos en funciones

# Configuración del búnker de datos en el HDD
DB_PATH = "/mnt/nba_data/dosaros_local.db"
MODELO_IA = "deepseek-coder:1.3b"

def obtener_esquema_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(nba_games)")
    columnas = [col[1] for col in cursor.fetchall()]
    conn.close()
    return ", ".join(columnas)

def preguntar_al_analista(pregunta_usuario):
    esquema = obtener_esquema_db()
    
    # Prompt ultra-restrictivo para evitar inventos
    prompt_sistema = f"""
    Eres un traductor de lenguaje natural a SQL para SQLite.
    TABLA: 'nba_games'
    COLUMNAS: {esquema}

    REGLAS:
    1. Usa SOLO las columnas listadas. No inventes nombres.
    2. Para 1987 usa: SEASON_ID LIKE '%1987'
    3. Para Regular Season: SEASON_ID LIKE '2%'
    4. Para Playoffs: SEASON_ID LIKE '4%'
    5. No uses la función YEAR(). Usa strftime si es necesario.
    6. Devuelve SOLO la query SQL, sin texto extra.

    EJEMPLO:
    Pregunta: Promedio puntos en 1987 regular vs playoffs.
    Respuesta: SELECT SEASON_ID LIKE '4%' as es_playoff, AVG(PTS) FROM nba_games WHERE SEASON_ID LIKE '%1987' GROUP BY es_playoff;
    """

    payload = {
        "model": MODELO_IA,
        "prompt": f"{prompt_sistema}\n\nPregunta: {pregunta_usuario}\nSQL:",
        "stream": False,
        "options": {
            "temperature": 0 # Creatividad cero para máxima precisión
        }
    }

    try:
        response = requests.post("http://localhost:11434/api/generate", json=payload)
        sql_query = response.json().get("response", "").strip()
        return sql_query.replace("```sql", "").replace("```", "").strip()
    except Exception as e:
        return f"Error con Ollama: {e}"

def ejecutar_en_investigacion(sql):
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(sql, conn)
        conn.close()
        return df
    except Exception as e:
        return f"Error SQL: {e}\nQuery intentada: {sql}"

if __name__ == "__main__":
    pregunta = "¿Cual es el promedio de puntos en temporada regular vs playoffs en 1987?"
    query = preguntar_al_analista(pregunta)
    print(f"SQL: {query}")
    print(ejecutar_en_investigacion(query))