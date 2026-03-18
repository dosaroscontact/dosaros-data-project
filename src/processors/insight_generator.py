import sqlite3
import pandas as pd
import os
from src.automation.bot_manager import enviar_mensaje

DB_PATH = "/mnt/nba_data/dosaros_local.db"

def buscar_perlas_nba():
    if not os.path.exists(DB_PATH): return []
    conn = sqlite3.connect(DB_PATH)
    
    # Columnas exactas de tu PRAGMA
    query = """
    SELECT PLAYER_NAME, TEAM_ABBREVIATION, FG3A
    FROM nba_players_games
    WHERE GAME_DATE = date('now', '-1 day') AND FG3A >= 10
    ORDER BY FG3A DESC LIMIT 3
    """
    try:
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        # Fallback si aún no hay partidos de "hoy" (ayer en USA)
        if df.empty:
            conn = sqlite3.connect(DB_PATH)
            df = pd.read_sql_query("SELECT PLAYER_NAME, TEAM_ABBREVIATION, FG3A FROM nba_players_games WHERE FG3A >= 12 ORDER BY GAME_DATE DESC LIMIT 3", conn)
            conn.close()

        perlas = []
        msg = "📊 *Dato Dos Aros: Cazadores de Triples*\n\n"
        for _, r in df.iterrows():
            perlas.append({'nombre': r['PLAYER_NAME'], 'equipo': r['TEAM_ABBREVIATION'], 'triples': int(r['FG3A'])})
            msg += f"• {r['PLAYER_NAME']} ({r['TEAM_ABBREVIATION']}) tiró {int(r['FG3A'])} triples.\n"
        
        msg += "\n¿Quieres que genere el gráfico para Instagram?"
        enviar_mensaje(msg)
        return perlas
    except Exception as e:
        print(f"❌ Error SQL: {e}")
        return []