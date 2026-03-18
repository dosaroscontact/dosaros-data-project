import sqlite3
import pandas as pd
import os
from src.automation.bot_manager import enviar_mensaje

# Ruta a tu base de datos en el HDD externo
DB_PATH = "/mnt/nba_data/dosaros_local.db"

def buscar_perlas_nba():
    """Busca hitos estadísticos y devuelve una lista para el generador de imágenes."""
    if not os.path.exists(DB_PATH):
        print(f"❌ Base de datos no encontrada en {DB_PATH}")
        return []

    conn = sqlite3.connect(DB_PATH)
    
    # Query para detectar volumen de triples inusual (ej. > 10 intentos)
    query = """
    SELECT playerName, teamAbbreviation, fga3pt
    FROM nba_players_games
    WHERE gameDate = date('now', '-1 day') 
    AND fga3pt >= 10
    ORDER BY fga3pt DESC
    LIMIT 3
    """
    
    try:
        df = pd.read_sql_query(query, conn)
        conn.close()

        if df.empty:
            enviar_mensaje("No hay hitos de volumen de triples destacables anoche.")
            return []

        # 1. Preparamos los datos para el generador de imágenes
        perlas = []
        mensaje_telegram = "📊 *Dato Dos Aros: Cazadores de Triples*\n\n"
        
        for _, row in df.iterrows():
            # Añadimos al diccionario para el gráfico
            perlas.append({
                'nombre': row['playerName'],
                'equipo': row['teamAbbreviation'],
                'triples': int(row['fga3pt'])
            })
            # Añadimos al texto para Telegram
            mensaje_telegram += f"• {row['playerName']} ({row['teamAbbreviation']}) tiró {int(row['fga3pt'])} triples.\n"

        mensaje_telegram += "\n¿Quieres que genere el gráfico para Instagram?"
        
        # 2. Enviamos el aviso a Telegram
        enviar_mensaje(mensaje_telegram)
        
        # 3. Devolvemos la lista para que master_sync sepa qué dibujar
        return perlas

    except Exception as e:
        print(f"❌ Error en insight_generator: {e}")
        return []