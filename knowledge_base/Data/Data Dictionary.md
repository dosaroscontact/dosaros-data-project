# 📖 Data Dictionary — Diccionario Canónico

**Regla**: Cualquier extractor o transformador debe seguir estas normalizaciones para permitir comparación NBA ↔ EuroLeague.

---

## 🔑 Campos Canónicos

| Campo Canónico | NBA (nba_api) | EuroLeague (euroleague-api) |
|----------------|---------------|------------------------------|
| `player_id` | `PERSON_ID` | `Player_ID` |
| `team_id` | `TEAM_ID` | `Team` |
| `pts` | `PTS` | `Points` |
| `ast` | `AST` | `Assists` |
| `reb` | `REB` | `TotalRebounds` |
| `min` | `MIN` | `Minutes` |
| `pir` | `PLUS_MINUS` (o cálculo) | `PIR` |

---

## 🎯 Coordenadas de Tiro

**Sistema canónico**: 0-100 (porcentual)
**Origen**: (0,0) en el centro de la pista

### NBA
- `LOC_X`, `LOC_Y` → ya normalizados en algunos endpoints
- Conversión: depende del endpoint

### EuroLeague
- `x`, `y` originales → requieren mapeo
- Función: `src.utils.mapper.map_euro_to_canonical(x, y)`
- Output: `x_norm`, `y_norm` (0-100)

---

## 📊 Categorización de Tiros

Agrupar siempre en:
- `2PT` — Tiros de dos puntos
- `3PT` — Triples
- `FT` — Tiros libres

---

## 🗄️ Tablas Principales

### NBA

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

### EuroLeague

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

## 🎭 Dimensiones Avatar

### `teams_metadata` (54 filas)
- 30 NBA + 24 EuroLeague
- **Campos**: `code`, `name`, `liga`, `color_primary`, `color_secondary`, `color_accent`

### Dimensiones LOCKED
- `dim_posturas` (50 filas) — Posturas del avatar
- `dim_vestimentas` (50 filas) — Variantes de ropa
- `dim_decorados` (61 filas) — Entornos
- `dim_tipos_logo` (56 filas) — Estilos de logo
- `avatar_teams` (68 filas) — Variaciones pre-curadas

---

## 📅 Convención de Temporadas

### NBA
- `22023` → Regular 2023-24
- `42023` → Playoffs 2023-24
- Patrón: `[type][year]` donde type: `1`=preseason, `2`=regular, `4`=playoffs

### EuroLeague
- `E2023_001` → Temporada 2023-24, partido 001
- Patrón: `E[year]_[3-digit-game]`

---

## ⚠️ Reglas SQL Críticas

### 1. Nunca usar `YEAR()`
```sql
-- ❌ MAL
SELECT * FROM nba_games WHERE YEAR(GAME_DATE) = 2024

-- ✅ BIEN
SELECT * FROM nba_games WHERE SEASON_ID LIKE '22023%'
SELECT * FROM nba_games WHERE GAME_DATE LIKE '2024%'
```

### 2. Mayúsculas vs camelCase
```sql
-- nba_games → MAYÚSCULAS
SELECT GAME_ID, SEASON_ID, PTS FROM nba_games;

-- nba_pbp → camelCase
SELECT gameId, period, actionType FROM nba_pbp;
```

### 3. JOIN entre tablas
```sql
SELECT g.GAME_DATE, p.playerName, p.actionType
FROM nba_games g
JOIN nba_pbp p ON g.GAME_ID = p.gameId
WHERE g.SEASON_ID LIKE '22023%'
LIMIT 10;
```

---

## 🔗 Referencias

- [[ETL Processes|⚙️ Procesos de ingesta]]
- [[../Architecture/Database Schema|🗄️ Schema completo]]
- [[../Analytics/Stats Glossary|📊 Glosario estadístico]]

---

**Fuente**: `CLAUDE.md` + esquema de BD inspeccionado
