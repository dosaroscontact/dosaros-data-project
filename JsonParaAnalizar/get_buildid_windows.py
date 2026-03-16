import re
import requests

# Obtener buildId desde Windows
r = requests.get(
    "https://www.euroleaguebasketball.net/euroleague/",
    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"}
)

m = re.search(r'"buildId":"(.*?)"', r.text)
if m:
    build_id = m.group(1)
    print(f"BuildId encontrado: {build_id}")
    print()
    print("Ejecuta esto en la Pi:")
    print(f'  echo "{build_id}" > ~/dosaros-data-project/data/raw/.buildid_cache')
else:
    print(f"No encontrado. HTTP {r.status_code}")
    print(r.text[:500])
