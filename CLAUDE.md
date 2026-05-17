# CLAUDE.md

> ⚠️ **AUTO-GENERADO desde Obsidian** — No editar manualmente.
> Fuente: `knowledge_base/` · Última sincronización: 2026-05-17 12:22:31
> Para editar: modificar archivos en `knowledge_base/` y ejecutar `python scripts/sync_obsidian_to_claude.py`

---

## 📋 Proyecto
**Dos Aros** — Análisis comparativo NBA + EuroLeague.
*"Datos primero. Contexto después. Opinión al final."*

Stack: Raspberry Pi 4 · Python · SQLite · Next.js 15 · Telegram bot · Multi-LLM (Gemini/Groq/Claude)
→ Knowledge base completo: `knowledge_base/INDEX.md` (Obsidian vault)

---


## 📖 Proyecto
*Fuente: `knowledge_base/Project Root/README.md`*

#### 🎯 Objetivo

Asistir en el desarrollo y mantenimiento de DOS AROS, un sistema de investigación de baloncesto comparado (NBA y EuroLeague).

**Principios rectores**:
1. **Datos primero**: Cualquier afirmación se apoya en SQL verificable
2. **Contexto después**: Comparación NBA ↔ EuroLeague, históricos
3. **Opinión al final**: Solo cuando los datos lo justifican
4. **Sostenibilidad**: Soluciones de bajo coste y mantenimiento
5. **Local-first**: SQLite Pi es source of truth; Supabase solo para serving

---

#### 🏗️ Stack Tecnológico

#### Backend
- **Lenguaje**: Python 3.10+
- **BD warehouse**: SQLite en Raspberry Pi (`/mnt/nba_data/dosaros_local.db`)
- **BD serving**: Supabase PostgreSQL (solo agregados)
- **APIs**: nba_api, euroleague_api, Telegram Bot API
- **LLMs**: Gemini (primario), OpenAI, Claude, Groq, DeepSeek, Kimi, Grok, Manus

#### Frontend
- **Framework**: Next.js 15 (App Router)
- **Lenguaje**: TypeScript
- **Estilos**: Tailwind CSS
- **Animaciones**: Framer Motion
- **Formularios**: FormSubmit.co (sin backend)

#### Infraestructura
- **Desarrollo**: Windows 11 (C:\Users\rover\dosaros-data-project\)
- **Producción**: Raspberry Pi 4 (192.168.1.136)
- **Remoto**: GitHub (rama main)

---


---


## 📊 Estado Actual
*Fuente: `knowledge_base/Project Root/STATUS.md`*

#### 🟢 Entornos Activos

