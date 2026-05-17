# 📅 CHANGELOG

Histórico de cambios significativos del proyecto.

---

## [2026-05-17] — Obsidian Knowledge Base + Frontend Recovery

### Added
- **Knowledge Base completo en Obsidian** (`knowledge_base/`)
  - Project Root: README, STATUS, CHANGELOG, ROADMAP
  - Architecture: System Design, Decisions Log (ADRs)
  - Brand: Visual Identity, Avatar System
  - Data: Data Dictionary, ETL Processes
  - Development: Environment Setup, Commands, Debugging Guide
  - Workflows: Daily Automation, Sync Obsidian to Claude
- `PROJECT_OVERVIEW.md` con visión integral del proyecto
- Sistema de sincronización Obsidian → CLAUDE.md (planificado)

### Fixed
- **Catálogo de productos restaurado** (`/productos`)
  - Recuperadas 40 imágenes de productos del commit 51c00de
  - Restaurado `ProductCatalog.tsx` con 5 categorías
  - Navbar actualizada para linkar a `/productos` (no anchor)
- **Push a GitHub habilitado**
  - BFG Repo Cleaner removió `next-swc.win32-x64-msvc.node` (141.5 MB)
  - Historial limpio, force push exitoso

### Changed
- Navbar reorganizada: Productos antes que Comunidad
- Página `/productos` ya no es "en construcción" (es catálogo completo)

---

## [2026-05-16] — Frontend Next.js Completo

### Added
- Landing page con Hero, Highlights, Products, Newsletter, Footer
- Página `/productos` con catálogo de 5 categorías × 6-8 colores
- Página `/contact` con formulario pre-relleno por URL params
- Páginas placeholder: `/analisis`, `/predicciones`, `/comunidad`
- Página experimental `/experimental` con glitch logo
- Integración FormSubmit.co para emails sin backend
- Component library: Navbar, Footer, ProductCatalog, ContactForm
- 40 imágenes de productos en `public/productos/`

### Changed
- Stack visual: paleta DOS AROS oficial aplicada
- Tailwind config con tokens: dos-blue, dos-orange, dos-magenta, etc.

---

## [2026-Q1] — Sistema Avatar Generativo

### Added
- Tabla `teams_metadata` (54 equipos)
- Tablas dimensionales: posturas, vestimentas, decorados, tipos_logo
- `avatar_prompt_generator.py` con 452M combinaciones
- Bot Telegram: comandos `/avatar_*`
- Documentación BRAND.md

---

## [2025-Q4] — Bot Telegram + Cron Diario

### Added
- `bot_consultas.py` con NL→SQL
- `master_sync.py` para cron diario 9:00
- `insight_generator.py` para detectar perlas
- `gemini_social.py` para hilos X/Twitter
- `image_generator.py` para stories 1080×1920

---

## [2025-Q3] — Multi-LLM con Fallback

### Added
- `api_manager.py` con cascade fallback
- Soporte: Gemini, OpenAI, Claude, Groq, DeepSeek, Kimi, Grok
- Sistema de credenciales editable (`credentials_loader.py`)
- Comando `/StatusIA` y `/Sync`

---

## [2025-Q2] — ETL Histórico

### Added
- `historic_pbp_loader.py` con `--liga` y `--bloque`
- Carga histórica NBA 2015 → presente
- Carga histórica EuroLeague E2007 → presente

---

## [2025-Q1] — Inicio del Proyecto

### Added
- Setup inicial: Python + SQLite + Raspberry Pi
- ETL diario NBA + EuroLeague
- Streamlit dashboard básico
- Filosofía: "Datos primero. Contexto después. Opinión al final."

---

## 📝 Template para Nuevas Entradas

```markdown
## [YYYY-MM-DD] — [Título descriptivo]

### Added
- Nueva funcionalidad

### Changed
- Cambios en comportamiento existente

### Fixed
- Bugs resueltos

### Deprecated
- Funciones que serán removidas

### Removed
- Funciones eliminadas

### Security
- Mejoras de seguridad
```

---

**Ver también**: [[ROADMAP|🗺️ Plan futuro]] · [[STATUS|📊 Estado actual]]
