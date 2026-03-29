# 🎬 Integración Editor Pro Max + Dos Aros

**Objetivo:** Generar videos automáticamente desde Telegram usando Claude Code + tus APIs + SQLite

**Flujo final:**
```
Usuario en Telegram: "Crea un video de los top 3 tiradores de 3P esta semana"
         ↓
Bot captura mensaje + extrae parámetros
         ↓
Consulta SQLite (tu base local)
         ↓
Claude Code genera composición Remotion
         ↓
Editor Pro Max renderiza MP4
         ↓
Bot envía video a Telegram
```

---

## 📋 PASO 1: Preparar la carpeta de Editor Pro Max

### 1.1 Clonar/copiar Editor Pro Max a tu proyecto

```bash
# Si aún no lo tienes, clona el repo
git clone https://github.com/Hainrixz/editor-pro-max.git

# Copia la carpeta a tu proyecto Dos Aros
cp -r editor-pro-max ~/dos-aros/editor_pro_max

# O si usas como submódulo (recomendado para Git):
cd ~/dos-aros
git submodule add https://github.com/Hainrixz/editor-pro-max.git editor_pro_max
```

### 1.2 Instalar dependencias de Editor Pro Max

```bash
cd ~/dos-aros/editor_pro_max

# Instala las dependencias
pip install -r requirements.txt

# Verifica que Remotion esté instalado
npm install

# Verifica que ffmpeg esté disponible
ffmpeg -version
```

**Si ffmpeg no está instalado:**
```bash
# En Ubuntu/Debian
sudo apt-get install ffmpeg

# En macOS
brew install ffmpeg

# En Windows
choco install ffmpeg
```

### 1.3 Configurar Remotion

```bash
cd ~/dos-aros/editor_pro_max

# Verifica que la config está lista
cat remotion.config.ts

# Debería incluir algo como:
# Config.setFrameRange([0, 1800]); // Max 60s @ 30fps
```

---

## 🏗️ PASO 2: Crear la estructura de módulos

### 2.1 Crear directorio de integración

```bash
# En tu proyecto Dos Aros
mkdir -p src/integrations/video_generator
mkdir -p src/prompts/video_prompts
mkdir -p assets/video_output
```

### 2.2 Crear el módulo principal: `video_generator.py`

**Ubicación:** `src/integrations/video_generator/video_generator.py`

