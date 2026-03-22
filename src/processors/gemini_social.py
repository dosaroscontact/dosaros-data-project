"""
================================================================================
GENERADOR DE HILO X - Proyecto Dos Aros
================================================================================
Genera un hilo de 5-6 tweets diario con:
  1. Resultados NBA destacados
  2. Resultados Euroliga destacados
  3. Comparativa NBA vs Euroliga (dato del día)
  4. Perlas de datos (cazadores de triples)
  5. Dato histórico del día
  6. Cierre con pregunta al seguidor

Flujo:
  cron → genera hilo → envía a Telegram para revisión → tú lo copias a X
================================================================================
"""

import os
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# Usar API Manager para fallback automático
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from src.utils.api_manager import APIManager

DB_PATH = os.getenv("LOCAL_DB", "/mnt/nba_data/dosaros_local.db")


# ============================================================================
# OBTENER DATOS
# ============================================================================

def get_connection():
    return sqlite3.connect(DB_PATH)


def obtener_resultados_nba(fecha=None):
    """Obtiene resultados NBA de ayer."""
    if fecha is None:
        fecha = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    try:
        conn = get_connection()
        # Intentar primero en nba_daily_results
        query = """
            SELECT home_team, away_team, home_score, away_score, winner
            FROM nba_daily_results
            WHERE game_date = ?
            ORDER BY home_score + away_score DESC
        """
        df = pd.read_sql_query(query, conn, params=[fecha])
        
        # Fallback a nba_games si está vacío
        if df.empty:
            query2 = """
                SELECT MATCHUP, PTS, WL, TEAM_ABBREVIATION
                FROM nba_games
                WHERE GAME_DATE = ?
                ORDER BY PTS DESC
            """
            df = pd.read_sql_query(query2, conn, params=[fecha])
        
        conn.close()
        return df
    except Exception as e:
        print(f"⚠️ Error NBA resultados: {e}")
        return pd.DataFrame()


def obtener_resultados_euro(fecha=None):
    """Obtiene resultados Euroliga de ayer."""
    if fecha is None:
        fecha = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    try:
        conn = get_connection()
        query = """
            SELECT home_team, away_team, score_home, score_away
            FROM euro_games
            WHERE date = ?
            ORDER BY score_home + score_away DESC
        """
        df = pd.read_sql_query(query, conn, params=[fecha])
        conn.close()
        return df
    except Exception as e:
        print(f"⚠️ Error Euro resultados: {e}")
        return pd.DataFrame()


def obtener_perlas_nba(fecha=None):
    """Obtiene los mejores cazadores de triples y actuaciones destacadas."""
    if fecha is None:
        fecha = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    try:
        conn = get_connection()
        
        # Cazadores de triples
        query_triples = """
            SELECT PLAYER_NAME, TEAM_ABBREVIATION, FG3M, FG3A, FG3_PCT, PTS
            FROM nba_players_games
            WHERE GAME_DATE = ? AND FG3A >= 7
            ORDER BY FG3M DESC
            LIMIT 3
        """
        df_triples = pd.read_sql_query(query_triples, conn, params=[fecha])
        
        # Mejores actuaciones generales
        query_top = """
            SELECT PLAYER_NAME, TEAM_ABBREVIATION, PTS, REB, AST, PLUS_MINUS
            FROM nba_players_games
            WHERE GAME_DATE = ? AND PTS >= 25
            ORDER BY PTS DESC
            LIMIT 3
        """
        df_top = pd.read_sql_query(query_top, conn, params=[fecha])
        
        # Fallback si no hay datos de ayer
        if df_triples.empty and df_top.empty:
            query_fallback = """
                SELECT PLAYER_NAME, TEAM_ABBREVIATION, FG3M, FG3A, PTS
                FROM nba_players_games
                WHERE FG3A >= 10
                ORDER BY GAME_DATE DESC, FG3M DESC
                LIMIT 3
            """
            df_triples = pd.read_sql_query(query_fallback, conn)
        
        conn.close()
        return df_triples, df_top
    except Exception as e:
        print(f"⚠️ Error perlas NBA: {e}")
        return pd.DataFrame(), pd.DataFrame()


def obtener_dato_historico():
    """Obtiene un dato curioso histórico de la base de datos."""
    try:
        conn = get_connection()
        
        # Récord de triples en un partido (histórico)
        query = """
            SELECT PLAYER_NAME, TEAM_ABBREVIATION, FG3M, FG3A, PTS, GAME_DATE
            FROM nba_players_games
            WHERE FG3M >= 10
            ORDER BY FG3M DESC
            LIMIT 1
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        print(f"⚠️ Error dato histórico: {e}")
        return pd.DataFrame()


# ============================================================================
# GENERAR HILO
# ============================================================================

def generar_hilo_x():
    """
    Genera un hilo de 5-6 tweets con datos de ayer.
    Retorna lista de tweets o string de error.
    """
    fecha_ayer = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    fecha_display = (datetime.now() - timedelta(days=1)).strftime('%d/%m/%Y')
    
    print(f"📊 Recogiendo datos del {fecha_display}...")
    
    # Recoger todos los datos
    nba_df = obtener_resultados_nba(fecha_ayer)
    euro_df = obtener_resultados_euro(fecha_ayer)
    perlas_triples, perlas_top = obtener_perlas_nba(fecha_ayer)
    historico_df = obtener_dato_historico()
    
    # Verificar que hay datos
    hay_nba = not nba_df.empty
    hay_euro = not euro_df.empty
    hay_perlas = not perlas_triples.empty or not perlas_top.empty
    
    if not hay_nba and not hay_euro:
        return "❌ No hay datos de ayer para generar el hilo."
    
    # Preparar datos para el prompt
    nba_data = nba_df.to_dict(orient='records') if hay_nba else "Sin partidos NBA ayer"
    euro_data = euro_df.to_dict(orient='records') if hay_euro else "Sin partidos Euroliga ayer"
    perlas_data = perlas_triples.to_dict(orient='records') if not perlas_triples.empty else []
    top_data = perlas_top.to_dict(orient='records') if not perlas_top.empty else []
    historico_data = historico_df.to_dict(orient='records') if not historico_df.empty else []
    
    prompt = f"""
