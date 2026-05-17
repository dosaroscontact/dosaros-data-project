import sqlite3
import csv

conn = sqlite3.connect('/mnt/nba_data/dosaros_local.db')
cursor = conn.cursor()

# Limpiar tabla
cursor.execute('DELETE FROM team_colors;')

# Cargar CSV
with open('assets/data/team_colors_clean.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        cursor.execute('''
            INSERT INTO team_colors (team_name, primary_color, secondary_color, tertiary_color)
            VALUES (?, ?, ?, ?)
        ''', (row['team_name'], row['primary_color'], row['secondary_color'], row['tertiary_color']))

conn.commit()
count = cursor.execute('SELECT COUNT(*) FROM team_colors').fetchone()[0]
conn.close()
print(f"✅ {count} colores cargados en BBDD")