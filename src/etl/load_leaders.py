import json
import sqlite3
import os

DB_PATH = "/mnt/nba_data/dosaros_local.db"
JSON_PATH = "../utils/json/stats.json"

def cargar_lideres():
    if not os.path.exists(JSON_PATH):
        print(f"No se encuentra el archivo en {JSON_PATH}")
        return

    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Navegamos por la estructura según la documentación
    blocks = data.get('pageProps', {}).get('article', {}).get('content', [])
    
    for block in blocks:
        category = block.get('statsBlockTitle')
        is_team = block.get('isTeamsStats', False)
        items = block.get('topFiveStats', {}).get('items', [])
        
        for item in items:
            cursor.execute("""
                INSERT OR REPLACE INTO euro_stats_leaders 
                (category_name, is_team, player_name, team_name, average_value, total_value, rank_position)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                category,
                is_team,
                item.get('playerName'),
                item.get('clubName'),
                item.get('value'),
                item.get('total'),
                item.get('rank')
            ))
            
    conn.commit()
    conn.close()
    print("Líderes estadísticos cargados correctamente.")

if __name__ == "__main__":
    cargar_lideres()