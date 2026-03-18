import os
import sys
import logging
from datetime import datetime

# 1. Configuración de rutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# 2. Importaciones unificadas
try:
    # Usamos la ruta completa src. para evitar errores de módulos
    from src.processors.insight_generator import buscar_perlas_nba
    from src.etl.pbp_extractor import descargar_pbp_por_temporada
    from src.etl.jugadores_extractor import descargar_boxscores_jugadores
    from automation.bot_manager import escuchar_confirmacion, enviar_grafico
    from src.app.image_generator import generar_post_triples
except ImportError as e:
    print(f"❌ Error de importación: {e}")
    sys.exit(1)

# 3. Configuración de Logs
os.makedirs(os.path.join(BASE_DIR, 'logs'), exist_ok=True)
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
        # IMPORTANTE: buscar_perlas_nba() debe retornar la lista de jugadores
        perlas_encontradas = buscar_perlas_nba() 

        # --- BLOQUE INTERACCIÓN ---
        # Solo si hay datos y confirmas por Telegram
        if perlas_encontradas and escuchar_confirmacion():
            print("🎨 Generando gráfico según Guía de Estilo...")
            path_imagen = generar_post_triples(perlas_encontradas)
            enviar_grafico(path_imagen, "Aquí tienes el post listo para Instagram. 🏀🔥")

        print("✅ Proceso completado con éxito.")
        logging.info("Sincronización finalizada correctamente.")

    except Exception as e:
        print(f"❌ Error durante la carga: {e}")
        logging.error(f"Error en master_sync: {e}")

if __name__ == "__main__":
    run_sync()