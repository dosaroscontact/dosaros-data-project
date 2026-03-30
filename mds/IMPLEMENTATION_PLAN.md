# ✅ PLAN DE IMPLEMENTACIÓN - Securización del Proyecto

**Fecha:** 22 de Marzo 2026  
**Estado:** Implementación en `Dos Aros`  
**Prioridad:** 🔴 CRÍTICA

---

## 1️⃣ ARCHIVOS MODIFICADOS

### Archivos Actualizados ✅

| Archivo | Cambio | Impacto |
|---------|--------|--------|
| `.gitignore` | Reconstruido en UTF-8, ahora ignora `.env` | **CRÍTICO** |
| `.env.example` | Creado (plantilla pública) | Documenta variables necesarias |
| `src/app/test_models.py` | Ahora usa `os.getenv("GEMINI_API_KEY")` | Elimina clave hardcodeada |

### Archivos Sin Cambios (ya seguros) ✅

| Archivo | Estado | Razón |
|---------|--------|-------|
| `src/app/main.py` | ✅ Seguro | Ya usa `load_dotenv()` y `os.getenv()` |
| `src/app/analista_ia.py` | ✅ Seguro | Ya usa `load_dotenv()` y `os.getenv()` |
| `src/processors/gemini_social.py` | ✅ Seguro | Ya usa `load_dotenv()` y `os.getenv()` |
| `src/database/supabase_client.py` | ✅ Seguro | Ya usa `load_dotenv()` y `os.environ.get()` |
| `automation/config.py` | ✅ Seguro | Ya usa `load_dotenv()` y `os.getenv()` |
| `automation/bot_manager.py` | ✅ Seguro | Importa desde `config.py` que usa `.env` |

---

## 2️⃣ PASOS A EJECUTAR (EN ORDEN)

### Paso 1: Generar Nuevas Claves (OBLIGATORIO)

Las claves antiguas estaban en Git público, deben ser rotadas **AHORA**:

#### Google Gemini
1. Ve a https://console.cloud.google.com
2. Selecciona tu proyecto
3. APIs & Services → Credentials
4. Elimina la clave antigua: `AIzaSyCk2z-nr0G1E-7xUhmipt2PFj2gTnRAm7A`
5. Click "Create Credentials" → "API Key" → Copia la NUEVA
6. (Opcional) Restringe por referrer HTTP o IP

#### Telegram Bot
1. Abre Telegram y busca `@BotFather`
2. `/gettoken` para tu bot actual
3. Confirma y copia el NUEVO token
4. (Recomendado) `/start` para crear un bot completamente nuevo

#### Supabase (si se usa)
1. Ve a https://app.supabase.com → Tu Proyecto
2. Settings → API → Infrastructure
3. Desactiva la clave antigua: `sb_publishable_e-jqYnsYmnLW_jUZ5mU7lw_UUvZ_isD`
4. Genera nueva clave pública (`anon`) y privada (`service_role`)

---

### Paso 2: Crear `.env` Local (EN TU MÁQUINA)

```bash
# Desde la raíz del proyecto:
# Windows (PowerShell):
Copy-Item .env.example .env

# Linux/Mac:
cp .env.example .env

# Luego edita .env con tus NUEVAS claves:
```

**Contenido de `.env`:**
```
# Google Gemini API (NUEVA CLAVE)
GEMINI_API_KEY=AIzaSy... (copiar de Google Cloud)

# Telegram Bot (NUEVO TOKEN)
TELEGRAM_TOKEN=123456789:ABCD... (copiar de BotFather)
TELEGRAM_CHAT_ID=546297096

# Supabase (NUEVA CLAVE)
SUPABASE_URL=https://bkjenzyygicqkunxvlyf.supabase.co
SUPABASE_KEY=eyJ... (NUEVA, de Supabase)

# PostgreSQL Pi (si aplica)
DB_HOST=192.168.1.136
DB_PORT=5432
DB_NAME=proyecto_dos_aros
DB_USER=postgres
DB_PASSWORD=tu_password_aqui

# Rutas locales
LOCAL_DB=/mnt/nba_data/dosaros_local.db
PYTHONPATH=.
```

**⚠️ IMPORTANTE:** NO COMMITES ESTE ARCHIVO

---

### Paso 3: Verificar `.gitignore` y Git

Ejecuta en terminal:

```bash
# Verifica que .gitignore está bien:
head -5 .gitignore
# Debe mostrar:
# Configuración y secretos (CRÍTICO)
# .env
# .env.local

# Verifica que .env no está trackeado:
git status
# No debe mostrar .env en "Changes not staged"

# Si .env está en git, removerlo:
git rm --cached .env
git commit -m "Remove .env from git (now in .gitignore)"

# Verifica cambios sin claves:
git diff --cached | grep -i "AIzaSy\|8742540551\|sb_publishable"
# Debe retornar VACÍO (sin claves)
```

---

### Paso 4: Test de Configuración

```bash
# Activa tu entorno virtual:
# Windows:
.\venv\Scripts\Activate.ps1

# Linux/Mac:
source venv/bin/activate

# Test 1: Verifica que .env se carga:
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(f'✅ GEMINI: {bool(os.getenv(\"GEMINI_API_KEY\"))}'); print(f'✅ TELEGRAM: {bool(os.getenv(\"TELEGRAM_TOKEN\"))}'); print(f'✅ SUPABASE: {bool(os.getenv(\"SUPABASE_URL\"))}')"

# Debe mostrar:
# ✅ GEMINI: True
# ✅ TELEGRAM: True
# ✅ SUPABASE: True

# Test 2: Corre el script de modelos Gemini:
python src/app/test_models.py
# Debe mostrar lista de modelos disponibles sin errores

# Test 3: Corre Streamlit (si quieres)
streamlit run src/app/main.py
# Debe abrir sin errores de API_KEY
```

