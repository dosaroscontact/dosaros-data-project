import os
import sys
import logging
from datetime import datetime

# Añadimos las rutas para que Python encuentre tus scripts
sys.path.append(os.path.join(os.path.dirname(__file__), 'src/etl'))

# Importamos las funciones de tus archivos actuales
from pbp_extractor import descargar_pbp_por_temporada
from jugadores_extractor import descargar_boxscores_jugadores
# Para la Euroliga, llamaremos al proceso que ya tienes en update_dosaros.py

logging.basicConfig(
    filename='/home/pi/dosaros-data-project/logs/daily_sync.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def run_sync():
    print(f"🚀 Iniciando carga diaria: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    logging.info("Iniciando sincronización diaria.")

    try:
        # --- BLOQUE EUROLEAGUE ---
        # Usamos tu script update_dosaros.py que ya es muy sólido
        print("🏀 Procesando Euroliga...")
        os.system("/home/pi/dosaros-data-project/venv/bin/python /home/pi/dosaros-data-project/src/etl/update_dosaros.py")
        
        # --- BLOQUE NBA ---
        print("🏀 Procesando NBA (PBP y Jugadores)...")
        # Temporada actual 2024-25 (ID 224 para NBA API)
        descargar_pbp_por_temporada("224") 
        descargar_boxscores_jugadores(2024, 2025)

        print("✅ Proceso completado con éxito.")
        logging.info("Sincronización finalizada correctamente.")

    except Exception as e:
        print(f"❌ Error durante la carga: {e}")
        logging.error(f"Error en master_sync: {e}")

if __name__ == "__main__":
    run_sync()