"""
================================================================================
EJEMPLOS DE USO - API Manager
================================================================================
Ejecutar con: python examples_api_manager.py

Este archivo contiene ejemplos ejecutables de cómo usar el API Manager
en diferentes escenarios.
"""

import sys
import os

# Agregar ruta al proyecto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.utils.api_manager import APIManager


# ============================================================================
# EJEMPLO 1: Inicializar y ver estado
# ============================================================================

def ejemplo_1_status():
    """
    Ejemplo 1: Ver qué APIs están configuradas.
    """
    print("\n" + "="*70)
    print("EJEMPLO 1: Ver estado de todas las APIs configuradas")
    print("="*70)
    
    api = APIManager()
    api.print_status()


# ============================================================================
# EJEMPLO 2: Usar Gemini
# ============================================================================

def ejemplo_2_gemini():
    """
    Ejemplo 2: Usar Google Gemini directamente.
    """
    print("\n" + "="*70)
    print("EJEMPLO 2: Google Gemini")
    print("="*70)
    
    api = APIManager()
    
    if not api.get_status()['gemini']:
        print("❌ Gemini no está configurado. Salta a ejemplo siguiente.")
        return
    
    print("Generando respuesta con Gemini...")
    
    response = api.gemini(
        prompt="Dame 3 razones por las que el baloncesto es emocionante"
    )
    
    print(f"\n✅ Respuesta de Gemini:\n{response}\n")


# ============================================================================
# EJEMPLO 3: Usar Claude
# ============================================================================

def ejemplo_3_claude():
    """
    Ejemplo 3: Usar Anthropic Claude directamente.
    """
    print("\n" + "="*70)
    print("EJEMPLO 3: Anthropic Claude")
    print("="*70)
    
    api = APIManager()
    
    if not api.get_status()['claude']:
        print("❌ Claude no está configurado. Salta a ejemplo siguiente.")
        return
    
    print("Generando respuesta con Claude...")
    
    response = api.claude(
        prompt="¿Cuál es la estrategia ganadora en el baloncesto?",
        system_prompt="Eres un entrenador de baloncesto experto."
    )
    
    print(f"\n✅ Respuesta de Claude:\n{response}\n")


# ============================================================================
# EJEMPLO 4: Usar Groq (RÁPIDO)
# ============================================================================

def ejemplo_4_groq():
    """
    Ejemplo 4: Usar Groq para respuestas rápidas (ideal para Telegram).
    """
    print("\n" + "="*70)
    print("EJEMPLO 4: Groq (Respuestas ultra-rápidas)")
    print("="*70)
    
    api = APIManager()
    
    if not api.get_status()['groq']:
        print("❌ Groq no está configurado. Salta a ejemplo siguiente.")
        return
    
    print("Generando respuesta CON GROQ (muy rápido)...")
    
    response = api.groq(
        prompt="Cuéntame en una frase qué es una asistencia en baloncesto."
    )
    
    print(f"\n✅ Respuesta de Groq (velocidad: <1s):\n{response}\n")


# ============================================================================
# EJEMPLO 5: Generar con fallback automático
# ============================================================================

def ejemplo_5_fallback():
    """
    Ejemplo 5: Generar texto con múltiples proveedores y fallback automático.
    
    Si Gemini falla, intenta Claude.
    Si Claude falla, intenta Groq.
    """
    print("\n" + "="*70)
    print("EJEMPLO 5: Generar con fallback automático")
    print("="*70)
    
    api = APIManager()
    
    print("Intentando generar respuesta con fallback: Gemini → Claude → Groq")
    
    try:
        response = api.generate_text(
            prompt="¿Quién ganó la NBA en 2020?",
            system_prompt="Eres experto en historia de NBA.",
            providers=['gemini', 'claude', 'groq']  # Orden de preferencia
        )
        
        print(f"\n✅ Respuesta generada con fallback:\n{response}\n")
    except ValueError as e:
        print(f"❌ Error: {e}")


