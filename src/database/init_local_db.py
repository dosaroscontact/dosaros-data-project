import sqlite3
import os

# Definimos la ruta de la base de datos (Data Warehouse Real)
DB_PATH = "dosaros_local.db"

def init_db():
    print(f"Inicializando base de datos local en: {DB_PATH}...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Creamos la tabla principal de partidos (nba_games)
    # Usamos GAME_ID y TEAM_ID como clave compuesta implícita para evitar duplicados
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS nba_games (
            SEASON_ID TEXT,
            TEAM_ID INTEGER,
            TEAM_ABBREVIATION TEXT,
            TEAM_NAME TEXT,
            GAME_ID TEXT,
            GAME_DATE TEXT,
            MATCHUP TEXT,
            WL TEXT,
            MIN INTEGER,
            PTS INTEGER,
            FGM INTEGER,
            FGA INTEGER,
            FG_PCT REAL,
            FG3M INTEGER,
            FG3A INTEGER,
            FG3_PCT REAL,
            FTM INTEGER,
            FTA INTEGER,
            FT_PCT REAL,
            OREB INTEGER,
            DREB INTEGER,
            REB INTEGER,
            AST INTEGER,
            STL INTEGER,
            BLK INTEGER,
            TOV INTEGER,
            PF INTEGER,
            PLUS_MINUS REAL,
            PRIMARY KEY (GAME_ID, TEAM_ID)
        )
    ''')

    # Índices estratégicos para investigación (Línea 1)
    # Optimizan búsquedas por temporada y equipo
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_season ON nba_games (SEASON_ID)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_team ON nba_games (TEAM_ID)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_date ON nba_games (GAME_DATE)')

    conn.commit()
    conn.close()
    print("Estructura de tablas e índices creada con éxito.")

if __name__ == "__main__":
    init_db()