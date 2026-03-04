import requests
import sqlite3
import pandas as pd
import time

DB_PATH = "/mnt/nba_data/dosaros_local.db"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

def fetch_game_data(season, game_code):
    """Obtiene el JSON crudo de la web de Euroliga."""
    url = f"https://api-live.euroleague.net/v1/games/season/{season}/game/{game_code}/boxscore"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        print(f"Error en S{season} G{game_code}: {e}")
    return None

def process_and_save(game_data):
    """Extrae info de 'euro_games' y 'euro_players_games'."""
    if not game_data:
        return

    conn = sqlite3.connect(DB_PATH)
    
    # 1. Datos del Partido (euro_games)
    header = game_data.get('game', {})
    game_id = f"E{header.get('seasonCode')}_{header.get('gameCode')}"
    
    game_entry = {
        "game_id": game_id,
        "date": header.get('gameDate'),
        "home_team": game_data['home']['team']['name'],
        "away_team": game_data['away']['team']['name'],
        "score_home": game_data['home']['score'],
        "score_away": game_data['away']['score']
    }
    
    # 2. Datos de Jugadores (euro_players_games)
    players_list = []
    for side in ['home', 'away']:
        team_id = game_data[side]['team']['code']
        for p in game_data[side]['players']:
            if p['minutes']: # Solo si ha jugado
                players_list.append({
                    "game_id": game_id,
                    "player_id": p['player']['code'],
                    "team_id": team_id,
                    "pts": p['points'],
                    "reb": p['totalRebounds'],
                    "ast": p['assists']
                })

    # Carga rápida con Pandas
    pd.DataFrame([game_entry]).to_sql("euro_games", conn, if_exists="append", index=False)
    pd.DataFrame(players_list).to_sql("euro_players_games", conn, if_exists="append", index=False)
    
    conn.close()
    print(f"Partido {game_id} guardado.")

def run_season_import(season, start_game=1, end_game=340):
    """Bucle para importar una temporada completa."""
    for code in range(start_game, end_game + 1):
        data = fetch_game_data(season, code)
        if data:
            process_and_save(data)
            time.sleep(1) # Respeto a los servidores para evitar BAN
        else:
            print(f"No hay más datos para el código {code}")

if __name__ == "__main__":
    # Probamos con la temporada 2023 (formato de la API: 2023)
    run_season_import(2023, 1, 10)