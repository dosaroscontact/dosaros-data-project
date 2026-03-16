import json
import re
import time
import random
import requests
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
TEAMS_JSON = SCRIPT_DIR / ".." / ".." / "data" / "raw" / "teams" / "teams.json"
BASE_DIR   = SCRIPT_DIR / ".." / ".." / "data" / "raw" / "teams"
BASE_DIR.mkdir(parents=True, exist_ok=True)

BUILD_ID_CACHE = BASE_DIR / ".buildid_cache"

HEADERS = {
    "User-Agent":                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept":                    "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language":           "en-US,en;q=0.9,es;q=0.8",
    "Accept-Encoding":           "gzip, deflate, br",
    "Connection":                "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest":            "document",
    "Sec-Fetch-Mode":            "navigate",
    "Sec-Fetch-Site":            "none",
    "Sec-Fetch-User":            "?1",
    "Cache-Control":             "max-age=0",
}


def get_build_id():
    """Obtiene el buildId con sesión persistente y reintentos anti-bot."""
    # Intentar desde caché primero
    if BUILD_ID_CACHE.exists():
        cached = BUILD_ID_CACHE.read_text().strip()
        if cached:
            print(f"BuildId desde caché: {cached}")
            return cached

    url     = "https://www.euroleaguebasketball.net/euroleague/"
    session = requests.Session()
    session.headers.update(HEADERS)

    for attempt in range(4):
        delay = 3 + random.uniform(1, 3) + attempt * 4
        if attempt > 0:
            print(f"  Reintento {attempt} — esperando {delay:.1f}s...")
        time.sleep(delay)

        try:
            r = session.get(url)
            print(f"  GET home → HTTP {r.status_code}")

            if r.status_code == 429:
                print("  429 — cookies guardadas, reintentando...")
                continue

            if r.status_code != 200:
                continue

            for pat in [r'"buildId":"(.*?)"', r"/_next/static/([A-Za-z0-9_\\-]{20,})/"]:
                m = re.search(pat, r.text)
                if m:
                    build_id = m.group(1)
                    print(f"  BuildId: {build_id}")
                    BUILD_ID_CACHE.write_text(build_id)
                    return build_id

            print(f"  buildId no encontrado (intento {attempt+1})")

        except Exception as e:
            print(f"  Error: {e}")

    print("No se pudo obtener el buildId.")
    return None


def download_teams():
    build_id = get_build_id()
    if not build_id:
        return

    print(f"Usando buildId: {build_id}")

    with open(TEAMS_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    clubs = data.get("headerData", {}).get("euroleague", {}).get("clubs", {}).get("clubs", [])
    session = requests.Session()
    session.headers.update({**HEADERS, "Accept": "application/json", "Sec-Fetch-Dest": "empty", "Sec-Fetch-Mode": "cors", "Sec-Fetch-Site": "same-origin", "Referer": "https://www.euroleaguebasketball.net/euroleague/"})

    for club in clubs:
        name     = club.get("name")
        url_path = club.get("url", "")
        parts    = [p for p in url_path.split("/") if p]
        if len(parts) < 5:
            continue

        slug = parts[2]
        code = parts[4]

        json_url = f"https://www.euroleaguebasketball.net/_next/data/{build_id}/en/euroleague/teams/{slug}/{code}.json"
        filename = BASE_DIR / f"{code.lower()}.json"

        print(f"Descargando {name} ({code})...")
        try:
            res = session.get(json_url)
            if res.status_code == 200:
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(res.json(), f, indent=4)
                print(f"  Guardado: {filename}")
            elif res.status_code == 404:
                # buildId caducado
                print(f"  404 — buildId posiblemente caducado, borrando caché...")
                if BUILD_ID_CACHE.exists():
                    BUILD_ID_CACHE.unlink()
                break
            else:
                print(f"  Error {res.status_code} en {name}")
        except Exception as e:
            print(f"  Fallo en {name}: {e}")

        time.sleep(1.5 + random.uniform(0.3, 0.8))


if __name__ == "__main__":
    download_teams()
