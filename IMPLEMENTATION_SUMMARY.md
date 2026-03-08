# Estado de implementación — Proyecto dosaros-data-project

**Fecha:** 2026-03-08

Resumen compacto del código y artefactos presentes en el workspace a día de hoy.

**Raíz del proyecto**
- [project_context.md](project_context.md) — contexto y arquitectura del proyecto.
- [task.md](task.md) — roadmap y tareas.
- [README.md](README.md) — información general del proyecto.
- [requirements.txt](requirements.txt) — dependencias del proyecto.

**Paquete `src/`**
- [src/__init__.py](src/__init__.py)

**App (UI / IA / integración)**
- [src/app/main.py](src/app/main.py) — app Streamlit; integración con IA y funciones para consultas y sincronización.
- [src/app/analista_ia.py](src/app/analista_ia.py) — interfaces para consultas a modelos (p. ej. Gemini/Ollama).
- [src/app/chat_boloncesto.py](src/app/chat_boloncesto.py) — chat y generación de SQL mediante IA.
- [src/app/consulta_ia.py](src/app/consulta_ia.py) — funciones auxiliares para preguntar a modelos locales/remotos.
- [src/app/inicializar_db.py](src/app/inicializar_db.py) — creación de tablas en PostgreSQL/entorno Pi.
- [src/app/init_local_db.py](src/app/init_local_db.py) — alternativa para inicializar BD local.
- [src/app/test_models.py](src/app/test_models.py) — pruebas de integración con modelos GenAI.
- [src/app/components/](src/app/components/) — componentes UI (Streamlit).

**Database (cliente y esquemas)**
- [src/database/supabase_client.py](src/database/supabase_client.py) — wrapper para Supabase.
- [src/database/init_local_db.py](src/database/init_local_db.py) — inicialización de SQLite local.
- [src/database/init_db.py](src/database/init_db.py) — creación de esquemas/tabla Euroliga en SQLite.

**ETL (NBA y Euroliga)**
- [src/etl/nba_extractor.py](src/etl/nba_extractor.py) — sincronización de equipos NBA con Supabase.
- [src/etl/nba_games_extractor.py](src/etl/nba_games_extractor.py) — sincronización de partidos NBA.
- [src/etl/nba_player_extractor.py](src/etl/nba_player_extractor.py) — extracción de estadísticas de jugadores.
- [src/etl/pbp_extractor.py](src/etl/pbp_extractor.py) — descarga de play-by-play con `nba_api`.
- [src/etl/jugadores_extractor.py](src/etl/jugadores_extractor.py) — extracción masiva de boxscores a SQLite.
- [src/etl/historical_games.py](src/etl/historical_games.py) — carga histórica local a SQLite.
- [src/etl/local_nba_sync.py](src/etl/local_nba_sync.py) — sincronización local de estadísticas.

**Euroliga / Euro**
- [src/etl/euro_extractor.py](src/etl/euro_extractor.py) — extracción y guardado de partidos de Euroliga en SQLite.
- [src/etl/test_euro_load.py](src/etl/test_euro_load.py) — script de prueba para descargar partidos Euroliga.
- [src/etl/quick_fix.py](src/etl/quick_fix.py) — pruebas y experimentos contra endpoints Euroliga.
- [src/etl/debug_euro.py](src/etl/debug_euro.py) — comprobaciones y validación de URLs/endpoints.

**Otros ficheros útiles**
- Archivos de configuración: `.env` (credenciales), `.streamlit/config.toml`.

**Estado funcional general**
- ETL NBA: implementado para extracción de equipos, partidos y estadísticas y subida a Supabase.
- ETL histórico local: scripts para poblar SQLite con datos históricos.
- Euroliga: extractor y pruebas para guardar boxscores y PBP en SQLite.
- Base local: esquemas y scripts de inicialización (SQLite).
- Supabase: cliente y uso desde ETL y la app.
- App Streamlit: visualización básica e integración con IA para generación de SQL y consultas.

