import logging
from src.etl.extract_yesterday_results import get_nba_results_yesterday
from src.etl.extract_yesterday_euro import extract_euro_results_yesterday
from src.automation.bot_manager import enviar_mensaje
from src.processors.insight_generator import buscar_perlas_nba

def generar_reporte_mañana():
    logging.info("Iniciando proceso diario de las 9:00 AM...")

    # 1. Extracción de datos (Lo que acabamos de crear)
    # Esto guarda los datos en el HDD /mnt/nba_data/
    status_nba = get_nba_results_yesterday()
    status_euro = extract_euro_results_yesterday()

    # 2. Generación del mensaje para Telegram
    # Recuperamos las perlas (tu lógica actual)
    perlas = buscar_perlas_nba() 
    
    msg = "🏀 *PROYECTO DOS AROS - REPORTE DIARIO*\n\n"
    msg += f"✅ *Sincronización:*\n- {status_nba}\n- {status_euro}\n\n"
    
    if perlas:
        msg += perlas # Aquí asumo que buscar_perlas_nba devuelve el string formateado
    else:
        msg += "⚠️ No se detectaron perlas destacadas anoche."

    # 3. Envío final
    enviar_mensaje(msg)
    logging.info("Reporte enviado a Telegram.")

if __name__ == "__main__":
    generar_reporte_mañana()