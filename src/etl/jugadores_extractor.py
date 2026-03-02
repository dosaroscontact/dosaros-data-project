from nba_api.stats.endpoints import leaguegamelog
import pandas as pd
import sqlite3
import time
import os

def descargar_boxscores_jugadores(ano_inicio, ano_fin):
    db_path = "/mnt/nba_data/dosaros_local.db"
    
    for ano in range(ano_inicio, ano_fin):
        season = f"{ano}-{str(ano+1)[-2:]}"
        print(f"Buscando estadísticas de jugadores: Temporada {season}...")
        
        try:
            # Petición masiva por temporada para jugadores
            log = leaguegamelog.LeagueGameLog(
                season=season,
                league_id='00',
                player_or_team_abbreviation='P', # 'P' para Jugadores
                season_type_all_star='Regular Season'
            )
            
            df = log.get_data_frames()[0]
            
            # Guardamos en una tabla nueva: 'nba_players_games'
            conn = sqlite3.connect(db_path)
            df.to_sql('nba_players_games', conn, if_exists='append', index=False)
            conn.close()
            
            print(f"Hecho: {len(df)} registros de jugadores añadidos.")
            
            # Pausa para que la API de la NBA no nos bloquee
            time.sleep(3)
            
        except Exception as e:
            print(f"Error en {season}: {e}")
            time.sleep(10)

if __name__ == "__main__":
    print("--- Extractor de Jugadores Dos Aros ---")
    descargar_boxscores_jugadores(1980, 2026)