Si quieres, puedo:
- Añadir más detalles por fichero (resumen de funciones públicas).
- Generar un README más extenso a partir de este resumen.
- Ejecutar tests o comprobar dependencias en `requirements.txt`.

Archivo generado automáticamente por la herramienta de resumen.
\
## Resumen ampliado por fichero

**src/app/main.py**
- Funciones principales:
	- `obtener_sql_ia(pregunta)`: usa `google.genai` para traducir NL a SQL (quita bloques ```sql```).
	- `consultar_db_local(sql)`: ejecuta una consulta SQL sobre la base SQLite local (`/mnt/nba_data/dosaros_local.db`) y devuelve un `DataFrame` o un mensaje de error.
	- `load_data(table_name, season_filter=None)`: carga tablas desde Supabase con caché de Streamlit.
- Notas: App Streamlit con pestañas para resultados, análisis y un analista IA que traduce preguntas a SQL y ejecuta en la DB local.

**src/app/analista_ia.py**
- Funciones principales:
	- `preguntar_a_gemini(pregunta_usuario)`: genera SQL usando `google.genai` con prompts específicos para `nba_games`.
	- `ejecutar_en_hdd(sql)`: ejecuta SQL contra el fichero SQLite del HDD.
- Notas: incluye un `__main__` de laboratorio para pruebas locales.

**src/app/chat_boloncesto.py**
- Funciones principales:
	- `generar_sql(pregunta)`: usa `ollama` para generar SQL a partir de lenguaje natural, limpiando bloques de código.
- Notas: componente Streamlit para chat que traduce preguntas y ejecuta la consulta en una DB remota (Pi) vía `psycopg2`.

**src/app/consulta_ia.py**
- Funciones principales:
	- `preguntar_a_nba(pregunta)`: genera SQL con `ollama`, ejecuta en PostgreSQL (Pi) y devuelve un `DataFrame`.

**src/app/inicializar_db.py / src/app/init_local_db.py**
- Scripts para crear las tablas maestras en PostgreSQL (Pi) y/o inicializar la estructura local; incluyen `nba_teams`, `nba_games`, `nba_player_stats`.

**src/app/test_models.py**
- Script mínimo que lista modelos disponibles con `google.genai` (contiene clave en texto, revisar seguridad).

**src/database/supabase_client.py**
- Funciones principales:
	- `get_supabase_client() -> Client`: crea un cliente Supabase leyendo `SUPABASE_URL` y `SUPABASE_KEY` de `.env`.
- Notas: lanza `ValueError` si faltan credenciales.

**src/database/init_local_db.py / src/database/init_db.py**
- Scripts para crear tablas SQLite locales: `nba_games`, índices y tablas `euro_games`, `euro_players_games`, `euro_pbp` para Euroliga.

**src/etl/nba_extractor.py**
- Funciones principales:
	- `run_nba_teams_sync()`: sincroniza equipos NBA desde `nba_api` a Supabase, añade conferencia.

**src/etl/nba_games_extractor.py**
- Funciones principales:
	- `sync_nba_games(season_id='2025-26')`: obtiene partidos con `leaguegamefinder`, filtra por equipos válidos y `upsert` en Supabase.

**src/etl/nba_player_extractor.py**
- Funciones principales:
	- `sync_player_stats(limit_games=200)`: extrae boxscores (V3) y sube estadísticas de jugadores a Supabase (`nba_player_stats`).

**src/etl/nba_games_extractor.py**
- Ya indicado arriba (sincronización de partidos).

**src/etl/nba_player_extractor.py**
- Ya indicado arriba (sincronización de estadísticas de jugadores).

**src/etl/nba_games_extractor.py**
- (Duplicado en el repo; ver arriba).

**src/etl/nba_games_extractor.py**
- (Nota: hay módulos que comparten responsabilidades; revisar duplicados si es necesario.)

**src/etl/nba_games_extractor.py**
- (El extractor principal de partidos ya documentado.)

**src/etl/nba_games_extractor.py**
- (Evita repetición — contenido en `n_b_a_games_extractor.py`.)

