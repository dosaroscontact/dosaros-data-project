# 🔒 GUÍA DE SEGURIDAD - Proyecto Dos Aros

## SITUACIÓN CRÍTICA (22 de Marzo 2026)

Tu clave de Gemini API fue **bloqueada por Google** porque:
1. ✗ Estaba **hardcodeada en el código** (`src/app/test_models.py`)
2. ✗ El archivo `.env` **estaba siendo trackeado en Git**
3. ✗ GitHub descartuló los repositorios públicos y Google detectó las claves

---

## ✅ SOLUCIÓN IMPLEMENTADA

### 1. **Correcciones Realizadas**

- ✅ `.gitignore` reconstruido (estaba corrompido en UTF-16)
- ✅ `.env.example` creado como plantilla
- ✅ `src/app/test_models.py` actualizado (usa .env ahora)
- ✅ Claves hardcodeadas removidas del código

### 2. **Próximos Pasos (INMEDIATOS)**

#### A. Cambiar TODAS tus claves (OBLIGATORIO)

Google y otros servicios ya vieron estas claves en Git:

```
OLD KEYS (INVALIDAR):
- GEMINI_API_KEY: AIzaSyCk2z-nr0G1E-7xUhmipt2PFj2gTnRAm7A
- TELEGRAM_TOKEN: 8742540551:AAGXzgk5b-7MACxAoVbD6J4akGnLgm3ek3Q
- SUPABASE_KEY: sb_publishable_e-jqYnsYmnLW_jUZ5mU7lw_UUvZ_isD
```

