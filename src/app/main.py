import streamlit as st
import pandas as pd
import altair as alt
import sqlite3
import os
import plotly.express as px
import plotly.graph_objects as go
from google import genai
from dotenv import load_dotenv

# 1. Configuración de Seguridad y Entorno
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
LOCAL_DB = "/mnt/nba_data/dosaros_local.db"
client = genai.Client(api_key=API_KEY)

st.set_page_config(page_title="Proyecto Dos Aros", page_icon="🏀", layout="wide")

# 2. Estilo CSS para look "Flat & Light"
st.markdown("""
<style>
    .main { background-color: #FDFDFD; }
    h1, h2, h3 { color: #4A4A4A; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; font-weight: 300; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; border-bottom: 1px solid #E0E0E0; }
    .stTabs [data-baseweb="tab"] { 
        height: 50px; 
        background-color: transparent; 
        border: none; 
        color: #888; 
        font-weight: 400;
    }
    .stTabs [aria-selected="true"] { 
        color: #4A4A4A !important; 
        border-bottom: 2px solid #88D4AB !important; 
    }
</style>
""", unsafe_allow_stdio=True)

# --- FUNCIONES DE APOYO ---

def dibujar_pista_flat(fig):
    """Añade líneas de pista minimalistas al gráfico de Plotly."""
    # Aro y Tablero (Escala 0-100)
    fig.add_shape(type="circle", x0=47, y0=40, x1=53, y1=60, line=dict(color="#D1D1D1", width=1))
    fig.add_shape(type="line", x0=40, y0=30, x1=60, y1=30, line=dict(color="#D1D1D1", width=1))
    # Zona (Llave)
    fig.add_shape(type="rect", x0=30, y0=0, x1=70, y1=190, line=dict(color="#E0E0E0", width=1))
    # Línea de tres
    fig.add_shape(type="path", path="M 10 0 L 10 140 Q 50 250 90 140 L 90 0", line=dict(color="#E0E0E0", width=1))
    return fig

# --- CARGA DE DATOS (NBA) ---
@st.cache_data
def cargar_datos_nba():
    conn = sqlite3.connect(LOCAL_DB)
    df_g = pd.read_sql("SELECT * FROM nba_games LIMIT 1000", conn)
    df_p = pd.read_sql("SELECT * FROM nba_players_games LIMIT 5000", conn)
    conn.close()
    return df_g, df_p

df_games, df_players = cargar_datos_nba()

# --- ESTRUCTURA DE PESTAÑAS ---
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Dashboard Global", "Eficiencia", "Equipos", "Analista IA", "Explorador EuroLeague", "Configuración"
])

with tab1:
    st.header("Resumen de Actividad")
    c1, c2, c3 = st.columns(3)
    c1.metric("Partidos NBA", f"{len(df_games):,}")
    try:
        conn = sqlite3.connect(LOCAL_DB)
        total_euro = conn.execute("SELECT COUNT(*) FROM euro_pbp").fetchone()[0]
        conn.close()
        c2.metric("Eventos EuroLeague", f"{total_euro:,}")
    except:
        c2.metric("Eventos EuroLeague", "0")
    c3.metric("Jugadores", f"{df_players['player_id'].nunique():,}")

with tab5:
    st.header("🎯 Análisis de Tiro: EuroLeague")
    try:
        conn = sqlite3.connect(LOCAL_DB)
        euro_players = pd.read_sql("SELECT DISTINCT player_id FROM euro_pbp WHERE player_id IS NOT NULL", conn)
        
        col_in, col_ch = st.columns([1, 3])
        with col_in:
            p_sel = st.selectbox("Selecciona Jugador:", euro_players['player_id'].sort_values())
            
        if p_sel:
            query = f"SELECT x_norm, y_norm, action_type FROM euro_pbp WHERE player_id = '{p_sel}'"
            df_s = pd.read_sql(query, conn)
            
            if not df_s.empty:
                df_s['Resultado'] = df_s['action_type'].apply(
                    lambda x: 'Acierto' if any(w in x for w in ['Made', 'Dunk', 'Layup', 'Score']) else 'Fallo'
                )
                
                fig = px.scatter(
                    df_s, x='x_norm', y='y_norm', color='Resultado',
                    color_discrete_map={'Acierto': '#88D4AB', 'Fallo': '#FF8787'},
                    range_x=[0, 100], range_y=[0, 1000], template="plotly_white"
                )
                fig = dibujar_pista_flat(fig)
                fig.update_layout(height=700, showlegend=True,
                                  xaxis=dict(visible=False), yaxis=dict(visible=False))
                st.plotly_chart(fig, use_container_width=True)
        conn.close()
    except Exception as e:
        st.error(f"Error: {e}")

with tab6:
    st.header("Configuración")
    st.write(f"DB: `{LOCAL_DB}`")
    if st.button("Check HDD"):
        st.success("Conectado") if os.path.exists(LOCAL_DB) else st.error("No montado")