# AGENTS.md — Contexto Técnico para Agentes IA
**Proyecto Dos Aros**  
**Última actualización:** 21 de marzo de 2026  
**Propósito:** Documentación de arquitectura, APIs públicas y flujos de datos para agentes IA autónomos (OpenClaw, etc.)

---

## 1. RUTAS CRÍTICAS DEL SISTEMA

### 1.1 Base de Datos Principal (SQLite3)
```
/mnt/nba_data/dosaros_local.db
```
**Descripción:** Data warehouse centralizada (formato largo, una fila por equipo-partido)  
**Propietario:** BD primaria del proyecto  
**Fuente de verdad:** ALWAYS usar esta para consultas, incluso desde PostgreSQL hay que validar contra esta  
**Acceso:** Local en Raspberry Pi; en Windows, usar ruta relativa o configurar en `.env`

**Variable de entorno:**
```env
LOCAL_DB=/mnt/nba_data/dosaros_local.db   # Linux/Pi
LOCAL_DB=C:\Users\rover\dosaros-data-project\dosaros_local.db  # Windows dev
```

### 1.2 Base de Datos PostgreSQL (Backup/Cloud)
```
postgresql://postgres:PASSWORD@192.168.1.136:5432/proyecto_dos_aros
```
**Descripción:** PostgreSQL en Raspberry Pi, esquema para consultas interactivas  
**Estado:** Sincronizado desde SQLite (no es fuente de verdad)  
**Acceso:** Red local (requiere VPN Dos Aros o estar en LAN Nuvole)

**Credenciales (`.env`):**
```env
DB_HOST=192.168.1.136
DB_PORT=5432
DB_NAME=proyecto_dos_aros
DB_USER=postgres
DB_PASSWORD=<value>  # rotado regularmente
```

### 1.3 APIs de Datos
| Origen | Endpoint | Responsable | Rango |
|--------|----------|------------|-------|
| **NBA** | `stats.nba.com` (nba_api v1.11.4) | Estadísticas oficiales NBA | 1983-hoy |
| **Euroliga** | `euroleague_api` (paquete Python) | Stats EuroLeague oficial | 2004-hoy |
| **Google Gemini** | `generativelanguage.googleapis.com` | Claude/Gemini Flash para IA | N/A |
| **Ollama** | `http://localhost:11434` | LLM local (gemma2:2b, llama3) | Local |

### 1.4 Directorios Importantes
```
c:\Users\rover\dosaros-data-project\
├── src/
│   ├── app/              # Streamlit + entrada principal
│   ├── etl/              # Extractores de datos (39 scripts)
│   ├── database/         # Inicializadores de BD
│   ├── processors/       # Post-procesado (IA, reportes)
│   ├── utils/            # Helpers (mapper.py CRÍTICO)
│   └── docs/
├── data/                 # JSONs descargas raw
├── logs/                 # Archivos de log
├── automation/           # Bot Telegram
├── scripts/              # check_syntax.py, etc.
└── requirements.txt      # Dependencias Python
```

**Archivo crítico: `src/utils/mapper.py`**  
Normaliza todas las coordenadas Euroliga (-250 a 1400 original) → escala 0-100

---

## 2. ARQUITECTURA TÉCNICA REAL

### 2.1 Diagrama General

```
┌─────────────────────────────────────────────────────────────────────┐
│                        PROYECTO DOS AROS                             │
│                    Laboratorio Análisis Cuantitativo                │
└─────────────────────────────────────────────────────────────────────┘
                              ▲        ▲        ▲
                              │        │        │
                  ┌───────────┘        │        └──────────┐
                  │                    │                   │
          ┌───────▼────────┐   ┌──────▼──────┐   ┌────────▼────────┐
          │   NBA API       │   │Euroliga API │   │PostgreSQL (Pi)  │
          │ (Official Stats)│   │(Official)   │   │(Backup Cloud)   │
          └────────┬────────┘   └──────┬──────┘   └─────────────────┘
                   │                   │
                   └───────┬───────────┘
                           │
                  ┌────────▼────────────────┐
                  │   ETL Layer (39 scripts)│
                  ├───────────────────────┐
                  │ • NBA extractors       │
                  │ • Euroliga extractors  │
                  │ • PBP (Play-by-Play)   │
                  │ • Player stats         │
                  │ • Yesterdau snapshots  │
                  │ • Bulk loaders         │
                  └────────┬──────────────┘
                           │
                  ┌────────▼──────────────────┐
                  │ Mappers & Processors      │
                  ├───────────────────────────┤
                  │ • Coordinate normalize    │
                  │ • Column mapping          │
                  │ • Data validation         │
                  │ • Insight generation      │
                  └────────┬──────────────────┘
                           │
                   ┌───────▼─────────┐
                   │ SQLite3 (Primary)│
                   ├──────────────────┤
                   │/mnt/nba_data/    │
                   │dosaros_local.db  │
                   └────┬──────┬──────┘
                        │      │
          ┌─────────────┘      └──────────────┐
          │                                   │
     ┌────▼──────┐                    ┌──────▼──────┐
     │ Streamlit │                    │ PostgreSQL  │
     │ Dashboard │                    │ Backup/Sync │
     │ + IA Chat │                    │             │
     └────┬──────┘                    └─────────────┘
          │
   ┌──────┴─────────┐
   │                │
┌──▼────┐    ┌─────▼──┐
│Gemini │    │ Ollama  │
│(Cloud)│    │(Local)  │
└──┬────┘    └────┬────┘
   │              │
   └──────┬───────┘
          │
   ┌──────▼──────────┐
   │ Telegram Bot    │
   │ (Reportes AI)   │
   └─────────────────┘
```

### 2.2 Componentes Principales

#### **Layer 1: Data Ingestion (ETL)**
- **Responsabilidad:** Extraer datos de APIs oficiales, limpiar, validar
- **Patrón:** Fetch → Validate → Upsert (evitar duplicados)
- **Tecnología:** `nba_api`, `euroleague_api`, `requests`, `pandas`
- **Almacenamiento temporal:** DataFrames en memoria; inserción batch a BD

**Características:**
- Reintentos automáticos con backoff exponencial
- Control de pausas entre requests (respeto API)
- Mensajes de error capturados (programa prosigue)
- Logging de inserciones completadas

