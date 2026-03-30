# 🤖 Contexto Dos Aros - Claude Code

**Propósito:** Documentación para que Claude Code pueda trabajar eficientemente en el proyecto.

---

## 📍 UBICACIÓN DEL PROYECTO

```
Local (Windows):  C:\Users\rover\dosaros-data-project\
Pi (Raspberry):   /home/pi/dosaros-data-project\
BBDD:             /mnt/nba_data/dosaros_local.db
```

---

## 🏗️ ARQUITECTURA GENERAL

```
Windows (Git + Desarrollo)
    ↓
GitHub (dosaroscontact/dosaros-data-project)
    ↓
Raspberry Pi (192.168.1.136)
    ├── Bot Telegram (24/7)
    ├── Cron jobs (8:00 AM + 9:00 AM)
    └── SQLite BBDD (68 equipos + 68 prompts)
```

---

## 🎯 COMPONENTES PRINCIPALES

### 1. **Base de Datos (SQLite)**
```
/mnt/nba_data/dosaros_local.db

Tablas:
├── avatar_teams (67 registros)
│   └── Equipos con postura, vestimenta, decorado, scene_type
├── team_colors (60 equipos)
│   └── Colores primario, secundario, terciario
└── avatar_prompts (68 registros)
    └── Prompts dinámicos + URLs de avatar/logo
```

### 2. **Bot Telegram**
```
src/automation/bot_consultas.py (En vivo 24/7)

Comandos:
├── /avatar_prompt [equipo]  → Prompt específico
├── /avatar_random           → Aleatorio
├── /avatar_today            → 5 prompts
├── /video [instrucción]     → Generar video Remotion
└── [pregunta natural]       → Consultas + imagen
```

### 3. **Automatización (Cron)**
```
08:00 AM → daily_avatar_generator.py (regenera 68 prompts)
09:00 AM → master_sync.py (envía resumen del día)
```

### 4. **Assets en GitHub**
```
assets/avatars/
├── avatars_base/ (4 variantes PNG)
├── logos_base/ (2 logos PNG)
└── data/ (CSV con colores)
```

---

## 🔑 VARIABLES CRÍTICAS

### `.env` (Pi)
```
GOOGLE_CLOUD_PROJECT=dosarosproject
GOOGLE_APPLICATION_CREDENTIALS=/home/pi/credentials.json
TELEGRAM_TOKEN=8742540551:AAGXzgk5b-7MACxAoVbD6J4akGnLgm3ek3Q
LOCAL_DB=/mnt/nba_data/dosaros_local.db
GEMINI_API_KEY=AIzaSyBDx5GKa5mg...
GEMINI_MODEL=gemini-2.0-flash
```

### Rutas Críticas
```
REPO:  /home/pi/dosaros-data-project
BBDD:  /mnt/nba_data/dosaros_local.db
LOGS:  /home/pi/dosaros-data-project/logs/
```

---

## 📋 FLUJOS PRINCIPALES

### Flujo 1: Generar Prompt
```
Usuario: /avatar_prompt Lakers
    ↓
Bot consulta: SELECT FROM avatar_prompts WHERE team LIKE 'Lakers'
    ↓
Bot devuelve: Prompt + Avatar URL + Logo URL
```

### Flujo 2: Automatización Diaria
```
08:00 AM: Cron ejecuta daily_avatar_generator.py
    ↓
Script: Llama a avatar_prompt_generator.py
    ↓
avatar_prompt_generator.py: 
  1. Lee avatar_teams (67)
  2. Lee team_colors (60)
  3. Genera 68 prompts nuevos
  4. Inserta en avatar_prompts
    ↓
Notifica a Telegram: "✅ Prompts regenerados"
```

### Flujo 3: Consulta Natural
```
Usuario: "Quién fue máximo anotador NBA?"
    ↓
Bot (APIManager): Envía a Gemini
    ↓
Gemini: Traduce pregunta → SQL
    ↓
Bot: Ejecuta SQL en BBDD
    ↓
Bot: Devuelve tabla + pregunta de confirmación
    ↓
Si usuario confirma: Genera tweet + imagen automática
```

---

## 🔧 TECNOLOGÍAS USADAS

| Stack | Versión |
|-------|---------|
| Python | 3.11 |
| SQLite | 3.x |
| Telegram | python-telegram-bot |
| Google | Gemini API + Vertex AI |
| Raspberry Pi | 4B (OS 32-bit) |

---

## 📚 SCRIPTS PRINCIPALES

### `avatar_prompt_generator.py`
**Propósito:** Generar 68 prompts dinámicos  
**Entrada:** avatar_teams + team_colors  
**Salida:** avatar_prompts (68 registros)  
**Ejecución:** Manual o via cron (8:00 AM)

```bash
python avatar_prompt_generator.py
```

### `bot_consultas.py`
**Propósito:** Bot Telegram escucha y responde  
**Comandos:** 5 principales  
**Estado:** En vivo 24/7  
**Ejecución:** Via tmux en Pi

```bash
PYTHONPATH=/home/pi/dosaros-data-project python src/automation/bot_consultas.py
```

### `daily_avatar_generator.py`
**Propósito:** Wrapper que ejecuta avatar_prompt_generator + notifica  
**Ejecución:** Via cron (08:00 AM cada día)

