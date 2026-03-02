import streamlit as st
import pandas as pd
import altair as alt
import sqlite3
import os
from google import genai
from dotenv import load_dotenv
from src.database.supabase_client import get_supabase_client
from src.etl.nba_games_extractor import sync_nba_games

# 1. Configuración de Seguridad y Entorno
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
LOCAL_DB = "/mnt/nba_data/dosaros_local.db" # Tu base de datos del HDD
client = genai.Client(api_key=API_KEY)

st.set_page_config(page_title="Proyecto Dos Aros", page_icon="🏀", layout="wide")

# --- LÓGICA DEL ANALISTA IA (MOTOR LOCAL) ---
def obtener_sql_ia(pregunta):
    contexto = """
    Eres experto en SQLite. Tablas: 'nba_games' (equipos) y 'nba_players_games' (jugadores).
    Reglas: No uses YEAR(). Filtra año con LIKE '%AÑO'.
    Fase: Regular (LIKE '2%'), Playoffs (LIKE '4%').
    Salida: Solo SQL plano sin markdown.
    """
    prompt = f"{contexto}\n\nPregunta: {pregunta}"
    response = client.models.generate_content(model="gemini-flash-latest", contents=prompt)
    return response.text.replace("```sql", "").replace("```", "").strip()

def consultar_db_local(sql):
    try:
        conn = sqlite3.connect(LOCAL_DB)
        df = pd.read_sql_query(sql, conn)
        conn.close()
        return df
    except Exception as e:
        return f"Error SQL: {e}"

# --- SIDEBAR EXISTENTE ---
with st.sidebar:
    st.header("Configuración")
    temporada = st.selectbox(
        "Temporada NBA",
        options=["2025-26", "2024-25", "2023-24", "2022-23"],
        index=0
    )
    
    if st.button(f"Sincronizar {temporada}"):
        with st.spinner("Actualizando base de datos..."):
            sync_nba_games(temporada)
            st.success("Sincronización finalizada")
            st.cache_data.clear()
            st.rerun()
    
    st.divider()
    st.info(f"BBDD Local: {os.path.getsize(LOCAL_DB)/(1024*1024):.1f} MB")

st.title("Proyecto Dos Aros 🏀")

# --- CARGA DE DATOS (SUPABASE) ---
@st.cache_data
def load_data(table_name, season_filter=None):
    try:
        supabase = get_supabase_client()
        if table_name == "nba_games" and season_filter:
            year_val = int(season_filter.split('-')[0])
            response = supabase.table(table_name).select("*").eq("season", year_val).execute()
        else:
            response = supabase.table(table_name).select("*").execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        return pd.DataFrame()

df_teams = load_data("nba_teams")
df_games = load_data("nba_games", temporada)
df_players = load_data("nba_player_stats")

team_map = dict(zip(df_teams['id'], df_teams['full_name'])) if not df_teams.empty else {}

# Métricas rápidas
col1, col2, col3 = st.columns(3)
col1.metric("Equipos", len(df_teams))
col2.metric("Partidos", len(df_games))
col3.metric("Acciones de Jugadores", len(df_players))

# --- TABS (AÑADIMOS EL ANALISTA) ---
tab1, tab2, tab3, tab4 = st.tabs(["Resultados", "Análisis de Jugadores", "Equipos", "🕵️ Analista IA"])

with tab1:
    if not df_games.empty:
        df_games['game_date'] = pd.to_datetime(df_games['game_date'])
        df_games['Local'] = df_games['home_team_id'].map(team_map)
        df_games['Visitante'] = df_games['visitor_team_id'].map(team_map)
        df_display = df_games.sort_values(by='game_date', ascending=False)
        st.dataframe(df_display[['game_date', 'Local', 'home_points', 'Visitante', 'visitor_points']], use_container_width=True)

with tab2:
    # ... (Mantenemos tu lógica de Altair intacta)
    if not df_players.empty and not df_games.empty:
        st.subheader("Eficiencia vs Volumen de Anotación")
        game_ids = df_games['game_id'].tolist()
        df_view = df_players[df_players['game_id'].isin(game_ids)].copy()
        
        chart = alt.Chart(df_view).mark_circle(size=100).encode(
            x=alt.X('field_goals_pct:Q', title='Eficiencia (FG%)', scale=alt.Scale(domain=[0, 1])),
            y=alt.Y('points:Q', title='Puntos Anotados'),
            color=alt.Color('team_id:N', legend=None),
            tooltip=['player_name', 'points', 'field_goals_pct']
        ).interactive().properties(height=400)
        st.altair_chart(chart, use_container_width=True)

with tab3:
    st.dataframe(df_teams, use_container_width=True)

with tab4:
    st.header("Consulta a la Gema")
    st.write("Usa lenguaje natural para interrogar la base de datos histórica (1980-2025).")
    
    pregunta = st.text_input("Haz tu pregunta técnica:", placeholder="Ej: ¿Qué jugador anotó más puntos en un partido en los 90?")
    
    if pregunta:
        with st.spinner("Traduciendo a SQL..."):
            sql = obtener_sql_ia(pregunta)
            st.code(sql, language="sql")
            
            res = consultar_db_local(sql)
            if isinstance(res, pd.DataFrame):
                st.table(res)
            else:
                st.error(res)