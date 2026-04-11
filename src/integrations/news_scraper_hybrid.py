"""
================================================================================
NEWS SCRAPER HYBRID - Proyecto Dos Aros (Playwright + RSS-Bridge)
================================================================================
Sin Selenium, sin problemas de ChromeDriver.

Usa:
  - Playwright para X/Twitter (YA FUNCIONA)
  - RSS-Bridge + feedparser para webs (ligero, rápido)

Retorna JSON con noticias destacadas para pasar a IA.
================================================================================
"""

import json
import feedparser
import requests
from datetime import datetime, timedelta
from typing import List, Dict
from dotenv import load_dotenv
import os

load_dotenv()

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

# Cuentas X/Twitter a monitorear
X_ACCOUNTS = [
    "UrbonasS",  # Donatas Urbonas (BasketNews/Euroliga)
    "ArisBarkas",  # Aris Barkas (Eurohoops)
    "chemadelucas",  # Chema de Lucas (rastreador español)
    "AravantinosDA",  # Dionysis Aravantinos (Euroliga)
    "ShamsCharania",  # Shams (NBA insider)
    "BobbyMarks42",  # Bobby Marks (NBA salary cap)
    "kirkgoldsberry",  # Kirk Goldsberry (NBA analytics)
    "StatMuse",  # StatMuse (NBA stats)
    "TheSteinLine",  # Marc Stein (NBA insider)
]

# RSS-Bridge URL (Docker en puerto 8082)
RSS_BRIDGE_URL = os.getenv("RSS_BRIDGE_URL", "http://192.168.1.136:8082/")

# URLs RSS de X (via RSS-Bridge)
X_ACCOUNTS_RSS = {
    "UrbonasS": f"{RSS_BRIDGE_URL}?action=display&bridge=Twitter&context=By%20keyword&q=from%3AUrbonasS&format=Atom",
    "ArisBarkas": f"{RSS_BRIDGE_URL}?action=display&bridge=Twitter&context=By%20keyword&q=from%3AArisBarkas&format=Atom",
    "chemadelucas": f"{RSS_BRIDGE_URL}?action=display&bridge=Twitter&context=By%20keyword&q=from%3Achemadelucas&format=Atom",
    "AravantinosDA": f"{RSS_BRIDGE_URL}?action=display&bridge=Twitter&context=By%20keyword&q=from%3AAravantinosDA&format=Atom",
    "ShamsCharania": f"{RSS_BRIDGE_URL}?action=display&bridge=Twitter&context=By%20keyword&q=from%3AShamsCharania&format=Atom",
    "BobbyMarks42": f"{RSS_BRIDGE_URL}?action=display&bridge=Twitter&context=By%20keyword&q=from%3ABobbyMarks42&format=Atom",
    "kirkgoldsberry": f"{RSS_BRIDGE_URL}?action=display&bridge=Twitter&context=By%20keyword&q=from%3Akirkgoldsberry&format=Atom",
    "StatMuse": f"{RSS_BRIDGE_URL}?action=display&bridge=Twitter&context=By%20keyword&q=from%3AStatMuse&format=Atom",
    "TheSteinLine": f"{RSS_BRIDGE_URL}?action=display&bridge=Twitter&context=By%20keyword&q=from%3ATheSteinLine&format=Atom",
}

# Webs a scrapear (RSS-Bridge)
EUROLIGA_WEBS = {
    "basketnews": ("BasketNews", f"{RSS_BRIDGE_URL}?action=display&bridge=XPathBridge&url=https://www.basketnews.com/news&item=article&title=h2&content=p&format=Atom"),
    "eurohoops": ("Eurohoops", f"{RSS_BRIDGE_URL}?action=display&bridge=XPathBridge&url=https://www.eurohoops.net&item=article&title=h3&format=Atom"),
    "euroleague_net": ("Euroleague.net", f"{RSS_BRIDGE_URL}?action=display&bridge=XPathBridge&url=https://www.euroleague.net/news&item=.news-item&title=h2&format=Atom"),
    "encestando": ("Encestando", f"{RSS_BRIDGE_URL}?action=display&bridge=XPathBridge&url=https://www.encestando.net&item=article&title=h2&format=Atom"),
}

NBA_WEBS = {
    "the_ringer": ("The Ringer", f"{RSS_BRIDGE_URL}?action=display&bridge=XPathBridge&url=https://www.theringer.com/nba&item=article&title=h2&format=Atom"),
    "nba_maniacs": ("NBAmaniacs", f"{RSS_BRIDGE_URL}?action=display&bridge=XPathBridge&url=https://www.nbamaniacs.com&item=article&title=h2&format=Atom"),
}

# ============================================================================
# SCRAPING VÍA RSS-BRIDGE
# ============================================================================

def scrape_rss_feed(nombre: str, url: str, liga: str) -> List[Dict]:
    """Scrape genérico de cualquier feed RSS."""
    noticias = []
    
    try:
        print(f"  📰 {nombre}...")
        feed = feedparser.parse(url)
        
        if not feed.entries:
            print(f"     ⚠️ Sin noticias en feed")
            return noticias
        
        # Top 5 noticias
        for entry in feed.entries[:5]:
            try:
                titulo = entry.get("title", "").strip()
                link = entry.get("link", "")
                
                if titulo and len(titulo) > 5:
                    noticias.append({
                        "fuente": nombre,
                        "liga": liga,
                        "titulo": titulo[:150],
                        "url": link,
                        "timestamp": datetime.now().isoformat()
                    })
            except Exception as e:
                continue
    
    except Exception as e:
        print(f"  ⚠️ Error {nombre}: {e}")
    
    return noticias


