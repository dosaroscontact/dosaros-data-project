# 📊 STATUS — Estado Actual del Proyecto

**Última actualización**: 2026-05-17

---

## 🟢 Entornos Activos

### Windows (Desarrollo Local)
- **Ruta**: `C:\Users\rover\dosaros-data-project\`
- **Frontend dev server**: http://localhost:3000 ✅ Activo
- **Servidor Streamlit**: Inactivo (lanzar con `streamlit run src/app/main.py`)
- **Rama git**: `main` (sincronizada con remoto)

### Raspberry Pi 4 (Producción)
- **IP**: `192.168.1.136`
- **Ruta**: `/home/pi/dosaros-data-project/`
- **BD**: `/mnt/nba_data/dosaros_local.db` (SQLite)
- **Cron 9:00**: ✅ Activo (master_sync.py)
- **Bot Telegram**: ✅ Activo en tmux `bot_consultas`

**Sesiones tmux activas**:
- `bot_consultas` — Bot Telegram polling
- `nba_hist2` — Carga histórica NBA 2017-2019 ⚙️ En progreso
- `euro_hist2` — Carga histórica EuroLeague E2010-E2021 ⚙️ En progreso

### GitHub
- **Repo**: https://github.com/dosaroscontact/dosaros-data-project
- **Rama principal**: `main`
- **Historial**: ✅ Limpio (BFG aplicado 2026-05-17)
- **Último commit**: `d991ba6` — docs: Add comprehensive project overview

---

## 📦 Cobertura de Datos

### NBA (`nba_pbp`, 5,015,190 registros)
- ✅ Regular 2015-16, 2016-17 (completas)
- ⚠️ Regular 2017-18 parcial (~25%, en `nba_hist2`)
- ❌ 2018-19, 2019-20 (pendientes)
- ✅ Regular + Playoffs 2020-21 → 2024-25 (completas)
- ✅ `nba_games`: completo desde 1983

### EuroLeague (`euro_pbp`, 1,049,283 registros)
- ✅ E2007, E2008, E2009 cargadas
- ⚠️ E2010 parcial (en `euro_hist2`)
- ❌ E2011 → E2021 (pendientes)
- ✅ E2022-E2025 completas

---

## 🌐 Frontend Next.js (Producción local)

### Páginas Implementadas
| Ruta | Estado | Descripción |
|------|--------|-------------|
| `/` | ✅ | Landing page (Hero, Highlights, Products, Newsletter, Footer) |
| `/productos` | ✅ | Catálogo con 5 categorías × 6-8 colores (40 imágenes) |
| `/contact` | ✅ | Formulario con pre-relleno por URL parameter |
| `/analisis` | ✅ | Sistema de blog con análisis diarios |
| `/analisis/[slug]` | ✅ | Artículo individual renderizado desde markdown |
| `/predicciones` | ⚠️ | En construcción (placeholder) |
| `/competiciones` | ✅ | NBA + EuroLeague con cobertura y stats |
| `/experimental` | ✅ | Glitch logo effect (hidden) |

### Funcionalidades
- ✅ Dark mode
- ✅ Responsive (mobile-first)
- ✅ Formulario contacto → FormSubmit.co
- ✅ Pre-relleno producto (URL params)
- ✅ Navbar fija con social links

---

## 🤖 Bot Telegram (Producción)

### Comandos Activos
| Input | Respuesta |
|-------|-----------|
| Pregunta en español | SQL automático → tabla resultados |
| `sí` tras resultado | Tweet redactado + story imagen 1080×1920 |
| `/video <texto>` | Genera MP4 con Remotion |
| `/avatar_prompt <equipo>` | Prompt Midjourney para ese equipo |
| `/avatar_random` | Prompt aleatorio |
| `/avatars` | 5 prompts aleatorios del día |
| `/StatusIA` | Estado de proveedores LLM |
| `/Sync` | Lanzar sincronización bajo demanda |

---

## 🔌 APIs LLM (Estado actual)

| Proveedor | Estado | Uso |
|-----------|--------|-----|
| Gemini | ✅ | Primario |
| OpenAI | ✅ | Fallback |
| Claude (ROVE) | ✅ | Fallback secundario |
| Groq | ✅ | Fallback rápido |
| Grok | ✅ | Tweets |
| Manus | ✅ | Variante |
| DeepSeek | ⚠️ | Bug pendiente |
| Kimi | ⚠️ | Bug pendiente |

---

## 🚧 Trabajo Pendiente

### Inmediato
- [ ] Esperar finalización de ETL histórico (nba_hist2, euro_hist2)
- [ ] Reparar bug DeepSeek/Kimi en api_manager.py

### Próximas Iteraciones
- [ ] Implementar páginas reales en /analisis, /predicciones, /comunidad
- [ ] Conectar Newsletter signup a BD
- [ ] Sistema de notificaciones de errores ETL
- [ ] Tests automatizados de ETL

### Mejoras Estratégicas
- [x] Migrar a Obsidian como fuente de verdad ✅ COMPLETADO (2026-05-17)
- [x] Implementar sincronización automática Obsidian → CLAUDE.md ✅ COMPLETADO (2026-05-17)
- [x] Sistema de Architecture Decision Records (ADRs) ✅ COMPLETADO (2026-05-17)
- [ ] Probar flujo completo en producción

---

## 📞 Referencias Rápidas

- **Setup completo**: [[../Development/Environment Setup]]
- **Comandos**: [[../Development/Commands]]
- **Troubleshooting**: [[../Development/Debugging Guide]]
