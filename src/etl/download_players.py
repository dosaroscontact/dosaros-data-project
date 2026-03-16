"""
download_players.py
===================
Descarga los JSONs de perfil de cada jugador desde euroleaguebasketball.net.
Usa players_manual.json como fuente de player_ids.

Estructura de URL:
  https://www.euroleaguebasketball.net/_next/data/{buildId}/en/euroleague/players/{player_id}.json
"""

import json
import re
import time
import argparse
import requests
from pathlib import Path

SCRIPT_DIR  = Path(__file__).parent
PLAYERS_REF = SCRIPT_DIR / ".." / ".." / "data" / "raw" / "players_manual.json"
BASE_DIR    = SCRIPT_DIR / ".." / ".." / "data" / "raw" / "players"
BASE_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
SLEEP_BETWEEN  = 1.2
SLEEP_ON_ERROR = 5.0


def get_build_id():
    try:
        r = requests.get(
            "https://www.euroleaguebasketball.net/euroleague/",
            headers=HEADERS)
        m = re.search(r'"buildId":"(.*?)"', r.text)
        return m.group(1) if m else None
    except Exception as e:
        print(f"  Error obteniendo buildId: {e}")
        return None


def load_player_ids():
    if not PLAYERS_REF.exists():
        print(f"  No se encontró {PLAYERS_REF}")
        return []
    with open(PLAYERS_REF, encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, list) else []


def download_players(force=False):
    stats = {"downloaded": 0, "skipped": 0, "errors": 0}

    build_id = get_build_id()
    if not build_id:
        print("  ❌ No se pudo obtener el buildId.")
        return stats
    print(f"  BuildId: {build_id}")

    players = load_player_ids()
    if not players:
        print("  ❌ No se encontraron jugadores en players_manual.json")
        return stats

    print(f"  {len(players)} jugadores a procesar...")

    for p in players:
        player_id = str(p.get("player_id", "")).strip()
        name      = p.get("player_name", player_id)
        if not player_id:
            continue

        out_file = BASE_DIR / f"{player_id}.json"

        if out_file.exists() and not force:
            stats["skipped"] += 1
            continue

        url = (
            f"https://www.euroleaguebasketball.net/_next/data/{build_id}"
            f"/en/euroleague/players/{player_id}.json"
        )

        try:
            res = requests.get(url, headers=HEADERS)

            if res.status_code == 200:
                with open(out_file, "w", encoding="utf-8") as f:
                    json.dump(res.json(), f, indent=2, ensure_ascii=False)
                stats["downloaded"] += 1
                print(f"  ✅ {name} ({player_id})")

            elif res.status_code == 429:
                print(f"  ⚠️  Rate limit — esperando {SLEEP_ON_ERROR}s...")
                time.sleep(SLEEP_ON_ERROR)
                stats["errors"] += 1

            else:
                print(f"  ❌ {name} ({player_id}) → HTTP {res.status_code}")
                stats["errors"] += 1

        except Exception as e:
            print(f"  ❌ {name} ({player_id}) → {e}")
            stats["errors"] += 1

        time.sleep(SLEEP_BETWEEN)

    return stats


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Descarga JSONs de jugadores EuroLeague")
    parser.add_argument("--force", action="store_true", help="Re-descarga aunque el fichero exista")
    args = parser.parse_args()

    print("\n🏀 Descargando perfiles de jugadores...")
    stats = download_players(force=args.force)
    print(f"\n  Descargados : {stats['downloaded']}")
    print(f"  Omitidos    : {stats['skipped']}")
    print(f"  Errores     : {stats['errors']}")
