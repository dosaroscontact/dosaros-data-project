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

def fetch_pbp_data(season, game_code):
    """Obtiene los eventos minuto a minuto del partido."""
    url = f"https://api-live.euroleague.net/v1/games/season/{season}/game/{game_code}/playbyplay"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        print(f"Error PBP S{season} G{game_code}: {e}")
    return None

def process_pbp(pbp_data, game_id):
    """Normaliza y guarda los eventos en euro_pbp."""
    if not pbp_data or 'firstQuarter' not in pbp_data:
        return

    events = []
    # La Euroliga divide el JSON por cuartos (firstQuarter, secondQuarter, etc.)
    quarters = ['firstQuarter', 'secondQuarter', 'thirdQuarter', 'fourthQuarter', 'extraTime']
    
    for q_idx, q_name in enumerate(quarters, 1):
        quarter_data = pbp_data.get(q_name, [])
        for event in quarter_data:
            events.append({
                "game_id": game_id,
                "event_num": event.get('NUMBER'),
                "period": q_idx,
                "clock": event.get('MARKERTIME'),
                "action_type": event.get('PLAYTYPE'),
                "player_id": event.get('PLAYER_ID'),
                "x_canvas": event.get('COORD_X'), # Coordenada original
                "y_canvas": event.get('COORD_Y'), # Coordenada original
                "score_home": int(event.get('SCORE_A', 0) or 0),
                "score_away": int(event.get('SCORE_B', 0) or 0)
            })

    if events:
        conn = sqlite3.connect(DB_PATH)
        pd.DataFrame(events).to_sql("euro_pbp", conn, if_exists="append", index=False)
        conn.close()
        print(f"PBP de {game_id} procesado: {len(events)} eventos.")

# Actualizamos el flujo principal
def run_full_import(season, code):
    game_id = f"E{season}_{code}"
    
    # 1. Boxscore (Partidos y Jugadores)
    box_data = fetch_game_data(season, code)
    if box_data:
        process_and_save(box_data)
        
        # 2. Play-by-Play (Eventos y Tiros)
        pbp_data = fetch_pbp_data(season, code)
        process_pbp(pbp_data, game_id)

def fetch_pbp_data(season, game_code):
    """Obtiene los eventos minuto a minuto del partido."""
    url = f"https://api-live.euroleague.net/v1/games/season/{season}/game/{game_code}/playbyplay"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        print(f"Error PBP S{season} G{game_code}: {e}")
    return None

def process_pbp(pbp_data, game_id):
    """Normaliza y guarda los eventos en euro_pbp."""
    if not pbp_data or 'firstQuarter' not in pbp_data:
        return

    events = []
    # La Euroliga divide el JSON por cuartos (firstQuarter, secondQuarter, etc.)
    quarters = ['firstQuarter', 'secondQuarter', 'thirdQuarter', 'fourthQuarter', 'extraTime']
    
    for q_idx, q_name in enumerate(quarters, 1):
        quarter_data = pbp_data.get(q_name, [])
        for event in quarter_data:
            events.append({
                "game_id": game_id,
                "event_num": event.get('NUMBER'),
                "period": q_idx,
                "clock": event.get('MARKERTIME'),
                "action_type": event.get('PLAYTYPE'),
                "player_id": event.get('PLAYER_ID'),
                "x_canvas": event.get('COORD_X'), # Coordenada original
                "y_canvas": event.get('COORD_Y'), # Coordenada original
                "score_home": int(event.get('SCORE_A', 0) or 0),
                "score_away": int(event.get('SCORE_B', 0) or 0)
            })

    if events:
        conn = sqlite3.connect(DB_PATH)
        pd.DataFrame(events).to_sql("euro_pbp", conn, if_exists="append", index=False)
        conn.close()
        print(f"PBP de {game_id} procesado: {len(events)} eventos.")

# Actualizamos el flujo principal
def run_full_import(season, code):
    game_id = f"E{season}_{code}"
    
    # 1. Boxscore (Partidos y Jugadores)
    box_data = fetch_game_data(season, code)
    if box_data:
        process_and_save(box_data)
        
        # 2. Play-by-Play (Eventos y Tiros)
        pbp_data = fetch_pbp_data(season, code)
        process_pbp(pbp_data, game_id)

if __name__ == "__main__":
    # Probamos con la temporada 2023 (formato de la API: 2023)
    run_season_import(2023, 1, 10)