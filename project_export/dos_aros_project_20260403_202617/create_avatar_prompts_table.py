import sqlite3

conn = sqlite3.connect('/mnt/nba_data/dosaros_local.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS avatar_prompts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team_id INTEGER NOT NULL,
    team_name TEXT NOT NULL,
    scene_type TEXT NOT NULL,
    avatar_variant INTEGER NOT NULL,
    avatar_url TEXT NOT NULL,
    logo_url TEXT NOT NULL,
    prompt_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(team_id) REFERENCES avatar_teams(id)
);
''')

conn.commit()
conn.close()
print("✅ Tabla avatar_prompts creada")