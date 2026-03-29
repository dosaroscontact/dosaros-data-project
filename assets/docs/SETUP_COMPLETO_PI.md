# 🚀 SETUP UNIFICADO DOS AROS - COPIAR Y PEGAR EN PI

## ⚡ BLOQUE 1: INSTALAR EDITOR PRO MAX (5 min)

```bash
ssh pi@192.168.1.136

# Ir a home
cd /home/pi

# Clonar Editor Pro Max si no lo tienes
if [ ! -d "editor-pro-max" ]; then
  git clone https://github.com/Hainrixz/editor-pro-max.git
  cd editor-pro-max
  npm install -q
  pip install -r requirements.txt -q
  echo "✅ Editor Pro Max instalado"
else
  echo "✅ Editor Pro Max ya existe"
fi

cd /home/pi/dosaros-data-project
```

---

## ⚡ BLOQUE 2: CONFIGURAR VIDEO GENERATOR (5 min)

```bash
cd /home/pi/dosaros-data-project

# Crear estructura
mkdir -p src/integrations/video_generator
mkdir -p assets/video_output
mkdir -p logs

touch src/integrations/__init__.py
touch src/integrations/video_generator/__init__.py

echo "✅ Estructura creada"
```

---

## ⚡ BLOQUE 3: CREAR video_generator.py

