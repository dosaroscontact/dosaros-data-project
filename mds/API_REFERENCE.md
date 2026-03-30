# 🎯 REFERENCIA RÁPIDA - API Manager + Configuración

**Última actualización:** 22 de Marzo 2026  
**Propósito:** Guía rápida para trabajar con la nueva arquitectura de APIs

---

## 📂 Archivos Principales

```
.env                          ← TUS CLAVES LOCALES (NO COMMITES)
.env.example                  ← PLANTILLA (en Git, públicamente visible)
src/utils/api_manager.py      ← GESTOR CENTRALIZADO DE APIs
examples_api_manager.py       ← EJEMPLOS EJECUTABLES
API_INTEGRATION.md            ← GUÍA DE INTEGRACIÓN COMPLETA
```

---

## ⚡ Inicio Rápido (3 pasos)

### 1️⃣ Configurar .env
```bash
cp .env.example .env
# Editar .env y llenar con tus claves (al menos GEMINI_API_KEY)
```

### 2️⃣ Probar que funciona
```bash
python examples_api_manager.py
# Seleccionar opción "1" para ver estado de APIs
```

### 3️⃣ Usar en tu código
```python
from src.utils.api_manager import APIManager

api = APIManager()
response = api.gemini("Tu pregunta aquí")
```

---

## 🔌 API Manager - Métodos Principales

### LLMs - Generar Texto

```python
from src.utils.api_manager import APIManager
api = APIManager()

# Opción 1: Usar proveedor específico
response = api.gemini("¿Quién ganó la NBA en 2020?")
response = api.claude("Analiza estos datos...")
response = api.openai("Genera JSON con...")
response = api.groq("Responde rápidamente...")

# Opción 2: Usar con fallback automático (RECOMENDADO)
response = api.generate_text(
    prompt="Tu pregunta",
    system_prompt="Contexto adicional (opcional)",
    providers=['gemini', 'claude', 'groq']  # Orden de preferencia
)
```

### Imágenes

```python
# Together AI (mejor calidad)
image_url = api.generate_image(
    prompt="Cartel de Instagram con...",
    provider="together"
)

# Pollinations (gratis, sin KEY)
image_url = api.generate_image(
    prompt="Jugador de NBA...",
    provider="pollinations"
)
```

### Audio (Text-to-Speech)

```python
audio_bytes = api.text_to_speech(
    text="Cuéntame sobre el partido...",
    provider="elevenlabs"
)

# Guardar a archivo
with open("output.mp3", "wb") as f:
    f.write(audio_bytes)
```

### Estado de APIs

```python
# Ver qué está configurado
status = api.get_status()  # Retorna dict con True/False

# Imprimir tabla formateada
api.print_status()

# Ejemplo output:
# LLMs:
#   ✅ GEMINI      Configurado
#   ❌ CLAUDE      NO configurado
#   ✅ GROQ        Configurado
```

---

## 📋 Configuración .env

### Secciones principales

```
# Bases de datos
LOCAL_DB=/mnt/nba_data/dosaros_local.db
DB_HOST=192.168.1.136
SUPABASE_KEY=sb_...

# LLMs (al menos uno OBLIGATORIO)
GEMINI_API_KEY=AIzaSy...
CLAUDE_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-proj-...
GROQ_API_KEY=gsk_...

# Imágenes
TOGETHER_API_KEY=...        # Recomendado
POLLINATIONS_ENABLED=true   # Gratis (no KEY)

# Audio
ELEVENLABS_API_KEY=...
PLAYHT_API_KEY=...

# Comunicación
TELEGRAM_TOKEN=123456:ABC...
TELEGRAM_CHAT_ID=987654321
```

**Ver .env.example para lista completa**

---

## 🚀 Ejemplos de Uso Comunes

### Caso 1: Generar análisis NBA

```python
from src.utils.api_manager import APIManager

api = APIManager()

system = "Eres experto en NBA con experiencia en análisis de datos."
prompt = "¿Cuáles son los 5 mejores tiradores de 3P del 2026?"

respuesta = api.generate_text(
    prompt=prompt,
    system_prompt=system,
    providers=['gemini', 'claude']  # Intenta Gemini, fallback a Claude
)

print(respuesta)
```

### Caso 2: Integrar en Streamlit

```python
# src/app/main.py
import streamlit as st
from src.utils.api_manager import APIManager

api = APIManager()

st.set_page_config(page_title="Dos Aros", layout="wide")

pregunta = st.text_input("Haz una pregunta sobre NBA:")

if pregunta:
    respuesta = api.generate_text(
        prompt=pregunta,
        system_prompt="Eres analista NBA.",
        providers=['gemini', 'claude', 'groq']
    )
    st.write(respuesta)
```

### Caso 3: Generar imagen para post

```python
from src.utils.api_manager import APIManager

api = APIManager()

prompt = """
Cartel profesional 1024x1024 para Instagram:
- Tema: Top 3 cazadores de 3-pointers NBA 2026
- Colores: Mint (#88D4AB) y Coral (#FF8787)
- Estilo: Moderno, fuente legible, efecto deportivo
- Logo de "Dos Aros" en la esquina
"""

image_url = api.generate_image(
    prompt=prompt,
    provider="together",
    size="1024x1024"
)

print(f"✅ Imagen: {image_url}")
```

