# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Dos Aros** is a basketball data project focused on comparative analysis of NBA and EuroLeague. The philosophy: *"Datos primero. Contexto después. Opinión al final."*

## Common Commands

```bash
# Run the Streamlit app
streamlit run src/app/main.py

# Check syntax across the project
python scripts/check_syntax.py

# Initialize local SQLite DB
python -c "from src.database.init_local_db import init_db; init_db()"

# Create tables on Raspberry Pi (PostgreSQL)
python -c "from src.app.inicializar_db import crear_tablas; crear_tablas()"
```

## Architecture

### Data Flow
```
APIs (nba_api, euroleague_api) → ETL (src/etl/) → SQLite on Raspberry Pi → Transform → Supabase → Streamlit App
```

### Storage Tiers
1. **Primary warehouse**: SQLite on Raspberry Pi (`/mnt/nba_data/dosaros_local.db`) — full historical data, source of truth for PBP
2. **Serving layer**: Supabase PostgreSQL — aggregated, visualization-ready subsets
3. **Local dev**: Code only, no critical data

### Key Modules
- `src/app/main.py` — Streamlit entry point; tabs for analysis and natural language SQL queries
- `src/utils/api_manager.py` — Unified interface for 10+ LLM/image/audio APIs with fallback support
- `src/etl/` — All data extraction; NBA and EuroLeague extractors are separate but similar (consolidation pending)
- `src/database/` — SQLite and Supabase connection utilities, schema creation
- `src/processors/insight_generator.py` — AI-driven insight generation
- `src/prompts/` — System personas and content generation for social media

### AI/LLM Layer
Google Gemini is the primary model; OpenAI, Claude, Groq, DeepSeek, Kimi, Grok are fallbacks. All routed through `src/utils/api_manager.py`. SQL generation for basketball queries happens in `src/app/analista_ia.py` and `src/app/chat_boloncesto.py`.

## Critical Rules

### SQL
- **Never use `YEAR()` in SQL** — use `LIKE` on `SEASON_ID` instead (e.g., `SEASON_ID LIKE '2024%'`)
- Maintain compatibility with existing table schemas in `src/database/init_local_db.py` and `src/database/init_db.py`

### Coordinates (EuroLeague)
- All Euro shot coordinates **must** be normalized to 0–100 scale via `src.utils.mapper.map_euro_to_canonical` before storing or visualizing
- Always use `x_norm` and `y_norm` fields

### Visualization Standards
- Theme: `plotly_white`
- Makes: `#88D4AB` (Mint), Misses: `#FF8787` (Coral)

### Code Style
- Code and comments are written in **Spanish** (technical terms in English)
- Use `print` for logging; catch errors and continue ETL rather than aborting
- Use environment variables for all paths and keys (never hardcode); `DB_PATH` for local SQLite

## Environment Setup

Copy `.env.example` to `.env` and fill in credentials. Key variables:
- `LOCAL_DB` — path to SQLite file
- `SUPABASE_URL`, `SUPABASE_KEY` — Supabase connection
- LLM keys: `GEMINI_API_KEY`, `OPENAI_API_KEY`, `CLAUDE_API_KEY`, etc.
- `TELEGRAM_BOT_TOKEN` — automation notifications
