# ⌨️ Commands — Comandos Frecuentes

---

## 🚀 Arranque de Servicios

### Frontend Next.js
```bash
npm run dev          # Dev server con hot reload → http://localhost:3000
npm run build        # Compilar a producción
npm start            # Servidor producción (post-build)
```

### Streamlit Dashboard
```bash
streamlit run src/app/main.py
```

### Bot Telegram (Pi)
```bash
tmux attach -t bot_consultas
python src/automation/bot_consultas.py
# Ctrl+B, D para salir sin detener
```

---

## 🗄️ Base de Datos

### Inicializar BD Local
```bash
python -c "from src.database.init_local_db import init_db; init_db()"
```

### Poblar Avatares (dimensiones)
```bash
python src/database/populate_avatars.py
python src/etl/seed_avatar_teams.py
```

### Verificar Sintaxis Python
```bash
python scripts/check_syntax.py
```

---

## 📊 ETL — Extracción de Datos

### Carga Histórica NBA
```bash
python src/etl/historic_pbp_loader.py --liga nba --bloque 2015-2019
python src/etl/historic_pbp_loader.py --liga nba --bloque 2020-2024
```

### Carga Histórica EuroLeague
```bash
python src/etl/historic_pbp_loader.py --liga euro --bloque 2007-2022
```

### Cargar Partidos Euro Históricos
```bash
python src/etl/euro_historic_games_loader.py
```

### Sincronización Diaria (Manual)
```bash
# Todo el flujo
python master_sync.py

# Solo NBA
python src/etl/extract_yesterday_results.py

# Solo EuroLeague
python src/etl/extract_yesterday_euro.py
```

---

## 🎭 Avatar System

### Generar Prompt por Equipo
```bash
python src/processors/avatar_prompt_generator.py --equipo LAL
python src/processors/avatar_prompt_generator.py --equipo MAD
```

### Generar Prompts por Liga
```bash
python src/processors/avatar_prompt_generator.py --liga NBA
python src/processors/avatar_prompt_generator.py --liga EUR
```

### Generar Prompt Aleatorio
```bash
python src/processors/avatar_prompt_generator.py --random
```

---

## 🤖 Bot Telegram — Comandos

| Input | Acción |
|-------|--------|
| Pregunta en español | NL→SQL automático |
| `sí` | Generar tweet + imagen tras resultado |
| `no` | Descartar resultado |
| `/video <texto>` | Generar MP4 |
| `/v <texto>` | Alias de /video |
| `/avatar_prompt LAL` | Prompt avatar para Lakers |
| `/avatar_random` | Prompt aleatorio |
| `/avatars` | 5 prompts del día |
| `/StatusIA` | Estado proveedores LLM |
| `/Sync` | Lanzar sync bajo demanda |

---

## 🔧 Git — Operaciones Comunes

### Workflow Estándar
```bash
git status
git add <archivo>
git commit -m "feat: ..."
git push origin main
```

### Limpiar Historial (BFG)
```bash
# Solo si hay archivos >100MB
java -jar bfg.jar --delete-files "archivo.ext" --no-blob-protection
git reflog expire --expire=now --all
git gc --prune=now --aggressive
git push --force-with-lease origin main
```

### Verificar Estado Remoto
```bash
git fetch origin
git log origin/main..HEAD --oneline    # Commits locales no pusheados
git log HEAD..origin/main --oneline    # Commits remotos no pulleados
```

---

## 🐛 Debugging

### Ver Logs Cron (Pi)
```bash
ssh pi@192.168.1.136
tail -f /home/pi/dosaros-data-project/logs/cron_output.log
```

### Ver Logs Bot Telegram
```bash
tmux attach -t bot_consultas
# Ctrl+B, D para salir
```

### Inspeccionar BD SQLite
```bash
sqlite3 /mnt/nba_data/dosaros_local.db
.tables
.schema nba_pbp
SELECT COUNT(*) FROM nba_pbp;
.exit
```

---

## 📦 Gestión de Dependencias

### Python (Pi)
```bash
source venv/bin/activate
pip install -r requirements.txt
pip freeze > requirements.txt    # Tras añadir libs
```

### Node.js (Windows)
```bash
npm install
npm install <package>
npm update
```

---

## 🔄 Sincronización Obsidian ↔ CLAUDE.md (Fase 2)

```bash
# Ejecutar script de sincronización (cuando esté listo)
python scripts/sync_obsidian_to_claude.py
```

---

**Ver también**:
- [[Environment Setup|💻 Setup de entornos]]
- [[Debugging Guide|🐛 Troubleshooting]]
