import csv

missing_teams = [
    "AS Monaco", "Anadolu Efes", "Charlotte Hornets", "Crvena Zvezda mts",
    "Detroit Pistons", "Dubai Basketball", "FC Bayern Munich", "Fenerbahçe Beko",
    "Hapoel Tel Aviv", "Houston Rockets", "Jugoplastika Split", "LDLC ASVEL",
    "Maccabi Playtika Tel Aviv", "Olympiacos BC", "Panathinaikos AKTOR", "Paris Basketball",
    "Partizan Mozzart Bet", "Philadelphia 76ers", "Phoenix Suns", "Portland Trail Blazers",
    "Real Madrid", "Sacramento Kings", "San Antonio Spurs", "TD Systems Baskonia",
    "Toronto Raptors", "Utah Jazz", "Valencia Basket", "Virtus Segafredo Bologna",
    "Washington Wizards", "Zalgiris Kaunas"
]

# Leer CSV existente
existing = []
with open('assets/data/team_colors_clean.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    existing = list(reader)

print(f"✅ {len(existing)} equipos actuales")
print(f"\n🎯 Agregando {len(missing_teams)} equipos faltantes:\n")

new_rows = []
for team in missing_teams:
    print(f"\n{team}:")
    primary = input("  Color primario: ")
    secondary = input("  Color secundario: ")
    tertiary = input("  Color terciario: ")
    
    new_rows.append({
        'team_name': team,
        'primary_color': primary,
        'secondary_color': secondary,
        'tertiary_color': tertiary
    })

# Combinar
all_data = existing + new_rows

# Guardar
with open('assets/data/team_colors_clean.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['team_name', 'primary_color', 'secondary_color', 'tertiary_color'])
    writer.writeheader()
    writer.writerows(all_data)

print(f"\n✅ {len(all_data)} equipos totales guardados")