# 📁 Estructura del Proyecto - Dos Aros

---

## 🌳 ÁRBOL COMPLETO

```
dosaros-data-project/
│
├── 📄 README.md                          ← Inicio del proyecto
├── 📄 .env                               ← Variables de entorno (SENSIBLE)
├── 📄 .env.example                       ← Template de .env
├── 📄 .gitignore                         ← Archivos ignorados en Git
├── 📄 requirements.txt                   ← Dependencias Python
│
├── 🐍 SCRIPTS PRINCIPALES
│   ├── avatar_prompt_generator.py        ← Genera 68 prompts dinámicos
│   ├── daily_avatar_generator.py         ← Wrapper diario (cron 8:00 AM)
│   ├── patch_bot_avatars.py              ← Integra avatares en bot
│   ├── export_project.py                 ← Empaqueta proyecto en ZIP
│   ├── master_sync.py                    ← Sincronización diaria (cron 9:00 AM)
│   ├── main.py                           ← Punto de entrada principal
│   └── test_bot.py                       ← Tests del bot
│
├── 📂 src/                               ← Código fuente
│   ├── automation/
│   │   ├── bot_consultas.py              ← 🤖 BOT TELEGRAM (EN VIVO)
│   │   ├── bot_manager.py                ← Gestor de Telegram
│   │   ├── config.py                     ← Configuración global
│   │   └── task_scheduler.py             ← Scheduler de tareas
│   │
│   ├── utils/
│   │   ├── api_manager.py                ← Gestor de APIs (Gemini, Groq)
│   │   ├── database.py                   ← Funciones de BBDD
│   │   └── validators.py                 ← Validación de datos
│   │
│   ├── processors/
│   │   ├── image_generator.py            ← Generador de imágenes (Pillow)
│   │   ├── video_generator.py            ← Generador de videos (Remotion)
│   │   └── data_processor.py             ← Procesamiento de datos
│   │
│   └── integrations/
│       ├── telegram_client.py            ← Cliente Telegram
│       ├── google_cloud_client.py        ← Cliente Google Cloud
│       └── github_client.py              ← Cliente GitHub
│
├── 📂 assets/                            ← Recursos multimedia
│   ├── avatars/
│   │   ├── avatars_base/                 ← 4 PNG bases del avatar
│   │   │   ├── avatar_base_1_standing_casual.png
│   │   │   ├── avatar_base_2_action_jump.png
│   │   │   ├── avatar_base_3_upper_body.png
│   │   │   └── avatar_base_4_standing_gorro.png
│   │   ├── logos_base/                   ← 2 logos PNG
│   │   │   ├── logoDosAros.png
│   │   │   └── logoLetrasAzul.png
│   │   ├── generated/                    ← Imágenes generadas (OUTPUT)
│   │   │   └── NBA/
│   │   ├── posts/                        ← Posts generados
│   │   ├── presenter/                    ← Presenter assets
│   │   └── prompts/                      ← Prompts exportados (TXT + CSV)
│   │
│   └── data/
│       ├── team_colors.csv               ← Documento original (desordenado)
│       ├── team_colors_clean.csv         ← CSV limpio (60 equipos)
│       └── team_colors_structure.json    ← Estructura JSON
│
├── 📂 docs/                              ← Documentación
│   ├── README.md                         ← Inicio documentación
│   ├── AVATAR_SYSTEM_DOCS.md             ← 📖 Docs completas del sistema avatar
│   ├── AVATAR_BIBLE.md                   ← Especificaciones del avatar
│   ├── BOT_MANUAL.md                     ← 📖 Manual de uso del bot
│   ├── API_REFERENCE.md                  ← Referencia de APIs
│   ├── IMPLEMENTATION_PLAN.md            ← Plan de implementación
│   ├── IMPLEMENTATION_SUMMARY.md         ← Resumen de implementación
│   ├── IMPLEMENTATION_DOCS.md            ← Docs de implementación
│   ├── SECURITY.md                       ← Políticas de seguridad
│   ├── CHANGELOG_v3.0.md                 ← Cambios en v3.0
│   └── QUICK_START.md                    ← Guía rápida
│
├── 📂 logs/                              ← Logs del sistema
│   ├── cron_output.log                   ← Log master_sync.py
│   ├── cron_daily_avatar.log             ← Log daily_avatar_generator.py
│   ├── avatar_generation.log             ← Log de generación
│   └── bot_errors.log                    ← Errores del bot
│
├── 📂 tests/                             ← Tests automáticos
│   ├── test_avatar_generator.py
│   ├── test_bot_commands.py
│   └── test_database.py
│
├── 📂 .github/                           ← GitHub workflows
│   ├── workflows/
│   │   └── ci.yml                        ← CI/CD pipeline
│   └── copilot-instructions.md           ← Instrucciones para Copilot
│
├── 📂 venv/                              ← Virtual environment (NO TOCAR)
│   └── ...
│
└── 📂 project_export/                    ← Backup exportado
    └── dos_aros_project_20260329_*.zip   ← ZIP del proyecto
```

---

## 📊 RELACIONES DE ARCHIVOS CLAVE

