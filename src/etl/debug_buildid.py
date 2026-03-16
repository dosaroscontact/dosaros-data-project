"""
debug_buildid.py
================
Diagnóstico para encontrar el buildId en la web de EuroLeague.
Ejecutar en la Pi:  python debug_buildid.py
"""

import re
import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

URL = "https://www.euroleaguebasketball.net/euroleague/"

print(f"Conectando a {URL} ...\n")
r = requests.get(URL, headers=HEADERS)

print(f"Status code : {r.status_code}")
print(f"URL final   : {r.url}")
print(f"Tamaño HTML : {len(r.text)} chars\n")

# Buscar buildId con varios patrones
patterns = [
    r'"buildId":"(.*?)"',
    r"'buildId':'(.*?)'",
    r'buildId["\s:=]+([A-Za-z0-9_\-]+)',
    r'/_next/static/([A-Za-z0-9_\-]+)/',
]

print("=== Búsqueda de buildId ===")
for pat in patterns:
    m = re.search(pat, r.text)
    if m:
        print(f"  ✅ Patrón '{pat}' → '{m.group(1)}'")
    else:
        print(f"  ❌ Patrón '{pat}' → no encontrado")

# Mostrar primeros 2000 chars del HTML para inspección manual
print("\n=== Primeros 2000 chars del HTML ===")
print(r.text[:2000])

print("\n=== Búsqueda de '_next' en el HTML ===")
idx = r.text.find("_next")
if idx >= 0:
    print(f"  Primera aparición en posición {idx}:")
    print(f"  ...{r.text[max(0,idx-50):idx+150]}...")
else:
    print("  '_next' no aparece en el HTML")
