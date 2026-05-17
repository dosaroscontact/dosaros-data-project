# 📊 Analytics Tracking Plan — DOS AROS

**GTM Container**: `GTM-MWDXWXZN`
**Última actualización**: 2026-05-17

---

## 🎯 Eventos Trackeados

Todos los eventos se pushean al `dataLayer` de GTM. Para activarlos en GA4, crea Triggers en GTM con `Custom Event` name = nombre del evento.

### Tracking Plan

| Event Name | Cuándo se dispara | Propiedades | Helper |
|------------|------------------|-------------|--------|
| `page_view` | Cada navegación SPA (cliente) | `page_path`, `page_title`, `page_referrer` | `PageViewTracker.tsx` |
| `nav_clicked` | Click en menú navbar/footer | `link_text`, `link_url`, `nav_location` | `Navbar.tsx`, `Footer.tsx` |
| `cta_clicked` | Click en CTA principal (Hero) | `cta_text`, `cta_location`, `destination` | `Hero.tsx` |
| `product_interest` | "Ver disponibilidad" en catálogo | `product_name`, `product_category`, `action` | `ProductCatalog.tsx` |
| `category_changed` | Cambio de tab en catálogo | `category_id`, `category_name` | `ProductCatalog.tsx` |
| `analysis_clicked` | Click en artículo del listado | `analysis_slug`, `analysis_title`, `analysis_date` | `AnalysisList.tsx` |
| `tag_filter_clicked` | Click en filtro por tag | `tag_name` | `AnalysisList.tsx` |
| `form_submitted` | Submit del formulario contacto | `form_name`, `status`, `source_product?` | `ContactForm.tsx` |
| `social_clicked` | Click en X/Instagram | `platform`, `handle`, `location` | `Navbar.tsx`, `Footer.tsx` |

---

## 🔧 Implementación Técnica

### Helper: `lib/analytics.ts`

Función tipada `trackEvent()` que valida y pushea al dataLayer:

```typescript
import { trackEvent } from '@/lib/analytics'

trackEvent({
  event: 'cta_clicked',
  cta_text: 'Productos',
  cta_location: 'hero_secondary',
  destination: '/productos',
})
```

**Ventajas**:
- ✅ Tipado fuerte (TypeScript)
- ✅ Safe en SSR (no-op si `window` undefined)
- ✅ Debug logs en desarrollo (`process.env.NODE_ENV === 'development'`)

### Page Views: `components/PageViewTracker.tsx`

Componente client-side que escucha cambios de ruta:

```tsx
// app/layout.tsx
<PageViewTracker />
{children}
```

GTM ya trackea el primer `page_view` automático. Este componente captura las navegaciones SPA posteriores.

---

## 🎨 Localizaciones (nav_location, cta_location)

### `nav_location`
- `header_desktop` — Menú top, vista desktop
- `header_mobile` — Menú hamburguesa móvil
- `footer` — Links del footer

### `cta_location`
- `hero_primary` — Botón naranja "Explora partidos en vivo"
- `hero_secondary` — Botón borde magenta "Productos"
- `highlights_view_all` — "Ver todas las perlas"
- `products_view_all` — "Explorar toda la colección"
- `analysis_view_all` — "Ver todos los análisis"

### `social_location`
- `navbar` — Iconos sociales en header
- `mobile_menu` — Iconos en menú móvil
- `footer` — Iconos en footer

---

## 🚀 Configuración en GTM (paso a paso)

### 1. Conectar GTM con GA4
1. GTM dashboard → **Tags** → **New**
2. Tag Configuration → **Google Analytics: GA4 Configuration**
3. Measurement ID: `G-XXXXXXX` (tu ID de GA4)
4. Trigger: **All Pages**
5. Save → **Submit**

### 2. Crear triggers para eventos custom
Para cada evento de la tabla anterior:

1. **Triggers** → **New** → **Custom Event**
2. Event name: `cta_clicked` (o el que corresponda)
3. Save

### 3. Crear tags GA4 para cada evento
Para enviar a GA4:

1. **Tags** → **New**
2. Tag Configuration → **Google Analytics: GA4 Event**
3. Configuration Tag: tu GA4 config tag
4. Event Name: `cta_clicked`
5. Event Parameters:
   - `cta_text` → `{{DLV - cta_text}}` (Data Layer Variable)
   - `cta_location` → `{{DLV - cta_location}}`
   - `destination` → `{{DLV - destination}}`
6. Trigger: `cta_clicked` (el creado en paso 2)
7. Save

### 4. Variables Data Layer
Para cada propiedad de evento, crear una variable:

1. **Variables** → **User-Defined Variables** → **New**
2. Type: **Data Layer Variable**
3. Variable Name: `DLV - cta_text`
4. Data Layer Variable Name: `cta_text`
5. Save

---

## 🧪 Cómo Verificar

### Modo Preview en GTM
1. GTM dashboard → click **Preview** (arriba derecha)
2. Introduce URL de la web
3. Abre la web en otra ventana
4. Verás eventos en tiempo real en el panel de Preview

### GA4 DebugView
1. Instala extensión **GA4 DebugView** en Chrome
2. Activa Debug Mode
3. Visita la web
4. GA4 → Admin → DebugView → ves eventos en tiempo real

### Console del navegador (modo dev)
En desarrollo (`npm run dev`), los eventos se loguean también en consola:
```
[analytics] { event: 'cta_clicked', cta_text: 'Productos', ... }
```

---

## 📈 Conversiones Sugeridas (marcar en GA4)

Marcar como conversión en GA4 → Admin → Conversions:

1. **`form_submitted` (status=success)** — Lead capturado
2. **`product_interest`** — Interés en producto (potencial venta)
3. **`analysis_clicked`** — Engagement con contenido
4. **`social_clicked`** — Crecimiento social

---

## 🚨 Reglas Importantes

### NO trackear PII
- ❌ NO `user_email`, `user_phone`, `nombre`
- ✅ Solo IDs/categorías agregadas

### Naming consistency
- ✅ `snake_case` SIEMPRE
- ✅ `object_action` format (ej: `cta_clicked`, no `click_cta`)
- ❌ NO mezclar idiomas en nombres (todo inglés en eventos)

### Antes de añadir evento nuevo
1. Pregunta: **"¿Qué decisión me ayudará a tomar?"**
2. Si no hay respuesta clara → no lo añadas
3. Documenta aquí (Workflows/Analytics Tracking Plan.md)

---

## 🔗 Referencias

- Helper: `lib/analytics.ts`
- Page tracker: `components/PageViewTracker.tsx`
- GTM ID: `GTM-MWDXWXZN`
- Layout integration: `app/layout.tsx`
- [[../Project Root/STATUS|📊 STATUS]]
