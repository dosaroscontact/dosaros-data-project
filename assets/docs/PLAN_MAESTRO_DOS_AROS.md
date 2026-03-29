# 🎬 PLAN MAESTRO: Dos Aros + Editor Pro Max

**Estado Actual:** ✅ Funcional
- Raspberry Pi 4 (192.168.1.136)
- SQLite con NBA/Euro PBP + coordenadas
- Bot Telegram (24/7)
- Cron 9:00 AM (master_sync.py)
- Generador avatares (Hugging Face)
- Generador imágenes Story
- Generador tweets

**Objetivo:** Añadir generación automática de VIDEOS

---

## 🚀 PLAN DE ACCIÓN (Orden exacto)

### FASE 1: INSTALAR EDITOR PRO MAX EN PI (30 min)

```bash
ssh pi@192.168.1.136

# 1. Clonar Editor Pro Max en la Pi
cd /home/pi
git clone https://github.com/Hainrixz/editor-pro-max.git
cd editor-pro-max

# 2. Instalar Node.js + npm (si no lo tienes)
# Verificar versión:
node --version  # Debería ser v18+ o v20+
npm --version

# Si no lo tienes:
# curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
# sudo apt-get install -y nodejs

# 3. Instalar dependencias Remotion
npm install
# Esto tarda ~5-10 min

# 4. Verificar ffmpeg
ffmpeg -version
# Si no está:
# sudo apt-get install ffmpeg

# 5. Instalar Python deps de Editor Pro Max
pip install -r requirements.txt

# 6. Test que Remotion funciona
npx remotion --version
# Debería mostrar: 4.0.440 o similar

# 7. Volver a tu proyecto Dos Aros
cd /home/pi/dosaros-data-project
```

**✅ Si todo sale bien:** Ya tienes Editor Pro Max listo

---

### FASE 2: INTEGRAR VIDEOSGENERATOR EN TU PROYECTO (30 min)

```bash
cd /home/pi/dosaros-data-project

# 1. Crear carpeta de integración
mkdir -p src/integrations/video_generator
mkdir -p assets/video_output
touch src/integrations/__init__.py
touch src/integrations/video_generator/__init__.py

# 2. Copiar video_generator.py (que descargaste)
# [Copiar el archivo video_generator.py a:]
cp ~/video_generator.py src/integrations/video_generator/

# 3. Copiar telegram_video_handler.py (que descargaste)
cp ~/telegram_video_handler.py src/integrations/

# 4. Crear los __init__.py correctamente

# src/integrations/__init__.py
cat > src/integrations/__init__.py << 'EOF'
from .video_generator.video_generator import VideoGenerator
from .telegram_video_handler import TelegramVideoHandler, setup_video_handlers

__all__ = ['VideoGenerator', 'TelegramVideoHandler', 'setup_video_handlers']
EOF

# src/integrations/video_generator/__init__.py
cat > src/integrations/video_generator/__init__.py << 'EOF'
from .video_generator import VideoGenerator

__all__ = ['VideoGenerator']
EOF

# 5. Actualizar .env (añadir path a Editor Pro Max)
cat >> .env << 'EOF'

# Editor Pro Max
EDITOR_PRO_MAX_PATH=/home/pi/editor-pro-max
VIDEO_OUTPUT_DIR=./assets/video_output
VIDEO_DEFAULT_FPS=30
EOF

# 6. Test que carga sin errores
PYTHONPATH=/home/pi/dosaros-data-project \
  venv/bin/python -c "
from src.integrations import VideoGenerator
gen = VideoGenerator()
print('✅ VideoGenerator cargado correctamente')
gen.api.print_status()
"
```

**✅ Si sale "VideoGenerator cargado":** Lista la integración

---

### FASE 3: INTEGRAR CON TU BOT DE TELEGRAM (15 min)

En tu archivo `src/automation/bot_consultas.py` o donde tengas el bot:

