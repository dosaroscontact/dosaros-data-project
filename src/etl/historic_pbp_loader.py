"""
historic_pbp_loader.py — Carga histórica masiva de Play-by-Play (NBA y Euroliga)

Uso:
    python src/etl/historic_pbp_loader.py --liga nba  --bloque 2023-2025
    python src/etl/historic_pbp_loader.py --liga euro --bloque 2023-2025
    python src/etl/historic_pbp_loader.py --liga ambas --bloque 2023-2025
"""

import argparse
import sqlite3
import time
import pandas as pd
from datetime import datetime

from nba_api.stats.endpoints import playbyplayv3
from euroleague_api.play_by_play_data import PlayByPlay
from src.utils.mapper import map_euro_to_canonical

DB_PATH = "/mnt/nba_data/dosaros_local.db"
COMPETITION_EURO = "E"

# ──────────────────────────────────────────────
# Utilidades
# ──────────────────────────────────────────────

def _tiempo_restante(inicio, completados, total):
    """Devuelve string con tiempo estimado restante."""
    if completados == 0:
        return "calculando..."
    elapsed = time.time() - inicio
    por_partido = elapsed / completados
    restantes = total - completados
    segundos = int(por_partido * restantes)
    h, rem = divmod(segundos, 3600)
    m, s = divmod(rem, 60)
    return f"{h}h {m}m {s}s"


def _parsear_bloque(bloque):
    """Convierte '2023-2025' en [2023, 2024, 2025]."""
    partes = bloque.split("-")
    inicio, fin = int(partes[0]), int(partes[1])
    return list(range(inicio, fin + 1))


# ──────────────────────────────────────────────
# NBA
# ──────────────────────────────────────────────

def _partidos_nba_pendientes(conn, season_prefix):
    """Devuelve lista de GAME_ID sin PBP para una temporada dada."""
    try:
        query = f"""
            SELECT DISTINCT GAME_ID FROM nba_games
            WHERE SEASON_ID LIKE '{season_prefix}%'
            AND GAME_ID NOT IN (SELECT DISTINCT gameId FROM nba_pbp)
        """
        return pd.read_sql_query(query, conn)['GAME_ID'].tolist()
    except Exception:
        # Si nba_pbp aún no existe, descargamos todos
        query = f"SELECT DISTINCT GAME_ID FROM nba_games WHERE SEASON_ID LIKE '{season_prefix}%'"
        try:
            return pd.read_sql_query(query, conn)['GAME_ID'].tolist()
        except Exception as e:
            print(f"  Error consultando nba_games para {season_prefix}: {e}")
            return []


def cargar_pbp_nba(anos):
    """Descarga PBP NBA para los años indicados (regular season + playoffs)."""
    tipos = [('2', 'Regular'), ('4', 'Playoffs')]

    for ano in anos:
        for prefijo, tipo_nombre in tipos:
            season_prefix = f"{prefijo}{ano}"
            print(f"\n{'='*60}")
            print(f"NBA — Temporada {ano} ({tipo_nombre}) | prefijo SEASON_ID: {season_prefix}")
            print(f"{'='*60}")

            conn = sqlite3.connect(DB_PATH)
            partidos = _partidos_nba_pendientes(conn, season_prefix)
            conn.close()

            total = len(partidos)
            if total == 0:
                print("  Sin partidos pendientes.")
                continue

            print(f"  Partidos pendientes: {total}")
            completados = 0
            errores = 0
            inicio = time.time()

            for i, game_id in enumerate(partidos):
                eta = _tiempo_restante(inicio, i, total)
                print(f"  [{i+1}/{total}] Partido {game_id} | ETA: {eta}")
                try:
                    pbp = playbyplayv3.PlayByPlayV3(game_id=game_id)
                    df = pbp.get_data_frames()[0]

                    if df.empty:
                        print(f"    Aviso: sin datos PBP para {game_id}")
                        errores += 1
                        time.sleep(4)
                        continue

                    conn = sqlite3.connect(DB_PATH)
                    df.to_sql('nba_pbp', conn, if_exists='append', index=False)
                    conn.close()
                    completados += 1

                except Exception as e:
                    print(f"    Error en {game_id}: {e}")
                    errores += 1
                    time.sleep(10)
                    continue

                time.sleep(4)

            # Resumen de temporada
            elapsed = int(time.time() - inicio)
            print(f"\n  ── Resumen {ano} {tipo_nombre} ──")
            print(f"  Descargados: {completados} | Errores: {errores} | Tiempo: {elapsed}s")

        # Pausa entre temporadas
        if ano != anos[-1]:
            print(f"\n  Pausa entre temporadas (30s)...")
            time.sleep(30)