#### **Layer 2: Data Transformation (Mappers)**
- **Responsabilidad:** Normalizar esquemas, calcular métricas derivadas
- **Crítico:** `src/utils/mapper.py::map_euro_to_canonical()` y `normalize_euro_coords()`
- **Entrada:** DataFrames crudos de API
- **Salida:** DataFrames listos para inserción en BD

**Transformaciones típicas:**
```python
# Coordenadas Euroliga: (-250 a 250, 0 a 1400) → (0 a 100, 0 a 100)
x_norm = ((x + 250) / 500) * 100
y_norm = (y / 1400) * 100

# Columnas API Euroliga → nombres canónicos
'Player_ID' → 'player_id', 'Points' → 'pts', etc.

# Derivadas
'fg_pct' = 'FGM' / 'FGA' (si not null)
```

#### **Layer 3: Data Warehouse (SQLite3)**
- **Formato:** Relacional, una fila por evento/equipo-partido
- **Consistencia:** ACID transacciones
- **Índices:** Estratégicos sobre columnas de filtrado frecuente
- **Escalabilidad:** ~50MB (nba_games full history), eficiente con indices

**Tablas principales:**
- `nba_games` — fuente de verdad NBA (stats equipo por partido)
- `nba_players_games` — stats individuales NBA
- `nba_pbp` — evento a evento (play-by-play)
- `euro_games` — partidos Euroliga
- `euro_pbp` — eventos Euroliga (con coords normalizadas)
- `euro_players_games` — stats individuales Euroliga
- `euro_standings` — tabla dinámica (overwrite diario)
- `euro_players_ref/euro_teams/euro_stats_career` — referencias

#### **Layer 4: Query Engine (Gemini / Ollama)**
- **Gemini (Cloud):** `google.genai.GenerativeModel("gemini-2.5-flash-latest")`
  - Trade-off: latencia ~500ms vs. calidad SQL superior
  - Contexto: Tablas + primeras 5 filas (instrucción Copilot)
  
- **Ollama (Local):** `gemma2:2b`, `llama3`
  - Trade-off: latencia ~100ms vs. calidad SQL menor
  - Contexto: Esquema texto hardcodeado

**Patrón:**
1. Usuario pregunta → "¿Top 3 tiradores de triples ayer?"
2. IA genera SQL (`SELECT PLAYER_NAME FROM nba_players_games WHERE...`)
3. Limpieza (remover markdown, validar sintaxis)
4. Ejecución contra SQLite3
5. Resultado → UI (Streamlit) o Telegram

#### **Layer 5: Presentation (Streamlit)**
- **Puerto:** 8501 (default)
- **Estructura:** Multipage con 6 tabs
- **Caché:** `@st.cache_data` para `load_data()` (5 min default)
- **Colores:** Plotly White + Mint (`#88D4AB` acierto) / Coral (`#FF8787` fallo)

#### **Layer 6: Automation (Telegram Bot + Cron)**
- **Punto entrada:** `master_sync.py::main()`
- **Frecuencia:** Cron diario ~23:00 UTC
- **Acciones:**
  1. Extrae resultados ayer (NBA+Euro)
  2. Busca perlas (top 3 cazadores)
  3. Genera hilo (3 tweets IA)
  4. Envía Telegram (imagen + texto)

---

## 3. LISTA DE FUNCIONES PÚBLICAS

### 3.1 Módulo Principal: `src/app/main.py` (Streamlit)

**Punto entrada:** `streamlit run src/app/main.py`

| Función | Línea | Firma | Propósito |
|---------|-------|-------|----------|
| `obtener_sql_ia` | L37 | `def obtener_sql_ia(pregunta: str) -> str` | Genera SQL desde pregunta natural (Gemini Flash Latest) |
| `dibujar_pista_flat` | L65 | `def dibujar_pista_flat(fig) -> go.Figure` | Añade líneas de cancha minimalista a gráfico Plotly |
| `cargar_datos_nba` | L74 | `@st.cache_data def cargar_datos_nba() -> tuple[pd.DataFrame, ...]` | Carga datos NBA desde SQLite con cache Streamlit |

**Tab 1 - Dashboard Global (L~88):** Métricas resumen NBA/Euro

**Tab 2 - Eficiencia 3P (L~110):** Scatter eficiencia vs. volumen (altair)

**Tab 3 - Series Equipo (L~130):** Timeline de puntos por equipo

**Tab 4 - Analista IA (L~150):** Q&A conversacional (obtener_sql_ia → ejecutar → st.dataframe)

**Tab 5 - Explorador Euro (L~175):** Heatmap tiros jugador (coords normalizadas)

**Tab 6 - Configuración (L~250):** Status conexión BD, versión, etc.

---

### 3.2 Módulo: `src/app/analista_ia.py`

| Función | Línea | Firma | Propósito |
|---------|-------|-------|----------|
| `preguntar_a_gemini` | L22 | `def preguntar_a_gemini(pregunta_usuario: str) -> str` | Envía pregunta a Gemini Flash Latest (API key desde env) |
| `ejecutar_en_hdd` | L33 | `def ejecutar_en_hdd(sql: str) -> Union[pd.DataFrame, str]` | Ejecuta SQL contra `/mnt/nba_data/dosaros_local.db` |

**Contexto Gemini:** Esquema nba_games, nba_players_games, euro_pbp (en prompt)

---

### 3.3 Módulo: `src/app/chat_boloncesto.py`

| Función | Línea | Firma | Propósito |
|---------|-------|-------|----------|
| `generar_sql` | L17 | `def generar_sql(pregunta: str) -> str` | Ollama gemma2:2b → SQL PostgreSQL (Pi) |

**Contexto Ollama:** Texto con tabla nba_teams, nba_games, nba_player_stats

---

### 3.4 Módulo: `src/app/consulta_ia.py`

| Función | Línea | Firma | Propósito |
|---------|-------|-------|----------|
| `preguntar_a_nba` | L13 | `def preguntar_a_nba(pregunta: str) -> pd.DataFrame` | Ollama llama3 → PostgreSQL ejecución |

---

### 3.5 Módulo: `src/app/historial_partidos.py`

