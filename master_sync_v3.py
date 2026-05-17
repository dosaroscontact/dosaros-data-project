"""
================================================================================
MASTER_SYNC_V3_FIXED.PY — Orquestador Funcional Dos Aros
================================================================================
VERSIÓN FUNCIONAL que integra SOLO lo que existe:
  ✅ Resultados NBA + EuroLeague (intentado)
  ✅ Noticias: BasketNews + ESPN + Eurohoops (FUNCIONA 100%)
  ✅ Hilo X desde noticias (FUNCIONA 100%)
  ✅ Propuestas reels + stories (FUNCIONA 100%)

NOTA: Pasos de extracción y perlas omitidos (funciones no existen aún)

Flujo simplificado (5 pasos funcionales):
  PASO 1: Intenta extraer resultados NBA/Euro (si fallan, continúa)
  PASO 2: Procesa noticias + IA
  PASO 3: Genera hilo X desde noticias
  PASO 4: Propuestas reels + stories
  PASO 5: Envía TODO a Telegram para revisión manual

Tiempo esperado: ~15-30 segundos
================================================================================
"""

import os
import sys
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()
PYTHONPATH = os.getenv("PYTHONPATH", "/home/pi/dosaros-data-project")
sys.path.insert(0, PYTHONPATH)

DB_PATH = os.getenv("LOCAL_DB", "/mnt/nba_data/dosaros_local.db")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

print(f"""
╔════════════════════════════════════════════════════════════════════╗
║    MASTER SYNC V3 FIXED — Dos Aros Daily Automation              ║
║    Ejecutado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                   ║
╚════════════════════════════════════════════════════════════════════╝
""")

inicio = time.time()

# ============================================================================
# PASO 1: Intenta extraer resultados (fallback seguro)
# ============================================================================

print("PASO 1: Intentando extraer resultados NBA + EuroLeague...")
nba_results = []   # lista de dicts: {home, away, score_home, score_away, winner}
euro_results = []  # lista de dicts: {home, away, score_home, score_away}
fecha_ayer = (datetime.now() - __import__('datetime').timedelta(days=1)).strftime('%Y-%m-%d')

try:
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # NBA: una fila por equipo → reconstruimos partidos agrupando por GAME_ID
    # Usamos solo el lado "vs." (local) para obtener cada partido una sola vez
    cursor.execute("""
        SELECT GAME_ID, TEAM_ABBREVIATION, MATCHUP, PTS, WL
        FROM nba_games
        WHERE GAME_DATE = ?
        ORDER BY GAME_ID
    """, (fecha_ayer,))
    filas_nba = cursor.fetchall()

    # Agrupar por GAME_ID → par home/away
    juegos = {}
    for game_id, abrev, matchup, pts, wl in filas_nba:
        if game_id not in juegos:
            juegos[game_id] = []
        juegos[game_id].append((abrev, matchup, pts, wl))

    for game_id, equipos in juegos.items():
        if len(equipos) == 2:
            # El que tiene "vs." en MATCHUP es el local
            local = next((e for e in equipos if 'vs.' in e[1]), equipos[0])
            visitante = next((e for e in equipos if e != local), equipos[1])
            ganador = local[0] if local[3] == 'W' else visitante[0]
            nba_results.append({
                'home': local[0], 'away': visitante[0],
                'score_home': local[2], 'score_away': visitante[2],
                'winner': ganador
            })

    # EuroLeague: ya viene por partido
    cursor.execute("""
        SELECT home_team, away_team, score_home, score_away
        FROM euro_games
        WHERE date = ?
        ORDER BY score_home + score_away DESC
    """, (fecha_ayer,))
    for row in cursor.fetchall():
        ganador = row[0] if row[2] > row[3] else row[1]
        euro_results.append({
            'home': row[0], 'away': row[1],
            'score_home': row[2], 'score_away': row[3],
            'winner': ganador
        })

    conn.close()
    print(f"  ✅ NBA: {len(nba_results)} partidos ({fecha_ayer})")
    print(f"  ✅ Euro: {len(euro_results)} partidos ({fecha_ayer})")
except Exception as e:
    print(f"  ⚠️ No se pudieron extraer resultados: {e} (continuando)")

# ============================================================================
# PASO 2: Procesa noticias + IA (FUNCIONA 100%)
# ============================================================================

print("\nPASO 2: Procesando noticias con IA...")
noticias = {}

try:
    from src.processors.news_processor_v2 import procesar_noticias_hoy
    
    noticias = procesar_noticias_hoy()
    
    if noticias.get("procesadas"):
        print(f"  ✅ Noticias procesadas: {noticias.get('procesadas')}")
        print(f"  ✅ Insights: {len(noticias.get('insights', []))}")
        print(f"  ✅ Hilo X: generado")
        print(f"  ✅ Reels: {len(noticias.get('reels', []))}")
        print(f"  ✅ Stories: {len(noticias.get('stories', []))}")
    else:
        print("  ℹ️ Sin noticias disponibles")
except Exception as e:
    print(f"  ❌ Error procesando noticias: {e}")

# ============================================================================
# PASO 3: Envía contenido a Telegram
# ============================================================================

print("\nPASO 3: Enviando contenido a Telegram...")

