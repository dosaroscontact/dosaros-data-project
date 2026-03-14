import requests
import sqlite3
import json

# Configuración del entorno
BUILD_ID = "hvGIyKafFCKSt6G5KJbO-"
DB_PATH = "/mnt/nba_data/dosaros_local.db"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Selección para el test
TEST_PLAYERS = [
    {"id": "008104", "slug": "arturs-zagars"},
    {"id": "003733", "slug": "alberto-abalde"}
]

def obtener_json(player_id, slug):
    url = f"https://www.euroleaguebasketball.net/_next/data/{BUILD_ID}/en/euroleague/players/{slug}/{player_id}.json"
    try:
        res = requests.get(url, headers=HEADERS)
        if res.status_code == 200:
            return res.json()
        print(f"Fallo en la petición para {slug}: Status {res.status_code}")
    except Exception as e:
        print(f"Error de conexión: {e}")
    return None

def ejecutar_carga_test():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Tabla de biografía enriquecida
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS euro_players_bio (
            player_id TEXT PRIMARY KEY,
            player_name TEXT,
            position TEXT,
            height INTEGER,
            club_name TEXT,
            nationality TEXT,
            image_url TEXT
        )
    """)
    
    for p in TEST_PLAYERS:
        print(f"Solicitando datos de {p['slug']}...")
        full_json = obtener_json(p['id'], p['slug'])
        
        if not full_json:
            continue
            
        # Acceso a la capa de datos pageProps -> data
        data_block = full_json.get('pageProps', {}).get('data', {})
        hero = data_block.get('hero', {})
        
        if not hero:
            print(f"No se encontró el bloque 'hero' para {p['slug']}")
            continue
            
        # Preparación de datos para la inserción
        nombre = f"{hero.get('firstName')} {hero.get('lastName')}"
        values = (
            hero.get('id'),
            nombre,
            hero.get('position'),
            hero.get('height'),
            hero.get('clubName'),
            hero.get('nationality'),
            hero.get('photo')
        )
        
        cursor.execute("""
            INSERT OR REPLACE INTO euro_players_bio 
            (player_id, player_name, position, height, club_name, nationality, image_url)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, values)
        
        # Nota técnica: Las estadísticas residen en data_block.get('stats')
        # Se pueden procesar de forma similar para tablas de promedios
        
        print(f"✅ {nombre} cargado en euro_players_bio.")

    conn.commit()
    conn.close()
    print("\nTest completado. Los datos están en la base de datos local.")

if __name__ == "__main__":
    ejecutar_carga_test()