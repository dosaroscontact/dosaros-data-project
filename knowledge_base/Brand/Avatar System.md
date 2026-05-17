# 👤 Avatar System — Sistema Generativo

**Total combinaciones posibles**: **452,620,000**

---

## 🎭 Identidad del Avatar (LOCKED)

**Personaje**: Hombre ~35 años
- Calvo
- Barba oscura corta
- Gafas negras
- Tono olivo

**Vestimenta base**:
- Camiseta negra
- Número 7 rojo (outline blanco)
- Franja diagonal rojo-blanco-rojo
- Vaqueros slim
- Smartwatch negro (muñeca izquierda)
- Pulseras oscuras (muñeca derecha)

**Render**:
- Fondo: chroma key verde `#00FF00`
- Estilo: Pixar 3D, 8K, PBR, iluminación estudio

**Parámetros Midjourney**:
```
--ar 2:3 --v 6 --style raw --q 2 --s 250
```

---

## 🎨 Marca en Imagen

**"DOS AROS"** como graffiti recoloreado en los colores oficiales del equipo.

---

## 🗄️ Dimensiones en BD (`dosaros_local.db`)

| Tabla | Filas | Descripción |
|-------|-------|-------------|
| `teams_metadata` | 54 | 30 NBA + 24 Euro con `color_primary`/`secondary`/`accent` |
| `dim_posturas` | 50 | Posturas del avatar |
| `dim_vestimentas` | 50 | Variantes de ropa |
| `dim_decorados` | 61 | Entornos/decorados |
| `dim_tipos_logo` | 56 | Estilos de logo |
| `avatar_teams` | 68 | Variaciones detalladas pre-curadas |

**Cálculo**: 54 × 50 × 50 × 61 × 56 = **452,620,000 combinaciones**

---

## 🧮 Generadores

### SQL — Prompt Aleatorio
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

### Python — Generador Programático
```python
from src.processors.avatar_prompt_generator import (
    generar_prompt_avatar,
    generar_prompts_liga
)

# Equipo concreto
r = generar_prompt_avatar("LAL")

# Equipo con variación específica
r = generar_prompt_avatar("LAL", variacion=2)

# Todos los equipos de la liga
todos = generar_prompts_liga("NBA")
todos = generar_prompts_liga("EUR")
```

---

## 🤖 Bot Telegram — Comandos Avatar

| Comando | Resultado |
|---------|-----------|
| `/avatar_prompt LAL` | Prompt Midjourney para Lakers |
| `/avatar_random` | Prompt aleatorio |
| `/avatar` | Alias de `/avatar_random` |
| `/avatars` | 5 prompts aleatorios del día |
| `/avatar_today` | Alias de `/avatars` |

---

## 📂 Flujo de Generación Completo

```
teams_metadata (54 equipos)
    × dim_posturas (50)
    × dim_vestimentas (50)
    × dim_decorados (61)
    × dim_tipos_logo (56)
    ↓
avatar_prompt_generator.py
    ↓
Prompt Midjourney/ImageFX
    ↓
Imagen generada (con chroma key verde)
    ↓
image_generator.py
    ↓
Story 1080×1920 Telegram
```

---

## 🔗 Referencias

- [[Visual Identity|🎭 Identidad visual completa]]
- [[../Data/Data Dictionary|📖 Diccionario de datos]]
- [[../Workflows/Daily Automation|⏰ Cron diario]]

---

**Archivo fuente**: `src/processors/avatar_prompt_generator.py`
**Tablas en BD**: `teams_metadata`, `dim_*`, `avatar_teams`
