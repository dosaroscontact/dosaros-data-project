import logging
from src.etl.nba_sync import run_nba_daily
from src.etl.euro_sync import run_euro_daily

# Configuración de logs para ver errores desde el móvil
logging.basicConfig(
    filename='logs/daily_etl.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    logging.info("🚀 Iniciando proceso de carga diario Dos Aros")
    
    try:
        # 1. Sincronizar Euroliga (Usa tu lógica de update_dosaros.py)
        logging.info("Cargando datos de Euroliga...")
        run_euro_daily()
        
        # 2. Sincronizar NBA (Usa tu lógica de pbp_extractor.py y jugadores_extractor.py)
        logging.info("Cargando datos de NBA...")
        run_nba_daily()
        
        logging.info("✅ Carga completada con éxito")
        
    except Exception as e:
        logging.error(f"❌ Error crítico en el proceso: {str(e)}")
        # Aquí es donde el Bot de Telegram te avisaría del fallo

if __name__ == "__main__":
    main()