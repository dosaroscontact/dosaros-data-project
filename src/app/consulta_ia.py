import ollama
import psycopg2
import pandas as pd

# Configuración de tu nueva DB local
DB_CONFIG = {
    "host": "192.168.1.136",
    "database": "proyecto_dos_aros",
    "user": "postgres",
    "password": "tu_password_aqui"
}

def preguntar_a_nba(pregunta):
    # Definimos el esquema para que la IA sepa qué consultar
    contexto = """
    Tablas disponibles:
    - nba_games (game_id, game_date, home_team_id, visitor_team_id, home_points, visitor_points, season)
    - nba_player_stats (game_id, player_id, player_name, team_id, points, rebounds, assists, minutes)
    Genera solo el código SQL sin explicaciones.
    """
    
    response = ollama.chat(model='llama3', messages=[
        {'role': 'system', 'content': contexto},
        {'role': 'user', 'content': pregunta},
    ])
    
    sql = response['message']['content']
    print(f"SQL Generado: {sql}")
    
    # Conexión a la Pi y ejecución
    conn = psycopg2.connect(**DB_CONFIG)
    df = pd.read_sql_query(sql, conn)
    conn.close()
    return df

# Prueba de fuego
# print(preguntar_a_nba("¿Cuántos partidos de la temporada 2025 tenemos?"))