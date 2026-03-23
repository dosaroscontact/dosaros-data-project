# Dos Aros — Daily Briefing

_Actualizar este archivo al inicio o fin de cada jornada._

---

## Estado general del proyecto
<!-- Una línea: en qué fase estamos y cuál es el foco actual -->
Fase: Ingesta masiva EuroLeague + análisis comparativo NBA vs Euro

## Última sesión
<!-- Fecha y resumen de lo que se hizo -->
- **Fecha:** 2026-03-23
- **Hecho:** Renombrado final de avatars con esquema por código de equipo y reorganización en subdirectorios `posts/` y `presenter/`

## En progreso ahora
<!-- Máx. 3 cosas activas -->
- [ ] Ejecutar primera carga histórica: `python src/etl/historic_pbp_loader.py --liga ambas --bloque 2023-2025`
- [ ] Análisis: Comparativa mapas de tiro NBA vs EuroLeague

## Bloqueantes / Problemas abiertos
<!-- Cosas que impiden avanzar o requieren decisión -->
- (ninguno)

## Próximos pasos (ordenados por prioridad)
<!-- Lo que toca hacer en las próximas 1-3 sesiones -->
1. Lanzar `historic_pbp_loader.py --liga ambas --bloque 2023-2025` en la Raspberry Pi
2. Primer análisis comparativo de shot charts
3. Consolidar extractores ETL duplicados en `src/etl/`

## Decisiones tomadas (log)
<!-- Registro de decisiones de diseño para no repetir debates -->
| Fecha | Decisión |
|---|---|
| 2026-03-23 | CLAUDE.md como fuente de contexto para Claude Code |
| — | Coordenadas Euro normalizadas a 0-100 via `mapper.py` antes de guardar |
| — | SQLite en Raspberry Pi es la fuente de verdad (no Supabase) |
| — | SQL usa `SEASON_ID LIKE` en vez de `YEAR()` |

## Completado
- [x] Configuración entorno local (Python, VS Code, Git)
- [x] Conexión base de datos (Supabase + .env)
- [x] ETL: Sincronización equipos NBA
- [x] ETL EuroLeague: Extractor con normalización de coordenadas
- [x] Ingesta: Primer bloque 100 partidos (54k eventos)
- [x] Dashboard Streamlit v1.0 (Light & Flat, Shot Charts)
- [x] CLAUDE.md con arquitectura y guía de desarrollo
- [x] ETL: `historic_pbp_loader.py` — carga histórica masiva PBP NBA + Euroliga (args `--liga`, `--bloque`)
- [x] Assets: 27 avatars renombrados con esquema final (código equipo NBA/Euro) y organizados en `avatars/`, `avatars/posts/`, `avatars/presenter/`
