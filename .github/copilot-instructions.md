# Copilot Instruction — Proyecto Dos Aros

Objetivo
- Asistir en desarrollo, mantenimiento y despliegue del proyecto Dos Aros siguiendo la arquitectura y las convenciones del workspace.

Prioridades inmediatas
- Mantener seguridad: eliminar claves embebidas y mover a `.env` ([.env](.env)).
- Asegurar rutas: la mayoría de scripts asumen DB en `/mnt/nba_data/dosaros_local.db`.
- Evitar duplicados: consolidar extractores ETL similares en `src/etl/`.

Entorno
- Python según [requirements.txt](requirements.txt).
- Streamlit: entrada en [src/app/main.py](src/app/main.py).
- Supabase: configuración en [src/database/supabase_client.py](src/database/supabase_client.py).
- PostgreSQL local (Raspberry Pi) en `src/app/inicializar_db.py` / `src/app/init_local_db.py`.

Cómo actuar (rules of engagement)
1. Priorizar cambios que no rompan la ingesta histórica (SQLite).
2. Documentar en `IMPLEMENTATION_DOCS.md` y `IMPLEMENTATION_SUMMARY.md` cualquier cambio en APIs públicas.
3. No subir claves ni tokens en el repo; sugerir `.env` y rotación.
4. Mantener compatibilidad con la estructura de tablas existente (ver `src/database/init_local_db.py` y `src/database/init_db.py`).

Comandos útiles
- Comprobar sintaxis: `python scripts/check_syntax.py` ([scripts/check_syntax.py](scripts/check_syntax.py)).
- Inicializar SQLite local: ejecutar [`src/database/init_local_db.init_db`](src/database/init_local_db.py).
- Crear tablas en Pi (Postgres): ejecutar [`src/app/inicializar_db.crear_tablas`](src/app/inicializar_db.py).
- Ejecutar Streamlit: `streamlit run src/app/main.py` ([src/app/main.py](src/app/main.py)).

Seguridad y limpieza rápida
- Eliminar la API key incrustada en [`src/app/test_models.py`](src/app/test_models.py).
- Asegurar que `requirements.txt` incluya `psycopg2-binary` en versión concreta.
- Añadir `.env` a `.gitignore` y comprobar `.gitignore` (actualizar caracteres corruptos).

Estilo y convenciones
- Logs simples con print; errores capturados y continuamos ETL.
- Evitar YEAR() en SQL: usar `LIKE` sobre `SEASON_ID` como indica la app (ver [`src/app/analista_ia.preguntar_a_gemini`](src/app/analista_ia.py) y [`src/app/main.obtener_sql_ia`](src/app/main.py)).
- Mantener rutas absolutas configurables mediante variables de entorno.

Tareas recomendadas (priorizadas)
1. Mover claves a `.env` y borrar claves en código (`src/app/test_models.py`) — alta.
2. Corregir `.gitignore` (caracteres corruptos) — alta.
3. Añadir manejo de configuración para `DB_PATH` (variable, no hardcode) — media.
4. Unificar extractores duplicados en `src/etl/` — media.
5. Añadir tests básicos de integración para ETL y pruebas de consulta SQL (usando una DB temporal) — baja.

Referencias principales del workspace
- Documentos: [project_context.md](project_context.md), [IMPLEMENTATION_DOCS.md](IMPLEMENTATION_DOCS.md), [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md), [README.md](README.md)
- Entradas app: [`src.app.main.obtener_sql_ia`](src/app/main.py), [`src.app.main.consultar_db_local`](src/app/main.py), [src/app/main.py](src/app/main.py)
- IA helpers: [`src.app.analista_ia.preguntar_a_gemini`](src/app/analista_ia.py), [`src.app.analista_ia.ejecutar_en_hdd`](src/app/analista_ia.py), [`src.app.chat_boloncesto.generar_sql`](src/app/chat_boloncesto.py), [`src.app.consulta_ia.preguntar_a_nba`](src/app/consulta_ia.py)
- Database: [`src.database.supabase_client.get_supabase_client`](src/database/supabase_client.py), [`src.database.init_local_db.init_db`](src/database/init_local_db.py), [`src.database.init_db.init_tables`](src/database/init_db.py)
- ETL clave: [`src.etl.nba_extractor.run_nba_teams_sync`](src/etl/nba_extractor.py), [`src.etl.nba_games_extractor.sync_nba_games`](src/etl/nba_games_extractor.py), [`src.etl.nba_player_extractor.sync_player_stats`](src/etl/nba_player_extractor.py), [`src.etl.pbp_extractor.descargar_pbp_por_temporada`](src/etl/pbp_extractor.py), [`src.etl.jugadores_extractor.descargar_boxscores_jugadores`](src/etl/jugadores_extractor.py), [`src.etl.historical_games.fetch_historical_games`](src/etl/historical_games.py), [`src/etl/euro_extractor.get_and_save_game`](src/etl/euro_extractor.py)
- Utilidades y scripts: [scripts/check_syntax.py](scripts/check_syntax.py), [.streamlit/config.toml](.streamlit/config.toml)

# Reglas de Coordenadas (Crucial)
- Estándar Dos Aros: Todas las coordenadas deben normalizarse a escala 0-100 usando `src.utils.mapper.map_euro_to_canonical`.
- Visualización: El Dashboard usa `plotly_white` y colores `#88D4AB` (Acierto) y `#FF8787` (Fallo).
- Rutas: La DB local en la Pi es la fuente de verdad absoluta para PBP.

# Reglas Técnicas Actualizadas
- **Normalización**: Las coordenadas de Euroliga DEBEN pasar por `src/utils/mapper.py` para convertirse a escala 0-100 antes de guardarse o visualizarse.
- **UI Standard**: El dashboard usa `plotly_white` con colores Mint (`#88D4AB`) para aciertos y Coral (`#FF8787`) para fallos.
- **Data Source**: La tabla `euro_pbp` es la fuente principal para mapas de calor y volumen de tiro.

# Estándares Visuales y de Datos
- Coordenadas: Usar siempre `x_norm` e `y_norm` (escala 0-100).
- Colores: Acierto: `#88D4AB` (Mint), Fallo: `#FF8787` (Coral).
- Tema: Plotly White / Streamlit Light.

Fin.