| Función | Línea | Firma | Propósito |
|---------|-------|-------|----------|
| `descargar_periodo_historico` | L6 | `def descargar_periodo_historico(ano_inicio, ano_fin) -> None` | Carga histórico NBA 1983-2026 (leaguegamefinder) |

---

### 3.6 Módulo: `src/app/inicializar_db.py`

| Función | Línea | Firma | Propósito |
|---------|-------|-------|----------|
| `crear_tablas` | L11 | `def crear_tablas() -> None` | CREATE TABLE nba_teams, nba_games, nba_player_stats (PostgreSQL Pi) |

---

### 3.7 Módulo: `src/database/db_utils.py`

| Función | Línea | Firma | Propósito | Retorna |
|---------|-------|-------|----------|---------|
| `get_db_connection` | L7 | `def get_db_connection() -> sqlite3.Connection` | Abre SQLite3 con row_factory=Row | Connection |
| `setup_logging` | L18 | `def setup_logging() -> None` | Configura logging INFO | None |

---

### 3.8 Módulo: `src/database/supabase_client.py`

| Función | Línea | Firma | Propósito | Retorna |
|---------|-------|-------|----------|---------|
| `get_supabase_client` | L11 | `def get_supabase_client() -> Client` | Crea cliente Supabase desde `.env` | supabase.Client |

**Requiere `.env`:**
```env
SUPABASE_URL=https://...supabase.co
SUPABASE_KEY=eyJ... (anon public key)
```

---

### 3.9 Módulo: `src/database/init_db.py`

| Función | Línea | Firma | Propósito |
|---------|-------|-------|----------|
| `init_tables` | L6 | `def init_tables() -> None` | Crea tablas Euroliga (euro_games, euro_pbp, euro_players_games) |

---

### 3.10 Módulo: `src/database/init_local_db.py`

| Función | Línea | Firma | Propósito |
|---------|-------|-------|----------|
| `init_db` | L8 | `def init_db() -> None` | Crea tabla nba_games + índices (PRIMARY KEY: GAME_ID, TEAM_ID) |

---

### 3.11 Módulo: `src/etl/nba_extractor.py`

| Función | Línea | Firma | Propósito |
|---------|-------|-------|----------|
| `run_nba_teams_sync` | ~15 | `def run_nba_teams_sync() -> None` | Obtiene equipos NBA (nba_api) → UPSERT Supabase |

---

### 3.12 Módulo: `src/etl/nba_games_extractor.py`

| Función | Línea | Firma | Propósito |
|---------|-------|-------|----------|
| `sync_nba_games` | ~10 | `def sync_nba_games(season_id='2025-26') -> None` | Descarga partidos NBA (LeagueGameFinder) → UPSERT Supabase |

---

### 3.13 Módulo: `src/etl/nba_player_extractor.py`

| Función | Línea | Firma | Propósito |
|---------|-------|-------|----------|
| `sync_player_stats` | ~10 | `def sync_player_stats(limit_games=200) -> None` | Stats individuales (BoxScoreTraditionalV3) → UPSERT Supabase |

---

### 3.14 Módulo: `src/etl/pbp_extractor.py`

| Función | Línea | Firma | Propósito |
|---------|-------|-------|----------|
| `descargar_pbp_por_temporada` | ~8 | `def descargar_pbp_por_temporada(season_id_prefix: str) -> None` | Play-by-play NBA por temporada (PlayByPlayV3) |

---

### 3.15 Módulo: `src/etl/historical_games.py`

| Función | Línea | Firma | Propósito |
|---------|-------|-------|----------|
| `fetch_historical_games` | ~10 | `def fetch_historical_games(start_year=1983) -> None` | Carga histórico completo NBA (1983-2026) |

---

### 3.16 Módulo: `src/etl/jugadores_extractor.py`

| Función | Línea | Firma | Propósito |
|---------|-------|-------|----------|
| `descargar_boxscores_jugadores` | ~10 | `def descargar_boxscores_jugadores(ano_inicio, ano_fin) -> None` | Stats jugadores NBA (LeagueGameLog) |

---

### 3.17 Módulo: `src/etl/euro_extractor.py`

| Función | Línea | Firma | Propósito |
|---------|-------|-------|----------|
| `fetch_game_data` | L10 | `def fetch_game_data(season: int, game_code: int) -> pd.DataFrame \| None` | Obtiene boxscore Euroliga (euroleague_api) |
| `fetch_pbp_data` | L19 | `def fetch_pbp_data(season: int, game_code: int) -> pd.DataFrame \| None` | Obtiene PBP Euroliga |
| `process_and_save` | L32 | `def process_and_save(df_players: pd.DataFrame, season, game_code) -> None` | Mapea columns → euro_players_games |
| `process_pbp` | L56 | `def process_pbp(df_pbp: pd.DataFrame, season, game_code) -> None` | Normaliza PBP (map_euro_to_canonical) → euro_pbp |

---

### 3.18 Módulo: `src/etl/euro_bulk_load.py`

| Función | Línea | Firma | Propósito |
|---------|-------|-------|----------|
| `get_already_loaded_games` | L17 | `def get_already_loaded_games() -> set` | Consulta euro_players_games (evita duplicados) |
| `bulk_load` | L29 | `def bulk_load(start_code: int, end_code: int) -> None` | Carga masiva partidos Euroliga (range códigos) |

---

### 3.19 Módulo: `src/etl/euro_sync.py`

| Función | Línea | Firma | Propósito |
|---------|-------|-------|----------|
| `run_euro_daily` | ~8 | `def run_euro_daily(season: int = 2025) -> None` | Sincronizac diaria: standings + últimos partidos |

---

### 3.20 Módulo: `src/etl/extract_yesterday_results.py`

| Función | Línea | Firma | Propósito |
|---------|-------|-------|----------|
| `get_nba_results_yesterday` | ~8 | `def get_nba_results_yesterday() -> str` | Resultados NBA ayer (ScoreboardV3) |

---

### 3.21 Módulo: `src/etl/extract_yesterday_euro.py`

| Función | Línea | Firma | Propósito |
|---------|-------|-------|----------|
| `extract_euro_results_yesterday` | ~8 | `def extract_euro_results_yesterday() -> str` | Resultados Euroliga ayer (GameStats API) |

