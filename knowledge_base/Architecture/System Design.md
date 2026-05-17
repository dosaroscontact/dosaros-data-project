# 🎯 System Design

**Filosofía**: Local-first. Pi como warehouse. Cloud solo para serving.

---

## 🏗️ Arquitectura de Alto Nivel

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

## 📐 Patrones Arquitectónicos

### 1. Local-First Data
- **Source of Truth**: SQLite en Pi (`/mnt/nba_data/dosaros_local.db`)
- **Serving Layer**: Supabase PostgreSQL (solo agregados visualizables)
- **Local Dev**: BD aparte para testing

**Justificación**: Coste bajo, latencia baja, control total.

### 2. ETL Incremental
- **Diario**: Solo resultados del día anterior
- **Histórico**: Bajo demanda con `--bloque`
- **Idempotente**: `INSERT OR IGNORE` para evitar duplicados

### 3. Cascade Fallback (LLMs)
- **Primario**: Gemini (Google, mejor relación coste/calidad)
- **Fallbacks**: OpenAI → Claude → Groq → DeepSeek → Kimi → Grok
- **Router**: `src/utils/api_manager.py`

### 4. Bot-First UX
- Usuario interactúa vía Telegram (no requiere UI compleja)
- Bot acepta NL → SQL → resultado → opción de publicar

---

## 🔄 Flujo de Datos Típico

### Cron Diario (9:00)
1. `master_sync.py` ejecuta:
2. Extrae resultados NBA de ayer
3. Extrae resultados EuroLeague de ayer
4. Inserta en SQLite Pi
5. Genera resumen → Telegram
6. Detecta perlas (actuaciones destacadas) con IA
7. Genera hilo X/Twitter (5-6 tweets)
8. Genera story imagen 1080×1920

### Consulta Bot Telegram
1. Usuario pregunta en español
2. `analista_ia.py` traduce a SQL
3. SQL ejecuta sobre SQLite
4. Resultados formateados a tabla
5. Si usuario confirma: genera tweet + imagen

---

## 🔗 Componentes y Responsabilidades

| Capa | Componente | Responsabilidad |
|------|------------|-----------------|
| **Ingestion** | `src/etl/*` | Extraer datos de APIs externas |
| **Storage** | SQLite Pi | Persistir histórico completo |
| **Processing** | `src/processors/*` | Transformar datos en insights |
| **Intelligence** | `src/utils/api_manager.py` | Router de LLMs |
| **Delivery** | `src/automation/*` | Telegram bot + envío de mensajes |
| **Presentation** | `app/` (Next.js) | Frontend web |

---

## 📊 Decisiones Clave

Ver detalles completos en [[Decisions Log|📝 ADRs]].

| Decisión | Razón |
|----------|-------|
| SQLite vs PostgreSQL | Coste cero, suficiente para escala actual |
| Pi vs Cloud | Coste mínimo, control total |
| Telegram vs custom app | Adopción inmediata, no requiere instalación |
| Multi-LLM | Resilience + coste optimization |
| FormSubmit.co vs custom backend | Cero infraestructura para frontend |

---

## 🔗 Referencias

- [[Database Schema|🗄️ Schema completo]]
- [[API Stack|🔌 APIs y LLM providers]]
- [[Decisions Log|📝 Architecture Decision Records]]
- [[../Data/ETL Processes|⚙️ Procesos ETL]]
