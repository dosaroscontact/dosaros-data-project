import json
import os

JSON_INPUT = "src/utils/all_eureleague_web.json"
JSON_OUTPUT = "src/etl/estructura_reducida.json"

def podar_json(obj, limite=2):
    """Recorre el JSON y deja solo 'limite' elementos en las listas."""
    if isinstance(obj, dict):
        return {k: podar_json(v, limite) for k, v in obj.items()}
    elif isinstance(obj, list):
        # Solo tomamos los primeros elementos para ver la estructura
        return [podar_json(elem, limite) for elem in obj[:limite]]
    else:
        return obj

def generar_mapa():
    if not os.path.exists(JSON_INPUT):
        print(f"❌ No encuentro el archivo en {JSON_INPUT}")
        return

    print(f"Leyendo {JSON_INPUT} para analizar estructura...")
    
    try:
        with open(JSON_INPUT, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Podamos el objeto (que suele ser una lista de archivos unificados)
        mapa_reducido = podar_json(data, limite=2)
        
        with open(JSON_OUTPUT, 'w', encoding='utf-8') as f:
            json.dump(mapa_reducido, f, indent=4, ensure_ascii=False)
            
        print(f"✅ Mapa generado en: {JSON_OUTPUT}")
        print("Ábrelo en VS Code y usa 'Ctrl+Shift+P' -> 'Format Document' para verlo claro.")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    generar_mapa()