import sys
from pathlib import Path

# Añadimos la raíz del proyecto al path para que encuentre tus módulos
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.etl.euro_extractor import fetch_game_data, process_and_save, fetch_pbp_data, process_pbp
import sqlite3

def test_load(season=2025, num_games=5):
    print(f"--- Iniciando Carga de Prueba: Temporada {season} ---")
    
    for code in range(1, num_games + 1):
        game_id = f"E{season}_{code}"
        print(f"Procesando {game_id}...")
        
        # 1. Boxscore
        box = fetch_game_data(season, code)
        if box:
            process_and_save(box)
            
            # 2. Play-by-Play
            pbp = fetch_pbp_data(season, code)
            if pbp:
                process_pbp(pbp, game_id)
        else:
            print(f"Salto: El partido {code} no parece estar disponible.")

    # Verificación final
    conn = sqlite3.connect("/mnt/nba_data/dosaros_local.db")
    cursor = conn.cursor()
    
    print("\n--- Resultados en DB ---")
    tables = ['euro_games', 'euro_players_games', 'euro_pbp']
    for table in tables:
        count = cursor.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"Tabla {table}: {count} filas.")
    
    conn.close()

if __name__ == "__main__":
    test_load()