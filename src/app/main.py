import streamlit as st
import pandas as pd
import altair as alt
from src.database.supabase_client import get_supabase_client
from src.etl.nba_games_extractor import sync_nba_games

st.set_page_config(page_title="Proyecto Dos Aros", layout="wide")

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

st.title("Proyecto Dos Aros 🏀")

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

tab1, tab2, tab3 = st.tabs(["Resultados", "Análisis de Jugadores", "Equipos"])

with tab1:
    if not df_games.empty:
        df_games['game_date'] = pd.to_datetime(df_games['game_date'])
        df_games['Local'] = df_games['home_team_id'].map(team_map)
        df_games['Visitante'] = df_games['visitor_team_id'].map(team_map)
        df_display = df_games.sort_values(by='game_date', ascending=False)
        st.dataframe(df_display[['game_date', 'Local', 'home_points', 'Visitante', 'visitor_points']], use_container_width=True)

with tab2:
    if not df_players.empty and not df_games.empty:
        game_ids = df_games['game_id'].tolist()
        df_view = df_players[df_players['game_id'].isin(game_ids)].copy()
        
        if not df_view.empty:
            st.subheader("Eficiencia vs Volumen de Anotación")
            
            # Gráfico de dispersión con Altair
            chart = alt.Chart(df_view).mark_circle(size=100).encode(
                x=alt.X('field_goals_pct:Q', title='Eficiencia (FG%)', scale=alt.Scale(domain=[0, 1])),
                y=alt.Y('points:Q', title='Puntos Anotados'),
                color=alt.Color('team_id:N', legend=None),
                tooltip=['player_name', 'points', 'field_goals_pct', 'minutes']
            ).interactive().properties(height=400)
            
            st.altair_chart(chart, use_container_width=True)
            
            st.subheader("Top 10 Anotadores")
            df_view['Equipo'] = df_view['team_id'].map(team_map)
            st.table(df_view.sort_values(by='points', ascending=False).head(10)[['player_name', 'Equipo', 'points', 'minutes']])
    else:
        st.info("Sincroniza datos para ver el análisis de jugadores.")

with tab3:
    st.dataframe(df_teams, use_container_width=True)