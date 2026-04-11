"""
================================================================================
NEWS SCRAPER FINAL - Proyecto Dos Aros (Tweets X + DB)
================================================================================
Simple y directo:
  - Tweets X via Playwright (YA FUNCIONA)
  - Resultados NBA/Euro de ayer
  - Próximos partidos

Retorna JSON para pasar a IA.
================================================================================
"""

import json
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict
from dotenv import load_dotenv
import os

load_dotenv()

DB_PATH = os.getenv("LOCAL_DB", "/mnt/nba_data/dosaros_local.db")

# ============================================================================
# DATOS DE BD
# ============================================================================

def get_connection():
    return sqlite3.connect(DB_PATH)


def obtener_resultados_nba(fecha=None) -> List[Dict]:
    """Resultados NBA del día anterior."""
    if fecha is None:
        fecha = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    try:
        conn = get_connection()
        query = """
            SELECT MATCHUP, PTS, WL, TEAM_ABBREVIATION
            FROM nba_games
            WHERE GAME_DATE = ?
            ORDER BY PTS DESC
        """
        df = pd.read_sql_query(query, conn, params=[fecha])
        conn.close()
        
        resultados = []
        for _, row in df.iterrows():
            resultados.append({
                "equipo": row['TEAM_ABBREVIATION'],
                "puntos": row['PTS'],
                "resultado": row['WL']
            })
        return resultados
    except Exception as e:
        print(f"⚠️ Error NBA: {e}")
        return []


def obtener_resultados_euro(fecha=None) -> List[Dict]:
    """Resultados Euroliga del día anterior."""
    if fecha is None:
        fecha = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    try:
        conn = get_connection()
        query = """
            SELECT home_team, away_team, score_home, score_away
            FROM euro_games
            WHERE date = ?
        """
        df = pd.read_sql_query(query, conn, params=[fecha])
        conn.close()
        
        resultados = []
        for _, row in df.iterrows():
            resultados.append({
                "home": row['home_team'],
                "away": row['away_team'],
                "score_home": row['score_home'],
                "score_away": row['score_away']
            })
        return resultados
    except Exception as e:
        print(f"⚠️ Error Euro: {e}")
        return []


def obtener_proximos_partidos() -> Dict:
    """Próximos partidos NBA y Euro."""
    try:
        conn = get_connection()
        
        # NBA (si existe tabla)
        try:
            query_nba = """
                SELECT GAME_DATE, TEAM_ABBREVIATION, MATCHUP
                FROM nba_games
                WHERE GAME_DATE > date('now')
                ORDER BY GAME_DATE ASC
                LIMIT 5
            """
            nba_df = pd.read_sql_query(query_nba, conn)
            nba_proximos = nba_df.to_dict('records') if not nba_df.empty else []
        except:
            nba_proximos = []
        
        # Euro
        try:
            query_euro = """
                SELECT date, home_team, away_team
                FROM euro_games
                WHERE date > date('now')
                ORDER BY date ASC
                LIMIT 5
            """
            euro_df = pd.read_sql_query(query_euro, conn)
            euro_proximos = euro_df.to_dict('records') if not euro_df.empty else []
        except:
            euro_proximos = []
        
        conn.close()
        
        return {
            "nba": nba_proximos,
            "euroliga": euro_proximos
        }
    except Exception as e:
        print(f"⚠️ Error próximos partidos: {e}")
        return {"nba": [], "euroliga": []}


# ============================================================================
# TWEETS X (PLAYWRIGHT)
# ============================================================================

