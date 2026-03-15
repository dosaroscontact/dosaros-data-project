#!/usr/bin/env python3
"""
fetch_all_players.py
====================
Descarga el perfil detallado de todos los jugadores de EuroLeague
y guarda cada uno como un fichero JSON individual: 008104.json

Uso:
    python fetch_all_players.py --build-id hvGIyKafFCKSt6G5KJbO-

Opcionales:
    --json PATH       Fichero fuente con la lista de jugadores (default: all_eureleague_web.json)
    --output DIR      Carpeta donde guardar los JSON (default: players_data)
    --delay SECS      Pausa entre requests (default: 0.8)
    --limit N         Solo descargar los primeros N jugadores (para pruebas)
    --player-id ID    Descargar solo un jugador concreto (ej: 003733)

Ejemplo:
    python fetch_all_players.py --build-id hvGIyKafFCKSt6G5KJbO- --limit 3
    python fetch_all_players.py --build-id hvGIyKafFCKSt6G5KJbO- --player-id 003733

NOTA: El build-id caduca con cada deploy de la web. Si obtienes 404:
    1. Abre https://www.euroleaguebasketball.net/en/euroleague/players/
    2. DevTools (F12) -> Network -> filtrar "_next/data"
    3. Recarga la pagina y copia el nuevo ID del path
"""

import json
import argparse
import time
import sys
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
import unicodedata, re



BASE_URL = (
    "https://www.euroleaguebasketball.net/_next/data/"
    "{build_id}/en/euroleague/players/{slug}/{player_id}.json"
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.euroleaguebasketball.net/en/euroleague/players/",
}



def fetch_json(url, retries=3, timeout=15):
    for attempt in range(1, retries + 1):
        try:
            req = Request(url, headers=HEADERS)
            with urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode('utf-8'))
        except HTTPError as e:
            if e.code == 404:
                return None
            if attempt == retries:
                raise
            time.sleep(2 ** attempt)
        except URLError as e:
            if attempt == retries:
                raise
            time.sleep(2 ** attempt)
    return None


def slug_from_url(url_path):
    """/en/euroleague/players/arturs-zagars/008104/ -> arturs-zagars"""
    parts = [p for p in url_path.strip('/').split('/') if p]
    if len(parts) >= 4:
        return parts[-2]
    return None
def slug_from_name(first, last):
    """Melvin Ajinca -> melvin-ajinca"""
    full = f"{first}-{last}".lower()
    # Normalizar acentos
    full = unicodedata.normalize('NFD', full)
    full = ''.join(c for c in full if unicodedata.category(c) != 'Mn')
    # Reemplazar espacios y caracteres raros por guión
    full = re.sub(r'[^a-z0-9]+', '-', full).strip('-')
    return full


def main():
    parser = argparse.ArgumentParser(description='Descarga perfiles de jugadores EuroLeague -> JSON')
    parser.add_argument('--build-id',  required=True,
                        help='Build ID de Next.js (ej: hvGIyKafFCKSt6G5KJbO-)')
    parser.add_argument('--json',      default='players_manual.json',
                        help='Fichero fuente con la lista de jugadores')
    parser.add_argument('--output',    default='players_data',
                        help='Carpeta donde guardar los JSON individuales')
    parser.add_argument('--delay',     type=float, default=0.8,
                        help='Segundos de pausa entre requests (default: 0.8)')
    parser.add_argument('--limit',     type=int,   default=None,
                        help='Limitar a N jugadores (para pruebas)')
    parser.add_argument('--player-id', default=None,
                        help='Descargar solo un jugador concreto (ej: 003733)')
    args = parser.parse_args()

    # -- Cargar lista de jugadores --
    json_path = Path(args.json)
    if not json_path.exists():
        print(f"ERROR: No se encuentra {json_path}", file=sys.stderr)
        sys.exit(1)

    with open(json_path, encoding='utf-8') as f:
        raw = json.load(f)

    lookup = {item['player_id'] for item in raw}
    players_raw = [item for item in raw if item['player_id'] in lookup]

    if not players_raw:
        print("ERROR: No se encontro 'all_info_euroleague_web.json' en el JSON", file=sys.stderr)
        sys.exit(1)

    # Filtros opcionales
    if args.player_id:
        players_raw = [p for p in players_raw if p['id'] == args.player_id]
        if not players_raw:
            print(f"ERROR: Jugador {args.player_id} no encontrado", file=sys.stderr)
            #sys.exit(1)

    if args.limit:
        players_raw = players_raw[:args.limit]

    total = len(players_raw)

    # -- Crear carpeta de salida --
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Fuente:     {json_path}")
    print(f"Salida:     {output_dir.resolve()}")
    print(f"Jugadores:  {total}")
    print()

    # -- Bucle principal --
    ok = 0
    skipped = 0
    errors = []

    for i, p in enumerate(players_raw, 1):
        pid      = p['player_id']
        slug     = slug_from_url(p.get('url', ''))
        name     = f"{p.get('first_name', '')} {p.get('last_name', '')}"

        # if not p.get('url') and not p.get('firstName'):
        #     print(f"\nDEBUG item sin datos ({pid}):")
        #     print(json.dumps(p, indent=2, ensure_ascii=False))
        #     print()

        if not slug:
            print(f" name : {name}  slug : {slug}")
            slug = slug_from_name(p.get('first_name', ''), p.get('last_name', ''))

        out_file = output_dir / f"{pid}.json"

        # Saltar si ya existe
        if out_file.exists():
            print(f"  [{i:3}/{total}] SKIP  {name:<28} ({pid}) ya existe")
            skipped += 1
            continue

        if not slug:
            print(f"  [{i:3}/{total}] WARN  {name:<28} ({pid}) sin slug, saltando")
            errors.append((pid, name, 'sin slug'))
            continue

        url = BASE_URL.format(build_id=args.build_id, slug=slug, player_id=pid)
        print(f"  [{i:3}/{total}] DOWN  {name:<28} ({pid}) ...", end='', flush=True)

        try:
            data = fetch_json(url)
        except Exception as e:
            print(f" ERROR: {e}")
            errors.append((pid, name, str(e)))
            continue

        if data is None:
            print(f" 404")
            errors.append((pid, name, '404'))
            # Si los primeros fallan seguidos, el build ID probablemente caduco
            if len(errors) >= 3 and ok == 0:
                print("\nDemasiados 404 seguidos. El build ID puede haber caducado.")
                print("Obten uno nuevo desde DevTools -> Network -> _next/data\n")
                break
            continue

        # Guardar como JSON con indentacion legible
        with open(out_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        ok += 1
        size_kb = out_file.stat().st_size / 1024
        print(f" OK  ({size_kb:.1f} KB)")

        if i < total:
            time.sleep(args.delay)

    # -- Resumen --
    print(f"\n{'-'*50}")
    print(f"Descargados:  {ok}")
    print(f"Ya existian:  {skipped}")
    if errors:
        print(f"Errores ({len(errors)}):")
        for pid, name, err in errors:
            print(f"   {pid}  {name}: {err}")

    print(f"\nFicheros guardados en: {output_dir.resolve()}")


if __name__ == '__main__':
    main()
