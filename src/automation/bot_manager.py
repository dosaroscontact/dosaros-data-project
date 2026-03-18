import time
import requests

def escuchar_confirmacion(timeout_minutos=5):
    """Limpia mensajes viejos y espera una confirmación nueva."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
    
    # 1. Limpieza inicial: obtenemos el ID del último mensaje para ignorar lo pasado
    res_inicio = requests.get(url, timeout=10).json()
    ultimo_id = 0
    if res_inicio.get("ok") and res_inicio.get("result"):
        ultimo_id = res_inicio["result"][-1]["update_id"]

    start_time = time.time()
    print(f"👂 Esperando confirmación (ID > {ultimo_id})...")
    
    while (time.time() - start_time) < (timeout_minutos * 60):
        try:
            # Solo pedimos mensajes con ID mayor al que había al empezar
            res = requests.get(url, params={"offset": ultimo_id + 1}, timeout=10).json()
            if res.get("ok") and res.get("result"):
                for update in res["result"]:
                    ultimo_id = update["update_id"]
                    texto = update.get("message", {}).get("text", "").lower()
                    if "si" in texto or "sí" in texto:
                        return True
            time.sleep(5)
        except Exception:
            time.sleep(10)
    return False