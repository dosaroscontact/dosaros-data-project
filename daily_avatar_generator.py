"""
Script para generar prompts de avatares diariamente.
Se ejecuta via cron job a las 8:00 AM.
"""

import subprocess
import sys
import os
from datetime import datetime

# Rutas
REPO_PATH = "/home/pi/dosaros-data-project"
DB_PATH = "/mnt/nba_data/dosaros_local.db"
LOG_PATH = f"{REPO_PATH}/logs/avatar_generation.log"

def log_message(msg):
    """Escribe en log y stdout"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_msg = f"[{timestamp}] {msg}"
    print(log_msg)
    
    with open(LOG_PATH, 'a') as f:
        f.write(log_msg + '\n')

def run_generator():
    """Ejecuta el generador de prompts"""
    try:
        log_message("🚀 Iniciando generación de prompts...")
        
        # Ejecutar script
        result = subprocess.run(
            [
                sys.executable, 
                f"{REPO_PATH}/avatar_prompt_generator.py"
            ],
            cwd=REPO_PATH,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutos max
        )
        
        if result.returncode == 0:
            log_message("✅ Prompts generados exitosamente")
            return True
        else:
            log_message(f"❌ Error en generador: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        log_message("❌ Timeout: generación tardó más de 5 minutos")
        return False
    except Exception as e:
        log_message(f"❌ Error ejecutando generador: {e}")
        return False

def send_telegram_notification(success):
    """Notifica a Telegram del resultado"""
    try:
        from src.automation.bot_manager import enviar_mensaje
        
        if success:
            msg = "✅ Prompts de avatares regenerados para hoy\n\nUsa /avatar_today para verlos"
        else:
            msg = "❌ Error regenerando prompts hoy. Revisa logs en Pi."
        
        enviar_mensaje(msg)
        log_message("📬 Notificación enviada a Telegram")
    except Exception as e:
        log_message(f"⚠️ No se pudo enviar notificación: {e}")

if __name__ == "__main__":
    try:
        # Cambiar a directorio del proyecto
        os.chdir(REPO_PATH)
        
        # Crear directorio de logs si no existe
        log_dir = os.path.dirname(LOG_PATH)
        os.makedirs(log_dir, exist_ok=True)
        
        log_message("=" * 50)
        log_message("GENERADOR DIARIO DE PROMPTS")
        log_message("=" * 50)
        
        # Ejecutar generador
        success = run_generator()
        
        # Notificar resultado
        send_telegram_notification(success)
        
        log_message("=" * 50)
        
        sys.exit(0 if success else 1)
        
    except Exception as e:
        log_message(f"❌ Error crítico: {e}")
        sys.exit(1)