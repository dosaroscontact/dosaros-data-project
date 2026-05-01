"""
================================================================================
MASTER_SYNC_V2.PY - Orquestador Diario Dos Aros (CON PASO 6)
================================================================================
Orquestador principal con 6 pasos:
  1. Extrae resultados NBA de ayer
  2. Extrae resultados Euroliga de ayer
  3. Envía resumen a Telegram
  4. Detecta perlas (BD + webs + IA)
  5. Genera hilo X (5-6 tweets)
  6. ✨ NUEVO: Genera story 1080×1920 con la perla TOP

Cron:
  0 9 * * * /home/pi/dosaros-data-project/venv/bin/python master_sync_v2.py
================================================================================
"""

import sys
import os
import logging
from datetime import datetime, timedelta

# Añadimos la raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.etl.extract_yesterday_results import get_nba_results_yesterday
from src.etl.extract_yesterday_euro import extract_euro_results_yesterday
from src.automation.bot_manager import enviar_mensaje
from src.processors.gemini_social import ejecutar_generacion_hilo

# Importar insight_generator_v2 (o fallback a insight_generator si no existe)
try:
    from src.processors.insight_generator_v2 import buscar_perlas_mejorado
except ImportError:
    from src.processors.insight_generator import buscar_perlas

# Logging
log_path = os.path.join(os.path.dirname(__file__), 'logs/cron_output.log')
os.makedirs(os.path.dirname(log_path), exist_ok=True)

logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# HELPERS
# ============================================================================

def log_paso(numero: int, mensaje: str):
    """Log formateado para cada paso."""
    print(f"PASO {numero}: {mensaje}")
    logger.info(f"PASO {numero}: {mensaje}")


# ============================================================================
# MAIN
# ============================================================================