```python
# ARRIBA DEL TODO, añadir:
from src.integrations import setup_video_handlers, VideoGenerator

# En la función donde configuras handlers (probablemente main()):
def main():
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    
    app = Application.builder().token(TOKEN).build()
    
    # ... tus handlers existentes ...
    
    # ✅ AÑADIR ESTO:
    video_gen = VideoGenerator()
    setup_video_handlers(app, video_gen)
    
    print("✅ Handlers de video configurados")
    
    # Iniciar bot
    app.run_polling()

if __name__ == "__main__":
    main()
```

**Comandos que tendrá el bot:**
```
/video Top 3 tiradores 3P NBA esta semana
/v Resultado último partido Celtics
/vstatus Ver estado del sistema
/vlist Listar tus videos generados
```

---

### FASE 4: INTEGRAR CON MASTER_SYNC (AUTOMÁTICO A LAS 9:00)

En `src/automation/master_sync.py`, añadir después de generar imágenes:

```python
# Después de generar Story imagen, añadir:

print("\n🎬 Generando video del día...")
try:
    from src.integrations import VideoGenerator
    
    video_gen = VideoGenerator()
    
    # Crear prompt basado en las perlas del día
    mejor_perla = perlas_detectadas[0]  # La mejor del día
    
    prompt = f"""
    Crea un video corto (30-45 segundos) para TikTok/Instagram Reel:
    
    Título: {mejor_perla['titulo']}
    Jugador: {mejor_perla['jugador']}
    Equipo: {mejor_perla['equipo']}
    Estadísticas: {mejor_perla['stats']}
    Contexto: {mejor_perla['descripcion']}
    
    Usa colores del equipo {mejor_perla['equipo_codigo']}.
    Incluye logo Dos Aros.
    Estilo: deportivo, energético, listo para redes.
    """
    
    video_path = video_gen.generar_video(
        instruccion=prompt,
        usuario_id="master_sync_daily",
        preset="tiktok"
    )
    
    if video_path:
        # Enviar video a Telegram
        await send_to_telegram(
            chat_id=TELEGRAM_CHAT_ID,
            video=video_path,
            caption=f"🎬 Video del día: {mejor_perla['titulo']}"
        )
        print(f"✅ Video generado: {video_path}")
    else:
        print("⚠️ Error generando video, pero continuamos con el resto")

except Exception as e:
    print(f"⚠️ Error en generación de video: {e}")
    # No abortes el resto del proceso

# Continuar con el resto (tweets, etc)
```

---

### FASE 5: SETUP COMPLETO EN UN BLOQUE (COPIAR Y PEGAR)

```bash
ssh pi@192.168.1.136

# ===== SETUP COMPLETO =====

# 1. Instalar Editor Pro Max
cd /home/pi
git clone https://github.com/Hainrixz/editor-pro-max.git
cd editor-pro-max && npm install && pip install -r requirements.txt -q
cd /home/pi/dosaros-data-project

# 2. Crear estructura
mkdir -p src/integrations/video_generator
mkdir -p assets/video_output
touch src/integrations/__init__.py
touch src/integrations/video_generator/__init__.py

# 3. Descargar archivos de integración
# (Asumo que ya tienes video_generator.py y telegram_video_handler.py)
# Si no los tienes, copiarlos desde acá abajo

# 4. Actualizar .env
echo "" >> .env
echo "# Editor Pro Max" >> .env
echo "EDITOR_PRO_MAX_PATH=/home/pi/editor-pro-max" >> .env
echo "VIDEO_OUTPUT_DIR=./assets/video_output" >> .env
echo "VIDEO_DEFAULT_FPS=30" >> .env

# 5. Test
PYTHONPATH=/home/pi/dosaros-data-project \
  venv/bin/python -c "from src.integrations import VideoGenerator; VideoGenerator()"

echo "✅ Setup completado"
```

---

## 📅 FLUJO AUTOMÁTICO DIARIO (CRONTAB)

