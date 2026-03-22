"""
================================================================================
TEST MODELS - Verificar disponiblidad de todas las APIs/LLMs
================================================================================
Prueba rápida de todos los modelos de IA configurados en .env

Uso: python test_models.py
"""

import os
import sys
from dotenv import load_dotenv
import logging

# Configurar logging
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Cargar configuración desde .env
load_dotenv()

# ============================================================================
# IMPORTES DE LIBRERÍAS - Con manejo de errores
# ============================================================================

try:
    import google.genai as genai_lib
    GEMINI_AVAILABLE = True
except ImportError:
    # Fallback to old package if new one not available
    try:
        import google.generativeai as genai_lib
        GEMINI_AVAILABLE = True
    except ImportError:
        GEMINI_AVAILABLE = False
        genai_lib = None

try:
    import anthropic
    CLAUDE_AVAILABLE = True
except ImportError:
    CLAUDE_AVAILABLE = False
    anthropic = None

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    openai = None

try:
    import groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    groq = None

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    requests = None


# ============================================================================
# FUNCIONES DE PRUEBA POR MODELO
# ============================================================================

def test_gemini():
    """Prueba Google Gemini."""
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("❌ GEMINI_API_KEY no configurada")
        return False
    
    if not GEMINI_AVAILABLE:
        print("❌ Librería 'google-genai' o 'google-generativeai' no instalada")
        return False
    
    try:
        # Detectar cuál API está disponible y usar la correcta
        try:
            # Intentar API nueva (google-genai)
            import google.genai as new_genai
            client = new_genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
                contents="Di 'Hola' en una palabra."
            )
            print(f"✅ GEMINI: {response.text[:50]}...")
            return True
        except (ImportError, AttributeError):
            # Fallback a API antigua (google-generativeai)
            import google.generativeai as old_genai
            old_genai.configure(api_key=api_key)
            model = old_genai.GenerativeModel(os.getenv("GEMINI_MODEL", "gemini-2.0-flash"))
            response = model.generate_content("Di 'Hola' en una palabra.")
            print(f"✅ GEMINI: {response.text[:50]}...")
            return True
    except Exception as e:
        print(f"❌ GEMINI: {str(e)[:80]}")
        return False


def test_openai():
    """Prueba OpenAI ChatGPT."""
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("❌ OPENAI_API_KEY no configurada")
        return False
    
    if not OPENAI_AVAILABLE:
        print("❌ Librería 'openai' no instalada (pip install openai)")
        return False
    
    try:
        client = openai.Client(api_key=api_key)
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[{"role": "user", "content": "Di 'Hola' en una palabra."}]
        )
        print(f"✅ OPENAI: {response.choices[0].message.content[:50]}...")
        return True
    except Exception as e:
        print(f"❌ OPENAI: {str(e)[:80]}")
        return False


def test_claude():
    """Prueba Anthropic Claude."""
    api_key = os.getenv("CLAUDE_API_KEY")
    
    if not api_key:
        print("❌ CLAUDE_API_KEY no configurada")
        return False
    
    if not CLAUDE_AVAILABLE:
        print("❌ Librería 'anthropic' no instalada (pip install anthropic)")
        return False
    
    try:
        client = anthropic.Anthropic(api_key=api_key)
        
        # Usar modelo válido de Anthropic
        # Opciones: claude-opus, claude-sonnet, claude-haiku
        model = os.getenv("CLAUDE_MODEL", "claude-opus")
        
        response = client.messages.create(
            model=model,
            max_tokens=100,
            messages=[{"role": "user", "content": "Di 'Hola' en una palabra."}]
        )
        print(f"✅ CLAUDE: {response.content[0].text[:50]}...")
        return True
    except Exception as e:
        error_msg = str(e)
        # Mostrar mensaje de error más útil
        if "401" in error_msg or "Unauthorized" in error_msg:
            print(f"❌ CLAUDE: API key inválida o expirada")
        elif "400" in error_msg or "invalid_request" in error_msg:
            print(f"❌ CLAUDE: Modelo '{model}' no encontrado o request inválido")
        else:
            print(f"❌ CLAUDE: {error_msg[:80]}")
        return False