# ============================================================================
# EJEMPLO 6: Generar imagen (Together)
# ============================================================================

def ejemplo_6_imagen_together():
    """
    Ejemplo 6: Generar imagen con Together AI (Flux.1 Schnell).
    """
    print("\n" + "="*70)
    print("EJEMPLO 6: Generar imagen con Together AI")
    print("="*70)
    
    api = APIManager()
    
    if not api.get_status()['together']:
        print("❌ Together AI no está configurado. Salta a ejemplo siguiente.")
        return
    
    print("Generando imagen con Together AI...")
    
    try:
        image_url = api.generate_image(
            prompt="Cartel profesional de baloncesto con un jugador en acción, "
                   "colores vibrantes, estilo moderno, texto legible 'DOS AROS'",
            provider="together",
            size="1024x1024"
        )
        
        print(f"\n✅ Imagen generada:\n{image_url}\n")
    except Exception as e:
        print(f"❌ Error generando imagen: {e}")


# ============================================================================
# EJEMPLO 7: Generar imagen FREE (Pollinations)
# ============================================================================

def ejemplo_7_imagen_free():
    """
    Ejemplo 7: Generar imagen GRATIS con Pollinations (sin KEY requerida).
    """
    print("\n" + "="*70)
    print("EJEMPLO 7: Generar imagen GRATIS con Pollinations")
    print("="*70)
    
    api = APIManager()
    
    print("Generando imagen con Pollinations (FREE)...")
    
    try:
        image_url = api.generate_image(
            prompt="Jugador de NBA tirando un triple, estadio de fondo, "
                   "luces de neón azul y naranja",
            provider="pollinations"
        )
        
        print(f"\n✅ Imagen generada (FREE):\n{image_url}\n")
        print("💡 Nota: Pollinations genera imágenes sin limite, sin KEY requerida")
    except Exception as e:
        print(f"❌ Error: {e}")


# ============================================================================
# EJEMPLO 8: Generar audio (Text-to-Speech)
# ============================================================================

def ejemplo_8_audio():
    """
    Ejemplo 8: Generar audio con ElevenLabs.
    """
    print("\n" + "="*70)
    print("EJEMPLO 8: Generar audio (Text-to-Speech) con ElevenLabs")
    print("="*70)
    
    api = APIManager()
    
    if not api.get_status()['elevenlabs']:
        print("❌ ElevenLabs no está configurado. Salta a ejemplo siguiente.")
        return
    
    print("Generando audio con ElevenLabs...")
    
    try:
        audio_bytes = api.text_to_speech(
            text="Hola, este es el análisis de hoy. Los Lakers ganaron con una "
                 "soberbia actuación de su estrella LeBron James. "
                 "Un partido para recordar.",
            provider="elevenlabs"
        )
        
        # Guardar el audio
        filename = "audio_ejemplo.mp3"
        with open(filename, "wb") as f:
            f.write(audio_bytes)
        
        print(f"\n✅ Audio generado y guardado en: {filename}\n")
        print(f"📊 Tamaño del archivo: {len(audio_bytes)} bytes\n")
    except Exception as e:
        print(f"❌ Error generando audio: {e}")


# ============================================================================
# EJEMPLO 9: Caso de uso real - Análisis de NBA
# ============================================================================

def ejemplo_9_caso_real():
    """
    Ejemplo 9: Caso de uso real - Analista IA para NBA.
    
    Simula cómo se usaría el API Manager en un contexto real:
    - Usuario pregunta sobre NBA
    - API Manager genera respuesta con fallback
    - Resultado se formatea para mostrar
    """
    print("\n" + "="*70)
    print("EJEMPLO 9: Caso real - Analista IA NBA")
    print("="*70)
    
    api = APIManager()
    
    system_prompt = """
    Eres un experto analista de NBA con experiencia en estadísticas y estrategia.
    Responde preguntas sobre jugadores, equipos y temporadas con precisión.
    """
    
    pregunta = "¿Cuáles son los 3 mejores tiradores de 3-pointers de la NBA actual?"
    
    print(f"Pregunta: {pregunta}")
    print(f"\nGenerando análisis con fallback automático...")
    
    try:
        respuesta = api.generate_text(
            prompt=pregunta,
            system_prompt=system_prompt,
            providers=['gemini', 'claude', 'groq']
        )
        
        print(f"\n✅ Análisis NBA:\n{respuesta}\n")
    except Exception as e:
        print(f"❌ Error: {e}")