---

### 3.22 Módulo: `src/processors/insight_generator.py`

| Función | Línea | Firma | Propósito |
|---------|-------|-------|----------|
| `buscar_perlas_nba` | ~10 | `def buscar_perlas_nba() -> list` | Top 3 cazadores triples ayer → Telegram |

---

### 3.23 Módulo: `src/processors/gemini_social.py`

| Función | Línea | Firma | Propósito |
|---------|-------|-------|----------|
| `obtener_datos_ultima_noche` | ~10 | `def obtener_datos_ultima_noche() -> dict` | Consulta nba_games y euro_games ayer |
| `generar_hilo_resultados` | ~30 | `def generar_hilo_resultados() -> str` | Genera 3 tweets (140 chars c/u) con Gemini |

---

### 3.24 Módulo: `src/utils/mapper.py` ⭐ CRÍTICO

| Función | Línea | Firma | Propósito |
|---------|-------|-------|----------|
| `normalize_euro_coords` | ~5 | `def normalize_euro_coords(x: float, y: float) -> tuple[float, float]` | Convierte coords Euroliga (-250/1400) → 0-100 |
| `map_euro_to_canonical` | ~20 | `def map_euro_to_canonical(df: pd.DataFrame, data_type='pbp') -> pd.DataFrame` | Mapea columnas API → canónicas + normaliza coords |

**Rango original Euroliga:**
- X: -250 (izda) a 250 (dcha)  
- Y: 0 (fondo) a 1400 (arriba)

**Después mapper:**
- X: 0-100 (izda-dcha)
- Y: 0-100 (fondo-arriba)

**Uso obligatorio:** `src/etl/euro_extractor.py::process_pbp()` y visualización Streamlit

---

### 3.25 Módulo: `automation/bot_manager.py`

| Función | Línea | Firma | Propósito |
|---------|-------|-------|----------|
| `enviar_mensaje` | ~12 | `def enviar_mensaje(texto: str) -> dict` | Envía texto Telegram (Markdown parsing) |
| `enviar_grafico` | ~23 | `def enviar_grafico(image_path: str, pie_de_foto: str) -> dict` | Envía PNG a Telegram |
| `escuchar_confirmacion` | ~38 | `def escuchar_confirmacion(timeout_minutos=5) -> bool` | Espera respuesta Telegram (polling) |

**Requiere `.env`:**
```env
TELEGRAM_TOKEN=123456789:ABCDEFGhijklmno...  # Bot token
CHAT_ID=987654321                            # Chat/Channel ID
```

---

### 3.26 Archivo: `master_sync.py` (Orquestador)

| Función | Línea | Firma | Propósito |
|---------|-------|-------|----------|
| `main` | ~14 | `def main() -> None` | Orquesta: extrae ayer → perlas → hilo → Telegram |

**Flujo:**
```python
main()
├── get_nba_results_yesterday() → tabla
├── extract_euro_results_yesterday() → tabla
├── buscar_perlas_nba() → list (imggen)
├── enviar_grafico() → Telegram
├── generar_hilo_resultados() → str (3 tweets)
└── enviar_mensaje() → Telegram
```

**Ejecución:** `python master_sync.py` (típicamente con cron: `0 23 * * * python master_sync.py`)

---

## 4. ESQUEMA BASE DE DATOS

### 4.1 SQLite3: `/mnt/nba_data/dosaros_local.db`

#### Tabla: `nba_games` (Fuente de verdad NBA)
```sql
CREATE TABLE nba_games (
    SEASON_ID TEXT,                -- ej: "2025-26"
    TEAM_ID INTEGER,               -- ID equipo NBA
    TEAM_ABBREVIATION TEXT,        -- ej: "LAL"
    TEAM_NAME TEXT,                -- ej: "Los Angeles Lakers"
    GAME_ID TEXT,                  -- identificador partido
    GAME_DATE TEXT,                -- YYYY-MM-DD
    MATCHUP TEXT,                  -- ej: "LAL vs. BOS"
    WL TEXT,                       -- "W" o "L"
    MIN INTEGER,
    PTS INTEGER,  -- Puntos anotados (TEAM)
    FGM INTEGER, FGA INTEGER, FG_PCT REAL,
    FG3M INTEGER, FG3A INTEGER, FG3_PCT REAL,  -- 3-pointers
    FTM INTEGER, FTA INTEGER, FT_PCT REAL,    -- Free throws
    OREB INTEGER, DREB INTEGER, REB INTEGER,  -- Rebounds
    AST INTEGER,   -- Assists
    STL INTEGER,   -- Steals
    BLK INTEGER,   -- Blocks
    TOV INTEGER,   -- Turnovers
    PF INTEGER,    -- Personal fouls
    PLUS_MINUS REAL,  -- ±
    PRIMARY KEY (GAME_ID, TEAM_ID)
);

CREATE INDEX idx_season ON nba_games (SEASON_ID);
CREATE INDEX idx_team ON nba_games (TEAM_ID);
CREATE INDEX idx_date ON nba_games (GAME_DATE);
```

**Nota especial:** Cada partido tiene **2 filas** (home + away). Consultas deben INNER JOIN o hacer GROUP BY.

---

#### Tabla: `nba_players_games`
```sql
-- Estadísticas individuales de jugadores NBA
-- Proviene de: nba_api BoxScoreTraditionalV3
-- Columnas típicas: gameId, personId, playerName, teamId,
--   minutes, points, reboundsTotal, assists, steals, blocks,
--   fieldGoalsPercentage, threePointersPercentage, plusMinusPoints
```

---

#### Tabla: `nba_pbp`
```sql
-- Play-by-play NBA (evento a evento)
-- Proviene de: nba_api PlayByPlayV3
-- Estructura dinámica (varía según versión API)
-- Columnas típicas: gameId, period, clock, actionType, 
--   personId, shotType, shotDistance, xLegacy, yLegacy
```

---

#### Tabla: `euro_games`
```sql
CREATE TABLE euro_games (
    game_id TEXT PRIMARY KEY,       -- ej: "E2025_1001"
    date TEXT,                      -- YYYY-MM-DD
    home_team TEXT,                 -- nombre equipo local
    away_team TEXT,                 -- nombre equipo visitante
    score_home INTEGER,             -- puntos locales
    score_away INTEGER              -- puntos visitantes
);
```

