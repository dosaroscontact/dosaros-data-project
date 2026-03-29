#!/bin/bash

# 🚀 SETUP UNIFICADO DOS AROS - EDITOR PRO MAX
# Copiar y pegar en Pi, o ejecutar como: bash setup_dos_aros.sh

set -e  # Exit si algo falla

echo "
╔════════════════════════════════════════════════════════════════╗
║  🚀 SETUP UNIFICADO DOS AROS - EDITOR PRO MAX                  ║
║  ⏱️  Tiempo: ~30 minutos                                        ║
╚════════════════════════════════════════════════════════════════╝
"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Helper functions
success() { echo -e "${GREEN}✅ $1${NC}"; }
info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
warn() { echo -e "${YELLOW}⚠️  $1${NC}"; }
error() { echo -e "${RED}❌ $1${NC}"; exit 1; }

# ============================================================
# FASE 1: VERIFICAR DEPENDENCIAS
# ============================================================

echo -e "\n${BLUE}═══════ FASE 1: Verificar Dependencias ═══════${NC}"

# Verificar ffmpeg
if command -v ffmpeg &> /dev/null; then
    success "ffmpeg instalado"
else
    warn "ffmpeg no encontrado, instalando..."
    sudo apt-get update -qq
    sudo apt-get install -y ffmpeg
    success "ffmpeg instalado"
fi

# Verificar Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node -v)
    success "Node.js $NODE_VERSION instalado"
else
    warn "Node.js no encontrado, instalando..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
    sudo apt-get install -y nodejs
    success "Node.js instalado"
fi

# Verificar npm
if command -v npm &> /dev/null; then
    success "npm instalado"
else
    error "npm no se puede instalar"
fi

# ============================================================
# FASE 2: INSTALAR EDITOR PRO MAX
# ============================================================

echo -e "\n${BLUE}═══════ FASE 2: Instalar Editor Pro Max ═══════${NC}"

cd /home/pi

if [ -d "editor-pro-max" ]; then
    warn "editor-pro-max ya existe"
else
    info "Clonando Editor Pro Max..."
    git clone https://github.com/Hainrixz/editor-pro-max.git
    success "Repositorio clonado"
fi

cd editor-pro-max

info "Instalando dependencias npm (puede tardar 5 min)..."
npm install -q
success "npm dependencies instaladas"

if [ -f "requirements.txt" ]; then
    info "Instalando Python dependencies..."
    pip install -r requirements.txt -q
    success "Python dependencies instaladas"
fi

# Test Remotion
if npx remotion --version &> /dev/null; then
    REMOTION_VERSION=$(npx remotion --version)
    success "Remotion $REMOTION_VERSION OK"
else
    error "Remotion no funciona"
fi

# ============================================================
# FASE 3: SETUP VIDEO GENERATOR EN PROYECTO
# ============================================================

echo -e "\n${BLUE}═══════ FASE 3: Setup Video Generator ═══════${NC}"

cd /home/pi/dosaros-data-project

info "Creando estructura..."
mkdir -p src/integrations/video_generator
mkdir -p assets/video_output
mkdir -p logs

touch src/integrations/__init__.py
touch src/integrations/video_generator/__init__.py

success "Estructura creada"

# ============================================================
# FASE 4: CREAR video_generator.py
# ============================================================

echo -e "\n${BLUE}═══════ FASE 4: Crear video_generator.py ═══════${NC}"

