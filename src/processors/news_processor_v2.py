"""
================================================================================
NEWS_PROCESSOR_V2.PY - Procesa Noticias con IA (Versión Simplificada)
================================================================================
Función principal:
  1. Scrapeea noticias (BasketNews, ESPN, Eurohoops)
  2. Procesa con IA (Gemini/Groq)
  3. Retorna: insights + hilo X + propuestas reels/stories

Nota: Twitter scraping agregado en próxima versión (Nitter estructura compleja)

Uso:
  python news_processor_v2.py
  
  O en código:
  from src.processors.news_processor_v2 import procesar_noticias_hoy
  resultado = procesar_noticias_hoy()
================================================================================
"""

import json
import requests
from datetime import datetime, timedelta
from typing import List, Dict
import os
import sys
import logging

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Añade la raíz al path para imports correctos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


# ============================================================================
# PASO 1: SCRAPEAR NOTICIAS
# ============================================================================

def scrapear_noticias_basketnews() -> List[Dict]:
    """Scrapeea noticias de BasketNews."""
    noticias = []
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        resp = requests.get("https://www.basketnews.com/news", headers=headers, timeout=10)
        
        if resp.status_code == 200:
            keywords = ["NBA", "Euroliga", "playoffs", "trade", "lesión", "MVP"]
            content_lower = resp.text.lower()
            
            for keyword in keywords:
                if keyword.lower() in content_lower:
                    noticias.append({
                        "fuente": "BasketNews",
                        "titulo": f"Noticia destacada: {keyword}",
                        "url": "https://www.basketnews.com/news",
                        "fecha": datetime.now().strftime('%Y-%m-%d'),
                        "relevancia": "medium"
                    })
                    break
    
    except Exception as e:
        logger.warning(f"⚠️ Error scrapear BasketNews: {e}")
    
    return noticias


def scrapear_noticias_espn() -> List[Dict]:
    """Scrapeea noticias de ESPN."""
    noticias = []
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        resp = requests.get("https://www.espn.com/nba/", headers=headers, timeout=10)
        
        if resp.status_code == 200:
            noticias.append({
                "fuente": "ESPN",
                "titulo": "Últimas noticias NBA",
                "url": "https://www.espn.com/nba/",
                "fecha": datetime.now().strftime('%Y-%m-%d'),
                "relevancia": "medium"
            })
    
    except Exception as e:
        logger.warning(f"⚠️ Error scrapear ESPN: {e}")
    
    return noticias


def scrapear_noticias_eurohoops() -> List[Dict]:
    """Scrapeea noticias de Eurohoops."""
    noticias = []
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        resp = requests.get("https://www.eurohoops.net", headers=headers, timeout=10)
        
        if resp.status_code == 200:
            noticias.append({
                "fuente": "Eurohoops",
                "titulo": "Últimas noticias Euroliga",
                "url": "https://www.eurohoops.net",
                "fecha": datetime.now().strftime('%Y-%m-%d'),
                "relevancia": "medium"
            })
    
    except Exception as e:
        logger.warning(f"⚠️ Error scrapear Eurohoops: {e}")
    
    return noticias


# ============================================================================
# PASO 2: PROCESAR CON IA
# ============================================================================

