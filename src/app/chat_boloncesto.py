import streamlit as st
import ollama
import psycopg2
import pandas as pd

st.set_page_config(page_title="Proyecto Dos Aros - IA", page_icon="🏀")
st.title("🏀 Consultor Proyecto Dos Aros")

# Configuración de conexión (Asegúrate de que la IP sea la correcta)
conn_params = {
    "host": "192.168.1.136",
    "database": "proyecto_dos_aros",
    "user": "postgres",
    "password": "tu_password_aqui"
}

def generar_sql(pregunta):
    contexto = """
    Eres un experto en SQL para la base de datos Proyecto Dos Aros.
    Tablas:
    - nba_teams (id, full_name, abbreviation, city)
    - nba_games (game_id, game_date, home_team_id, visitor_team_id, home_points, visitor_points, season)

    IMPORTANTE: 
    1. Los nombres de los equipos suelen ser completos (ej: 'Los Angeles Lakers'). 
    2. Si el usuario dice un nombre corto, usa ILIKE '%nombre%' para buscar en full_name.
    3. Para contar partidos de un equipo, recuerda que puede ser home_team_id O visitor_team_id.
    Responde solo con el código SQL.
    """
    response = ollama.chat(model='gemma2:2b', messages=[
        {'role': 'system', 'content': contexto},
        {'role': 'user', 'content': pregunta}
    ])
    return response['message']['content'].strip().replace('```sql', '').replace('```', '')

prompt = st.chat_input("Hazme una pregunta sobre los datos de la NBA...")

if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.spinner("La IA está consultando tu Raspberry Pi..."):
        try:
            # 1. Traducir a SQL
            sql = generar_sql(prompt)
            
            # 2. Consultar la Pi
            conn = psycopg2.connect(**conn_params)
            df = pd.read_sql_query(sql, conn)
            conn.close()
            
            with st.chat_message("assistant"):
                st.code(sql, language="sql")
                if not df.empty:
                    st.dataframe(df)
                else:
                    st.warning("No se encontraron datos para esa consulta.")
        except Exception as e:
            st.error(f"Error: {e}")