```bash
PYTHONPATH=/home/pi/dosaros-data-project python daily_avatar_generator.py
```

### `patch_bot_avatars.py`
**Propósito:** Integra comandos avatar al bot existente  
**Ejecución:** Una sola vez (ya ejecutado)

---

## 🎨 PROMPTS Y URLS

### Template de Prompt
```
A cinematic, ultra-realistic, photorealistic full-body render.

AVATAR: Use the exact avatar from {AVATAR_URL} as the base reference. 
Maintain 100% identity consistency (face, beard, sunglasses, proportions).

POSE: {POSTURA}

OUTFIT: {VESTIMENTA}. Colors: Primary {PRIMARY_COLOR}, Secondary {SECONDARY_COLOR}, Tertiary {TERTIARY_COLOR}

SCENE: {DECORADO}. Cinematic lighting, realistic depth, warm tones.

LOGO: Include the Dos Aros logo from {LOGO_URL} naturally blended in the scene without modification.

RENDER: Ultra-realistic 3D, Pixar-quality, 8K, sharp focus, global illumination, PBR materials.

BACKGROUND: Solid chroma key green (#00FF00), perfectly uniform, no gradients.

FRAMING: Full body visible, centered, no cropping.
```

### URLs de Avatares Base
```
VARIANTE 1: https://github.com/dosaroscontact/dosaros-data-project/raw/main/assets/avatars/avatars_base/avatar_base_1_standing_casual.png
VARIANTE 2: https://github.com/dosaroscontact/dosaros-data-project/raw/main/assets/avatars/avatars_base/avatar_base_2_action_jump.png
VARIANTE 3: https://github.com/dosaroscontact/dosaros-data-project/raw/main/assets/avatars/avatars_base/avatar_base_3_upper_body.png
VARIANTE 4: https://github.com/dosaroscontact/dosaros-data-project/raw/main/assets/avatars/avatars_base/avatar_base_4_standing_gorro.png
```

### URLs de Logos
```
TRANSPARENT: https://github.com/dosaroscontact/dosaros-data-project/raw/main/assets/avatars/logos_base/logoDosAros.png
NEON AZUL:   https://github.com/dosaroscontact/dosaros-data-project/raw/main/assets/avatars/logos_base/logoLetrasAzul.png
```

---

## 📊 ESTADÍSTICAS

```
Equipos totales:     68
Equipos con colores: 60
Prompts generados:   68
Avatares base:       4 variantes
Logos:              2 tipos
Comandos Telegram:  5
Cron jobs:         2 (8:00 AM + 9:00 AM)
Estado del sistema: ✅ EN VIVO 24/7
```

---

## 🚨 PROBLEMAS COMUNES

### "ModuleNotFoundError: No module named 'src'"
**Solución:** Ejecutar con `PYTHONPATH=/home/pi/dosaros-data-project`

### Bot no responde en Telegram
**Solución:** Verificar TELEGRAM_TOKEN en .env (debe ser token largo)

### Prompts no se regeneran
**Solución:** Verificar que cron está ejecutándose:
```bash
crontab -l
grep CRON /var/log/syslog | tail -20
```

### BBDD corrupta
**Solución:** Regenrar tabla avatar_prompts:
```bash
sqlite3 /mnt/nba_data/dosaros_local.db "DROP TABLE avatar_prompts; CREATE TABLE avatar_prompts..."
```

---

## 🔄 FLUJO DE TRABAJO CON CLAUDE CODE

### Cuando necesites editar código:
1. Especifica qué archivo editar
2. Claude Code clona el repo
3. Edita el archivo
4. Hace git commit + push
5. Indica que en Pi hacer `git pull`

### Cuando necesites ejecutar algo en Pi:
1. Especifica el comando
2. Claude Code NO accede directamente a Pi
3. Debes copiar el comando y ejecutar manualmente en Pi
4. Pásale el output a Claude Code

### Cuándo necesites queries SQL:
1. Especifica la query
2. Claude Code la genera
3. Tú ejecutas en Pi:
```bash
sqlite3 /mnt/nba_data/dosaros_local.db "SELECT..."
```
4. Pasas el resultado a Claude Code

---

## 📖 DOCUMENTOS DE REFERENCIA

| Documento | Propósito |
|-----------|-----------|
| **BOT_MANUAL.md** | Guía de uso del bot para usuarios |
| **AVATAR_SYSTEM_DOCS.md** | Documentación técnica completa |
| **PROJECT_STRUCTURE.md** | Estructura de carpetas y archivos |
| **SCRIPTS_REFERENCE.md** | Referencia de todos los scripts |
| **QUICK_REFERENCE.md** | Comandos y snippets frecuentes |

---

## ✅ CHECKLIST PARA CLAUDE CODE

Antes de trabajar en cambios:

- [ ] ¿Cambio es en Windows (código) o Pi (ejecución)?
- [ ] ¿Necesito acceso a BBDD? (especificar query)
- [ ] ¿Necesito ejecutar en Pi? (proporcionar comando)
- [ ] ¿Necesito hacer commit a GitHub?
- [ ] ¿Afecta .env o variables críticas?
- [ ] ¿Hay que reiniciar bot después del cambio?

---

**Versión:** 1.0  
**Última actualización:** 2026-03-29  
**Estado:** LISTO PARA USAR CON CLAUDE CODE
