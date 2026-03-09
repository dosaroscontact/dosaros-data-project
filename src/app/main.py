import streamlit as st
import pandas as pd
import altair as alt
import sqlite3
import os
import sys
import plotly.express as px
import plotly.graph_objects as go
from google import genai
from dotenv import load_dotenv

# Add project root to path for proper imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from src.utils.mapper import normalize_euro_coords

# 1. Configuración de Seguridad y Entorno
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
LOCAL_DB = "/mnt/nba_data/dosaros_local.db"
client = genai.Client(api_key=API_KEY)

st.set_page_config(page_title="Proyecto Dos Aros", page_icon="🏀", layout="wide")

# 2. Estilo CSS - Alineado a la izquierda para evitar errores de indentación
st.markdown("""
<style>
.main { background-color: #FDFDFD; }
h1, h2, h3 { color: #4A4A4A; font-family: 'Helvetica Neue', sans-serif; font-weight: 300; }
.stTabs [data-baseweb="tab-list"] { gap: 24px; border-bottom: 1px solid #E0E0E0; }
.stTabs [data-baseweb="tab"] { height: 50px; background-color: transparent; border: none; color: #888; }
.stTabs [aria-selected="true"] { color: #4A4A4A !important; border-bottom: 2px solid #88D4AB !important; }
</style>
""", unsafe_allow_html=True)

# --- FUNCIONES DE APOYO ---

def obtener_sql_ia(pregunta):
    contexto = """
    Eres experto en SQLite. Tienes estas tablas:
    
    1. nba_games (FORMATO LARGO - una fila por equipo por partido):
       - SEASON_ID, TEAM_ID, TEAM_ABBREVIATION, TEAM_NAME
       - GAME_ID, GAME_DATE, MATCHUP, WL
       - PTS, FGM, FGA, FG_PCT, FG3M, FG3A, FG3_PCT, FTM, FTA, FT_PCT
       - OREB, DREB, REB, AST, STL, BLK, TOV, PF, PLUS_MINUS, MIN
       IMPORTANTE: NO hay columnas team_name_home/away o pts_home/away. Cada juego tiene DOS filas (una por equipo).
       
    2. nba_players_games: estadísticas de jugadores individuales
    
    3. euro_pbp: datos de EuroLeague con columnas x_norm, y_norm (coordenadas normalizadas 0-100)
    
    REGLAS:
    - No uses YEAR(). Filtra temporada con: LIKE '%AÑO' sobre SEASON_ID (ej: LIKE '%2024')
    - Para obtener ambos equipos de un partido: JOIN nba_games consigo mismo por GAME_ID
    - Para puntos totales de ambos equipos: suma los dos PTS de las dos filas por GAME_ID
    - Para EuroLeague usa euro_pbp y columas x_norm, y_norm
    
    Salida: Solo SQL plano sin markdown.
    """
    prompt = f"{contexto}\n\nPregunta: {pregunta}"
    response = client.models.generate_content(model="gemini-flash-latest", contents=prompt)
    return response.text.replace("```sql", "").replace("```", "").strip()


def dibujar_pista_flat(fig):
    """Añade líneas de pista minimalistas al gráfico de Plotly."""
    fig.add_shape(type="circle", x0=47, y0=40, x1=53, y1=60, line=dict(color="#D1D1D1", width=1))
    fig.add_shape(type="line", x0=40, y0=30, x1=60, y1=30, line=dict(color="#D1D1D1", width=1))
    fig.add_shape(type="rect", x0=30, y0=0, x1=70, y1=190, line=dict(color="#E0E0E0", width=1))
    fig.add_shape(type="path", path="M 10 0 L 10 140 Q 50 250 90 140 L 90 0", line=dict(color="#E0E0E0", width=1))
    return fig

@st.cache_data
def cargar_datos_nba():
    conn = sqlite3.connect(LOCAL_DB)
    df_g = pd.read_sql("SELECT * FROM nba_games LIMIT 1000", conn)
    df_p = pd.read_sql("SELECT * FROM nba_players_games LIMIT 5000", conn)
    conn.close()
    return df_g, df_p

# --- INICIO DE LA APP ---
df_games, df_players = cargar_datos_nba()

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Dashboard Global", "Eficiencia NBA", "Equipos", "Analista IA", "Explorador EuroLeague", "Configuración"
])

with tab1:
    st.header("Resumen de Actividad")
    c1, c2, c3 = st.columns(3)
    c1.metric("Partidos NBA", f"{len(df_games):,}")
    try:
        conn = sqlite3.connect(LOCAL_DB)
        res = conn.execute("SELECT COUNT(DISTINCT game_id), COUNT(*) FROM euro_pbp").fetchone()
        conn.close()
        c2.metric("Partidos EuroLeague", f"{res[0]:,}")
        c3.metric("Eventos Euro", f"{res[1]:,}")
    except:
        c2.metric("Partidos EuroLeague", "0")
        c3.metric("Eventos Euro", "0")
