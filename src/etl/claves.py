import json

# Prueba con un archivo específico de la carpeta players_data
ruta = "/home/pi/dosaros-data-project/src/etl/players/players_data/008104.json"

with open(ruta, 'r') as f:
    d = json.load(f)
    # Navegamos la ruta confirmada por tus pruebas anteriores
    alltime = d.get('pageProps', {}).get('data', {}).get('stats', {}).get('alltime', {})
    print("Claves encontradas dentro de 'alltime':", alltime.keys())
    
    if 'statTables' in alltime:
        print("Número de tablas en statTables:", len(alltime['statTables']))