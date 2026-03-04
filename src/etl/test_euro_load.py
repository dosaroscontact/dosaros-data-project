import sys
from pathlib import Path
# Asegúrate de que el path sea correcto para tu Raspberry Pi
sys.path.append("/home/pi/dosaros-data-project")

from src.etl.euro_extractor import fetch_game_data, process_and_save, fetch_pbp_data, process_pbp
import sqlite3

def test_real_games():
    # Vamos a probar con los IDs que me has pasado
    # Formato: E2025 (Temporada) y el número del final de la URL
    season = "2025"
    games_to_test = [281, 283, 286] 
    
    print(f"--- Probando con Partidos Reales: Temporada {season} ---")
    
    for code in games_to_test:
        game_id = f"E{season}_{code}"
        print(f"Intentando descargar: {game_id}...")
        
        # OJO: La URL base debe llevar la 'E' antes del año
        # Asegúrate de que en euro_extractor.py la URL sea:
        # f"https://api-live.euroleague.net/v1/games/season/E{season}/game/{code}/boxscore"
        
        box = fetch_game_data(season, code)
        if box:
            process_and_save(box)
            pbp = fetch_pbp_data(season, code)
            if pbp:
                process_pbp(pbp, game_id)
        else:
            print(f"Error: No se pudo obtener el partido {code}. Revisa la URL en euro_extractor.py")

    # Verificación
    conn = sqlite3.connect("/mnt/nba_data/dosaros_local.db")
    res = conn.execute("SELECT COUNT(*) FROM euro_games").fetchone()[0]
    print(f"\nÉxito: {res} partidos nuevos en la base de datos.")
    conn.close()

if __name__ == "__main__":
    test_real_games()