```
avatar_prompt_generator.py
    ↓ (lee de BBDD)
avatar_teams + team_colors
    ↓ (genera)
avatar_prompts (68 registros)
    ↓ (usa)
bot_consultas.py (responde /avatar_prompt, /avatar_random, /avatar_today)

---

daily_avatar_generator.py
    ↓ (ejecuta)
avatar_prompt_generator.py
    ↓ (notifica)
bot_manager.py
    ↓ (envía a)
Telegram

---

bot_consultas.py
    ↓ (importa)
APIManager → Gemini/Groq
    ↓ (traduce pregunta a SQL)
database.py
    ↓ (ejecuta en)
/mnt/nba_data/dosaros_local.db
    ↓ (devuelve datos)
bot_consultas.py (genera tweet + imagen)
    ↓ (envía a)
Telegram
```

---

## 🔑 ARCHIVOS CRÍTICOS (NO ELIMINAR)

| Archivo | Propósito | Riesgo |
|---------|-----------|--------|
| `.env` | Tokens y credenciales | 🔴 CRÍTICO |
| `src/automation/bot_consultas.py` | Bot Telegram | 🔴 CRÍTICO |
| `avatar_prompt_generator.py` | Generador de prompts | 🟡 IMPORTANTE |
| `/mnt/nba_data/dosaros_local.db` | BBDD | 🔴 CRÍTICO |
| `requirements.txt` | Dependencias | 🟡 IMPORTANTE |

---

## 🚀 ARCHIVOS EDITABLES SEGUROS

| Archivo | Tipo | Cambios Seguros |
|---------|------|-----------------|
| `docs/*.md` | Documentación | ✅ Editar libremente |
| `assets/data/team_colors_clean.csv` | Datos | ⚠️ Backup primero |
| Scripts propios | Python | ✅ Editar + test |
| `.env.example` | Template | ✅ Actualizar ejemplo |

---

## 📍 LOCALIZACIONES IMPORTANTES

### Windows (Local)
```
C:\Users\rover\dosaros-data-project\
├── .env                   (local, no sincronizar)
├── venv\                  (no sincronizar)
├── .git\                  (para push/pull)
└── ... resto del código
```

### Pi (Producción)
```
/home/pi/dosaros-data-project/
├── .env                   (con tokens reales)
├── venv/                  (venv activado)
├── logs/                  (generados por cron)
└── src/automation/bot_consultas.py (EN VIVO)

BBDD separada:
/mnt/nba_data/dosaros_local.db
```

### GitHub
```
github.com/dosaroscontact/dosaros-data-project/
├── main branch            (producción)
└── dev branch             (desarrollo, opcional)
```

---

## 🔄 FLUJO DE CAMBIOS

### Para editar código en Windows:
```
1. Edita archivo en Windows
   C:\Users\rover\dosaros-data-project\archivo.py

2. Commit y push a GitHub
   git add archivo.py
   git commit -m "Descripción"
   git push origin main

3. Pull en Pi
   cd /home/pi/dosaros-data-project
   git pull origin main

4. Si cambió bot_consultas.py:
   tmux kill-session -t bot_consultas
   tmux new-session -d -s bot_consultas \
     "cd /home/pi/dosaros-data-project && \
      source venv/bin/activate && \
      PYTHONPATH=/home/pi/dosaros-data-project \
      python src/automation/bot_consultas.py"

5. Verificar:
   ps aux | grep bot_consultas.py
```

### Para ejecutar scripts en Pi:
```
1. SSH a Pi:
   ssh pi@192.168.1.136

2. Navegar:
   cd /home/pi/dosaros-data-project

3. Activar venv:
   source venv/bin/activate

4. Ejecutar:
   PYTHONPATH=/home/pi/dosaros-data-project python script.py

5. Ver logs:
   tail -f logs/archivo.log
```

---

## 📦 DEPENDENCIAS PRINCIPALES

Ver en `requirements.txt`:

```
python-telegram-bot==20.x     ← Bot Telegram
requests==2.31.x             ← HTTP requests
google-cloud-aiplatform==1.x ← Vertex AI
google-auth==2.x             ← Google Auth
google-cloud-storage==2.x    ← Google Cloud Storage
SQLAlchemy==2.x              ← ORM (opcional)
pillow==10.x                 ← Imagen
dotenv==0.21.x               ← Variables de entorno
```

---

## 🎯 PUNTOS DE ENTRADA

| Punto | Tipo | Ejecutor |
|-------|------|----------|
| `bot_consultas.py` | Daemon | tmux (24/7) |
| `daily_avatar_generator.py` | Cron | Sistema (08:00 AM) |
| `master_sync.py` | Cron | Sistema (09:00 AM) |
| `main.py` | CLI | Manual (desarrollo) |

---

## 📝 NOTAS IMPORTANTES

1. **`.env` NO va a GitHub** (está en .gitignore)
   - Guardar copia segura separadamente
   - Tokens son sensibles

2. **Logs se generan automáticamente** en `/logs/`
   - Monitorear cron_daily_avatar.log
   - Revisar errores en bot_errors.log

3. **venv NO tocar**
   - Contiene paquetes instalados
   - Regenerar si está corrupto: `pip install -r requirements.txt`

4. **BBDD en ruta especial** (/mnt/nba_data/)
   - No mover ni renombrar
   - Backup recomendado regularmente

5. **GitHub credenciales**
   - Usuario: dosaroscontact
   - Usar SSH key o token personal

---

**Versión:** 1.0  
**Última actualización:** 2026-03-29
