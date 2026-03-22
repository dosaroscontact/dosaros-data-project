#!/usr/bin/env python3
"""
================================================================================
SETUP_DEPENDENCIES.PY - Instala las librerías necesarias para Dos Aros
================================================================================

Uso:
    python setup_dependencies.py          # Instala todo
    python setup_dependencies.py --llms   # Solo LLMs
    python setup_dependencies.py --help   # Muestra opciones

"""

import subprocess
import sys
import os
from pathlib import Path


# ============================================================================
# DEFINICIÓN DE PAQUETES POR CATEGORÍA
# ============================================================================

PACKAGES = {
    # Básico (siempre necesario)
    'base': [
        'python-dotenv>=1.0.0',
        'requests>=2.32.5',
    ],
    
    # LLMs - Generadores de Texto
    'llms': [
        'google-generativeai>=0.15.0',       # Gemini
        'anthropic>=0.28.0',                 # Claude
        'openai>=1.59.0',                    # OpenAI + DeepSeek, Kimi, Grok compat
        'groq>=0.10.0',                      # Groq Llama/Mixtral
    ],
    
    # Datos y análisis
    'data': [
        'pandas>=3.0.1',
        'numpy>=2.4.2',
        'nba_api>=1.11.4',
    ],
    
    # Base de datos
    'database': [
        'psycopg2-binary>=2.9.9',            # PostgreSQL
        'sqlalchemy>=2.0.0',
    ],
    
    # Web UI y visualización
    'visualization': [
        'streamlit>=1.47.0',
        'plotly>=5.17.0',
        'altair>=5.0.0',
        'pillow>=11.0.0',                    # Generación de imágenes
    ],
    
    # Optional - Aceleración SIMD (recomendado para generación de imágenes)
    'optional': [
        'Pillow-SIMD>=9.4.0',
    ]
}


# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def print_header(text):
    """Imprime encabezado centrado."""
    print(f"\n{'='*70}")
    print(f"  {text.center(66)}")
    print(f"{'='*70}\n")


def print_section(text):
    """Imprime título de sección."""
    print(f"\n📦 {text}")
    print("-" * 70)


def run_pip_install(packages, section_name=''):
    """Instala lista de paquetes."""
    if not packages:
        return True
    
    if section_name:
        print_section(section_name)
    
    try:
        cmd = [sys.executable, '-m', 'pip', 'install', '--upgrade'] + packages
        print(f"Instalando {len(packages)} paquete(s)...\n")
        
        result = subprocess.run(cmd, capture_output=False, text=True)
        
        if result.returncode == 0:
            print(f"\n✅ {section_name if section_name else 'Paquetes'} instalados correctamente")
            return True
        else:
            print(f"\n❌ Error instalando {section_name if section_name else 'paquetes'}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def get_requirements():
    """Lee requirements.txt y devuelve lista de paquetes."""
    req_file = Path('requirements.txt')
    
    if not req_file.exists():
        print("⚠️ requirements.txt no encontrado")
        return []
    
    try:
        with open(req_file, 'r') as f:
            lines = f.readlines()
        
        packages = []
        for line in lines:
            line = line.strip()
            # Ignorar comentarios y líneas vacías
            if line and not line.startswith('#'):
                packages.append(line)
        
        return packages
    except Exception as e:
        print(f"Error leyendo requirements.txt: {e}")
        return []


def print_menu():
    """Imprime menú de opciones."""
    print("""
Opciones de instalación:

  all      → Instala TODO (base + LLMs + datos + BD + visualización)
  base     → Instala solo base (python-dotenv, requests)
  llms     → Instala solo LLMs (Gemini, Claude, OpenAI, Groq)
  data     → Instala solo dependencias de datos (pandas, numpy, nba_api)
  database → Instala solo BD (PostgreSQL, SQLAlchemy)
  viz      → Instala solo visualización (Streamlit, Plotly, Pillow)
  optional → Instala dependencias opcionales (Pillow-SIMD)
  from-req → Instala desde requirements.txt (automático)
  help     → Muestra esta ayuda
  q        → Salir

    """)


# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def main():
    """Función principal."""
    
    print_header("⚙️ SETUP DEPENDENCIES - Instalador Dos Aros")
    
    # Argumentos de línea de comandos
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        
        if arg == '--help' or arg == 'help':
            print_menu()
            return
        
        if arg == '--llms':
            run_pip_install(PACKAGES['base'] + PACKAGES['llms'], "Base + LLMs")
            return
        
        if arg == '--all':
            all_packages = (
                PACKAGES['base'] + 
                PACKAGES['llms'] + 
                PACKAGES['data'] + 
                PACKAGES['database'] + 
                PACKAGES['visualization']
            )
            run_pip_install(all_packages, "TODO (completo)")
            return
    
    # Modo interactivo
    while True:
        print_header("⚙️ SETUP DEPENDENCIES - Instalador Dos Aros")
        print_menu()
        
        opcion = input("Elige una opción: ").strip().lower()
        
        if opcion == 'q':
            print("¡Hasta luego!")
            sys.exit(0)
        
        if opcion == 'all':
            all_packages = (
                PACKAGES['base'] + 
                PACKAGES['llms'] + 
                PACKAGES['data'] + 
                PACKAGES['database'] + 
                PACKAGES['visualization']
            )
            run_pip_install(all_packages, "TODO (completo)")
        
        elif opcion == 'base':
            run_pip_install(PACKAGES['base'], "Base")
        
        elif opcion == 'llms':
            run_pip_install(PACKAGES['llms'], "LLMs")
        
        elif opcion == 'data':
            run_pip_install(PACKAGES['data'], "Datos")
        
        elif opcion == 'database':
            run_pip_install(PACKAGES['database'], "Base de Datos")
        
        elif opcion == 'viz':
            run_pip_install(PACKAGES['visualization'], "Visualización")
        
        elif opcion == 'optional':
            run_pip_install(PACKAGES['optional'], "Dependencias Opcionales")
        
        elif opcion == 'from-req':
            print_section("Instalando desde requirements.txt")
            reqs = get_requirements()
            if reqs:
                run_pip_install(reqs, f"requirements.txt ({len(reqs)} paquetes)")
            else:
                print("❌ No se encontraron paquetes en requirements.txt")
        
        elif opcion == 'help':
            continue  # Vuelve al menú
        
        else:
            print("❌ Opción no válida")
        
        input("\nPresiona ENTER para volver al menú...")


if __name__ == "__main__":
    main()
