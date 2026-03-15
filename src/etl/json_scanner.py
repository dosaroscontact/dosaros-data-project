import json
import os
import sys
from collections import Counter

# Build ID para reconstrucción de URLs (se puede actualizar según la versión del sitio)
BUILD_ID = "hvGIyKafFCKSt6G5KJbO-"

# Glosario para documentar el significado de las claves
GLOSARIO_CLAVES = {
    "hero": "Bloque principal con la identidad visual y biográfica",
    "id": "Identificador único en el sistema de origen",
    "firstName": "Nombre de pila del sujeto",
    "lastName": "Apellidos completos",
    "stats": "Contenedor de métricas de rendimiento y carrera",
    "currentSeason": "Estadísticas acumuladas de la temporada en curso",
    "careerHighs": "Récords históricos personales por categoría estadística",
    "clubCode": "Código de tres letras que identifica al equipo actual",
    "photo": "URL directa a la imagen oficial en el CDN",
    "position": "Rol o posición táctica en el campo",
    "height": "Altura física registrada (normalmente en cm)",
    "nationality": "País de origen o nacionalidad deportiva"
}

def obtener_metadata_url(datos):
    """Intenta reconstruir la URL de origen basándose en la estructura del JSON."""
    try:
        # Intento de reconstrucción para perfiles individuales
        hero = datos.get('pageProps', {}).get('data', {}).get('hero', {})
        if hero:
            p_id = hero.get('id')
            f_name = hero.get('firstName', '').lower().replace(' ', '-')
            l_name = hero.get('lastName', '').lower().replace(' ', '-')
            return f"https://www.euroleaguebasketball.net/_next/data/{BUILD_ID}/en/euroleague/players/{f_name}-{l_name}/{p_id}.json"
    except:
        pass
    return "URL no determinada (estructura no estándar)"

def analizar_estructura(obj, ruta="root", nivel=0):
    indent = "  " * nivel
    # Obtenemos descripción del glosario si existe
    desc = f" | ℹ️ {GLOSARIO_CLAVES[ruta]}" if ruta in GLOSARIO_CLAVES else ""

    if isinstance(obj, dict):
        resumen = [f"{indent}📂 {ruta} (Objeto){desc}"]
        for clave, valor in obj.items():
            resumen.extend(analizar_estructura(valor, clave, nivel + 1))
        return resumen
    
    elif isinstance(obj, list):
        tipos_internos = Counter([type(elem).__name__ for elem in obj])
        resumen = [f"{indent}📜 {ruta} (Lista con {len(obj)} elementos de tipo: {dict(tipos_internos)}){desc}"]
        if len(obj) > 0 and isinstance(obj[0], dict):
            resumen.append(f"{indent}  🔍 Estructura del primer hijo:")
            for clave_hijo, valor_hijo in obj[0].items():
                desc_hijo = f" | ℹ️ {GLOSARIO_CLAVES[clave_hijo]}" if clave_hijo in GLOSARIO_CLAVES else ""
                resumen.append(f"{indent}    - {clave_hijo}: {type(valor_hijo).__name__}{desc_hijo}")
        return resumen
    
    else:
        return [f"{indent}🔹 {ruta}: {type(obj).__name__}{desc}"]

def ejecutar_escaneo():
    if len(sys.argv) < 2:
        print("Uso: python3 src/etl/json_scanner.py ruta/al/archivo.json")
        return

    ruta_archivo = sys.argv[1]
    nombre_fichero = os.path.basename(ruta_archivo)

    if not os.path.exists(ruta_archivo):
        print(f"❌ Error: El archivo {ruta_archivo} no existe.")
        return

    with open(ruta_archivo, 'r', encoding='utf-8') as f:
        try:
            datos = json.load(f)
            url_procedencia = obtener_metadata_url(datos)
            
            # Construcción de la ficha de documentación
            encabezado = [
                "=========================================================",
                " DOCUMENTACIÓN DE ESTRUCTURA JSON",
                f" Archivo: {nombre_fichero}",
                f" URL de origen: {url_procedencia}",
                "=========================================================\n"
            ]
            
            informe = analizar_estructura(datos)
            resultado_completo = "\n".join(encabezado + informe)
            
            print(resultado_completo)
            
            # Guardado del reporte técnico
            nombre_salida = f"doc_{nombre_fichero.replace('.json', '.txt')}"
            with open(nombre_salida, "w", encoding="utf-8") as f_out:
                f_out.write(resultado_completo)
            
            print(f"\n✅ Análisis guardado en: {nombre_salida}")
            
        except Exception as e:
            print(f"❌ Error al procesar el JSON: {e}")

if __name__ == "__main__":
    ejecutar_escaneo()