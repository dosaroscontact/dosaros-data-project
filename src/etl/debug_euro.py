import requests

def check_url(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    print(f"URL: {url} -> Status: {r.status_code}")
    if r.status_code == 200:
        print("¡Bingo! Datos encontrados.")
    return r.status_code

# Prueba 1: Temporada pasada (2024), Partido 1
check_url("https://api-live.euroleague.net/v1/games/season/E2024/game/1/boxscore")

# Prueba 2: Temporada actual con prefijo 'E'
check_url("https://api-live.euroleague.net/v1/games/season/E2025/game/1/boxscore")

# Prueba 3: Temporada actual sin prefijo
check_url("https://api-live.euroleague.net/v1/games/season/2025/game/1/boxscore")