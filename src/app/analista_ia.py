import ollama
import psycopg2
import pandas as pd

def consultor_inteligente(pregunta):
    # Definimos el esquema para que la IA sepa qué tablas existen
    esquema = """
    Tablas de la base de datos:
    1. nba_games (game_id, game_date, home_team_id, visitor_team_id, home_points, visitor_points, season)
    2. nba_player_stats (player_name, points, rebounds, assists, game_id)
    Regla: Genera solo el código SQL de PostgreSQL. Sin explicaciones.
    """

    # La IA genera el SQL
    response = ollama.chat(model='llama3', messages=[
        {'role': 'system', 'content': esquema},
        {'role': 'user', 'content': pregunta}
    ])
    
    sql = response['message']['content'].strip()
    print(f"--- SQL GENERADO ---\n{sql}\n--------------------")

    # Ejecutamos en la Pi
    conn = psycopg2.connect(
        host="192.168.1.136",
        database="proyecto_dos_aros",
        user="postgres",
        password="tu_password_aqui"
    )
    
    df = pd.read_sql(sql, conn)
    conn.close()
    return df

# Ejemplo de uso:
# print(consultor_inteligente("¿Cuál es el promedio de puntos en casa esta temporada?"))