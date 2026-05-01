"""
================================================================================
TWEET_SCRAPER_V3.PY - Scrapeea Tweets con snscrape (Simple, Sin Credenciales)
================================================================================
Función principal:
  Scrapeea últimos tweets de 6 influencers clave (NBA + Euroliga)
  Usa snscrape (sin credenciales, muy simple)

Requisitos:
  - pip install snscrape

Ventajas:
  - SIN credenciales requeridas
  - Scrapeea datos públicos
  - Muy ligero para Pi
  - Fácil de implementar

Desventajas:
  - Menos estable que APIs oficiales
  - X cambia estructura ocasionalmente
  - Pero para uso personal está bien

Uso:
  python tweet_scraper_v3.py
  
  O en código:
  from src.processors.tweet_scraper_v3 import scrapear_tweets_snscrape
  tweets = scrapear_tweets_snscrape()
================================================================================
"""

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

# Configuración
TWEETS_LIMIT = 5  # Máximo tweets por influencer


# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def scrapear_tweets_snscrape() -> List[Dict]:
    """
    Scrapeea tweets de influencers usando snscrape.
    
    snscrape NO requiere credenciales, scrapeea datos públicos directamente.
    Es más simple pero menos estable que APIs oficiales.
    
    Returns:
        Lista de tweets con estructura: {autor, texto, fecha, likes, url}
    """
    try:
        import snscrape.modules.twitter as sntwitter
    except ImportError:
        logger.error("❌ snscrape no instalado. Ejecuta: pip install snscrape")
        return []
    
    tweets = []
    
    logger.info("🐦 Inicializando snscrape (sin credenciales)...\n")
    logger.info(f"📊 Scrapeando tweets de {len(INFLUENCERS)} influencers...\n")
    
    for influencer in INFLUENCERS:
        try:
            logger.info(f"  🔍 @{influencer}...")
            
            # Query para snscrape: busca tweets de la cuenta
            query = f"from:{influencer}"
            
            tweets_count = 0
            
            # snscrape retorna iterador de tweets
            for tweet in sntwitter.TwitterSearchScraper(query).get_items():
                # Limitar a TWEETS_LIMIT por influencer
                if tweets_count >= TWEETS_LIMIT:
                    break
                
                try:
                    tweets.append({
                        "autor": influencer,
                        "texto": tweet.content[:280],  # Twitter max 280 chars
                        "fecha": tweet.date.strftime('%Y-%m-%d') if tweet.date else datetime.now().strftime('%Y-%m-%d'),
                        "likes": tweet.likeCount if hasattr(tweet, 'likeCount') else 0,
                        "url": f"https://twitter.com/{influencer}"
                    })
                    tweets_count += 1
                except Exception as e:
                    logger.debug(f"      ⚠️ Error procesando tweet: {e}")
                    continue
            
            logger.info(f"      ✅ {tweets_count} tweets scrapeados")
        
        except Exception as e:
            logger.warning(f"      ⚠️ Error con @{influencer}: {e}")
            continue
    
    logger.info(f"\n✅ Total tweets scrapeados: {len(tweets)}\n")
    return tweets


# ============================================================================
# TEST / MAIN
# ============================================================================

def main():
    """Función principal para testing."""
    tweets = scrapear_tweets_snscrape()
    
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
        print("\n⚠️ No se scrapearon tweets. Verifica conexión o que las cuentas existan.\n")


if __name__ == "__main__":
    main()
