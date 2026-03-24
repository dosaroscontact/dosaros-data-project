"""
euro_historic_games_loader.py — Carga histórica de partidos Euroliga en euro_games

Uso:
    python src/etl/euro_historic_games_loader.py --bloque 2007-2024
"""

import argparse
import re
import sqlite3
import time
import pandas as pd
from datetime import datetime

from euroleague_api.game_stats import GameStats

DB_PATH = "/mnt/nba_data/dosaros_local.db"
COMPETITION = "E"


def _parsear_bloque(bloque):
    """Convierte '2007-2024' en [2007, 2008, ..., 2024].
    Usa regex para extraer los años, inmune a variantes del separador."""
    anos = re.findall(r'\d{4}', bloque)
    if len(anos) < 2:
        raise ValueError(f"Formato inválido para --bloque: '{bloque}'. Usa ej: 2007-2024")
    inicio, fin = int(anos[0]), int(anos[1])
    if inicio > fin:
        raise ValueError(f"El año de inicio ({inicio}) no puede ser mayor que el final ({fin})")
    return list(range(inicio, fin + 1))


def _parsear_fecha(valor):
    """Convierte cualquier formato de fecha a YYYY-MM-DD. Devuelve None si falla."""
    if pd.isna(valor) or valor is None or str(valor).strip() == "":
        return None
    try:
        return pd.to_datetime(str(valor)).strftime("%Y-%m-%d")
    except Exception:
        return str(valor)


def _insertar_partidos(conn, filas):
    """Inserta filas en euro_games usando INSERT OR IGNORE."""
    sql = """
        INSERT OR IGNORE INTO euro_games
            (game_id, date, time, home_team, away_team, score_home, score_away)
        VALUES
            (:game_id, :date, :time, :home_team, :away_team, :score_home, :score_away)
    """
    conn.executemany(sql, filas)
    conn.commit()


def cargar_games_euro(anos):
    """Descarga y guarda partidos Euroliga para los años indicados."""
    gs = GameStats(COMPETITION)

    for season in anos:
        print(f"\n{'='*60}")
        print(f"EUROLIGA — Temporada {season}")
        print(f"{'='*60}")

        try:
            df = gs.get_gamecodes_season(season)
        except Exception as e:
            print(f"  Error al obtener partidos para {season}: {e}")
            continue

        if df is None or df.empty:
            print(f"  Sin datos para temporada {season}.")
            continue

        # Normalizar nombres de columnas a minúsculas
        df.columns = [c.lower() for c in df.columns]

        filas = []
        for _, row in df.iterrows():
            try:
                gamecode_raw = row['gamecode']
                # Si es una Serie de pandas, extraer el valor
                if hasattr(gamecode_raw, 'iloc'):
                    gamecode_raw = gamecode_raw.iloc[0]
                gamecode = str(gamecode_raw).strip()
                game_id = f"E{season}_{gamecode}"

                fecha_raw = row.get("date", None)
                fecha = _parsear_fecha(fecha_raw)

                # homescore / awayscore: None si el partido no se ha jugado
                def _score(val):
                    try:
                        v = int(val)
                        return v
                    except (TypeError, ValueError):
                        return None

                filas.append({
                    "game_id":    game_id,
                    "date":       fecha,
                    "time":       row.get("time", None) or None,
                    "home_team":  row.get("hometeam", row.get("homecode", None)),
                    "away_team":  row.get("awayteam", row.get("awaycode", None)),
                    "score_home": _score(row.get("homescore", None)),
                    "score_away": _score(row.get("awayscore", None)),
                })
            except Exception as e:
                print(f"  Aviso: error procesando fila — {e}")
                continue

        if not filas:
            print(f"  Sin filas válidas para temporada {season}.")
            continue

        try:
            conn = sqlite3.connect(DB_PATH)
            _insertar_partidos(conn, filas)
            conn.close()
            print(f"  Insertados (o ya existentes): {len(filas)} partidos.")
        except Exception as e:
            print(f"  Error guardando en DB para {season}: {e}")
            continue

        # Pausa entre temporadas para no saturar la API
        if season != anos[-1]:
            time.sleep(2)


def main():
    parser = argparse.ArgumentParser(
        description="Carga histórica de partidos Euroliga en euro_games"
    )
    parser.add_argument(
        "--bloque",
        required=True,
        help="Rango de años a procesar, ej: 2007-2024"
    )
    args = parser.parse_args()

    anos = _parsear_bloque(args.bloque)

    print(f"\nInicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Bloque recibido : '{args.bloque}'")
    print(f"Años a procesar : {anos[0]} → {anos[-1]} ({len(anos)} temporadas)")
    print(f"Lista completa  : {anos}")

    cargar_games_euro(anos)

    print(f"\nFin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
