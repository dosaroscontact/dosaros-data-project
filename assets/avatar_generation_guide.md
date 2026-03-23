# Guía de Generación de Avatares — Dos Aros

Referencia para crear nuevos avatares consistentes con el personaje del proyecto
usando **Google ImageFX** (https://labs.google/fx/tools/image-fx).

---

## 1. Cómo usar Google ImageFX con imagen de referencia

1. Ve a https://labs.google/fx/tools/image-fx
2. Haz clic en el icono de imagen (📎) o en **"Add image"** en la barra de prompt
3. Sube `assets/avatars/nba_LAL.PNG` como imagen de referencia del personaje
4. Pega el prompt en el campo de texto
5. Selecciona **ratio 9:16** (vertical, story)
6. Genera 4 variantes y selecciona la más consistente con el personaje base
7. Descarga en resolución máxima

> **Importante:** ImageFX no siempre respeta 100% la referencia. Si el resultado
> cambia demasiado la cara, vuelve a subir la imagen de referencia y regenera.

---

## 2. Prompt Base (copiar siempre como base)

```
3D cartoon character, bald man with short salt-and-pepper beard, wearing round glasses,
medium build, friendly smile, standing full body pose on a solid bright green background
(#00C800) for chroma key removal. Pixar/Disney animation style, soft studio lighting,
sharp details, photorealistic 3D render. The character wears a [JERSEY] basketball jersey
with number [NUMBER]. Vertical composition, full body visible from head to toe,
slight 3/4 angle. NO watermarks, NO logos on background, NO text overlays.
```

Sustituir `[JERSEY]` y `[NUMBER]` con los valores de la tabla de equipos.

---

## 3. Tabla de Equipos NBA

| Código | Equipo | Color primario | Jersey prompt | Número sugerido |
|--------|--------|---------------|---------------|-----------------|
| ATL | Atlanta Hawks | Rojo `#C8102E` | `red and white Atlanta Hawks` | 11 |
| BKN | Brooklyn Nets | Negro `#000000` | `black and white Brooklyn Nets` | 7 |
| BOS | Boston Celtics | Verde `#007A33` | `green and white Boston Celtics` | 7 |
| CHA | Charlotte Hornets | Teal `#1D1160` | `teal and purple Charlotte Hornets` | 1 |
| CHI | Chicago Bulls | Rojo `#CE1141` | `red and black Chicago Bulls` | 23 |
| CLE | Cleveland Cavaliers | Granate `#860038` | `wine and gold Cleveland Cavaliers` | 7 |
| DAL | Dallas Mavericks | Azul `#00538C` | `blue and silver Dallas Mavericks` | 77 |
| DEN | Denver Nuggets | Azul marino `#0D2240` | `navy blue and gold Denver Nuggets` | 15 |
| DET | Detroit Pistons | Azul `#002D62` | `blue and red Detroit Pistons` | 3 |
| GSW | Golden State Warriors | Azul/Dorado `#1D428A` | `royal blue and gold Golden State Warriors` | 30 |
| HOU | Houston Rockets | Rojo `#CE1141` | `red and silver Houston Rockets` | 3 |
| IND | Indiana Pacers | Azul marino `#002D62` | `navy blue and gold Indiana Pacers` | 11 |
| LAC | LA Clippers | Rojo/Azul `#C8102E` | `red and blue LA Clippers` | 13 |
| LAL | Los Angeles Lakers | Púrpura `#552583` | `purple and gold Los Angeles Lakers` | 7 |
| MEM | Memphis Grizzlies | Azul `#5D76A9` | `light blue and navy Memphis Grizzlies` | 12 |
| MIA | Miami Heat | Rojo oscuro `#98002E` | `black and red Miami Heat` | 3 |
| MIL | Milwaukee Bucks | Verde `#00471B` | `dark green and cream Milwaukee Bucks` | 34 |
| MIN | Minnesota Timberwolves | Azul `#0C2340` | `navy blue and green Minnesota Timberwolves` | 7 |
| NOP | New Orleans Pelicans | Marino `#0C2340` | `navy blue and gold New Orleans Pelicans` | 1 |
| NYK | New York Knicks | Azul/Naranja `#006BB6` | `blue and orange New York Knicks` | 7 |
| OKC | Oklahoma City Thunder | Azul `#007AC1` | `blue and orange Oklahoma City Thunder` | 2 |
| ORL | Orlando Magic | Azul `#0077C0` | `blue and black Orlando Magic` | 1 |
| PHI | Philadelphia 76ers | Azul `#006BB6` | `blue and red Philadelphia 76ers` | 21 |
| PHX | Phoenix Suns | Morado `#1D1160` | `purple and orange Phoenix Suns` | 13 |
| POR | Portland Trail Blazers | Rojo `#E03A3E` | `red and black Portland Trail Blazers` | 0 |
| SAC | Sacramento Kings | Morado `#5B2B82` | `purple and silver Sacramento Kings` | 7 |
| SAS | San Antonio Spurs | Negro `#C4CED4` | `black and silver San Antonio Spurs` | 21 |
| TOR | Toronto Raptors | Rojo `#CE1141` | `red and black Toronto Raptors` | 7 |
| UTA | Utah Jazz | Azul marino `#002B5C` | `navy blue and yellow Utah Jazz` | 45 |
| WAS | Washington Wizards | Azul/Rojo `#002B5C` | `navy blue and red Washington Wizards` | 5 |

---

## 4. Tabla de Equipos Euroliga

| Código | Equipo | Color primario | Jersey prompt | Número sugerido |
|--------|--------|---------------|---------------|-----------------|
| BAR | FC Barcelona | Azul/Grana `#004D98` | `blue and dark red FC Barcelona basketball` | 7 |
| RMA | Real Madrid | Blanco `#FFFFFF` | `white and gold Real Madrid basketball` | 7 |
| FEN | Fenerbahçe | Amarillo/Azul `#003087` | `yellow and navy Fenerbahce basketball` | 7 |
| OLY | Olympiacos | Rojo/Blanco `#CC0000` | `red and white Olympiacos basketball` | 7 |
| PAO | Panathinaikos | Verde `#006633` | `green and white Panathinaikos basketball` | 7 |
| CSK | CSKA Moscow | Rojo/Azul `#CC0000` | `red and blue CSKA Moscow basketball` | 7 |
| EFS | Anadolu Efes | Azul `#003087` | `blue and white Anadolu Efes basketball` | 7 |
| ZAL | Žalgiris | Verde/Blanco `#007A33` | `green and white Zalgiris basketball` | 7 |
| BAS | Baskonia | Azul/Rojo `#003087` | `blue and red Baskonia basketball` | 7 |
| MIL | AS Monaco | Rojo/Blanco `#CC0000` | `red and white AS Monaco basketball` | 7 |
| VIR | Virtus Bologna | Negro/Blanco `#000000` | `black and white Virtus Bologna basketball` | 7 |
| PAR | Partizan | Negro/Blanco `#000000` | `black and white Partizan basketball` | 7 |
| UNI | Valencia Basket | Naranja/Negro `#FF6B00` | `orange and black Valencia Basket` | 7 |
| BER | Alba Berlin | Rojo/Amarillo `#CC0000` | `red and yellow Alba Berlin basketball` | 7 |
| MCO | Bayern Munich | Rojo `#DC052D` | `red and white Bayern Munich basketball` | 7 |

---

## 5. Poses Especiales

Para variantes del personaje fuera del green screen estándar, usar estos prompts adicionales:

### Pizarra táctica
```
[PROMPT BASE sin jersey específico, con camiseta negra Dos Aros]
The character stands next to a large blackboard with basketball play diagrams (X's and O's),
pointing at the board with one hand, looking at the viewer with a knowing smile.
Dark studio background.
```

### Presentador TV
```
[PROMPT BASE]
The character stands in a modern sports TV studio, wearing a navy blazer over the jersey,
pointing to a large screen showing basketball statistics. Professional lighting,
orange and blue color scheme in the background.
```

### Marco de estadísticas
```
[PROMPT BASE]
The character holds up a large transparent data card/frame showing statistics,
facing the camera with an excited expression. Dark background with subtle basketball court lines.
```

### Efecto neón
```
[PROMPT BASE]
The character raises both hands with energy, surrounded by glowing neon light trails
in pink and purple colors. Dark indoor basketball arena background, dramatic lighting.
```

### Salto con balón
```
[PROMPT BASE]
The character jumps dynamically holding a basketball above their head in a shooting motion,
high energy pose, slight upward angle, green screen background.
```

---

## 6. Consejos para Consistencia del Personaje

### Cara
- Siempre incluir: **"bald man with short salt-and-pepper beard, wearing round glasses"**
- Si la cara cambia demasiado: subir `nba_LAL.PNG` como referencia visual en cada generación
- Usar la misma imagen de referencia siempre — no mezclar referencias de distintas generaciones

### Estilo 3D
- Mantener siempre: **"Pixar/Disney animation style, soft studio lighting, photorealistic 3D render"**
- No usar "illustration", "cartoon drawing" ni "anime" — el estilo es 3D render específicamente

### Green Screen
- El fondo SIEMPRE debe ser verde sólido: **"solid bright green background (#00C800) for chroma key removal"**
- Evitar sombras verdes en el personaje — si aparecen, ajustar el chroma key con `tolerancia` en `image_generator.py`

### Número de camiseta
- El número **7** es el estándar del personaje para la mayoría de equipos
- Excepción: CHI usa 23 (Jordan), GSW usa 30 (Curry), MIL usa 34 (Giannis) para contexto

---

## 7. Checklist de Avatares

### NBA — Avatares disponibles ✅ / Pendientes ⬜

| Código | Equipo | Estado | Archivo |
|--------|--------|--------|---------|
| ATL | Atlanta Hawks | ⬜ | — |
| BKN | Brooklyn Nets | ⬜ | — |
| BOS | Boston Celtics | ✅ | `nba_BOS.PNG` |
| CHA | Charlotte Hornets | ⬜ | — |
| CHI | Chicago Bulls | ✅ | `nba_CHI.PNG`, `nba_CHI_gorro.PNG` |
| CLE | Cleveland Cavaliers | ✅ | `nba_CLE.PNG` |
| DAL | Dallas Mavericks | ⬜ | — |
| DEN | Denver Nuggets | ✅ | `nba_DEN.PNG`, `nba_DEN_bucket.PNG` |
| DET | Detroit Pistons | ✅ | `nba_DET.PNG`, `nba_DET_notas.png` |
| GSW | Golden State Warriors | ⬜ | — |
| HOU | Houston Rockets | ⬜ | — |
| IND | Indiana Pacers | ⬜ | — |
| LAC | LA Clippers | ⬜ | — |
| LAL | Los Angeles Lakers | ✅ | `nba_LAL.PNG`, `nba_LAL_presentacion.JPG` |
| MEM | Memphis Grizzlies | ⬜ | — |
| MIA | Miami Heat | ✅ | `nba_MIA.PNG` |
| MIL | Milwaukee Bucks | ⬜ | — |
| MIN | Minnesota Timberwolves | ⬜ | — |
| NOP | New Orleans Pelicans | ⬜ | — |
| NYK | New York Knicks | ⬜ | — |
| OKC | Oklahoma City Thunder | ⬜ | — |
| ORL | Orlando Magic | ⬜ | — |
| PHI | Philadelphia 76ers | ⬜ | — |
| PHX | Phoenix Suns | ⬜ | — |
| POR | Portland Trail Blazers | ⬜ | — |
| SAC | Sacramento Kings | ✅ | `nba_SAC.PNG` |
| SAS | San Antonio Spurs | ⬜ | — |
| TOR | Toronto Raptors | ⬜ | — |
| UTA | Utah Jazz | ✅ | `nba_UTA.PNG` |
| WAS | Washington Wizards | ⬜ | — |

**NBA: 9 equipos ✅ / 21 pendientes ⬜**

### Euroliga — Avatares disponibles ✅ / Pendientes ⬜

| Código | Equipo | Estado | Archivo |
|--------|--------|--------|---------|
| BAR | FC Barcelona | ⬜ | — |
| RMA | Real Madrid | ⬜ | — |
| FEN | Fenerbahçe | ⬜ | — |
| OLY | Olympiacos | ⬜ | — |
| PAO | Panathinaikos | ⬜ | — |
| CSK | CSKA Moscow | ⬜ | — |
| EFS | Anadolu Efes | ⬜ | — |
| ZAL | Žalgiris | ⬜ | — |
| BAS | Baskonia | ⬜ | — |
| MIL | AS Monaco | ⬜ | — |
| VIR | Virtus Bologna | ⬜ | — |
| PAR | Partizan | ⬜ | — |
| UNI | Valencia Basket | ⬜ | — |
| BER | Alba Berlin | ⬜ | — |
| MCO | Bayern Munich | ⬜ | — |
| DEFAULT | Genérico verde | ✅ | `euro_DEFAULT_verde.PNG` |
| RED | Genérico rojo | ✅ | `euro_RED.PNG` |

**Euroliga: 2 genéricos ✅ / 15 equipos específicos pendientes ⬜**

### Poses especiales

| Nombre | Estado | Archivo |
|--------|--------|---------|
| Pizarra táctica | ✅ | `presenter/presenter_pizarra.jpg` |
| Presentador TV | ✅ | `presenter/presenter_tv.jpg` |
| Presentador deportes | ✅ | `presenter/presenter_deportes.jpg` |
| Presentador Nuggets | ✅ | `presenter/presenter_nuggets.jpg` |
| Efecto neón v1 | ✅ | `presenter/presenter_neon_v1.PNG` |
| Efecto neón v2 | ✅ | `presenter/presenter_neon_v2.PNG` |
| Playoffs | ✅ | `presenter/presenter_playoffs.PNG` |
| Salto con balón | ⬜ | — |
| Marco estadísticas | ⬜ | — |

---

## 8. Naming Convention

```
assets/avatars/
├── nba_CODIGO.PNG          # Avatar estándar NBA (green screen, pose neutral)
├── nba_CODIGO_variante.PNG # Variante del mismo equipo (bucket, gorro, etc.)
├── euro_CODIGO.PNG         # Avatar estándar Euroliga
├── presenter/
│   └── presenter_NOMBRE.jpg  # Poses especiales sin contexto de equipo
└── posts/
    └── post_DESCRIPCION.PNG  # Imágenes ya compuestas con texto (no reutilizables)
```

**Reglas:**
- Siempre mayúsculas para el código: `nba_LAL.PNG`, no `nba_lal.png`
- Extensión `.PNG` para imágenes con transparencia/green screen
- Extensión `.jpg` para imágenes compuestas sin necesidad de transparencia
- El código sigue la abreviatura oficial NBA de 3 letras
- Para Euroliga usar el código de 3 letras más reconocible internacionalmente
