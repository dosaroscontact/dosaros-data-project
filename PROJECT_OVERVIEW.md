# DOS AROS — Visión Integral del Proyecto

**Última actualización**: 2026-05-17  
**Estado**: Activo en desarrollo (Windows + Pi + GitHub)

---

## 📋 Tabla de Contenidos
1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Entornos](#entornos)
3. [Estructura de Carpetas](#estructura-de-carpetas)
4. [Archivos de Documentación (.md)](#archivos-de-documentación-md)
5. [Estado Técnico Actual](#estado-técnico-actual)
6. [Knowledge Base / Obsidian](#knowledge-base--obsidian)
7. [Propuesta: Obsidian como Fuente de Verdad](#propuesta-obsidian-como-fuente-de-verdad)

---

## 📊 Resumen Ejecutivo

**DOS AROS** es un sistema comparativo de análisis de baloncesto (NBA vs EuroLeague) con la filosofía:

> **"Datos primero. Contexto después. Opinión al final."**

- **Backend**: Python (ETL, procesamiento, IA con Gemini/Groq/Claude)
- **Frontend**: Next.js 15 (landing page, catálogo de productos, análisis)
- **Base de Datos**: SQLite (Pi) → Supabase (PostgreSQL)
- **Automatización**: Bot Telegram que ejecuta cron diarios a las 9:00
- **Branding**: Sistema avatar generativo con 452 millones de combinaciones

**Objetivo**: Ser fuente confiable de insights data-driven en baloncesto, NO comentarista deportivo.

---

## 🖥️ Entornos

### **Windows (Desarrollo Local)**

**Ubicación**: `C:\Users\rover\dosaros-data-project\`

**Stack Activo**:
- Node.js 20+ (Next.js 15)
- Python 3.10+ (venv)
- SQLite local (para testing)
- Navegador: Chrome/Edge

**Comando para arrancar**:
```bash
npm run dev          # Frontend en http://localhost:3000
streamlit run src/app/main.py  # Backend Streamlit
```

**Servidor Next.js**: http://localhost:3000
- ✅ Landing page
- ✅ Catálogo de productos (/productos)
- ✅ Formulario de contacto (/contact)
- ✅ Páginas en construcción (Análisis, Predicciones, Comunidad)

**Ramas activas**: `main` (estable + frontend completo)

---

### **Raspberry Pi 4 (Producción)**

**IP**: `192.168.1.136`  
**Usuario**: `pi`  
**Ubicación del proyecto**: `/home/pi/dosaros-data-project/`  
**BD warehouse**: `/mnt/nba_data/dosaros_local.db`

**Stack de Producción**:
- Python 3.11 (venv)
- SQLite (source of truth)
- Telegram Bot (bot_consultas tmux)
- Cron automático (9:00 diarios)

**Sesiones tmux activas** (2026-05-17):
- `bot_consultas` — Bot Telegram siempre activo
- `nba_hist2` — Carga histórica NBA 2017-2019 (en progreso)
- `euro_hist2` — Carga histórica EuroLeague E2010-E2021 (en progreso)

**Cron diario** (master_sync.py):
```
0 9 * * * /home/pi/dosaros-data-project/venv/bin/python master_sync.py
```

**Cobertura BD actual**:
- NBA games: 1983-2024-25 (completo)
- NBA PBP: 2015-2024 + playoffs (5M registros)
- EuroLeague games: E2007-E2025 (completo)
- EuroLeague PBP: E2007-E2009, E2022-E2025 (1M registros; E2010-E2021 cargándose)

---

### **GitHub (Repositorio Remoto)**

**URL**: `https://github.com/dosaroscontact/dosaros-data-project.git`  
**Rama principal**: `main` (protegida)

**Últimos commits**:
- `e1e9136` — restore: Add product images (40 imágenes)
- `46566b9` — fix: Restore complete product catalog
- `4f4c297` — merge: resolve settings conflict

**Historial limpio**: BFG limpieza aplicada (2026-05-17) para remover node_modules de 141.5 MB

**Flujo de trabajo**:
- Desarrollo local en Windows
- Commits a `main` cuando feature está completa
- Push directo (sin PR aún)

---

## 📁 Estructura de Carpetas

### **Raíz del Proyecto**

| Carpeta | Descripción |
|---------|------------|
| `.claude/` | Configuración de Claude Code (settings.json, skills) |
| `.github/` | Workflows de GitHub (CI/CD) |
| `.next/` | Build de Next.js (cachés, compilados) |
| `.streamlit/` | Config de Streamlit |
| `app/` | **Frontend Next.js App Router** |
| `components/` | Componentes React reutilizables |
| `lib/` | Utilidades JavaScript |
| `public/` | Assets estáticos (logos, imágenes, productos) |
| `src/` | **Backend Python** (ETL, IA, automación) |
| `assets/` | Documentación de marca, avatares, datos |
| `docs/` | Documentos varios (Roadmap, expectativas) |
| `scripts/` | Scripts Python auxiliares |
| `knowledge_base/` | **Vault de Obsidian** |
| `logs/` | Logs de cron y servicios |
| `node_modules/` | Dependencias Node.js |
| `venv/` | Virtualenv de Python |

---

### **`app/` — Frontend Next.js**

**Estructura App Router**:
```
app/
├── page.tsx            # Home (/ — landing page)
├── layout.tsx          # Layout global
├── globals.css         # Estilos globales
├── api/
│   └── contact/
│       └── route.ts    # Endpoint para FormSubmit.co
├── productos/
│   └── page.tsx        # /productos — Catálogo completo
├── contact/
│   └── page.tsx        # /contact — Formulario pre-rellenado
├── analisis/
│   └── page.tsx        # /analisis — En construcción
├── predicciones/
│   └── page.tsx        # /predicciones — En construcción
├── comunidad/
│   └── page.tsx        # /comunidad — En construcción
└── experimental/
    └── page.tsx        # /experimental — Glitch logo effect
```

**Archivos estáticos** (`public/`):
```
public/
├── logos/              # Logo DOS AROS official
├── banners/            # Banner naranja (letering-orange.png)
├── productos/          # 40 imágenes de productos (5 categorías × 6-8 colores)
├── products/           # Imágenes antiguas (deprecated)
├── twitter.svg         # Social media icons
├── instagram.svg
└── favicon.ico
```

---

### **`src/` — Backend Python**

**Arquitectura ETL**:
```
src/
├── app/                # Streamlit dashboard
│   ├── main.py         # App principal (tabs: Análisis + NL→SQL)
│   └── analista_ia.py  # Generador de SQL con IA
├── etl/                # Extractores de datos
│   ├── nba_sync.py     # Sincronización NBA (partidos, PBP, jugadores)
│   ├── euro_sync.py    # Sincronización EuroLeague
│   ├── extract_yesterday_results.py  # Resultados diarios NBA
│   ├── extract_yesterday_euro.py     # Resultados diarios Euro
│   ├── historic_pbp_loader.py        # Carga histórica (--liga, --bloque)
│   ├── euro_historic_games_loader.py # Partidos históricos Euro
│   └── seed_avatar_teams.py          # Semilla de avatares
├── database/           # Operaciones BD
│   ├── init_local_db.py      # Inicializar SQLite
│   ├── populate_avatars.py   # Poblar dimensiones avatar
│   └── init_avatar_teams.py  # Crear tabla avatar_teams
├── processors/         # Lógica de transformación
│   ├── image_generator.py    # Story 1080×1920 con Pillow
│   ├── avatar_prompt_generator.py  # Prompts Midjourney/ImageFX
│   ├── insight_generator.py  # Detecta perlas IA
│   ├── gemini_social.py      # Hilo X/Twitter (5-6 tweets)
│   └── video_generator/      # Remotion + IA para MP4
├── automation/         # Bots y automatización
│   ├── bot_consultas.py      # Bot Telegram NL→SQL + /video
│   └── bot_manager.py        # Envío a Telegram
├── integrations/       # Integraciones externas
│   └── video_generator/      # Generación MP4
├── utils/              # Utilidades
│   ├── api_manager.py        # Router LLM (Gemini, OpenAI, Claude, etc.)
│   ├── credentials_loader.py # Gestión de credenciales
│   ├── mapper.py             # Mapeo de coordenadas EuroLeague
│   └── database.py           # Operaciones BD
├── prompts/            # Personas y plantillas
│   └── (varios .txt con personas para redes)
└── docs/               # Documentación técnica
```

---

### **`assets/` — Datos y Documentación de Marca**

```
assets/
├── docs/
│   ├── BRAND.md        # 📋 Guía completa de marca (avatar, colores, postura)
│   └── (otros docs)
├── avatars/            # Avatares generados (PNG)
├── logos/              # Logos oficiales
├── static/             # Fuentes bundled (Space Grotesk, Inter)
├── video_output/       # Videos generados
├── player_aliases.json # Mapeo apodos → nombres reales
└── data/               # CSVs de referencia
    └── raw/            # Datos crudos
```

---

### **`knowledge_base/` — Obsidian Vault**

**Ubicación**: `C:\Users\rover\dosaros-data-project\knowledge_base\`

```
knowledge_base/
├── .obsidian/          # Config de Obsidian (vault settings)
├── DosAros/            # Notas sobre el proyecto DOS AROS
├── NBA/                # Notas sobre NBA (equipos, reglas)
├── EuroLeague/         # Notas sobre EuroLeague
├── Analytics/          # Métodos analíticos, estadísticas
├── Architecture/       # Decisiones arquitectónicas
├── Insights/           # Resultados de análisis
├── Project Docs/       # Documentación técnica
├── Templates/          # Plantillas de notas
└── (otros folders)
```

**Tamaño actual**: ~2-3 MB de notas (estimado)

---

## 📄 Archivos de Documentación (.md)

### **En Raíz del Proyecto**

| Archivo | Misión | Contenido |
|---------|--------|-----------|
| `CLAUDE.md` | **Instrucciones para IA** | Comando de inicio, rutas Pi, comandos SQL, vars de entorno, schema BD, arquitectura, cron, reglas críticas, prevención de errores |
| `README.md` | Intro del proyecto | Resumen de ETL, Streamlit, referencias a IMPLEMENTATION_SUMMARY |
| `contexto_proyecto_20260412.md` | Snapshot histórico | Estado de BD, commits pendientes (deprecated) |

### **En `assets/docs/`**

| Archivo | Misión | Contenido |
|---------|--------|-----------|
| `BRAND.md` | **Guía visual y conceptual** | Avatar (54 equipos), tabla dimensiones (postura/vestimenta/decorado/tipo_logo), paleta 7 colores, 452M combinaciones, historia de marca |

### **En `docs/`** (Legacy)

| Archivo | Estado |
|---------|--------|
| `Roadmap.txt` | Outdated |
| `expectativas.txt` | Outdated |
| Reel Librarian.html | Outdated |

---

## 🔧 Estado Técnico Actual

### **Frontend (Next.js)**
- ✅ Landing page completa (Hero, Highlights, Newsletter, Footer)
- ✅ Catálogo de productos (/productos) — 40 imágenes, 5 categorías, 6-8 colores cada una
- ✅ Formulario de contacto (/contact) — pre-relleno con producto
- ✅ Navbar + Footer en todas las páginas
- ✅ Dark mode funcional
- ✅ Responsive (mobile-first)
- ⚠️ Análisis, Predicciones, Comunidad en construcción (placeholder)

**Color Palette** (Tailwind):
```
dos-blue: #0D1321        | dos-orange: #FF7D28
dos-blue-dark: #011E3B   | dos-orange-dark: #FF3E04
dos-magenta: #B1005A     | dos-white: #FFFFFF
dos-gray: #E6E8EE
```

### **Backend (Python)**
- ✅ ETL NBA completamente sincronizado (2015-2024)
- ✅ ETL EuroLeague parcial (E2007-E2009, E2022-E2025; E2010-E2021 en progreso)
- ✅ Bot Telegram con NL→SQL y /video
- ✅ Sistema de avatar con generación de prompts
- ✅ Cron automático diario (resultados, perlas, hilo X)
- ✅ API Manager (10+ LLM providers con fallback)
- ✅ Streamlit dashboard básico
- ⚠️ Video Generator (Remotion) — funciona pero necesita optimización
- ⚠️ Newsletter — no conectada a BD

### **Bases de Datos**
- ✅ SQLite Pi (source of truth)
- ⚠️ Supabase (desincronizado, solo referencia)
- ✅ BD local de desarrollo
- ⚠️ Cobertura histórica incompleta (E2010-E2021 Euro aún cargando)

### **GitHub**
- ✅ Historial limpio (BFG aplicado)
- ✅ Todos los commits del frontend pusheados
- ✅ Protección de rama main

---

## 📚 Knowledge Base / Obsidian

### **Ubicación y Estado**
```
C:\Users\rover\dosaros-data-project\knowledge_base\
├── .obsidian/        # Configuración de vault
├── DosAros/          # Notas sobre el proyecto
├── NBA/              # Referencia de equipos, reglas
├── EuroLeague/       # Referencia de competición
└── [otros folders]
```

### **Contenido Estimado**

**DosAros/**:
- Descripción del proyecto
- Decisiones técnicas
- Roadmap
- Estado actual

**NBA/** y **EuroLeague/**:
- Reglas de competición
- Diccionarios de equipos/jugadores
- Contexto histórico

**Architecture/**:
- Decisiones de diseño
- Justificación técnica
- Trade-offs

**Insights/**:
- Resultados de análisis
- Patrones descubiertos

**Templates/**:
- Template de reporte
- Template de análisis
- Estructura de notas

---

## 🔗 Propuesta: Obsidian como Fuente de Verdad

### **Problema Actual**

1. **Fragmentación de conocimiento**: 
   - Docs en `.md` en raíz
   - CLAUDE.md como instrucciones (no como notas)
   - Knowledge base en Obsidian (pero desconectado)
   - Memory de Claude Code (persistente pero no visible)

2. **Sin vinculación activa**:
   - Claude Code lee CLAUDE.md pero no accede a Obsidian
   - Usuario trabaja en Obsidian pero no está integrado en flujo de dev
   - Decisiones arquitectónicas sin histórico de cambios

3. **Duplicación de información**:
   - BRAND.md en `assets/docs/`
   - Pero también notas en Obsidian
   - CLAUDE.md por separado

---

### **Solución Propuesta: Arquitectura de Conocimiento Centrada en Obsidian**

```
┌─────────────────────────────────────────┐
│      OBSIDIAN (Fuente de Verdad)        │
│  C:\Users\rover\knowledge_base\         │
├─────────────────────────────────────────┤
│                                         │
│ Project/ (Estructura del proyecto)     │
│  ├── 📋 README.md (overview)           │
│  ├── 🏗️ Architecture.md (decisiones)  │
│  ├── 📊 Brand.md (sistema visual)      │
│  ├── 🗄️ Database.md (schema)          │
│  └── 🔄 Workflows.md (procesos)        │
│                                         │
│ NBA/ + EuroLeague/ (Referencia)        │
│ Insights/ (Análisis)                   │
│ Templates/ (Plantillas)                │
│                                         │
└─────────────────────────────────────────┘
        ↓                      ↓
    ┌───────────────────────────────┐
    │ Síncrono con:                │
    ├───────────────────────────────┤
    │ • CLAUDE.md (regenerado)     │
    │ • assets/docs/BRAND.md       │
    │ • Memory de Claude Code      │
    └───────────────────────────────┘
        ↓                      ↓
    ┌───────────────────────────────┐
    │ Acceso desde:                │
    ├───────────────────────────────┤
    │ • Claude Code (read-only)    │
    │ • Editor local (edit)        │
    │ • GitHub (síncrono)         │
    └───────────────────────────────┘
```

---

### **Estructura Recomendada de Obsidian**

```
knowledge_base/
│
├── 📋 Project Root/
│   ├── README.md              # Overview general (links a todas las secciones)
│   ├── CHANGELOG.md           # Histórico de cambios
│   ├── STATUS.md              # Estado actual (entornos, servidores, BD)
│   └── ROADMAP.md             # Plan futuro
│
├── 🏗️ Architecture/
│   ├── System Design.md       # Diagrama conceptual
│   ├── Database Schema.md     # Tablas, relaciones, índices
│   ├── API Design.md          # Endpoints, LLM providers
│   ├── Frontend Stack.md      # Next.js, componentes
│   └── Decisions Log.md       # ADRs (Architecture Decision Records)
│
├── 🎨 Brand/
│   ├── Visual Identity.md     # Avatar, colores, paleta
│   ├── Design System.md       # Componentes, tokens
│   └── Logo & Assets.md       # Referencias de archivos
│
├── 🗄️ Data/
│   ├── NBA Reference.md       # Teams, seasons, rules
│   ├── EuroLeague Reference.md
│   ├── Data Dictionary.md     # Campos canónicos
│   └── ETL Processes.md       # Flujos de ingesta
│
├── 🤖 Development/
│   ├── Environment Setup.md   # Windows, Pi, GitHub
│   ├── Commands.md            # Comandos frecuentes
│   ├── Debugging Guide.md     # Troubleshooting
│   └── Performance.md         # Optimizaciones
│
├── 📊 Insights/
│   ├── Analysis Results/      # Resultados por fecha
│   ├── Patterns.md            # Patrones descubiertos
│   └── Anomalies.md           # Casos interesantes
│
├── 🔄 Workflows/
│   ├── Daily Automation.md    # Cron, bot Telegram
│   ├── Release Process.md     # Deployment
│   └── Monitoring.md          # Logs, alertas
│
└── 📝 Templates/
    ├── Analysis Template.md
    ├── Bug Report.md
    └── Feature Proposal.md
```

---

### **Implementación Paso a Paso**

#### **Fase 1: Migración de Contenido (1-2 días)**

1. **Extraer contenido de CLAUDE.md → Architecture/Environment Setup.md**
   - Respetar estructura actual
   - Agregar links bidireccionales
   - Versionar con changelog

2. **Reorganizar BRAND.md → Brand/Visual Identity.md**
   - Copiar assets/docs/BRAND.md al vault
   - Mantener original en `assets/docs/` como referencia

3. **Crear notas de referencia (NBA, EuroLeague, Data)**
   - Usar estructura existente en Obsidian
   - Enriquecer con contexto

4. **Documentar decisiones arquitectónicas pasadas**
   - ADRs (Architecture Decision Records)
   - Crear Architecture/Decisions Log.md

#### **Fase 2: Sincronización Automática (2-3 días)**

1. **Script Python que exporta Obsidian → CLAUDE.md**
   - Leer vault de Obsidian
   - Generar CLAUDE.md estructurado
   - Ejecutar post-commit

2. **GitHub Actions que síncronizan**
   - On push: actualizar Obsidian
   - On Obsidian update: crear commit

3. **Claude Code memory que referencia Obsidian**
   - Memory file que apunta a rutas
   - Links en formato `[[filename|section]]`

#### **Fase 3: Flujo de Trabajo Integrado (1 semana)**

1. **Usuario edita Obsidian** (tu espacio mental)
   - Toma decisiones
   - Documenta cambios
   - Crea templates

2. **Cambios se sincronizan** automáticamente
   - CLAUDE.md regenerado
   - GitHub actualizado
   - Claude Code accede al contenido

3. **Claude Code accede contenido** (automático)
   - Lee CLAUDE.md regenerado
   - Consulta memory que apunta a Obsidian
   - Sigue instrucciones actualizadas

---

### **Ejemplo: Cómo Funcionaría**

**Escenario**: Cambias la paleta de colores

1. **Editas en Obsidian**: `Brand/Visual Identity.md`
   ```markdown
   ## Color Palette
   - dos-blue: #0D1321 → #000000 (más oscuro)
   ```

2. **Script nocturno ejecuta**: `sync_obsidian_to_claude.py`
   - Extrae cambios de Obsidian
   - Regenera `assets/docs/BRAND.md`
   - Actualiza `CLAUDE.md`
   - Commit automático

3. **Claude Code accede**: En siguiente sesión
   - Lee CLAUDE.md actualizado
   - Aplica nuevos colores en Tailwind
   - Propone cambios según el plan

---

### **Tooling Recomendado**

1. **Obsidian Plugins**:
   - `Dataview` — queries sobre notas
   - `Excalidraw` — diagramas
   - `Templater` — plantillas dinámicas
   - `Obsidian Git` — sincronización con repo
   - `Breadcrumbs` — navegación jerárquica

2. **Scripts Python** (en `scripts/`):
   - `sync_obsidian_to_claude.py` — exportar a CLAUDE.md
   - `validate_obsidian_schema.py` — validar estructura
   - `generate_dashboard.py` — crear index dinámico

3. **GitHub Actions** (en `.github/workflows/`):
   - `sync-obsidian.yml` — sincronización bidireccional

---

### **Ventajas**

✅ **Para ti (Usuario)**:
- Obsidian es tu espacio mental principal
- No necesitas editar archivos técnicos
- Historial de cambios en Obsidian
- Búsqueda full-text sobre todo el proyecto

✅ **Para Claude Code**:
- Acceso a contexto actualizado automáticamente
- No necesita preguntar "dime el estado actual"
- Sigue instrucciones de CLAUDE.md regenerado
- Memory apunta a fuente de verdad

✅ **Para GitHub**:
- Documentación siempre sincronizada
- Cambios visibles en commits
- Audit trail completo

---

## 🚀 Próximos Pasos

1. **Corto plazo** (1 semana):
   - [ ] Transferir contenido a Obsidian
   - [ ] Crear estructura de carpetas definitiva
   - [ ] Documentar decisiones pasadas (ADRs)

2. **Mediano plazo** (2-3 semanas):
   - [ ] Implementar sincronización Obsidian ↔ CLAUDE.md
   - [ ] Crear scripts de validación
   - [ ] GitHub Actions de sincronización

3. **Largo plazo**:
   - [ ] Dashboard dinámico (Dataview)
   - [ ] Sistema de plantillas (Templater)
   - [ ] Integración con Analytics (GA, Telegram metrics)

---

## 📞 Contacto y Soporte

**Mantenedor**: @DosAros  
**Email**: dosaroscontact@gmail.com  
**Repo**: https://github.com/dosaroscontact/dosaros-data-project

---

**Generado por Claude Code | 2026-05-17**
