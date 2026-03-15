import json

ruta = "/home/pi/dosaros-data-project/src/etl/players/players_data/008104.json"
with open(ruta, 'r') as f:
    d = json.load(f)
    # Buscamos dónde cuelga 'alltime' o 'statTables'
    pp = d.get('pageProps', {})
    data = pp.get('data', {})
    print("Claves en pageProps:", pp.keys())
    print("Claves en pageProps['data']:", data.keys())
    if 'alltime' in data:
        print("Claves en alltime:", data['alltime'].keys())