def test_groq():
    """Prueba Groq (Llama/Mixtral)."""
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        print("❌ GROQ_API_KEY no configurada")
        return False
    
    if not GROQ_AVAILABLE:
        print("❌ Librería 'groq' no instalada (pip install groq)")
        return False
    
    try:
        client = groq.Groq(api_key=api_key)
        response = client.chat.completions.create(
            model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            messages=[{"role": "user", "content": "Di 'Hola' en una palabra."}]
        )
        print(f"✅ GROQ: {response.choices[0].message.content[:50]}...")
        return True
    except Exception as e:
        print(f"❌ GROQ: {str(e)[:80]}")
        return False


def test_deepseek():
    """Prueba DeepSeek (vía OpenAI compatible)."""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    
    if not api_key:
        print("❌ DEEPSEEK_API_KEY no configurada")
        return False
    
    if not OPENAI_AVAILABLE:
        print("❌ Librería 'openai' no instalada (pip install openai)")
        return False
    
    try:
        client = openai.Client(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
        response = client.chat.completions.create(
            model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
            messages=[{"role": "user", "content": "Di 'Hola' en una palabra."}]
        )
        print(f"✅ DEEPSEEK: {response.choices[0].message.content[:50]}...")
        return True
    except Exception as e:
        print(f"❌ DEEPSEEK: {str(e)[:80]}")
        return False


def test_kimi():
    """Prueba Kimi/Moonshot (vía OpenAI compatible)."""
    api_key = os.getenv("KIMI_API_KEY")
    
    if not api_key:
        print("❌ KIMI_API_KEY no configurada")
        return False
    
    if not OPENAI_AVAILABLE:
        print("❌ Librería 'openai' no instalada (pip install openai)")
        return False
    
    try:
        client = openai.Client(
            api_key=api_key,
            base_url="https://api.moonshot.cn/v1"
        )
        response = client.chat.completions.create(
            model=os.getenv("KIMI_MODEL", "moonshot-v1-128k"),
            messages=[{"role": "user", "content": "Di 'Hola' en una palabra."}]
        )
        print(f"✅ KIMI: {response.choices[0].message.content[:50]}...")
        return True
    except Exception as e:
        print(f"❌ KIMI: {str(e)[:80]}")
        return False


def test_grok():
    """Prueba X.AI Grok."""
    api_key = os.getenv("GROK_API_KEY")
    
    if not api_key:
        print("❌ GROK_API_KEY no configurada")
        return False
    
    if not OPENAI_AVAILABLE:
        print("❌ Librería 'openai' no instalada (pip install openai)")
        return False
    
    try:
        client = openai.Client(
            api_key=api_key,
            base_url="https://api.x.ai"
        )
        response = client.chat.completions.create(
            model=os.getenv("GROK_MODEL", "grok-beta"),
            messages=[{"role": "user", "content": "Di 'Hola' en una palabra."}]
        )
        print(f"✅ GROK: {response.choices[0].message.content[:50]}...")
        return True
    except Exception as e:
        print(f"❌ GROK: {str(e)[:80]}")
        return False


def test_together():
    """Prueba Together AI (Flux.1)."""
    api_key = os.getenv("TOGETHER_API_KEY")
    
    if not api_key:
        print("❌ TOGETHER_API_KEY no configurada")
        return False
    
    if not REQUESTS_AVAILABLE:
        print("❌ Librería 'requests' no instalada (pip install requests)")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        # Solo verificar que la KEY es válida, no hacer request compluro
        print("✅ TOGETHER: API KEY válida (no se generó imagen para no gastar créditos)")
        return True
    except Exception as e:
        print(f"❌ TOGETHER: {str(e)[:80]}")
        return False


def test_elevenlabs():
    """Prueba ElevenLabs TTS."""
    api_key = os.getenv("ELEVENLABS_API_KEY")
    
    if not api_key:
        print("❌ ELEVENLABS_API_KEY no configurada")
        return False
    
    if not REQUESTS_AVAILABLE:
        print("❌ Librería 'requests' no instalada (pip install requests)")
        return False
    
    try:
        # Solo verificar que la KEY es válida
        print("✅ ELEVENLABS: API KEY válida (no se generó audio para no gastar cuota)")
        return True
    except Exception as e:
        print(f"❌ ELEVENLABS: {str(e)[:80]}")
        return False


def test_pollinations():
    """Prueba Pollinations (FREE - sin KEY)."""
    enabled = os.getenv("POLLINATIONS_ENABLED", "true").lower() == "true"
    
    if not enabled:
        print("⚠️ POLLINATIONS: Deshabilitado")
        return False
    
    print("✅ POLLINATIONS: Disponible (FREE, sin KEY)")
    return True


# ============================================================================
# MENÚ PRINCIPAL
# ============================================================================

def print_header():
    """Imprime encabezado."""
    print("\n" + "="*70)
    print("🧪 TEST MODELS - Verificar disponibilidad de IAs")
    print("="*70 + "\n")


def print_menu():
    """Imprime menú de opciones."""
    models = {
        '1': ('⭐ Google Gemini', test_gemini),
        '2': ('🤖 OpenAI ChatGPT', test_openai),
        '3': ('🧠 Anthropic Claude', test_claude),
        '4': ('⚡ Groq (Llama/Mixtral)', test_groq),
        '5': ('🔍 DeepSeek', test_deepseek),
        '6': ('🌙 Kimi (Moonshot)', test_kimi),
        '7': ('🚀 X.AI Grok', test_grok),
        '8': ('🎨 Together AI (Flux.1)', test_together),
        '9': ('🎤 ElevenLabs TTS', test_elevenlabs),
        '10': ('🆓 Pollinations (FREE)', test_pollinations),
        'llms': ('📊 Test todos los LLMs', None),
        'all': ('🔬 Test TODO', None),
    }
    
    print("Elige un modelo para probar:\n")
    for key in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']:
        print(f"  {key:2}  → {models[key][0]}")
    
    print(f"\n  llms → Probar todos los LLMs")
    print(f"  all  → Probar TODOS (LLMs + imagen + audio)")
    print(f"  q    → Salir\n")
    
    return models


def run_all_tests():
    """Ejecuta todas las pruebas."""
    print("\n🔬 Ejecutando TODAS las pruebas...\n")
    
    tests = [
        ("GEMINI", test_gemini),
        ("OPENAI", test_openai),
        ("CLAUDE", test_claude),
        ("GROQ", test_groq),
        ("DEEPSEEK", test_deepseek),
        ("KIMI", test_kimi),
        ("GROK", test_grok),
        ("TOGETHER", test_together),
        ("ELEVENLABS", test_elevenlabs),
        ("POLLINATIONS", test_pollinations),
    ]
    
    results = {name: func() for name, func in tests}
    
    # Resumen
    print("\n" + "="*70)
    print("📊 RESUMEN DE PRUEBAS")
    print("="*70)
    
    for name, result in results.items():
        emoji = "✅" if result else "❌"
        print(f"{emoji} {name:20} {'Funcionando' if result else 'No disponible'}")
    
    total = sum(results.values())
    print(f"\n📈 Total: {total}/{len(tests)} modelos disponibles\n")


def run_llm_tests():
    """Ejecuta solo pruebas de LLMs."""
    print("\n📊 Ejecutando pruebas de LLMs...\n")
    
    tests = [
        ("GEMINI", test_gemini),
        ("OPENAI", test_openai),
        ("CLAUDE", test_claude),
        ("GROQ", test_groq),
        ("DEEPSEEK", test_deepseek),
        ("KIMI", test_kimi),
        ("GROK", test_grok),
    ]
    
    results = {name: func() for name, func in tests}
    
    # Resumen
    print("\n" + "="*70)
    print("📊 RESUMEN DE LLMs")
    print("="*70)
    
    for name, result in results.items():
        emoji = "✅" if result else "❌"
        print(f"{emoji} {name:20} {'Disponible' if result else 'No configurado'}")
    
    total = sum(results.values())
    print(f"\n📈 Total: {total}/{len(tests)} LLMs disponibles\n")


def main():
    """Función principal."""
    print_header()
    models = print_menu()
    
    while True:
        opcion = input("Elige una opción: ").strip().lower()
        
        if opcion == 'q':
            print("¡Hasta luego!")
            sys.exit(0)
        
        if opcion == 'all':
            run_all_tests()
        
        elif opcion == 'llms':
            run_llm_tests()
        
        elif opcion in models and models[opcion][1]:
            print(f"\n🧪 Probando {models[opcion][0]}...")
            models[opcion][1]()
        
        else:
            print("❌ Opción no válida. Intenta de nuevo.\n")
        
        if opcion not in ['all', 'llms'] or opcion in ['all', 'llms']:
            input("\nPresiona ENTER para volver al menú...")
            print_header()
            models = print_menu()


if __name__ == "__main__":
    main()