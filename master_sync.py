import os
import sys
import logging
from datetime import datetime

# Configuración de rutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

try:
    from src.etl.pbp_extractor import descargar_pbp_por_temporada
    from src.etl.jugadores_extractor import descargar_boxscores_jugadores
    from src.automation.bot_manager import enviar_mensaje
    from src.processors.insight_generator import buscar_perlas_nba
except ImportError as e:
    print(f"❌ Error importando módulos: {e}")
    sys.exit(1)

def run_sync():
    inicio = datetime.now()
    print(f"🚀 Iniciando carga diaria: {inicio.strftime('%H:%M:%S')}")

    try:
        # 1. Euroliga
        print("🏀 Procesando Euroliga...")
        os.system(f"{BASE_DIR}/venv/bin/python {BASE_DIR}/src/etl/update_dosaros.py")
        
        # 2. NBA
        print("🏀 Procesando NBA...")
        descargar_pbp_por_temporada("224") 
        descargar_boxscores_jugadores(2024, 2025)

        # 3. Insights y Notificación
        print("💡 Buscando datos de valor...")
        buscar_perlas_nba()
        
        fin = datetime.now()
        duracion = str(fin - inicio).split('.')[0]
        enviar_mensaje(f"✅ *Carga Dos Aros Completada*\n• Duración: {duracion}\n• Estado: Base de Datos al día.")

    except Exception as e:
        enviar_mensaje(f"⚠️ *ERROR EN CARGA DOS AROS*\n{str(e)}")

if __name__ == "__main__":
    run_sync()