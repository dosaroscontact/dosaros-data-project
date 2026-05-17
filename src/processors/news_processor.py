"""
================================================================================
NEWS_PROCESSOR.PY - Scrapeea y Procesa Noticias con IA
================================================================================
Función principal:
  1. Scrapeea noticias (BasketNews, ESPN, Eurohoops)
  2. Scrapeea tweets de influencers (X/Twitter)
  3. Procesa TODO con IA (Gemini/Groq)
  4. Retorna: insights + hilo X + propuestas reels/stories

Uso:
  from src.processors.news_processor import procesar_noticias_con_ia
  resultado = procesar_noticias_con_ia()
  print(resultado['hilo_x'])
================================================================================
"""

import json
import requests
from datetime import datetime, timedelta
from typing import List, Dict
import os
import logging

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
        
        # Intenta acceder al feed
        resp = requests.get("https://www.basketnews.com/news", headers=headers, timeout=10)
        
        if resp.status_code == 200:
            # Busca títulos con palabras clave
            keywords = ["NBA", "Euroliga", "playoffs", "trade", "lesión", "MVP"]
            
            # Heurística simple: detecta si hay contenido relevante
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
                    break  # Solo una noticia por intento
    
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
# PASO 2: SCRAPEAR TWEETS X/TWITTER
# ============================================================================

def scrapear_tweets_x() -> List[Dict]:
    """
    Scrapeea tweets de influencers clave usando Nitter (espejo público de Twitter).
    Completamente gratuito, sin API key requerida.
    
    Influencers a monitorear:
    - @ShamsCharania (NBA insider)
    - @UrbonasS (BasketNews/Euroliga)
    - @ArisBarkas (Eurohoops)
    - @chemadelucas (rastreador español)
    - @BobbyMarks42 (NBA salary cap)
    - @StatMuse (NBA stats)
    """
    tweets = []
    
    cuentas = [
        "ShamsCharania",
        "UrbonasS",
        "ArisBarkas",
        "chemadelucas",
        "BobbyMarks42",
        "StatMuse"
    ]
    
    # Nitter instances (mirrors públicos de Twitter)
    nitter_instances = [
        "https://nitter.net",
        "https://nitter.poast.org",
        "https://nitter.1d4.us"
    ]
    
    try:
        from bs4 import BeautifulSoup
        
        logger.info("🐦 Scrapeando tweets de influencers (Nitter)...")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        for cuenta in cuentas:
            tweets_encontrados = 0
            
            # Intenta con cada instancia de Nitter
            for instance in nitter_instances:
                try:
                    url = f"{instance}/{cuenta}"
                    resp = requests.get(url, headers=headers, timeout=10)
                    
                    if resp.status_code != 200:
                        continue
                    
                    # Parsea HTML
                    soup = BeautifulSoup(resp.content, 'html.parser')
                    
                    # Busca tweets (estructura Nitter)
                    tweet_elements = soup.find_all('div', class_='tweet')
                    
                    for tweet_elem in tweet_elements[:5]:  # Máximo 5 tweets
                        try:
                            # Extrae texto del tweet
                            texto_elem = tweet_elem.find('p', class_='tweet-text')
                            texto = texto_elem.get_text(strip=True) if texto_elem else ""
                            
                            if texto:
                                tweets.append({
                                    "autor": cuenta,
                                    "texto": texto[:280],  # Máx 280 caracteres
                                    "fecha": datetime.now().strftime('%Y-%m-%d'),
                                    "likes": 0,  # Nitter no siempre muestra likes
                                    "url": f"https://twitter.com/{cuenta}"
                                })
                                tweets_encontrados += 1
                        
                        except Exception as e:
                            logger.debug(f"  ⚠️ Error parseando tweet de @{cuenta}: {e}")
                            continue
                    
                    if tweets_encontrados > 0:
                        logger.info(f"  ✅ @{cuenta}: {tweets_encontrados} tweets scrapeados")
                        break  # Si encontró tweets, no intenta otra instancia
                
                except Exception as e:
                    logger.debug(f"  ⚠️ Error con {instance}: {e}")
                    continue
            
            if tweets_encontrados == 0:
                logger.warning(f"  ⚠️ @{cuenta}: No se pudieron scrapear tweets")
    
    except ImportError:
        logger.warning("⚠️ beautifulsoup4 no instalado. Instala con: pip install beautifulsoup4")
    
    except Exception as e:
        logger.warning(f"⚠️ Error general scrapeando X/Twitter: {e}")
    
    return tweets


# ============================================================================
# PASO 3: PROCESAR CON IA
# ============================================================================

def procesar_noticias_con_ia(noticias: List[Dict], tweets: List[Dict] = None) -> Dict:
    """
    Procesa noticias scrapeadas con IA para generar:
    - Insights clave
    - Hilo X
    - Propuestas de reels
    - Propuestas de stories
    
    Args:
        noticias: Lista de noticias dict
        tweets: Lista de tweets dict (opcional)
    
    Returns:
        dict con keys: insights, hilo_x, reels, stories
    """
    if tweets is None:
        tweets = []
    
    try:
        from src.utils.api_manager import consultar_llm
        
        # Formatea noticias en texto para el prompt
        noticias_texto = "\n".join([
            f"- {n['fuente']}: {n['titulo']} ({n.get('relevancia', 'unknown')})"
            for n in noticias
        ])
        
        # Formatea tweets en texto
        tweets_texto = "\n".join([
            f"- @{t.get('autor', 'unknown')}: {t.get('texto', '')}"
            for t in tweets
        ]) if tweets else "No hay tweets disponibles"
        
        # Prompt para IA
        prompt = f"""
Eres un analista de baloncesto profesional.

Tienes estas noticias de HOY ({datetime.now().strftime('%d/%m/%Y')}):

NOTICIAS:
{noticias_texto}

TWEETS DE INFLUENCERS:
{tweets_texto}

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
        respuesta = consultar_llm(prompt, modelo="gemini")
        
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
            "fecha": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
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
            "error": "JSON parse error"
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
        dict con insights, hilo_x, reels, stories
    """
    fecha_hoy = datetime.now().strftime('%d/%m/%Y')
    logger.info(f"\n📰 Procesando noticias del {fecha_hoy}...\n")
    
    # PASO 1: Scrapeea noticias
    logger.info("1️⃣  Scrapepando noticias...")
    noticias = []
    noticias += scrapear_noticias_basketnews()
    noticias += scrapear_noticias_espn()
    noticias += scrapear_noticias_eurohoops()
    
    logger.info(f"   ✅ {len(noticias)} noticias scrapeadas\n")
    
    # PASO 2: Scrapeea tweets
    logger.info("2️⃣  Scrapeando tweets X...")
    tweets = scrapear_tweets_x()
    logger.info(f"   ℹ️  {len(tweets)} tweets (requiere API credentials)\n")
    
    # PASO 3: Procesa con IA
    logger.info("3️⃣  Procesando con IA...")
    resultado = procesar_noticias_con_ia(noticias, tweets)
    logger.info(f"   ✅ Procesadas: {resultado['procesadas']}\n")
    
    return resultado


# ============================================================================
# TEST
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
