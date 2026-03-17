import sqlite3
import pandas as pd
from src.automation.bot_manager import enviar_mensaje

DB_PATH = "/mnt/nba_data/dosaros_local.db"

def buscar_perlas_nba():
    conn = sqlite3.connect(DB_PATH)
    # Buscamos jugadores que anoche tiraron +3 triples de lo que suelen tirar
    query = """
    SELECT PLAYER_NAME, FG3A, TEAM_ABBREVIATION
    FROM nba_players_games 
    WHERE GAME_DATE = (SELECT MAX(GAME_DATE) FROM nba_players_games)
    AND FG3A > 5
    ORDER BY FG3A DESC LIMIT 3;
    """
    df = pd.read_sql(query, conn)
    conn.close()

    if not df.empty:
        msg = "🎯 *Dato Dos Aros: Cazadores de Triples*\n\n"
        for _, row in df.iterrows():
            msg += f"• *{row['PLAYER_NAME']}* ({row['TEAM_ABBREVIATION']}) tiró {int(row['FG3A'])} triples anoche.\n"
        msg += "\n¿Quieres que genere el gráfico para Instagram?"
        enviar_mensaje(msg)
    else:
        enviar_mensaje("Carga terminada. No he encontrado datos anómalos hoy.")

if __name__ == "__main__":
    buscar_perlas_nba()