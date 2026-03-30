# Implementación: firmas y docstrings detalladas

**Fecha:** 2026-03-08

Este documento contiene firmas y descripciones extraídas del código fuente en `src/`.

- `get_and_save_game(season: int, game_code: int)` — `src/etl/euro_extractor.py`
  - Docstring: """Extrae, limpia y guarda un partido completo."""
  - Descripción: usa `euroleague_api.Boxscore` y `PlayByPlay` para obtener boxscore y PBP, mapea columnas y persiste en `euro_players_games`, `euro_pbp`, `euro_games` en el fichero SQLite configurado.

- `init_tables()` — `src/database/init_db.py`
  - Docstring: (no presente)
  - Descripción: crea las tablas `euro_games`, `euro_players_games`, `euro_pbp` y los índices asociados en el fichero SQLite definido en `DB_PATH`.

- `check_url(url)` — `src/etl/debug_euro.py`
  - Docstring: (no presente)
  - Descripción: hace una petición HTTP simple a una URL de la API Euroliga y devuelve el `status_code`.

- `preguntar_a_gemini(pregunta_usuario)` — `src/app/analista_ia.py`
  - Docstring: (no presente)
  - Descripción: construye un prompt con contexto SQL y usa `google.genai` para generar SQL; devuelve SQL limpio o mensaje de error.

- `ejecutar_en_hdd(sql)` — `src/app/analista_ia.py`
  - Docstring: (no presente)
  - Descripción: ejecuta la consulta SQL sobre la base SQLite en `DB_PATH` y devuelve un `pandas.DataFrame` o un mensaje de error.

- `init_db()` — `src/database/init_local_db.py`
  - Docstring: (no presente)
  - Descripción: inicializa la tabla `nba_games` y crea índices (`idx_season`, `idx_team`, `idx_date`) en el DB local (`DB_PATH`).

- `generar_sql(pregunta)` — `src/app/chat_boloncesto.py`
  - Docstring: (no presente)
  - Descripción: usa `ollama.chat` para convertir lenguaje natural en SQL, limpiando bloques de código markdown.

- `fetch_historical_games(start_year=1983)` — `src/etl/historical_games.py`
  - Docstring: (no presente)
  - Descripción: itera por temporadas, utiliza `leaguegamefinder` para descargar partidos y los inserta en `nba_games` en SQLite con control de pausas.

- `get_supabase_client() -> Client` — `src/database/supabase_client.py`
  - Docstring: """Crea y devuelve una instancia del cliente de Supabase."""
  - Descripción: lee `SUPABASE_URL` y `SUPABASE_KEY` desde `.env` y devuelve `create_client(url, key)`; lanza `ValueError` si faltan credenciales.

- `preguntar_a_nba(pregunta)` — `src/app/consulta_ia.py`
  - Docstring: (no presente)
  - Descripción: usa `ollama` para generar SQL dado el esquema y ejecuta la consulta contra PostgreSQL (configurada en `DB_CONFIG`), devolviendo un `pandas.DataFrame`.

- `descargar_boxscores_jugadores(ano_inicio, ano_fin)` — `src/etl/jugadores_extractor.py`
  - Docstring: (no presente)
  - Descripción: usa `leaguegamelog` para descargar logs de jugadores por temporada y guarda en `nba_players_games` en SQLite.

- `descargar_periodo_historico(ano_inicio, ano_fin)` — `src/app/historial_partidos.py`
  - Docstring: (no presente)
  - Descripción: descarga temporadas completas con `leaguegamefinder` y añade registros a `nba_games` en SQLite.

- `sync_stats()` — `src/etl/local_nba_sync.py`
  - Docstring: (no presente)
  - Descripción: (requiere `DB_CONFIG`) extrae `game_id` de `nba_games`, solicita boxscore tradicional (v2) y guarda `nba_player_stats` en PostgreSQL.

- `crear_tablas()` — `src/app/inicializar_db.py`
  - Docstring: (no presente)
  - Descripción: crea tablas maestras (`nba_teams`, `nba_games`, `nba_player_stats`) en la PostgreSQL configurada (Pi).

- `run_nba_teams_sync()` — `src/etl/nba_extractor.py`
  - Docstring: (no presente)
  - Descripción: obtiene equipos con `nba_api` y hace `upsert` en la tabla `nba_teams` de Supabase, asignando `conference`.

- `sync_nba_games(season_id='2025-26')` — `src/etl/nba_games_extractor.py`
  - Docstring: (no presente)
  - Descripción: descarga partidos para la temporada indicada, filtra por equipos válidos y hace `upsert` en `nba_games` en Supabase.

- `obtener_sql_ia(pregunta)` — `src/app/main.py`
  - Docstring: (no presente)
  - Descripción: prompt preconfigurado para `google.genai` que devuelve SQL (limpia bloque de código) para ejecutar en la DB local.

- `consultar_db_local(sql)` — `src/app/main.py`
  - Docstring: (no presente)
  - Descripción: ejecuta consulta SQL contra `LOCAL_DB` y devuelve `pandas.DataFrame` o mensaje de error.

- `load_data(table_name, season_filter=None)` — `src/app/main.py`
  - Docstring: (no presente)
  - Descripción: carga datos desde Supabase (usa `get_supabase_client`) y está cacheado con `@st.cache_data`.

- `sync_player_stats(limit_games=200)` — `src/etl/nba_player_extractor.py`
  - Docstring: (no presente)
  - Descripción: extrae estadísticas de jugadores usando `boxscoretraditionalv3` y hace `upsert` en `nba_player_stats` en Supabase.

- `descargar_pbp_por_temporada(season_id_prefix)` — `src/etl/pbp_extractor.py`
  - Docstring: (no presente)
  - Descripción: descarga play-by-play usando `playbyplayv3` y persiste en `nba_pbp` en SQLite, manejando pausas y excepciones.


---

Archivo generado automáticamente a partir del análisis de `src/`.