### Caso 4: Usar con fallback inteligente

```python
from src.utils.api_manager import APIManager

api = APIManager()
status = api.get_status()

# Construir lista de proveedores disponibles
providers = []
if status['gemini']:
    providers.append('gemini')
if status['claude']:
    providers.append('claude')
if status['groq']:
    providers.append('groq')

if not providers:
    raise ValueError("❌ Ningún LLM configurado")

# Usar cualquier disponible (fallback automático)
response = api.generate_text(
    prompt="...",
    providers=providers
)
```

---

## 📊 Migrando Scripts Existentes

### Patrón: Antes vs Después

```python
# ❌ ANTES (duplicado y propenso a errores)
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY)

response = client.models.generate_content("...")

# ✅ DESPUÉS (centralizadrá y robust)
from src.utils.api_manager import APIManager

api = APIManager()
response = api.gemini("...")

# O con fallback:
response = api.generate_text("...", providers=['gemini', 'claude'])
```

---

## 🎮 Ejecutar Ejemplos Interactivos

```bash
# Terminal
python examples_api_manager.py

# Menú:
# 1 - Ver estado de APIs
# 2 - Test Gemini
# 3 - Test Claude
# 4 - Test Groq (rápido)
# 5 - Test con Fallback
# 6 - Generar imagen (Together)
# 7 - Generar imagen FREE (Pollinations)
# 8 - Generar audio (ElevenLabs)
# 9 - Caso real: NBA Analyzer
# 10 - Manejo de errores
```

---

## 🔧 Troubleshooting Rápido

### Error: "ModuleNotFoundError: No module named 'src.utils.api_manager'"

```python
# Solución: Añadir path al proyecto
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from src.utils.api_manager import APIManager
```

### Error: "GEMINI_API_KEY no configurada"

```bash
# Checklist:
1. ¿Existe .env en la raíz?
   ls -la .env
   
2. ¿Contiene GEMINI_API_KEY?
   grep GEMINI_API_KEY .env
   
3. ¿Es UTF-8 (no UTF-16)?
   file .env
   
4. ¿Venv está activado?
   python -c "import sys; print(sys.executable)"
```

### Error: "Ningún proveedor disponible"

```python
# Solución: Verificar status
api = APIManager()
api.print_status()

# Si ves ❌ en todos, significa que .env no está cargando

# Alternativa: usar fallback
response = api.generate_text("...", providers=['gemini'])
# Si falla, intenta manualmente:
response = api.groq("...")  # Groq puede ser más flexible
```

---

## 📚 Documentación Completa

| Documento | Propósito |
|-----------|-----------|
| [API_INTEGRATION.md](./API_INTEGRATION.md) | Guía completa de integración |
| [SECURITY.md](./SECURITY.md) | Seguridad y configuración |
| [QUICK_START.md](./QUICK_START.md) | Setup inicial paso a paso |
| [.env.example](./.env.example) | Plantilla de configuración |
| [examples_api_manager.py](./examples_api_manager.py) | Ejemplos ejecutables |

---

## 🗺️ Roadmap de Uso

```
1️⃣ Copiar .env.example → .env
   └─ Llenar con tus claves (al menos GEMINI_API_KEY)

2️⃣ Ejecutar examples_api_manager.py
   └─ Ver estado con opción "1"

3️⃣ Integrar en tus scripts
   └─ from src.utils.api_manager import APIManager
   └─ api = APIManager()
   └─ api.generate_text("...")

4️⃣ Usar fallback automático
   └─ api.generate_text(..., providers=['gemini', 'claude', 'groq'])

5️⃣ Migrar scripts existentes
   └─ Reemplazar genai → APIManager
```

---

## 💡 Tips y Trucos

### Tip 1: Comprobar rápidamente qué funciona
```python
api = APIManager()
api.print_status()
```

### Tip 2: Usar el proveedor más rápido para Telegram
```python
# Groq es sub-segundo, perfecto para bots
response = api.groq("Responde rápidamente: ¿quién...?")
```

### Tip 3: Usar provider específico si uno no está disponible
```python
try:
    response = api.gemini(prompt)
except:
    response = api.claude(prompt)  # Fallback manual
```

### Tip 4: Imágenes gratis sin KEY
```python
# Pollinations no requiere KEY registrada
image_url = api.generate_image(prompt="...", provider="pollinations")
```

### Tip 5: Cachear el API Manager (evitar reinicializaciones)
```python
# ❌ INEFICIENTE: Reinicializa en cada llamada
for _ in range(100):
    api = APIManager()  # Caro

# ✅ EFICIENTE: Crear una sola vez
api = APIManager()
for _ in range(100):
    response = api.gemini("...")  # Rápido
```

---

**Siguiente paso:** Lee [API_INTEGRATION.md](./API_INTEGRATION.md) para integración avanzada.
