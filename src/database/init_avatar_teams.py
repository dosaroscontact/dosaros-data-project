"""
init_avatar_teams.py — Crea la tabla avatar_teams en SQLite.

Uso:
    python src/database/init_avatar_teams.py
"""

import os
import sqlite3
from pathlib import Path

DB_PATH = os.getenv("LOCAL_DB", "/mnt/nba_data/dosaros_local.db")


def crear_tabla_avatar_teams():
    print(f"Conectando a BD: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS avatar_teams (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            team_code     TEXT NOT NULL,
            liga          TEXT NOT NULL,
            team_name     TEXT NOT NULL,
            color_a       TEXT,
            color_b       TEXT,
            color_c       TEXT,
            color_d       TEXT,
            postura       TEXT,
            vestimenta    TEXT,
            decorado      TEXT,
            tipo_logo     TEXT,
            variacion_idx INTEGER NOT NULL DEFAULT 1,
            UNIQUE(team_code, variacion_idx)
        )
    """)

    c.execute("CREATE INDEX IF NOT EXISTS idx_avatar_liga      ON avatar_teams (liga)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_avatar_teamcode  ON avatar_teams (team_code)")

    conn.commit()
    conn.close()
    print("Tabla avatar_teams creada (o ya existía).")


if __name__ == "__main__":
    crear_tabla_avatar_teams()
