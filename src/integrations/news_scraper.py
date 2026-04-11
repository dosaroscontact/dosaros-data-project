"""
================================================================================
NEWS SCRAPER - Proyecto Dos Aros (Avanzado con Selenium)
================================================================================
Scrape avanzado de:
  - Euroliga: BasketNews, Eurohoops, Euroleague.net, Encestando
  - NBA: Basketball-Reference, The Athletic, The Ringer, NBAmaniacs
  - X/Twitter: 9 cuentas clave (@UrbonasS, @ArisBarkas, @chemadelucas, etc.)

Retorna JSON con noticias destacadas para pasar a IA.
================================================================================
"""

import json
import time
import requests
from datetime import datetime, timedelta
from typing import List, Dict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import tweepy
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

# Webs a scrapear
EUROLIGA_WEBS = {
    "baske_news": "https://www.basketnews.com/news",
    "eurohoops": "https://www.eurohoops.net",
    "euroleague_net": "https://www.euroleague.net/news",
    "encestando": "https://www.encestando.net",
}

NBA_WEBS = {
    "basketball_reference": "https://www.basketball-reference.com/",
    "the_athletic": "https://theathletic.com/nba/",
    "the_ringer": "https://www.theringer.com/nba",
    "nba_maniacs": "https://www.nbamaniacs.com/",
}

# ============================================================================
# CONFIGURAR SELENIUM (headless)
# ============================================================================

def _create_driver():
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.service import Service
    
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(10)
        return driver
    except Exception as e:
        print(f"⚠️ Error creando driver Chrome: {e}")
        return None

# ============================================================================
# SCRAPING DE WEBS
# ============================================================================

def scrape_basketnews() -> List[Dict]:
    """Scrape avanzado de BasketNews."""
    noticias = []
    driver = _create_driver()
    if not driver:
        return noticias
    
    try:
        print("  📰 BasketNews...")
        driver.get(EUROLIGA_WEBS["baske_news"])
        time.sleep(3)  # Espera a que cargue JS
        
        # Buscar artículos (selectores típicos de BasketNews)
        articles = driver.find_elements(By.CSS_SELECTOR, "article, .article-card, [data-article-id]")
        
        for article in articles[:5]:  # Top 5
            try:
                # Intentar diferentes selectores
                titulo_elem = article.find_elements(By.TAG_NAME, "h2") or article.find_elements(By.TAG_NAME, "h3")
                if titulo_elem:
                    titulo = titulo_elem[0].text.strip()
                else:
                    titulo = "Sin título"
                
                link_elem = article.find_elements(By.TAG_NAME, "a")
                link = link_elem[0].get_attribute("href") if link_elem else ""
                
                if titulo and titulo != "Sin título":
                    noticias.append({
                        "fuente": "BasketNews",
                        "liga": "Euroliga",
                        "titulo": titulo,
                        "url": link,
                        "timestamp": datetime.now().isoformat()
                    })
            except Exception as e:
                continue
    
    except Exception as e:
        print(f"  ⚠️ Error BasketNews: {e}")
    finally:
        driver.quit()
    
    return noticias


def scrape_eurohoops() -> List[Dict]:
    """Scrape avanzado de Eurohoops."""
    noticias = []
    driver = _create_driver()
    if not driver:
        return noticias
    
    try:
        print("  📰 Eurohoops...")
        driver.get(EUROLIGA_WEBS["eurohoops"])
        time.sleep(3)
        
        # Buscar artículos
        articles = driver.find_elements(By.CSS_SELECTOR, ".story-item, .article-item, .post-item")
        
        for article in articles[:5]:
            try:
                titulo_elem = article.find_elements(By.TAG_NAME, "h2") or article.find_elements(By.TAG_NAME, "a")
                titulo = titulo_elem[0].text.strip() if titulo_elem else "Sin título"
                
                link = article.find_element(By.TAG_NAME, "a").get_attribute("href")
                
                if titulo and titulo != "Sin título":
                    noticias.append({
                        "fuente": "Eurohoops",
                        "liga": "Euroliga",
                        "titulo": titulo,
                        "url": link,
                        "timestamp": datetime.now().isoformat()
                    })
            except Exception as e:
                continue
    
    except Exception as e:
        print(f"  ⚠️ Error Eurohoops: {e}")
    finally:
        driver.quit()
    
    return noticias


def scrape_euroleague_net() -> List[Dict]:
    """Scrape avanzado de Euroleague.net."""
    noticias = []
    driver = _create_driver()
    if not driver:
        return noticias
    
    try:
        print("  📰 Euroleague.net...")
        driver.get(EUROLIGA_WEBS["euroleague_net"])
        time.sleep(3)
        
        # Buscar noticias (selectores típicos)
        articles = driver.find_elements(By.CSS_SELECTOR, ".news-item, .article, [class*='news']")
        
        for article in articles[:5]:
            try:
                titulo_elem = article.find_elements(By.TAG_NAME, "h2") or article.find_elements(By.TAG_NAME, "h3")
                titulo = titulo_elem[0].text.strip() if titulo_elem else "Sin título"
                
                link = article.find_element(By.TAG_NAME, "a").get_attribute("href")
                
                if titulo and titulo != "Sin título":
                    noticias.append({
                        "fuente": "Euroleague.net",
                        "liga": "Euroliga",
                        "titulo": titulo,
                        "url": link,
                        "timestamp": datetime.now().isoformat()
                    })
            except Exception as e:
                continue
    
    except Exception as e:
        print(f"  ⚠️ Error Euroleague.net: {e}")
    finally:
        driver.quit()
    
    return noticias


