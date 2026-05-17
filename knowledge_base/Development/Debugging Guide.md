# 🐛 Debugging Guide

---

## 🌐 Frontend Next.js

### Servidor no arranca
```bash
# Limpiar cache
rm -rf .next
npm run dev
```

### Error de build
```bash
# Ver errores TypeScript
npx tsc --noEmit

# Build con verbose
npm run build -- --verbose
```

### Página muestra contenido viejo
```bash
# Hard refresh: Ctrl+Shift+R
# O limpiar cache del navegador
```

---

## 🐍 Backend Python

### Import Error `src.xxx not found`
```bash
# Verificar PYTHONPATH
export PYTHONPATH=/home/pi/dosaros-data-project  # Pi
$env:PYTHONPATH = "C:\Users\rover\dosaros-data-project"  # Windows
```

### Venv no se activa
```bash
# Pi
source venv/bin/activate

# Windows
.\venv\Scripts\Activate.ps1
# Si falla: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### BD locked
```bash
# Identificar proceso
lsof | grep dosaros_local.db  # Linux
# O en Windows con Handle.exe

# Matar proceso si bloqueado
kill -9 <PID>
```

---

## 🤖 Bot Telegram

### Bot no responde
```bash
ssh pi@192.168.1.136
tmux attach -t bot_consultas
# Ver errores en consola
# Ctrl+C para detener
python src/automation/bot_consultas.py
```

### Comando /Sync no funciona
- Verificar tmux session `bot_consultas` activa
- Verificar permisos de archivos en Pi
- Ver logs: `grep Sync logs/cron_output.log`

---

## 🔌 APIs LLM

### Status de Proveedores
Telegram: enviar `/StatusIA`

### Cuota excedida (Gemini)
- Gemini Free: 60 req/min, 1500 req/día
- Esperar reset (24h) o cambiar a fallback
- Ver actual: `python -c "from src.utils.api_manager import status; print(status())"`

### Bug DeepSeek/Kimi
- Issue conocido (pendiente)
- Workaround: están al final del fallback chain

---

## 🗄️ Base de Datos

### Inspeccionar SQLite
```bash
sqlite3 /mnt/nba_data/dosaros_local.db
.tables                    # Listar tablas
.schema nba_pbp           # Ver schema
SELECT COUNT(*) FROM nba_pbp;
SELECT * FROM nba_games WHERE SEASON_ID LIKE '22023%' LIMIT 5;
.exit
```

### Backup BD Pi
```bash
ssh pi@192.168.1.136 "cat /mnt/nba_data/dosaros_local.db" > backup_$(date +%Y%m%d).db
```

### Restaurar BD
```bash
scp backup_20260517.db pi@192.168.1.136:/mnt/nba_data/dosaros_local.db
```

---

## 🔧 Git

### GitHub Push Rejected (Large Files)
```bash
# Error: File X is 141.5 MB; exceeds 100 MB limit
# Solución: BFG

java -jar bfg.jar --delete-files "filename.ext" --no-blob-protection
git reflog expire --expire=now --all
git gc --prune=now --aggressive
git push --force-with-lease origin main
```

### Push Rejected (Behind Remote)
```bash
git fetch origin
git pull --rebase origin main
git push origin main
```

### Conflicto durante Merge
```bash
git status                     # Ver conflictos
# Editar archivos con conflictos
git add <archivo>
git commit                     # NO usar --no-edit
```

---

## 📊 Streamlit

### App no carga datos
- Verificar `LOCAL_DB` apunta a BD válida
- Probar query directamente en SQLite

### Plot vacío
- Verificar query devuelve datos
- Theme: `plotly_white`

---

## 🎬 Video Generator

### MP4 no se genera
```bash
# Verificar Remotion instalado
cd src/integrations/video_generator
npm install
npm run render
```

### Datos incorrectos en video
- Revisar `assets/player_aliases.json`
- Apodos comunes: "Shai" → "Gilgeous-Alexander"

---

## 🚨 Errores Comunes

### `ModuleNotFoundError: No module named 'src'`
→ PYTHONPATH no configurado, ver [[Environment Setup]]

### `sqlite3.OperationalError: database is locked`
→ Otro proceso accediendo BD, kill PID

### `telegram.error.TimedOut`
→ Red lenta, reintenta automáticamente

### `RateLimitError` (Gemini)
→ Quota excedida, fallback debería activarse

### `next-swc not found`
→ Reinstalar: `npm install`

---

## 🔗 Referencias

- [[Environment Setup|💻 Setup completo]]
- [[Commands|⌨️ Comandos]]
- [[../Workflows/Daily Automation|⏰ Automatización]]
