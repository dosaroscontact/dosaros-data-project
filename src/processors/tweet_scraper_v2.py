"""
================================================================================
TWEET_SCRAPER_V2.PY - Scrapeea Tweets con twscrape (Más Estable)
================================================================================
Función principal:
  Scrapeea últimos tweets de 6 influencers clave (NBA + Euroliga)
  Usa twscrape (librería muy mantenida, manejo automático de cuentas)

Requisitos:
  - pip install twscrape
  - Cuenta X (Twitter) real para login
  - accounts.json (generada automáticamente en primer setup)

Uso:
  python tweet_scraper_v2.py
  
  O en código:
  from src.processors.tweet_scraper_v2 import scrapear_tweets_twscrape
  tweets = asyncio.run(scrapear_tweets_twscrape())
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
ACCOUNTS_PATH = "accounts.json"
TWEETS_LIMIT = 5  # Máximo tweets por influencer


# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

async def scrapear_tweets_twscrape() -> List[Dict]:
    """
    Scrapeea tweets de influencers usando twscrape.
    
    twscrape es más estable que Twikit en 2026 porque:
    - Mantiene múltiples cuentas automáticamente
    - Maneja rate limiting mejor
    - API más moderna
    
    Returns:
        Lista de tweets con estructura: {autor, texto, fecha, likes, url}
    """
    try:
        from twscrape import API
    except ImportError:
        logger.error("❌ twscrape no instalado. Ejecuta: pip install twscrape")
        return []
    
    tweets = []
    
    try:
        # PASO 1: Inicializar API
        logger.info("🐦 Inicializando API twscrape...\n")
        api = API()
        
        # PASO 2: Verificar cuentas
        logger.info("📂 Verificando cuentas configuradas...")
        
        # Cargar cuentas si existen
        if os.path.exists(ACCOUNTS_PATH):
            try:
                with open(ACCOUNTS_PATH, 'r') as f:
                    accounts = json.load(f)
                logger.info(f"✅ {len(accounts)} cuentas cargadas desde {ACCOUNTS_PATH}\n")
            except Exception as e:
                logger.warning(f"⚠️ Error cargando cuentas: {e}")
                logger.info("🔐 Se requiere setup de cuentas...\n")
                await _setup_cuentas(api)
        else:
            logger.info("🔐 Primer setup requerido. Se necesita al menos 1 cuenta X.\n")
            await _setup_cuentas(api)
        
        # PASO 3: Scrapear tweets de cada influencer
        logger.info(f"\n📊 Scrapeando tweets de {len(INFLUENCERS)} influencers...\n")
        
        for influencer in INFLUENCERS:
            try:
                logger.info(f"  🔍 @{influencer}...")
                
                # Buscar tweets del usuario
                tweets_iter = api.search_tweet(f"from:{influencer}", limit=TWEETS_LIMIT)
                
                tweets_count = 0
                async for tweet in tweets_iter:
                    tweets.append({
                        "autor": influencer,
                        "texto": tweet.text[:280],  # Twitter max 280 chars
                        "fecha": datetime.now().strftime('%Y-%m-%d'),
                        "likes": tweet.likes,
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
        logger.error(f"❌ Error general en twscrape: {e}")
        return []


# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

async def _setup_cuentas(api) -> bool:
    """
    Setup interactivo de cuentas para twscrape.
    
    Requiere que el usuario ingrese credenciales en la terminal.
    """
    try:
        print("\n" + "="*60)
        print("🔐 SETUP DE CUENTAS X/TWITTER (twscrape)")
        print("="*60)
        print("\nNecesitas al menos 1 cuenta X para scrapear.")
        print("Puedes añadir varias cuentas para mejorar el scraping.\n")
        
        while True:
            username = input("📝 Usuario X (@usuario) [o 'done' para terminar]: ").strip()
            
            if username.lower() == 'done':
                break
            
            if not username.startswith('@'):
                username = '@' + username
            
            email = input("📧 Email: ").strip()
            password = input("🔒 Contraseña: ").strip()
            
            if not (username and email and password):
                logger.error("❌ Credenciales incompletas")
                continue
            
            logger.info(f"🔄 Añadiendo cuenta {username}...")
            
            try:
                # twscrape usa pool de cuentas
                await api.pool.add_account(username, email, password)
                logger.info(f"✅ Cuenta {username} añadida exitosamente\n")
            except Exception as e:
                logger.error(f"❌ Error añadiendo cuenta: {e}\n")
                continue
        
        # Guardar cuentas
        logger.info("💾 Guardando cuentas...")
        # twscrape maneja las cuentas internamente, pero podemos guardar referencia
        accounts_ref = {
            "timestamp": datetime.now().isoformat(),
            "status": "configured",
            "note": "Cuentas gestionadas internamente por twscrape"
        }
        
        with open(ACCOUNTS_PATH, 'w') as f:
            json.dump(accounts_ref, f, indent=2)
        
        logger.info(f"✅ Setup completado. Archivo {ACCOUNTS_PATH} creado.\n")
        return True
    
    except Exception as e:
        logger.error(f"❌ Error en setup: {e}")
        return False


# ============================================================================
# TEST / MAIN
# ============================================================================

async def main():
    """Función principal para testing."""
    tweets = await scrapear_tweets_twscrape()
    
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
        print("\n⚠️ No se scrapearon tweets. Verifica cuentas o conexión.\n")


if __name__ == "__main__":
    asyncio.run(main())
