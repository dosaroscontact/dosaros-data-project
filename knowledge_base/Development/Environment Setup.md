# 💻 Environment Setup — Windows + Pi + GitHub

---

## 🖥️ Windows (Desarrollo Local)

**Ubicación**: `C:\Users\rover\dosaros-data-project\`

### Stack
- Node.js 20+ (Next.js 15)
- Python 3.10+ con venv
- SQLite local (testing)
- Git for Windows
- Java 25 (para BFG Repo Cleaner)

### Setup Inicial
```powershell
# Frontend
npm install

# Backend Python
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Variables de Entorno (.env)
```
LOCAL_DB=C:\Users\rover\dosaros-data-project\data\dosaros_local.db
SUPABASE_URL=...
SUPABASE_KEY=...
GEMINI_API_KEY=...
OPENAI_API_KEY=...
CLAUDE_API_KEY=...
GROQ_API_KEY=...
DEEPSEEK_API_KEY=...
TELEGRAM_BOT_TOKEN=...
```

### Arrancar Servicios
```bash
npm run dev                       # Frontend → http://localhost:3000
streamlit run src/app/main.py    # Streamlit dashboard
python -c "from src.database.init_local_db import init_db; init_db()"
```

---

## 🥧 Raspberry Pi 4 (Producción)

**IP**: `192.168.1.136` · **Usuario**: `pi`
**Ruta**: `/home/pi/dosaros-data-project/`
**venv**: `/home/pi/dosaros-data-project/venv/bin/python`
**PYTHONPATH**: `/home/pi/dosaros-data-project` (requerido para imports `src.*`)

### BD Warehouse
- **Ruta**: `/mnt/nba_data/dosaros_local.db`
- **Tipo**: SQLite (source of truth)
- **Backup**: Manual (vía SCP)

### Conexión SSH
```bash
ssh pi@192.168.1.136
cd /home/pi/dosaros-data-project
source venv/bin/activate
export PYTHONPATH=/home/pi/dosaros-data-project
```

### Sesiones tmux
| Sesión | Proceso |
|--------|---------|
| `bot_consultas` | Bot Telegram (siempre activo) |
| `nba_hist2` | Carga histórica NBA 2017-2019 |
| `euro_hist2` | Carga histórica EuroLeague E2010-E2021 |

```bash
tmux ls                          # Listar sesiones
tmux attach -t bot_consultas    # Conectar a una
# Ctrl+B, D para salir sin matar
```

### Cron Diario
```cron
0 9 * * * /home/pi/dosaros-data-project/venv/bin/python master_sync.py >> logs/cron_output.log 2>&1
```

**Logs**: `/home/pi/dosaros-data-project/logs/cron_output.log`

### Comandos de Producción
```bash
# Carga histórica NBA
python src/etl/historic_pbp_loader.py --liga nba --bloque 2015-2019

# Carga histórica EuroLeague
python src/etl/historic_pbp_loader.py --liga euro --bloque 2007-2022

# Cron manual
python master_sync.py

# Avatar prompts
python src/processors/avatar_prompt_generator.py --equipo LAL
python src/processors/avatar_prompt_generator.py --liga NBA
```

---

## ☁️ GitHub (Remoto)

**Repo**: `https://github.com/dosaroscontact/dosaros-data-project.git`
**Rama principal**: `main`

### Configuración Git
```bash
git config user.name "DosAros"
git config user.email "dosaroscontact@gmail.com"
```

### Flujo de Commits
1. Desarrollo local en Windows
2. Cambios pequeños y frecuentes
3. Commit con mensaje descriptivo
4. Push directo a `main` (sin PR por ahora)

### Limpieza de Historial (si hay archivos grandes)
```bash
# BFG Repo Cleaner
java -jar bfg.jar --delete-files "filename.ext" --no-blob-protection
git reflog expire --expire=now --all && git gc --prune=now --aggressive
git push --force-with-lease origin main
```

### .gitignore Crítico
```
node_modules/
.next/
venv/
__pycache__/
.env
*.db
logs/
```

---

## 🔗 Sincronización entre Entornos

### Flujo Windows → Pi
```bash
# En Windows: commit y push
git add .
git commit -m "feat: ..."
git push origin main

# En Pi: pull
ssh pi@192.168.1.136
cd /home/pi/dosaros-data-project
git pull origin main
sudo systemctl restart cron  # si cambias master_sync.py
```

### Flujo Pi → Windows
La Pi no debe modificar código directamente. Solo lee datos y los procesa.
Si necesitas cambios desde la Pi: hacer commit localmente, push, y pull en Windows.

---

## 🛠️ Troubleshooting Común

### Frontend no arranca
```bash
rm -rf .next
npm run dev
```

### BD locked en Pi
```bash
# Identificar proceso bloqueante
lsof | grep dosaros_local.db
# Si es necesario, matar proceso
kill -9 <PID>
```

### Bot Telegram caído
```bash
tmux attach -t bot_consultas
# Ctrl+C para detener si está roto
python src/automation/bot_consultas.py
# Ctrl+B, D para salir
```

### Push rechazado por GitHub
Ver [[../Development/Debugging Guide#GitHub Push Rejected]]

---

**Ver también**:
- [[Commands|⌨️ Comandos frecuentes]]
- [[Debugging Guide|🐛 Guía de troubleshooting]]