Tu cron actual a las 9:00 AM:
```bash
0 9 * * * cd /home/pi/dosaros-data-project && venv/bin/python src/automation/master_sync.py
```

**Después de la integración, el flujo será:**

```
9:00 AM Cron ejecuta master_sync.py
  ↓
1. Obtiene resultados NBA/Euro de ayer
  ↓
2. Detecta "perlas" (IA encuentra actuaciones destacadas)
  ↓
3. Genera imagen Story 1080×1920
  ↓
4. ✨ NUEVO: Genera video (30-45 seg) con la mejor perla
  ↓
5. Genera hilo Twitter
  ↓
6. Envía TODO a Telegram:
   - Foto story
   - Video
   - Tweets
   ↓
7. Notifica: "✅ Contenido del día listo"
```

---

## 🧪 TESTING ANTES DE LANZAR

### Test 1: VideoGenerator carga correctamente
```bash
cd /home/pi/dosaros-data-project

PYTHONPATH=/home/pi/dosaros-data-project \
  venv/bin/python -c "
from src.integrations import VideoGenerator
gen = VideoGenerator()
print('✅ VideoGenerator OK')
gen.api.print_status()
"
```

**Esperado:** Muestra estado de APIs ✅

### Test 2: Generar video de prueba
```bash
cd /home/pi/dosaros-data-project

PYTHONPATH=/home/pi/dosaros-data-project \
  venv/bin/python -c "
from src.integrations import VideoGenerator
gen = VideoGenerator()
video = gen.generar_video(
    'Crea un video de prueba con top 3 tiradores NBA',
    usuario_id='test_001'
)
if video:
    print(f'✅ Video generado: {video}')
    import os
    print(f'   Tamaño: {os.path.getsize(video) / (1024*1024):.2f} MB')
else:
    print('❌ Error generando video')
"
```

**Esperado:** Video de ~50-100 MB en `assets/video_output/`

### Test 3: Comando Telegram
```
En tu Telegram bot:
/video Top 3 tiradores 3P NBA esta semana

Esperado:
- Bot responde: "⏳ Generando video..."
- Después de 2-5 min: Video recibido
```

### Test 4: Master_sync simulado
```bash
cd /home/pi/dosaros-data-project

# Simular que es las 9:00 (sin cron)
PYTHONPATH=/home/pi/dosaros-data-project \
  venv/bin/python src/automation/master_sync.py
```

**Esperado:** Ejecuta todo, incluye generación de video

---

## ⚡ OPTIMIZATION: RENDIMIENTO

### Problema: Videos tardan 5-10 min en Pi
**Solución:** Renderizar en otro lado (opcional)

```python
# En VideoGenerator, si quieres renderizar en máquina con GPU:

# OPCIÓN A: Renderizar en Pi (actual)
# - Lento (~5 min por video)
# - No requiere otra máquina
# - OK para 1-2 videos/día

# OPCIÓN B: Renderizar en desktop con GPU
# - Rápido (~30-60 seg)
# - Requiere setup adicional
# - Idea: master_sync en Pi genera composición,
#   envía a desktop para renderizar

# OPCIÓN C: Renderizar en background tmux
# - Ejecutar en tmux para no bloquear cron

# Recomendado para ti: OPCIÓN A (simple)
# Meta: Video en < 5 min a las 9:00 AM
```

---

## 📊 DIAGRAMA DEL FLUJO FINAL

