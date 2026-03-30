# 📖 Manual de Uso - Bot Telegram Dos Aros

**Versión:** 1.1
**Fecha:** Marzo 30, 2026
**Estado:** En Vivo

---

## 📋 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Comandos Disponibles](#comandos-disponibles)
3. [Guías por Comando](#guías-por-comando)
4. [Flujos de Trabajo](#flujos-de-trabajo)
5. [Ejemplos Prácticos](#ejemplos-prácticos)
6. [Troubleshooting](#troubleshooting)

---

## 🎯 Introducción

El **Bot Telegram de Dos Aros** es un asistente que:

- 🎨 **Genera prompts de avatares** para equipos de NBA y Euroliga
- 📊 **Consulta datos de baloncesto** en lenguaje natural
- 🎬 **Crea videos** con Remotion
- 📸 **Genera imágenes** e tweets automáticos

**Estado:** ✅ En vivo 24/7  
**Ubicación:** Raspberry Pi (192.168.1.136)

---

## 🎮 Comandos Disponibles

### 1. **Avatar Commands**

#### `/avatar_prompt [equipo]`
Obtiene el prompt dinámico para generar avatar de un equipo específico.

```
Uso: /avatar_prompt Lakers
Uso: /avatar_prompt Barcelona
Uso: /avatar_prompt Real Madrid
```

**Qué devuelve:**
- ✅ Avatar URL (para referencia)
- ✅ Logo URL (para componer)
- ✅ Prompt completo para Google ImageFX
- ✅ Instrucciones paso a paso

---

#### `/avatar_random` (alias: `/avatar`)
Obtiene un prompt de avatar aleatorio.

```
Uso: /avatar_random
Uso: /avatar
```

**Qué devuelve:**
- ✅ Equipo aleatorio
- ✅ Tipo de escena (EDITORIAL, HISTORIC, ELITE, STREET, GAME)
- ✅ Prompt + URLs
- ✅ Instrucciones

---

#### `/avatar_today` (alias: `/avatars`)
Obtiene 5 prompts de avatares del día (aleatorios).

```
Uso: /avatar_today
Uso: /avatars
```

**Qué devuelve:**
- ✅ 5 prompts diferentes (uno por mensaje)
- ✅ Cada uno con su equipo, tipo y detalles
- ✅ Listos para generar en Google ImageFX

---

### 2. **Video Command**

#### `/video [instrucción]`
Genera un video MP4 con Remotion basado en una instrucción en lenguaje natural.

```
Uso: /video Top 3 anotadores NBA esta semana
Uso: /video Mejores defensas Euroliga del mes
Uso: /video Rachas ganadores actuales
```

**Qué devuelve:**
- ✅ Video MP4 generado
- ✅ Basado en datos reales de la BBDD
- ✅ Listo para publicar en redes

---

### 3. **Consultas en Lenguaje Natural**

Escribe cualquier pregunta sobre baloncesto en ESPAÑOL o INGLÉS.

```
Ejemplos:
"Quién fue el máximo anotador de la NBA la semana pasada?"
"Top 5 asistentes en Euroliga este mes"
"Cuántos triples metió Luka Doncic ayer?"
"Comparar eficiencia defensiva Lakers vs Celtics"
```

**Flujo de respuesta:**
1. Bot traduce pregunta → SQL
2. Ejecuta consulta en BBDD
3. Devuelve datos en tabla
4. **Pregunta:** ¿Generar imagen + tweet?
5. Si confirmas (sí/no):
   - 🐦 Crea tweet automático
   - 🎨 Genera imagen con dato clave
   - Envía ambos al chat

---

## 📚 Guías por Comando

### GUÍA 1: Avatar Prompt para un Equipo

**Objetivo:** Obtener prompt para generar avatar de Lakers

**Paso 1:** Envía comando
```
/avatar_prompt Los Angeles Lakers
```

**Paso 2:** Bot devuelve:
- Equipo: Los Angeles Lakers
- Tipo: EDITORIAL (o HISTORIC/ELITE/STREET/GAME)
- Avatar URL: referencia visual
- Logo URL: logo Dos Aros
- **Prompt completo** en un código block

**Paso 3:** Copia el prompt
- Selecciona todo el texto del prompt
- Ctrl+C (copiar)

**Paso 4:** Abre Google ImageFX
- Ve a https://imagegeneration.dev
- Pega el prompt en el campo de texto
- **Adjunta imagen de referencia:**
  - Click en "Upload image"
  - Copia la Avatar URL en navegador
  - O descargar y subir localmente

**Paso 5:** Genera la imagen
- Click en "Generate"
- Espera 30-60 segundos
- Descarga la imagen

**Paso 6:** Publica en redes
- Instagram Stories (1080×1920)
- X/Twitter
- LinkedIn
- Telegram

---

### GUÍA 2: Avatar Aleatorio del Día

**Objetivo:** Obtener 5 prompts para generar múltiples avatares

**Paso 1:** Envía comando
```
/avatar_today
```

**Paso 2:** Bot envía 5 prompts (uno por mensaje)

**Paso 3-6:** Repite el flujo de GUÍA 1 para cada uno

**Consejo:** Genera 1-2 al día para mantener consistencia

---

### GUÍA 3: Consulta de Datos + Imagen

**Objetivo:** Consultar dato de baloncesto y generar imagen automáticamente

**Paso 1:** Haz tu pregunta
```
Quién fue el máximo anotador NBA la semana pasada?
```

**Paso 2:** Bot responde
- 🔍 Convierte pregunta a SQL
- 📊 Devuelve tabla de datos
- ❓ Pregunta: "¿Genero imagen y tweet? (sí/no)"

**Paso 3a:** Confirma (escribe "sí")
- 🐦 **Tweet:** Automático, 280 caracteres máximo
- 🎨 **Imagen:** Gráfico con logo Dos Aros
- ✅ Ambos enviados al chat

**Paso 3b:** Rechaza (escribe "no")
- ❌ Solo recibiste los datos

---

### GUÍA 4: Generar Video

**Objetivo:** Crear un video MP4 con Remotion

**Paso 1:** Envía comando
```
/video Top 5 reboteadores Euroliga este mes
```

**Paso 2:** Bot responde
```
⏳ Generando video...
Puede tardar 2-5 minutos.
```

**Paso 3:** Espera (2-5 minutos)
- Bot está procesando datos
- Generando frames con Remotion
- Compilando video MP4

**Paso 4:** Recibe video
```
✅ Video generado
[archivo MP4 descargable]
```

**Paso 5:** Publica
- Descarga el archivo
- Publica en Reels Instagram
- TikTok
- YouTube Shorts

---

## 🔄 Flujos de Trabajo

### Flujo 1: Generación Diaria de Avatares (RECOMENDADO)

```
08:30 AM → Abres Telegram
08:35 AM → /avatar_today (recibes 5 prompts)
08:40 AM → Abres Google ImageFX
08:45 AM → Generas avatar 1
09:00 AM → Generas avatar 2
(...)
10:00 AM → Generas avatar 5 (opcional)

TOTAL: ~1.5-2 horas para 5 imágenes
```

**Frecuencia:** Diaria o 3-4 veces por semana

---

### Flujo 2: Consultas + Contenido

```
Cualquier momento → Haces pregunta sobre datos
(ej: "Top anotadores Lakers?")

Bot responde → Muestra tabla de datos

Decides → ¿Convertir en contenido?
  ├─ SÍ → Bot genera tweet + imagen
  └─ NO → Solo guardas los datos

Resultado → Tweet + Imagen listos para publicar
```

**Frecuencia:** Según necesidad

---

### Flujo 3: Generación Semanal de Video

```
Viernes 2 PM → /video [tema semanal]
(ej: "Resumen defensivas Euroliga semana 15")

Bot genera → Video MP4

Viernes 3 PM → Descargas el video

Viernes 4 PM → Publicas en Reels/Shorts
```

**Frecuencia:** Semanal o quincenal

---

## 💡 Ejemplos Prácticos

### Ejemplo 1: Avatar Prompt Paso a Paso

**Paso 1: Solicitar prompt**
```
Usuario: /avatar_prompt Lakers
```

**Paso 2: Bot devuelve**
```
🎨 DOS AROS - AVATAR GENERATOR

📍 Equipo: Los Angeles Lakers
📊 Tipo: EDITORIAL
⏱️ Generado: 2026-03-29 15:30

🖼️ AVATAR REFERENCE:
https://github.com/.../avatar_base_2_action_jump.png

📌 LOGO:
https://github.com/.../logoDosAros.png

📝 PROMPT PARA GOOGLE IMAGEFX:

A cinematic, ultra-realistic, photorealistic full-body render.

AVATAR: Use the exact avatar from [URL] as the base reference...
POSE: Dynamic jump, mid-action, confident expression
OUTFIT: Los Angeles Lakers jersey. Colors: Primary #552583 (Purple), 
Secondary #FDB927 (Gold), Tertiary #000000 (Black)
SCENE: Modern NBA arena background with warm dramatic lighting
LOGO: Include the Dos Aros logo naturally blended
RENDER: Ultra-realistic 3D, Pixar-quality, 8K
BACKGROUND: Solid chroma key green (#00FF00)
FRAMING: Full body visible, centered

✅ INSTRUCCIONES:
1. Copia el prompt completo
2. Abre Google ImageFX (imagegeneration.dev)
3. Pega el prompt + adjunta avatar URL como imagen de referencia
4. Genera imagen
5. Descarga y publica en redes
```

**Paso 3: Usuario copia prompt y va a Google ImageFX**

**Paso 4: Genera imagen**

**Paso 5: Publica en redes**

---

### Ejemplo 2: Consulta + Imagen

**Paso 1: Usuario pregunta**
```
Quién fue el máximo anotador NBA esta semana?
```

**Paso 2: Bot procesa**
```
🔍 Consultando datos...
```

**Paso 3: Bot devuelve tabla**
```
PLAYER_NAME | TEAM_ABBREVIATION | PTS
Luka Doncic | DAL               | 156
Shai Gilgeous-Alexander | OKC   | 142
...
```

**Paso 4: Bot pregunta**
```
¿Genero imagen y tweet con este dato? (sí/no)
```

**Paso 5: Usuario responde "sí"**

**Paso 6: Bot genera ambos**
```
🐦 Tweet:
"Luka Doncic fue el máximo anotador de la NBA esta semana 
con 156 puntos. @luka7doncic dominando @NBA 💪 #NBAStats"

🎨 [Imagen con gráfico: Luka Doncic - 156 PTS]
```

**Paso 7: Usuario publica ambos en redes**

---

### Ejemplo 3: Video Semanal

**Paso 1: Usuario solicita video**
```
/video Top 5 defensas Euroliga esta semana
```

**Paso 2: Bot comienza a generar**
```
⏳ Generando video...
Instrucción: Top 5 defensas Euroliga esta semana
Puede tardar 2-5 minutos.
```

**Paso 3: Bot termina (después de 3 minutos)**
```
✅ Video generado
Instrucción: Top 5 defensas Euroliga esta semana
Tamaño: 45.2 MB
[Archivo MP4 para descargar]
```

**Paso 4: Usuario descarga y publica en Reels**

---

## 🔧 Troubleshooting

### Problema 1: "Equipo no encontrado"

**Síntoma:**
```
/avatar_prompt Guaros
❌ Equipo 'Guaros' no encontrado.
```

**Causa:** Nombre del equipo incorrecto o variación

**Solución:**
```
Intenta con:
/avatar_prompt Lara (en lugar de Guaros)
/avatar_prompt Barcelona (en lugar de FC Barcelona)
/avatar_prompt Real Madrid (nombre completo)
```

**Equipos válidos (ejemplos):**
- Los Angeles Lakers
- Golden State Warriors
- Boston Celtics
- FC Barcelona
- Real Madrid
- Olympiacos BC
- CSKA Moscú

---

### Problema 2: "No hay prompts disponibles"

**Síntoma:**
```
/avatar_today
❌ No hay prompts disponibles
```

**Causa:** BBDD corrupta o sin datos

**Solución:**
- Contacta a administrador Pi
- Verifica que avatar_prompts tenga 68 registros

```bash
# En Pi:
sqlite3 /mnt/nba_data/dosaros_local.db "SELECT COUNT(*) FROM avatar_prompts;"
```

---

### Problema 3: Timeout en video

**Síntoma:**
```
/video [instrucción]
❌ No se pudo generar el video
```

**Causas posibles:**
- Remotion no instalado en Pi
- Error en APIs (Claude/Gemini)
- Datos insuficientes en BBDD

**Solución:**
```
Intenta reformular:
❌ /video cosa muy específica
✅ /video Top 5 anotadores NBA esta semana

❌ /video liga extraña
✅ /video NBA o Euroliga
```

---

### Problema 4: Bot no responde

**Síntoma:**
```
Envías mensaje → Sin respuesta después de 1 min
```

**Causa:** Bot fuera de línea o error

**Solución:**
```bash
# En Pi, verifica:
ps aux | grep bot_consultas.py

# Si no hay proceso:
tmux new-session -d -s bot_consultas "cd /home/pi/dosaros-data-project && PYTHONPATH=/home/pi/dosaros-data-project python src/automation/bot_consultas.py"
```

---

### Problema 4b: Bot no arranca aunque el proceso existe

**Síntoma:**
```
Proceso visible en `ps aux` pero el bot no responde
```

**Causa:** `PYTHONPATH` no configurado — los imports `src.*` fallan silenciosamente.

**Solución:** Asegúrate de que `PYTHONPATH` está configurado correctamente al lanzar el bot:
```bash
PYTHONPATH=/home/pi/dosaros-data-project python src/automation/bot_consultas.py
```

---

### Problema 5: Google ImageFX rechaza el prompt

**Síntoma:**
```
Copias prompt, lo pegas en ImageFX
Error: "Invalid prompt" o "Generation failed"
```

**Causa:** Prompt muy largo o caracteres especiales

**Solución:**
```
1. Copia todo el texto entre los === ===
2. Si aún falla, simplifica:
   ❌ Copia exacto del bot
   ✅ Copia solo la parte AVATAR/OUTFIT/SCENE

3. Ejemplo simplificado:
"Avatar with Lakers jersey, yellow and purple colors,
jumping pose, arena background, chroma key green"
```

---

### Problema 6: Imagen sale sin avatar

**Síntoma:**
```
Generas imagen en ImageFX
Resultado: Solo fondo sin avatar visible
```

**Causa:** Avatar URL no cargó como referencia

**Solución:**
```
1. Cuando pegues prompt en ImageFX:
   - Busca "Upload image" o "Reference image"
   - Sube el avatar manualmente desde:
     https://github.com/.../avatar_base_X.png

2. O descarga local:
   - Abre avatar URL en navegador
   - Click derecho → Guardar imagen
   - Sube a ImageFX
```

---

## 📞 Contacto y Soporte

**Problema no resuelto?**

- 📧 Email: robe@dosaros.com
- 💬 Telegram: Mensaje directo
- 🔧 GitHub: Abre issue en repo

---

## 📋 Cheat Sheet (Referencia Rápida)

### Comandos Avatar
```
/avatar_prompt Lakers          → Prompt de Lakers
/avatar_random  o  /avatar     → Prompt aleatorio
/avatar_today   o  /avatars    → 5 prompts
```

### Comandos Otros
```
/video [instrucción]           → Generar video
/v [instrucción]               → Alias de /video
[pregunta natural]             → Consultar datos → imagen + tweet opcional
```

### Equipos NBA Comunes
```
Lakers, Celtics, Warriors, Heat, Suns, Nuggets,
Mavericks, 76ers, Bucks, Knicks, Raptors, Grizzlies
```

### Equipos Euroliga Comunes
```
Barcelona, Real Madrid, Olimpiacos, Panathinaikos,
CSKA, Fenerbahçe, Anadolu Efes, Partizan
```

---

**¡Listo para usar el bot!** 🚀

Para dudas, consulta este manual o contacta al equipo.
