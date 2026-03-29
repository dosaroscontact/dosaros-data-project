# 🎯 Sistema de Generación de Avatares Dos Aros - Documentación Completa

**Fecha:** Marzo 29, 2026  
**Estado:** FUNCIONAL (generación de prompts completada, imagen aún en desarrollo)

---

## 📋 Tabla de Contenidos

1. [Arquitectura General](#arquitectura-general)
2. [Componentes del Sistema](#componentes-del-sistema)
3. [Base de Datos](#base-de-datos)
4. [URLs de Recursos](#urls-de-recursos)
5. [Scripts Principales](#scripts-principales)
6. [Flujo de Generación](#flujo-de-generación)
7. [Próximos Pasos](#próximos-pasos)
8. [Troubleshooting](#troubleshooting)

---

## 🏗️ Arquitectura General

```
Windows (Local)
    ↓
GitHub (dosaros-data-project)
    ↓
Raspberry Pi (192.168.1.136)
    ├── /mnt/nba_data/dosaros_local.db (SQLite)
    ├── /home/pi/assets/avatars_base/ (4 variantes)
    ├── /home/pi/assets/generated/ (imágenes finales)
    └── Scripts Python (generación)
    ↓
Vertex AI (Google Cloud) [PENDIENTE]
    ↓
Cloud Storage + Local Storage
```

---

## 🎨 Componentes del Sistema

### 1. **Avatar Base (4 Variantes)**

Ubicación en GitHub: `/assets/avatars/avatars_base/`

| Variante | Archivo | Descripción |
|----------|---------|-------------|
| 1 | `avatar_base_1_standing_casual.png` | Standing casual, sonriente, gafas oscuras, full body |
| 2 | `avatar_base_2_action_jump.png` | Action jump, sonriente, gafas oscuras, full body |
| 3 | `avatar_base_3_upper_body.png` | Upper body, busto, gafas, sonriente |
| 4 | `avatar_base_4_standing_gorro.png` | Standing con gorro, gafas amarillas, sonriente |

**Características comunes:**
- Edad: ~35 años
- Aspecto: Calvo, barba oscura corta, piel oliva
- Expresión: Sonriente, confiado
- Smartwatch negro en muñeca izquierda
- Pulseras oscuras en muñeca derecha

### 2. **Logos Base**

Ubicación en GitHub: `/assets/avatars/logos_base/`

| Logo | Archivo | Uso |
|------|---------|-----|
| Transparent | `logoDosAros.png` | EDITORIAL, HISTORIC, GAME |
| Neon Azul | `logoLetrasAzul.png` | ELITE, STREET |

---

## 🗄️ Base de Datos

### Ubicación
```
/mnt/nba_data/dosaros_local.db
```

### Tablas Creadas

#### 1. `avatar_teams` (67 registros)

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

**Distribución por scene_type:**
- EDITORIAL: 33 equipos
- HISTORIC: 13 equipos
- ELITE: 8 equipos
- GAME: 6 equipos
- STREET: 8 equipos

**Nota:** Algunos equipos tienen 2 registros (diferentes escenas)

#### 2. `team_colors` (30 equipos)

```sql
CREATE TABLE team_colors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team_name TEXT UNIQUE NOT NULL,
    primary_color TEXT NOT NULL,
    secondary_color TEXT NOT NULL,
    tertiary_color TEXT NOT NULL
);
```

**Equipos con colores definidos:**
- 20 NBA teams
- 10 EuroLeague teams

#### 3. `avatar_prompts` (31 registros)

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
    FOREIGN KEY(team_id) REFERENCES avatar_teams(id)
);
```

**Contenido:**
- 31 prompts generados (1 por equipo con colores definidos)
- Cada prompt es único (variante avatar aleatoria, colores del equipo)
- Logo asignado según scene_type

---

## 🔗 URLs de Recursos

### Avatar Base URLs

```
VARIANTE 1: https://github.com/dosaroscontact/dosaros-data-project/raw/main/assets/avatars/avatars_base/avatar_base_1_standing_casual.png

VARIANTE 2: https://github.com/dosaroscontact/dosaros-data-project/raw/main/assets/avatars/avatars_base/avatar_base_2_action_jump.png

VARIANTE 3: https://github.com/dosaroscontact/dosaros-data-project/raw/main/assets/avatars/avatars_base/avatar_base_3_upper_body.png

VARIANTE 4: https://github.com/dosaroscontact/dosaros-data-project/raw/main/assets/avatars/avatars_base/avatar_base_4_standing_gorro.png
```

### Logo URLs

```
TRANSPARENT: https://github.com/dosaroscontact/dosaros-data-project/raw/main/assets/avatars/logos_base/logoDosAros.png

NEON AZUL: https://github.com/dosaroscontact/dosaros-data-project/raw/main/assets/avatars/logos_base/logoLetrasAzul.png
```

---

## 📝 Scripts Principales

### 1. `create_avatar_prompts_table.py`

**Propósito:** Crear tabla `avatar_prompts` en BBDD

```python
# Ejecutar una sola vez en el Pi
python create_avatar_prompts_table.py
```

### 2. `crear_team_colors.py`

**Propósito:** Crear tabla `team_colors` en BBDD

```python
# Ejecutar una sola vez en el Pi
python crear_team_colors.py
```

### 3. `parse_team_colors.py`

**Propósito:** Parsear documento de colores y generar CSV limpio

**Ubicación:** Windows  
**Entrada:** `assets/data/team_colors.csv` (texto desordenado)  
**Salida:** `assets/data/team_colors_clean.csv` (CSV estructurado)

```bash
# En Windows
python parse_team_colors.py
```

**Resultado:** 30 equipos parseados

### 4. `load_team_colors_to_db.py`

**Propósito:** Cargar colores de CSV a BBDD

**Ubicación:** Pi  
**Entrada:** `assets/data/team_colors_clean.csv`

```bash
# En el Pi
python load_team_colors_to_db.py
```

**Resultado:** 30 colores cargados en `team_colors`

### 5. `avatar_prompt_generator.py` ⭐ **PRINCIPAL**

**Propósito:** Generar prompts dinámicos para Google ImageFX

**Ubicación:** Pi  
**Entrada:** `avatar_teams` + `team_colors`  
**Salida:** 31 prompts en tabla `avatar_prompts`

```bash
# En el Pi
python avatar_prompt_generator.py
```

**Lógica:**
1. Obtiene cada equipo con colores definidos
2. Selecciona avatar variante aleatoria (1-4)
3. Asigna logo según scene_type (ELITE/STREET → neon, otros → transparent)
4. Reemplaza placeholders en template
5. Inserta en `avatar_prompts`

**Estructura de Prompt:**
```
A cinematic, ultra-realistic, photorealistic full-body render.

AVATAR: Use the exact avatar from {AVATAR_URL} as the base reference. 
Maintain 100% identity consistency (face, beard, sunglasses, proportions).

POSE: {POSTURA}

OUTFIT: {VESTIMENTA}. Colors: Primary {PRIMARY_COLOR}, Secondary {SECONDARY_COLOR}, Tertiary {TERTIARY_COLOR}

SCENE: {DECORADO}. Cinematic lighting, realistic depth, warm tones.

LOGO: Include the Dos Aros logo from {LOGO_URL} naturally blended in the scene without modification.

RENDER: Ultra-realistic 3D, Pixar-quality, 8K, sharp focus, global illumination, PBR materials.

BACKGROUND: Solid chroma key green (#00FF00), perfectly uniform, no gradients.

FRAMING: Full body visible, centered, no cropping.
```

---

## 🔄 Flujo de Generación

### Paso 1: Preparación (COMPLETADO ✅)

```
1. Crear tablas BBDD
   ├── avatar_teams (67 registros)
   ├── team_colors (30 equipos)
   └── avatar_prompts (vacía)

2. Cargar datos
   ├── avatar_teams desde CSV
   ├── team_colors desde documento parseado
   └── Ready

3. Subir assets a GitHub
   ├── 4 avatares base
   └── 2 logos base
```

### Paso 2: Generación de Prompts (COMPLETADO ✅)

```
1. Ejecutar avatar_prompt_generator.py
   ├── Leer avatar_teams + team_colors
   ├── Generar prompt dinámico por equipo
   ├── Asignar avatar variante aleatoria
   ├── Asignar logo según scene_type
   └── Insertar en avatar_prompts (31 registros)
```

### Paso 3: Generación de Imágenes (PENDIENTE ⏳)

```
1. Configura Vertex AI + Cloud Storage
   ├── Service Account credentials
   └── GCS bucket para almacenar imágenes

2. Crear script image_generator.py
   ├── Leer prompts de avatar_prompts
   ├── Llamar Vertex AI Image Generation API
   ├── Descargar imagen generada
   ├── Guardar localmente en /home/pi/assets/generated/
   ├── Guardar en GCS (opcional)
   └── Actualizar tabla avatar_prompts con image_url

3. Integrar Telegram bot
   ├── Bot envía imágenes generadas a canal review
   ├── Usuario aprueba/rechaza
   ├── Si aprueba: marcar como ready_to_publish
   └── Si rechaza: generar con variante diferente
```

### Paso 4: Publicación (PENDIENTE ⏳)

```
1. Generar contenido social
   ├── Crear cards Instagram Stories
   ├── Crear posts X/Twitter
   └── Crear carruseles LinkedIn

2. Publicar en redes
   ├── Instagram (manual o Remotion)
   ├── X/Twitter (API)
   └── LinkedIn (API)
```

---

## 📊 Estadísticas Actuales

| Métrica | Valor |
|---------|-------|
| Equipos totales en sistema | 68 |
| Equipos con escenas definidas | 67 |
| Equipos con colores | 30 |
| Prompts generados | 31 |
| Avatares base creados | 4 |
| Logos base creados | 2 |
| Imágenes generadas | 0 (pendiente Vertex AI) |

---

## 🚀 Próximos Pasos

### FASE 1: Imagen Generation (Semana 1)

- [ ] Configurar Google Cloud (Vertex AI + GCS)
- [ ] Crear `image_generator.py`
- [ ] Generar primeras 5 imágenes de prueba
- [ ] Validar calidad

### FASE 2: Telegram Integration (Semana 2)

- [ ] Crear comando `/avatar_gen` en bot
- [ ] Implementar canal de review
- [ ] Crear tabla `image_approval_queue`
- [ ] Integrar aprobación/rechazo

### FASE 3: Automatización (Semana 3)

- [ ] Crear cron job para generación diaria
- [ ] Implementar `master_sync.py` actualizado
- [ ] Automatizar publicación en redes
- [ ] Dashboard de estadísticas

### FASE 4: Escalado (Semana 4+)

- [ ] Generar avatares para 68 equipos (solo 30 ahora)
- [ ] Crear múltiples escenas por equipo
- [ ] Integración con Remotion para videos
- [ ] Analytics de rendimiento

---

## 🔧 Troubleshooting

### Problema: "FileNotFoundError: team_colors_clean.csv"

**Solución:**
```bash
# En Windows, hacer push a GitHub
git add assets/data/team_colors_clean.csv
git commit -m "Add clean team colors"
git push

# En el Pi
git pull origin main
```

### Problema: Avatar no mantiene identidad

**Causa:** Avatar URL incorrecta o variante no encontrada  
**Solución:** Verificar URLs en `avatar_prompt_generator.py`

### Problema: Logo incorrecto en escena

**Causa:** scene_type no mapeado correctamente  
**Solución:** Verificar función `get_logo_url()` en `avatar_prompt_generator.py`

---

## 📚 Referencias

- **Repositorio:** https://github.com/dosaroscontact/dosaros-data-project
- **BBDD:** `/mnt/nba_data/dosaros_local.db`
- **Documentación Avatar:** `/assets/avatar_generation_guide.md`
- **Brand Guide:** `/assets/docs/BRAND.md`

---

**Último actualizado:** Marzo 29, 2026  
**Por:** Claude + Robe  
**Estado:** FUNCIONAL - Fase 1 completada ✅