```
┌─────────────────────────────────────────────────────────────┐
│         RASPBERRY PI 4 - 192.168.1.136                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  9:00 AM CRON                                               │
│    │                                                        │
│    ├─► nba_api + euroleague_api                            │
│    │   └─► SQLite (consulta resultados)                    │
│    │                                                        │
│    ├─► IA Perlas (Gemini/Claude)                           │
│    │   └─► Detecta mejor actuación                         │
│    │                                                        │
│    ├─► image_generator.py                                  │
│    │   └─► Story 1080×1920                                 │
│    │                                                        │
│    ├─► ✨ VideoGenerator.py (NUEVO)                        │
│    │   ├─► Extrae contexto (Claude)                        │
│    │   ├─► Consulta SQLite                                 │
│    │   ├─► Claude genera composición Remotion              │
│    │   └─► Remotion renderiza MP4 (5 min)                  │
│    │                                                        │
│    ├─► gemini_social.py                                    │
│    │   └─► Hilo Twitter                                    │
│    │                                                        │
│    └─► Telegram Bot                                        │
│        └─► Envía: Foto + Video + Tweets                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔑 VARIABLES .env FINALES

```env
# Existentes
GEMINI_API_KEY=...
CLAUDE_API_KEY=...
GROQ_API_KEY=...
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
LOCAL_DB=/mnt/nba_data/dosaros_local.db

# Avatar Generator (ya tienes)
HF_TOKEN=hf_...
HF_PROVIDER=wavespeed
HF_IMAGE_MODEL=black-forest-labs/FLUX.1-dev

# Editor Pro Max (NUEVO)
EDITOR_PRO_MAX_PATH=/home/pi/editor-pro-max
VIDEO_OUTPUT_DIR=./assets/video_output
VIDEO_DEFAULT_FPS=30
VIDEO_MAX_DURATION=90  # segundos
```

---

## ⚠️ TROUBLESHOOTING ESPECÍFICO PARA TU PI

| Problema | Solución |
|----------|----------|
| "npm: command not found" | Instala Node.js: `curl -fsSL https://deb.nodesource.com/setup_20.x \| sudo -E bash -` && `sudo apt-get install nodejs` |
| "ffmpeg not found" | `sudo apt-get install ffmpeg` |
| "Memory error rendering" | Reduce resolución o duración en parámetros |
| "Timeout > 10 min" | Video demasiado largo, máx 60s |
| "TypeError: APIManager" | Verifica .env tiene todas las keys |
| "Remotion render failed" | Verifica que npx remotion funciona: `cd /home/pi/editor-pro-max && npx remotion --version` |
| "Master_sync se cuelga" | Reduce videos/día o renderiza en background con tmux |
| "Videos muy pesados" | Aplica compresión post-render: `ffmpeg -i input.mp4 -crf 28 output.mp4` |

---

## 📈 NEXT STEPS DESPUÉS

1. **Optimización de Velocidad**
   - Caché de composiciones
   - Renderizado en paralelo
   - Usar GPU si la tienes

2. **Más Tipos de Videos**
   - Top 3 semanales
   - Comparativas NBA vs Euro
   - Highlights automáticos
   - Récords y milestones

3. **Integración Avanzada**
   - Subir automático a YouTube
   - Distribuir a múltiples plataformas
   - Analytics de engagement
   - A/B testing de contenido

4. **AI Mejorada**
   - Fine-tuning de prompts
   - Generación de música
   - Voiceover automático
   - Avatares personalizados

---

## ✅ CHECKLIST FINAL

- [ ] Git pull en `/home/pi/dosaros-data-project`
- [ ] Node.js v18+ instalado
- [ ] npm install en editor-pro-max/
- [ ] ffmpeg disponible
- [ ] src/integrations/ creado
- [ ] video_generator.py copiado
- [ ] telegram_video_handler.py copiado
- [ ] .env actualizado con EDITOR_PRO_MAX_PATH
- [ ] Test 1 pasado (VideoGenerator carga)
- [ ] Test 2 pasado (genera video de prueba)
- [ ] Test 3 pasado (comando Telegram funciona)
- [ ] Test 4 pasado (master_sync simula video)
- [ ] Crontab sin cambios (automático a las 9:00)
- [ ] Logs se guardan en `logs/video_*.log`

---

**Cuando tengas TODO listo, avísame y te daré instrucciones de monitoreo y optimizaciones específicas para tu Pi.** 🚀

(Si necesitas los archivos video_generator.py y telegram_video_handler.py, están arriba en los outputs)
