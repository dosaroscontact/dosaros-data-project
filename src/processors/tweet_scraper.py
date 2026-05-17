"""
================================================================================
TWEET_SCRAPER.PY - Scrapeea Tweets de Influencers con Twikit
================================================================================
Función principal:
  Scrapeea últimos tweets de 6 influencers clave (NBA + Euroliga)
  Usa Twikit (librería activa, bajo consumo RAM)

Requisitos:
  - pip install twikit
  - Cuenta X (Twitter) real para login
  - cookies.json (generada automáticamente en primer login)

Uso:
  python tweet_scraper.py
  
  O en código:
  from src.processors.tweet_scraper import scrapear_tweets_twikit
  tweets = asyncio.run(scrapear_tweets_twikit())
================================================================================
"""

import asyncio
import json
import os
import logging
from typing import List, Dict
from datetime import datetime

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cuentas de influencers a scrapear
INFLUENCERS = [
    "ShamsCharania",      # NBA insider
    "UrbonasS",          # BasketNews/Euroliga
    "ArisBarkas",        # Eurohoops
    "chemadelucas",      # Rastreador español
    "BobbyMarks42",      # NBA salary cap
    "StatMuse",          # NBA stats
]

# Rutas
COOKIES_PATH = "cookies.json"
TWEETS_LIMIT = 5  # Máximo tweets por influencer


# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

async def scrapear_tweets_twikit() -> List[Dict]:
    """
    Scrapeea tweets de influencers usando Twikit.
    
    Returns:
        Lista de tweets con estructura: {autor, texto, fecha, likes, url}
    """
    try:
        from twikit import Client
    except ImportError:
        logger.error("❌ twikit no instalado. Ejecuta: pip install twikit")
        return []
    
    tweets = []
    
    try:
        # PASO 1: Inicializar cliente
        logger.info("🐦 Inicializando cliente Twikit...\n")
        client = Client('en-US')
        
        # PASO 2: Login (usa cookies si existen, si no pide credenciales)
        if os.path.exists(COOKIES_PATH):
            logger.info("📂 Cargando cookies existentes...")
            try:
                client.load_cookies(COOKIES_PATH)
                logger.info("✅ Cookies cargadas correctamente\n")
            except Exception as e:
                logger.warning(f"⚠️ Cookies expiradas o corruptas: {e}")
                logger.info("🔐 Se requiere nuevo login...\n")
                await _login_y_guardar_cookies(client)
        else:
            logger.info("🔐 Primer login requerido.\n")
            await _login_y_guardar_cookies(client)
        
        # PASO 3: Scrapear tweets de cada influencer
        logger.info(f"\n📊 Scrapeando tweets de {len(INFLUENCERS)} influencers...\n")
        
        for influencer in INFLUENCERS:
            try:
                logger.info(f"  🔍 @{influencer}...")
                
                # Obtener usuario
                user = await client.get_user_by_screen_name(influencer)
                
                # Obtener tweets del usuario
                user_tweets = await user.get_tweets('Tweets', count=TWEETS_LIMIT)
                
                # Procesar cada tweet
                tweets_count = 0
                for tweet in user_tweets:
                    tweets.append({
                        "autor": influencer,
                        "texto": tweet.text[:280],  # Twitter max 280 chars
                        "fecha": datetime.now().strftime('%Y-%m-%d'),
                        "likes": getattr(tweet, 'likes', 0),
                        "url": f"https://twitter.com/{influencer}"
                    })
                    tweets_count += 1
                
                logger.info(f"      ✅ {tweets_count} tweets scrapeados")
            
            except Exception as e:
                logger.warning(f"      ⚠️ Error: {e}")
                continue
        
        logger.info(f"\n✅ Total tweets scrapeados: {len(tweets)}\n")
        return tweets
    
    except Exception as e:
        logger.error(f"❌ Error general en Twikit: {e}")
        return []


# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

async def _login_y_guardar_cookies(client) -> bool:
    """
    Realiza login interactivo y guarda cookies.
    
    Requiere que el usuario ingrese credenciales en la terminal.
    """
    try:
        print("\n" + "="*60)
        print("🔐 LOGIN A X/TWITTER (Twikit)")
        print("="*60)
        
        # Solicitar credenciales
        username = input("\n📝 Usuario X (@usuario): ").strip()
        email = input("📧 Email: ").strip()
        password = input("🔒 Contraseña: ").strip()
        
        if not (username and email and password):
            logger.error("❌ Credenciales incompletas")
            return False
        
        logger.info("\n🔄 Autenticando...")
        
        # Realizar login
        await client.login(
            auth_info_1=username,
            auth_info_2=email,
            password=password
        )
        
        # Guardar cookies
        client.save_cookies(COOKIES_PATH)
        logger.info(f"✅ Login exitoso. Cookies guardadas en {COOKIES_PATH}\n")
        
        return True
    
    except Exception as e:
        logger.error(f"❌ Error en login: {e}")
        return False


# ============================================================================
# TEST / MAIN
# ============================================================================

async def main():
    """Función principal para testing."""
    tweets = await scrapear_tweets_twikit()
    
    print("\n" + "="*60)
    print("📊 RESULTADO DEL SCRAPING")
    print("="*60)
    
    if tweets:
        print(f"\n✅ Total tweets: {len(tweets)}\n")
        
        # Mostrar primeros 3 tweets
        for i, tweet in enumerate(tweets[:3], 1):
            print(f"{i}. [{tweet['autor']}]")
            print(f"   {tweet['texto']}")
            print(f"   📅 {tweet['fecha']} | ❤️ {tweet['likes']} likes\n")
    else:
        print("\n⚠️ No se scrapearon tweets. Verifica credenciales o conexión.\n")


if __name__ == "__main__":
    asyncio.run(main())