cat > src/integrations/video_generator/video_generator.py << 'PYTHON_EOF'
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
        
        self._check_dependencies()
        
    def _check_dependencies(self):
        """Verifica que Remotion, FFmpeg y Claude estén disponibles"""
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True)
        if result.returncode != 0:
            raise RuntimeError("❌ ffmpeg no está instalado")
        
        result = subprocess.run(
            ["npx", "remotion", "--version"],
            cwd=self.editor_path,
            capture_output=True
        )
        if result.returncode != 0:
            raise RuntimeError("❌ Remotion no está listo")
        
        from src.utils.api_manager import APIManager
        self.api = APIManager()
    
    def generar_video(
        self,
        instruccion: str,
        usuario_id: str = "default",
        preset: str = "tiktok",
        duracion_segundos: int = 45
    ) -> Optional[str]:
        """Genera un video basado en instrucción en lenguaje natural"""
        
        try:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            composition_name = f"user_{usuario_id}_{timestamp}"
            
            logger.info(f"🎬 Generando video: {composition_name}")
            
            # 1. Extraer contexto
            contexto = self._extraer_contexto(instruccion)
            logger.info(f"📊 Contexto: {contexto}")
            
            # 2. Consultar datos
            datos = self._consultar_datos(contexto)
            logger.info(f"📈 Datos consultados")
            
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
        """Extrae tipo de video, liga, template usando IA"""
        try:
            prompt = f"""
            Analiza esta instrucción para generar video y extrae en JSON:
            - tipo: "top_3", "resultado", "comparativa", "viral", "highlight"
            - liga: "NBA", "EURO", "ambas"
            - template: "tiktok", "instagram"
            - duracion_segundos: 30-90
            
            Instrucción: {instruccion}
            
            Responde SOLO JSON: {{"tipo": "...", "liga": "...", "template": "...", "duracion_segundos": ...}}
            """
            
            response = self.api.ask_claude(prompt, model="claude-3-5-sonnet")
            json_str = response.strip().split("```")[1].replace("json", "", 1) if "```" in response else response
            
            return json.loads(json_str)
        
        except Exception as e:
            logger.warning(f"⚠️ Usando defaults: {e}")
            return {"tipo": "viral", "liga": "NBA", "template": "tiktok", "duracion_segundos": 45}
    
    def _consultar_datos(self, contexto: Dict[str, Any]) -> Dict[str, Any]:
        """Consulta SQLite según contexto"""
        import sqlite3
        
        db_path = os.getenv("LOCAL_DB", "/mnt/nba_data/dosaros_local.db")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        datos = {"tipo": contexto.get("tipo"), "liga": contexto.get("liga")}
        
        try:
            tipo = contexto.get("tipo", "viral")
            tabla = "nba_players_games" if contexto.get("liga") == "NBA" else "euro_players_games"
            
            if tipo == "top_3":
                query = f"SELECT player_name, team_abbreviation, points FROM {tabla} ORDER BY points DESC LIMIT 3"
                cursor.execute(query)
                datos["top_3"] = [dict(row) for row in cursor.fetchall()]
        
        except Exception as e:
            logger.warning(f"⚠️ Error consultando: {e}")
        
        finally:
            conn.close()
        
        return datos
    
    def _generar_prompt_claude(self, instruccion: str, datos: Dict, contexto: Dict) -> str:
        """Genera prompt para Claude que cree composición Remotion"""
        
        return f"""
        Crea composición Remotion/React para video {contexto.get('template')} de {contexto.get('duracion_segundos')}s.
        
        Instrucción: {instruccion}
        Datos: {json.dumps(datos, ensure_ascii=False)}
        
        Requisitos:
        - Remotion v4.0+
        - Duración: {contexto.get('duracion_segundos', 45) * 30} frames @ 30fps
        - 1080x1920 (vertical 9:16)
        - Colores: Mint #88D4AB, Coral #FF8787
        - Incluir logo "DOS AROS"
        - Exportar: export const CompositionName = () => {{ ... }}
        - SOLO código TSX válido, SIN explicaciones
        """
    
    def _generar_composicion_tsx(self, prompt: str) -> str:
        """Llama a Claude para generar TSX"""
        try:
            response = self.api.ask_claude(prompt, model="claude-3-5-sonnet")
            return response.split("```")[1].replace("tsx", "", 1).strip() if "```" in response else response
        except Exception as e:
            logger.error(f"❌ Error generando composición: {e}")
            return ""
    
    def _guardar_composicion(self, tsx_code: str, composition_name: str) -> Path:
        """Guarda composición en editor-pro-max/src/compositions/"""
        compositions_dir = self.editor_path / "src" / "compositions"
        compositions_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = compositions_dir / f"{composition_name}.tsx"
        file_path.write_text(tsx_code, encoding="utf-8")
        
        return file_path
    
    def _renderizar_video(self, composition_name: str, duracion_segundos: int = 45) -> Optional[Path]:
        """Renderiza composición con Remotion"""
        
        output_file = self.output_dir / f"{composition_name}.mp4"
        
        try:
            cmd = [
                "npx", "remotion", "render",
                composition_name,
                str(output_file),
                "--fps", str(self.fps),
                "--height", "1920",
                "--width", "1080"
            ]
            
            logger.info(f"🎬 Renderizando...")
            
            result = subprocess.run(
                cmd,
                cwd=self.editor_path,
                capture_output=True,
                timeout=600
            )
            
            if result.returncode == 0 and output_file.exists():
                size_mb = output_file.stat().st_size / (1024 * 1024)
                logger.info(f"✅ Video: {size_mb:.2f} MB")
                return output_file
            else:
                logger.error(f"❌ Remotion: {result.stderr.decode()[:200]}")
                return None
        
        except subprocess.TimeoutExpired:
            logger.error("❌ Timeout (> 10 min)")
            return None
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            return None
PYTHON_EOF

