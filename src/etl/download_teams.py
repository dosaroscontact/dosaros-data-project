import json
import os
import requests
import re
import time
from pathlib import Path

# Configuración
TEAMS_JSON = "teams.json"
# 1. Definimos la carpeta del script para calcular rutas relativas
SCRIPT_DIR = Path(__file__).parent

# 2. Ruta corregida hacia teams.json (sube un nivel a src, luego utils/json/)
TEAMS_JSON = SCRIPT_DIR / ".." / ".." / "data" / "raw" / "teams" / "teams.json"

# 3. Ruta corregida para descargar los datos (fuera de src, en la raíz del proyecto)
BASE_DIR = SCRIPT_DIR / ".." / ".." / "data" / "raw" / "teams"

# 4. Crear la carpeta si no existe (parents=True para crear 'data' y 'teams')
BASE_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def get_build_id():
    """Busca el buildId actual en la web de la Euroliga"""
    url = "https://www.euroleaguebasketball.net/euroleague/"
    response = requests.get(url, headers=HEADERS)
    match = re.search(r'"buildId":"(.*?)"', response.text)
    if match:
        return match.group(1)
    return None

def download_teams():
    build_id = get_build_id()
    if not build_id:
        print("No se encontró el buildId.")
        return

    print(f"Usando buildId: {build_id}")

    with open(TEAMS_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Navegación por la estructura que me pasaste
    clubs = data.get("headerData", {}).get("euroleague", {}).get("clubs", {}).get("clubs", [])

    for club in clubs:
        name = club.get("name")
        url_path = club.get("url") # Ej: /euroleague/teams/as-monaco/roster/mco/
        
        # Extraemos slug y código de la URL
        parts = [p for p in url_path.split("/") if p]
        if len(parts) < 4:
            continue
            
        slug = parts[2]
        code = parts[4]

        # Construcción de la URL del JSON de hidratación
        json_url = f"https://www.euroleaguebasketball.net/_next/data/{build_id}/en/euroleague/teams/{slug}/{code}.json"
        filename = BASE_DIR / f"{code.lower()}.json"

        print(f"Descargando {name} ({code})...")
        try:
            res = requests.get(json_url, headers=HEADERS)
            if res.status_code == 200:
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(res.json(), f, indent=4)
                print(f"Guardado: {filename}")
            else:
                print(f"Error {res.status_code} en {name}")
        except Exception as e:
            print(f"Fallo en {name}: {e}")
        
        # Pausa para evitar bloqueos
        time.sleep(1.5)

if __name__ == "__main__":
    download_teams()