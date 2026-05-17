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

## ADR-008: Vercel como plataforma de deploy
**Fecha**: 2026-05-17
**Estado**: ✅ Activa

**Decisión**: Usar Vercel (plan Hobby) para hostear el frontend Next.js.

**Contexto**:
- Necesitamos hosting para frontend Next.js 15
- Buscamos coste mínimo, SSL automático, auto-deploy
- Dominio dosaros.com está en DonDominio

**Alternativas consideradas**:
- **Netlify**: similar pero peor integración Next.js
- **Cloudflare Pages**: bueno pero menos features Next.js
- **VPS propio**: más control pero más mantenimiento y coste
- **Pi** (auto-hosting): no escalable, sin SSL fácil

**Consecuencias**:
- ✅ 0€/mes (plan Hobby)
- ✅ Auto-deploy en cada push a main
- ✅ SSL automático Let's Encrypt
- ✅ CDN global incluido
- ✅ Preview URLs en cada PR
- ⚠️ Vendor lock-in moderado (next/image, ISR optimizado para Vercel)
- ⚠️ Plan Hobby: 100GB bandwidth/mes (suficiente al inicio)

---

## ADR-009: GTM + GA4 para analytics
**Fecha**: 2026-05-17
**Estado**: ✅ Activa

**Decisión**: Usar GTM (`GTM-MWDXWXZN`) como capa de tag management y GA4 como destino.

**Eventos custom diseñados**: 9 (page_view, nav_clicked, cta_clicked, product_interest, category_changed, analysis_clicked, tag_filter_clicked, form_submitted, social_clicked).

**Implementación**:
- `lib/analytics.ts` con `trackEvent()` tipado
- Cada componente importa helper y llama trackEvent en interacciones clave
- GTM container importado via JSON (21 vars + 9 triggers + 10 tags)

**Consecuencias**:
- ✅ Flexibilidad: añadir/quitar tags sin re-deploy
- ✅ Multi-tool: GTM puede enviar a GA4, Meta Pixel, Hotjar, etc.
- ✅ Naming consistency (snake_case, object_action)
- ✅ Type-safe en código (TypeScript)
- ⚠️ Dependencia de GTM (si falla, no hay tracking)
- ⚠️ JavaScript required (no SSR-tracked)

---

## ADR-010: Markdown files para análisis diarios (no CMS)
**Fecha**: 2026-05-17
**Estado**: ✅ Activa

**Decisión**: Sistema de blog basado en archivos `.md` en `content/analysis/YYYY/MM/`, con script Python que genera frontmatter automáticamente.

**Alternativas consideradas**:
- **Sanity/Contentful**: overkill, coste adicional
- **Notion API**: dependencia externa, latencia
- **WordPress headless**: complejidad innecesaria
- **DB en Supabase**: pendiente para futuro (cuando haya múltiples autores)

**Consecuencias**:
- ✅ Versionado en git
- ✅ Build estático ultra-rápido (`generateStaticParams`)
- ✅ Zero infra adicional
- ✅ Tu workflow actual (escribir .md) sigue igual
- ⚠️ Solo un autor a la vez
- ⚠️ Requiere git push para publicar

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
