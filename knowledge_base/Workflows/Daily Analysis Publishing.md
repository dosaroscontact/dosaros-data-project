# 📰 Daily Analysis Publishing

**Objetivo**: Publicar análisis diarios markdown en la web con flujo automatizado.

---

## 🎯 Arquitectura

```
Downloads/DOS_AROS_ANALISIS_DD_MES_YYYY.md  (tu escribe)
              ↓
   python scripts/publish_analysis.py <archivo>
              ↓
content/analysis/YYYY/MM/YYYY-MM-DD-slug.md  (frontmatter generado)
              ↓
   git push origin main
              ↓
Next.js build → /analisis (lista) + /analisis/[slug] (artículo)
```

---

## 📂 Estructura de Archivos

```
content/
└── analysis/
    └── 2026/
        └── 05/
            └── 2026-05-16-spurs-139-timberwolves-109.md
            └── 2026-05-17-...md
```

---

## 📝 Formato del Archivo (Frontmatter)

Generado automáticamente por el script:

```yaml
---
date: "2026-05-16"
title: "SPURS 139 - TIMBERWOLVES 109 · EUROLIGA"
slug: 2026-05-16-spurs-139-timberwolves-109
summary: "Stephon Castle metió 32 puntos para cerrar..."
tags: [NBA, EuroLeague, Playoffs, FinalFour]
sections:
  - league: NBA
    icon: "🇺🇸"
    title: "SPURS 139 - TIMBERWOLVES 109"
    subtitle: "Game 6"
  - league: EuroLeague
    icon: "🇪🇺"
    title: "EUROLIGA"
    subtitle: "FINAL FOUR ATENAS — 22 y 24 de mayo"
published: true
---

# 🏀 DOS AROS — 16 de mayo de 2026

## 🇺🇸 SPURS 139 - TIMBERWOLVES 109 | Game 6

Stephon Castle metió 32 puntos...
```

### Convención del archivo fuente
- **Nombre**: `DOS_AROS_ANALISIS_DD_MES_YYYY[_Vx].md` (en español, con mes en palabras)
- **Primera línea**: `# 🏀 DOS AROS — DD de MES de YYYY`
- **Secciones**: H2 con emoji bandera + título (opcional `| subtítulo`)
- **Cuerpo**: Markdown estándar, párrafos separados por línea en blanco

---

## 🔧 Comandos

### Publicar análisis (workflow normal)
```bash
python scripts/publish_analysis.py DOS_AROS_ANALISIS_17_MAYO_2026.md
```
El script:
1. Lee de `~/Downloads/` (si solo das el nombre)
2. Detecta fecha (filename + content)
3. Genera frontmatter automáticamente:
   - Slug basado en primera sección
   - Tags detectados por keywords (NBA, EuroLeague, Playoffs, etc.)
   - Summary del primer párrafo
4. Guarda en `content/analysis/YYYY/MM/YYYY-MM-DD-slug.md`
5. Hace `git add` y `git commit`
6. Pregunta si hacer `git push`

### Dry-run (preview sin escribir)
```bash
python scripts/publish_analysis.py archivo.md --dry-run
```

### Sin commit automático
```bash
python scripts/publish_analysis.py archivo.md --no-commit
```

### Con ruta completa
```bash
python scripts/publish_analysis.py /ruta/completa/archivo.md
```

---

## 🌐 URLs de la Web

| URL | Contenido |
|-----|-----------|
| `/analisis` | Listado cronológico de todos los análisis |
| `/analisis?tag=NBA` | Filtrado por tag |
| `/analisis/2026-05-16-spurs-139-timberwolves-109` | Artículo individual |

---

## 🎨 Renderizado

### Componentes
- `components/AnalysisList.tsx` — Listado con cards + filtros por tag
- `components/AnalysisArticle.tsx` — Artículo individual con prose styling

### Estilos
- Clase CSS: `.prose-dos-aros` en `app/globals.css`
- Tipografías: Space Grotesk (titulares) + Inter (body)
- H1: línea inferior gris
- H2: línea izquierda naranja + texto naranja
- H3: magenta
- Italic: magenta
- Links: naranja
- HR: gradiente sutil
- Tablas: header naranja, bordes grises

### Animaciones
- Stagger fade-in en la lista de cards (0.08s entre cada)
- Fade-in del artículo individual
- Respeta `prefers-reduced-motion`

---

## 🏷️ Tags Detectados Automáticamente

El script reconoce estos tags por keywords en el contenido:

| Tag | Palabras clave |
|-----|----------------|
| NBA | NBA, Spurs, Lakers, Celtics, Warriors, Wolves, Thunder, Knicks, Heat, Bucks |
| EuroLeague | EuroLeague, Euroliga, Real Madrid, Barcelona, Valencia, Olympiacos, Panathinaikos, Fenerbahçe, Žalgiris |
| Playoffs | Playoffs, Game 1-7, serie |
| FinalFour | Final Four, F4, Atenas |
| Finales | Finales, Conference Finals, NBA Finals |
| RegularSeason | regular season, temporada regular |

Para añadir tags: editar `TAG_KEYWORDS` en `scripts/publish_analysis.py`.

---

## ⚙️ Stack Técnico

| Componente | Librería |
|-----------|----------|
| Parser frontmatter | `gray-matter` |
| Renderer markdown | `react-markdown` + `remark-gfm` |
| Lectura de archivos | `fs` + `path` (Node) |
| Build | Next.js 15 (static al build time) |
| Generación estática | `generateStaticParams` en `[slug]/page.tsx` |

---

## 🚀 Despliegue

Cada `git push origin main` que toque `content/analysis/**`:
1. Triggea rebuild en Vercel/host
2. Genera páginas estáticas para cada análisis
3. Disponible en producción en ~2 minutos

---

## 🐛 Troubleshooting

### El script no detecta la fecha
- Verificar que el nombre tiene formato `DD_MES_YYYY` (con guiones bajos)
- Verificar que el H1 del archivo tiene "DD de MES de YYYY"
- Si falla: usa fecha de hoy (puedes editar el frontmatter después)

### Tags incorrectos o faltantes
- Editar `TAG_KEYWORDS` en `scripts/publish_analysis.py`
- O editar manualmente el frontmatter después

### Caracteres raros (\\-, \\.)
- El script ya limpia escapes markdown automáticamente
- Si quedan: editar manualmente

### YAML date parseada como Date object
- Ya solucionado: el script escribe la fecha entre comillas
- Si tienes un .md viejo: añade comillas manualmente: `date: "2026-05-16"`

---

## 🔗 Referencias

- Script: `scripts/publish_analysis.py`
- Lib lectura: `lib/analysis.ts`
- Componentes: `components/AnalysisList.tsx`, `components/AnalysisArticle.tsx`
- Páginas: `app/analisis/page.tsx`, `app/analisis/[slug]/page.tsx`
- Estilos: `.prose-dos-aros` en `app/globals.css`
- [[../Project Root/STATUS|📊 STATUS]]
- [[../Architecture/Decisions Log|📝 ADRs]]