---

### Paso 5: Subir a Git (SEGURO)

```bash
# Estadio 1: Prepara cambios
git add .gitignore .env.example src/app/test_models.py SECURITY.md IMPLEMENTATION_PLAN.md

# Verifica qué va a subir:
git diff --cached | grep -i "api\|key\|token\|secret"
# Debe retornar VACÍO (sin claves)

# Estadio 2: Commit
git commit -m "Security: Move secrets to .env, fix .gitignore, update test_models.py"

# Estadio 3: Push
git push origin main

# Verifica en GitHub que:
# ✅ .env.example se subió (con placeholders, sin valores)
# ✅ .gitignore existe y contiene .env
# ✅ test_models.py usa os.getenv, no claves hardcodeadas
```

---

### Paso 6: En Raspberry Pi (si aplica)

```bash
# SSH a la Pi:
ssh usuario@192.168.1.136

# Navega al proyecto:
cd /ruta/a/dosaros-data-project

# Git pull:
git pull origin main

# Copia .env.example a .env (en la Pi):
cp .env.example .env

# Edita .env con tus claves (en la Pi):
nano .env
# Pega las MISMAS claves que pusiste en tu máquina local

# Test:
python src/app/test_models.py
# Debe funcionar sin errores

# Configura tu backup automatizado (cron):
# La clave de Gemini estará ahora en .env (gitignored), no en código
```

---

## 3️⃣ VERIFICACIÓN FINAL

Antes de considerar esto completado, verifica:

- [ ] **Claves rotadas:** Nuevas claves en Google, Telegram, Supabase generadas
- [ ] **`.env` creado:** Local en tu máquina con nuevas claves
- [ ] **`.env` no en Git:** `git status` no muestra `.env`
- [ ] **`.gitignore` correcto:** Primera línea es `# Configuración y secretos`
- [ ] **`test_models.py` corregido:** Usa `os.getenv("GEMINI_API_KEY")`
- [ ] **Tests pasan:** `python src/app/test_models.py` funciona
- [ ] **Streamlit corre:** `streamlit run src/app/main.py` sin errores
- [ ] **Git push limpio:** `git diff --cached` sin claves
- [ ] **Pi sincronizada:** `.env` existe en Pi con claves correctas
- [ ] **Documentación:** `SECURITY.md` creado y commiteado

---

## 4️⃣ REFERENCIA DE ARCHIVOS

### Estructura Post-Securización

```
c:\Users\rover\dosaros-data-project\
├── .env                  ← LOCAL (NO EN GIT)
├── .env.example          ← PLANTILLA (EN GIT) ✅
├── .gitignore            ← IGNORA .env (EN GIT) ✅
├── SECURITY.md           ← GUÍA DE SEGURIDAD (EN GIT) ✅
├── IMPLEMENTATION_PLAN.md ← ESTE ARCHIVO (EN GIT) ✅
│
├── src/
│   ├── app/
│   │   ├── main.py                  ✅ load_dotenv()
│   │   ├── test_models.py           ✅ CORREGIDO
│   │   ├── analista_ia.py           ✅ load_dotenv()
│   │   └── ...
│   │
│   ├── processors/
│   │   └── gemini_social.py         ✅ load_dotenv()
│   │
│   ├── database/
│   │   └── supabase_client.py       ✅ load_dotenv()
│   │
│   └── utils/
│       └── mapper.py                ✅ NO necesita claves
│
├── automation/
│   ├── config.py                    ✅ load_dotenv()
│   ├── bot_manager.py               ✅ Importa de config.py
│   └── ...
│
└── requirements.txt                  ✅ Ya contiene python-dotenv
```

---

## 5️⃣ TROUBLESHOOTING

### Problema: `API_KEY not configured` en Streamlit

**Solución:**
```bash
# Verifica .env existe:
ls -la .env  # o en Windows: dir .env

# Verifica que GEMINI_API_KEY está en .env:
grep GEMINI_API_KEY .env

# Verifica que .venv está activado:
python -c "import sys; print(sys.executable)"
# Debe mostrar ruta dentro de venv/

# Recarga Streamlit (Ctrl+R en browser)
```

---

### Problema: `Error loading .env` en test

**Solución:**
```bash
# Verifica que python-dotenv está instalado:
pip install python-dotenv

# Verifica encoding de .env:
file .env
# Debe mostrar: UTF-8 Unicode, no UTF-16

# Si está corrupto, regenera:
cp .env.example .env
# Edita con VS Code (asegúrate encoding UTF-8)
```

---

### Problema: Claves aún visibles en GitHub

**Solución (requiere admin permisos):**
```bash
# USA BFG Repo-Cleaner (herramienta especializada)
# https://rtyley.github.io/bfg-repo-cleaner/

# 1. Descarga bfg.jar
# 2. Copia tu repo a una carpeta temporal
# 3. Ejecuta:
bfg --replace-text passwords.txt my-repo.git

# 4. Force push:
git push --force
```

---

## 6️⃣ PRÓXIMAS ACCIONES

1. **Monitoreo:** Configura GitHub Secret Scanning activado
2. **Educación:** Haz que todo el equipo entienda `.env` security
3. **Automatización:** Considera usar `dotenv-vault` para encriptar `.env`
4. **CI/CD:** Si tienes GitHub Actions, asegúrate que NO logea `GEMINI_API_KEY`

---

**Última actualización:** 22 de Marzo 2026  
**Estado:** Implementación completada ✅  
**Próximo review:** Semana del 29 de Marzo
