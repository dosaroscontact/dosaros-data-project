import sys
import sqlite3
import pandas as pd
sys.path.append("/home/pi/dosaros-data-project")
from src.etl.euro_extractor import fetch_game_data, process_and_save, fetch_pbp_data, process_pbp

def test_real_games():
    season = "2025"
    games_to_test = [281, 283, 286] 
    print(f"--- Probando con Partidos Reales: Temporada {season} ---")
    
    for code in games_to_test:
        game_id = f"E{season}_{code}"
        print(f"Intentando descargar: {game_id}...")
        
        box = fetch_game_data(season, code)
        if box is not None and not box.empty:
            process_and_save(box, season, code)
            
            pbp = fetch_pbp_data(season, code)
            if pbp is not None and not pbp.empty:
                process_pbp(pbp, season, code)
                print(f"✅ Éxito: {game_id} guardado correctamente.")
        else:
            print(f"❌ Error al obtener {game_id}")

if __name__ == "__main__":
    test_real_games()