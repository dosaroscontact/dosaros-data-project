import json
import os
import sqlite3
import glob

# Configuración de rutas
DB_PATH = "/mnt/nba_data/dosaros_local.db"
DATA_PATH = "players/players_data/*.json"

def cargar_jugadores():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    archivos = glob.glob(DATA_PATH)
    print(f"Encontrados {len(archivos)} archivos. Iniciando proceso...")

    for ruta in archivos:
        with open(ruta, 'r', encoding='utf-8') as f:
            try:
                datos = json.load(f)
                # Acceso simplificado a la data del jugador
                player_data = datos.get('pageProps', {}).get('data', {})
                hero = player_data.get('hero', {})
                
                if not hero:
                    continue

                p_id = hero.get('id')
                nombre = f"{hero.get('firstName')} {hero.get('lastName')}"
                
                # 1. Inserción en euro_players (Bio)
                cursor.execute("""
                    INSERT OR REPLACE INTO euro_players 
                    (player_id, player_name, position, height, club_name, nationality, image_url)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    p_id,
                    nombre,
                    hero.get('position'),
                    hero.get('height'),
                    hero.get('clubCode'), # Usamos el código para vincular con euro_teams
                    hero.get('nationality'),
                    hero.get('photo')
                ))

                # 2. Inserción en euro_stats_career (Historial)
                stat_tables = player_data.get('alltime', {}).get('statTables', [])
                for table in stat_tables:
                    es_euroliga = table.get('groupName') == "EuroLeague"
                    for row in table.get('stats', []):
                        cursor.execute("""
                            INSERT OR REPLACE INTO euro_stats_career
                            (player_id, season_code, team_name, games_played, pts, reb, ast, pir, is_euroleague)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            p_id,
                            row.get('season'),
                            row.get('club'),
                            row.get('gamesPlayed'),
                            row.get('points'),
                            row.get('rebounds'),
                            row.get('assists'),
                            row.get('pir'),
                            es_euroliga
                        ))
                
            except Exception as e:
                print(f"Error en archivo {ruta}: {e}")

    conn.commit()
    conn.close()
    print("¡Carga masiva finalizada con éxito!")

if __name__ == "__main__":
    cargar_jugadores()