import pandas as pd
import sqlite3
from euroleague_api.boxscore_data import BoxScoreData  # Validado con OK
from euroleague_api.play_by_play_data import PlayByPlayData # Siguiendo la misma estructura
from src.utils.mapper import map_euro_to_canonical



# Ruta al HDD en la Raspberry Pi
DB_PATH = "/mnt/nba_data/dosaros_local.db"

def get_and_save_game(season: int, game_code: int):
    """Extrae, limpia y guarda un partido completo."""
    try:
        # 1. Instanciamos herramientas
        bx = Boxscore()
        pbp = PlayByPlay()

        # 2. Boxscore (Estadísticas de jugadores)
        # La librería ya gestiona el prefijo 'E' internamente
        df_players = bx.get_game_report(season, game_code)
        
        if df_players.empty:
            print(f"Partido {game_code} no encontrado.")
            return

        # 3. Limpieza y Mapeo (Para que coincida con tus tablas)
        # Filtramos solo lo que nos interesa para ahorrar espacio en el HDD
        players_to_db = df_players[['Player_ID', 'Team', 'Points', 'TotalRebounds', 'Assists']].copy()
        players_to_db.columns = ['player_id', 'team_id', 'pts', 'reb', 'ast']
        players_to_db['game_id'] = f"E{season}_{game_code}"

        # 4. Play-by-Play (Eventos de tiro y más)
        df_events = pbp.get_game_play_by_play_data(season, game_code)
        
        # Mapeo de PBP (ajustamos a tu tabla euro_pbp)
        events_to_db = df_events[['NUMBER', 'PERIOD', 'MARKERTIME', 'PLAYTYPE', 'PLAYER_ID', 'COORD_X', 'COORD_Y']].copy()
        events_to_db.columns = ['event_num', 'period', 'clock', 'action_type', 'player_id', 'x_canvas', 'y_canvas']
        events_to_db['game_id'] = f"E{season}_{game_code}"

        # 5. Carga atómica en SQLite
        conn = sqlite3.connect(DB_PATH)
        
        # Guardamos estadísticas de jugadores
        players_to_db.to_sql("euro_players_games", conn, if_exists="append", index=False)
        
        # Guardamos eventos
        events_to_db.to_sql("euro_pbp", conn, if_exists="append", index=False)
        
        # Guardamos cabecera del partido (euro_games) de forma manual simple
        # Sacamos el nombre de los equipos del primer registro de jugadores
        home_team = players_to_db['team_id'].unique()[0]
        away_team = players_to_db['team_id'].unique()[1]
        
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO euro_games (game_id, home_team, away_team)
            VALUES (?, ?, ?)
        """, (f"E{season}_{game_code}", home_team, away_team))
        
        conn.commit()
        conn.close()
        print(f"Éxito: Partido E{season}_{game_code} guardado en el HDD.")

    except Exception as e:
        print(f"Error en E{season}_{game_code}: {e}")

if __name__ == "__main__":
    # Prueba real con los IDs que confirmamos antes
    for code in [281, 283, 286]:
        get_and_save_game(2025, code)