---

#### Tabla: `euro_pbp` (⭐ Crítica — coords normalizadas)
```sql
CREATE TABLE euro_pbp (
    game_id TEXT,                   -- FK euro_games
    event_num INTEGER,              -- número evento en partido
    period INTEGER,                 -- cuarto (1-4 o más en prórroga)
    clock TEXT,                     -- MM:SS (tiempo reloj)
    action_type TEXT,               -- "FGMade", "FGMiss", "Rebound", etc.
    player_id TEXT,                 -- ID jugador
    x_canvas REAL,                  -- X RAW (-250 a 250)
    y_canvas REAL,                  -- Y RAW (0 a 1400)
    x_norm REAL,                    -- X NORMALIZADO (0-100) ⭐
    y_norm REAL,                    -- Y NORMALIZADO (0-100) ⭐
    score_home INTEGER,             -- peaje local en momento evento
    score_away INTEGER              -- puntuación visitante
);

CREATE INDEX idx_pbp_game ON euro_pbp (game_id);
CREATE INDEX idx_pbp_player ON euro_pbp (player_id);
```

**Conversión coordenadas:**
```python
x_norm = ((x_canvas + 250) / 500) * 100
y_norm = (y_canvas / 1400) * 100
```

---

#### Tabla: `euro_players_games`
```sql
CREATE TABLE euro_players_games (
    game_id TEXT,                   -- FK euro_games
    player_id TEXT,                 -- ID jugador Euroliga
    team_id TEXT,                   -- equipo
    pts INTEGER,                    -- puntos
    reb INTEGER,                    -- rebotes
    ast INTEGER,                    -- asistencias
    FOREIGN KEY (game_id) REFERENCES euro_games(game_id)
);

CREATE INDEX idx_player_game ON euro_players_games (game_id, player_id);
```

---

#### Tabla: `euro_players_ref`
```sql
CREATE TABLE euro_players_ref (
    player_id TEXT PRIMARY KEY,
    player_name TEXT                -- ej: "Juan Carlos Navarro"
);

CREATE UNIQUE INDEX idx_pid ON euro_players_ref (player_id);
```

---

#### Tablas de Referencia Euroliga
```sql
CREATE TABLE euro_teams (
    code TEXT PRIMARY KEY,          -- ej: "FCB"
    name TEXT,                      -- FC Barcelona
    tv_code TEXT,
    primary_color TEXT,
    crest_url TEXT
);

CREATE TABLE euro_players (
    id TEXT PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    club_code TEXT,
    position TEXT,                  -- ej: "G", "F", "C"
    height INTEGER,
    nationality TEXT,
    photo_url TEXT
);

CREATE TABLE euro_standings (
    team_code TEXT PRIMARY KEY,
    team_name TEXT,
    wins INTEGER,
    losses INTEGER,
    points_for INTEGER,
    points_against INTEGER
    -- Overwrite diario (no históricos)
);

CREATE TABLE euro_stats_career (
    player_id TEXT,
    season_code TEXT,
    team_name TEXT,
    games_played INTEGER,
    pts INTEGER, reb INTEGER, ast INTEGER, pir INTEGER,
    is_euroleague BOOLEAN
);
```

---

### 4.2 PostgreSQL: `postgresql://192.168.1.136:5432/proyecto_dos_aros`

**Nota:** Sincronizado desde SQLite (no fuente de verdad). Solo para desarrollo/debugging.

```sql
CREATE TABLE nba_teams (
    id BIGINT PRIMARY KEY,
    full_name TEXT,
    abbreviation TEXT,
    city TEXT
);

CREATE TABLE nba_games (
    game_id TEXT PRIMARY KEY,
    game_date DATE,
    home_team_id BIGINT REFERENCES nba_teams(id),
    visitor_team_id BIGINT,
    home_points INT,
    visitor_points INT,
    season INT
);

CREATE TABLE nba_player_stats (
    id SERIAL PRIMARY KEY,
    game_id TEXT REFERENCES nba_games(game_id),
    player_name TEXT,
    points INT, rebounds INT, assists INT,
    minutes TEXT
);
```

---

## 5. DEPENDENCIAS EXTERNAS

### 5.1 APIs Deportivas

| Paquete | Versión | Método | Endpoints clave |
|---------|---------|--------|-----------------|
| **nba_api** | 1.11.4 | `from nba_api.stats.endpoints import ...` | LeagueGameFinder, PlayByPlayV3, BoxScoreTraditionalV3, LeagueGameLog |
| **nba_api.stats.static.teams** | 1.11.4 | `teams.get_teams()` | Equipo NBA estáticos (cache client-side) |
| **euroleague_api** | Latest | `from euroleague_api import ...` | boxscore_data, play_by_play_data, game_stats, standings |

**notas nba_api:**
- Endpoints con rate-limiting automático (_per_ request ~50ms)
- Cache de headers (si-match etag)
- Season format: `2025-26` (int: 2025, tipo Season)

**Notas euroleague_api:**
- API "semi-oficial" (reverse-engineered de euroleaguetv.net)
- Parámetros: `Competition="E"` (Euroliga), `Season=2024`, `GameCode=1001`
- Coords en sistema propio (-250/1400)

---

### 5.2 IA & LLMs

| Paquete | Versión | Modelo | Host | Latencia |
|---------|---------|--------|------|----------|
| **google-generativeai** | Latest | gemini-2.5-flash-latest | google.genai.GenerativeModel() | ~500ms |
| **ollama** | - | gemma2:2b, llama3 | http://localhost:11434 | ~100ms |

**Configuración Ollama:**
```bash
ollama pull gemma2:2b
ollama pull llama3
ollama serve  # escucha en localhost:11434
```

**Contexto SQL pasado a LLM:**
- Primer 5-10 filas (preview)
- Esquema de tabla completo
- Comentario sobre PK/FK

---

### 5.3 Bases de Datos

| Paquete | Versión | Uso |
|---------|---------|-----|
| **sqlite3** | Built-in | BD local primaria (`/mnt/nba_data/dosaros_local.db`) |
| **psycopg2-binary** | Latest | PostgreSQL Raspberry Pi (192.168.1.136) |
| **supabase-py** | Latest | Supabase (backup, no usado activamente) |