def main():
    inicio = datetime.now()
    fecha_str = inicio.strftime('%d/%m/%Y')
    
    print("\n" + "="*60)
    print(f"🚀 Iniciando Dos Aros Master Sync V2 — {fecha_str}")
    print("="*60)
    logger.info(f"Iniciando Master Sync V2 {inicio}")
    
    # ──────────────────────────────────────────────────────────────────────
    # PASO 1: Extracción NBA
    # ──────────────────────────────────────────────────────────────────────
    log_paso(1, "Extrayendo resultados NBA...")
    reporte_nba = ""
    try:
        reporte_nba = get_nba_results_yesterday()
        logger.info("✅ NBA extraída correctamente")
    except Exception as e:
        reporte_nba = f"⚠️ Error extrayendo NBA: {e}"
        logger.error(f"Error NBA: {e}")
        print(f"❌ {reporte_nba}")
    
    # ──────────────────────────────────────────────────────────────────────
    # PASO 2: Extracción Euroliga
    # ──────────────────────────────────────────────────────────────────────
    log_paso(2, "Extrayendo resultados Euroliga...")
    reporte_euro = ""
    try:
        reporte_euro = extract_euro_results_yesterday()
        logger.info("✅ Euroliga extraída correctamente")
    except Exception as e:
        reporte_euro = f"⚠️ Error extrayendo Euroliga: {e}"
        logger.error(f"Error Euroliga: {e}")
        print(f"❌ {reporte_euro}")
    
    # ──────────────────────────────────────────────────────────────────────
    # PASO 3: Envío de Resultados a Telegram
    # ──────────────────────────────────────────────────────────────────────
    log_paso(3, "Enviando resultados a Telegram...")
    try:
        mensaje_resultados = (
            f"📌 *Dos Aros — {fecha_str}*\n\n"
            f"{reporte_nba}\n\n"
            f"{reporte_euro}"
        )
        enviar_mensaje(mensaje_resultados)
        logger.info("✅ Resultados enviados a Telegram")
    except Exception as e:
        logger.error(f"Error enviando resultados a Telegram: {e}")
        print(f"❌ Error enviando resultados: {e}")
    
    # ──────────────────────────────────────────────────────────────────────
    # PASO 4: Detección de Perlas (BD + Webs + IA)
    # ──────────────────────────────────────────────────────────────────────
    log_paso(4, "Detectando perlas...")
    perlas_resultado = None
    try:
        # Usar insight_generator_v2 si existe, si no, fallback a insight_generator
        try:
            perlas_resultado = buscar_perlas_mejorado(enviar_telegram=True)
        except NameError:
            # Fallback a versión antigua
            from src.processors.insight_generator import buscar_perlas
            perlas_resultado = buscar_perlas(enviar_telegram=True)
        
        logger.info("✅ Perlas detectadas y enviadas a Telegram")
    except Exception as e:
        logger.error(f"Error detectando perlas: {e}")
        print(f"❌ Error detectando perlas: {e}")
        try:
            enviar_mensaje(f"⚠️ Error procesando perlas: {e}")
        except:
            pass
    
    # ──────────────────────────────────────────────────────────────────────
    # PASO 5: Generación de Hilo X
    # ──────────────────────────────────────────────────────────────────────
    log_paso(5, "Generando hilo X/Twitter...")
    try:
        ejecutar_generacion_hilo()
        logger.info("✅ Hilo X generado y enviado a Telegram para revisión")
    except Exception as e:
        logger.error(f"Error generando hilo X: {e}")
        print(f"❌ Error generando hilo X: {e}")
        try:
            enviar_mensaje(f"⚠️ Error generando hilo X: {e}")
        except:
            pass
    
    # ──────────────────────────────────────────────────────────────────────
    # PASO 6: ✨ NUEVO - Generación de Story con Perla TOP
    # ──────────────────────────────────────────────────────────────────────
    log_paso(6, "Generando story 1080×1920 con perla TOP...")
    try:
        # Extraer perla top del resultado
        if perlas_resultado and isinstance(perlas_resultado, dict):
            perlas_lista = perlas_resultado.get("perlas", [])
            
            if perlas_lista:
                perla_top = perlas_lista[0]  # La primera es la más importante (ordenadas por peso)
                
                print(f"  📸 Perla seleccionada: {perla_top.get('tipo')} - {perla_top.get('jugador', 'N/A')}")
                logger.info(f"Perla TOP: {perla_top.get('tipo')} - {perla_top.get('jugador', 'N/A')}")
                
                # Intentar generar story con generar_story_perla()
                # Si no existe, log y continua
                try:
                    from src.processors.image_generator import generar_story_perla
                    ruta_story = generar_story_perla(
                        perla=perla_top,
                        fecha=datetime.now().strftime('%d/%m/%Y')
                    )
                    
                    if ruta_story and os.path.exists(ruta_story):
                        # Enviar a Telegram usando sendPhoto
                        with open(ruta_story, 'rb') as f:
                            enviar_mensaje(caption="📸 Perla del día", image=f)
                        
                        logger.info(f"✅ Story generada y enviada: {ruta_story}")
                        print(f"  ✅ Story enviada a Telegram")
                    else:
                        logger.warning("⚠️ Story no se generó correctamente")
                        print("  ⚠️ Story no se generó")
                except ImportError:
                    logger.info("ℹ️ generar_story_perla no disponible aún (TODO)")
                    print("  ℹ️ generar_story_perla no disponible (fase de desarrollo)")
                except Exception as e:
                    logger.error(f"Error generando story: {e}")
                    print(f"  ❌ Error generando story: {e}")
            else:
                logger.info("ℹ️ Sin perlas disponibles para generar story")
                print("  ℹ️ Sin perlas para story")
        else:
            logger.info("ℹ️ Sin resultado de perlas para generar story")
            print("  ℹ️ Sin resultado de perlas")
    
    except Exception as e:
        logger.error(f"Error en PASO 6: {e}")
        print(f"❌ Error en PASO 6: {e}")
    
    # ──────────────────────────────────────────────────────────────────────
    # FIN
    # ──────────────────────────────────────────────────────────────────────
    duracion = (datetime.now() - inicio).seconds
    print("\n" + "="*60)
    print(f"✅ Master Sync V2 completado en {duracion}s")
    print("="*60)
    logger.info(f"Master Sync V2 completado en {duracion}s")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical(f"❌ Error crítico en master_sync: {e}")
        print(f"\n❌ ERROR CRÍTICO: {e}")