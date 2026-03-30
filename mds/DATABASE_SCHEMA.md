# 🗄️ Database Schema - Dos Aros SQLite

**Documentación completa del esquema de la BBDD.**

---

## 📍 UBICACIÓN

```
/mnt/nba_data/dosaros_local.db
```

---

## 📊 TABLAS (3 principales)

---

## TABLE 1: `avatar_teams`

**Propósito:** Almacena equipos con sus características visuales para avatares

**Registros:** 67  
**Tamaño:** ~5 KB  
**Índices:** id (PK)

```sql
CREATE TABLE avatar_teams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team_name TEXT NOT NULL,
    postura TEXT NOT NULL,
    vestimenta TEXT NOT NULL,
    decorado TEXT NOT NULL,
    scene_type TEXT NOT NULL
);
```

### Columnas

| Columna | Tipo | Descripción | Ejemplo |
|---------|------|-----------|---------|
| `id` | INTEGER | ID único (autoincrement) | 1, 2, 3... |
| `team_name` | TEXT | Nombre del equipo | "Los Angeles Lakers" |
| `postura` | TEXT | Pose del avatar | "Dynamic jump" |
| `vestimenta` | TEXT | Jersey/outfit | "Los Angeles Lakers jersey" |
| `decorado` | TEXT | Escenario | "Modern NBA arena" |
| `scene_type` | TEXT | Tipo de escena | EDITORIAL, HISTORIC, ELITE, STREET, GAME |

### Scene Types Disponibles

```
EDITORIAL  (33 equipos) - Formal, profesional
HISTORIC   (13 equipos) - Estilo vintage
ELITE      (8 equipos)  - Premium, de lujo
STREET     (8 equipos)  - Urbano, casual
GAME       (6 equipos)  - Acción, durante partido
```

### Ejemplos de Registros

```sql
-- Lakers - EDITORIAL
| 1 | Los Angeles Lakers | Standing, confident | Lakers purple jersey | Modern NBA arena | EDITORIAL |

-- Celtics - HISTORIC
| 15 | Boston Celtics | Vintage pose | Celtics green retro | 1960s Boston Garden | HISTORIC |

-- Barcelona - ELITE
| 50 | FC Barcelona | Dynamic jump | Barcelona orange jersey | Palau Blaugrana | ELITE |
```

### Notas

- Algunos equipos tienen 2 registros (diferente scene_type)
- `postura` y `vestimenta` son textos descriptivos para prompts
- `decorado` describe el background
- NO hay URLs en esta tabla (URLs están en avatar_prompts)

---

## TABLE 2: `team_colors`

**Propósito:** Mapea colores primarios, secundarios y terciarios de cada equipo

**Registros:** 60 equipos  
**Tamaño:** ~3 KB  
**Índices:** id (PK), team_name (UNIQUE)

```sql
CREATE TABLE team_colors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team_name TEXT UNIQUE NOT NULL,
    primary_color TEXT NOT NULL,
    secondary_color TEXT NOT NULL,
    tertiary_color TEXT NOT NULL
);
```

### Columnas

| Columna | Tipo | Descripción | Ejemplo |
|---------|------|-----------|---------|
| `id` | INTEGER | ID único | 1, 2, 3... |
| `team_name` | TEXT | Nombre del equipo (UNIQUE) | "Los Angeles Lakers" |
| `primary_color` | TEXT | Color primario (HEX o nombre) | "#552583" o "Purple" |
| `secondary_color` | TEXT | Color secundario | "#FDB927" |
| `tertiary_color` | TEXT | Color terciario (opcional) | "#000000" |

### Ejemplos de Colores

```sql
-- Lakers
| 1 | Los Angeles Lakers | #552583 | #FDB927 | #000000 |
-- Celtics
| 2 | Boston Celtics | #007A33 | #FFFFFF | #BA3C1D |
-- Warriors
| 3 | Golden State Warriors | #1D428A | #FFC72C | #000000 |
-- Barcelona
| 30 | FC Barcelona | #00407B | #FFA700 | #000000 |
```

### Nota Importante

- Solo 60 equipos tienen colores definidos
- 8 equipos aún sin colores definidos (pendiente actualización)
- Colores pueden ser HEX, RGB o nombres
- UNIQUE constraint en team_name para evitar duplicados

---

## TABLE 3: `avatar_prompts` ⭐ PRINCIPAL

**Propósito:** Almacena prompts dinámicos para generar avatares con todas las URLs

**Registros:** 68  
**Tamaño:** ~150 KB  
**Índices:** id (PK), team_id (FK), team_name

