import psycopg2

# Usa la IP de tu Pi y la contraseña que pusiste en el comando de Docker
conn = psycopg2.connect(
    host="192.168.1.136",
    database="proyecto_dos_aros",
    user="postgres",
    password="tu_password_aqui" 
)

cur = conn.cursor()

# Creamos las tablas en tu HDD de 149GB
tables = [
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
        player_id BIGINT,
        player_name TEXT,
        team_id BIGINT REFERENCES nba_teams(id),
        points INT,
        rebounds INT,
        assists INT,
        minutes TEXT
    );"""
]

for table in tables:
    cur.execute(table)

conn.commit()
cur.close()
conn.close()
print("Estructura local creada con éxito en la Raspberry Pi.")