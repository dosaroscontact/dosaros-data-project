# 🎯 GA4 — Configuración de Conversiones (Key Events)

**Property**: `dosaros.com`
**Measurement ID**: `G-EYPB37DEGE`
**Fecha**: 2026-05-18

---

## 🎯 Conversiones Recomendadas

De los 9 eventos custom que trackeamos, **3 son business outcomes reales** que deben marcarse como Key Events / Conversions:

| Conversión | Evento GA4 | Por qué importa | Valor sugerido |
|------------|-----------|-----------------|----------------|
| **🥇 Lead capturado** | `form_submitted` | Es el outcome final del funnel: alguien deja sus datos | 5€ |
| **🥈 Interés en producto** | `product_interest` | Intención de compra (click "Ver disponibilidad") | 2€ |
| **🥉 Engagement contenido** | `analysis_clicked` | Lector lee un análisis (KPI editorial principal) | 0.50€ |

### ¿Por qué NO marcar como conversion los otros?

| Evento | Razón |
|--------|-------|
| `page_view` | Demasiado genérico, GA4 lo trackea aparte |
| `nav_clicked` | Engagement intermedio, no outcome |
| `cta_clicked` | Mid-funnel, no final |
| `category_changed` | Exploración, no decisión |
| `tag_filter_clicked` | Filtro, no acción |
| `social_clicked` | Salida hacia otro sitio |

**Regla**: 2-4 conversiones por property. Si marcas 9, GA4 deja de dar señal clara.

---

## 📋 Cómo Configurarlas en GA4

### **Paso 1 — Acceso**

👉 https://analytics.google.com/

1. Property selector arriba → **dosaros.com**
2. **Admin** (engranaje abajo izquierda)

### **Paso 2 — Crear/Marcar Key Events**

En la columna **Property**:

1. Click **Data display** → **Events**
2. Verás lista de eventos detectados

#### Para cada conversión:

**Si el evento YA aparece en la lista** (porque ya se disparó al menos 1 vez):
- Click en el toggle **"Mark as key event"** a la derecha del evento

**Si NO aparece todavía** (porque aún no se ha disparado):
- Click botón **"Create event"** (arriba derecha)
- Custom event name: `form_submitted` (o el que sea)
- Matching conditions: dejar vacío (que matchee con cualquier event_name = form_submitted)
- Save
- Luego en la lista click toggle **"Mark as key event"**

### **Paso 3 — Eventos a marcar (uno por uno)**

```
✅ form_submitted   → Mark as key event
✅ product_interest → Mark as key event
✅ analysis_clicked → Mark as key event
```

### **Paso 4 — Asignar valor monetario** (opcional pero recomendado)

Para que GA4 te diga "esta campaña generó X€":

1. **Admin** → **Data display** → **Key events**
2. Click en el evento (ej: `form_submitted`)
3. Toggle **"Set default value"** ON
4. **Currency**: EUR
5. **Default value**: `5` (5€ por lead)
6. Save

Repetir para:
- `form_submitted` → 5€
- `product_interest` → 2€
- `analysis_clicked` → 0.50€ (opcional)

Estos valores son **estimaciones de ROI**. No es lo que cobras, es lo que vale ese tipo de acción para tu negocio.

---

## 🧪 Verificar que Funcionan

### **Test 1: Trigger un evento ahora mismo**

1. Abre https://www.dosaros.com en pestaña nueva (modo incógnito)
2. Click en "Productos" del menú → llegas a `/productos`
3. Click en cualquier "Ver disponibilidad" → llega a `/contact?product=...`
4. Rellena el formulario → submit

Esto dispara:
- `nav_clicked` (Productos)
- `product_interest`
- `form_submitted`

### **Test 2: Ver en GA4 Realtime**

1. GA4 → **Reports** → **Realtime**
2. Mira la sección **"Event count by Event name"**
3. Deberías ver tus eventos en <30 segundos

### **Test 3: Filtrar conversions**

1. GA4 → **Reports** → **Realtime**
2. En "Key event count by Event name"
3. Verás solo los 3 que marcaste

---

## 📊 Dónde Aparecen las Conversiones

Una vez marcadas, las verás en:

| Report | Qué muestra |
|--------|-------------|
| **Reports → Realtime** | Conversiones en tiempo real |
| **Reports → Engagement → Conversions** | Histórico por día |
| **Reports → Acquisition → Traffic acquisition** | Conversiones por fuente (instagram vs twitter) |
| **Advertising → Conversions** | Funnel + atribución |
| **Explore → Funnel exploration** | Crear funnel custom |

### Filtro útil: Conversiones por campaña launch

1. **Reports → Acquisition → Traffic acquisition**
2. Add filter → **Session campaign** = `launch_2026_05`
3. Cambiar métrica a **"Key events"**
4. Verás cuál plataforma trae más conversiones

---

## 🎯 KPIs Realistas Primera Semana

Para un lanzamiento de nicho (basket España) en redes orgánicas:

| Métrica | Esperado | Bueno | Excelente |
|---------|----------|-------|-----------|
| Sessions semana 1 | 100-300 | 500+ | 1000+ |
| `form_submitted` | 2-5 | 10+ | 25+ |
| `product_interest` | 10-30 | 50+ | 100+ |
| `analysis_clicked` | 30-80 | 150+ | 300+ |

**No te obsesiones con números absolutos**, mira:
- ¿La tendencia sube cada día?
- ¿Qué fuente convierte mejor?
- ¿Qué post genera más eventos?

---

## 🔁 Conversiones que Añadir Más Adelante

Cuando crezcas, considera añadir:

1. **`newsletter_signup`** — cuando conectes el newsletter a BD
2. **`product_purchase`** — si vendes online directo (no solo consulta)
3. **`scroll_75`** — engagement profundo (scroll >75% en artículo)
4. **`time_on_page_60s`** — lectura larga

Hoy NO los necesitas. Pre-medir es overkill.

---

## 🚨 Reglas Importantes

### NO hacer
- ❌ Marcar `page_view` como conversion (GA4 lo gestiona aparte)
- ❌ Marcar más de 4-5 conversiones
- ❌ Cambiar `event_name` después de configurar (rompe histórico)
- ❌ Trackear PII (email, teléfono) en eventos

### SÍ hacer
- ✅ Revisar conversiones semanalmente
- ✅ Asignar valores monetarios realistas
- ✅ Crear audiences basadas en conversions (más adelante)
- ✅ Mantener naming consistency (snake_case)

---

## 🔗 Referencias

- Tracking events: [[Analytics Tracking Plan]]
- UTM links: [[Launch UTM Tracking Links]]
- Plan social: [[Launch Social Plan]]
- GA4 Property ID: `G-EYPB37DEGE`
