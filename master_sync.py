import sys
import os
from datetime import datetime
# En master_sync.py, añade la importación:
from src.processors.gemini_social import generar_hilo_resultados

# Añadimos la raíz al path para que funcionen los imports de src
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.etl.extract_yesterday_results import get_nba_results_yesterday
from src.etl.extract_yesterday_euro import extract_euro_results_yesterday
from src.automation.bot_manager import enviar_mensaje
from src.processors.insight_generator import buscar_perlas_nba

def main():
    print(f"--- Iniciando Sincronización {datetime.now()} ---")
    
    # 1. Ejecutar extractores y obtener los resultados formateados
    reporte_nba = get_nba_results_yesterday()
    reporte_euro = extract_euro_results_yesterday()
    
    # 2. Obtener las perlas (tu lógica actual)
    try:
        # Asumiendo que esta función ya devuelve un string o lista
        perlas = buscar_perlas_nba() 
    except:
        perlas = "No se han podido procesar las perlas hoy."

    # 3. Construir el mensaje final
    fecha_str = datetime.now().strftime('%d/%m/%Y')
    mensaje_final = f"📌 *Resultados Dos Aros - {fecha_str}*\n\n"
    mensaje_final += f"{reporte_nba}\n"
    mensaje_final += f"{reporte_euro}\n"
    mensaje_final += f"✨ *Perlas de la noche:*\n{perlas}"

    # 4. Envío único a Telegram
    enviar_mensaje(mensaje_final)
    # Y en la función main(), después de mensaje_final:
    hilo_x = generar_hilo_resultados()
    enviar_mensaje(f"🐦 *Propuesta de Hilo para X:*\n\n{hilo_x}")
    print("✅ Reporte enviado con éxito.")

if __name__ == "__main__":
    main()