Eres el analista de datos de Dos Aros, cuenta de baloncesto en X (Twitter).
Fecha de referencia: {fecha_display}

DATOS DISPONIBLES:
- Resultados NBA: {nba_data}
- Resultados Euroliga: {euro_data}
- Cazadores de triples NBA: {perlas_data}
- Mejores actuaciones NBA: {top_data}
- Dato histórico de la DB: {historico_data}

GENERA UN HILO DE 5 TWEETS con este esquema exacto:

TWEET 1 - Apertura impactante con el resultado más llamativo de la noche (NBA o Euro).
TWEET 2 - Resultados NBA: los 2-3 partidos más relevantes con marcadores.
TWEET 3 - Resultados Euroliga: los partidos más destacados con marcadores.
TWEET 4 - Perla de datos: el cazador de triples más destacado o mejor actuación individual.
TWEET 5 - Dato histórico curioso sacado de la base de datos. Algo que sorprenda.
TWEET 6 (opcional) - Cierre con pregunta al seguidor para generar debate.

REGLAS ESTRICTAS:
- Máximo 250 caracteres por tweet (cuenta el número 1/, 2/, etc.)
- Empieza cada tweet con su número: 1/, 2/, 3/, etc.
- Sin hashtags
- Sin emojis excesivos (máximo 1 por tweet si aporta)
- Tono directo, periodístico, con datos concretos
- Prohibido usar: además, crucial, fundamental, intrincado, profundizar, subrayar, cabe destacar
- Los números son protagonistas: marcadores, porcentajes, récords
- Separa cada tweet con una línea en blanco

FORMATO DE SALIDA: Solo los tweets, numerados, separados por línea en blanco.
"""
    
    print("🤖 Generando hilo con IA...")
    
    try:
        api = APIManager()
        hilo = api.generate_text(
            prompt=prompt,
            providers=['gemini', 'groq', 'claude']
        )
        return hilo
    except Exception as e:
        return f"❌ Error generando hilo: {e}"


# ============================================================================
# ENVIAR A TELEGRAM PARA REVISIÓN
# ============================================================================

def enviar_hilo_a_telegram(hilo: str):
    """Envía el hilo generado a Telegram para revisión."""
    try:
        from automation.bot_manager import enviar_mensaje
        
        fecha_display = (datetime.now() - timedelta(days=1)).strftime('%d/%m/%Y')
        
        cabecera = f"📝 *HILO X - {fecha_display}*\n\n"
        cabecera += "Revisa y copia a X si está bien:\n"
        cabecera += "─" * 30 + "\n\n"
        
        mensaje_completo = cabecera + hilo
        
        # Telegram tiene límite de 4096 chars por mensaje
        if len(mensaje_completo) > 4096:
            # Enviar en partes
            enviar_mensaje(cabecera + "⚠️ Hilo largo, enviando en partes...")
            
            tweets = hilo.split('\n\n')
            for tweet in tweets:
                if tweet.strip():
                    enviar_mensaje(tweet.strip())
        else:
            enviar_mensaje(mensaje_completo)
        
        print("✅ Hilo enviado a Telegram")
        return True
    except Exception as e:
        print(f"❌ Error enviando a Telegram: {e}")
        return False


# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def ejecutar_generacion_hilo():
    """
    Función principal. Llamada desde cron o master_sync.
    Genera el hilo y lo envía a Telegram para revisión.
    """
    print("\n" + "="*50)
    print("🧵 GENERADOR DE HILO X - DOS AROS")
    print("="*50)
    
    hilo = generar_hilo_x()
    
    if hilo.startswith("❌"):
        print(hilo)
        return False
    
    print("\n--- HILO GENERADO ---")
    print(hilo)
    print("─" * 50)
    
    # Enviar a Telegram
    enviado = enviar_hilo_a_telegram(hilo)
    
    if enviado:
        print("✅ Hilo enviado a Telegram para revisión")
    else:
        print("⚠️ No se pudo enviar a Telegram, pero el hilo está generado arriba")
    
    return hilo


# ============================================================================
# EJECUCIÓN DIRECTA
# ============================================================================

if __name__ == "__main__":
    resultado = ejecutar_generacion_hilo()
    if resultado and not resultado.startswith("❌"):
        print("\n✅ Proceso completado. Revisa Telegram.")