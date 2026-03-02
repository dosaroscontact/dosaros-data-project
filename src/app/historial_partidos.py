from nba_api.stats.endpoints import leaguegamefinder
import pandas as pd
import sqlite3
import time

def descargar_periodo_historico(ano_inicio, ano_fin):
    # Ruta al archivo en el disco duro externo
    db_path = "/mnt/nba_data/dosaros_local.db"
    
    for ano in range(ano_inicio, ano_fin):
        # Generar formato: 1980-81, 1981-82, etc.
        sig_ano = str(ano + 1)[-2:]
        season_str = f"{ano}-{sig_ano}"
        
        print(f"Descargando temporada {season_str}...")
        
        try:
            # Petición a la API
            query = leaguegamefinder.LeagueGameFinder(
                season_nullable=season_str,
                league_id_nullable='00',
                season_type_nullable='Regular Season'
            )
            
            df = query.get_data_frames()[0]
            
            # Guardar en la tabla existente 'nba_games'
            conexion = sqlite3.connect(db_path)
            df.to_sql('nba_games', conexion, if_exists='append', index=False)
            conexion.close()
            
            print(f"Éxito: {len(df)} registros añadidos.")
            
            # Pausa de seguridad para evitar bloqueos (Rate Limiting)
            time.sleep(2.5)
            
        except Exception as e:
            print(f"Error en temporada {season_str}: {e}")
            time.sleep(10) # Pausa más larga si hay error

# Ejecución desde 1980 hasta la actualidad
descargar_periodo_historico(1980, 2026)