```bash
cat > src/integrations/video_generator/video_generator.py << 'EOF'
"""
VideoGenerator - Genera videos con Remotion + Claude
Integración con Dos Aros + Editor Pro Max
"""

import os
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class VideoGenerator:
    """Genera videos usando Remotion + Claude para composiciones"""
    
    def __init__(self):
        self.editor_path = Path(os.getenv("EDITOR_PRO_MAX_PATH", "./editor-pro-max"))
        self.output_dir = Path(os.getenv("VIDEO_OUTPUT_DIR", "./assets/video_output"))
        self.fps = int(os.getenv("VIDEO_DEFAULT_FPS", "30"))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Verificar dependencias
        self._check_dependencies()
        
    def _check_dependencies(self):
        """Verifica que Remotion, FFmpeg y Claude estén disponibles"""
        # FFmpeg
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True)
        if result.returncode != 0:
            raise RuntimeError("❌ ffmpeg no está instalado. Instala: sudo apt-get install ffmpeg")
        
        # Remotion
        result = subprocess.run(
            ["npx", "remotion", "--version"],
            cwd=self.editor_path,
            capture_output=True
        )
        if result.returncode != 0:
            raise RuntimeError("❌ Remotion no está listo. Corre: cd editor-pro-max && npm install")
        
        # Claude/Gemini API
        from src.utils.api_manager import APIManager
        self.api = APIManager()
    
    def generar_video(
        self,
        instruccion: str,
        usuario_id: str = "default",
        preset: str = "tiktok",
        duracion_segundos: int = 45
    ) -> Optional[str]:
        """
        Genera un video basado en instrucción en lenguaje natural
        
        Args:
            instruccion: Descripción del video en español
            usuario_id: ID del usuario (para logs)
            preset: tiktok, instagram, youtube, presentation
            duracion_segundos: Duración máxima del video
        
        Returns:
            Path del video generado o None si falla
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            composition_name = f"user_{usuario_id}_{timestamp}"
            
            logger.info(f"🎬 Generando video: {composition_name}")
            
            # 1. Extraer contexto
            contexto = self._extraer_contexto(instruccion)
            logger.info(f"📊 Contexto: {contexto}")
            
            # 2. Consultar datos
            datos = self._consultar_datos(contexto)
            logger.info(f"📈 Datos consultados: {len(str(datos))} caracteres")
            
            # 3. Generar prompt para Claude
            prompt = self._generar_prompt_claude(instruccion, datos, contexto)
            
            # 4. Generar composición TSX
            tsx_code = self._generar_composicion_tsx(prompt)
            
            # 5. Guardar composición
            composition_path = self._guardar_composicion(tsx_code, composition_name)
            logger.info(f"✅ Composición guardada: {composition_path}")
            
            # 6. Renderizar
            video_path = self._renderizar_video(composition_name, duracion_segundos)
            logger.info(f"✅ Video renderizado: {video_path}")
            
            return str(video_path) if video_path else None
        
        except Exception as e:
            logger.error(f"❌ Error generando video: {e}")
            return None
    
    def _extraer_contexto(self, instruccion: str) -> Dict[str, Any]:
        """Extrae tipo de video, liga, template, etc. usando IA"""
        try:
            prompt = f"""
            Analiza esta instrucción para generar video y extrae:
            - tipo: "top_3", "resultado", "comparativa", "viral", "highlight"
            - liga: "NBA", "EURO", "ambas"
            - template: "tiktok", "instagram", "youtube", "announcement"
            - duracion_segundos: 30-90
            
            Instrucción: {instruccion}
            
            Responde SOLO en JSON:
            {{"tipo": "...", "liga": "...", "template": "...", "duracion_segundos": ...}}
            """
            
            response = self.api.ask_claude(prompt, model="claude-3-5-sonnet")
            
            # Parse JSON (limpiar markdown si es necesario)
            json_str = response.strip()
            if json_str.startswith("```"):
                json_str = json_str.split("```")[1].replace("json", "", 1)
            
            return json.loads(json_str)
        
        except Exception as e:
            logger.warning(f"⚠️ Error extrayendo contexto, usando defaults: {e}")
            return {
                "tipo": "viral",
                "liga": "NBA",
                "template": "tiktok",
                "duracion_segundos": 45
            }
    
    def _consultar_datos(self, contexto: Dict[str, Any]) -> Dict[str, Any]:
        """Consulta SQLite según el contexto"""
        import sqlite3
        
        db_path = os.getenv("LOCAL_DB", "/mnt/nba_data/dosaros_local.db")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        datos = {"tipo": contexto.get("tipo"), "liga": contexto.get("liga")}
        
        try:
            # Según tipo de video
            tipo = contexto.get("tipo", "viral")
            liga = contexto.get("liga", "NBA")
            
            if tipo == "top_3":
                # Top 3 jugadores
                query = f"""
                SELECT 
                    player_name, team_abbreviation, points, rebounds, assists, 
                    field_goal_percentage, three_point_percentage
                FROM {'nba_players_games' if liga == 'NBA' else 'euro_players_games'}
                WHERE season_id = (SELECT MAX(season_id) FROM {'nba_players_games' if liga == 'NBA' else 'euro_players_games'})
                ORDER BY points DESC LIMIT 3
                """
                cursor.execute(query)
                datos["top_3"] = [dict(row) for row in cursor.fetchall()]
            
            elif tipo == "resultado":
                # Último partido
                query = f"""
                SELECT 
                    date, home_team_name, away_team_name, 
                    home_team_points, away_team_points,
                    season_id
                FROM {'nba_games' if liga == 'NBA' else 'euro_games'}
                ORDER BY date DESC LIMIT 1
                """
                cursor.execute(query)
                row = cursor.fetchone()
                if row:
                    datos["ultimo_partido"] = dict(row)
            
            elif tipo == "comparativa":
                # Stats comparativos
                query = f"""
                SELECT 
                    player_name, team_abbreviation, 
                    AVG(points) as puntos_media,
                    AVG(rebounds) as rebotes_media,
                    AVG(assists) as asistencias_media
                FROM {'nba_players_games' if liga == 'NBA' else 'euro_players_games'}
                WHERE season_id = (SELECT MAX(season_id) FROM {'nba_players_games' if liga == 'NBA' else 'euro_players_games'})
                GROUP BY player_name
                LIMIT 5
                """
                cursor.execute(query)
                datos["comparativa"] = [dict(row) for row in cursor.fetchall()]
        
        except Exception as e:
            logger.warning(f"⚠️ Error consultando datos: {e}")
        
        finally:
            conn.close()
        
        return datos
    
    def _generar_prompt_claude(self, instruccion: str, datos: Dict, contexto: Dict) -> str:
        """Genera prompt detallado para Claude que cree la composición Remotion"""
        
        datos_str = json.dumps(datos, indent=2, ensure_ascii=False)
        
        prompt = f"""
        Eres un experto en Remotion (React framework para videos).
        Crea una composición TypeScript/React para un video {contexto.get('template', 'tiktok')}.
        
        INSTRUCCIÓN DEL USUARIO:
        {instruccion}
        
        DATOS DISPONIBLES:
        {datos_str}
        
        REQUISITOS:
        1. Usa Remotion v4.0+
        2. Duración: {contexto.get('duracion_segundos', 45)} segundos (en frames: {contexto.get('duracion_segundos', 45) * 30} @ 30fps)
        3. Dimensiones: 1080x1920 (9:16 vertical para TikTok/Instagram)
        4. Colores Dos Aros: Mint (#88D4AB), Coral (#FF8787)
        5. Incluir logo Dos Aros (texto blanco)
        6. Componentes permitidos: Text, Image, Sequence, AbsoluteFill, Spring
        7. NO usar audio, NO usar fetch
        8. Exportar como: export const CompositionName = () => { ... }
        
        ESTRUCTURA MÍNIMA:
        ```tsx
        import {{ Composition, Sequence, AbsoluteFill, Text, spring, interpolate }} from "remotion";
        
        export const CompositionName = () => {{
          const durationInFrames = {contexto.get('duracion_segundos', 45) * 30};
          
          return (
            <AbsoluteFill style={{{{ backgroundColor: "#000" }}}}>
              {/* Tu contenido aquí */}
            </AbsoluteFill>
          );
        }};
        ```
        
        RESPONDE SOLO CON CÓDIGO TSX VÁLIDO, SIN EXPLICACIONES.
        """
        
        return prompt
    
    def _generar_composicion_tsx(self, prompt: str) -> str:
        """Llama a Claude para generar el código TSX"""
        try:
            response = self.api.ask_claude(prompt, model="claude-3-5-sonnet")
            
            # Limpiar markdown
            if "```" in response:
                tsx_code = response.split("```")[1]
                if tsx_code.startswith("tsx"):
                    tsx_code = tsx_code[3:]
            else:
                tsx_code = response
            
            return tsx_code.strip()
        
        except Exception as e:
            logger.error(f"❌ Error generando composición: {e}")
            return ""
    
    def _guardar_composicion(self, tsx_code: str, composition_name: str) -> Path:
        """Guarda la composición en editor-pro-max/src/compositions/"""
        
        compositions_dir = self.editor_path / "src" / "compositions"
        compositions_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = compositions_dir / f"{composition_name}.tsx"
        file_path.write_text(tsx_code, encoding="utf-8")
        
        return file_path
    
    def _renderizar_video(self, composition_name: str, duracion_segundos: int = 45) -> Optional[Path]:
        """Renderiza la composición con Remotion"""
        
        output_file = self.output_dir / f"{composition_name}.mp4"
        
        try:
            cmd = [
                "npx",
                "remotion",
                "render",
                composition_name,
                str(output_file),
                "--fps", str(self.fps),
                "--height", "1920",
                "--width", "1080"
            ]
            
            logger.info(f"🎬 Renderizando: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                cwd=self.editor_path,
                capture_output=True,
                timeout=600  # 10 min max
            )
            
            if result.returncode == 0 and output_file.exists():
                size_mb = output_file.stat().st_size / (1024 * 1024)
                logger.info(f"✅ Video renderizado: {size_mb:.2f} MB")
                return output_file
            else:
                logger.error(f"❌ Remotion error: {result.stderr.decode()}")
                return None
        
        except subprocess.TimeoutExpired:
            logger.error("❌ Timeout renderizando (> 10 min)")
            return None
        except Exception as e:
            logger.error(f"❌ Error renderizando: {e}")
            return None