**Debes:**
1. Ve a [Google Cloud Console](https://console.cloud.google.com)
   - Elimina la clave antigua
   - Genera una NUEVA clave de Gemini API
2. Ve a [Telegram BotFather](https://t.me/botfather)
   - Solicita un nuevo token para tu bot
3. Ve a [Supabase Dashboard](https://app.supabase.com)
   - Regenera la clave de API

---

## 📋 CONFIGURACIÓN CORRECTA

### Paso 1: Crear `.env` local (NO commitear)

```bash
# En la raíz del proyecto, copia:
cp .env.example .env

# Luego edita .env con TUS NUEVAS CLAVES:
GEMINI_API_KEY=AIzaSy... (NUEVA)
TELEGRAM_TOKEN=123456... (NUEVA)
SUPABASE_KEY=sb_... (NUEVA)
```

### Paso 2: Verificar `.gitignore`

Ejecuta en terminal:
```bash
# Verifica que .env está ignorado:
git status | grep .env
# Debe estar VACÍO (no debe mostrar .env)

# Verifica que el .gitignore es correcto:
cat .gitignore | head -3
# Debe mostrar:
# Configuración y secretos (CRÍTICO)
# .env
```

### Paso 3: Test de Carga

```bash
# Verifica que tus variables se cargan correctamente:
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(f'API Key cargada: {bool(os.getenv(\"GEMINI_API_KEY\"))}')"
# Debe mostrar: API Key cargada: True
```

---

## 🚨 CHECKLIST DE SEGURIDAD

- [ ] Nuevas claves generadas en Google, Telegram, Supabase
- [ ] `.env` creado en la raíz (no commiteado)
- [ ] `.gitignore` contiene `.env` como primera línea
- [ ] `git status` no muestra `.env`
- [ ] `src/app/test_models.py` usa `os.getenv("GEMINI_API_KEY")`
- [ ] Correr `python src/app/test_models.py` sin errores
- [ ] Streamlit abre sin "API_KEY not configured"

---

## 📝 ARQUITECURA DE SECRETOS CORRECTA

```
proyecto-dos-aros/
├── .env              ← TUS CLAVES (LOCAL, NO EN GIT)
├── .env.example      ← PLANTILLA (PÚBLICA, EN GIT)
├── .gitignore        ← IGNORA .env (CRÍTICO)
├── src/
│   ├── app/
│   │   ├── main.py       → load_dotenv() + os.getenv("GEMINI_API_KEY")
│   │   └── test_models.py → load_dotenv() + os.getenv("GEMINI_API_KEY")
│   ├── processors/
│   │   └── gemini_social.py → load_dotenv() + os.getenv("GEMINI_API_KEY")
│   └── database/
│       └── supabase_client.py → load_dotenv() + os.getenv("SUPABASE_KEY")
└── automation/
    └── bot_manager.py → load_dotenv() + os.getenv("TELEGRAM_TOKEN")
```

---

## 🔐 REGLAS DE ORO

### 1. **NUNCA hardcodear claves**
```python
# ❌ NUNCA:
api_key = "AIzaSyXXXXXXX"

# ✅ SIEMPRE:
from dotenv import load_dotenv
import os
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
```

### 2. **NUNCA commiter .env**
```bash
# .gitignore DEBE contener:
.env
.env.local
.env.*.local
secrets/
*.key
```

### 3. **SIEMPRE revisar antes de push**
```bash
# Antes de cualquier push, verifica:
git diff --cached | grep -i "api\|key\|token\|secret"
# Debe retornar VACÍO
```

### 4. **SIEMPRE usar .env.example como referencia**
```bash
# Mantén .env.example actualizado cuando agregues variables:
# .env.example → tiene placeholders
# .env → tiene valores reales (gitignored)
```

---

## 🛠️ ARCHIVOS AUDITADOS Y CORREGIDOS

| Archivo | Problema | Solución |
|---------|----------|----------|
| `src/app/test_models.py` | Clave hardcodeada | ✅ Usa `os.getenv("GEMINI_API_KEY")` |
| `src/app/main.py` | Ya usaba `.env` | ✅ Sin cambios necesarios |
| `src/app/analista_ia.py` | Ya usaba `.env` | ✅ Sin cambios necesarios |
| `src/processors/gemini_social.py` | Usa `.env` | ✅ Sin cambios necesarios |
| `.gitignore` | UTF-16 corrompido | ✅ Reconstruido en UTF-8 |
| `.env` | Trackeado en Git | ⚠️ Debes eliminar histórico (ver abajo) |

---

## 🧹 ELIMINAR CLAVES DEL HISTÓRICO GIT (Importante)

Si el repositorio es **público**, Google ya vio tus claves. Debes limpiar el histórico:

```bash
# Opción 1: Si tienes pocos commits (RECOMENDADO)
# 1. Crea rama nueva:
git checkout -b clean-secrets

# 2. Revert el .env a .env.example:
git rm --cached .env
git commit --amend -m "Secretos movidos a .env (gitignored)"

# 3. Force push (cuidado: reescribe historia):
git push origin main --force

# Opción 2: Si tienes muchos commits
# Usa BFG Repo-Cleaner (herramienta especializada)
```

**IMPORTANTE:** Después de limpiar el histórico, **TODAS** tus claves siguen siendo de riesgo porque estuvieron públicas. Deberás rotarlas ahora en Google Cloud, Telegram, Supabase.

---

## 📞 CONTACTOS PARA ROTACIÓN DE CLAVES

| Servicio | URL | Acción |
|----------|-----|--------|
| **Google Cloud** | https://console.cloud.google.com | Revocar vieja, crear nueva Gemini API key |
| **Telegram BotFather** | @botfather en Telegram | `/gettoken` para nuevo token |
| **Supabase** | https://app.supabase.com | Project Settings → API Keys → disable old, create new |

---

## 📚 REFERENCIAS

- [Google Cloud: API Key Security](https://cloud.google.com/docs/authentication/api-keys#api_key_best_practices)
- [OWASP: Secrets Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [Python dotenv Documentation](https://python-dotenv.readthedocs.io/)
- [GitHub Secret Scanning](https://docs.github.com/en/code-security/secret-scanning)

---

**Fecha de actualización:** 22 de Marzo 2026  
**Prioridad:** 🔴 CRÍTICA — Implementar inmediatamente
