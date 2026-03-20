import os
import pandas as pd
from google import genai
from dotenv import load_dotenv
from src.database.db_utils import get_db_connection

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def obtener_datos_ultima_noche():
    """Recupera los resultados que acabamos de guardar en el HDD."""
    conn = get_db_connection()
    
    # Marcadores NBA
    nba_query = "SELECT TEAM_ABBREVIATION, PTS, WL FROM nba_games WHERE GAME_DATE = date('now', '-1 day')"
    nba_df = pd.read_sql(nba_query, conn)
    
    # Marcadores Euroliga
    euro_query = "SELECT home_team, score_home, score_away, away_team FROM euro_games WHERE date = date('now', '-1 day')"
    euro_df = pd.read_sql(euro_query, conn)
    
    conn.close()
    
    return {
        "nba": nba_df.to_dict(orient='records'),
        "euro": euro_df.to_dict(orient='records')
    }

def generar_hilo_resultados():
    data = obtener_datos_ultima_noche()
    
    prompt = f"""
    Actúa como Lead Data Engineer del Proyecto Dos Aros. 
    Basado en estos resultados de ayer:
    NBA: {data['nba']}
    Euroliga: {data['euro']}
    
    Genera un hilo de X (Twitter) de 3 tweets resumiendo la jornada.
    
    REGLAS DE ESTILO:
    1. Máximo 140 caracteres por tweet.
    2. Prohibido usar: además, crucial, fundamental, intrincado, profundizar, subrayar.
    3. Usa verbos simples (es, son, tiene).
    4. Tono directo y analítico.
    5. No uses emojis ni hashtags.
    6. Formato: Tweet 1: ..., Tweet 2: ...
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Error con Gemini: {e}"

if __name__ == "__main__":
    print(generar_hilo_resultados())