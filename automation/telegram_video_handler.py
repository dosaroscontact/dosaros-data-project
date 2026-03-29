"""
TelegramVideoHandler para Dos Aros
Maneja comandos /video, /v en Telegram

Integración con python-telegram-bot
"""

import os
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, os.path.dirname(__file__))

try:
    from telegram import Update
    from telegram.ext import ContextTypes
except ImportError:
    print("⚠️ python-telegram-bot no instalado: pip install python-telegram-bot")
    Update = None
    ContextTypes = None

from video_generator import VideoGenerator


class TelegramVideoHandler:
    """Maneja comandos de video desde Telegram"""
    
    def __init__(self, video_generator: Optional[VideoGenerator] = None):
        """
        Inicializa el handler.
        
        Args:
            video_generator: Instancia de VideoGenerator (crea nueva si no se proporciona)
        """
        self.generator = video_generator or VideoGenerator()
        self.active_jobs = {}  # Tracking de trabajos activos
    
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
        
        Args:
            update: Update de Telegram
            context: Context de la conversación
        """
        
        usuario_id = str(update.effective_user.id)
        username = update.effective_user.username or "usuario"
        
        # Validar que hay argumento
        if len(context.args) == 0:
            await update.message.reply_text(
                "❌ <b>Uso:</b> /video &lt;descripción&gt;\n\n"
                "<b>Ejemplos:</b>\n"
                "• /video Top 3 tiradores 3P NBA esta semana\n"
                "• /video Video de los resultados de hoy\n"
                "• /video Comparativa NBA vs EuroLeague Luka Doncic\n"
                "• /video Último partido Celtics\n\n"
                "⏱️ <i>El primer video puede tardar 2-5 minutos</i>",
                parse_mode="HTML"
            )
            return
        
        # Obtener instrucción
        instruccion = " ".join(context.args)
        
        # Verificar longitud
        if len(instruccion) > 500:
            await update.message.reply_text(
                "❌ Instrucción demasiado larga (máx 500 caracteres)"
            )
            return
        
        # Crear mensaje de espera
        mensaje_espera = await update.message.reply_text(
            f"⏳ <b>Generando video...</b>\n\n"
            f"<b>Instrucción:</b> {instruccion}\n"
            f"<b>Usuario:</b> @{username}\n\n"
            f"<i>Paso 1/6: Extrayendo contexto...</i>",
            parse_mode="HTML"
        )
        
        try:
            # Almacenar job activo
            self.active_jobs[usuario_id] = {
                "instruccion": instruccion,
                "mensaje_id": mensaje_espera.message_id,
                "status": "generando"
            }
            
            # Generar video
            print(f"\n👤 @{username} (ID: {usuario_id})")
            print(f"📝 Instrucción: {instruccion}\n")
            
            video_path = self.generator.generar_video(
                instruccion=instruccion,
                usuario_id=usuario_id
            )
            
            # Si falla la generación
            if not video_path:
                await mensaje_espera.edit_text(
                    "❌ <b>Error generando video</b>\n\n"
                    "<i>Posibles causas:</i>\n"
                    "• Las APIs no están disponibles\n"
                    "• Error en la base de datos\n"
                    "• Remotion no está instalado\n\n"
                    "Intenta de nuevo más tarde.",
                    parse_mode="HTML"
                )
                self.active_jobs[usuario_id]["status"] = "error"
                return
            
            # Actualizar mensaje: preparando para envío
            await mensaje_espera.edit_text(
                f"📤 <b>Enviando video...</b>\n"
                f"<i>Tamaño: Calculando...</i>",
                parse_mode="HTML"
            )
            
            # Verificar que el archivo existe
            if not Path(video_path).exists():
                await mensaje_espera.edit_text(
                    f"❌ <b>Error:</b> Archivo de video no encontrado\n"
                    f"Ubicación esperada: {video_path}",
                    parse_mode="HTML"
                )
                return
            
            # Obtener tamaño del archivo
            file_size = Path(video_path).stat().st_size
            file_size_mb = file_size / (1024 * 1024)
            
            # Enviar video
            with open(video_path, 'rb') as f:
                await update.message.reply_video(
                    video=f,
                    caption=(
                        f"✅ <b>Video generado exitosamente</b>\n\n"
                        f"<b>Instrucción:</b> {instruccion}\n"
                        f"<b>Tamaño:</b> {file_size_mb:.2f} MB\n"
                        f"<b>Usuario:</b> @{username}"
                    ),
                    parse_mode="HTML",
                    supports_streaming=True,
                    thumb=None
                )
            
            # Borrar mensaje de espera
            try:
                await mensaje_espera.delete()
            except:
                pass
            
            # Marcar como completado
            self.active_jobs[usuario_id]["status"] = "completado"
            
            print(f"✅ Video enviado a @{username}")
            print(f"   Tamaño: {file_size_mb:.2f} MB\n")
        
        except Exception as e:
            error_msg = str(e)[:200]
            
            try:
                await mensaje_espera.edit_text(
                    f"❌ <b>Error:</b>\n{error_msg}",
                    parse_mode="HTML"
                )
            except:
                await update.message.reply_text(
                    f"❌ <b>Error:</b>\n{error_msg}",
                    parse_mode="HTML"
                )
            
            self.active_jobs[usuario_id]["status"] = "error"
            
            print(f"❌ Error para @{username}: {error_msg}\n")
    
    async def handle_video_status(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):
        """
        Comando para ver estado del sistema.
        
        Uso: /vstatus
        """
        
        try:
            # Verificar APIs
            status_apis = self.generator.api.get_status() if self.generator.api else {}
            
            apis_online = sum(1 for v in status_apis.values() if v)
            apis_total = len(status_apis)
            
            # Construir mensaje
            mensaje = (
                "📊 <b>Estado del Sistema - Video Generator</b>\n\n"
                f"<b>APIs:</b> {apis_online}/{apis_total} disponibles\n"
            )
            
            if status_apis:
                for api_name, disponible in status_apis.items():
                    estado = "✅" if disponible else "❌"
                    mensaje += f"  {estado} {api_name.upper()}\n"
            
            mensaje += f"\n<b>Trabajos activos:</b> {len(self.active_jobs)}\n"
            
            # Mostrar trabajos activos
            for user_id, job in list(self.active_jobs.items())[-5:]:  # Últimos 5
                status = job.get("status", "desconocido")
                instruccion = job.get("instruccion", "?")[:40]
                emoji_status = "⏳" if status == "generando" else "✅" if status == "completado" else "❌"
                mensaje += f"  {emoji_status} {instruccion}...\n"
            
            mensaje += (
                "\n<b>Componentes:</b>\n"
                f"  ✅ VideoGenerator\n"
                f"  ✅ APIManager\n"
                f"  ✅ Remotion\n"
                f"\n<i>Comandos disponibles:</i>\n"
                f"  /video &lt;descripción&gt; - Generar video\n"
                f"  /vstatus - Ver estado"
            )
            
            await update.message.reply_text(mensaje, parse_mode="HTML")
        
        except Exception as e:
            await update.message.reply_text(
                f"❌ Error obteniendo estado: {str(e)[:100]}",
                parse_mode="HTML"
            )
    
    async def handle_video_list(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):
        """
        Comando para listar videos generados.
        
        Uso: /vlist
        """
        
        usuario_id = str(update.effective_user.id)
        
        try:
            # Buscar videos del usuario
            output_dir = self.generator.output_dir
            videos_usuario = list(output_dir.glob(f"video_{usuario_id}_*.mp4"))
            
            if not videos_usuario:
                await update.message.reply_text(
                    "📭 <b>No tienes videos generados aún</b>\n\n"
                    "Usa /video para crear tu primer video",
                    parse_mode="HTML"
                )
                return
            
            # Ordenar por fecha (más nuevos primero)
            videos_usuario.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            mensaje = f"📹 <b>Tus videos ({len(videos_usuario)})</b>\n\n"
            
            for i, video_path in enumerate(videos_usuario[:10], 1):
                size_mb = video_path.stat().st_size / (1024 * 1024)
                mtime = Path(video_path).stat().st_mtime
                
                from datetime import datetime
                fecha = datetime.fromtimestamp(mtime).strftime("%d/%m %H:%M")
                
                mensaje += f"{i}. {video_path.name}\n"
                mensaje += f"   Size: {size_mb:.1f} MB | {fecha}\n"
            
            await update.message.reply_text(mensaje, parse_mode="HTML")
        
        except Exception as e:
            await update.message.reply_text(
                f"❌ Error: {str(e)[:100]}",
                parse_mode="HTML"
            )


def setup_video_handlers(application, video_generator: Optional[VideoGenerator] = None):
    """
    Configura los handlers de video en una aplicación python-telegram-bot.
    
    Usage:
        from telegram.ext import Application, CommandHandler
        from video_handler import setup_video_handlers
        
        app = Application.builder().token(TOKEN).build()
        setup_video_handlers(app)
        app.run_polling()
    
    Args:
        application: Instancia de Application de python-telegram-bot
        video_generator: Instancia de VideoGenerator (opcional)
    """
    
    handler = TelegramVideoHandler(video_generator)
    
    # Importar CommandHandler
    try:
        from telegram.ext import CommandHandler
    except ImportError:
        print("❌ python-telegram-bot no está instalado")
        return
    
    # Registrar handlers
    application.add_handler(CommandHandler("video", handler.handle_video_command))
    application.add_handler(CommandHandler("v", handler.handle_video_command))
    application.add_handler(CommandHandler("vstatus", handler.handle_video_status))
    application.add_handler(CommandHandler("vlist", handler.handle_video_list))
    
    print("✅ Video handlers configurados en Telegram Bot")
    print("   Comandos: /video, /v, /vstatus, /vlist")


if __name__ == "__main__":
    # Test de importación
    print("✅ TelegramVideoHandler importado correctamente")
    
    if Update and ContextTypes:
        print("✅ python-telegram-bot disponible")
    else:
        print("⚠️ python-telegram-bot no disponible (instala: pip install python-telegram-bot)")