def scrape_encestando() -> List[Dict]:
    """Scrape avanzado de Encestando."""
    noticias = []
    driver = _create_driver()
    if not driver:
        return noticias
    
    try:
        print("  📰 Encestando...")
        driver.get(EUROLIGA_WEBS["encestando"])
        time.sleep(3)
        
        articles = driver.find_elements(By.CSS_SELECTOR, ".post, article, [data-post-id]")
        
        for article in articles[:5]:
            try:
                titulo_elem = article.find_elements(By.TAG_NAME, "h2") or article.find_elements(By.TAG_NAME, "h3")
                titulo = titulo_elem[0].text.strip() if titulo_elem else "Sin título"
                
                link = article.find_element(By.TAG_NAME, "a").get_attribute("href")
                
                if titulo and titulo != "Sin título":
                    noticias.append({
                        "fuente": "Encestando",
                        "liga": "Euroliga",
                        "titulo": titulo,
                        "url": link,
                        "timestamp": datetime.now().isoformat()
                    })
            except Exception as e:
                continue
    
    except Exception as e:
        print(f"  ⚠️ Error Encestando: {e}")
    finally:
        driver.quit()
    
    return noticias


def scrape_nba_webs() -> List[Dict]:
    """Scrape avanzado de webs NBA (genérico)."""
    noticias = []
    driver = _create_driver()
    if not driver:
        return noticias
    
    webs_nba = [
        ("Basketball-Reference", "https://www.basketball-reference.com/"),
        ("The Ringer", "https://www.theringer.com/nba"),
        ("NBAmaniacs", "https://www.nbamaniacs.com/"),
    ]
    
    for fuente, url in webs_nba:
        try:
            print(f"  📰 {fuente}...")
            driver.get(url)
            time.sleep(2)
            
            articles = driver.find_elements(By.CSS_SELECTOR, "article, .article, [class*='post'], [class*='news']")
            
            for article in articles[:5]:
                try:
                    titulo_elem = article.find_elements(By.TAG_NAME, "h2") or article.find_elements(By.TAG_NAME, "h3") or article.find_elements(By.TAG_NAME, "a")
                    titulo = titulo_elem[0].text.strip() if titulo_elem else "Sin título"
                    
                    link = article.find_element(By.TAG_NAME, "a").get_attribute("href")
                    
                    if titulo and titulo != "Sin título":
                        noticias.append({
                            "fuente": fuente,
                            "liga": "NBA",
                            "titulo": titulo,
                            "url": link,
                            "timestamp": datetime.now().isoformat()
                        })
                except Exception as e:
                    continue
        
        except Exception as e:
            print(f"  ⚠️ Error {fuente}: {e}")
    
    driver.quit()
    return noticias


# ============================================================================
# SCRAPING DE X/TWITTER
# ============================================================================

def scrape_x_tweets() -> List[Dict]:
    """
    Scrape de tweets de cuentas clave usando Playwright (sin API, sin token).
    Funciona con sesión autenticada del navegador.
    """
    tweets = []
    
    try:
        from playwright.async_api import async_playwright
        import asyncio
        
        async def scrape_async():
            async with async_playwright() as p:
                # Usar navegador existente o crear uno nuevo
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context()
                page = await context.new_page()
                
                for account in X_ACCOUNTS:
                    try:
                        print(f"  🐦 @{account}...")
                        
                        # Navegar al perfil
                        await page.goto(f"https://x.com/{account}", wait_until="networkidle", timeout=10000)
                        await page.wait_for_timeout(2000)  # Esperar JS
                        
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
                                    tweets.append({
                                        "fuente": f"@{account}",
                                        "liga": "Euroliga" if account in ["UrbonasS", "ArisBarkas", "chemadelucas", "AravantinosDA"] else "NBA",
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
        
        # Ejecutar async
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
    
    Returns:
        {
            "euroliga": [...noticias Euro],
            "nba": [...noticias NBA],
            "x": [...tweets],
            "timestamp": "2026-04-11T09:00:00"
        }
    """
    print("\n[NEWS SCRAPER] Recabando noticias del día...\n")
    
    noticias = {
        "euroliga": [],
        "nba": [],
        "x": [],
        "timestamp": datetime.now().isoformat()
    }
    
    # Scrape Euroliga
    print("🌍 EUROLIGA:\n")
    noticias["euroliga"].extend(scrape_basketnews())
    noticias["euroliga"].extend(scrape_eurohoops())
    noticias["euroliga"].extend(scrape_euroleague_net())
    noticias["euroliga"].extend(scrape_encestando())
    
    # Scrape NBA
    print("\n🏀 NBA:\n")
    noticias["nba"].extend(scrape_nba_webs())
    
    # Scrape X
    print("\n🐦 X/TWITTER:\n")
    tweets = scrape_x_tweets()
    noticias["x"] = tweets
    
    # Deduplicar y limpiar
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
        if titulo not in vistas and titulo:
            vistas.add(titulo)
            resultado.append(noticia)
    return resultado


# ============================================================================
# EXPORTAR JSON
# ============================================================================

def guardar_noticias_json(noticias: Dict, filepath: str = "/home/pi/dosaros-data-project/noticias_dia.json"):
    """Guarda noticias en JSON para usar en prompts."""
    try:
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
            print(f"  • @{t['fuente']}: {t['titulo'][:80]}")
    
    # Guardar JSON
    guardar_noticias_json(noticias)
