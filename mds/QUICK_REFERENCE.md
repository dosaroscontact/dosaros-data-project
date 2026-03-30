# ⚡ Quick Reference - Dos Aros

**Guía rápida para Claude Code y desarrollo.**

---

## 🚀 COMANDOS CRÍTICOS

### Iniciar Bot (en Pi)
```bash
cd /home/pi/dosaros-data-project
source venv/bin/activate
PYTHONPATH=/home/pi/dosaros-data-project python src/automation/bot_consultas.py
```

### Detener Bot (en Pi)
```bash
tmux kill-session -t bot_consultas
# O manualmente:
pkill -f bot_consultas.py
```

### Reiniciar Bot en tmux (en Pi)
```bash
tmux kill-session -t bot_consultas
sleep 1
tmux new-session -d -s bot_consultas "cd /home/pi/dosaros-data-project && source venv/bin/activate && PYTHONPATH=/home/pi/dosaros-data-project python src/automation/bot_consultas.py"
```

### Regenerar Prompts (en Pi)
```bash
cd /home/pi/dosaros-data-project
source venv/bin/activate
PYTHONPATH=/home/pi/dosaros-data-project python avatar_prompt_generator.py
```

### Ver Bot en ejecución
```bash
ps aux | grep bot_consultas.py | grep -v grep
tmux list-sessions
tmux attach-session -t bot_consultas  # Ver logs vivos
```

---

## 📊 COMANDOS BBDD

### Conectar a BBDD
```bash
sqlite3 /mnt/nba_data/dosaros_local.db
```

### Contar registros
```bash
sqlite3 /mnt/nba_data/dosaros_local.db "SELECT COUNT(*) FROM avatar_prompts;"
sqlite3 /mnt/nba_data/dosaros_local.db "SELECT COUNT(*) FROM team_colors;"
sqlite3 /mnt/nba_data/dosaros_local.db "SELECT COUNT(*) FROM avatar_teams;"
```

### Ver estructura tabla
```bash
sqlite3 /mnt/nba_data/dosaros_local.db ".schema avatar_prompts"
sqlite3 /mnt/nba_data/dosaros_local.db ".schema team_colors"
sqlite3 /mnt/nba_data/dosaros_local.db ".schema avatar_teams"
```

### Ver primeros registros
```bash
sqlite3 /mnt/nba_data/dosaros_local.db "SELECT * FROM avatar_prompts LIMIT 5;"
sqlite3 /mnt/nba_data/dosaros_local.db "SELECT team_name, primary_color FROM team_colors LIMIT 10;"
```

### Buscar equipo específico
```bash
sqlite3 /mnt/nba_data/dosaros_local.db "SELECT * FROM avatar_prompts WHERE team_name LIKE '%Lakers%';"
sqlite3 /mnt/nba_data/dosaros_local.db "SELECT * FROM team_colors WHERE team_name = 'Los Angeles Lakers';"
```

### Actualizar registro
```bash
sqlite3 /mnt/nba_data/dosaros_local.db "UPDATE avatar_prompts SET image_url = '/path/to/image.png' WHERE id = 1;"
```

---

## 🐙 COMANDOS GIT

### Status del repo
```bash
git status
git log --oneline -10
```

### Commit y push
```bash
git add archivo.py
git commit -m "Descripción del cambio"
git push origin main
```

### Ver cambios
```bash
git diff archivo.py
git show HEAD~1
```

### Pull en Pi
```bash
cd /home/pi/dosaros-data-project
git pull origin main
```

---

## 🎮 COMANDOS TELEGRAM (Para testear)

Desde el chat de Telegram:

```
/avatar_prompt Lakers          → prompt específico por equipo
/avatar_random                 → prompt aleatorio  (alias: /avatar)
/avatar_today                  → 5 prompts del día (alias: /avatars)
/video Top 5 anotadores NBA esta semana
/v Top 5 anotadores NBA esta semana  → alias de /video
¿Quién fue el máximo anotador NBA?
Cuántos triples metió Luka esta temporada
```

---

## 📋 VARIABLES DE ENTORNO CRÍTICAS

```bash
# Ver .env actual
cat /home/pi/dosaros-data-project/.env

# Editar .env
nano /home/pi/dosaros-data-project/.env

# Verificar token Telegram
grep TELEGRAM_TOKEN /home/pi/dosaros-data-project/.env

# Verificar ruta BBDD
grep LOCAL_DB /home/pi/dosaros-data-project/.env
```

---

## 📁 CAMBIOS DE DIRECTORIO FRECUENTES

```bash
# Ir a repo local
cd /home/pi/dosaros-data-project

# Ver contenido
ls -la
ls -la src/automation/
ls -la assets/avatars/

# Ver logs
cd logs
ls -la
tail -f cron_daily_avatar.log
tail -f avatar_generation.log

# Ir a BBDD
sqlite3 /mnt/nba_data/dosaros_local.db
```

---

## 🔍 DEBUGGING COMÚN

### Bot no responde
```bash
# Ver si está corriendo
ps aux | grep bot_consultas

# Ver logs vivos
tmux attach-session -t bot_consultas

# Revisar errors
tail -50 logs/bot_errors.log
```

### Bot no responde pero el proceso existe

Si `ps aux | grep bot_consultas` muestra un proceso activo pero el bot no responde a comandos en Telegram:

1. Verifica si hay error "No module named 'src'":
```bash
tmux attach-session -t bot_consultas
```

2. Si ves ese error, reinicia con PYTHONPATH:
```bash
tmux kill-session -t bot_consultas
tmux new-session -d -s bot_consultas "cd /home/pi/dosaros-data-project && PYTHONPATH=/home/pi/dosaros-data-project python src/automation/bot_consultas.py"
```

---

