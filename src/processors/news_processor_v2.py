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
from bs4 import BeautifulSoup
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

_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'
}


# ============================================================================
# PASO 1: SCRAPEAR NOTICIAS
# ============================================================================

def scrapear_noticias_basketnews() -> List[Dict]:
    """Extrae titulares reales de BasketNews."""
    noticias = []
    try:
        resp = requests.get("https://www.basketnews.com/news", headers=_HEADERS, timeout=10)
        if resp.status_code != 200:
            return noticias
        soup = BeautifulSoup(resp.text, 'html.parser')
        # Titulares en etiquetas h2, h3 o enlaces con clase de artículo
        candidatos = soup.find_all(['h2', 'h3'], limit=15)
        for tag in candidatos:
            texto = tag.get_text(strip=True)
            if len(texto) > 20:
                enlace = tag.find('a')
                url = enlace['href'] if enlace and enlace.get('href') else "https://www.basketnews.com/news"
                if url.startswith('/'):
                    url = "https://www.basketnews.com" + url
                noticias.append({
                    "fuente": "BasketNews",
                    "titulo": texto,
                    "url": url,
                    "fecha": datetime.now().strftime('%Y-%m-%d'),
                })
    except Exception as e:
        logger.warning(f"⚠️ BasketNews: {e}")
    return noticias[:5]


def scrapear_noticias_espn() -> List[Dict]:
    """Extrae titulares reales de ESPN NBA."""
    noticias = []
    try:
        resp = requests.get("https://www.espn.com/nba/", headers=_HEADERS, timeout=10)
        if resp.status_code != 200:
            return noticias
        soup = BeautifulSoup(resp.text, 'html.parser')
        candidatos = soup.find_all(['h1', 'h2', 'h3'], limit=20)
        for tag in candidatos:
            texto = tag.get_text(strip=True)
            if len(texto) > 20:
                enlace = tag.find('a')
                url = enlace['href'] if enlace and enlace.get('href') else "https://www.espn.com/nba/"
                if url.startswith('/'):
                    url = "https://www.espn.com" + url
                noticias.append({
                    "fuente": "ESPN",
                    "titulo": texto,
                    "url": url,
                    "fecha": datetime.now().strftime('%Y-%m-%d'),
                })
    except Exception as e:
        logger.warning(f"⚠️ ESPN: {e}")
    return noticias[:5]


def scrapear_noticias_eurohoops() -> List[Dict]:
    """Extrae titulares reales de Eurohoops."""
    noticias = []
    try:
        resp = requests.get("https://www.eurohoops.net", headers=_HEADERS, timeout=10)
        if resp.status_code != 200:
            return noticias
        soup = BeautifulSoup(resp.text, 'html.parser')
        candidatos = soup.find_all(['h2', 'h3'], limit=15)
        for tag in candidatos:
            texto = tag.get_text(strip=True)
            if len(texto) > 20:
                enlace = tag.find('a')
                url = enlace['href'] if enlace and enlace.get('href') else "https://www.eurohoops.net"
                if url.startswith('/'):
                    url = "https://www.eurohoops.net" + url
                noticias.append({
                    "fuente": "Eurohoops",
                    "titulo": texto,
                    "url": url,
                    "fecha": datetime.now().strftime('%Y-%m-%d'),
                })
    except Exception as e:
        logger.warning(f"⚠️ Eurohoops: {e}")
    return noticias[:5]


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
        
        # Formatea titulares reales para el prompt
        noticias_texto = "\n".join([
            f"- [{n['fuente']}] {n['titulo']}"
            for n in noticias
        ])

        if not noticias_texto.strip():
            noticias_texto = "Sin noticias disponibles hoy."

        # Prompt para IA — fuerza uso de los titulares concretos
        prompt = f"""Eres el analista de Dos Aros: baloncesto NBA + EuroLeague con datos, contexto y opinión.
Filosofía: "Datos primero. Contexto después. Opinión al final."
Estilo: directo, irónico, nunca genérico. Cita los titulares EXACTOS que te doy, no inventes noticias.

TITULARES REALES DE HOY {datetime.now().strftime('%d/%m/%Y')}:
{noticias_texto}

TAREA — genera EXACTAMENTE esto en JSON:

1. INSIGHTS: 3 observaciones que conecten los titulares con contexto o historia. Menciona nombres/equipos reales.

2. HILO X: 6 tweets basados en los titulares reales.
   - Tweet 1: Hook con un dato o frase de los titulares que sorprenda
   - Tweets 2-4: Desarrollo con los hechos reales
   - Tweet 5: Dato histórico o comparativa que contextualice
   - Tweet 6: Pregunta de debate concreta (nunca "¿qué opináis?")
   Máximo 250 caracteres por tweet. Sin hashtags. Máximo 1 emoji por tweet.

3. REELS: 2 ideas basadas en los titulares reales.

4. STORIES: 2 ideas basadas en los titulares reales.

RESPONDE SOLO con JSON válido (sin markdown, sin triple backticks):
{{
  "insights": ["insight 1", "insight 2", "insight 3"],
  "hilo_x": ["1/ tweet", "2/ tweet", "3/ tweet", "4/ tweet", "5/ tweet", "6/ tweet"],
  "reels": [
    {{"titulo": "...", "hook": "...", "estructura": "..."}},
    {{"titulo": "...", "hook": "...", "estructura": "..."}}
  ],
  "stories": [
    {{"titulo": "...", "frames": ["frame 1", "frame 2", "frame 3"]}},
    {{"titulo": "...", "frames": ["frame 1", "frame 2", "frame 3"]}}
  ]
}}"""
        
        logger.info("🤖 Procesando noticias con IA...")
        
        # Rotación diaria: cada día usa un LLM distinto → variedad de estilo + distribuye free tiers
        respuesta = api.generate_text(prompt, rotate=True)
        
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