with tab2:
    st.header("Eficiencia vs Volumen (NBA)")
    if not df_players.empty:
        # Aseguramos que existan las columnas necesarias o usamos nombres genéricos
        # Si tu DB usa 'player_id' en lugar de 'player_name', lo mapeamos aquí
        df_eff = df_players.copy()
        if 'player_name' not in df_eff.columns and 'player_id' in df_eff.columns:
            df_eff['player_name'] = df_eff['player_id']

        chart = alt.Chart(df_eff).mark_circle(size=100, opacity=0.6).encode(
            x=alt.X('field_goals_pct:Q', title='FG%'),
            y=alt.Y('points:Q', title='Puntos'),
            color=alt.value('#88D4AB'),
            # Usamos :N para indicar que es un dato Nominal (texto)
            tooltip=[alt.Tooltip('player_name:N', title='Jugador'), 
                     alt.Tooltip('points:Q', title='Puntos')]
        ).interactive().properties(height=500)
        st.altair_chart(chart, use_container_width=True)
with tab3:
    st.header("Estadísticas por Equipo (NBA)")
    if not df_games.empty:
        # Usamos TEAM_NAME del esquema real de nba_games
        if 'TEAM_NAME' in df_games.columns and 'PTS' in df_games.columns:
            equipo = st.selectbox("Selecciona equipo:", df_games['TEAM_NAME'].unique())
            df_eq = df_games[df_games['TEAM_NAME'] == equipo].sort_values('GAME_DATE')
            st.line_chart(df_eq[['GAME_DATE', 'PTS']].set_index('GAME_DATE'))
        else:
            st.warning("No se encontró la columna de equipos en nba_games. Revisa el esquema de la DB.")
with tab4:
    st.header("Analista IA")
    pregunta = st.text_input("Haz tu pregunta técnica (NBA o EuroLeague):")
    if pregunta:
        sql = obtener_sql_ia(pregunta)
        st.code(sql, language="sql")
        try:
            conn = sqlite3.connect(LOCAL_DB)
            res_ia = pd.read_sql(sql, conn)
            conn.close()
            st.dataframe(res_ia, use_container_width=True)
        except Exception as e:
            st.error(f"Error en SQL: {e}")

with tab5:
    st.header("🎯 Análisis de Tiro: EuroLeague")
    try:
        conn = sqlite3.connect(LOCAL_DB)
        euro_players = pd.read_sql("SELECT DISTINCT player_id FROM euro_pbp WHERE player_id IS NOT NULL", conn)
        
        col_in, col_ch = st.columns([1, 3])
        with col_in:
            p_sel = st.selectbox("Selecciona Jugador:", euro_players['player_id'].sort_values())
            
        if p_sel:
            query = f"SELECT x_canvas, y_canvas, action_type FROM euro_pbp WHERE player_id = '{p_sel}'"
            df_s = pd.read_sql(query, conn)
            
            if not df_s.empty:
                # Normalizar coordenadas canvas a escala 0-100
                df_s['x_norm'] = df_s['x_canvas'].apply(lambda x: ((float(x) + 250) / 500) * 100 if x is not None else None)
                df_s['y_norm'] = df_s['y_canvas'].apply(lambda y: (float(y) / 1400) * 100 if y is not None else None)
                
                df_s['Resultado'] = df_s['action_type'].apply(
                    lambda x: 'Acierto' if any(w in x for w in ['Made', 'Dunk', 'Layup', 'Score']) else 'Fallo'
                )
                
                fig = px.scatter(
                    df_s, x='x_norm', y='y_norm', color='Resultado',
                    color_discrete_map={'Acierto': '#88D4AB', 'Fallo': '#FF8787'},
                    range_x=[0, 100], range_y=[0, 1000], template="plotly_white"
                )
                fig = dibujar_pista_flat(fig)
                fig.update_layout(height=700, showlegend=True, xaxis=dict(visible=False), yaxis=dict(visible=False))
                st.plotly_chart(fig, use_container_width=True)
        conn.close()
    except Exception as e:
        st.error(f"Error de conexión: {e}")

with tab6:
    st.header("Configuración")
    st.write(f"Ruta DB: `{LOCAL_DB}`")
    if st.button("Check Conexión"):
        st.success("HDD Detectado") if os.path.exists(LOCAL_DB) else st.error("HDD No Encontrado")