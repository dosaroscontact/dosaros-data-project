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

def _snippet_cercano(tag) -> str:
    """Busca el primer párrafo de texto próximo a un titular (sibling o en el contenedor padre)."""
    # 1. Buscar <p> hermano inmediato
    siguiente = tag.find_next_sibling()
    if siguiente and siguiente.name == 'p':
        texto = siguiente.get_text(strip=True)
        if len(texto) > 30:
            return texto[:200]

    # 2. Buscar <p> dentro del contenedor padre (article, div, li…)
    padre = tag.parent
    if padre:
        parrafo = padre.find('p')
        if parrafo:
            texto = parrafo.get_text(strip=True)
            if len(texto) > 30:
                return texto[:200]

    return ""


def _construir_noticia(fuente: str, tag, base_url: str) -> Dict:
    """Construye un dict de noticia a partir de un tag de titular."""
    titulo = tag.get_text(strip=True)
    if len(titulo) < 20:
        return {}

    enlace = tag.find('a') or tag.find_parent('a')
    href = (enlace.get('href') or '') if enlace else ''
    if href.startswith('/'):
        href = base_url.rstrip('/') + href
    url = href if href.startswith('http') else base_url

    snippet = _snippet_cercano(tag)

    return {
        "fuente": fuente,
        "titulo": titulo,
        "snippet": snippet,
        "url": url,
        "fecha": datetime.now().strftime('%Y-%m-%d'),
    }


def scrapear_noticias_basketnews() -> List[Dict]:
    """Extrae titulares + snippets de BasketNews."""
    noticias = []
    try:
        resp = requests.get("https://www.basketnews.com/news", headers=_HEADERS, timeout=10)
        if resp.status_code != 200:
            return noticias
        soup = BeautifulSoup(resp.text, 'html.parser')
        for tag in soup.find_all(['h2', 'h3'], limit=15):
            n = _construir_noticia("BasketNews", tag, "https://www.basketnews.com")
            if n:
                noticias.append(n)
    except Exception as e:
        logger.warning(f"⚠️ BasketNews: {e}")
    return noticias[:5]


def scrapear_noticias_espn() -> List[Dict]:
    """Extrae titulares + snippets de ESPN NBA."""
    noticias = []
    try:
        resp = requests.get("https://www.espn.com/nba/", headers=_HEADERS, timeout=10)
        if resp.status_code != 200:
            return noticias
        soup = BeautifulSoup(resp.text, 'html.parser')
        for tag in soup.find_all(['h1', 'h2', 'h3'], limit=20):
            n = _construir_noticia("ESPN", tag, "https://www.espn.com")
            if n:
                noticias.append(n)
    except Exception as e:
        logger.warning(f"⚠️ ESPN: {e}")
    return noticias[:5]


def scrapear_noticias_eurohoops() -> List[Dict]:
    """Extrae titulares + snippets de Eurohoops."""
    noticias = []
    try:
        resp = requests.get("https://www.eurohoops.net", headers=_HEADERS, timeout=10)
        if resp.status_code != 200:
            return noticias
        soup = BeautifulSoup(resp.text, 'html.parser')
        for tag in soup.find_all(['h2', 'h3'], limit=15):
            n = _construir_noticia("Eurohoops", tag, "https://www.eurohoops.net")
            if n:
                noticias.append(n)
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
        
        # Formatea noticias con título + snippet + número de referencia para las fuentes
        bloques = []
        for i, n in enumerate(noticias, 1):
            bloque = f"[{i}] [{n['fuente']}] {n['titulo']}"
            if n.get('snippet'):
                bloque += f"\n    → {n['snippet']}"
            bloques.append(bloque)

        noticias_texto = "\n\n".join(bloques) if bloques else "Sin noticias disponibles hoy."

        # Prompt para IA — titular + snippet + referencias numeradas
        prompt = f"""Eres el analista de Dos Aros: baloncesto NBA + EuroLeague con datos, contexto y opinión.
Filosofía: "Datos primero. Contexto después. Opinión al final."
Estilo: directo, irónico, nunca genérico. Usa los hechos concretos que te doy, no inventes nada.

NOTICIAS REALES DE HOY {datetime.now().strftime('%d/%m/%Y')} (con contexto):
{noticias_texto}

TAREA — genera EXACTAMENTE esto en JSON:

1. INSIGHTS: 3 observaciones que usen los hechos del snippet para conectar con contexto histórico o tendencias.
   No repitas el titular, profundiza en lo que significa.

2. HILO X: 6 tweets basados en los hechos reales. Incluye en cada tweet el número de fuente entre corchetes, ej: [3].
   - Tweet 1: Hook con el hecho más sorprendente o contraintuitivo
   - Tweets 2-4: Desarrollo con datos concretos (nombres, cifras, contexto)
   - Tweet 5: Comparativa histórica o dato que ponga en perspectiva
   - Tweet 6: Pregunta de debate con un ángulo concreto (nunca "¿qué opináis?")
   Máximo 250 caracteres por tweet. Sin hashtags. Máximo 1 emoji por tweet.

3. REELS: 2 ideas con gancho basado en los hechos reales del snippet.

4. STORIES: 2 ideas basadas en los hechos reales.

RESPONDE SOLO con JSON válido (sin markdown, sin triple backticks):
{{
  "insights": ["insight 1", "insight 2", "insight 3"],
  "hilo_x": ["1/ tweet [N]", "2/ tweet [N]", "3/ tweet [N]", "4/ tweet [N]", "5/ tweet", "6/ tweet"],
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
        
        # Construir lista de fuentes numeradas para Telegram
        fuentes = [
            {"num": i, "fuente": n["fuente"], "titulo": n["titulo"][:60], "url": n["url"]}
            for i, n in enumerate(noticias, 1)
        ]

        return {
            "insights": datos.get("insights", []),
            "hilo_x": datos.get("hilo_x", []),
            "reels": datos.get("reels", []),
            "stories": datos.get("stories", []),
            "fuentes": fuentes,
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