### Cron job no ejecuta
```bash
# Ver cron jobs
crontab -l

# Ver logs de cron
grep CRON /var/log/syslog | tail -20

# Ejecutar manualmente
cd /home/pi/dosaros-data-project && source venv/bin/activate && python daily_avatar_generator.py
```

### BBDD no accesible
```bash
# Verificar ruta
ls -la /mnt/nba_data/dosaros_local.db

# Permisos
chmod 666 /mnt/nba_data/dosaros_local.db

# Test conexión
sqlite3 /mnt/nba_data/dosaros_local.db "SELECT 1;"
```

### Error "No module named 'src'"
```bash
# SIEMPRE ejecutar con PYTHONPATH:
PYTHONPATH=/home/pi/dosaros-data-project python script.py
```

---

## 📊 SNIPPETS SQL FRECUENTES

### Contar prompts por equipo
```sql
SELECT team_name, COUNT(*) as count 
FROM avatar_prompts 
GROUP BY team_name 
ORDER BY count DESC;
```

### Prompts sin colores
```sql
SELECT ap.team_name 
FROM avatar_prompts ap 
LEFT JOIN team_colors tc ON ap.team_name = tc.team_name 
WHERE tc.team_name IS NULL;
```

### Listar todos los equipos
```sql
SELECT DISTINCT team_name FROM avatar_teams ORDER BY team_name;
```

### Prompts aleatorio
```sql
SELECT * FROM avatar_prompts ORDER BY RANDOM() LIMIT 1;
```

### Actualizar múltiples registros
```sql
UPDATE avatar_prompts 
SET image_url = '/path/to/images/' || LOWER(REPLACE(team_name, ' ', '_')) || '.png' 
WHERE image_url IS NULL;
```

---

## 🔧 PATRONES COMUNES

### Patrón: Cambiar archivo en Windows, sincronizar en Pi

```bash
# 1. En Windows, edita archivo
# 2. Commit
git add archivo.py
git commit -m "Cambio en archivo.py"
git push origin main

# 3. En Pi
git pull origin main

# 4. Si cambió bot, reinicia
tmux kill-session -t bot_consultas
# ... reinicia con comando de arriba

# 5. Verifica
ps aux | grep bot_consultas
```

### Patrón: Ejecutar query SQL y ver resultado

```bash
# En Pi, ejecutar query
sqlite3 /mnt/nba_data/dosaros_local.db "SELECT * FROM avatar_prompts WHERE team_name LIKE '%Lakers%';"

# Ver output
# Devolver resultado a Claude Code
```

### Patrón: Ver logs vivos

```bash
# En Pi
tail -f logs/cron_daily_avatar.log
# Ctrl+C para salir

# O específico del bot
tmux attach-session -t bot_consultas
# Ctrl+B + D para desconectar
```

---

## 📈 MONITOREO DIARIO

```bash
# Ver status general
ps aux | grep -E 'bot_consultas|python'

# Ver últimos logs
tail -20 logs/cron_daily_avatar.log
tail -20 logs/avatar_generation.log

# Ver mensajes Telegram (en logs o Telegram app)

# Contar prompts
sqlite3 /mnt/nba_data/dosaros_local.db "SELECT COUNT(*) FROM avatar_prompts;"

# Ver equipos sin colores
sqlite3 /mnt/nba_data/dosaros_local.db "SELECT team_name FROM avatar_teams WHERE team_name NOT IN (SELECT team_name FROM team_colors);"
```

---

## 🚨 EMERGENCIAS

### Bot completamente congelado
```bash
# 1. Matar proceso
pkill -9 -f bot_consultas.py

# 2. Limpiar sesiones tmux
tmux kill-server

# 3. Reiniciar desde cero
tmux new-session -d -s bot_consultas "cd /home/pi/dosaros-data-project && source venv/bin/activate && PYTHONPATH=/home/pi/dosaros-data-project python src/automation/bot_consultas.py"

# 4. Verificar
ps aux | grep bot_consultas
```

### BBDD corrupta
```bash
# 1. Backup
cp /mnt/nba_data/dosaros_local.db /mnt/nba_data/dosaros_local.db.bak

# 2. Verificar integridad
sqlite3 /mnt/nba_data/dosaros_local.db "PRAGMA integrity_check;"

# 3. Reparar (si es necesario)
sqlite3 /mnt/nba_data/dosaros_local.db ".recover" | sqlite3 /mnt/nba_data/dosaros_local.db.recovered

# 4. Restaurar desde backup
cp /mnt/nba_data/dosaros_local.db.bak /mnt/nba_data/dosaros_local.db
```

### Cron no ejecuta
```bash
# 1. Verificar crontab
crontab -l

# 2. Revisar logs
grep CRON /var/log/syslog | tail -50

# 3. Probar manualmente
cd /home/pi/dosaros-data-project && source venv/bin/activate && python daily_avatar_generator.py

# 4. Si funciona, re-agregar a cron
crontab -e
```

---

## 📞 TESTING RÁPIDO

### Test bot en desarrollo (sin cron)
```bash
cd /home/pi/dosaros-data-project
source venv/bin/activate
PYTHONPATH=/home/pi/dosaros-data-project python src/automation/bot_consultas.py
# Enviar mensaje en Telegram
# Ver respuesta en terminal
# Ctrl+C para salir
```

### Test de prompts
```bash
python -c "
from avatar_prompt_generator import *
result = get_avatar_prompt('Lakers')
print(result)
"
```

### Test de BBDD
```python
import sqlite3
conn = sqlite3.connect('/mnt/nba_data/dosaros_local.db')
cursor = conn.execute('SELECT COUNT(*) FROM avatar_prompts')
print(cursor.fetchone())
```

---

**Última actualización:** 2026-03-29  
**Para Claude Code:** Copiar y pegar snippets según sea necesario