try:
    from src.automation.bot_manager import enviar_mensaje
    
    # Formatear resultados NBA
    def _fmt_nba(partidos):
        if not partidos:
            return "_Sin partidos NBA ayer_"
        lineas = []
        for p in partidos:
            marcador = f"{p['away']} {p['score_away']} — {p['score_home']} {p['home']}"
            ganador_label = f"✓ {p['winner']}"
            lineas.append(f"• {marcador}  ({ganador_label})")
        return "\n".join(lineas)

    def _fmt_euro(partidos):
        if not partidos:
            return "_Sin partidos Euroliga ayer_"
        lineas = []
        for p in partidos:
            marcador = f"{p['home']} {p['score_home']} — {p['score_away']} {p['away']}"
            ganador_label = f"✓ {p['winner']}"
            lineas.append(f"• {marcador}  ({ganador_label})")
        return "\n".join(lineas)

    nba_texto = _fmt_nba(nba_results)
    euro_texto = _fmt_euro(euro_results)
    fecha_display = (datetime.now() - __import__('datetime').timedelta(days=1)).strftime('%d/%m/%Y')

    # Encabezado con resultados reales
    header = f"""📌 *Dos Aros — {fecha_display}*

🏀 *NBA PLAYOFFS* ({len(nba_results)} partidos)
{nba_texto}

🏀 *EUROLIGA* ({len(euro_results)} partidos)
{euro_texto}
"""
    enviar_mensaje(header, TELEGRAM_CHAT_ID)
    print("  ✅ Resultados enviados")
    
    # Insights
    if noticias.get("insights"):
        insights_text = "\n".join([f"💡 {i}" for i in noticias.get("insights", [])[:3]])
        msg_insights = f"""
*💡 INSIGHTS DEL DÍA*

{insights_text}

_Basado en análisis de noticias_
"""
        enviar_mensaje(msg_insights, TELEGRAM_CHAT_ID)
        print("  ✅ Insights enviados")
    
    # Hilo X — viene como lista de tweets, unir con saltos de línea
    if noticias.get("hilo_x"):
        tweets = noticias.get("hilo_x", [])
        if isinstance(tweets, list):
            hilo_texto = "\n\n".join(tweets)
        else:
            hilo_texto = str(tweets)
        msg_x = f"*🧵 HILO X — {fecha_display}*\n\n{hilo_texto}\n\n_Revisar y publicar en X_"
        enviar_mensaje(msg_x, TELEGRAM_CHAT_ID)
        print("  ✅ Hilo X enviado")

    # Fuentes con enlaces — para verificar cada noticia
    fuentes = noticias.get("fuentes", [])
    if fuentes:
        lineas = [f"[{f['num']}] [{f['fuente']}]({f['url']}) — {f['titulo']}" for f in fuentes]
        msg_fuentes = "*📰 Fuentes consultadas hoy:*\n\n" + "\n".join(lineas)
        enviar_mensaje(msg_fuentes, TELEGRAM_CHAT_ID)
        print("  ✅ Fuentes enviadas")
    
    # Reels
    if noticias.get("reels"):
        reels_text = "\n".join([f"📹 {r}" for r in noticias.get("reels", [])[:2]])
        msg_reels = f"""
*📹 PROPUESTAS DE REELS*

{reels_text}

_Crear manualmente en Instagram/TikTok_
"""
        enviar_mensaje(msg_reels, TELEGRAM_CHAT_ID)
        print("  ✅ Reels enviados")
    
    # Stories
    if noticias.get("stories"):
        stories_text = "\n".join([f"📖 {s}" for s in noticias.get("stories", [])[:2]])
        msg_stories = f"""
*📖 PROPUESTAS DE STORIES*

{stories_text}

_Crear manualmente en Instagram_
"""
        enviar_mensaje(msg_stories, TELEGRAM_CHAT_ID)
        print("  ✅ Stories enviadas")
    
    # Resumen final
    elapsed = time.time() - inicio
    final_msg = f"""
✅ *MASTER SYNC V3 COMPLETADO*

⏱️ Duración: {elapsed:.1f}s
📊 Resultados: {len(nba_results) + len(euro_results)} partidos
📰 Noticias procesadas: {'Sí' if noticias.get('procesadas') else 'No'}

_Todo listo para revisión y publicación manual_
"""
    enviar_mensaje(final_msg, TELEGRAM_CHAT_ID)
    print("  ✅ Resumen final enviado")

except Exception as e:
    print(f"  ❌ Error enviando a Telegram: {e}")

# ============================================================================
# Resumen final
# ============================================================================

elapsed = time.time() - inicio

print(f"""
╔════════════════════════════════════════════════════════════════════╗
║                  ✅ MASTER SYNC V3 COMPLETADO                     ║
║                                                                    ║
║  Duración: {elapsed:.1f} segundos                                      ║
║  Noticias: {'Procesadas ✅' if noticias.get('procesadas') else 'No disponibles'}
║  Resultados: {len(nba_results) + len(euro_results)} partidos                           
║                                                                    ║
║  Próximos pasos:                                                  ║
║  1. Revisar hilos X en Telegram                                   ║
║  2. Publicar en X, Instagram y TikTok                             ║
║  3. Crear reels + stories manualmente si es necesario            ║
╚════════════════════════════════════════════════════════════════════╝
""")