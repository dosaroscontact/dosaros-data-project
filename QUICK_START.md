# ⚡ QUICK START - Acciones Inmediatas

**Copia esta checklist y ve marcando conforme lo hagas:**

---

## FASE 0: ENTENDER LA NUEVA ARQUITECTURA (5 min)

Tu proyecto ahora soporta **10+ APIs diferentes** con fallback automático:

```
LLMs:           Gemini, Claude, OpenAI, Groq, DeepSeek, Kimi, Grok
Imágenes:       Together (Flux.1), Pollinations (FREE)
Audio:          ElevenLabs, Play.ht
Vídeo:          Luma AI, HeyGen
Datos:          NBA API, Euroliga API
```

**Clave:** No necesitas TODAS las APIs. Configura al menos una de LLMs (Gemini) y el resto es opcional.

Archivo de gestión: `src/utils/api_manager.py` (interfaz única para todas)

---

## FASE 1: GENERAR NUEVAS CLAVES (30 min)

### 🔴 CRÍTICO: Google Gemini (OBLIGATORIO)
- [ ] Ve a https://console.cloud.google.com
- [ ] Proyecto → APIs & Services → Credentials
- [ ] Elimina la ANTIGUA: `AIzaSyCk2z-nr0G1E-7xUhmipt2PFj2gTnRAm7A`
- [ ] "Create API Key" → Copia la NUEVA → Guarda en notepad
- [ ] (Opcional) Restringe a HTTP referrer para seguridad

### 🟡 Recomendado: Telegram Bot
- [ ] Abre Telegram → Busca `@BotFather`
- [ ] Escribe `/gettoken`
- [ ] Selecciona tu bot actual
- [ ] Confirma y copia el NUEVO TOKEN → Guarda en notepad
- [ ] (Alternativa: `/start` para crear un bot COMPLETAMENTE nuevo)

### 🟡 Recomendado: Supabase
- [ ] Ve a https://app.supabase.com → Selecciona proyecto
- [ ] Settings → API → Infrastructure
- [ ] Busca: `sb_publishable_e-jqYnsYmnLW_jUZ5mU7lw_UUvZ_isD`
- [ ] Click en ⚙️ → "Disable key"
- [ ] "New Key" → Copia nueva clave pública → Guarda en notepad

### 🟢 OPCIONAL: Otras APIs (elije al menos una más)

**Generación de Imágenes:**
- [ ] **Together AI (Recomendado):** https://api.together.ai/ → API Keys → Nueva clave
  - $5 crédito gratuito inicial (cientos de imágenes)
- [ ] **Pollinations (FREE):** No requiere KEY, generación ilimitada

**Análisis Rápido (LLMs alternativos):**
- [ ] **Groq:** https://console.groq.com/ → API Keys → Crear nueva
  - Especializado en velocidad (sub-segundo) para Telegram
- [ ] **Claude (Anthropic):** https://console.anthropic.com/ → API Keys → Crear nueva
  - Mejor razonamiento lógico y redacción humanizada

**Audio (Text-to-Speech):**
- [ ] **ElevenLabs:** https://elevenlabs.io/api → API Keys → Crear nueva
  - 10.000 caracteres/mes gratuito
- [ ] **Play.ht:** https://play.ht/ → API Keys → Crear nueva
  - Clonación de voz, 5.000 palabras/mes gratuito

**Vídeo/Deepseek/Kimi:**
- [ ] **DeepSeek:** https://platform.deepseek.com/ → API Keys
  - 5M tokens gratis al registrarse, genial para scripts
- [ ] **Luma AI:** https://lumalabs.ai/ → API Keys → Generate
  - 30 vídeos/mes gratuito (5s realistas)

---

## FASE 2: CREAR .env LOCAL (5 min)

### Windows (PowerShell)
```powershell
cd c:\Users\rover\dosaros-data-project

# Copia plantilla
Copy-Item .env.example .env

# Edita con tu editor favorito (VS Code):
code .env

# Paste las claves nuevas que copiaste en FASE 1
```

### Linux/Mac
```bash
cd ~/dosaros-data-project
cp .env.example .env
nano .env  # o vim .env, o abre en tu editor
# Paste las claves nuevas
```

### Contenido exacto que debe tener .env:
```
GEMINI_API_KEY=AIzaSy... (LA NUEVA de Google)
TELEGRAM_TOKEN=123456789:ABCD... (EL NUEVO de Telegram)
TELEGRAM_CHAT_ID=546297096  (Este no cambia)
SUPABASE_URL=https://bkjenzyygicqkunxvlyf.supabase.co
SUPABASE_KEY=eyJ... (LA NUEVA de Supabase)
DB_HOST=192.168.1.136
DB_PORT=5432
DB_NAME=proyecto_dos_aros
DB_USER=postgres
DB_PASSWORD=tu_password_aqui
LOCAL_DB=/mnt/nba_data/dosaros_local.db
PYTHONPATH=.
```

---

## FASE 3: VERIFICAR QUE FUNCIONA (10 min)

### Test 1: Carga de variables básicas
```bash
# Activa venv:
# Windows:
.\venv\Scripts\Activate.ps1

# Linux/Mac:
source venv/bin/activate

# Test carga:
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(f'✅ GEMINI: {bool(os.getenv(\"GEMINI_API_KEY\"))}'); print(f'✅ TELEGRAM: {bool(os.getenv(\"TELEGRAM_TOKEN\"))}'); print(f'✅ SUPABASE: {bool(os.getenv(\"SUPABASE_URL\"))}')"

# Debe mostrar: ✅ GEMINI: True, ✅ TELEGRAM: True, ✅ SUPABASE: True
```

