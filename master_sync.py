import os
import sys
import logging
from datetime import datetime

# 1. Configuración de rutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# 2. Importaciones

from processors.insight_generator import buscar_perlas_nba
from src.etl.pbp_extractor import descargar_pbp_por_temporada
from src.etl.jugadores_extractor import descargar_boxscores_jugadores

# 3. Configuración de Logs
logging.basicConfig(
    filename=os.path.join(BASE_DIR, 'logs/daily_sync.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def run_sync():
    print(f"🚀 Iniciando carga diaria: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    logging.info("Iniciando sincronización diaria.")

    try:
        # --- BLOQUE EUROLEAGUE ---
        print("🏀 Procesando Euroliga...")
        os.system(f"{BASE_DIR}/venv/bin/python {BASE_DIR}/src/etl/update_dosaros.py")
        
        # --- BLOQUE NBA ---
        print("🏀 Procesando NBA (PBP y Jugadores)...")
        descargar_pbp_por_temporada("224") 
        descargar_boxscores_jugadores(2024, 2025)

        # --- BLOQUE INSIGHTS ---
        print("💡 Buscando perlas para Telegram...")
        buscar_perlas_nba() # <--- Indentación corregida

        print("✅ Proceso completado con éxito.")
        logging.info("Sincronización finalizada correctamente.")

    except Exception as e:
        print(f"❌ Error durante la carga: {e}")
        logging.error(f"Error en master_sync: {e}")

if __name__ == "__main__":
    run_sync()