```sql
CREATE TABLE avatar_prompts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team_id INTEGER NOT NULL,
    team_name TEXT NOT NULL,
    scene_type TEXT NOT NULL,
    avatar_variant INTEGER NOT NULL,
    avatar_url TEXT NOT NULL,
    logo_url TEXT NOT NULL,
    prompt_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    image_url TEXT,
    FOREIGN KEY(team_id) REFERENCES avatar_teams(id)
);
```

### Columnas

| Columna | Tipo | Descripción | Ejemplo |
|---------|------|-----------|---------|
| `id` | INTEGER | ID único | 1, 2, 3... |
| `team_id` | INTEGER | FK a avatar_teams.id | 1, 15, 50... |
| `team_name` | TEXT | Nombre del equipo | "Los Angeles Lakers" |
| `scene_type` | TEXT | Tipo de escena | "EDITORIAL" |
| `avatar_variant` | INTEGER | Variante 1-4 | 1, 2, 3, o 4 |
| `avatar_url` | TEXT | URL al avatar base en GitHub | https://github.com/.../avatar_base_1.png |
| `logo_url` | TEXT | URL al logo en GitHub | https://github.com/.../logoDosAros.png |
| `prompt_text` | TEXT | PROMPT COMPLETO para ImageFX | "A cinematic, ultra-realistic..." |
| `created_at` | TIMESTAMP | Marca de tiempo creación | 2026-03-29 15:44:45 |
| `image_url` | TEXT | URL a imagen generada (opcional) | /home/pi/assets/generated/lakers.png |

### Ejemplo de Registro Completo

```sql
INSERT INTO avatar_prompts VALUES (
    1,
    1,
    'Los Angeles Lakers',
    'EDITORIAL',
    2,
    'https://github.com/dosaroscontact/dosaros-data-project/raw/main/assets/avatars/avatars_base/avatar_base_2_action_jump.png',
    'https://github.com/dosaroscontact/dosaros-data-project/raw/main/assets/avatars/logos_base/logoDosAros.png',
    'A cinematic, ultra-realistic, photorealistic full-body render.

AVATAR: Use the exact avatar from https://github.com/... as the base reference. Maintain 100% identity consistency (face, beard, sunglasses, proportions).

POSE: Dynamic jump, mid-action, confident expression

OUTFIT: Los Angeles Lakers jersey. Colors: Primary #552583 (Purple), Secondary #FDB927 (Gold), Tertiary #000000 (Black)

SCENE: Modern NBA arena with warm dramatic lighting

LOGO: Include the Dos Aros logo naturally blended

RENDER: Ultra-realistic 3D, Pixar-quality, 8K, sharp focus, global illumination, PBR materials.

BACKGROUND: Solid chroma key green (#00FF00), perfectly uniform, no gradients.

FRAMING: Full body visible, centered, no cropping.',
    '2026-03-29 15:44:45',
    NULL
);
```

### Avatar Variants (Mapeo)

```
1 → avatar_base_1_standing_casual.png    (Standing casual, sonriente)
2 → avatar_base_2_action_jump.png        (Action jump, dinámico)
3 → avatar_base_3_upper_body.png         (Upper body, busto)
4 → avatar_base_4_standing_gorro.png     (Con gorro, gafas amarillas)
```

### Logo URL Assignment (por scene_type)

```
EDITORIAL → logo_transparent   (logoDosAros.png)
HISTORIC  → logo_transparent
GAME      → logo_transparent
ELITE     → logo_neon_azul     (logoLetrasAzul.png)
STREET    → logo_neon_azul
```

---

## 🔗 RELACIONES

```
avatar_teams (67 registros)
    ↓ team_name
team_colors (60 equipos)
    ↓ team_name
avatar_prompts (68 registros)
    ↓ usa avatar_url, logo_url, colores
Genera imagen final
```

---

## 📈 ESTADÍSTICAS

```sql
-- Total de registros por tabla
SELECT 'avatar_teams' as tabla, COUNT(*) FROM avatar_teams
UNION ALL
SELECT 'team_colors', COUNT(*) FROM team_colors
UNION ALL
SELECT 'avatar_prompts', COUNT(*) FROM avatar_prompts;

-- Resultado esperado:
avatar_teams     67
team_colors      60
avatar_prompts   68
```

---

## 🔍 QUERIES ÚTILES

### 1. Ver prompt completo de un equipo

```sql
SELECT team_name, scene_type, avatar_variant, prompt_text
FROM avatar_prompts
WHERE team_name LIKE '%Lakers%'
LIMIT 1;
```

### 2. Equipos sin colores definidos

```sql
SELECT ap.team_name
FROM avatar_prompts ap
WHERE ap.team_name NOT IN (SELECT team_name FROM team_colors)
GROUP BY ap.team_name;
```

### 3. Distribución de escenas

```sql
SELECT scene_type, COUNT(*) as count
FROM avatar_prompts
GROUP BY scene_type
ORDER BY count DESC;
```