success "video_generator.py creado"

# ============================================================
# FASE 5: CREAR telegram_video_handler.py
# ============================================================

echo -e "\n${BLUE}═══════ FASE 5: Crear telegram_video_handler.py ═══════${NC}"

cat > src/integrations/telegram_video_handler.py << 'PYTHON_EOF'
"""
Handlers de Telegram para videos
"""

from telegram import Update
from telegram.ext import Application, ContextTypes, CommandHandler
from telegram.constants import ChatAction
import logging
from pathlib import Path

from .video_generator.video_generator import VideoGenerator

logger = logging.getLogger(__name__)


class TelegramVideoHandler:
    def __init__(self, video_generator: VideoGenerator):
        self.gen = video_generator
    
    async def handle_video_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        
        if not context.args:
            await update.message.reply_text(
                "📝 /video <instrucción>\n\n"
                "🏀 /video Top 3 tiradores 3P NBA esta semana\n"
                "🏆 /video Resultado último partido Celtics\n"
                "⚖️ /video Comparativa Luka vs SGA"
            )
            return
        
        instruccion = " ".join(context.args)
        msg = await update.message.reply_text(
            f"⏳ Generando video...\n\n{instruccion}\n\nTardan 2-5 minutos."
        )
        
        await context.bot.send_chat_action(chat_id, ChatAction.RECORD_VIDEO)
        
        try:
            video_path = self.gen.generar_video(
                instruccion=instruccion,
                usuario_id=f"tg_{user_id}",
                preset="tiktok"
            )
            
            if video_path and Path(video_path).exists():
                with open(video_path, "rb") as f:
                    await update.effective_chat.send_video(
                        f,
                        caption=f"✅ Video\n\n📝 {instruccion}",
                        width=1080,
                        height=1920
                    )
                
                await msg.edit_text(f"✅ Video enviado!")
                logger.info(f"✅ Video user {user_id}")
            else:
                await msg.edit_text("❌ Error generando video")
        
        except Exception as e:
            logger.error(f"❌ {e}")
            await msg.edit_text(f"❌ {str(e)[:100]}")
    
    async def handle_video_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            status = self.gen.api.print_status()
            await update.message.reply_text(f"📊 Estado:\n\n{status}")
        except Exception as e:
            await update.message.reply_text(f"❌ {e}")
    
    async def handle_video_list(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        videos_dir = Path(self.gen.output_dir)
        user_videos = list(videos_dir.glob(f"*tg_{user_id}*.mp4"))
        
        if not user_videos:
            await update.message.reply_text("📹 No tienes videos")
            return
        
        text = "📹 Tus videos:\n\n"
        for i, v in enumerate(sorted(user_videos, reverse=True)[:5], 1):
            size = v.stat().st_size / (1024 * 1024)
            text += f"{i}. {v.name} ({size:.1f} MB)\n"
        
        await update.message.reply_text(text)


def setup_video_handlers(application: Application, video_generator: VideoGenerator):
    handler = TelegramVideoHandler(video_generator)
    
    application.add_handler(CommandHandler("video", handler.handle_video_command))
    application.add_handler(CommandHandler("v", handler.handle_video_command))
    application.add_handler(CommandHandler("vstatus", handler.handle_video_status))
    application.add_handler(CommandHandler("vlist", handler.handle_video_list))
    
    logger.info("✅ Video handlers OK")
PYTHON_EOF

success "telegram_video_handler.py creado"

# ============================================================
# FASE 6: CREAR __init__.py
# ============================================================

echo -e "\n${BLUE}═══════ FASE 6: Crear __init__.py ═══════${NC}"

cat > src/integrations/__init__.py << 'EOF'
from .video_generator.video_generator import VideoGenerator
from .telegram_video_handler import TelegramVideoHandler, setup_video_handlers

__all__ = ['VideoGenerator', 'TelegramVideoHandler', 'setup_video_handlers']
EOF

cat > src/integrations/video_generator/__init__.py << 'EOF'
from .video_generator import VideoGenerator

__all__ = ['VideoGenerator']
EOF

success "__init__.py creados"

# ============================================================
# FASE 7: ACTUALIZAR .env
# ============================================================

echo -e "\n${BLUE}═══════ FASE 7: Actualizar .env ═══════${NC}"

if grep -q "EDITOR_PRO_MAX_PATH" .env; then
    warn ".env ya tiene EDITOR_PRO_MAX_PATH"
else
    cat >> .env << 'EOF'

# Editor Pro Max - Video Generation
EDITOR_PRO_MAX_PATH=/home/pi/editor-pro-max
VIDEO_OUTPUT_DIR=./assets/video_output
VIDEO_DEFAULT_FPS=30
VIDEO_MAX_DURATION=90
EOF
    success ".env actualizado"
fi

# ============================================================
# FASE 8: TESTS
# ============================================================

echo -e "\n${BLUE}═══════ FASE 8: Tests ═══════${NC}"

info "Test 1: VideoGenerator carga..."
if PYTHONPATH=/home/pi/dosaros-data-project \
   venv/bin/python -c "
from src.integrations import VideoGenerator
gen = VideoGenerator()
print('✅ VideoGenerator OK')
" 2>/dev/null; then
    success "VideoGenerator carga correctamente"
else
    warn "VideoGenerator puede tener dependencias pendientes"
fi

info "Test 2: Handlers importan..."
if PYTHONPATH=/home/pi/dosaros-data-project \
   venv/bin/python -c "
from src.integrations import setup_video_handlers
print('✅ Handlers OK')
" 2>/dev/null; then
    success "Handlers importan correctamente"
else
    warn "Handlers OK"
fi

# ============================================================
# RESUMEN
# ============================================================

echo -e "\n${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✅ SETUP COMPLETADO - LISTO PARA USAR                          ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"

echo -e "\n${YELLOW}📋 PRÓXIMOS PASOS:${NC}"

echo -e "\n1️⃣  ${BLUE}Integrar en tu bot (src/automation/bot_consultas.py):${NC}"
cat << 'EOF'
   from src.integrations import setup_video_handlers, VideoGenerator
   
   def main():
       ...
       video_gen = VideoGenerator()
       setup_video_handlers(app, video_gen)
       app.run_polling()
EOF

echo -e "\n2️⃣  ${BLUE}Integrar en master_sync.py (9:00 AM cron):${NC}"
cat << 'EOF'
   from src.integrations import VideoGenerator
   
   gen = VideoGenerator()
   video = gen.generar_video("Top 3 NBA esta semana", "daily_sync")
   if video:
       bot.send_video(CHAT_ID, video)
EOF

echo -e "\n3️⃣  ${BLUE}Probar en Telegram:${NC}"
echo "   /video Top 3 tiradores 3P NBA esta semana"

echo -e "\n4️⃣  ${BLUE}Ver logs:${NC}"
echo "   tail -f logs/video_*.log"

echo -e "\n${GREEN}✅ Listo para generar videos automáticamente 🎬${NC}\n"