### Test 2: API Manager Status (NUEVO - RECOMENDADO)
```bash
# Ver estado de TODAS las APIs configuradas:
python examples_api_manager.py

# Selecciona opción "1" para ver estado
# Debe mostrar tabla de ✅ y ❌ para cada API
```

### Test 3: Ejecutar ejemplos de API Manager (NUEVO)
```bash
# Ejecutar ejemplos interactivos
python examples_api_manager.py

# Prueba:
# - Opción 1: Ver estado (debe mostrar al menos Gemini ✅)
# - Opción 2: Test Gemini (genera respuesta)
# - Opción 5: Test Fallback (intenta múltiples APIs)
# - Opción 9: Caso real NBA (análisis completo)
```

### Test 4: Script de modelos Gemini
```bash
python src/app/test_models.py

# Debe mostrar lista de modelos disponibles:
# - models/gemini-2.0-flash-lite-latest
# - models/gemini-1.5-flash-latest
# - etc.
```

### Test 5: Streamlit (opcional)
```bash
streamlit run src/app/main.py

# Debe abrir en http://localhost:8501 sin errores
# Ctrl+C para cerrar
```

- [ ] Test 1 mostró 3 ✅
- [ ] Test 2 mostró tabla con APIs
- [ ] Test 3 generó respuesta exitosa
- [ ] Test 4 listó modelos sin errores
- [ ] Test 5 abrió Streamlit sin errores (o skipped)

- [ ] Test 1 mostró 3 ✅
- [ ] Test 2 listó modelos sin errores
- [ ] Test 3 abrió Streamlit sin errores (o skipped)

---

## FASE 4: SUBIR A GITHUB (5 min)

```bash
# Verifica qué va a subir (CRÍTICO):
git status
# Debe mostrar SOLO:
#   modified: .gitignore
#   new file: .env.example
#   new file: SECURITY.md
#   new file: IMPLEMENTATION_PLAN.md
#   new file: SECURIDAD_RESUMEN.md
#   new file: QUICK_START.md (este archivo)
#   modified: src/app/test_models.py
# NO debe mostrar .env

# Verifica que NO hay claves en el código:
git diff --cached | grep -i "AIzaSy\|8742540551\|sb_publishable"
# Debe retornar VACÍO (sin resultados)

# Si todo está bien:
git add .gitignore .env.example src/app/test_models.py SECURITY.md IMPLEMENTATION_PLAN.md SECURIDAD_RESUMEN.md QUICK_START.md

# Commit:
git commit -m "Security: Move secrets to .env, fix .gitignore corruption"

# Push:
git push origin main

# Verifica en GitHub.com que NO hay claves visibles
```

- [ ] git status mostró solo archivos esperados
- [ ] grep no encontró claves (vacío)
- [ ] git push ejecutado exitosamente
- [ ] GitHub mostró el commit sin claves

---

## FASE 5: EN RASPBERRY PI (Cuando tengas SSH)

```bash
# SSH a la Pi:
ssh usuario@192.168.1.136

# Navega al proyecto:
cd /ruta/a/proyecto

# Pull cambios:
git pull origin main

# Copia plantilla:
cp .env.example .env

# Edita con las MISMAS claves (las nuevas):
nano .env
# Pega las mismas claves que pusiste en tu máquina local

# Test:
python src/app/test_models.py
# Debe funcionar igual que en tu máquina

# Con esto, tus cron jobs ahora serán seguros:
# La clave está en .env (gitignored), no en código hardcodeado
```

- [ ] SSH a Pi exitoso
- [ ] git pull exitoso
- [ ] .env copiado en Pi
- [ ] .env editado con nuevas claves
- [ ] test_models.py funciona en Pi

---

## FASE 6: VALIDACIÓN FINAL

- [ ] Tu máquina: streamlit run src/app/main.py → Funciona ✅
- [ ] Tu máquina: python src/app/test_models.py → Funciona ✅
- [ ] GitHub: No hay .env trackeado
- [ ] GitHub: No hay claves visibles en commits
- [ ] GitHub: .env.example existe (plantilla)
- [ ] GitHub: .gitignore contiene .env como primera línea
- [ ] Pi: .env existe local con nuevas claves
- [ ] Pi: test_models.py funciona

---

## 🎯 TIEMPO ESTIMADO TOTAL

- Fase 1 (nuevas claves): **15 minutos**
- Fase 2 (crear .env): **5 minutos**
- Fase 3 (verificar): **5 minutos**
- Fase 4 (GitHub): **5 minutos**
- Fase 5 (Pi): **10 minutos**
- **TOTAL: ~40 minutos**

---

## 🆘 SI ALGO FALLA

### "API_KEY not configured"
```bash
# Verifica que .env existe:
ls .env

# Verifica contenido:
grep GEMINI_API_KEY .env

# Recarga Streamlit (Ctrl+R en navegador)
```

### "Error loading .env"
```bash
# Verifica encoding:
file .env
# Debe mostrar: UTF-8, no UTF-16

# Si está corrupto, regenera:
rm .env
cp .env.example .env
# Re-edita con VS Code (guardar como UTF-8)
```

### ".env todavía aparece en git"
```bash
# Remover del histórico:
git rm --cached .env
git commit -m "Remove .env from git (now gitignored)"
git push
```

---

## ✅ CUANDO TERMINES

Tu proyecto estará:
- ✅ Cubierto con `.gitignore` seguro
- ✅ Sin claves hardcodeadas en código
- ✅ Con configuración en variables de entorno
- ✅ Con documentación de seguridad
- ✅ Listo para público sin riesgos

**¡Felicidades! Tu proyecto es ahora seguro.** 🎉

---

*Tiempo: ~40 minutos | Dificultad: 🟢 FÁCIL | Prioridad: 🔴 CRÍTICA*
