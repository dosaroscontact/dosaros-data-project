# ⏰ Daily Automation — Cron + Bot Telegram

---

## 📅 Cron Diario (Pi, 9:00 AM)

**Script**: `master_sync.py`
**Comando cron**:
```cron
0 9 * * * /home/pi/dosaros-data-project/venv/bin/python master_sync.py >> logs/cron_output.log 2>&1
```

### Pipeline Completo
1. ⬇️ Extraer resultados NBA de ayer → BD
2. ⬇️ Extraer resultados EuroLeague de ayer → BD
3. 📨 Enviar resumen a Telegram
4. 💎 Detectar perlas (actuaciones destacadas) con IA → Telegram
5. 🐦 Generar hilo X/Twitter (5-6 tweets) → Telegram para revisión
6. 🖼️ Generar story 1080×1920 con la perla top → Telegram

**Duración estimada**: 5-15 minutos (depende de rate limits LLM)

**Logs**: `/home/pi/dosaros-data-project/logs/cron_output.log`

---

## 🤖 Bot Telegram (Siempre Activo)

**Script**: `src/automation/bot_consultas.py`
**Sesión tmux**: `bot_consultas`
**Polling**: Constante

### Comandos del Bot

| Input | Acción |
|-------|--------|
| Pregunta en español | NL→SQL automático → tabla resultados |
| `sí` | Generar tweet + imagen tras un resultado |
| `no` | Descartar resultado, no hacer nada |
| `/video <texto>` | Generar MP4 con Remotion |
| `/v <texto>` | Alias de `/video` |
| `/avatar_prompt <equipo>` | Prompt Midjourney/ImageFX para equipo |
| `/avatar_random` o `/avatar` | Prompt aleatorio |
| `/avatar_today` o `/avatars` | 5 prompts aleatorios del día |
| `/StatusIA` | Estado de proveedores LLM |
| `/Sync` | Lanzar sincronización bajo demanda |

### Flujo de Consulta NL → SQL
1. Usuario envía pregunta
2. `analista_ia.py` → LLM traduce a SQL
3. SQL ejecuta sobre SQLite Pi
4. Resultados → tabla formateada
5. Bot pregunta: "¿generar tweet/imagen?"
6. Si "sí": `gemini_social.py` + `image_generator.py`

---

## 🎬 Video Generator

**Script**: `src/integrations/video_generator/`
**Stack**: Editor Pro Max + Remotion + IA

### Flujo
1. Usuario: `/video <texto>`
2. `video_data_extractor.py` extrae datos de BD
3. Mapea apodos → nombres reales (`assets/player_aliases.json`)
4. Remotion compone MP4
5. Bot envía MP4

---

## 📨 Bot Manager (Envío)

**Script**: `src/automation/bot_manager.py`

### Funciones
```python
enviar_mensaje(chat_id, texto)
enviar_grafico(chat_id, imagen_path)
enviar_video(chat_id, video_path)
```

---

## 🔄 Reintentos y Resilience

### LLM Fallback
Si Gemini falla → OpenAI → Claude → Groq → DeepSeek → Kimi → Grok

Implementado en `src/utils/api_manager.py`.

### ETL Errores
Si un partido falla, se loguea pero el ETL continúa:
```python
try:
    procesar_partido(game_id)
except Exception as e:
    print(f"ERROR partido {game_id}: {e}")
    continue
```

---

## 📊 Monitorización

### Logs en Tiempo Real
```bash
# Cron
tail -f /home/pi/dosaros-data-project/logs/cron_output.log

# Bot Telegram
tmux attach -t bot_consultas
```

### Verificar Última Ejecución Cron
```bash
# Pi
grep "ejecución" /home/pi/dosaros-data-project/logs/cron_output.log | tail -5
```

### Estado del Bot
Telegram: enviar `/StatusIA` → muestra estado de cada proveedor LLM.

---

## 🚨 Manejo de Incidentes

### Cron no ejecutó
```bash
# Verificar cron está corriendo
systemctl status cron

# Ver últimos logs
tail -100 /home/pi/dosaros-data-project/logs/cron_output.log

# Ejecutar manualmente
cd /home/pi/dosaros-data-project
source venv/bin/activate
python master_sync.py
```

### Bot Telegram silencioso
```bash
ssh pi@192.168.1.136
tmux attach -t bot_consultas
# Ver si hay errores
# Ctrl+C, restart si necesario
python src/automation/bot_consultas.py
```

### Quota LLM excedida
- `/StatusIA` en Telegram para ver qué proveedor falla
- Editar `.env` con nueva clave o esperar reset (Gemini: 24h)
- El fallback debería tomar el siguiente

---

## 🔗 Referencias

- [[../Development/Environment Setup|💻 Setup Pi]]
- [[../Data/ETL Processes|⚙️ Procesos ETL]]
- [[../Project Root/STATUS|📊 Estado actual]]
- [[../Architecture/API Stack|🔌 LLM providers]]
