from nba_api.stats.endpoints import boxscoretraditionalv2
import time

def sync_stats():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    cur.execute("SELECT game_id FROM nba_games")
    games = cur.fetchall()
    
    print(f"Iniciando descarga de estadisticas para {len(games)} partidos")
    
    for (game_id,) in games:
        try:
            print(f"Procesando partido: {game_id}")
            box = boxscoretraditionalv2.BoxScoreTraditionalV2(game_id=game_id)
            player_stats = box.get_data_frames()[0]
            
            for _, row in player_stats.iterrows():
                pts = row['PTS'] if row['PTS'] is not None else 0
                reb = row['REB'] if row['REB'] is not None else 0
                ast = row['AST'] if row['AST'] is not None else 0
                
                cur.execute("""
                    INSERT INTO nba_player_stats (game_id, player_name, points, rebounds, assists, minutes)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (game_id, row['PLAYER_NAME'], pts, reb, ast, row['MIN']))
            
            conn.commit()
            time.sleep(1) 
        except Exception as e:
            print(f"Error en {game_id}: {e}")
            continue

    cur.close()
    conn.close()
    print("Sincronizacion de estadisticas completada")

if __name__ == "__main__":
    sync_stats()