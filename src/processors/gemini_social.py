import os
import pandas as pd
from google import genai
from dotenv import load_dotenv
from src.database.db_utils import get_db_connection

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def obtener_datos_ultima_noche():
    conn = get_db_connection()
    # Usamos las fechas de ayer para NBA y Euroliga
    nba_query = "SELECT TEAM_ABBREVIATION, PTS FROM nba_games WHERE GAME_DATE = date('now', '-1 day')"
    nba_df = pd.read_sql(nba_query, conn)
    
    euro_query = "SELECT home_team, score_home, score_away, away_team FROM euro_games WHERE date = date('now', '-1 day')"
    euro_df = pd.read_sql(euro_query, conn)
    conn.close()
    
    return {
        "nba": nba_df.to_dict(orient='records'),
        "euro": euro_df.to_dict(orient='records')
    }

def generar_hilo_resultados():
    data = obtener_datos_ultima_noche()
    if not data['nba'] and not data['euro']:
        return "No hay datos de ayer para generar el hilo."

    prompt = f"""
    Eres el Lead Data Engineer de Dos Aros. Resultados de ayer:
    NBA: {data['nba']}
    Euroliga: {data['euro']}
    
    Genera un hilo de X de 3 tweets.
    REGLAS: Máximo 140 caracteres por tweet. Sin emojis. Sin hashtags. 
    Prohibido usar: además, crucial, fundamental, intrincado, profundizar, subrayar.
    Verbos simples. Tono directo.
    """
    
    try:
        # USAMOS EL MODELO QUE DIO ÉXITO EN EL TEST
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Error en Gemini: {e}"

if __name__ == "__main__":
    print("\n--- Hilo propuesto para X ---")
    print(generar_hilo_resultados())