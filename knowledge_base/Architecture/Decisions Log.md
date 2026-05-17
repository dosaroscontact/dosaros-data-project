# 📝 Architecture Decision Records (ADRs)

Registro cronológico de decisiones arquitectónicas importantes.

**Formato**: Decisión · Contexto · Consecuencias

---

## ADR-001: SQLite como Warehouse Principal
**Fecha**: 2025 (inicio del proyecto)
**Estado**: ✅ Activa

**Decisión**: Usar SQLite en Raspberry Pi como source of truth.

**Contexto**:
- Proyecto personal con presupuesto limitado
- Datos relativamente pequeños (~6M registros)
- Control total preferible

**Consecuencias**:
- ✅ Coste cero
- ✅ Backups simples (copia de archivo)
- ❌ Sin concurrencia escritura
- ❌ No accesible directamente desde internet

---

## ADR-002: Multi-LLM con Cascade Fallback
**Fecha**: 2025-2026
**Estado**: ✅ Activa

**Decisión**: Implementar router `api_manager.py` que prueba múltiples LLMs en orden.

**Contexto**:
- Gemini gratuito tiene rate limits
- Diferentes LLMs son mejores en tareas distintas
- Resilience requerida (cron no debe fallar)

**Orden de fallback**:
1. Gemini (primario)
2. OpenAI
3. Claude (ROVE)
4. Groq
5. DeepSeek
6. Kimi
7. Grok

**Consecuencias**:
- ✅ Alta disponibilidad
- ✅ Coste optimizado
- ⚠️ Complejidad de mantenimiento
- ⚠️ Resultados pueden variar según LLM

---

## ADR-003: Telegram Bot como Interface Principal
**Fecha**: 2025
**Estado**: ✅ Activa

**Decisión**: El usuario interactúa con el sistema vía Telegram, no web UI.

**Contexto**:
- Usuario quiere consultas rápidas
- No quiere instalar apps
- Telegram tiene API gratuita
- UX inmediata desde móvil

**Consecuencias**:
- ✅ Adopción instantánea
- ✅ Sin coste de hosting UI
- ❌ UI limitada (texto + imágenes)
- ❌ No accesible para no-Telegram users

---

## ADR-004: Next.js 15 para Frontend Público
**Fecha**: 2026-05
**Estado**: ✅ Activa

**Decisión**: Construir landing page + catálogo en Next.js 15 (App Router) en lugar de Streamlit.

**Contexto**:
- Streamlit es para internal dashboards
- Necesita SEO y performance para web pública
- React ecosystem para componentes ricos

**Consecuencias**:
- ✅ SEO óptimo (SSR/SSG)
- ✅ Performance superior
- ✅ Mejor UX
- ❌ Mayor complejidad de deployment
- ❌ Curva de aprendizaje

---

## ADR-005: FormSubmit.co (sin backend)
**Fecha**: 2026-05
**Estado**: ✅ Activa

**Decisión**: Usar FormSubmit.co para formulario de contacto en vez de backend custom.

**Contexto**:
- Solo necesitamos enviar emails
- No queremos hospedar backend
- FormSubmit es gratuito

**Consecuencias**:
- ✅ Cero infraestructura
- ✅ Implementación en minutos
- ❌ Dependencia de servicio externo
- ⚠️ Limites de envíos diarios

---

## ADR-006: Obsidian como Knowledge Base (En curso)
**Fecha**: 2026-05-17
**Estado**: 🚧 En implementación

**Decisión**: Usar Obsidian como fuente única de verdad para documentación. Sincronizar automáticamente con CLAUDE.md.

**Contexto**:
- Documentación fragmentada (CLAUDE.md, BRAND.md, memory de Claude)
- Difícil mantener consistencia
- Obsidian ya está parcialmente usado

**Consecuencias**:
- ✅ Una sola fuente de verdad
- ✅ Sincronización automática
- ✅ Mejor UX para escribir docs
- ⚠️ Requiere script de sincronización
- ⚠️ Posible desincronización si script falla

**Plan de implementación**:
- Fase 1: Migrar contenido (en curso)
- Fase 2: Script `sync_obsidian_to_claude.py`
- Fase 3: Documentar workflow

---

## ADR-007: BFG Repo Cleaner para Limpieza de Historial
**Fecha**: 2026-05-17
**Estado**: ✅ Aplicada

**Decisión**: Usar BFG en lugar de `git filter-branch` para remover archivos grandes del historial.

**Contexto**:
- `node_modules/@next/swc-win32-x64-msvc/next-swc.win32-x64-msvc.node` (141.5 MB) bloqueaba push
- GitHub rechaza archivos >100 MB
- BFG es más rápido y simple que filter-branch

**Consecuencias**:
- ✅ Push exitoso después de limpieza
- ⚠️ Force push requerido (history rewrite)
- ⚠️ Coordinar si hay otros developers

---

## 📐 Template para Nuevos ADRs

```markdown
## ADR-XXX: [Título]
**Fecha**: YYYY-MM-DD
**Estado**: 🚧 Propuesta / ✅ Activa / ❌ Deprecated

**Decisión**: [Qué se decidió]

**Contexto**: [Por qué fue necesaria esta decisión]

**Alternativas consideradas**: [Qué se descartó y por qué]

**Consecuencias**:
- ✅ Pros
- ❌ Contras
- ⚠️ Trade-offs
```

---

## 🔗 Referencias

- [[System Design|🎯 Diseño del sistema]]
- [[../Workflows/Sync Obsidian to Claude|🔁 Sync workflow (ADR-006)]]