```python
import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.utils.api_manager import APIManager
from src.database.database import consultar_db_local

class VideoGenerator:
    """Generador de videos para Dos Aros usando Editor Pro Max + Claude"""
    
    def __init__(self):
        self.api = APIManager()
        self.editor_pro_max_path = Path(__file__).parent.parent.parent.parent / "editor_pro_max"
        self.output_dir = Path(__file__).parent.parent.parent.parent / "assets" / "video_output"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        if not self.editor_pro_max_path.exists():
            raise ValueError(f"❌ Editor Pro Max no encontrado en {self.editor_pro_max_path}")
    
    def generar_video(
        self,
        instruccion: str,
        usuario_id: str = "telegram_user",
        preset: str = "default"
    ) -> Optional[str]:
        """
        Genera un video basado en una instrucción natural.
        
        Args:
            instruccion: Descripción natural del video (ej: "Top 3 tiradores 3P NBA esta semana")
            usuario_id: ID del usuario (para tracking)
            preset: Preset de template (default, nba, euro, analysis, etc)
        
        Returns:
            Path al video generado, o None si falla
        """
        
        try:
            print(f"🎬 Iniciando generación de video...")
            print(f"   Instrucción: {instruccion}")
            
            # PASO 1: Extraer contexto de la instrucción
            contexto = self._extraer_contexto(instruccion)
            print(f"✅ Contexto extraído: {contexto}")
            
            # PASO 2: Consultar datos de la BBD
            datos_bd = self._consultar_datos(contexto)
            print(f"✅ Datos extraídos de SQLite: {len(datos_bd)} registros")
            
            # PASO 3: Generar prompt para Claude
            prompt_claude = self._generar_prompt_claude(instruccion, datos_bd, contexto)
            
            # PASO 4: Usar Claude Code para generar composición Remotion
            composicion_tsx = self._generar_composicion_tsx(prompt_claude, contexto)
            print(f"✅ Composición TSX generada")
            
            # PASO 5: Guardar composición en Editor Pro Max
            composicion_path = self._guardar_composicion(composicion_tsx, usuario_id)
            print(f"✅ Composición guardada: {composicion_path}")
            
            # PASO 6: Renderizar video con Remotion
            video_path = self._renderizar_video(composicion_path, usuario_id)
            print(f"✅ Video renderizado: {video_path}")
            
            return str(video_path)
        
        except Exception as e:
            print(f"❌ Error generando video: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _extraer_contexto(self, instruccion: str) -> Dict:
        """Extrae parámetros clave de la instrucción usando IA"""
        
        prompt = f"""
        Analiza esta instrucción de video y extrae los parámetros:
        
        "{instruccion}"
        
        Responde en JSON con EXACTAMENTE estos campos (sin markdown):
        {{
            "tipo": "resultado|top3|comparativa|analisis|hilo|otro",
            "liga": "nba|euro|ambas",
            "equipo": "codigo_equipo_o_null",
            "jugador": "nombre_jugador_o_null",
            "periodo": "hoy|semana|mes|temporada|custom",
            "estadistica": "pts|3p|ast|reb|otros_o_null",
            "template": "tiktok|instagram|youtube|announcement|analysis|comparativa",
            "duracion_segundos": 30 a 60,
            "notas_especiales": "cualquier_requisito_adicional"
        }}
        
        Responde SOLO el JSON, sin explicaciones.
        """
        
        response = self.api.generate_text(
            prompt=prompt,
            providers=['gemini', 'claude']
        )
        
        # Limpiar respuesta (a veces viene con markdown)
        response = response.replace("```json", "").replace("```", "").strip()
        
        try:
            contexto = json.loads(response)
            return contexto
        except json.JSONDecodeError:
            print(f"⚠️ No se pudo parsear contexto, usando default: {response}")
            return {
                "tipo": "analisis",
                "liga": "nba",
                "template": "tiktok",
                "duracion_segundos": 45
            }
    
    def _consultar_datos(self, contexto: Dict) -> Dict:
        """Consulta SQLite según el contexto extraído"""
        
        liga = contexto.get("liga", "nba")
        periodo = contexto.get("periodo", "semana")
        estadistica = contexto.get("estadistica", "pts")
        
        # Construir consultas SQL dinámicamente
        # IMPORTANTE: Usa LIKE para SEASON_ID, no YEAR()
        
        if contexto["tipo"] == "top3":
            if liga == "nba":
                sql = f"""
                SELECT 
                    player_name, 
                    team_abbreviation,
                    {estadistica} as valor,
                    game_date
                FROM nba_stats
                WHERE game_date >= date('now', '-7 days')
                ORDER BY {estadistica} DESC
                LIMIT 3
                """
            else:  # euro
                sql = f"""
                SELECT 
                    player_name,
                    team_code,
                    {estadistica} as valor,
                    game_date
                FROM euro_stats
                WHERE game_date >= date('now', '-7 days')
                ORDER BY {estadistica} DESC
                LIMIT 3
                """
        
        elif contexto["tipo"] == "resultado":
            sql = """
            SELECT *
            FROM games
            WHERE game_date = date('now')
            ORDER BY game_date DESC
            LIMIT 5
            """
        
        else:
            sql = "SELECT player_name, team_abbreviation, pts FROM nba_stats LIMIT 10"
        
        try:
            datos = consultar_db_local(sql)
            return {"registros": datos, "count": len(datos)} if datos else {"registros": [], "count": 0}
        except Exception as e:
            print(f"⚠️ Error consultando BD: {e}")
            return {"registros": [], "count": 0, "error": str(e)}
    
    def _generar_prompt_claude(
        self, 
        instruccion: str, 
        datos_bd: Dict, 
        contexto: Dict
    ) -> str:
        """Genera el prompt para Claude que creará la composición Remotion"""
        
        template = contexto.get("template", "tiktok")
        duracion = contexto.get("duracion_segundos", 45)
        
        prompt = f"""
        Eres experto en crear videos deportivos profesionales con Remotion.
        
        INSTRUCCIÓN DEL USUARIO:
        "{instruccion}"
        
        CONTEXTO EXTRAÍDO:
        - Tipo de video: {contexto.get('tipo')}
        - Liga: {contexto.get('liga')}
        - Template: {template}
        - Duración: {duracion}s (aproximadamente {int(duracion * 30)} frames a 30fps)
        
        DATOS DE LA BASE DE DATOS (para usar en el video):
        {json.dumps(datos_bd, ensure_ascii=False, indent=2)}
        
        INSTRUCCIONES:
        1. Crea una composición Remotion en TypeScript/React que:
           - Use datos reales de la BD proporcionada
           - Implemente el template "{template}"
           - Dure aproximadamente {duracion} segundos
           - Incluya colores Dos Aros: Mint (#88D4AB) y Coral (#FF8787)
           - Sea atractiva para redes sociales
        
        2. Usa SOLO componentes disponibles en Editor Pro Max:
           - Text: AnimatedTitle, LowerThird, TypewriterText, WordByWordCaption, CaptionOverlay
           - Media: FitVideo, FitImage, VideoClip, JumpCut
           - Backgrounds: GradientBackground, ParticleField, ColorWash
           - Overlays: ProgressBar, Watermark, CallToAction
           - Transitions: Presets de transiciones
        
        3. La composición debe:
           - Ser válida en TypeScript 5.7+
           - Usar React 19 y Remotion 4.0.440
           - Exportarse como composición (export const MyComposition = ...)
           - Tener dimensiones: 1080x1920 para {template} (ajusta según template)
        
        4. Incluye datos reales en el video (nombres, estadísticas, etc.)
        
        ESTRUCTURA ESPERADA:
        ```tsx
        import {{ Composition, Sequence, interpolate, useCurrentFrame, useVideoConfig }} from 'remotion';
        import {{ AnimatedTitle, GradientBackground, CaptionOverlay }} from '../components';
        import {{ colores }} from '../presets/colors';
        
        export const MiComposicion = () => {{
          const frame = useCurrentFrame();
          const {{ fps, durationInFrames }} = useVideoConfig();
          
          return (
            <div style={{{{ width: '100%', height: '100%' }}}}>
              {{/* Tu composición aquí */}}
            </div>
          );
        }};
        ```
        
        Genera SOLO el código TypeScript válido de la composición, sin explicaciones adicionales.
        """
        
        return prompt
    
    def _generar_composicion_tsx(self, prompt_claude: str, contexto: Dict) -> str:
        """Usa Claude para generar la composición TSX"""
        
        print("🤖 Claude generando composición...")
        
        # Usar Claude con fallback
        response = self.api.generate_text(
            prompt=prompt_claude,
            system_prompt="Eres un experto en Remotion y React. Genera código limpio y válido.",
            providers=['claude', 'gemini']
        )
        
        # Limpiar markdown si lo hay
        if "```tsx" in response:
            response = response.split("```tsx")[1].split("```")[0]
        elif "```typescript" in response:
            response = response.split("```typescript")[1].split("```")[0]
        elif "```" in response:
            response = response.split("```")[1].split("```")[0]
        
        return response.strip()
    
    def _guardar_composicion(self, codigo_tsx: str, usuario_id: str) -> Path:
        """Guarda la composición en src/compositions/"""
        
        # Crear nombre único
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"user_{usuario_id}_{timestamp}.tsx"
        
        # Ruta en Editor Pro Max
        compositions_dir = self.editor_pro_max_path / "src" / "compositions"
        compositions_dir.mkdir(parents=True, exist_ok=True)
        
        archivo_path = compositions_dir / nombre_archivo
        
        with open(archivo_path, 'w') as f:
            f.write(codigo_tsx)
        
        print(f"💾 Composición guardada: {archivo_path}")
        return archivo_path
    
    def _renderizar_video(self, composicion_path: Path, usuario_id: str) -> Path:
        """Usa Remotion CLI para renderizar el video"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_salida = f"video_{usuario_id}_{timestamp}.mp4"
        
        output_path = self.output_dir / nombre_salida
        
        # Obtener nombre de la composición del archivo
        with open(composicion_path) as f:
            contenido = f.read()
            # Buscar: export const NombreComposicion
            import re
            match = re.search(r'export\s+const\s+(\w+)\s*=', contenido)
            nombre_composicion = match.group(1) if match else "MiComposicion"
        
        try:
            # Cambiar a directorio de Editor Pro Max
            os.chdir(self.editor_pro_max_path)
            
            # Comando Remotion
            cmd = [
                "npx",
                "remotion",
                "render",
                nombre_composicion,
                str(output_path),
                "--props",
                json.dumps({"usuario_id": usuario_id})
            ]
            
            print(f"🎬 Renderizando con Remotion...")
            print(f"   Comando: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            if result.returncode != 0:
                print(f"❌ Error Remotion: {result.stderr}")
                raise Exception(f"Remotion error: {result.stderr}")
            
            print(f"✅ Video renderizado: {output_path}")
            
            if not output_path.exists():
                raise FileNotFoundError(f"Video no encontrado en {output_path}")
            
            return output_path
        
        except subprocess.TimeoutExpired:
            raise Exception("⏱️ Timeout renderizando video (>10 min)")
        except Exception as e:
            raise Exception(f"Error renderizando: {e}")
```

---

## 🤖 PASO 3: Integración con tu Telegram Bot

### 3.1 Crear handler de Telegram

**Ubicación:** `src/integrations/telegram_video_handler.py`

```python
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from telegram import Update
from telegram.ext import ContextTypes
from video_generator.video_generator import VideoGenerator

class TelegramVideoHandler:
    """Maneja comandos de video desde Telegram"""
    
    def __init__(self):
        self.generator = VideoGenerator()
    
    async def handle_video_command(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):
        """
        Manejador del comando /video o /v
        
        Uso:
        /video Top 3 tiradores de 3P NBA esta semana
        /v Crea un video del resultado Celtics vs Lakers
        """
        
        usuario_id = str(update.effective_user.id)
        
        # Obtener el mensaje
        if len(context.args) == 0:
            await update.message.reply_text(
                "❌ Uso: /video <descripción>\n\n"
                "Ejemplos:\n"
                "• /video Top 3 tiradores 3P NBA esta semana\n"
                "• /video Video de los resultados de hoy\n"
                "• /video Comparativa NBA vs EuroLeague Luka Doncic"
            )
            return
        
        instruccion = " ".join(context.args)
        
        # Mostrar que está procesando
        mensaje_espera = await update.message.reply_text(
            f"⏳ Generando video...\n"
            f"Instrucción: {instruccion}\n\n"
            f"Esto puede tomar 1-5 minutos..."
        )
        
        try:
            # Generar video
            video_path = self.generator.generar_video(
                instruccion=instruccion,
                usuario_id=usuario_id
            )
            
            if not video_path:
                await mensaje_espera.edit_text(
                    "❌ Error generando video. Intenta de nuevo."
                )
                return
            
            # Enviar video
            await mensaje_espera.edit_text("📤 Enviando video...")
            
            with open(video_path, 'rb') as f:
                await update.message.reply_video(
                    video=f,
                    caption=f"✅ Video generado\n\n{instruccion}",
                    supports_streaming=True
                )
            
            await mensaje_espera.delete()
            
        except Exception as e:
            await mensaje_espera.edit_text(
                f"❌ Error: {str(e)[:200]}"
            )
    
    async def handle_video_status(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):
        """Comando para ver estado de videos en cola"""
        
        await update.message.reply_text(
            "📊 Estado:\n"
            "- Sistema listo\n"
            "- Editor Pro Max: ✅ Configurado\n"
            "- APIs: ✅ Conectadas\n"
            "- Remotion: ✅ Disponible"
        )
```

### 3.2 Integrar con tu main bot

**En tu archivo principal de Telegram (ej: `automation/bot_manager.py`):**

```python
from src.integrations.telegram_video_handler import TelegramVideoHandler

def setup_handlers(application):
    """Añade handlers de video"""
    
    video_handler = TelegramVideoHandler()
    
    # Comando /video
    application.add_handler(
        CommandHandler("video", video_handler.handle_video_command)
    )
    application.add_handler(
        CommandHandler("v", video_handler.handle_video_command)
    )
    
    # Comando /vstatus
    application.add_handler(
        CommandHandler("vstatus", video_handler.handle_video_status)
    )
    
    print("✅ Video handlers añadidos")

# En tu función main():
if __name__ == "__main__":
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # ... otros handlers ...
    
    # Añadir handlers de video
    setup_handlers(app)
    
    app.run_polling()
```

---

## 🚀 PASO 4: Usar con Claude Code

### 4.1 Crear `.claude/skills/video-generation`

Crea el directorio y archivo:

```bash
mkdir -p .claude/skills/video-generation
touch .claude/skills/video-generation/SKILL.md
```

**Contenido de `.claude/skills/video-generation/SKILL.md`:**

```markdown
# Video Generation Skill

Genera videos de Dos Aros usando Editor Pro Max + Claude Code.

## Uso rápido

```python
from src.integrations.video_generator import VideoGenerator

gen = VideoGenerator()
video_path = gen.generar_video(
    "Top 3 tiradores 3P NBA esta semana",
    usuario_id="telegram_12345"
)
```

## Composiciones disponibles

- `tiktok` - 1080x1920, 15-60s
- `instagram` - 1080x1920, 15-60s  
- `youtube_short` - 1080x1920, 15-60s
- `announcement` - 1920x1080, 30-60s
- `analysis` - 1920x1080, 45-90s
- `comparison` - 1920x1080, 45-90s

## Datos disponibles en SQLite

- `nba_stats` - Estadísticas NBA diarias
- `euro_stats` - Estadísticas EuroLeague
- `games` - Resultados de partidos
- `players` - Info de jugadores

## Ejemplos

### Ejemplo 1: Top 3 de la semana

\`\`\`python
gen.generar_video(
    "Crea un TikTok con los top 3 tiradores de 3 puntos NBA esta semana"
)
\`\`\`

### Ejemplo 2: Resultado de partido

\`\`\`python
gen.generar_video(
    "Video rápido (30s) del resultado Celtics vs Lakers hoy"
)
\`\`\`

### Ejemplo 3: Análisis comparativo

\`\`\`python
gen.generar_video(
    "Crea un video comparando Luka Doncic NBA vs EuroLeague"
)
\`\`\`
```

---

## 📝 PASO 5: Usando Claude Code

### 5.1 En claude.ai/code

```
/start

Quiero integrar Editor Pro Max con mi proyecto Dos Aros
para generar videos desde Telegram.

Estos son mis archivos:
- src/integrations/video_generator/video_generator.py
- src/integrations/telegram_video_handler.py
- src/utils/api_manager.py (para LLMs)
- src/database/database.py (para consultas SQLite)

¿Puedes ayudarme a:
1. Verificar que la estructura está correcta
2. Crear el archivo __init__.py para los módulos
3. Añadir manejo de errores mejorado
4. Crear ejemplos de prompts para videos
```

### 5.2 Comandos Útiles en Claude Code

```python
# Test rápido
python -c "
from src.integrations.video_generator import VideoGenerator
gen = VideoGenerator()
print('✅ VideoGenerator cargado correctamente')
"

# Test conexión APIs
python -c "
from src.utils.api_manager import APIManager
api = APIManager()
api.print_status()
"

# Test consulta BD
python -c "
from src.database.database import consultar_db_local
resultado = consultar_db_local('SELECT COUNT(*) FROM nba_stats')
print(resultado)
"
```

---

## 🧪 PASO 6: Testing

### 6.1 Test unitario básico

**Ubicación:** `tests/test_video_generator.py`

```python
import pytest
from src.integrations.video_generator import VideoGenerator

def test_video_generator_init():
    """Test que VideoGenerator se inicializa correctamente"""
    gen = VideoGenerator()
    assert gen.api is not None
    assert gen.editor_pro_max_path.exists()

def test_extraer_contexto():
    """Test extracción de contexto"""
    gen = VideoGenerator()
    contexto = gen._extraer_contexto(
        "Top 3 tiradores de 3 puntos NBA esta semana"
    )
    assert contexto.get("tipo") in ["top3", "analisis"]
    assert contexto.get("liga") == "nba"

def test_consultar_datos():
    """Test consulta a base de datos"""
    gen = VideoGenerator()
    contexto = {"tipo": "top3", "liga": "nba", "periodo": "semana"}
    datos = gen._consultar_datos(contexto)
    assert "registros" in datos
    assert "count" in datos

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

### 6.2 Ejecutar tests

```bash
cd ~/dos-aros
pip install pytest
python -m pytest tests/test_video_generator.py -v
```

---

## 🔑 PASO 7: Variables de Entorno Necesarias

### 7.1 Actualizar `.env`

```env
# APIs (ya tienes)
GEMINI_API_KEY=tu_key
CLAUDE_API_KEY=tu_key
GROQ_API_KEY=tu_key

# Telegram (ya tienes)
TELEGRAM_BOT_TOKEN=tu_token
TELEGRAM_CHAT_ID=tu_chat_id

# Editor Pro Max
REMOTION_EXPORT_FOLDER=./assets/video_output
REMOTION_FFMPEG_OVERRIDE=/usr/bin/ffmpeg
EDITOR_PRO_MAX_PATH=./editor_pro_max

# Video defaults
VIDEO_DEFAULT_FPS=30
VIDEO_DEFAULT_WIDTH=1080
VIDEO_DEFAULT_HEIGHT=1920
```

---

## 📚 PASO 8: Documentación Complementaria

### 8.1 Crear README de integración

**Ubicación:** `src/integrations/README.md`

```markdown
# Integraciones de Dos Aros

## Video Generator (Editor Pro Max)

Genera videos automáticamente usando Claude + Remotion.

### Instalación

1. Instalar dependencias
2. Copiar Editor Pro Max
3. Configurar .env
4. Integrar con Telegram Bot

### Uso desde Telegram

```
/video Top 3 tiradores 3P NBA
/v Crea un video del resultado de hoy
/vstatus Ver estado del sistema
```

### Uso programático

```python
from src.integrations.video_generator import VideoGenerator
gen = VideoGenerator()
video = gen.generar_video("Tu instrucción aquí")
```

### Componentes

- VideoGenerator - Motor principal
- TelegramVideoHandler - Handler de Telegram
- Remotion - Framework de renderizado
```

---

## ⚙️ PASO 9: Optimizaciones (Opcional pero recomendado)

### 9.1 Caché de composiciones

```python
# En VideoGenerator, añadir:
import hashlib

def _generar_hash_instruccion(self, instruccion: str) -> str:
    """Genera hash para caché"""
    return hashlib.md5(instruccion.encode()).hexdigest()[:8]

def _obtener_composicion_cached(self, instruccion: str) -> Optional[Path]:
    """Busca composición en caché"""
    hash_instr = self._generar_hash_instruccion(instruccion)
    cache_dir = self.editor_pro_max_path / "src" / "compositions" / ".cache"
    cache_file = cache_dir / f"{hash_instr}.tsx"
    
    if cache_file.exists():
        print(f"✅ Usando composición en caché")
        return cache_file
    return None
```

### 9.2 Cola de renderizado

```python
# En video_generator.py, añadir:
from queue import Queue
from threading import Thread

class VideoGeneratorWithQueue:
    def __init__(self):
        self.queue = Queue()
        self.renderer_thread = Thread(self._render_worker, daemon=True)
        self.renderer_thread.start()
    
    def _render_worker(self):
        """Worker que procesa videos en background"""
        while True:
            job = self.queue.get()
            self._renderizar_video(job['path'], job['user_id'])
```

### 9.3 Webhooks para notificaciones

```python
# En video_generator.py:
async def notificar_progreso(self, usuario_id: str, progreso: str):
    """Notifica progreso a través de webhooks"""
    # Llamada a tu bot para actualizar mensajes
    # await bot.edit_message_text(...)
    pass
```

---

## 🎯 Resumen Flujo Completo

```
1. Usuario envía: /video Top 3 tiradores 3P NBA
                          ↓
2. Telegram bot captura mensaje
                          ↓
3. TelegramVideoHandler.handle_video_command()
                          ↓
4. VideoGenerator.generar_video()
   - _extraer_contexto() → parámetros
   - _consultar_datos() → datos SQLite
   - _generar_prompt_claude() → prompt para IA
   - _generar_composicion_tsx() → Claude crea código
   - _guardar_composicion() → guarda en Editor Pro Max
   - _renderizar_video() → Remotion renderiza MP4
                          ↓
5. Devuelve ruta video al handler
                          ↓
6. Telegram bot envía video al usuario
                          ↓
7. ✅ Video recibido en Telegram
```

---

## 🐛 Troubleshooting

| Error | Solución |
|-------|----------|
| "Editor Pro Max no encontrado" | Verifica que clonaste/copiaste el repo en la ruta correcta |
| "Remotion command not found" | Instala Node.js + npm en editor_pro_max: `npm install` |
| "ffmpeg not found" | Instala ffmpeg: `sudo apt-get install ffmpeg` |
| "JSONDecodeError en contexto" | Claude a veces devuelve markdown, se limpia automáticamente |
| "Timeout renderizando" | Videos muy largos (>90s), reduce duración en parámetros |
| "Video muy pesado" | Remotion genera MP4 sin comprimir, usa ffmpeg después para comprimir |

---

## 📞 Comandos Claude Code Recomendados

```bash
# 1. Verificar estructura
claude /verify-structure

# 2. Test completo
claude /test video_generator

# 3. Debug de APIs
claude /debug api_manager

# 4. Analizar logs
claude /logs --last 50 --filter video

# 5. Optimizar rendimiento
claude /profile video_generator.generar_video
```

---

**Versión:** 1.0 | **Última actualización:** Marzo 2026 | **Estado:** Listo para implementación