def procesar_noticias_con_ia(noticias: List[Dict]) -> Dict:
    """
    Procesa noticias scrapeadas con IA para generar:
    - Insights clave
    - Hilo X
    - Propuestas de reels
    - Propuestas de stories
    
    Args:
        noticias: Lista de noticias dict
    
    Returns:
        dict con keys: insights, hilo_x, reels, stories, procesadas, fecha
    """
    try:
        from src.utils.api_manager import APIManager
        
        # Inicializa API Manager
        api = APIManager()
        
        # Formatea noticias en texto para el prompt
        noticias_texto = "\n".join([
            f"- {n['fuente']}: {n['titulo']} ({n.get('relevancia', 'unknown')})"
            for n in noticias
        ])
        
        # Prompt para IA
        prompt = f"""
Eres un analista de baloncesto profesional.

Tienes estas noticias de HOY ({datetime.now().strftime('%d/%m/%Y')}):

NOTICIAS:
{noticias_texto}

TAREA: Analiza las noticias y genera:

1. INSIGHTS: Los 3 puntos más importantes (no titulares, sino conexiones/contexto)

2. HILO X: 6 tweets formateados como hilo (cada uno es un tweet independiente)
   - Tweet 1: Hook provocador
   - Tweets 2-4: Desarrollo
   - Tweet 5: Contexto
   - Tweet 6: CTA

3. REELS: 2 propuestas de reel (título, hook, estructura)

4. STORIES: 2 propuestas de story (título, estructura de frames)

Devuelve SOLO JSON (sin markdown, sin triple backticks):
{{
  "insights": ["insight 1", "insight 2", "insight 3"],
  "hilo_x": ["tweet 1", "tweet 2", "tweet 3", "tweet 4", "tweet 5", "tweet 6"],
  "reels": [
    {{"titulo": "...", "hook": "...", "estructura": "..."}},
    {{"titulo": "...", "hook": "...", "estructura": "..."}}
  ],
  "stories": [
    {{"titulo": "...", "frames": ["frame 1", "frame 2", "frame 3"]}},
    {{"titulo": "...", "frames": ["frame 1", "frame 2", "frame 3"]}}
  ]
}}
"""
        
        logger.info("🤖 Procesando noticias con IA...")
        
        # Usa generate_text con fallback automático (gemini → groq → deepseek → kimi → venice → claude → openai)
        respuesta = api.generate_text(prompt, providers=["gemini", "groq", "deepseek", "kimi", "venice", "claude", "openai"])
        
        # Limpia markdown si existe
        respuesta_limpia = respuesta.replace('```json', '').replace('```', '').strip()
        
        # Parsea JSON
        datos = json.loads(respuesta_limpia)
        
        logger.info(f"✅ Noticias procesadas: {len(datos.get('insights', []))} insights generados")
        
        return {
            "insights": datos.get("insights", []),
            "hilo_x": datos.get("hilo_x", []),
            "reels": datos.get("reels", []),
            "stories": datos.get("stories", []),
            "procesadas": True,
            "fecha": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "error": None
        }
    
    except json.JSONDecodeError as e:
        logger.error(f"❌ Error parseando respuesta IA: {e}")
        return {
            "insights": [],
            "hilo_x": [],
            "reels": [],
            "stories": [],
            "procesadas": False,
            "fecha": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "error": f"JSON parse error: {str(e)}"
        }
    
    except Exception as e:
        logger.error(f"❌ Error procesando con IA: {e}")
        return {
            "insights": [],
            "hilo_x": [],
            "reels": [],
            "stories": [],
            "procesadas": False,
            "fecha": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "error": str(e)
        }


# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def procesar_noticias_hoy() -> Dict:
    """
    Función principal: Scrapeea y procesa noticias de hoy.
    
    Returns:
        dict con insights, hilo_x, reels, stories, procesadas, fecha
    """
    fecha_hoy = datetime.now().strftime('%d/%m/%Y')
    logger.info(f"\n📰 Procesando noticias del {fecha_hoy}...\n")
    
    # PASO 1: Scrapeea noticias
    logger.info("1️⃣  Scrapeando noticias...")
    noticias = []
    noticias += scrapear_noticias_basketnews()
    noticias += scrapear_noticias_espn()
    noticias += scrapear_noticias_eurohoops()
    
    logger.info(f"   ✅ {len(noticias)} noticias scrapeadas\n")
    
    # PASO 2: Procesa con IA
    logger.info("2️⃣  Procesando con IA...")
    resultado = procesar_noticias_con_ia(noticias)
    logger.info(f"   ✅ Procesadas: {resultado['procesadas']}\n")
    
    return resultado


# ============================================================================
# TEST / MAIN
# ============================================================================

if __name__ == "__main__":
    resultado = procesar_noticias_hoy()
    
    print("\n" + "="*60)
    print("📰 RESULTADO DEL PROCESAMIENTO")
    print("="*60)
    
    print(f"\n✅ Procesadas: {resultado['procesadas']}")
    print(f"📅 Fecha: {resultado['fecha']}")
    
    if resultado.get('error'):
        print(f"⚠️ Error: {resultado['error']}")
    else:
        print(f"\n💡 Insights ({len(resultado['insights'])}):")
        for i, insight in enumerate(resultado['insights'], 1):
            print(f"  {i}. {insight}")
        
        print(f"\n🧵 Hilo X ({len(resultado['hilo_x'])} tweets):")
        for i, tweet in enumerate(resultado['hilo_x'], 1):
            print(f"  {i}/ {tweet}\n")
        
        print(f"\n📹 Reels ({len(resultado['reels'])}):")
        for reel in resultado['reels']:
            print(f"  - {reel.get('titulo', 'Sin título')}")
            print(f"    Hook: {reel.get('hook', 'N/A')}\n")
        
        print(f"\n📖 Stories ({len(resultado['stories'])}):")
        for story in resultado['stories']:
            print(f"  - {story.get('titulo', 'Sin título')}")
            print(f"    Frames: {len(story.get('frames', []))}\n")
