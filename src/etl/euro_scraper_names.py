import sqlite3
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

DB_PATH = "/mnt/nba_data/dosaros_local.db"

def scrape_jugadores_euro():
    # 1. Instalación rápida de dependencia si falta
    # pip install beautifulsoup4
    
    url = "https://www.euroleaguebasketball.net/euroleague/players/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    print("Accediendo a la web oficial de la Euroliga...")
    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        mapeo = []
        # Buscamos los enlaces de jugadores que contienen el ID y el Nombre
        # Ejemplo de link: /euroleague/players/facundo-campazzo/003941/
        links = soup.find_all('a', href=re.compile(r'/players/.*'))

        for link in links:
            href = link.get('href')
            parts = href.strip('/').split('/')
            if len(parts) >= 3:
                # El nombre suele ser el penúltimo y el ID el último
                raw_name = parts[-2].replace('-', ' ').title()
                raw_id = parts[-1]
                
                # Adaptamos al formato 'P00xxxx' que tienes en tu DB
                player_id = f"P{raw_id.zfill(6)}" 
                mapeo.append({'player_id': player_id, 'player_name': raw_name})

        if mapeo:
            conn = sqlite3.connect(DB_PATH)
            df = pd.DataFrame(mapeo).drop_duplicates(subset=['player_id'])
            df.to_sql('euro_players_ref', conn, if_exists='replace', index=False)
            print(f"✅ ¡POR FIN! {len(df)} jugadores registrados mediante scraping.")
            conn.close()
        else:
            print("❌ No se encontraron jugadores en la página. La estructura web puede haber cambiado.")

    except Exception as e:
        print(f"❌ Error durante el scraping: {e}")

if __name__ == "__main__":
    scrape_jugadores_euro()