import sqlite3
import json
import os

DB_PATH = "/mnt/nba_data/dosaros_local.db"
# Probamos con el archivo que unificamos antes
JSON_INPUT = "src/utils/all_eureleague_web.json" 

def debug_load():
    if not os.path.exists(JSON_INPUT):
        print(f"❌ ARCHIVO NO ENCONTRADO: {JSON_INPUT}")
        return

    print(f"--- Iniciando depuración de carga ---")
    print(f"Leyendo archivo: {JSON_INPUT}")
    
    try:
        with open(JSON_INPUT, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        
        print(f"Leídos {len(datos)} elementos en el nivel superior del JSON.")
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Asegurar tablas
        cursor.execute("CREATE TABLE IF NOT EXISTS euro_players_bio (player_id TEXT PRIMARY KEY, player_name TEXT, position TEXT, height INTEGER, club_name TEXT, nationality TEXT, image_url TEXT)")
        
        success_count = 0
        skipped_count = 0

        for i, item in enumerate(datos):
            # Log de inspección para el primer elemento
            if i == 0:
                print(f"DEBUG - Claves del primer elemento: {list(item.keys())}")
            
            # 1. Intentar extraer el bloque de datos (Estructura Wrapper)
            # Buscamos: item -> 'data' -> 'pageProps' -> 'data' -> 'hero'
            wrapper_data = item.get('data', {})
            page_props = wrapper_data.get('pageProps', {})
            
            # En algunos JSONs de Next.js, la info está directamente en 'data' o en 'pageProps'
            # Vamos a intentar encontrar 'hero' en cualquier parte de la jerarquía
            main = page_props.get('data', {})
            if not main:
                main = wrapper_data.get('data', {}) # Intento alternativo
            
            hero = main.get('hero', {})
            
            if not hero:
                # Si no hay hero, inspeccionamos por qué
                if i < 5: # Solo logeamos los primeros 5 fallos para no inundar la terminal
                    print(f"⚠️ Item {i} saltado: No se encontró bloque 'hero'. Claves en data/pageProps: {list(main.keys())}")
                skipped_count += 1
                continue

            # 2. Extracción de campos
            try:
                p_id = hero.get('id')
                nombre = f"{hero.get('firstName', '')} {hero.get('lastName', '')}".strip()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO euro_players_bio 
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    p_id,
                    nombre,
                    hero.get('position'),
                    hero.get('height'),
                    hero.get('clubName'),
                    hero.get('nationality'),
                    hero.get('photo')
                ))
                success_count += 1
                if i % 50 == 0:
                    print(f"PROGRESO: {i} procesados... (Último: {nombre})")
            
            except Exception as e_row:
                print(f"❌ ERROR en fila {i} ({p_id}): {e_row}")

        conn.commit()
        conn.close()
        
        print(f"\n--- RESUMEN FINAL ---")
        print(f"✅ Registros insertados: {success_count}")
        print(f"⏭️  Registros saltados: {skipped_count}")
        print(f"Base de datos actualizada en: {DB_PATH}")

    except json.JSONDecodeError:
        print("❌ ERROR: El archivo no es un JSON válido.")
    except Exception as e:
        print(f"❌ ERROR CRÍTICO: {e}")

if __name__ == "__main__":
    debug_load()