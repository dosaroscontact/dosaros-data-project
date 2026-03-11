import sqlite3
import pandas as pd
import os

# Configuración de rutas del Proyecto Dos Aros
DB_PATH = "/mnt/nba_data/dosaros_local.db"

def crear_mapeo_jugadores():
    if not os.path.exists(DB_PATH):
        print(f"Error: No se encuentra la base de datos en {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    
    print("Analizando eventos para extraer nombres de jugadores...")
    
    # Buscamos en la tabla de eventos o boxscores (si la tienes) 
    # donde aparezcan el ID y el nombre juntos.
    # Si solo tienes IDs en euro_pbp, el siguiente paso será usar la API.
    try:
        # Intentamos obtener la relación desde los datos de juego
        query = """
        SELECT DISTINCT player_id, player_name 
        FROM euro_pbp 
        WHERE player_id IS NOT NULL AND player_name IS NOT NULL
        """
        df_players = pd.read_sql(query, conn)
        
        if df_players.empty:
            print("No se encontraron nombres en euro_pbp. Necesitaremos consultar la API.")
            # Aquí iría la lógica de consulta a euroleague_api si es necesario
            return

        # Creamos la tabla de referencia
        df_players.to_sql('euro_players_ref', conn, if_exists='replace', index=False)
        
        # Creamos un índice para que las búsquedas futuras sean instantáneas en la Pi
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_player_id ON euro_players_ref (player_id);")
        
        print(f"✅ Éxito: Se han mapeado {len(df_players)} jugadores en 'euro_players_ref'.")
        
    except Exception as e:
        print(f"Error durante el mapeo: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    crear_mapeo_jugadores()