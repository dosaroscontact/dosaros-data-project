"""
================================================================================
MASTER SYNC - Proyecto Dos Aros
================================================================================
Orquestador principal. Se ejecuta via cron cada día a las 9:00.

Flujo:
  1. Extrae resultados NBA de ayer (API → DB)
  2. Extrae resultados Euroliga de ayer (API → DB)
  3. Envía resumen de resultados a Telegram
  4. Detecta perlas (actuaciones destacadas) y las envía a Telegram
  5. Genera hilo X y lo envía a Telegram para revisión
  6. Genera story 1080x1920 con la perla top del día y la envía a Telegram

Cron actual:
  0 9 * * * /home/pi/dosaros-data-project/venv/bin/python
            /home/pi/dosaros-data-project/master_sync.py
            >> /home/pi/dosaros-data-project/logs/cron_output.log 2>&1
================================================================================
"""

import sys
import os
import logging
from datetime import datetime

# Añadimos la raíz al path para que funcionen los imports de src
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.etl.extract_yesterday_results import get_nba_results_yesterday
from src.etl.extract_yesterday_euro import extract_euro_results_yesterday
from src.automation.bot_manager import enviar_mensaje, enviar_grafico
from src.processors.insight_generator import buscar_perlas
from src.processors.gemini_social import ejecutar_generacion_hilo
from src.processors.image_generator import generar_imagen_perla, generar_prompt_imagefx

# Logging
logging.basicConfig(
    filename=os.path.join(os.path.dirname(__file__), 'logs/cron_output.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def main():
    inicio = datetime.now()
    fecha_str = inicio.strftime('%d/%m/%Y')
    print(f"\n{'='*50}")
    print(f"🚀 Iniciando Dos Aros Master Sync — {fecha_str}")
    print(f"{'='*50}")
    logging.info(f"Iniciando Master Sync {inicio}")

    # ── PASO 1: Extracción NBA ────────────────────────────────────────────────
    print("\n📥 Extrayendo resultados NBA...")
    try:
        reporte_nba = get_nba_results_yesterday()
        logging.info("NBA extraída correctamente")
    except Exception as e:
        reporte_nba = f"⚠️ Error extrayendo NBA: {e}"
        logging.error(f"Error NBA: {e}")

    # ── PASO 2: Extracción Euroliga ───────────────────────────────────────────
    print("📥 Extrayendo resultados Euroliga...")
    try:
        reporte_euro = extract_euro_results_yesterday()
        logging.info("Euroliga extraída correctamente")
    except Exception as e:
        reporte_euro = f"⚠️ Error extrayendo Euroliga: {e}"
        logging.error(f"Error Euroliga: {e}")

    # ── PASO 3: Mensaje de resultados a Telegram ──────────────────────────────
    print("📤 Enviando resultados a Telegram...")
    try:
        mensaje_resultados = (
            f"📌 *Dos Aros — {fecha_str}*\n\n"
            f"{reporte_nba}\n"
            f"{reporte_euro}"
        )
        enviar_mensaje(mensaje_resultados)
        logging.info("Resultados enviados a Telegram")
    except Exception as e:
        logging.error(f"Error enviando resultados a Telegram: {e}")

    # ── PASO 4: Perlas ────────────────────────────────────────────────────────
    print("💎 Detectando perlas...")
    resultado_perlas = {"nba": [], "euroliga": []}
    try:
        # buscar_perlas() envía a Telegram internamente y devuelve dict
        resultado_perlas = buscar_perlas(enviar_telegram=True) or resultado_perlas
        logging.info("Perlas procesadas y enviadas")
    except Exception as e:
        logging.error(f"Error en perlas: {e}")
        enviar_mensaje(f"⚠️ Error procesando perlas: {e}")

    # ── PASO 5: Hilo X ────────────────────────────────────────────────────────
    print("🧵 Generando hilo X...")
    try:
        # ejecutar_generacion_hilo() genera y envía a Telegram para revisión
        ejecutar_generacion_hilo()
        logging.info("Hilo X generado y enviado a Telegram")
    except Exception as e:
        logging.error(f"Error generando hilo X: {e}")
        enviar_mensaje(f"⚠️ Error generando hilo X: {e}")

    # ── PASO 6: Story del día ─────────────────────────────────────────────────
    print("📸 Generando story del día...")
    try:
        # Seleccionar la perla más destacada: primero NBA, si no Euro
        perlas_nba  = resultado_perlas.get("nba", [])
        perlas_euro = resultado_perlas.get("euroliga", [])
        perla_top   = (perlas_nba or perlas_euro or [None])[0]

        if perla_top:
            perla_imagen = {
                "equipo":          perla_top.get("equipo", "DEFAULT"),
                "dato_principal":  perla_top.get("detalle", ""),
                "subtitulo":       f"{perla_top.get('jugador', '')} — {perla_top.get('tipo', '')}",
                "contexto":        perla_top.get("partido", ""),
                "fecha":           fecha_str,
                "fuente":          "@dos_aros",
            }
            path_imagen = generar_imagen_perla(perla_imagen)
            enviar_grafico(
                path_imagen,
                caption="📸 Story del día — lista para publicar en Instagram"
            )
            logging.info(f"Story del día generada y enviada: {path_imagen}")

            # Prompt para Google ImageFX (usa perla_top para tener el campo 'tipo')
            try:
                equipo_code  = perla_top.get("equipo", "DEFAULT").upper()
                avatar_ref   = f"assets/avatars/nba_{equipo_code}.PNG"
                prompt_ifx   = generar_prompt_imagefx(perla_top, path_imagen)
                enviar_mensaje(
                    f"🎨 *Prompt para Google ImageFX*\n"
                    f"📎 Adjunta: {avatar_ref} como referencia\n\n"
                    f"{prompt_ifx}"
                )
                logging.info("Prompt ImageFX enviado a Telegram")
            except Exception as e:
                logging.error(f"Error generando prompt ImageFX: {e}")
                print(f"  Aviso: no se pudo generar prompt ImageFX: {e}")
        else:
            print("  Sin perlas disponibles para generar story.")
            logging.info("Story del día omitida: sin perlas")
    except Exception as e:
        logging.error(f"Error generando story del día: {e}")
        print(f"  ⚠️ Error en story del día: {e} — continuando.")

    # ── FIN ───────────────────────────────────────────────────────────────────
    duracion = (datetime.now() - inicio).seconds
    print(f"\n✅ Master Sync completado en {duracion}s")
    logging.info(f"Master Sync completado en {duracion}s")


if __name__ == "__main__":
    main()