### 4. Avatar variants distribution

```sql
SELECT avatar_variant, COUNT(*) as count
FROM avatar_prompts
GROUP BY avatar_variant
ORDER BY avatar_variant;
```

### 5. Prompts sin imagen generada

```sql
SELECT team_name, scene_type
FROM avatar_prompts
WHERE image_url IS NULL
ORDER BY team_name;
```

### 6. Prompt aleatorio

```sql
SELECT team_name, prompt_text
FROM avatar_prompts
ORDER BY RANDOM()
LIMIT 1;
```

### 7. Verificar integridad (FKs)

```sql
SELECT ap.team_id, ap.team_name, at.team_name
FROM avatar_prompts ap
LEFT JOIN avatar_teams at ON ap.team_id = at.id
WHERE at.id IS NULL;
-- Debe devolver 0 filas
```

---

## 🔧 OPERACIONES COMUNES

### Insertar nuevo prompt

```sql
INSERT INTO avatar_prompts (
    team_id, team_name, scene_type, avatar_variant,
    avatar_url, logo_url, prompt_text, created_at
) VALUES (
    1, 'Los Angeles Lakers', 'EDITORIAL', 2,
    'https://github.com/...', 'https://github.com/...',
    'Prompt text here...', datetime('now')
);
```

### Actualizar imagen generada

```sql
UPDATE avatar_prompts
SET image_url = '/path/to/image.png'
WHERE team_name = 'Los Angeles Lakers' AND scene_type = 'EDITORIAL';
```

### Agregar colores a equipo

```sql
INSERT INTO team_colors (team_name, primary_color, secondary_color, tertiary_color)
VALUES ('Team Name', '#000000', '#FFFFFF', '#FF0000');
```

### Regenerar todos los prompts

```sql
DELETE FROM avatar_prompts;
-- Luego ejecutar avatar_prompt_generator.py
```

### Verificar datos completos de un equipo

```sql
SELECT
    at.team_name,
    at.scene_type,
    tc.primary_color,
    tc.secondary_color,
    ap.prompt_text,
    ap.avatar_url,
    ap.logo_url
FROM avatar_prompts ap
LEFT JOIN avatar_teams at ON ap.team_id = at.id
LEFT JOIN team_colors tc ON ap.team_name = tc.team_name
WHERE ap.team_name = 'Los Angeles Lakers'
LIMIT 1;
```

---

## 🚨 MANTENIMIENTO

### Backup regular

```bash
# En Pi
cp /mnt/nba_data/dosaros_local.db /mnt/nba_data/dosaros_local.db.backup_$(date +%Y%m%d_%H%M%S)
```

### Verificar integridad

```bash
sqlite3 /mnt/nba_data/dosaros_local.db "PRAGMA integrity_check;"
# Debe devolver: ok
```

### Limpiar registros huérfanos

```sql
DELETE FROM avatar_prompts
WHERE team_id NOT IN (SELECT id FROM avatar_teams);
```

### Vacío de espacio

```sql
VACUUM;
```

---

## 📝 NOTAS IMPORTANTES

1. **FK constraint:** avatar_prompts.team_id → avatar_teams.id
2. **UNIQUE constraint:** team_colors.team_name (no duplicados)
3. **DEFAULT:** avatar_prompts.created_at = CURRENT_TIMESTAMP
4. **Nullable:** image_url (se llena después de generar)
5. **Text length:** prompt_text puede ser muy largo (~2000 chars)
6. **UTF-8:** Todo en UTF-8 (caracteres españoles soportados)

---

## 🔐 SEGURIDAD

### Nunca:
```sql
-- ❌ Hardcodear valores en SQL
WHERE team_name = 'Lakers'

-- ✅ Usar parametrización
WHERE team_name = ?
cursor.execute(query, (team_name,))
```

### Siempre:
```python
# ✅ Usar prepared statements
cursor.execute('SELECT * FROM avatar_prompts WHERE team_name = ?', (team_name,))

# ✅ Validar input
if not team_name or len(team_name) > 100:
    raise ValueError("Invalid team_name")
```

---

## 📞 SOPORTE

**Si BBDD está corrupta:**
```bash
# Verificar integridad
sqlite3 /mnt/nba_data/dosaros_local.db "PRAGMA integrity_check;"

# Reparar si es necesario
sqlite3 /mnt/nba_data/dosaros_local.db ".recover" | sqlite3 repaired.db

# Restaurar desde backup
cp /mnt/nba_data/dosaros_local.db.backup /mnt/nba_data/dosaros_local.db
```

---

**Versión:** 1.0  
**Última actualización:** 2026-03-29  
**Herramienta:** SQLite 3.x
