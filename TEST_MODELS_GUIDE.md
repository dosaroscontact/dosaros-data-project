# 🧪 TEST MODELS - Guía de Uso

**Ubicación:** `src/app/test_models.py`

**Propósito:** Verificar la disponibilidad y funcionalidad de todos los modelos de IA configurados en `.env`.

---

## 📋 Pre-requisitos

### 1. Archivos Requeridos

- ✅ `.env` — Archivo de configuración (con todas las API keys)
- ✅ `requirements.txt` — Dependencias Python (actualizado)

### 2. Instalar Dependencias

Ejecuta TODAS las librerías necesarias:

```bash
# Opción 1: Instalar todo (recomendado)
pip install -r requirements.txt

# Opción 2: Instalar solo lo que necesitas
pip install google-generativeai anthropic openai groq python-dotenv requests
```

**Nota:** Las librerías se importan con `try/except`, así que si falta algo, el script lo indicará.

---

## 🚀 Cómo Usar

### Ejecutar el Script

```bash
python src/app/test_models.py
```

### Menú Principal

El script mostrará un menú con 10+opciones:

```
🧪 TEST MODELS - Verificar disponibilidad de IAs
======================================================================

Elige un modelo para probar:

  1  → ⭐ Google Gemini
  2  → 🤖 OpenAI ChatGPT
  3  → 🧠 Anthropic Claude
  4  → ⚡ Groq (Llama/Mixtral)
  5  → 🔍 DeepSeek
  6  → 🌙 Kimi (Moonshot)
  7  → 🚀 X.AI Grok
  8  → 🎨 Together AI (Flux.1)
  9  → 🎤 ElevenLabs TTS
  10 → 🆓 Pollinations (FREE)

  llms → Probar todos los LLMs
  all  → Probar TODOS (LLMs + imagen + audio)
  q    → Salir
```

### Opciones de Prueba

| Opción | Descripción | Requiere API KEY |
|--------|-------------|------------------|
| **1-7** | LLMs individuales | Sí (en `.env`) |
| **8-9** | Imagen + Audio | Sí (en `.env`) |
| **10** | Pollinations FREE | No |
| **llms** | Todos los LLMs | Depende configuración |
| **all** | TODOS (LLMs + imagen + audio) | Depende configuración |
| **q** | Salir | — |

---

## 📊 Ejemplos de Uso

### Test Individual

```
Elige una opción: 1

🧪 Probando ⭐ Google Gemini...
✅ GEMINI: Hola...

Presiona ENTER para volver al menú...
```

### Test Todos los LLMs

```
Elige una opción: llms

📊 Ejecutando pruebas de LLMs...

🧪 Probando ⭐ Google Gemini...
✅ GEMINI: Hola...

🧪 Probando 🤖 OpenAI ChatGPT...
✅ OPENAI: Hola...

...

===============================================================
📊 RESUMEN DE LLMs
===============================================================
✅ GEMINI               Disponible
✅ OPENAI              Disponible
✅ CLAUDE              Disponible
❌ GROQ                No configurado
❌ DEEPSEEK            No configurado
❌ KIMI                No configurado
❌ GROK                No configurado

📈 Total: 3/7 LLMs disponibles
```

### Test TODO

```
Elige una opción: all

🔬 Ejecutando TODAS las pruebas...

[Prueba todas las APIs]

===============================================================
📊 RESUMEN DE PRUEBAS
===============================================================
✅ GEMINI                      Funcionando
✅ OPENAI                      Funcionando
✅ CLAUDE                      Funcionando
❌ GROQ                        No disponible
✅ TOGETHER                    Funcionando (no se generó imagen)
✅ ELEVENLABS                  Funcionando (no se generó audio)
✅ POLLINATIONS                Disponible (FREE)

📈 Total: 6/10 modelos disponibles
```

---

## 🔧 Configuración Requerida en `.env`

### LLMs (Obligatorio para Test)