---

### 5.4 Web & HTTP

| Paquete | Versión | Uso |
|---------|---------|-----|
| **requests** | 2.32.5 | Peticiones HTTP (APIs, Telegram bot) |
| **urllib3** | 2.6.3 | HTTP client subyacente |
| **certifi** | 2026.1.4 | SSL certificates |

---

### 5.5 Datos & Procesamiento

| Paquete | Versión | Uso |
|---------|---------|-----|
| **pandas** | 3.0.1 | DataFrames ETL, transformaciones |
| **numpy** | 2.4.2 | Cálculos numéricos |
| **python-dateutil** | 2.9.0.post0 | Parsing/manipulación fechas |
| **pytz** | - | Zonas horarias (si se importa) |

---

### 5.6 Interfaz & Visualización

| Paquete | Uso |
|---------|-----|
| **streamlit** | Framework web UI (todas las tabs) |
| **plotly** (express + graph_objects) | Gráficos interactivos (scatter, heatmap, line) |
| **altair** | Gráficos declarativos vega-lite |
| **PIL/Pillow** | Generación PNG (generar_post_triples) |
| **matplotlib** (opcional) | Fallback visualización |

---

### 5.7 Configuración & Secrets

| Paquete | Uso |
|---------|-----|
| **python-dotenv** | Carga variables `.env` |

**Variables requeridas `.env`:**
```env
# Google API
GOOGLE_API_KEY=AIza...

# Telegram
TELEGRAM_TOKEN=123456:ABC_xyz...
CHAT_ID=987654321

# PostgreSQL (Pi)
DB_HOST=192.168.1.136
DB_PORT=5432
DB_NAME=proyecto_dos_aros
DB_USER=postgres
DB_PASSWORD=<secret>

# Supabase (si se usa)
SUPABASE_URL=https://...supabase.co
SUPABASE_KEY=eyJ...

# Rutas locales
LOCAL_DB=/mnt/nba_data/dosaros_local.db

# Ollama (si local)
OLLAMA_HOST=http://localhost:11434
```

---

## 6. CONVENCIONES DE CÓDIGO

### 6.1 Estándar General

```python
# Importes: orden estrictamente alfabético
import json
import sqlite3
from datetime import datetime, timedelta

import google.generativeai as genai
import pandas as pd
import requests
from euroleague_api.boxscore_data import BoxScoreData

from src.database.db_utils import get_db_connection
from src.utils.mapper import map_euro_to_canonical
```

**Regla:** Std lib → third party → local imports (blank line entre grupos)

---

### 6.2 Handling de Errores

```python
# Logging simple con print; continuamos ejecución
try:
    df = fetch_data_api()
except Exception as e:
    print(f"ERROR in fetch_data_api: {e}")
    df = pd.DataFrame()  # continúa
    
# NO usar sys.exit() en ETL (solo en scripts inicializadores)
```

---

### 6.3 URLs en SQL

**REGLA CRÍTICA:** No usar `YEAR()` en SQL; usar `LIKE` sobre `SEASON_ID`

```sql
-- ✅ CORRECTO
SELECT * FROM nba_games WHERE SEASON_ID LIKE '2025%'

-- ❌ EVITAR
SELECT * FROM nba_games WHERE YEAR(GAME_DATE) = 2025
-- (Algunos drivers SQLite no soportan YEAR())
```

---

### 6.4 Nombres de Función & Variables

```python
# Funciones públicas (sin _): nombre_descriptivo
def run_nba_daily():
def fetch_game_data(season, game_code):
def get_db_connection():

# Funciones privadas (con _)
def _parse_pbp_raw(df):
def _validate_coords(x, y):

# Variables constantes: MAYÚSCULAS
LOCAL_DB = "/mnt/nba_data/dosaros_local.db"
API_DELAY_SEC = 0.5
OLLAMA_HOST = "http://localhost:11434"

# Variables locales: snake_case
game_id = "0021900001"
player_stats = []
```

---

### 6.5 Docstrings

```python
def preguntar_a_gemini(pregunta_usuario: str) -> str:
    """Genera SQL desde pregunta natural usando Gemini Flash Latest.
    
    Args:
        pregunta_usuario: Pregunta en len natural (ej: "Top 3 tiradores de 3s")
        
    Returns:
        SQL plano (sin markdown) optimizado para SQLite3
        
    Raises:
        ValueError: Si GOOGLE_API_KEY no está en .env
    """
    # ...
```

**Estilo:** Google-style docstrings (Args, Returns, Raises)

---

### 6.6 Tipos de Datos (Optional)

```python
# Type hints recomendadas pero no obligatorias
def normalize_euro_coords(x: float, y: float) -> tuple[float, float]:
    x_norm = ((x + 250) / 500) * 100
    y_norm = (y / 1400) * 100
    return x_norm, y_norm

# Union para opcionales
def fetch_game_data(season: int, game_code: int) -> pd.DataFrame | None:
    if not validate_code(game_code):
        return None
    # ...
```

---

### 6.7 Pandas Convention

```python
# Siempre especificar dtype de columnas críticas
df = pd.read_sql(sql, conn)
df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE'])

# Renombrar columnas → lowercase snake_case
df.rename(columns={
    'Player_ID': 'player_id',
    'Points': 'pts',
    'Team': 'team_id'
}, inplace=True)

# Validar no-null críticos
assert not df['player_id'].isna().any(), "player_id no puede ser null"
```

---

### 6.8 Logs & Debugging

```python
# Simple print (no logger config)
print(f"Iniciando carga Euroliga: {n_games} partidos")
print(f"ERROR: No se pudo conectar a BD {LOCAL_DB}")
print(f"Insertados {n_inserted} registros en nba_games")

# Usar f-strings, nunca .format() o %
# Incluir timestamps si es looping
```

---

### 6.9 Consultas SQL

```python
# Formato multi-línea con comas finales
sql = '''
    SELECT 
        GAME_ID, TEAM_ID, GAME_DATE, PTS, WL
    FROM nba_games
    WHERE SEASON_ID = ?
      AND GAME_DATE > ?
    ORDER BY GAME_DATE DESC
    LIMIT 100
'''
conn.execute(sql, (season, since_date))

# Usar ? para placeholders (SQLite standard)
# NO string interpolation → SQL injection risk
```

