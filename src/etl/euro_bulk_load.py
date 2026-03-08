import sys
from pathlib import Path

# Detecta la raíz del proyecto (dosaros-data-project) y la añade al path
root_path = Path(__file__).resolve().parent.parent.parent
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))

import time
import sqlite3
from src.etl.euro_extractor import fetch_game_data, process_and_save, fetch_pbp_data, process_pbp

# ... resto del código que ya tienes ...
DB_PATH = "/mnt/nba_data/dosaros_local.db"
SEASON = 2024 # Temporada actual 2024-25

def get_already_loaded_games():
    """Consulta la DB para saber qué partidos ya tenemos."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT game_id FROM euro_players_games")
        games = {int(row[0].split('_')[1]) for row in cursor.fetchall()}
        conn.close()
        return games
    except:
        return set()

def bulk_load(start_code, end_code):
    loaded_games = get_already_loaded_games()
    print(f"🚀 Iniciando carga masiva. Ya tenemos {len(loaded_games)} partidos en DB.")

    for code in range(start_code, end_code + 1):
        if code in loaded_games:
            continue
            
        print(f"📦 Procesando partido {code}...")
        
        # 1. Boxscore
        box = fetch_game_data(SEASON, code)
        if box is not None and not box.empty:
            process_and_save(box, SEASON, code)
            
            # 2. Play-by-Play
            pbp = fetch_pbp_data(SEASON, code)
            if pbp is not None and not pbp.empty:
                process_pbp(pbp, SEASON, code)
            
            print(f"✅ Partido {code} guardado.")
            # Respiro para la API y la SD de la Pi
            time.sleep(1.5) 
        else:
            print(f"⚠️ Partido {code} no disponible o error.")

if __name__ == "__main__":
    # Probamos con los primeros 100 partidos de la temporada
    bulk_load(1, 500)