# ============================================================================
# EJEMPLO 10: Manejo de errores y recuperación
# ============================================================================

def ejemplo_10_error_handling():
    """
    Ejemplo 10: Cómo manejar errores y recuperarse.
    """
    print("\n" + "="*70)
    print("EJEMPLO 10: Manejo de errores")
    print("="*70)
    
    api = APIManager()
    
    # Caso 1: Verificar disponibilidad antes de usar
    print("\n🔍 Verificando disponibilidad de APIs...")
    status = api.get_status()
    
    apis_disponibles = [k for k, v in status.items() if v and k in ['gemini', 'claude', 'groq']]
    
    if not apis_disponibles:
        print("❌ No hay LLMs disponibles. Configura al menos uno en .env")
        return
    
    print(f"✅ APIs disponibles: {', '.join(apis_disponibles)}")
    
    # Caso 2: Usar solo lo que está disponible
    print("\nUsando fallback con APIs disponibles...")
    
    try:
        respuesta = api.generate_text(
            prompt="Di 'Hola' en una sola palabra.",
            providers=apis_disponibles
        )
        print(f"✅ Respuesta: {respuesta}")
    except Exception as e:
        print(f"❌ Error final: {e}")


# ============================================================================
# MENÚ PRINCIPAL
# ============================================================================

def main():
    """
    Menú principal para ejecutar ejemplos.
    """
    ejemplos = {
        '1': ('Ver estado de APIs', ejemplo_1_status),
        '2': ('Google Gemini', ejemplo_2_gemini),
        '3': ('Anthropic Claude', ejemplo_3_claude),
        '4': ('Groq (Rápido)', ejemplo_4_groq),
        '5': ('Generar con Fallback', ejemplo_5_fallback),
        '6': ('Generar imagen (Together)', ejemplo_6_imagen_together),
        '7': ('Generar imagen FREE (Pollinations)', ejemplo_7_imagen_free),
        '8': ('Generar audio (ElevenLabs)', ejemplo_8_audio),
        '9': ('Caso real - NBA Analyzer', ejemplo_9_caso_real),
        '10': ('Manejo de errores', ejemplo_10_error_handling),
        'all': ('Ejecutar todos', None),
    }
    
    print("\n" + "="*70)
    print("🎯 EJEMPLOS DE USO - API MANAGER")
    print("="*70)
    
    print("\nElige un ejemplo para ejecutar:\n")
    for key, (descripcion, _) in ejemplos.items():
        if key != 'all':
            print(f"  {key:3} → {descripcion}")
    
    print(f"\n  all → Ejecutar todos los ejemplos")
    print(f"  q   → Salir\n")
    
    while True:
        opcion = input("Elige una opción: ").strip().lower()
        
        if opcion == 'q':
            print("¡Hasta luego!")
            break
        
        if opcion == 'all':
            for key in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']:
                try:
                    ejemplos[key][1]()
                except Exception as e:
                    print(f"❌ Error en ejemplo {key}: {e}")
        elif opcion in ejemplos and ejemplos[opcion][1]:
            try:
                ejemplos[opcion][1]()
            except Exception as e:
                print(f"❌ Error: {e}")
        else:
            print("❌ Opción no válida. Intenta de nuevo.\n")
        
        if opcion != 'all':
            input("\nPresiona ENTER para volver al menú...")


if __name__ == "__main__":
    main()