---

### 6.10 Configuración Streamlit

**Archivo:** `.streamlit/config.toml`

```toml
[theme]
primaryColor = "#88D4AB"      # Mint (acierto)
backgroundColor = "#FFFFFF"  # Blanco
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[client]
showErrorDetails = true
toolbarMode = "minimal"

[server]
maxUploadSize = 200          # MB
port = 8501
```

---

## 7. FLUJO DE DATOS E2E (Real)

### 7.1 Ciclo Diario Estándar (23:00 UTC)

```
┌─ CRONOGRAMA
│   └─ python master_sync.py (cron: 0 23 * * *)
│
├─ FASE 1: Extracción Ayer
│   ├─ get_nba_results_yesterday()
│   │   ├─ API NBA ScoreboardV3 (ayer)
│   │   ├─ SELECT MAX(GAME_DATE) FROM nba_games
│   │   ├─ Comparar contra lastUpdate
│   │   ├─ INSERT nba_games (nuevos)
│   │   └─ return texto "LAL 110-105 BOS, ..."
│   │
│   └─ extract_euro_results_yesterday()
│       ├─ API Euroliga GameStats (últimos códigos)
│       ├─ INSERT euro_games (nuevos)
│       └─ return texto "Barcelona 85-80 Partizan, ..."
│
├─ FASE 2: Generación Insigts
│   ├─ buscar_perlas_nba()
│   │   ├─ SELECT PLAYER_NAME, TEAM_ABBREVIATION, FG3A
│   │   │    FROM nba_players_games
│   │   │    WHERE GAME_DATE = yesterday AND FG3A >= 10
│   │   │    ORDER BY FG3A DESC LIMIT 3
│   │   ├─ generar_post_triples(perlas_list) → PNG
│   │   │   ├─ PIL Image 1080x1080
│   │   │   ├─ Fondo Dos Aros
│   │   │   ├─ Render jugadores top 3
│   │   │   └─ Guardar /tmp/post_instagram.png
│   │   ├─ enviar_grafico("/tmp/post_instagram.png", "Cazadores...")
│   │   │   └─ Telegram API sendPhoto (TELEGRAM_TOKEN, CHAT_ID)
│   │   └─ return list(perlas)
│   │
│   └─ generar_hilo_resultados()
│       ├─ obtener_datos_ultima_noche()
│       │   ├─ SELECT * FROM nba_games WHERE GAME_DATE = yesterday
│       │   └─ SELECT * FROM euro_games WHERE DATE = yesterday
│       ├─ Prompt Gemini Flash Lite:
│       │   "Genera 3 tweets (140 chars c/u) analizando estos 5 partidos..."
│       ├─ Parse respuesta → 3 tweets individuales
│       └─ return str (hilo concatenado)
│
├─ FASE 3: Publicación
│   ├─ enviar_mensaje(reporte_nba)
│   │   └─ Telegram Bot API sendMessage
│   │
│   ├─ enviar_mensaje(reporte_euro)
│   │   └─ Telegram Bot API sendMessage
│   │
│   └─ enviar_mensaje(hilo_resultados)
│       └─ Telegram Bot API sendMessage
│
└─ FIN (logs → stdout)
```

---

### 7.2 Ciclo Ingesta Histórica (Inicial)

```
┌─ Script: python -c "from src.etl.historical_games import fetch_historical_games; fetch_historical_games(1983)"
│
├─ INICIO: Año 1983 → 2026
│   └─ Para season in [1983, ..., 2026]:
│
│       ├─ nba_api.LeagueGameFinder(Season=season)
│       │   ├─ Query: "Todos los equipos, temporada X"
│       │   ├─ Parse → DataFrame (2500-3000 filas/season = 150 partidos × 2 equipos)
│       │   └─ SELECT game_id FROM nba_games WHERE season = X
│       │       (si existe → skip duplicado)
│       │
│       ├─ INSERT BATCH → nba_games (SQLite)
│       │   └─ COMMIT cada 100 inserciones
│       │
│       ├─ sleep(0.5s) respeto API
│       │
│       └─ Repeat para siguiente season
│
└─ Resultado: nba_games completo (1983-2026, ~50MB SQLite)
```

---

### 7.3 Ciclo Sincronización Euroliga (Masivo)

```
┌─ Script: python -c "from src.etl.euro_bulk_load import bulk_load; bulk_load(1, 500)"
│
├─ get_already_loaded_games() → set de game_codes
│   └─ SELECT DISTINCT game_code FROM euro_players_games
│
├─ Para game_code in range(1, 501):
│   ├─ Si game_code ∈ already_set: SKIP
│   │
│   ├─ fetch_game_data(season=2024, game_code=code)
│   │   ├─ euroleague_api.BoxScoreData()
│   │   ├─ get_boxscore_data()
│   │   └─ return pd.DataFrame(columnas API)
│   │
│   ├─ process_and_save(df)
│   │   ├─ Rename columnas 'Player_ID' → 'player_id', etc.
│   │   ├─ Validaciones (pts >= 0, etc.)
│   │   └─ INSERT INTO euro_players_games
│   │
│   ├─ fetch_pbp_data(season=2024, game_code=code)
│   │   ├─ euroleague_api.PlayByPlay()
│   │   ├─ get_game_play_by_play_data()
│   │   └─ return pd.DataFrame(eventos)
│   │
│   ├─ process_pbp(df)
│   │   ├─ map_euro_to_canonical(df, "pbp")
│   │   │   ├─ Mapea columnas API → nombres estándar
│   │   │   └─ Agrega x_norm, y_norm
│   │   ├─ Validar coords en rango
│   │   └─ INSERT INTO euro_pbp (con x_norm, y_norm)
│   │
│   └─ sleep(1.5s) respeto API
│
└─ Resultado: tablas euro_pbp, euro_players_games pobladas
```

---

### 7.4 Ciclo Consulta IA en Streamlit

