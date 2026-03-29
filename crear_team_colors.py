import sqlite3

conn = sqlite3.connect('/mnt/nba_data/dosaros_local.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS team_colors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team_name TEXT UNIQUE NOT NULL,
    primary_color TEXT NOT NULL,
    secondary_color TEXT NOT NULL,
    tertiary_color TEXT NOT NULL
);
''')

conn.commit()
conn.close()
print("✅ Tabla team_colors creada")