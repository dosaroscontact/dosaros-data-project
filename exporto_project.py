import os
from pathlib import Path
from datetime import datetime

# --- CONFIGURACIÓN ---
PATH_DE_LA_PI = '/home/pi/dosaros-data-project' # Pega aquí tu pwd
PROJECT_ROOT = Path(PATH_DE_LA_PI).resolve()
OUTPUT_FILE = PROJECT_ROOT / f"contexto_proyecto_{datetime.now().strftime('%Y%m%d')}.md"

# Solo leeremos archivos de código y config
ALLOWED_EXTENSIONS = {'.py', '.md', '.txt', '.yml', '.yaml', '.sql'}
IGNORE_DIRS = {'project_export', '__pycache__', 'venv', '.git', 'assets', '.venv'}

def generate_context():
    print(f"🚀 Generando snapshot de código desde: {PROJECT_ROOT}")
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f_out:
        f_out.write(f"# SNAPSHOT DEL PROYECTO: {PROJECT_ROOT.name}\n")
        f_out.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f_out.write(f"Ruta raíz: {PROJECT_ROOT}\n\n")
        f_out.write("Este archivo contiene todo el código fuente del proyecto para análisis.\n\n---\n")

        for root, dirs, files in os.walk(PROJECT_ROOT):
            # Filtrar carpetas ignoradas
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

            for file in sorted(files):
                file_path = Path(root) / file
                
                # Solo procesar si es de las extensiones permitidas
                if file_path.suffix in ALLOWED_EXTENSIONS and file_path != OUTPUT_FILE:
                    rel_path = file_path.relative_to(PROJECT_ROOT)
                    
                    print(f"📄 Procesando: {rel_path}")
                    
                    # Escribir encabezado de archivo en el MD
                    f_out.write(f"\n## ARCHIVO: {rel_path}\n")
                    f_out.write(f"```python\n") # Usamos bloque python por defecto
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f_in:
                            f_out.write(f_in.read())
                    except Exception as e:
                        f_out.write(f"Error al leer el archivo: {e}")
                    
                    f_out.write(f"\n```\n")
                    f_out.write(f"\n{'='*50}\n")

    print(f"\n✨ ¡Hecho! Todo tu código está en: {OUTPUT_FILE.name}")

if __name__ == "__main__":
    generate_context()