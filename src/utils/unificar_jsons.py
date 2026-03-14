import json
import os

DIR_ORIGEN = "./"
ARCHIVO_SALIDA = "./all_eureleague_web.json"

def concatenar_bruto():
    contenedor_final = []
    
    # Listamos archivos, excluyendo el de salida para no entrar en bucle
    archivos = [f for f in os.listdir(DIR_ORIGEN) 
                if f.endswith('.json') and f != "all_eureleague_web.json"]
    
    print(f"Concatenando {len(archivos)} archivos en modo bruto...")

    for nombre in archivos:
        ruta = os.path.join(DIR_ORIGEN, nombre)
        try:
            with open(ruta, 'r', encoding='utf-8') as f:
                # Leemos el contenido tal cual es (sea lista o diccionario)
                contenido_archivo = json.load(f)
                
                # Creamos el objeto envoltorio que has pedido
                envoltorio = {
                    'name_file': nombre,
                    'data': contenido_archivo
                }
                
                contenedor_final.append(envoltorio)
                print(f"✅ Incluido: {nombre}")
                
        except Exception as e:
            print(f"❌ Error leyendo {nombre}: {e}")

    # Guardamos el resultado
    if contenedor_final:
        with open(ARCHIVO_SALIDA, 'w', encoding='utf-8') as f:
            json.dump(contenedor_final, f, indent=4, ensure_ascii=False)
        print(f"\n🚀 Archivo maestro creado: {ARCHIVO_SALIDA}")
        print(f"Tamaño total: {len(contenedor_final)} bloques de datos.")
    else:
        print("No se encontró nada para procesar.")

if __name__ == "__main__":
    concatenar_bruto()