from nba_api.stats.endpoints import leaguegamelog
import pandas as pd
import sqlite3
import time
import os
import argparse
from datetime import datetime


def descargar_boxscores_jugadores(ano_inicio, ano_fin, fecha=None):
    db_path = os.environ.get("DB_PATH", "/mnt/nba_data/dosaros_local.db")

    if fecha:
        # Convertir YYYY-MM-DD → MM/DD/YYYY para la API
        fecha_dt = datetime.strptime(fecha, "%Y-%m-%d")
        fecha_api = fecha_dt.strftime("%m/%d/%Y")
        # Inferir temporada: oct-dic → año actual, ene-sep → año anterior
        ano = fecha_dt.year if fecha_dt.month >= 10 else fecha_dt.year - 1
        temporadas = [f"{ano}-{str(ano + 1)[-2:]}"]
    else:
        temporadas = [f"{ano}-{str(ano + 1)[-2:]}" for ano in range(ano_inicio, ano_fin)]

    conn = sqlite3.connect(db_path)

    for season in temporadas:
        print(f"Buscando estadísticas de jugadores: Temporada {season}...")

        try:
            kwargs = dict(
                season=season,
                league_id='00',
                player_or_team_abbreviation='P',  # 'P' para Jugadores
                season_type_all_star='Regular Season'
            )
            if fecha:
                kwargs['date_from_nullable'] = fecha_api
                kwargs['date_to_nullable'] = fecha_api

            log = leaguegamelog.LeagueGameLog(**kwargs)
            df = log.get_data_frames()[0]

            if df.empty:
                print(f"Sin datos para {season}" + (f" ({fecha})" if fecha else ""))
                continue

            # INSERT OR IGNORE para evitar UNIQUE constraint al re-ejecutar
            insertados = 0
            for _, row in df.iterrows():
                try:
                    conn.execute(
                        "INSERT OR IGNORE INTO nba_players_games VALUES ({})".format(
                            ','.join(['?' for _ in row])
                        ),
                        tuple(row)
                    )
                    insertados += 1
                except Exception as e:
                    print(f"  Error fila: {e}")
            conn.commit()

            print(f"Hecho: {insertados} registros de jugadores añadidos.")
            time.sleep(3)

        except Exception as e:
            print(f"Error en {season}: {e}")
            time.sleep(10)

    conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extractor de boxscores de jugadores NBA")
    parser.add_argument("--fecha", type=str, default=None,
                        help="Filtrar solo una jornada (formato YYYY-MM-DD)")
    parser.add_argument("--ano_inicio", type=int, default=1980)
    parser.add_argument("--ano_fin", type=int, default=2026)
    args = parser.parse_args()

    print("--- Extractor de Jugadores Dos Aros ---")
    descargar_boxscores_jugadores(args.ano_inicio, args.ano_fin, fecha=args.fecha)
