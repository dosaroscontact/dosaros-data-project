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
    div[data-testid="stMetricValue"] { color: #4A4A4A; }
    </style>
    """, unsafe_allow_stdio=True)

# --- FUNCIONES DE APOYO ---

def obtener_sql_ia(pregunta):
    contexto = """
    Eres experto en SQLite. Tablas: 'nba_games' y 'nba_players_games'.
    Reglas: No uses YEAR(). Filtra año con LIKE '%AÑO'.
    Salida: Solo SQL plano sin markdown.
    """
    prompt = f"{contexto}\n\nPregunta: {pregunta}"
    response = client.models.generate_content(model="gemini-flash-latest", contents=prompt)
    return response.text.replace("```sql", "").replace("```", "").strip()

def dibujar_pista_flat(fig):
    """Añade líneas de pista minimalistas al gráfico de Plotly."""
    # Aro y Tablero (Coordenadas escaladas a 0-100 x 0-1000)
    fig.add_shape(type="circle", x0=47, y0=40, x1=53, y1=60, line=dict(color="#D1D1D1", width=1))
    fig.add_shape(type="line", x0=40, y0=30, x1=60, y1=30, line=dict(color="#D1D1D1", width=1))
    # Zona (Llave)
    fig.add_shape(type="rect", x0=30, y0=0, x1=70, y1=190, line=dict(color="#E0E0E0", width=1))
    # Línea de tres (Arco simplificado)
    fig.add_shape(type="path", 
                  path="M 10 0 L 10 140 Q 50 250 90 140 L 90 0", 
                  line=dict(color="#E0E0E0", width=1))
    return fig

# --- CARGA DE DATOS INICIAL (NBA) ---
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
    col1, col2, col3 = st.columns(3)
    
    # Métricas con estilo limpio
    with col1:
        st.metric("Partidos NBA", f"{len(df_games):,}")
    with col2:
        try:
            conn = sqlite3.connect(LOCAL_DB)
            total_euro = conn.execute("SELECT COUNT(*) FROM euro_pbp").fetchone()[0]
            conn.close()
            st.metric("Eventos EuroLeague", f"{total_euro:,}")
        except:
            st.metric("Eventos EuroLeague", "0")
    with col3:
        st.metric("Jugadores Procesados", f"{df_players['player_id'].nunique():,}")

    st.subheader("Últimos Partidos NBA")
    st.dataframe(df_games.tail(10), use_container_width=True)

with tab2:
    st.header("Eficiencia vs Volumen (NBA)")
    if not df_players.empty:
        chart = alt.Chart(df_players).mark_circle(size=100, opacity=0.6).encode(
            x=alt.X('field_goals_pct:Q', title='FG%'),
            y=alt.Y('points:Q', title='Puntos'),
            color=alt.value('#88D4AB'),
            tooltip=['player_name', 'points']
        ).interactive().properties(height=500)
        st.altair_chart(chart, use_container_width=True)

with tab3:
    st.header("Estadísticas por Equipo")
    equipo = st.selectbox("Selecciona un equipo:", df_games['home_team'].unique())
    df_eq = df_games[df_games['home_team'] == equipo]
    st.line_chart(df_eq['home_points'])

with tab4:
    st.header("Analista IA")
    st.info("Consulta la base de datos usando lenguaje natural.")
    pregunta = st.text_input("Haz tu pregunta técnica:", placeholder="Ej: ¿Qué jugador anotó más puntos en 2024?")
    
    if pregunta:
        sql = obtener_sql_ia(pregunta)
        st.code(sql, language="sql")
        try:
            conn = sqlite3.connect(LOCAL_DB)
            res = pd.read_sql(sql, conn)
            conn.close()
            st.write(res)
        except Exception as e:
            st.error(f"Error en consulta: {e}")

with tab5:
    st.header("🎯 Análisis de Tiro: EuroLeague")
    st.markdown("Visualización de coordenadas normalizadas sobre pista minimalista.")
    
    try:
        conn = sqlite3.connect(LOCAL_DB)
        # Cargamos jugadores disponibles en la tabla de Euroleague
        euro_players = pd.read_sql("SELECT DISTINCT player_id FROM euro_pbp WHERE player_id IS NOT NULL", conn)
        
        if not euro_players.empty:
            col_input, col_chart = st.columns([1, 3])
            
            with col_input:
                p_sel = st.selectbox("Selecciona Jugador:", euro_players['player_id'].sort_values())
                
            if p_sel:
                # Traemos los tiros normalizados
                query = f"SELECT x_norm, y_norm, action_type FROM euro_pbp WHERE player_id = '{p_sel}'"
                df_s = pd.read_sql(query, conn)
                
                if not df_s.empty:
                    # Lógica de acierto/fallo
                    df_s['Resultado'] = df_s['action_type'].apply(
                        lambda x: 'Acierto' if any(word in x for word in ['Made', 'Dunk', 'Layup', 'Score']) else 'Fallo'
                    )
                    
                    fig = px.scatter(
                        df_s, x='x_norm', y='y_norm', color='Resultado',
                        color_discrete_map={'Acierto': '#88D4AB', 'Fallo': '#FF8787'},
                        range_x=[0, 100], range_y=[0, 1000],
                        template="plotly_white"
                    )
                    
                    fig = dibujar_pista_flat(fig)
                    
                    fig.update_layout(
                        showlegend=True,
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                        plot_bgcolor='rgba(0,0,0,0)',
                        xaxis=dict(showgrid=False, zeroline=False, visible=False),
                        yaxis=dict(showgrid=False, zeroline=False, visible=False),
                        height=700,
                        margin=dict(l=0, r=0, t=50, b=0)
                    )
                    
                    fig.update_traces(marker=dict(size=10, opacity=0.7, line=dict(width=1, color='White')))
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("No hay datos de tiro registrados para este jugador.")
        else:
            st.info("Aún no hay datos de EuroLeague procesados en la base de datos.")
        conn.close()
    except Exception as e:
        st.error(f"Error al conectar con la base de datos: {e}")

with tab6:
    st.header("Configuración")
    st.write(f"Ruta Base de Datos: `{LOCAL_DB}`")
    if st.button("Verificar Conexión HDD"):
        if os.path.exists(LOCAL_DB):
            st.success("Conexión con HDD externo establecida correctamente.")
        else:
            st.error("No se encuentra el archivo de base de datos en /mnt/nba_data/")