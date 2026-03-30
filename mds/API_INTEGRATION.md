# 🔌 GUÍA DE INTEGRACIÓN APIs - API Manager

**Última actualización:** 22 de Marzo 2026  
**Propósito:** Documentar cómo adaptar scripts existentes para usar el nuevo API Manager centralizado

---

## 📋 CONTENIDO

1. [Visión General](#visión-general)
2. [Instalación y Setup](#instalación-y-setup)
3. [Uso Básico](#uso-básico)
4. [Ejemplos de Integración](#ejemplos-de-integración)
5. [Migrando Scripts Existentes](#migrando-scripts-existentes)
6. [Fallback y Manejo de Errores](#fallback-y-manejo-de-errores)
7. [Troubleshooting](#troubleshooting)

---

## 🎯 Visión General

### Antes (sin API Manager)
```python
# ❌ PROBLEMA: Importar de múltiples librerías, configurar en cada script
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")
response = model.generate_content("Hola")
```

### Después (con API Manager)
```python
# ✅ SOLUCIÓN: Una sola interfaz, centralizada, con fallback automático
from src.utils.api_manager import APIManager

api = APIManager()
response = api.gemini("Hola")

# O con fallback:
response = api.generate_text("Hola", providers=['gemini', 'claude', 'groq'])
```

---

## 🚀 Instalación y Setup

### Paso 1: Instalar dependencias (ya están en requirements.txt)

```bash
pip install google-generativeai anthropic openai groq python-dotenv
```

### Paso 2: Configurar .env

Copiar `.env.example` a `.env` y llenar con tus claves:

```bash
cp .env.example .env
# Editar .env y añadir tus claves
nano .env
```

### Paso 3: Importar y usar

```python
from src.utils.api_manager import APIManager

api = APIManager()
api.print_status()  # Ver qué APIs están configuradas
```

---

## 💻 Uso Básico

### Inicializar el API Manager

```python
from src.utils.api_manager import APIManager

# Se crea UNA SOLA instancia (el manager carga todos los clientes)
api = APIManager()

# Ver estado de todas las APIs
api.print_status()
```

### Usar una API específica

```python
# Google Gemini
response = api.gemini("¿Top 3 anotadores NBA ayer?")

# Claude
response = api.claude("Analiza esta estadística...")

# OpenAI
response = api.openai("Genera un JSON con...")

# Groq (la más rápida)
response = api.groq("Responde rápidamente: ...")
```

### Usar con fallback automático

```python
# Intenta Gemini, si falla intenta Claude, luego Groq
response = api.generate_text(
    prompt="¿Quién es el mejor tirador de triples?",
    system_prompt="Eres analista NBA experto",
    providers=['gemini', 'claude', 'groq']
)
```

### Generar imágenes

```python
# Together AI (recomendado)
image_url = api.generate_image(
    prompt="Cartel de Instagram: Top 3 cazadores de triples NBA",
    provider="together"
)

# Pollinations (gratis, sin KEY)
image_url = api.generate_image(
    prompt="...",
    provider="pollinations"
)
```

### Generar audio (TTS)

```python
audio_bytes = api.text_to_speech(
    text="Dentro de dos minutos comienza el partido entre Lakers y Celtics",
    provider="elevenlabs",
    voice_id="optional_voice_id"
)

# Guardar a archivo
with open("narration.mp3", "wb") as f:
    f.write(audio_bytes)
```

### Obtener estado

```python
status = api.get_status()
print(status)
# {'gemini': True, 'claude': False, 'groq': True, 'together': True, ...}

# O imprimir de forma bonita
api.print_status()
```

---

## 📊 Ejemplos de Integración

### Ejemplo 1: Integrar en main.py (Streamlit)

**ANTES:**
```python
# src/app/main.py
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY)
```

**DESPUÉS:**
```python
# src/app/main.py
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.utils.api_manager import APIManager

api = APIManager()

def obtener_sql_ia(pregunta):
    contexto = """Eres experto en SQLite..."""
    prompt = f"{contexto}\n\nPregunta: {pregunta}"
    
    # Usa Gemini con fallback a Claude
    return api.generate_text(
        prompt=prompt,
        providers=['gemini', 'claude']
    )
```

---

### Ejemplo 2: Integrar en analista_ia.py

**ANTES:**
```python
# src/app/analista_ia.py
import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY)

def preguntar_a_gemini(pregunta_usuario):
    # Código duplicado...
```

**DESPUÉS:**
```python
# src/app/analista_ia.py
from src.utils.api_manager import APIManager

def preguntar_a_gemini(pregunta_usuario):
    api = APIManager()
    return api.gemini(pregunta_usuario)
```

---

### Ejemplo 3: Integrar en gemini_social.py

**ANTES:**
```python
# src/processors/gemini_social.py
from google import genai
import os
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def generar_hilo_resultados():
    # Prompts largos manualmente...
```

**DESPUÉS:**
```python
# src/processors/gemini_social.py
from src.utils.api_manager import APIManager

def generar_hilo_resultados():
    api = APIManager()
    
    system_prompt = "Eres especialista en redes sociales deportivas..."
    prompt = "Genera 3 tweets sobre estos resultados..."
    
    return api.generate_text(
        prompt=prompt,
        system_prompt=system_prompt,
        providers=['gemini', 'groq']  # Groq es rápido para Twitter
    )
```

---

### Ejemplo 4: Crear imagen para Telegram

```python
# En master_sync.py o cualquier procesador

from src.utils.api_manager import APIManager
from automation.bot_manager import enviar_grafico

async def crear_y_enviar_imagen_perlas():
    api = APIManager()
    
    # Generar imagen
    image_url = api.generate_image(
        prompt="Post Instagram profesional: Top 3 cazadores de 3-pointers NBA 2026. "
               "Estilo moderno, fuente legible, colores Mint (#88D4AB) y Coral (#FF8787)",
        provider="together"
    )
    
    # Enviar a Telegram
    enviar_grafico(image_url, "🏀 Perlas del día - Cazadores de triples")
```

---

### Ejemplo 5: Fallback inteligente según disponibilidad

```python
from src.utils.api_manager import APIManager

def generar_analisis_con_fallback():
    api = APIManager()
    status = api.get_status()
    
    # Construir lista de proveedores disponibles
    available = []
    if status['gemini']:
        available.append('gemini')  # Primera opción
    if status['claude']:
        available.append('claude')  # Segunda opción
    if status['groq']:
        available.append('groq')    # Tercera opción (rápida)
    
    if not available:
        raise ValueError("❌ Ningún LLM disponible")
    
    # Usar cualquiera de los disponibles
    return api.generate_text(
        prompt="Analiza estos datos...",
        providers=available
    )
```

---

## 🔄 Migrando Scripts Existentes

### Paso 1: Identificar archivos que usan APIs

```bash
# Buscar imports de API clients
grep -r "import genai\|import anthropic\|import openai\|import groq" src/
```

**Archivos que necesitan actualización:**
- `src/app/main.py` (obtener_sql_ia)
- `src/app/analista_ia.py` (preguntar_a_gemini)
- `src/processors/gemini_social.py` (generar_hilo_resultados)
- `src/app/test_models.py` (ya actualizado ✅)

### Paso 2: Patrón de migración

```python
# PASO A: Cambiar importes
# ANTES:
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# DESPUÉS:
from src.utils.api_manager import APIManager
api = APIManager()

# PASO B: Cambiar llamadas
# ANTES:
response = client.models.generate_content(prompt)

# DESPUÉS:
response = api.gemini(prompt)

# PASO C: Agregar fallback si quieres
# ANTES:
response = api.gemini(prompt)

# DESPUÉS (con fallback):
response = api.generate_text(
    prompt=prompt,
    providers=['gemini', 'claude', 'groq']
)
```

### Paso 3: Ejemplo completo de migración

**ANTES (src/app/analista_ia.py):**
```python
import sqlite3
import pandas as pd
import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
DB_PATH = "/mnt/nba_data/dosaros_local.db"

client = genai.Client(api_key=API_KEY)
MODELO_ACTIVO = "gemini-flash-latest"

def preguntar_a_gemini(pregunta_usuario):
    prompt_final = f"Eres experto en SQLite...\n\nPregunta: {pregunta_usuario}"
    response = client.models.generate_content(
        model=MODELO_ACTIVO,
        contents=prompt_final
    )
    return response.text.replace("```sql", "").replace("```", "").strip()
```

**DESPUÉS (src/app/analista_ia.py):**
```python
import sys
import os
import sqlite3
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from src.utils.api_manager import APIManager

DB_PATH = "/mnt/nba_data/dosaros_local.db"
api = APIManager()

def preguntar_a_gemini(pregunta_usuario):
    system_prompt = "Eres experto en SQLite. Genera SQL limpio sin markdown."
    prompt_final = f"Pregunta: {pregunta_usuario}"
    
    response = api.generate_text(
        prompt=prompt_final,
        system_prompt=system_prompt,
        providers=['gemini', 'claude']  # Fallback a Claude si Gemini falla
    )
    
    return response.replace("```sql", "").replace("```", "").strip()
```

---

## 🛡️ Fallback y Manejo de Errores

### Fallback automático

```python
# Intenta providers en orden, salta al siguiente si falla
response = api.generate_text(
    prompt="...",
    providers=['gemini', 'claude', 'groq', 'openai']
)
```

### Fallback manual con try/except

```python
from src.utils.api_manager import APIManager

api = APIManager()

try:
    # Intenta Gemini
    response = api.gemini(prompt)
except ValueError:
    print("❌ Gemini no disponible, intentando Claude...")
    try:
        response = api.claude(prompt)
    except ValueError:
        print("❌ Claude no disponible, intentando Groq...")
        response = api.groq(prompt)
```

### Verificar disponibilidad antes

```python
status = api.get_status()

if status['gemini']:
    response = api.gemini(prompt)
elif status['claude']:
    response = api.claude(prompt)
elif status['groq']:
    response = api.groq(prompt)
else:
    raise ValueError("❌ No hay LLMs disponibles")
```

---

## 🔧 Troubleshooting

### Error: "ModuleNotFoundError: No module named 'src.utils.api_manager'"

**Solución:**
```python
# Asegúrate de que el import path es correcto
# Si estás en src/app/main.py, importa así:
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from src.utils.api_manager import APIManager
```

### Error: "GEMINI_API_KEY no configurada"

**Solución:**
```bash
# 1. Verifica que .env existe
ls -la .env

# 2. Verifica que contiene GEMINI_API_KEY
grep GEMINI_API_KEY .env

# 3. Verifica que .env es UTF-8 (no UTF-16)
file .env
# Debe ser: UTF-8 Unicode text

# 4. Recarga el terminal/IDE
```

### Error: "Ningún proveedor disponible"

**Solución:**
```python
# Verificar qué APIs están configuradas
api = APIManager()
api.print_status()

# Todos deben ser ✅ para tu setup inicial
# Si ves ❌, significa que KEY no está en .env
```

---

## 📚 API Manager - Referencia Rápida

### Métodos principales

```python
from src.utils.api_manager import APIManager

api = APIManager()

# LLMs
api.gemini(prompt, system_prompt=None) → str
api.claude(prompt, system_prompt=None, max_tokens=2048) → str
api.openai(prompt, system_prompt=None) → str
api.groq(prompt, system_prompt=None) → str
api.generate_text(prompt, system_prompt=None, providers=[...]) → str

# Imágenes
api.generate_image(prompt, provider="together", size="1024x1024") → str_url

# Audio
api.text_to_speech(text, provider="elevenlabs", voice_id=None) → bytes

# Utilidad
api.get_status() → dict
api.print_status() → None
```

---

## ✅ Checklist de Migración

Para cada script:

- [ ] Reemplazar `import genai` → `from src.utils.api_manager import APIManager`
- [ ] Reemplazar `genai.configure(...)` → `api = APIManager()`
- [ ] Reemplazar `client.models.generate_content()` → `api.gemini()`
- [ ] Actualizar `load_dotenv()` (ya no necesario, APIManager lo hace)
- [ ] Agregar fallback con `api.generate_text(..., providers=[...])`
- [ ] Probar que funciona: `python script.py`
- [ ] Verificar en `.env` que todas las keys están correctas

---

**Siguiente paso:** Ve a [QUICK_START.md](./QUICK_START.md) para obtener nuevas claves e integrarlas.
