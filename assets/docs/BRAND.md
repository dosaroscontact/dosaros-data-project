# Dos Aros — Brand Reference

## Identidad
Análisis de baloncesto basado en datos. Estética: dashboard analítico, no media deportiva.
Personalidad: analítico · preciso · moderno · visual. Nunca sensacionalista.

## Paleta
| Token       | HEX     | Uso                                          |
|-------------|---------|----------------------------------------------|
| Azul base   | #0D1321 | Logo, titulares, números, gráficos principales |
| Blanco      | #FFFFFF | Fondo posts, carruseles, visualizaciones      |
| Gris        | #E6E8EE | Ejes, divisores, cajas de stats, líneas       |
| Magenta     | #B1005A | Dato destacado, subcabeceras, highlights      |
| Naranja     | #F28C28 | Iconos, mapas de tiro, calor, detalles sport  |

Distribución: 70% blanco · 20% azul · 7% gris · 2% magenta · 1% naranja.

Plotly: `plotly_white` · Makes `#88D4AB` · Misses `#FF8787`

## Tipografías
- **Titulares / números grandes**: Space Grotesk (bundled en `assets/static/SpaceGrotesk-*.ttf`)
- **Texto / datos / etiquetas**: Inter (bundled en `assets/static/Inter_*.ttf`)

## Estructura de post
```
[LOGO] titular / dato principal grande / gráfico-contexto / nota analítica
```
Regla 3-1: 3 datos + 1 insight. El protagonista es el dato, no el logo.

## Sistema de gráficos (solo 3 tipos)
| Tipo      | Uso                                  | Estilo                         |
|-----------|--------------------------------------|--------------------------------|
| Línea     | Evolución histórica, tendencias      | Línea azul, punto magenta      |
| Barras    | Comparativas jugadores/equipos       | Barras azul, destacada magenta |
| Distribución | Mapas de tiro, zonas, calor       | Naranja + gris, líneas gris    |

Máximo: 5 colores · 2 tipografías · 3 tipos de gráfico · espacio en blanco abundante.

## Avatar — Sistema de imagen
**Identidad LOCKED**: Hombre ~35 años, calvo, barba oscura corta, gafas negras, tono olivo.
Camiseta negra + número 7 rojo (outline blanco) + franja diagonal rojo-blanco-rojo.
Vaqueros slim, smartwatch negro muñeca izquierda, pulseras oscuras muñeca derecha.
Fondo: chroma key verde #00FF00. Render: Pixar 3D, 8K, PBR, iluminación estudio.
Midjourney: `--ar 2:3 --v 6 --style raw --q 2 --s 250`

**Marca en imagen**: "DOS AROS" como graffiti recoloreado en colores del equipo.

## Dimensiones avatar (BD `dosaros_local.db`)
- `teams_metadata` — 54 equipos (30 NBA + 24 Euro) con color_primary/secondary/accent
- `dim_posturas` — 50 posturas
- `dim_vestimentas` — 50 vestimentas
- `dim_decorados` — 61 decorados/entornos
- `dim_tipos_logo` — 56 estilos de logo
- `avatar_teams` — 68 variaciones detalladas (team_code, postura, vestimenta, decorado, logo, variacion_idx)

**Combinaciones posibles**: 452,620,000

**Generador SQL de prompt aleatorio**:
```sql
SELECT 'Avatar ' || t.name || ' | ' || t.color_primary || '/' || t.color_secondary ||
       ' | Postura: ' || p.valor || ' | Vest: ' || v.valor ||
       ' | Deco: ' || d.valor || ' | Logo: ' || l.valor
FROM teams_metadata t,
     (SELECT valor FROM dim_posturas    ORDER BY RANDOM() LIMIT 1) p,
     (SELECT valor FROM dim_vestimentas ORDER BY RANDOM() LIMIT 1) v,
     (SELECT valor FROM dim_decorados   ORDER BY RANDOM() LIMIT 1) d,
     (SELECT valor FROM dim_tipos_logo  ORDER BY RANDOM() LIMIT 1) l
ORDER BY RANDOM() LIMIT 1;
```

**Generador Python**:
```python
from src.processors.avatar_prompt_generator import generar_prompt_avatar, generar_prompts_liga
r = generar_prompt_avatar("LAL")          # equipo concreto
r = generar_prompt_avatar("LAL", variacion=2)
todos = generar_prompts_liga("NBA")       # toda la liga
```
