import json

ruta = "/home/pi/dosaros-data-project/src/etl/players/players_data/008104.json"
with open(ruta, 'r') as f:
    datos = json.load(f)
    stats = datos.get('pageProps', {}).get('data', {}).get('stats', {})
    
    if isinstance(stats, dict):
        print("Claves dentro de 'stats':", stats.keys())
    elif isinstance(stats, list):
        print("Es una lista. Primer elemento contiene:", stats[0].keys() if stats else "Lista vacía")