def scrape_x_tweets() -> List[Dict]:
    """Scrape tweets de 9 cuentas clave."""
    tweets = []
    
    X_ACCOUNTS = [
        "UrbonasS", "ArisBarkas", "chemadelucas", "AravantinosDA",
        "ShamsCharania", "BobbyMarks42", "kirkgoldsberry", "StatMuse", "TheSteinLine"
    ]
    
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
                        await page.goto(f"https://x.com/{account}", wait_until="networkidle", timeout=10000)
                        await page.wait_for_timeout(2000)
                        
                        tweets_elements = await page.query_selector_all("[data-testid='Tweet']")
                        
                        for tweet_elem in tweets_elements[:2]:  # Top 2 tweets
                            try:
                                text_elem = await tweet_elem.query_selector("[data-testid='tweetText']")
                                text = await text_elem.inner_text() if text_elem else ""
                                
                                link_elem = await tweet_elem.query_selector("a[href*='/status/']")
                                link = await link_elem.get_attribute("href") if link_elem else ""
                                
                                if text and text.strip():
                                    liga = "Euroliga" if account in ["UrbonasS", "ArisBarkas", "chemadelucas", "AravantinosDA"] else "NBA"
                                    tweets.append({
                                        "fuente": f"@{account}",
                                        "liga": liga,
                                        "texto": text[:200],
                                        "url": f"https://x.com{link}" if link else "",
                                        "timestamp": datetime.now().isoformat()
                                    })
                            except:
                                continue
                    except Exception as e:
                        print(f"  ⚠️ Error @{account}: {e}")
                        continue
                
                await browser.close()
        
        asyncio.run(scrape_async())
    
    except ImportError:
        print("  ⚠️ Playwright no instalado")
        return tweets
    except Exception as e:
        print(f"  ⚠️ Error Playwright: {e}")
    
    return tweets


# ============================================================================
# AGREGADOR
# ============================================================================

def obtener_noticias_completas() -> Dict:
    """Combina tweets X + resultados + próximos partidos."""
    print("\n[NEWS SCRAPER FINAL] Recabando contenido...\n")
    
    fecha_ayer = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    noticias = {
        "fecha": fecha_ayer,
        "resultados": {
            "nba": obtener_resultados_nba(fecha_ayer),
            "euroliga": obtener_resultados_euro(fecha_ayer)
        },
        "proximos": obtener_proximos_partidos(),
        "tweets": [],
        "timestamp": datetime.now().isoformat()
    }
    
    print("🏀 NBA resultados:", len(noticias["resultados"]["nba"]))
    print("🌍 Euro resultados:", len(noticias["resultados"]["euroliga"]))
    print("📅 Próximos partidos:", len(noticias["proximos"]["nba"]) + len(noticias["proximos"]["euroliga"]))
    
    print("\n🐦 TWEETS X:\n")
    noticias["tweets"] = scrape_x_tweets()
    
    print(f"\n✅ Contenido recabado:")
    print(f"  - Tweets: {len(noticias['tweets'])}")
    print(f"  - Resultados NBA: {len(noticias['resultados']['nba'])}")
    print(f"  - Resultados Euro: {len(noticias['resultados']['euroliga'])}")
    
    return noticias


def guardar_json(noticias: Dict, filepath: str = "/home/pi/dosaros-data-project/noticias_dia.json"):
    """Guarda JSON para IA."""
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(noticias, f, indent=2, ensure_ascii=False)
        print(f"\n✅ JSON guardado: {filepath}")
        return True
    except Exception as e:
        print(f"⚠️ Error: {e}")
        return False


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    noticias = obtener_noticias_completas()
    
    print("\n" + "="*50)
    print("CONTENIDO PARA IA")
    print("="*50)
    
    if noticias["resultados"]["nba"]:
        print("\n🏀 NBA (ayer):")
        for r in noticias["resultados"]["nba"][:3]:
            print(f"  • {r['equipo']}: {r['puntos']} pts ({r['resultado']})")
    
    if noticias["resultados"]["euroliga"]:
        print("\n🌍 EUROLIGA (ayer):")
        for r in noticias["resultados"]["euroliga"][:3]:
            print(f"  • {r['home']} {r['score_home']} - {r['score_away']} {r['away']}")
    
    if noticias["tweets"]:
        print("\n🐦 TWEETS:")
        for t in noticias["tweets"][:3]:
            print(f"  • @{t['fuente'].replace('@', '')}: {t['texto'][:80]}...")
    
    guardar_json(noticias)