#### Windows (Desarrollo Local)
- **Ruta**: `C:\Users\rover\dosaros-data-project\`
- **Frontend dev server**: http://localhost:3000 ✅ Activo
- **Servidor Streamlit**: Inactivo (lanzar con `streamlit run src/app/main.py`)
- **Rama git**: `main` (sincronizada con remoto)

#### Raspberry Pi 4 (Producción)
- **IP**: `192.168.1.136`
- **Ruta**: `/home/pi/dosaros-data-project/`
- **BD**: `/mnt/nba_data/dosaros_local.db` (SQLite)
- **Cron 9:00**: ✅ Activo (master_sync.py)
- **Bot Telegram**: ✅ Activo en tmux `bot_consultas`

**Sesiones tmux activas**:
- `bot_consultas` — Bot Telegram polling
- `nba_hist2` — Carga histórica NBA 2017-2019 ⚙️ En progreso
- `euro_hist2` — Carga histórica EuroLeague E2010-E2021 ⚙️ En progreso

#### GitHub
- **Repo**: https://github.com/dosaroscontact/dosaros-data-project
- **Rama principal**: `main`
- **Historial**: ✅ Limpio (BFG aplicado 2026-05-17)
- **Último commit**: `d991ba6` — docs: Add comprehensive project overview

---

#### 📦 Cobertura de Datos

#### NBA (`nba_pbp`, 5,015,190 registros)
- ✅ Regular 2015-16, 2016-17 (completas)
- ⚠️ Regular 2017-18 parcial (~25%, en `nba_hist2`)
- ❌ 2018-19, 2019-20 (pendientes)
- ✅ Regular + Playoffs 2020-21 → 2024-25 (completas)
- ✅ `nba_games`: completo desde 1983

#### EuroLeague (`euro_pbp`, 1,049,283 registros)
- ✅ E2007, E2008, E2009 cargadas
- ⚠️ E2010 parcial (en `euro_hist2`)
- ❌ E2011 → E2021 (pendientes)
- ✅ E2022-E2025 completas

---


---


## 💻 Entornos
*Fuente: `knowledge_base/Development/Environment Setup.md`*

#### 🥧 Raspberry Pi 4 (Producción)

**IP**: `192.168.1.136` · **Usuario**: `pi`
**Ruta**: `/home/pi/dosaros-data-project/`
**venv**: `/home/pi/dosaros-data-project/venv/bin/python`
**PYTHONPATH**: `/home/pi/dosaros-data-project` (requerido para imports `src.*`)

#### BD Warehouse
- **Ruta**: `/mnt/nba_data/dosaros_local.db`
- **Tipo**: SQLite (source of truth)
- **Backup**: Manual (vía SCP)

#### Conexión SSH
```bash
ssh pi@192.168.1.136
cd /home/pi/dosaros-data-project
source venv/bin/activate
export PYTHONPATH=/home/pi/dosaros-data-project
```

#### Sesiones tmux
| Sesión | Proceso |
|--------|---------|
| `bot_consultas` | Bot Telegram (siempre activo) |
| `nba_hist2` | Carga histórica NBA 2017-2019 |
| `euro_hist2` | Carga histórica EuroLeague E2010-E2021 |

```bash
tmux ls                          # Listar sesiones
tmux attach -t bot_consultas    # Conectar a una

---


## ⌨️ Comandos
*Fuente: `knowledge_base/Development/Commands.md`*

#### 🚀 Arranque de Servicios

#### Frontend Next.js
```bash
npm run dev          # Dev server con hot reload → http://localhost:3000
npm run build        # Compilar a producción
npm start            # Servidor producción (post-build)
```

#### Streamlit Dashboard
```bash
streamlit run src/app/main.py
```

#### Bot Telegram (Pi)
```bash
tmux attach -t bot_consultas
python src/automation/bot_consultas.py
#### 📊 ETL — Extracción de Datos

#### Carga Histórica NBA
```bash
python src/etl/historic_pbp_loader.py --liga nba --bloque 2015-2019
python src/etl/historic_pbp_loader.py --liga nba --bloque 2020-2024
```

#### Carga Histórica EuroLeague
```bash
python src/etl/historic_pbp_loader.py --liga euro --bloque 2007-2022
```

#### Cargar Partidos Euro Históricos
```bash
python src/etl/euro_historic_games_loader.py
```

#### Sincronización Diaria (Manual)
```bash

---


## 🏗️ Arquitectura
*Fuente: `knowledge_base/Architecture/System Design.md`*

#### 🏗️ Arquitectura de Alto Nivel

