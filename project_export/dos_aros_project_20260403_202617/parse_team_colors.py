import re
import csv

with open('assets/data/team_colors.csv', 'r', encoding='utf-8') as f:
    content = f.read()

csv_data = [['team_name', 'primary_color', 'secondary_color', 'tertiary_color']]
seen = set()

# Buscar SOLO: "Nombre Equipo, A: color, B: color, C: color"
# Sin capturar el resto de la información
pattern = r'^([A-Za-z\s\(\)]+?),\s+A:\s+([^,\n]+?),\s+B:\s+([^,\n]+?),\s+C:\s+([^,\n"]+?)(?:\s|$)'

for line in content.split('\n'):
    match = re.search(pattern, line)
    if match:
        team = match.group(1).strip()
        primary = match.group(2).strip()
        secondary = match.group(3).strip()
        tertiary = match.group(4).strip().replace('(Acento)', '').strip()
        
        # Validar
        if team and primary and secondary and tertiary and len(team) > 2 and team not in seen:
            csv_data.append([team, primary, secondary, tertiary])
            seen.add(team)
            print(f"✅ {team}: {primary} | {secondary} | {tertiary}")

with open('assets/data/team_colors_clean.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerows(csv_data)

print(f"\n✅ {len(csv_data)-1} equipos parseados (limpio)")