EOF

echo "✅ video_generator.py creado"
```

---

## ⚡ BLOQUE 4: CREAR telegram_video_handler.py

```bash
cat > src/integrations/telegram_video_handler.py << 'EOF'
"""
Handlers de Telegram para generación de videos
Integra VideoGenerator con el bot
"""

from telegram import Update
from telegram.ext import Application, ContextTypes, CommandHandler
from telegram.constants import ChatAction
import logging
import asyncio
from pathlib import Path

from .video_generator.video_generator import VideoGenerator

logger = logging.getLogger(__name__)


class TelegramVideoHandler:
    """Maneja comandos de video en Telegram"""
    
    def __init__(self, video_generator: VideoGenerator):
        self.gen = video_generator
    
    async def handle_video_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        /video <instrucción>
        /v <instrucción>
        
        Genera un video basado en la instrucción del usuario
        """
        
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        
        # Obtener instrucción
        if not context.args:
            await update.message.reply_text(
                "📝 Uso: /video <instrucción>\n\n"
                "Ejemplos:\n"
                "🏀 /video Top 3 tiradores 3P NBA esta semana\n"
                "🏆 /video Resultado último partido Celtics\n"
                "⚖️ /video Comparativa Luka vs SGA"
            )
            return
        
        instruccion = " ".join(context.args)
        
        # Feedback inmediato
        msg = await update.message.reply_text(
            f"⏳ Generando video...\n\nInstrucción: {instruccion}\n\n"
            f"Esto puede tardar 2-5 minutos."
        )
        
        # Mostrar "typing"
        await context.bot.send_chat_action(chat_id, ChatAction.RECORD_VIDEO)
        
        try:
            # Generar video
            video_path = self.gen.generar_video(
                instruccion=instruccion,
                usuario_id=f"tg_{user_id}",
                preset="tiktok"
            )
            
            if video_path and Path(video_path).exists():
                # Enviar video
                with open(video_path, "rb") as f:
                    await update.effective_chat.send_video(
                        f,
                        caption=f"✅ Video generado\n\n📝 {instruccion}",
                        width=1080,
                        height=1920
                    )
                
                # Actualizar mensaje
                await msg.edit_text(f"✅ Video enviado!")
                logger.info(f"✅ Video generado para usuario {user_id}")
            
            else:
                await msg.edit_text(
                    "❌ Error generando video. Intenta:\n"
                    "- Una instrucción más específica\n"
                    "- Otra liga (NBA vs Euroliga)\n"
                    "- Otro tipo (top 3, resultado, etc)"
                )
        
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            await msg.edit_text(f"❌ Error: {str(e)[:100]}")
    
    async def handle_video_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        /vstatus
        Muestra estado del sistema y APIs
        """
        try:
            status = self.gen.api.print_status()
            await update.message.reply_text(f"📊 Estado del sistema:\n\n{status}")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {e}")
    
    async def handle_video_list(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        /vlist
        Lista videos generados por el usuario
        """
        user_id = update.effective_user.id
        videos_dir = Path(self.gen.output_dir)
        
        user_videos = list(videos_dir.glob(f"*tg_{user_id}*.mp4"))
        
        if not user_videos:
            await update.message.reply_text("📹 No tienes videos generados aún.")
            return
        
        text = "📹 Tus videos generados:\n\n"
        for i, video in enumerate(sorted(user_videos, reverse=True)[:5], 1):
            size_mb = video.stat().st_size / (1024 * 1024)
            text += f"{i}. {video.name} ({size_mb:.1f} MB)\n"
        
        await update.message.reply_text(text)


def setup_video_handlers(application: Application, video_generator: VideoGenerator):
    """
    Registra todos los handlers de video en el bot
    
    Uso en bot_consultas.py:
        from src.integrations import setup_video_handlers, VideoGenerator
        
        app = Application.builder().token(TOKEN).build()
        gen = VideoGenerator()
        setup_video_handlers(app, gen)
    """
    
    handler = TelegramVideoHandler(video_generator)
    
    # Comandos
    application.add_handler(CommandHandler("video", handler.handle_video_command))
    application.add_handler(CommandHandler("v", handler.handle_video_command))
    application.add_handler(CommandHandler("vstatus", handler.handle_video_status))
    application.add_handler(CommandHandler("vlist", handler.handle_video_list))
    
    logger.info("✅ Video handlers registrados")

EOF

echo "✅ telegram_video_handler.py creado"
```

---

## ⚡ BLOQUE 5: CREAR __init__.py

```bash
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

echo "✅ __init__.py creados"
```

---

## ⚡ BLOQUE 6: ACTUALIZAR .env

```bash
# Añadir variables de Editor Pro Max al .env
cat >> .env << 'EOF'

# Editor Pro Max - Video Generation
EDITOR_PRO_MAX_PATH=/home/pi/editor-pro-max
VIDEO_OUTPUT_DIR=./assets/video_output
VIDEO_DEFAULT_FPS=30
VIDEO_MAX_DURATION=90
EOF

echo "✅ .env actualizado"
```

---

## ⚡ BLOQUE 7: TEST RÁPIDO

```bash
cd /home/pi/dosaros-data-project

echo "🧪 Test 1: VideoGenerator carga..."
PYTHONPATH=/home/pi/dosaros-data-project \
  venv/bin/python -c "
from src.integrations import VideoGenerator
try:
    gen = VideoGenerator()
    print('✅ VideoGenerator OK')
except Exception as e:
    print(f'❌ Error: {e}')
"

echo ""
echo "🧪 Test 2: Importar handlers..."
PYTHONPATH=/home/pi/dosaros-data-project \
  venv/bin/python -c "
from src.integrations import setup_video_handlers
print('✅ Handlers OK')
" || echo "❌ Error en handlers"

echo ""
echo "✅ SETUP COMPLETO LISTO"
```

---

## 📋 SIGUIENTE: INTEGRAR CON TU BOT

En `src/automation/bot_consultas.py`, busca donde haces `Application.builder()` y añade:

```python
# ARRIBA DEL TODO
from src.integrations import setup_video_handlers, VideoGenerator

# En la función main() o donde inicies el bot:

def main():
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    app = Application.builder().token(TOKEN).build()
    
    # ... tus handlers existentes ...
    
    # ✨ AÑADIR ESTO:
    try:
        video_gen = VideoGenerator()
        setup_video_handlers(app, video_gen)
        print("✅ Video handlers configurados")
    except Exception as e:
        print(f"⚠️ Video deshabilitado: {e}")
    
    app.run_polling()

if __name__ == "__main__":
    main()
```

---

## 📅 SIGUIENTE: INTEGRAR CON MASTER_SYNC

En `src/automation/master_sync.py`, después de generar la imagen story, añade:

```python
print("\n🎬 Generando video del día...")
try:
    from src.integrations import VideoGenerator
    
    gen = VideoGenerator()
    
    # Usar la mejor perla del día
    if perlas and len(perlas) > 0:
        perla = perlas[0]
        
        prompt = f"""
        Crea un video corto (30-45 segundos) para TikTok/Instagram Reel:
        
        📊 Titulares del día:
        - Jugador: {perla.get('jugador', 'N/A')}
        - Equipo: {perla.get('equipo', 'N/A')}
        - Estadísticas: {perla.get('stats', 'N/A')}
        - Liga: {perla.get('liga', 'NBA')}
        
        Crea algo visual, energético y listo para redes sociales.
        Usa colores del equipo y el logo Dos Aros.
        """
        
        video_path = gen.generar_video(
            instruccion=prompt,
            usuario_id="master_sync",
            preset="tiktok"
        )
        
        if video_path:
            # Enviar a Telegram
            with open(video_path, "rb") as f:
                bot.send_video(
                    chat_id=TELEGRAM_CHAT_ID,
                    video=f,
                    caption=f"🎬 Video del día: {perla.get('titulo', 'Highlight')}"
                )
            print(f"✅ Video enviado: {video_path}")
        else:
            print("⚠️ Error generando video (continuamos sin él)")

except Exception as e:
    print(f"⚠️ Video skipped: {e}")

# Continuar con el resto del proceso (tweets, etc)
```

---

## ✅ CHECKLIST FINAL

Ejecuta esto después del setup para verificar:

```bash
cd /home/pi/dosaros-data-project

# 1. Estructura creada ✅
ls -la src/integrations/

# 2. Archivos presentes ✅
ls -la src/integrations/video_generator/
ls -la src/integrations/telegram_video_handler.py

# 3. .env actualizado ✅
grep "EDITOR_PRO_MAX_PATH" .env

# 4. Editor Pro Max listo ✅
ls -la /home/pi/editor-pro-max/package.json

# 5. npm instalado ✅
ls -la /home/pi/editor-pro-max/node_modules | head -5

# 6. Python deps ✅
venv/bin/pip list | grep -E "remotion|pillow|huggingface"

echo "✅ TODO OK - LISTO PARA VIDEOS"
```

---

## 🚀 COMANDOS ÚTILES DESPUÉS

```bash
cd /home/pi/dosaros-data-project

# Ver logs de videos
tail -f logs/video_*.log

# Listar videos generados
ls -lh assets/video_output/

# Eliminar videos antiguos (mantener últimos 10)
ls -t assets/video_output/*.mp4 | tail -n +11 | xargs rm -f

# Test manualmente
PYTHONPATH=/home/pi/dosaros-data-project \
  venv/bin/python -c "
from src.integrations import VideoGenerator
gen = VideoGenerator()
video = gen.generar_video('Top 3 anotadores NBA esta semana', 'test_001')
print(f'✅ Video: {video}')
"

# Ver estado de APIs
PYTHONPATH=/home/pi/dosaros-data-project \
  venv/bin/python -c "
from src.utils.api_manager import APIManager
api = APIManager()
api.print_status()
"
```

---

**Cuando termines el BLOQUE 7 (TEST), avísame y pasamos a integrar con tu bot.** 🎬

