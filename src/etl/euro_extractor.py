import requests
import sqlite3
import pandas as pd
from pathlib import Path

# Configuración de rutas según la estructura del proyecto
DB_PATH = "/mnt/nba_data/dosaros_local.db"

def get_euroleague_game(season: int, game_code: int):
    """
    Trae los datos de un partido específico.
    Ejemplo de season: 2023, game_code: 1 (Primer partido de jornada 1)
    """
    # La URL base que usa la web oficial para sus datos JSON
    url = f"https://api-live.euroleague.net/v1/games/season/{season}/game/{game_code}/boxscore"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Error en partido {game_code}: {e}")
    return None

def save_to_sqlite(data, table_name):
    """Carga eficiente en la Raspberry Pi usando pandas"""
    conn = sqlite3.connect(DB_PATH)
    # Aquí transformamos el JSON a DataFrame antes de insertar
    # df = pd.json_normalize(data) 
    # df.to_sql(table_name, conn, if_exists='append', index=False)
    conn.close()

def normalize_euro_pbp(raw_event, game_id):
    """
    Transforma un evento crudo de la Euroliga al formato Dos Aros.
    """
    # Ejemplo de mapeo simple
    return {
        "game_id": game_id,
        "event_num": raw_event.get("NUMBER"),
        "period": raw_event.get("PERIOD"),
        "clock": raw_event.get("MARKERTIME"),
        "action_type": raw_event.get("IDACTION"), # Habrá que mapear IDs a nombres
        "player_id": raw_event.get("PLAYER_ID"),
        "x_canvas": raw_event.get("COORD_X"),
        "y_canvas": raw_event.get("COORD_Y"),
        "score_home": raw_event.get("SCORE_HOME"),
        "score_away": raw_event.get("SCORE_ANY")
    }

# Ejemplo de uso inicial
if __name__ == "__main__":
    print("Iniciando extracción Euroliga...")
    # Prueba con el primer partido de la temporada actual
    game_data = get_euroleague_game(2023, 1)
    if game_data:
        print("Datos recibidos correctamente.")