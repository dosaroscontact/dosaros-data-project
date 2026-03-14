import sqlite3
import pandas as pd
import requests
from bs4 import BeautifulSoup

DB_PATH = "/mnt/nba_data/dosaros_local.db"

def extraer_nombres_oficial():
    # La página de todos los jugadores es la mejor fuente
    url = "https://www.euroleaguebasketball.net/euroleague/players/?seasonCode=E2024&pageType=all"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    print("Iniciando extracción desde el roster oficial...")
    
    try:
        r = requests.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # Buscamos todas las tarjetas de jugador según tu HTML
        items = soup.find_all('li', class_='all-players-list_filterListItem__UlZLg')
        
        mapeo = []
        for item in items:
            link_tag = item.find('a', href=True)
            if not link_tag:
                continue
                
            # Extraemos ID del href: /en/euroleague/players/melvin-ajinca/010316/
            href = link_tag['href']
            player_id = href.strip('/').split('/')[-1]
            
            # Extraemos nombre y apellido de las clases que pasaste
            first_name = item.find('div', class_=lambda x: x and 'playerFirstName' in x)
            last_name = item.find('div', class_=lambda x: x and 'playerLastName' in x)
            
            if player_id and first_name and last_name:
                full_name = f"{first_name.text.strip()} {last_name.text.strip()}".title()
                mapeo.append({
                    'player_id': player_id, 
                    'player_name': full_name
                })

        if mapeo:
            conn = sqlite3.connect(DB_PATH)
            df = pd.DataFrame(mapeo).drop_duplicates(subset=['player_id'])
            # Guardamos en la tabla de referencia
            df.to_sql('euro_players_ref', conn, if_exists='replace', index=False)
            # Creamos el índice para que las búsquedas futuras sean instantáneas
            conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_pid ON euro_players_ref (player_id);")
            print(f"Éxito: {len(df)} jugadores guardados en euro_players_ref.")
            conn.close()
        else:
            print("No se han detectado jugadores. Revisa si el User-Agent es bloqueado.")

    except Exception as e:
        print(f"Error en el proceso: {e}")

if __name__ == "__main__":
    extraer_nombres_oficial()