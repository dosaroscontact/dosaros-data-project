# 📖 DOS AROS — Overview

**Proyecto**: Análisis comparativo de baloncesto NBA + EuroLeague
**Filosofía**: *"Datos primero. Contexto después. Opinión al final."*
**Mantenedor**: @DosAros (dosaroscontact@gmail.com)
**Repo**: https://github.com/dosaroscontact/dosaros-data-project

---

## 🎯 Objetivo

Asistir en el desarrollo y mantenimiento de DOS AROS, un sistema de investigación de baloncesto comparado (NBA y EuroLeague).

**Principios rectores**:
1. **Datos primero**: Cualquier afirmación se apoya en SQL verificable
2. **Contexto después**: Comparación NBA ↔ EuroLeague, históricos
3. **Opinión al final**: Solo cuando los datos lo justifican
4. **Sostenibilidad**: Soluciones de bajo coste y mantenimiento
5. **Local-first**: SQLite Pi es source of truth; Supabase solo para serving

---

## 🏗️ Stack Tecnológico

### Backend
- **Lenguaje**: Python 3.10+
- **BD warehouse**: SQLite en Raspberry Pi (`/mnt/nba_data/dosaros_local.db`)
- **BD serving**: Supabase PostgreSQL (solo agregados)
- **APIs**: nba_api, euroleague_api, Telegram Bot API
- **LLMs**: Gemini (primario), OpenAI, Claude, Groq, DeepSeek, Kimi, Grok, Manus

### Frontend
- **Framework**: Next.js 15 (App Router)
- **Lenguaje**: TypeScript
- **Estilos**: Tailwind CSS
- **Animaciones**: Framer Motion
- **Formularios**: FormSubmit.co (sin backend)

### Infraestructura
- **Desarrollo**: Windows 11 (C:\Users\rover\dosaros-data-project\)
- **Producción**: Raspberry Pi 4 (192.168.1.136)
- **Remoto**: GitHub (rama main)

---

## 📁 Componentes Clave

| Componente | Función |
|------------|---------|
| `master_sync.py` | Orquestador cron 9:00 — extrae, analiza, envía a Telegram |
| `src/app/main.py` | Streamlit dashboard |
| `src/utils/api_manager.py` | Router LLM con fallback (10+ APIs) |
| `src/automation/bot_consultas.py` | Bot Telegram (NL→SQL + /video + /avatar_*) |
| `src/etl/*` | ETL NBA + EuroLeague |
| `src/processors/*` | Insights, imágenes, social, video |
| `app/` | Frontend Next.js (landing + catálogo + contacto) |

---

## 🌐 Navegación

- **Estado actual del proyecto**: [[STATUS]]
- **Setup de entornos**: [[../Development/Environment Setup]]
- **Comandos frecuentes**: [[../Development/Commands]]
- **Arquitectura**: [[../Architecture/System Design]]
- **Brand**: [[../Brand/Visual Identity]]

---

**Última actualización**: 2026-05-17