# ──────────────────────────────────────────────
# Euroliga
# ──────────────────────────────────────────────

def _partidos_euro_pendientes(conn, season):
    """
    Devuelve lista de (season, game_code) sin PBP para una temporada Euroliga.
    game_id en euro_games tiene formato 'E{season}_{game_code}'.
    """
    try:
        query = f"""
            SELECT game_id FROM euro_games
            WHERE game_id LIKE 'E{season}_%'
            AND game_id NOT IN (SELECT DISTINCT game_id FROM euro_pbp)
        """
        game_ids = pd.read_sql_query(query, conn)['game_id'].tolist()
    except Exception:
        # Si euro_pbp no existe, descargamos todos
        try:
            query = f"SELECT game_id FROM euro_games WHERE game_id LIKE 'E{season}_%'"
            game_ids = pd.read_sql_query(query, conn)['game_id'].tolist()
        except Exception as e:
            print(f"  Error consultando euro_games para {season}: {e}")
            return []

    # Extraemos (season, game_code) del game_id
    resultado = []
    for gid in game_ids:
        try:
            # Formato: E2023_001 → season=2023, code=001
            sin_e = gid[1:]  # quita la 'E'
            partes = sin_e.split("_")
            s = int(partes[0])
            code = int(partes[1])
            resultado.append((s, code, gid))
        except Exception:
            print(f"  Aviso: no se pudo parsear game_id '{gid}', ignorado.")
    return resultado


def cargar_pbp_euro(anos):
    """Descarga PBP Euroliga para los años indicados."""
    pbp_inst = PlayByPlay(COMPETITION_EURO)

    for season in anos:
        print(f"\n{'='*60}")
        print(f"EUROLIGA — Temporada {season}")
        print(f"{'='*60}")

        conn = sqlite3.connect(DB_PATH)
        partidos = _partidos_euro_pendientes(conn, season)
        conn.close()

        total = len(partidos)
        if total == 0:
            print("  Sin partidos pendientes.")
            continue

        print(f"  Partidos pendientes: {total}")
        completados = 0
        errores = 0
        inicio = time.time()

        for i, (s, code, game_id) in enumerate(partidos):
            eta = _tiempo_restante(inicio, i, total)
            print(f"  [{i+1}/{total}] {game_id} (season={s}, code={code}) | ETA: {eta}")
            try:
                data = pbp_inst.get_game_play_by_play_data(s, code)

                if data is None or len(data) == 0:
                    print(f"    Aviso: sin datos PBP para {game_id}")
                    errores += 1
                    time.sleep(2)
                    continue

                df_raw = pd.DataFrame(data)
                df_canonical = map_euro_to_canonical(df_raw, data_type="pbp")

                if df_canonical.empty:
                    print(f"    Aviso: datos vacíos tras normalización para {game_id}")
                    errores += 1
                    time.sleep(2)
                    continue

                df_canonical['game_id'] = game_id

                # Columnas compatibles con euro_pbp (x e y post ALTER TABLE)
                cols = ['game_id', 'event_num', 'period', 'clock', 'action_type', 'player_id', 'x', 'y']
                df_final = df_canonical[[c for c in cols if c in df_canonical.columns]]

                conn = sqlite3.connect(DB_PATH)
                df_final.to_sql('euro_pbp', conn, if_exists='append', index=False)
                conn.close()
                completados += 1

            except Exception as e:
                print(f"    Error en {game_id}: {e}")
                errores += 1
                time.sleep(5)
                continue

            time.sleep(2)

        # Resumen de temporada
        elapsed = int(time.time() - inicio)
        print(f"\n  ── Resumen Euroliga {season} ──")
        print(f"  Descargados: {completados} | Errores: {errores} | Tiempo: {elapsed}s")


# ──────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Carga histórica de PBP NBA y/o Euroliga")
    parser.add_argument(
        "--liga",
        choices=["nba", "euro", "ambas"],
        required=True,
        help="Liga a procesar: nba, euro o ambas"
    )
    parser.add_argument(
        "--bloque",
        required=True,
        help="Rango de años a procesar, ej: 2023-2025"
    )
    args = parser.parse_args()

    anos = _parsear_bloque(args.bloque)
    print(f"\nInicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Liga: {args.liga} | Años: {anos}")

    if args.liga in ("nba", "ambas"):
        cargar_pbp_nba(anos)

    if args.liga in ("euro", "ambas"):
        cargar_pbp_euro(anos)

    print(f"\nFin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