```
┌─ Usuario en Tab 4 "Analista IA"
│   └─ st.text_input("Haz tu pregunta sobre NBA...")
│       └─ pregunta = "¿Top 10 anotadores de temporada?"
│
├─ obtener_sql_ia(pregunta)
│   ├─ Contexto prompt:
│   │   SELECT * FROM nba_games LIMIT 5;
│   │   SELECT * FROM nba_players_games LIMIT 5;
│   │   [Esquema tablas]
│   │   [Instrucción: "Genera SQL para la pregunta"]
│   │
│   ├─ genai.GenerativeModel("gemini-2.5-flash-latest")
│   │   .generate_content(contexto + pregunta)
│   │
│   ├─ response = "SELECT PLAYER_NAME, SUM(pts) as total_pts ..."
│   │
│   ├─ Limpieza (remover ```sql\n...\n```)
│   │
│   └─ return SQL plano
│
├─ Mostrar SQL en st.code()
│
├─ consultar_db_local(sql)
│   ├─ conn = sqlite3.connect(LOCAL_DB)
│   ├─ df = pd.read_sql(sql, conn)
│   └─ return DataFrame
│
├─ st.dataframe(df)
│   └─ Render tabla interactiva
│
└─ [Usuario ve resultado]
```

---

### 7.5 Ciclo Visualización Tiros Euroliga (Heatmap Normalizado)

```
┌─ Usuario en Tab 5 "Explorador EuroLeague"
│
├─ st.selectbox("Selecciona jugador:")
│   ├─ SELECT DISTINCT player_id FROM euro_pbp
│   ├─ Mostrar droplist
│   └─ player_sel = "P003941"
│
├─ Consulta PBP
│   └─ SELECT x_norm, y_norm, action_type
│       FROM euro_pbp
│       WHERE player_id = 'P003941'
│       AND action_type IN ('FGMade', 'FGMiss')
│
├─ IN-MEMORY processing
│   └─ Crear columna 'Resultado'
│       ├─ Si action_type = 'FGMade' → 'Acierto'
│       └─ Si action_type = 'FGMiss' → 'Fallo'
│
├─ px.scatter(
│   │   x='x_norm', y='y_norm',
│   │   color='Resultado',
│   │   color_discrete_map={
│   │       'Acierto': '#88D4AB',    # Mint
│   │       'Fallo': '#FF8787'       # Coral
│   │   },
│   │   range_x=[0, 100],
│   │   range_y=[0, 100],
│   │   template='plotly_white'
│   │)
│   │+ dibujar_pista_flat()  # Añade líneas cancha
│
└─ [Usuario ve heatmap de tiros]
```

---

## 8. PROBLEMAS CONOCIDOS & MITIGACIONES

### Seguridad 🔴 CRÍTICO

| Problema | Ubicación | Mitigación |
|----------|-----------|-----------|
| API key visible en código | `src/app/test_models.py` | Mover a `.env` + agregar `.gitignore` |
| Credenciales PostgreSQL hardcodeadas | Múltiples archivos app/ | Usar `.env` (ver sección 5.7) |
| Frecuencia cron sin validación | `master_sync.py` | Asumir ejecución controlada |

---

### Inconsistencia Esquema 🟡 IMPORTANTE

| Problema | Mitigación |
|----------|-----------|
| `nba_games` en SQLite vs. PostgreSQL (formato diferente) | SQLite = fuente de verdad (instrucción Copilot oficial) |
| Coordenadas Euroliga sin normalización en BD | Guardar `x_norm`, `y_norm` post-mapper (redundante pero consistente) |

---

### Duplicidad ETL 🟡

| Problema | Estado |
|----------|--------|
| `load_players.py` vs. `load_leaders.py` | Ambos cargan desde JSON. Consolidar en una función |
| Múltiples extractores NBA | **OK** — cada uno tiene propósito distinto (diario, ayer, histórico) |

---

## 9. CHECKLIST PARA AGENTES IA

### Antes de Cualquier Cambio
- [ ] Verificar si afecta `nba_games` (fuente de verdad)
- [ ] Coordenadas Euroliga: ¿están normalizadas? (`src/utils/mapper.py`)
- [ ] ¿La consulta SQL usa `LIKE 'YYYY%'` en SEASON_ID (no `YEAR()`)? 
- [ ] ¿Backup `.env` variables sensibles?

### Deploy a Raspberry Pi
- [ ] `.env` seteado con credenciales PostgreSQL correctas
- [ ] `LOCAL_DB=/mnt/nba_data/dosaros_local.db` accesible
- [ ] Ollama corriendo (`ollama serve` en terminal)
- [ ] Cron job configurado: `0 23 * * * python master_sync.py`

### Testing
- [ ] Ejecutar `scripts/check_syntax.py` antes de push
- [ ] Validar consultas SQL contra SQLite local
- [ ] Verificar coords normalizadas (rango 0-100)

---

## 10. REFERENCIAS RÁPIDAS

### Funciones de Entrada
- **Streamlit:** `streamlit run src/app/main.py`
- **Chat Ollama:** `streamlit run src/app/chat_boloncesto.py`
- **Sync Diario:** `python master_sync.py`

### Importes Críticos
```python
from src.database.db_utils import get_db_connection
from src.utils.mapper import map_euro_to_canonical, normalize_euro_coords
from src.etl.euro_extractor import fetch_game_data, fetch_pbp_data
from automation.bot_manager import enviar_mensaje, enviar_grafico
```

### Consultas Útiles de Debugging
```sql
-- Top 10 anotadores NBA ayer
SELECT PLAYER_NAME, SUM(pts) as total FROM nba_players_games 
WHERE GAME_DATE = DATE('now', '-1 day') GROUP BY 1 ORDER BY 2 DESC LIMIT 10;

-- Partidos Euroliga cargados
SELECT COUNT(*), COUNT(DISTINCT game_id) FROM euro_pbp;

-- Últimas inserciones
SELECT MAX(GAME_DATE) FROM nba_games;
SELECT MAX(date) FROM euro_games;

-- Validar coords normalizadas
SELECT MIN(x_norm), MAX(x_norm), MIN(y_norm), MAX(y_norm) FROM euro_pbp;
```

---

**FIN DEL DOCUMENTO**  
**Actualización:** 21 de marzo de 2026  
**Propósito:** Referencia técnica para agentes IA autónomos (OpenClaw)
