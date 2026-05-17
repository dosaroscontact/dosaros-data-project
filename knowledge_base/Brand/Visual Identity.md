# 🎭 Brand — Visual Identity

**Filosofía**: Análisis de baloncesto basado en datos. Estética: dashboard analítico, no media deportiva.
**Personalidad**: Analítico · Preciso · Moderno · Visual. Nunca sensacionalista.

---

## 🎨 Paleta de Colores

| Token | HEX | Uso Principal |
|-------|-----|---------------|
| **Azul base** | `#0D1321` | Logo, titulares, números, gráficos principales |
| **Azul dark** | `#011E3B` | Backgrounds oscuros (frontend) |
| **Blanco** | `#FFFFFF` | Fondo posts, carruseles, visualizaciones |
| **Gris** | `#E6E8EE` | Ejes, divisores, cajas de stats, líneas |
| **Magenta** | `#B1005A` | Dato destacado, subcabeceras, highlights |
| **Naranja** | `#FF7D28` | CTAs, iconos, mapas de tiro, calor |
| **Naranja dark** | `#FF3E04` | Hover states, énfasis |
| **Naranja legacy** | `#F28C28` | (deprecated, no usar) |

### Distribución de Color
```
70% blanco · 20% azul · 7% gris · 2% magenta · 1% naranja
```

### Colores Plotly
- Theme: `plotly_white`
- Makes: `#88D4AB`
- Misses: `#FF8787`

---

## ✍️ Tipografías

| Uso | Fuente | Ubicación |
|-----|--------|-----------|
| Titulares / números grandes | **Space Grotesk** | `assets/static/SpaceGrotesk-*.ttf` |
| Texto / datos / etiquetas | **Inter** | `assets/static/Inter_*.ttf` |

---

## 📐 Estructura de Post (Redes Sociales)

```
[LOGO] → Titular / dato principal grande
         ↓
        Gráfico-contexto
         ↓
        Nota analítica breve
```

### Regla 3-1
**3 datos + 1 insight**. El protagonista es el dato, no el logo.

---

## 📊 Sistema de Gráficos (Solo 3 Tipos)

| Tipo | Uso | Estilo |
|------|-----|--------|
| **Línea** | Evolución histórica, tendencias | Línea azul, punto magenta |
| **Barras** | Comparativas jugadores/equipos | Barras azul, destacada magenta |
| **Distribución** | Mapas de tiro, zonas, calor | Naranja + gris, líneas gris |

### Reglas Visuales
- **Máximo**: 5 colores · 2 tipografías · 3 tipos de gráfico
- **Espacio en blanco**: Abundante
- **Sin decoración innecesaria**

---

## 📱 Frontend Web (Next.js)

### Tailwind Color Tokens
```js
{
  'dos-blue': '#0D1321',
  'dos-blue-dark': '#011E3B',
  'dos-orange': '#FF7D28',
  'dos-orange-dark': '#FF3E04',
  'dos-magenta': '#B1005A',
  'dos-white': '#FFFFFF',
  'dos-gray': '#E6E8EE',
}
```

### Componentes Visuales
- **Navbar**: Fixed top, fondo blanco/azul-dark, logo + lettering naranja
- **CTAs**: Naranja base con hover oscuro
- **Cards productos**: Border gris, hover naranja, scale 105%
- **Stories Telegram**: 1080×1920 con fondo color equipo + degradado

---

## 🎬 Imágenes Generadas (Stories Telegram)

- **Tamaño**: 1080×1920 px
- **Fondo**: Color primario del equipo + degradado
- **Recortes**: 80px inferior (eliminar watermark Google)
- **Chroma key**: `#00FF00` (verde) para extraer avatar

---

## 🔗 Referencias Cruzadas

- [[Avatar System|👤 Sistema de avatar generativo]]
- [[Design Tokens|🎨 Tokens detallados]]
- [[../Architecture/Landing Page Architecture|🖥️ Frontend Next.js]]

---

**Archivo fuente original**: `assets/docs/BRAND.md`
**Última actualización**: 2026-05-17
