import sqlite3
import os

DB_PATH = "/mnt/nba_data/dosaros_local.db"

def init_tables():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Tabla de partidos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS euro_games (
            game_id TEXT PRIMARY KEY,
            date TEXT,
            home_team TEXT,
            away_team TEXT,
            score_home INTEGER,
            score_away INTEGER
        )
    """)

    # Tabla de estadísticas de jugador
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS euro_players_games (
            game_id TEXT,
            player_id TEXT,
            team_id TEXT,
            pts INTEGER,
            reb INTEGER,
            ast INTEGER,
            FOREIGN KEY (game_id) REFERENCES euro_games(game_id)
        )
    """)

    # Tabla de Play-by-Play
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS euro_pbp (
            game_id TEXT,
            event_num INTEGER,
            period INTEGER,
            clock TEXT,
            action_type TEXT,
            player_id TEXT,
            x_canvas REAL,
            y_canvas REAL,
            score_home INTEGER,
            score_away INTEGER
        )
    """)

    # Índices para ganar velocidad en consultas
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_pbp_game ON euro_pbp(game_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_player_game ON euro_players_games(game_id, player_id)")

    conn.commit()
    conn.close()
    print("Tablas Euroliga creadas en SQLite.")

if __name__ == "__main__":
    init_tables()