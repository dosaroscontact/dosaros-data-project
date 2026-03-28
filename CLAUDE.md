# CLAUDE.md

## Proyecto
**Dos Aros** — análisis comparativo NBA + EuroLeague. Filosofía: *"Datos primero. Contexto después. Opinión al final."*
Stack: Raspberry Pi 4 · Python · SQLite · Telegram bot · Gemini/Groq API.
→ Guía de marca y avatar completa: `assets/docs/BRAND.md`

## Comandos
```bash
streamlit run src/app/main.py
python scripts/check_syntax.py
python -c "from src.database.init_local_db import init_db; init_db()"
python src/database/populate_avatars.py        # seed dimensiones avatar
python src/etl/seed_avatar_teams.py            # seed variaciones detalladas
python src/processors/avatar_prompt_generator.py --equipo LAL
python src/processors/avatar_prompt_generator.py --liga NBA
```

## Arquitectura
```
APIs (nba_api, euroleague_api) → ETL (src/etl/) → SQLite Pi → Supabase → Streamlit
```

### Storage
1. **Warehouse**: SQLite Pi `/mnt/nba_data/dosaros_local.db` — PBP histórico, source of truth
2. **Serving**: Supabase PostgreSQL — subsets agregados para visualización
3. **Local dev**: solo código, sin datos críticos

### Módulos clave
| Módulo | Función |
|--------|---------|
| `src/app/main.py` | Streamlit — tabs análisis + NL SQL |
| `src/utils/api_manager.py` | Interfaz unificada 10+ APIs LLM/imagen/audio con fallback |
| `src/etl/historic_pbp_loader.py` | Carga histórica PBP NBA+Euro (`--liga`, `--bloque`) |
| `src/etl/seed_avatar_teams.py` | Seed `avatar_teams` con 68 variaciones |
| `src/etl/euro_historic_games_loader.py` | Carga partidos Euro históricos |
| `src/database/init_avatar_teams.py` | Crea tabla `avatar_teams` |
| `src/database/populate_avatars.py` | Crea y puebla tablas dimensionales avatar |
| `src/processors/image_generator.py` | Story 1080×1920 con fuentes bundled (`assets/static/`) |
| `src/processors/avatar_prompt_generator.py` | Genera prompts Midjourney/ImageFX por equipo |
| `src/processors/insight_generator.py` | Insights AI sobre datos |
| `src/prompts/` | Personas y contenido redes sociales |
| `src/app/analista_ia.py` | SQL generation para consultas baloncesto |

### LLM
Primario: Google Gemini. Fallbacks: OpenAI, Claude, Groq, DeepSeek, Kimi, Grok.
Todo enrutado por `src/utils/api_manager.py`.

## Schema BD (tablas principales)
```
nba_games          — SEASON_ID, TEAM_ID, GAME_ID, GAME_DATE, PTS… (mayúsculas)
nba_pbp            — gameId, actionType, period, clock, playerName… (camelCase)
nba_players_games  — SEASON_ID, PLAYER_ID, GAME_ID, GAME_DATE…
euro_games         — game_id, date, home_team, away_team, score_home, score_away
euro_pbp           — game_id, event_num, period, action_type, player_id, x, y
euro_players_games — game_id, player_id, team_id, pts, reb, ast
euro_stats_career  — player_id, season_code, team_name, pts, reb, ast, pir
teams_metadata     — code, name, liga, color_primary, color_secondary, color_accent
dim_posturas       — id, valor  (50 filas)
dim_vestimentas    — id, valor  (50 filas)
dim_decorados      — id, valor  (61 filas)
dim_tipos_logo     — id, valor  (56 filas)
avatar_teams       — team_code, liga, team_name, colores A/B/C/D, postura,
                     vestimenta, decorado, tipo_logo, variacion_idx
```

#### Cobertura PBP actual (Pi)
- NBA: temporadas regulares 2020-21 → 2025-26 + playoffs 2020-2025 (cargando 2015-2019)
- EuroLeague: E2022-E2025 completas, cargando E2007-E2021

## Sistema Avatar
Ver `assets/docs/BRAND.md` para descripción completa del personaje y parámetros visuales.

**54 equipos en BD**: 30 NBA + 24 EuroLeague con colores oficiales en `teams_metadata`.
**452,620,000** combinaciones únicas de prompt vía tablas dimensionales.

Flujo de generación:
```
teams_metadata × dim_posturas × dim_vestimentas × dim_decorados × dim_tipos_logo
→ avatar_prompt_generator.py → prompt Midjourney/ImageFX
→ imagen generada → chroma key → image_generator.py → story Telegram
```

## Reglas críticas

### SQL
- **Nunca `YEAR()`** — usar `SEASON_ID LIKE '2024%'`
- `nba_pbp` usa camelCase (`gameId`, `actionType`); `nba_games` usa MAYÚSCULAS (`GAME_ID`, `SEASON_ID`)
- Temporada NBA: `22023` = regular 2023-24, `42023` = playoffs 2023-24
- Euro game_id: `E2023_001` → season=2023, code=001

### Coordenadas EuroLeague
- Normalizar a 0-100 vía `src.utils.mapper.map_euro_to_canonical` antes de guardar/visualizar
- Campos: `x_norm`, `y_norm`

### Visualización
- Theme: `plotly_white`; Makes: `#88D4AB`; Misses: `#FF8787`
- Colores marca: azul `#0D1321`, magenta `#B1005A`, naranja `#F28C28`, gris `#E6E8EE`
- Fuentes: Space Grotesk (titulares), Inter (datos) — ambas bundled en `assets/static/`

### Código
- Código y comentarios en **español** (términos técnicos en inglés)
- `print` para logging; capturar errores y continuar ETL sin abortar
- Variables de entorno para rutas y claves (`LOCAL_DB`, nunca hardcodear)
- `INSERT OR IGNORE` para upserts en tablas de referencia

### Imágenes
- Story: 1080×1920 px, fondo color equipo + degradado
- Fuentes cargadas desde `assets/static/` (primero bundled, luego sistema, luego fallback)
- Chroma key: `#00FF00`; recortar 80px inferior (watermark Google)

## Entorno
```
LOCAL_DB          — ruta SQLite (default: /mnt/nba_data/dosaros_local.db)
SUPABASE_URL/KEY  — Supabase
GEMINI_API_KEY    — primario LLM
OPENAI/CLAUDE/GROQ/DEEPSEEK_API_KEY — fallbacks
TELEGRAM_BOT_TOKEN — notificaciones
```
Copiar `.env.example` → `.env`.
