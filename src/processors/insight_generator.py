import sqlite3
import pandas as pd
import os
from src.automation.bot_manager import enviar_mensaje

DB_PATH = "/mnt/nba_data/dosaros_local.db"

def buscar_perlas_nba():
    """Busca hitos estadísticos usando los nombres de columna reales (PRAGMA)."""
    if not os.path.exists(DB_PATH):
        print(f"❌ Base de datos no encontrada en {DB_PATH}")
        return []

    conn = sqlite3.connect(DB_PATH)
    
    # Usamos los nombres exactos confirmados por tu comando PRAGMA
    query = """
    SELECT PLAYER_NAME, TEAM_ABBREVIATION, FG3A
    FROM nba_players_games
    WHERE GAME_DATE = date('now', '-1 day') 
    AND FG3A >= 10
    ORDER BY FG3A DESC
    LIMIT 3
    """
    
    try:
        df = pd.read_sql_query(query, conn)
        conn.close()

        if df.empty:
            # Si no hay datos de ayer (por horario), probamos con los últimos registros
            print("ℹ️ No hay triples de ayer, buscando últimos registros generales...")
            query_back = query.replace("WHERE GAME_DATE = date('now', '-1 day')", "WHERE FG3A >= 10")
            conn = sqlite3.connect(DB_PATH)
            df = pd.read_sql_query(query_back, conn)
            conn.close()

        if df.empty:
            enviar_mensaje("No he encontrado volumen de triples destacable en los datos actuales.")
            return []

        perlas = []
        mensaje_telegram = "📊 *Dato Dos Aros: Cazadores de Triples*\n\n"
        
        for _, row in df.iterrows():
            # Mapeamos las columnas de la BD a las claves que usa tu generador de imágenes
            perlas.append({
                'nombre': row['PLAYER_NAME'],
                'equipo': row['TEAM_ABBREVIATION'],
                'triples': int(row['FG3A'])
            })
            mensaje_telegram += f"• {row['PLAYER_NAME']} ({row['TEAM_ABBREVIATION']}) tiró {int(row['FG3A'])} triples.\n"

        mensaje_telegram += "\n¿Quieres que genere el gráfico para Instagram?"
        
        enviar_mensaje(mensaje_telegram)
        return perlas

    except Exception as e:
        print(f"❌ Error en insight_generator: {e}")
        return []