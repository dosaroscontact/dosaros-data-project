import psycopg2

# Configuración de tu Raspberry Pi
config = {
    "host": "192.168.1.136",
    "database": "proyecto_dos_aros",
    "user": "postgres",
    "password": "tu_password_aqui" # La que pusiste en el comando de Docker
}

def crear_tablas():
    try:
        conn = psycopg2.connect(**config)
        cur = conn.cursor()
        
        # Tablas maestras
        queries = [
            """CREATE TABLE IF NOT EXISTS nba_teams (
                id BIGINT PRIMARY KEY,
                full_name TEXT,
                abbreviation TEXT,
                city TEXT
            );""",
            """CREATE TABLE IF NOT EXISTS nba_games (
                game_id TEXT PRIMARY KEY,
                game_date DATE,
                home_team_id BIGINT REFERENCES nba_teams(id),
                visitor_team_id BIGINT,
                home_points INT,
                visitor_points INT,
                season INT
            );""",
            """CREATE TABLE IF NOT EXISTS nba_player_stats (
                id SERIAL PRIMARY KEY,
                game_id TEXT REFERENCES nba_games(game_id),
                player_name TEXT,
                points INT,
                rebounds INT,
                assists INT,
                minutes TEXT
            );"""
        ]
        
        for q in queries:
            cur.execute(q)
            
        conn.commit()
        print("✅ Estructura creada con éxito en la Raspberry Pi.")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ Error al conectar: {e}")

crear_tablas()