def scrape_euroliga() -> List[Dict]:
    """Scrape de todas las webs de Euroliga via RSS-Bridge."""
    noticias = []
    for key, (nombre, url) in EUROLIGA_WEBS.items():
        noticias.extend(scrape_rss_feed(nombre, url, "Euroliga"))
    return noticias


def scrape_nba() -> List[Dict]:
    """Scrape de todas las webs NBA via RSS-Bridge."""
    noticias = []
    for key, (nombre, url) in NBA_WEBS.items():
        noticias.extend(scrape_rss_feed(nombre, url, "NBA"))
    return noticias


# ============================================================================
# SCRAPING DE X VÍA PLAYWRIGHT (YA FUNCIONA)
# ============================================================================

def scrape_x_tweets() -> List[Dict]:
    """
    Scrape de tweets usando Playwright (sin API, sin token).
    Este método YA FUNCIONA en Pi.
    """
    tweets = []
    
    try:
        from playwright.async_api import async_playwright
        import asyncio
        
        async def scrape_async():
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context()
                page = await context.new_page()
                
                for account in X_ACCOUNTS:
                    try:
                        print(f"  🐦 @{account}...")
                        
                        # Navegar al perfil
                        await page.goto(f"https://x.com/{account}", wait_until="networkidle", timeout=10000)
                        await page.wait_for_timeout(2000)
                        
                        # Extraer tweets
                        tweets_elements = await page.query_selector_all("[data-testid='Tweet']")
                        
                        for tweet_elem in tweets_elements[:3]:  # Top 3 tweets
                            try:
                                # Extraer texto
                                text_elem = await tweet_elem.query_selector("[data-testid='tweetText']")
                                text = await text_elem.inner_text() if text_elem else ""
                                
                                # Extraer link
                                link_elem = await tweet_elem.query_selector("a[href*='/status/']")
                                link = await link_elem.get_attribute("href") if link_elem else ""
                                
                                if text and text.strip():
                                    liga = "Euroliga" if account in ["UrbonasS", "ArisBarkas", "chemadelucas", "AravantinosDA"] else "NBA"
                                    tweets.append({
                                        "fuente": f"@{account}",
                                        "liga": liga,
                                        "titulo": text[:150] + "..." if len(text) > 150 else text,
                                        "url": f"https://x.com{link}" if link and not link.startswith('http') else link,
                                        "timestamp": datetime.now().isoformat()
                                    })
                            except Exception as e:
                                continue
                    
                    except Exception as e:
                        print(f"  ⚠️ Error @{account}: {e}")
                        continue
                
                await browser.close()
        
        asyncio.run(scrape_async())
    
    except ImportError:
        print("  ⚠️ Playwright no instalado. Instala: pip install playwright")
        print("     Luego: playwright install chromium")
        return tweets
    except Exception as e:
        print(f"  ⚠️ Error general Playwright: {e}")
    
    return tweets


# ============================================================================
# AGREGADOR PRINCIPAL
# ============================================================================

def obtener_noticias_dia() -> Dict:
    """
    Función principal que agrega todas las noticias del día.
    """
    print("\n[NEWS SCRAPER HYBRID] Recabando noticias del día...\n")
    
    noticias = {
        "euroliga": [],
        "nba": [],
        "x": [],
        "timestamp": datetime.now().isoformat()
    }
    
    # Scrape Euroliga
    print("🌍 EUROLIGA:\n")
    noticias["euroliga"] = scrape_euroliga()
    
    # Scrape NBA
    print("\n🏀 NBA:\n")
    noticias["nba"] = scrape_nba()
    
    # Scrape X
    print("\n🐦 X/TWITTER:\n")
    noticias["x"] = scrape_x_tweets()
    
    # Deduplicar
    noticias["euroliga"] = _deduplicar(noticias["euroliga"])
    noticias["nba"] = _deduplicar(noticias["nba"])
    noticias["x"] = _deduplicar(noticias["x"])
    
    print(f"\n✅ Noticias recabadas:")
    print(f"  - Euroliga: {len(noticias['euroliga'])}")
    print(f"  - NBA: {len(noticias['nba'])}")
    print(f"  - X: {len(noticias['x'])}")
    
    return noticias


def _deduplicar(noticias: List[Dict]) -> List[Dict]:
    """Elimina duplicados por título."""
    vistas = set()
    resultado = []
    for noticia in noticias:
        titulo = noticia.get("titulo", "").lower().strip()
        if titulo not in vistas and len(titulo) > 5:
            vistas.add(titulo)
            resultado.append(noticia)
    return resultado


# ============================================================================
# EXPORTAR JSON
# ============================================================================

def guardar_noticias_json(noticias: Dict, filepath: str = "/home/pi/dosaros-data-project/noticias_dia.json"):
    """Guarda noticias en JSON para usar en prompts."""
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(noticias, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Noticias guardadas en {filepath}")
        return True
    except Exception as e:
        print(f"⚠️ Error guardando JSON: {e}")
        return False


# ============================================================================
# EJECUCIÓN DIRECTA
# ============================================================================

if __name__ == "__main__":
    noticias = obtener_noticias_dia()
    
    # Mostrar resumen
    print("\n" + "="*50)
    print("NOTICIAS RECABADAS DEL DÍA")
    print("="*50)
    
    if noticias["euroliga"]:
        print("\n🌍 EUROLIGA:")
        for n in noticias["euroliga"][:3]:
            print(f"  • {n['titulo'][:80]}")
    
    if noticias["nba"]:
        print("\n🏀 NBA:")
        for n in noticias["nba"][:3]:
            print(f"  • {n['titulo'][:80]}")
    
    if noticias["x"]:
        print("\n🐦 X/TWITTER:")
        for t in noticias["x"][:3]:
            print(f"  • {t['fuente']}: {t['titulo'][:80]}")
    
    # Guardar JSON
    guardar_noticias_json(noticias)
