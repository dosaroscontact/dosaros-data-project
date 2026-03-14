import sqlite3
import pandas as pd
import requests
import time

DB_PATH = "/mnt/nba_data/dosaros_local.db"
BUILD_ID = "hvGIyKafFCKSt6G5KJbO-"

# Cabeceras extraídas de tu navegación real para evitar el error 429
HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
    "x-nextjs-data": "1"
}

def descargar_todo():
    página = 0
    todos_los_jugadores = []
    
    print("Iniciando extracción por páginas...")
    
    while True:
        url = f"https://www.euroleaguebasketball.net/_next/data/{BUILD_ID}/en/euroleague/players.json?seasonCode=E2024&page={página}"
        
        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
            if r.status_code != 200:
                print(f"Final de la lista o bloqueo en página {página} (Status {r.status_code})")
                break
                
            data = r.json()
            # La ruta varía según la página, este selector es robusto:
            players = data.get('pageProps', {}).get('dataPlayers', {}).get('players', [])
            
            if not players:
                break
                
            for p in players:
                todos_los_jugadores.append({
                    'player_id': str(p.get('id')),
                    'player_name': f"{p.get('firstName', '')} {p.get('lastName', '')}".strip().title()
                })
            
            print(f"Página {página} procesada. Total acumulado: {len(todos_los_jugadores)}")
            
            # El JSON nos dice si hay más
            next_page = data.get('pageProps', {}).get('dataPlayers', {}).get('nextPage')
            if next_page is None:
                break
                
            página += 1
            # Pausa de cortesía para la Raspberry Pi y el servidor
            time.sleep(1) 
            
        except Exception as e:
            print(f"Error en página {página}: {e}")
            break

    if todos_los_jugadores:
        conn = sqlite3.connect(DB_PATH)
        df = pd.DataFrame(todos_los_jugadores).drop_duplicates(subset=['player_id'])
        df.to_sql('euro_players_ref', conn, if_exists='replace', index=False)
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_pid ON euro_players_ref (player_id);")
        print(f"✅ ¡TRABAJO TERMINADO! {len(df)} jugadores guardados en la base de datos.")
        conn.close()

if __name__ == "__main__":
    descargar_todo()