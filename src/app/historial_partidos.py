from nba_api.stats.endpoints import leaguegamefinder
import pandas as pd
import sqlite3
import time

def descargar_temporada(season_str):
    # 1. Consultar el endpoint de búsqueda de partidos
    # '00' es el ID para la NBA
    query = leaguegamefinder.LeagueGameFinder(
        season_nullable=season_str,
        league_id_nullable='00',
        season_type_nullable='Regular Season'
    )
    
    # 2. Transformar los datos a un formato tabular (DataFrame)
    df = query.get_data_frames()[0]
    
    # 3. Almacenamiento en base de datos local
    conexion = sqlite3.connect('nba_data_warehouse.db')
    df.to_sql('partidos_nba', conexion, if_exists='append', index=False)
    conexion.close()
    
    return len(df)

# Ejemplo: Descargar la temporada 2023-24
cantidad = descargar_temporada('2023-24')
print(f"Se han descargado {cantidad} registros de partidos.")