```
┌─────────────────────────────────────────────────────────┐
│                  APIs Externas                          │
│  (nba_api, euroleague_api, Telegram, LLM providers)    │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│         Raspberry Pi 4 (192.168.1.136)                 │
│  ┌──────────────────────────────────────────────────┐  │
│  │  ETL Layer (src/etl/)                            │  │
│  │  - nba_sync.py                                   │  │
│  │  - euro_sync.py                                  │  │
│  │  - historic_pbp_loader.py                        │  │
│  └──────────────────────────────────────────────────┘  │
│                         ↓                               │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Warehouse: SQLite                               │  │
│  │  /mnt/nba_data/dosaros_local.db                  │  │
│  │  (Source of Truth)                               │  │
│  └──────────────────────────────────────────────────┘  │
│                         ↓                               │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Processors (src/processors/)                    │  │
│  │  - insight_generator.py                          │  │
│  │  - gemini_social.py                              │  │
│  │  - image_generator.py                            │  │
│  │  - avatar_prompt_generator.py                    │  │
│  └──────────────────────────────────────────────────┘  │
│                         ↓                               │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Automation (src/automation/)                    │  │
│  │  - bot_consultas.py (Telegram)                   │  │
│  │  - bot_manager.py (envío)                        │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                         ↓                  ↓
        ┌────────────────────┐    ┌────────────────────┐
        │   Supabase         │    │   Telegram         │
        │   (Serving Layer)  │    │   (Bot + Stories)  │
        └────────────────────┘    └────────────────────┘
                ↓
        ┌────────────────────┐
        │   Frontend Web     │
        │   Next.js 15       │
        │   (Windows local)  │
        └────────────────────┘
```

---


---


## 🗄️ Schema BD
*Fuente: `knowledge_base/Data/Data Dictionary.md`*

#### 🗄️ Tablas Principales

#### NBA

#### `nba_games`
- **Naming**: MAYÚSCULAS
- **Clave**: `GAME_ID`
- **Campos clave**: `SEASON_ID`, `TEAM_ID`, `GAME_DATE`, `PTS`, `WL`
- **Cobertura**: 1983 → presente

#### `nba_pbp` (Play-by-Play)
- **Naming**: camelCase
- **Clave**: `(gameId, period, eventNum)`
- **Campos clave**: `gameId`, `actionType`, `period`, `clock`, `playerName`, `teamId`
- **Cobertura**: 2015-presente (con gaps)

#### `nba_players_games`
- **Naming**: MAYÚSCULAS
- **Clave**: `(GAME_ID, PLAYER_ID)`
- **Campos clave**: `SEASON_ID`, `PLAYER_ID`, `GAME_ID`, `GAME_DATE`, `PTS`, `AST`, `REB`

#### EuroLeague

#### `euro_games`
- **Naming**: snake_case
- **Clave**: `game_id` (formato `E2023_001`)
- **Campos clave**: `date`, `home_team`, `away_team`, `score_home`, `score_away`

#### `euro_pbp`
- **Naming**: snake_case
- **Clave**: `(game_id, event_num)`
- **Campos clave**: `game_id`, `event_num`, `period`, `action_type`, `player_id`, `x`, `y`

#### `euro_players_games`
- **Naming**: snake_case
- **Clave**: `(game_id, player_id)`
- **Campos clave**: `game_id`, `player_id`, `team_id`, `pts`, `reb`, `ast`

#### `euro_stats_career`
- Estadísticas career de jugadores Euro
- **Campos**: `player_id`, `season_code`, `team_name`, `pts`, `reb`, `ast`, `pir`

---

#### ⚠️ Reglas SQL Críticas

#### 1. Nunca usar `YEAR()`
```sql
-- ❌ MAL
SELECT * FROM nba_games WHERE YEAR(GAME_DATE) = 2024

-- ✅ BIEN
SELECT * FROM nba_games WHERE SEASON_ID LIKE '22023%'
SELECT * FROM nba_games WHERE GAME_DATE LIKE '2024%'
```

#### 2. Mayúsculas vs camelCase
```sql
-- nba_games → MAYÚSCULAS
SELECT GAME_ID, SEASON_ID, PTS FROM nba_games;

-- nba_pbp → camelCase
SELECT gameId, period, actionType FROM nba_pbp;
```

#### 3. JOIN entre tablas
```sql
SELECT g.GAME_DATE, p.playerName, p.actionType
FROM nba_games g
JOIN nba_pbp p ON g.GAME_ID = p.gameId
WHERE g.SEASON_ID LIKE '22023%'
LIMIT 10;
```

---


---


## 🎨 Brand
*Fuente: `knowledge_base/Brand/Visual Identity.md`*

#### 🎨 Paleta de Colores