**src/etl/nba_games_extractor.py**
- (Fin de notas de repetición.)

**src/etl/nba_games_extractor.py**
- (Por favor ignora estas líneas duplicadas; hay repetición en el resumen automática.)

**src/etl/pbp_extractor.py**
- Funciones principales:
	- `descargar_pbp_por_temporada(season_id_prefix)`: usa `playbyplayv3` para descargar PBP y guardarlo en `nba_pbp` en SQLite con gestión de pausas y reintentos.

**src/etl/jugadores_extractor.py**
- Funciones principales:
	- `descargar_boxscores_jugadores(ano_inicio, ano_fin)`: descarga logs por temporada y almacena en `nba_players_games` en SQLite.

**src/etl/historical_games.py**
- Funciones principales:
	- `fetch_historical_games(start_year=1983)`: descarga por temporada con `leaguegamefinder` y volcado en SQLite, con limpieza y pausas.

**src/etl/euro_extractor.py**
- Funciones principales:
	- `get_and_save_game(season: int, game_code: int)`: extrae boxscore y play-by-play con `euroleague_api`, mapea columnas y persiste en tablas `euro_players_games`, `euro_pbp`, `euro_games`.
- Notas: incluye manejo de prefijo `E` en `game_id` y persistencia atómica en SQLite.

**src/etl/test_euro_load.py / src/etl/quick_fix.py / src/etl/debug_euro.py**
- Scripts de prueba y debug: probar URLs del API Euroliga, descargar juegos de prueba y validar formatos JSON/boxscore/PBP.

---

**Observaciones y riesgos técnicos**
- Algunas claves API aparecen embebidas en scripts (`src/app/test_models.py`); conviene moverlas a `.env` y borrarlas del repositorio.
- Hay cierta duplicación o solapamiento en módulos ETL; revisar responsabilidades y unificar extractores si procede.
- Muchos scripts asumen la ruta `"/mnt/nba_data/dosaros_local.db"` (Raspberry Pi). Documentar este requisito y proporcionar alternativa para entornos Windows/CI.

Si quieres, hago una pasada adicional para:
- Generar un resumen con la lista de funciones públicas en cada fichero y sus firmas exactas.
- Fusionar este contenido en el `README.md`.
- Ejecutar pruebas unitarias o de integración si hay test suite.

## Firmas de funciones (resumen rápido)

- `get_and_save_game(season: int, game_code: int)` — `src/etl/euro_extractor.py`
- `init_tables()` — `src/database/init_db.py`
- `check_url(url)` — `src/etl/debug_euro.py`
- `preguntar_a_gemini(pregunta_usuario)` — `src/app/analista_ia.py`
- `ejecutar_en_hdd(sql)` — `src/app/analista_ia.py`
- `init_db()` — `src/database/init_local_db.py`
- `generar_sql(pregunta)` — `src/app/chat_boloncesto.py`
- `fetch_historical_games(start_year=1983)` — `src/etl/historical_games.py`
- `get_supabase_client() -> Client` — `src/database/supabase_client.py`
- `preguntar_a_nba(pregunta)` — `src/app/consulta_ia.py`
- `descargar_boxscores_jugadores(ano_inicio, ano_fin)` — `src/etl/jugadores_extractor.py`
- `descargar_periodo_historico(ano_inicio, ano_fin)` — `src/app/historial_partidos.py`
- `sync_stats()` — `src/etl/local_nba_sync.py`
- `crear_tablas()` — `src/app/inicializar_db.py`
- `run_nba_teams_sync()` — `src/etl/nba_extractor.py`
- `sync_nba_games(season_id='2025-26')` — `src/etl/nba_games_extractor.py`
- `obtener_sql_ia(pregunta)` — `src/app/main.py`
- `consultar_db_local(sql)` — `src/app/main.py`
- `load_data(table_name, season_filter=None)` — `src/app/main.py`
- `sync_player_stats(limit_games=200)` — `src/etl/nba_player_extractor.py`
- `descargar_pbp_por_temporada(season_id_prefix)` — `src/etl/pbp_extractor.py`
