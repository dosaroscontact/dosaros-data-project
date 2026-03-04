import requests
import sqlite3
import pandas as pd
import time

DB_PATH = "/mnt/nba_data/dosaros_local.db"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

def fetch_game_data(season, game_code):
    """URL actualizada para el Boxscore (Funciona en 2026)"""
    # Importante: season debe ser E2025
    url = f"https://live.euroleague.net/api/Boxscore?gamecode={game_code}&seasoncode=E{season}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Referer": "https://www.euroleaguebasketball.net/"
    }
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        print(f"Error Boxscore G{game_code}: {e}")
    return None

def fetch_pbp_data(season, game_code):
    """URL actualizada para el Play-by-Play"""
    url = f"https://live.euroleague.net/api/PlayByPlay?gamecode={game_code}&seasoncode=E{season}"
    headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://www.euroleaguebasketball.net/"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        print(f"Error PBP G{game_code}: {e}")
    return None

def process_and_save(game_data):
    if not game_data: return
    
    # Extraemos los nodos principales
    live = game_data.get('Live', {})
    stats = game_data.get('Stats', []) # Lista de 2 diccionarios (Home y Away)
    
    # Construimos el ID del partido
    season = "2025"
    game_code = live.get('GameCode')
    game_id = f"E{season}_{game_code}"
    
    # 1. Datos para 'euro_games'
    game_entry = {
        "game_id": game_id,
        "date": game_data.get('Date'), # Suele estar en la raíz
        "home_team": live.get('Home'),
        "away_team": live.get('Away'),
        "score_home": int(live.get('ScoreA', 0)),
        "score_away": int(live.get('ScoreB', 0))
    }
    
    # 2. Datos para 'euro_players_games'
    players_list = []
    for team_stats in stats:
        team_id = team_stats.get('Team')
        # En esta API, los jugadores suelen estar en 'PlayersStats'
        for p in team_stats.get('PlayersStats', []):
            # Solo guardamos si han jugado (minutos no vacíos)
            if p.get('Minutes'):
                players_list.append({
                    "game_id": game_id,
                    "player_id": p.get('Player_ID'),
                    "team_id": team_id,
                    "pts": int(p.get('Points', 0)),
                    "reb": int(p.get('TotalRebounds', 0)),
                    "ast": int(p.get('Assists', 0))
                })

    # Carga en SQLite
    conn = sqlite3.connect(DB_PATH)
    pd.DataFrame([game_entry]).to_sql("euro_games", conn, if_exists="append", index=False)
    pd.DataFrame(players_list).to_sql("euro_players_games", conn, if_exists="append", index=False)
    conn.close()
    print(f"Partido {game_id} procesado con éxito.")

def run_season_import(season, start_game=1, end_game=340):
    """Bucle para importar una temporada completa."""
    for code in range(start_game, end_game + 1):
        data = fetch_game_data(season, code)
        if data:
            process_and_save(data)
            time.sleep(1) # Respeto a los servidores para evitar BAN
        else:
            print(f"No hay más datos para el código {code}")

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