```env
# Google Gemini
GEMINI_API_KEY=tu_clave_aqui
GEMINI_MODEL=gemini-2.0-flash

# OpenAI ChatGPT
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini

# Anthropic Claude
CLAUDE_API_KEY=sk-ant-...
CLAUDE_MODEL=claude-3-5-sonnet-latest

# Groq
GROQ_API_KEY=gsk_...
GROQ_MODEL=llama-3.3-70b-versatile

# DeepSeek (opcional)
DEEPSEEK_API_KEY=sk-...
DEEPSEEK_MODEL=deepseek-chat

# Kimi/Moonshot (opcional)
KIMI_API_KEY=sk-...
KIMI_MODEL=moonshot-v1-128k

# X.AI Grok (opcional)
GROK_API_KEY=grok-...
GROK_MODEL=grok-beta
```

### APIs de Imagen/Audio (Opcional)

```env
# Together AI (Flux.1)
TOGETHER_API_KEY=...

# ElevenLabs TTS
ELEVENLABS_API_KEY=sk_...

# Pollinations (FREE - no key)
POLLINATIONS_ENABLED=true
```

---

## ⚠️ Mensajes de Error Comunes

### ❌ "GEMINI_API_KEY no configurada"

**Solución:**
1. Abre `.env`
2. Añade: `GEMINI_API_KEY=tu_clave_aqui`
3. Guarda el archivo

### ❌ "Librería 'google-generativeai' no instalada"

**Solución:**
```bash
pip install google-generativeai
```

### ❌ "Invalid API key" o "403 Forbidden"

**Solución:**
- Verifica que la clave sea correcta
- Comprueba que NO hay espacios al inicio/final
- Rota la clave en el panel de administración de la API
- Asegúrate de que `.env` está en `.gitignore` (**IMPORTANTE SEGURIDAD**)

---

## 📝 Cómo Funciona Internamente

### Importes Inteligentes

El script importa cada librería con `try/except`:

```python
try:
    import google.generativeai as genai_lib
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
```

Si una librería no está instalada, la prueba correspondiente mostrará:
```
❌ GEMINI: Librería 'google-generativeai' no instalada (pip install google-generativeai)
```

### Funciones de Prueba

Cada modelo tiene una función `test_XXX()` que:

1. **Verifica configuración** — Comprueba si `XXX_API_KEY` está en `.env`
2. **Valida librería** — Comprueba si la librería está instalada
3. **Crea cliente** — Inicializa el cliente de la API
4. **Realiza prueba simple** — Solicitud mínima ("Di 'Hola'")
5. **Reporta resultado** — ✅ o ❌ con fragmento de respuesta

### Menú Principal

Usa un bucle infinito que:

1. Solicita opción al usuario
2. Ejecuta función correspondiente
3. Vuelve al menú (a menos que se seleccione 'q')

---

## 🎯 Casos de Uso Recomendados

### 1. Verificación Rápida (Setup Inicial)

```bash
# Opción 'all' para validar toda la configuración
Elige una opción: all
```

### 2. Debugging de API Específica

```bash
# Test individual cuando una API falla
Elige una opción: 3  # Para probar Claude
```

### 3. Monitoreo Periódico

```bash
# Ejecutar regularmente para verificar que todas las keys siguen válidas
python src/app/test_models.py
Elige una opción: llms
```

### 4. CI/CD Pipeline

```bash
# En un script automatizado
python -c "
from src.app.test_models import test_gemini, test_openai
test_gemini()
test_openai()
"
```

---

## 📚 Referencia Rápida

| Tarea | Comando |
|-------|---------|
| Ejecutar script | `python src/app/test_models.py` |
| Instalar deps | `pip install -r requirements.txt` |
| Test Gemini | `Elige opción: 1` |
| Test todos LLMs | `Elige opción: llms` |
| Test TODO | `Elige opción: all` |
| Salir | `Elige opción: q` |

---

## 🔐 Seguridad

**IMPORTANTE:**

1. ✅ **Nunca** hardcodees API keys en el código
2. ✅ **Siempre** usa `.env` (gitignored)
3. ✅ **Verifica** que `.gitignore` contiene `.env`
4. ✅ **Rota** keys si accidentalmente las commits
5. ✅ **Usa** `.env.example` como template público

---

## 📞 Soporte

Si encuentras problemas:

1. **Verifica .env** — ¿Están todas las keys?
2. **Instala reqs** — `pip install -r requirements.txt`
3. **Lee logs** — El script muestra errores detallados
4. **Prueba individual** — Test cada API por separado

---

**Última actualización:** 21 Marzo 2026

**Versión:** 2.0 (Multi-provider con menú interactivo)
