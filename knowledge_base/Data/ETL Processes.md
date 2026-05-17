# ⚙️ ETL Processes

**Filosofía**: Incremental bajo demanda. No descargar datos masivos a menos que sea necesario.

---

## 🔄 Diario (Cron 9:00 — Pi)

**Script**: `master_sync.py`
**Cron**: `0 9 * * * /home/pi/dosaros-data-project/venv/bin/python master_sync.py`

### Flujo (6 pasos)
1. **Extrae resultados NBA de ayer** → BD
   - Script: `src/etl/extract_yesterday_results.py`
   - Llama: `nba_api.stats.endpoints.LeagueGameLog`
2. **Extrae resultados EuroLeague de ayer** → BD
   - Script: `src/etl/extract_yesterday_euro.py`
3. **Envía resumen** → Telegram
4. **Detecta perlas** (actuaciones destacadas) → Telegram
   - Script: `src/processors/insight_generator.py`
   - Usa IA (Gemini) para detectar patrones
5. **Genera hilo X/Twitter** (5-6 tweets) → Telegram (revisión manual)
   - Script: `src/processors/gemini_social.py`
6. **Genera story 1080×1920** → Telegram
   - Script: `src/processors/image_generator.py`

---

## 📚 Carga Histórica (Bajo Demanda)

### NBA
```bash
# Por bloques de años
python src/etl/historic_pbp_loader.py --liga nba --bloque 2015-2019
python src/etl/historic_pbp_loader.py --liga nba --bloque 2020-2024
```

### EuroLeague
```bash
python src/etl/historic_pbp_loader.py --liga euro --bloque 2007-2022
```

**Tip**: Lanzar en tmux para sesiones largas:
```bash
tmux new -s nba_hist
python src/etl/historic_pbp_loader.py --liga nba --bloque 2015-2019
# Ctrl+B, D para salir
```

---

## 🎭 Carga de Dimensiones Avatar

```bash
# Una sola vez (semilla)
python src/database/populate_avatars.py        # dimensiones
python src/etl/seed_avatar_teams.py            # variaciones detalladas
```

---

## 🗄️ Operaciones de BD

### Inicializar BD Local
```bash
python -c "from src.database.init_local_db import init_db; init_db()"
```

### Crear Tabla avatar_teams
```bash
python -c "from src.database.init_avatar_teams import create_avatar_teams; create_avatar_teams()"
```

---

## 🧩 Módulos Críticos

| Módulo | Función |
|--------|---------|
| `src/etl/nba_sync.py` | Sincronización NBA diaria (partidos + PBP + jugadores) |
| `src/etl/euro_sync.py` | Sincronización EuroLeague diaria |
| `src/etl/historic_pbp_loader.py` | Carga histórica con `--liga`, `--bloque` |
| `src/etl/euro_historic_games_loader.py` | Partidos Euro históricos |
| `src/etl/extract_yesterday_results.py` | Resultados NBA del día anterior |
| `src/etl/extract_yesterday_euro.py` | Resultados Euro del día anterior |
| `src/etl/seed_avatar_teams.py` | Semilla `avatar_teams` (68 variaciones) |

---

## 🔐 Convenciones de ETL

### Idempotencia
Todos los ETLs usan `INSERT OR IGNORE` para evitar duplicados:
```sql
INSERT OR IGNORE INTO nba_pbp (gameId, period, eventNum, ...)
VALUES (?, ?, ?, ...)
```

### Manejo de Errores
- `print` para logging (visible en cron logs)
- Capturar excepciones y continuar (no abortar todo el ETL por un partido)
```python
try:
    procesar_partido(game_id)
except Exception as e:
    print(f"ERROR partido {game_id}: {e}")
    continue
```

### Variables de Entorno
- `LOCAL_DB` — Ruta a SQLite (nunca hardcodear)
- `SUPABASE_URL/KEY` — Si se sube a serving
- `GEMINI_API_KEY` (+ fallbacks)
- `TELEGRAM_BOT_TOKEN` — Para notificaciones

---

## 📊 Coordenadas EuroLeague

**Antes de guardar**:
```python
from src.utils.mapper import map_euro_to_canonical

x_norm, y_norm = map_euro_to_canonical(x_raw, y_raw)
# x_norm, y_norm ∈ [0, 100]
```

**Guardar como**: `x_norm`, `y_norm` en `euro_pbp`.

---

## ⏰ Estado Actual de Procesos (Pi)

Ver siempre [[../Project Root/STATUS|📊 STATUS]] para estado actual.

**2026-05-17**:
- `tmux nba_hist2` → `historic_pbp_loader.py --liga nba --bloque 2017-2019`
- `tmux euro_hist2` → `historic_pbp_loader.py --liga euro --bloque 2010-2021`

---

## 🔗 Referencias

- [[Data Dictionary|📖 Diccionario canónico]]
- [[../Workflows/Daily Automation|⏰ Workflow automatización]]
- [[../Architecture/Database Schema|🗄️ Schema BD]]
- [[../Project Root/STATUS|📊 Estado actual]]
