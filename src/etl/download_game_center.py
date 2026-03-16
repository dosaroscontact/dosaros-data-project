"""
download_game_center.py
=======================
Descarga el JSON del game-center de EuroLeague para una o todas las jornadas.

Estructura de URL:
  https://www.euroleaguebasketball.net/_next/data/{buildId}/en/euroleague/game-center.json
  ?seasonCode=E2025&phaseTypeCode=RS&round=31

Por defecto descarga solo la jornada actual (currentRound).
Con --all descarga todas las jornadas disponibles (útil para carga inicial).
"""

import json
import re
import time
import argparse
import requests
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
BASE_DIR   = SCRIPT_DIR / ".." / ".." / "data" / "raw" / "game-center"
BASE_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
SEASON_CODE    = "E2025"
PHASE_CODE     = "RS"
SLEEP_BETWEEN  = 1.5
SLEEP_ON_ERROR = 6.0


def get_build_id():
    try:
        r = requests.get(
            "https://www.euroleaguebasketball.net/euroleague/",
            headers=HEADERS, timeout=15
        )
        m = re.search(r'"buildId":"(.*?)"', r.text)
        return m.group(1) if m else None
    except Exception as e:
        print(f"  Error obteniendo buildId: {e}")
        return None


def get_current_round(build_id):
    """Obtiene la jornada actual desde el game-center sin parámetros."""
    url = (
        f"https://www.euroleaguebasketball.net/_next/data/{build_id}"
        f"/en/euroleague/game-center.json"
    )
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code == 200:
            data = r.json()
            pp = data.get("pageProps", {})
            return pp.get("currentRound"), pp.get("maxRound"), pp.get("currentSeasonCode", SEASON_CODE)
    except Exception as e:
        print(f"  Error obteniendo jornada actual: {e}")
    return None, None, SEASON_CODE


def download_round(build_id, season_code, phase_code, round_num, force=False):
    """Descarga el JSON de una jornada concreta. Retorna True si OK."""
    out_file = BASE_DIR / f"{season_code}_round_{round_num:02d}.json"

    if out_file.exists() and not force:
        return "skipped"

    url = (
        f"https://www.euroleaguebasketball.net/_next/data/{build_id}"
        f"/en/euroleague/game-center.json"
        f"?seasonCode={season_code}&phaseTypeCode={phase_code}&round={round_num}"
    )

    try:
        res = requests.get(url, headers=HEADERS, timeout=15)

        if res.status_code == 200:
            data = res.json()
            # Verificar que tiene partidos
            games = data.get("pageProps", {}).get("games", [])
            if not games:
                return "empty"
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return "ok"

        elif res.status_code == 429:
            print(f"  ⚠️  Rate limit en jornada {round_num} — esperando {SLEEP_ON_ERROR}s...")
            time.sleep(SLEEP_ON_ERROR)
            return "error"

        else:
            print(f"  ❌ Jornada {round_num} → HTTP {res.status_code}")
            return "error"

    except Exception as e:
        print(f"  ❌ Jornada {round_num} → {e}")
        return "error"


def download_game_center(download_all=False, force=False):
    stats = {"downloaded": 0, "skipped": 0, "empty": 0, "errors": 0}

    build_id = get_build_id()
    if not build_id:
        print("  ❌ No se pudo obtener el buildId.")
        return stats
    print(f"  BuildId: {build_id}")

    current_round, max_round, season_code = get_current_round(build_id)
    if not current_round:
        print("  ❌ No se pudo obtener la jornada actual.")
        return stats

    print(f"  Temporada: {season_code} | Jornada actual: {current_round} | Total: {max_round}")

    if download_all:
        # Descargar todas las jornadas jugadas (1 hasta current_round)
        rounds_to_download = range(1, (current_round or 1) + 1)
        print(f"  Descargando {len(list(rounds_to_download))} jornadas...")
    else:
        # Solo la jornada actual
        rounds_to_download = [current_round]
        print(f"  Descargando jornada {current_round}...")

    for rnd in rounds_to_download:
        result = download_round(build_id, season_code, PHASE_CODE, rnd, force=force)

        if result == "ok":
            stats["downloaded"] += 1
            print(f"  ✅ Jornada {rnd:02d}")
        elif result == "skipped":
            stats["skipped"] += 1
        elif result == "empty":
            stats["empty"] += 1
            print(f"  ⚪ Jornada {rnd:02d} — sin partidos")
        else:
            stats["errors"] += 1

        if result != "skipped":
            time.sleep(SLEEP_BETWEEN)

    return stats


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Descarga JSONs del game-center EuroLeague")
    parser.add_argument("--all",   action="store_true", help="Descarga todas las jornadas jugadas")
    parser.add_argument("--force", action="store_true", help="Re-descarga aunque el fichero exista")
    args = parser.parse_args()

    print("\n🏀 Descargando game-center...")
    stats = download_game_center(download_all=args.all, force=args.force)
    print(f"\n  Descargadas : {stats['downloaded']}")
    print(f"  Omitidas    : {stats['skipped']}")
    print(f"  Vacías      : {stats['empty']}")
    print(f"  Errores     : {stats['errors']}")
