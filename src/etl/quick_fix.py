import requests

def test_new_api():
    # Esta es la estructura que suelen usar para el Game Center moderno
    game_code = "281"
    season_code = "E2025"
    
    # Probamos con tres variantes que usa su web actual
    urls = [
        f"https://api-live.euroleague.net/v1/games/season/{season_code}/game/{game_code}/boxscore",
        f"https://live.euroleague.net/api/Boxscore?gamecode={game_code}&seasoncode={season_code}",
        f"https://run.mocky.io/v3/ (esta no, es broma)" # Ignora esto
    ]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
        "Origin": "https://www.euroleaguebasketball.net",
        "Referer": "https://www.euroleaguebasketball.net/"
    }

    for url in urls:
        print(f"Probando: {url}")
        r = requests.get(url, headers=headers)
        print(f"Resultado: {r.status_code}")
        if r.status_code == 200:
            print("¡LO TENEMOS! Los datos están aquí.")
            return True
    return False

if __name__ == "__main__":
    test_new_api()