| Token | HEX | Uso Principal |
|-------|-----|---------------|
| **Azul base** | `#0D1321` | Logo, titulares, números, gráficos principales |
| **Azul dark** | `#011E3B` | Backgrounds oscuros (frontend) |
| **Blanco** | `#FFFFFF` | Fondo posts, carruseles, visualizaciones |
| **Gris** | `#E6E8EE` | Ejes, divisores, cajas de stats, líneas |
| **Magenta** | `#B1005A` | Dato destacado, subcabeceras, highlights |
| **Naranja** | `#FF7D28` | CTAs, iconos, mapas de tiro, calor |
| **Naranja dark** | `#FF3E04` | Hover states, énfasis |
| **Naranja legacy** | `#F28C28` | (deprecated, no usar) |

#### Distribución de Color
```
70% blanco · 20% azul · 7% gris · 2% magenta · 1% naranja
```

#### Colores Plotly
- Theme: `plotly_white`
- Makes: `#88D4AB`
- Misses: `#FF8787`

---

#### ✍️ Tipografías

| Uso | Fuente | Ubicación |
|-----|--------|-----------|
| Titulares / números grandes | **Space Grotesk** | `assets/static/SpaceGrotesk-*.ttf` |
| Texto / datos / etiquetas | **Inter** | `assets/static/Inter_*.ttf` |

---


---


## ⏰ Automatización
*Fuente: `knowledge_base/Workflows/Daily Automation.md`*

#### 📅 Cron Diario (Pi, 9:00 AM)

**Script**: `master_sync.py`
**Comando cron**:
```cron
0 9 * * * /home/pi/dosaros-data-project/venv/bin/python master_sync.py >> logs/cron_output.log 2>&1
```

#### Pipeline Completo
1. ⬇️ Extraer resultados NBA de ayer → BD
2. ⬇️ Extraer resultados EuroLeague de ayer → BD
3. 📨 Enviar resumen a Telegram
4. 💎 Detectar perlas (actuaciones destacadas) con IA → Telegram
5. 🐦 Generar hilo X/Twitter (5-6 tweets) → Telegram para revisión
6. 🖼️ Generar story 1080×1920 con la perla top → Telegram

**Duración estimada**: 5-15 minutos (depende de rate limits LLM)

**Logs**: `/home/pi/dosaros-data-project/logs/cron_output.log`

---

#### 🤖 Bot Telegram (Siempre Activo)

**Script**: `src/automation/bot_consultas.py`
**Sesión tmux**: `bot_consultas`
**Polling**: Constante

#### Comandos del Bot

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

#### Flujo de Consulta NL → SQL
1. Usuario envía pregunta
2. `analista_ia.py` → LLM traduce a SQL
3. SQL ejecuta sobre SQLite Pi
4. Resultados → tabla formateada
5. Bot pregunta: "¿generar tweet/imagen?"
6. Si "sí": `gemini_social.py` + `image_generator.py`

---


---



---

## 📚 Referencias en Obsidian Vault

Para contenido completo y actualizado, consultar:
- **Overview**: `knowledge_base/Project Root/README.md`
- **Estado actual**: `knowledge_base/Project Root/STATUS.md`
- **Comandos**: `knowledge_base/Development/Commands.md`
- **Setup entornos**: `knowledge_base/Development/Environment Setup.md`
- **Troubleshooting**: `knowledge_base/Development/Debugging Guide.md`
- **Arquitectura**: `knowledge_base/Architecture/System Design.md`
- **ADRs**: `knowledge_base/Architecture/Decisions Log.md`
- **Brand**: `knowledge_base/Brand/Visual Identity.md`
- **Avatar**: `knowledge_base/Brand/Avatar System.md`
- **Data dictionary**: `knowledge_base/Data/Data Dictionary.md`
- **ETL**: `knowledge_base/Data/ETL Processes.md`
- **Workflows**: `knowledge_base/Workflows/Daily Automation.md`

---

**Generado por**: `scripts/sync_obsidian_to_claude.py`
**Para regenerar**: `python scripts/sync_obsidian_to_claude.py`
