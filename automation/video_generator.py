"""
VideoGenerator para Dos Aros
Integración: Editor Pro Max + Claude + SQLite

Uso:
    gen = VideoGenerator()
    video_path = gen.generar_video("Top 3 tiradores 3P NBA esta semana")
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime

# Path setup
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importa desde tu proyecto
try:
    from src.utils.api_manager import APIManager
    from src.database.database import consultar_db_local
except ImportError:
    print("⚠️ Importaciones fallaron, asegúrate de estar en el directorio raíz de Dos Aros")
    APIManager = None
    consultar_db_local = None


class VideoGenerator:
    """Generador de videos para Dos Aros usando Editor Pro Max + Claude"""
    
    def __init__(self, editor_pro_max_path: Optional[str] = None):
        """
        Inicializa el generador de videos.
        
        Args:
            editor_pro_max_path: Path a Editor Pro Max (default: ./editor_pro_max)
        """
        self.api = APIManager() if APIManager else None
        
        # Resolver path de Editor Pro Max
        if editor_pro_max_path:
            self.editor_pro_max_path = Path(editor_pro_max_path)
        else:
            # Intenta encontrarlo automáticamente
            self.editor_pro_max_path = Path(__file__).parent / "editor_pro_max"
            if not self.editor_pro_max_path.exists():
                self.editor_pro_max_path = Path.cwd() / "editor_pro_max"
        
        # Output directory
        self.output_dir = Path(__file__).parent / "assets" / "video_output"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Validaciones
        self._validar_setup()
    
    def _validar_setup(self):
        """Valida que todo está configurado correctamente"""
        
        print("🔍 Validando setup...")
        
        # 1. Editor Pro Max path
        if not self.editor_pro_max_path.exists():
            raise ValueError(
                f"❌ Editor Pro Max no encontrado en {self.editor_pro_max_path}\n"
                f"   Clona el repo: git clone https://github.com/Hainrixz/editor-pro-max.git"
            )
        print(f"✅ Editor Pro Max: {self.editor_pro_max_path}")
        
        # 2. API Manager
        if not self.api:
            raise ValueError(
                "❌ APIManager no disponible. Verifica que src/utils/api_manager.py existe"
            )
        
        # 3. Remotion CLI
        try:
            result = subprocess.run(
                ["npx", "remotion", "--version"],
                cwd=self.editor_pro_max_path,
                capture_output=True,
                timeout=10
            )
            if result.returncode == 0:
                print(f"✅ Remotion: {result.stdout.decode().strip()}")
            else:
                print("⚠️ Remotion puede no estar instalado, intenta: npm install")
        except Exception as e:
            print(f"⚠️ No se pudo verificar Remotion: {e}")
        
        # 4. FFmpeg
        try:
            result = subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                version = result.stdout.decode().split('\n')[0]
                print(f"✅ FFmpeg: {version}")
            else:
                print("⚠️ FFmpeg no disponible")
        except Exception:
            print("⚠️ FFmpeg no encontrado, instala: sudo apt-get install ffmpeg")
        
        print("✅ Setup validado\n")
    
    def generar_video(
        self,
        instruccion: str,
        usuario_id: str = "telegram_user",
        preset: str = "default"
    ) -> Optional[str]:
        """
        Genera un video basado en una instrucción natural.
        
        Args:
            instruccion: Descripción del video (ej: "Top 3 tiradores 3P NBA")
            usuario_id: ID único del usuario (para tracking y caché)
            preset: Tipo de preset (default, nba, euro, analysis, etc)
        
        Returns:
            Path al video generado como string, o None si falla
        
        Example:
            >>> gen = VideoGenerator()
            >>> video = gen.generar_video("Top 3 tiradores 3P NBA esta semana")
            >>> print(f"Video: {video}")
        """
        
        print("\n" + "="*60)
        print("🎬 GENERADOR DE VIDEOS - Dos Aros")
        print("="*60)
        print(f"Instrucción: {instruccion}")
        print(f"Usuario: {usuario_id}")
        print(f"Preset: {preset}")
        print("="*60 + "\n")
        
        try:
            # PASO 1: Extraer contexto
            print("[1/6] Extrayendo contexto de la instrucción...")
            contexto = self._extraer_contexto(instruccion)
            print(f"      ✅ Contexto: {contexto}\n")
            
            # PASO 2: Consultar datos de BD
            print("[2/6] Consultando base de datos...")
            datos_bd = self._consultar_datos(contexto)
            print(f"      ✅ {datos_bd.get('count', 0)} registros obtenidos\n")
            
            # PASO 3: Generar prompt para Claude
            print("[3/6] Generando prompt para Claude...")
            prompt_claude = self._generar_prompt_claude(instruccion, datos_bd, contexto)
            print(f"      ✅ Prompt generado ({len(prompt_claude)} caracteres)\n")
            
            # PASO 4: Generar composición TSX
            print("[4/6] Claude generando composición TypeScript...")
            composicion_tsx = self._generar_composicion_tsx(prompt_claude, contexto)
            if not composicion_tsx or len(composicion_tsx) < 100:
                raise ValueError("Composición generada demasiado corta o vacía")
            print(f"      ✅ Composición generada ({len(composicion_tsx)} caracteres)\n")
            
            # PASO 5: Guardar composición
            print("[5/6] Guardando composición en Editor Pro Max...")
            composicion_path = self._guardar_composicion(composicion_tsx, usuario_id)
            print(f"      ✅ Guardado en: {composicion_path}\n")
            
            # PASO 6: Renderizar video
            print("[6/6] Renderizando video con Remotion...")
            video_path = self._renderizar_video(composicion_path, usuario_id)
            
            print("\n" + "="*60)
            print("✅ VIDEO GENERADO EXITOSAMENTE")
            print("="*60)
            print(f"Ubicación: {video_path}")
            print("="*60 + "\n")
            
            return str(video_path)
        
        except Exception as e:
            print("\n" + "="*60)
            print(f"❌ ERROR: {str(e)}")
            print("="*60 + "\n")
            import traceback
            traceback.print_exc()
            return None
    
    def _extraer_contexto(self, instruccion: str) -> Dict:
        """
        Extrae parámetros clave de la instrucción usando IA.
        
        Retorna un dict con:
        - tipo: resultado, top3, comparativa, analisis, etc
        - liga: nba, euro, ambas
        - template: tiktok, instagram, youtube, announcement, etc
        - duracion_segundos: 30-90
        """
        
        prompt = f"""
        Analiza esta instrucción de video y extrae los parámetros en JSON puro:
        
        "{instruccion}"
        
        Responde EXACTAMENTE con este JSON (sin markdown ni explicaciones):
        {{
            "tipo": "resultado|top3|comparativa|analisis|hilo|otro",
            "liga": "nba|euro|ambas",
            "equipo": "codigo_equipo_o_null",
            "jugador": "nombre_jugador_o_null",
            "periodo": "hoy|semana|mes|temporada",
            "estadistica": "pts|3p|ast|reb|pir|otro",
            "template": "tiktok|instagram|youtube|announcement|analysis|comparativa",
            "duracion_segundos": 30,
            "notas": "requisitos_especiales_o_null"
        }}
        """
        
        try:
            response = self.api.generate_text(
                prompt=prompt,
                providers=['gemini', 'claude']
            )
            
            # Limpiar markdown
            for tag in ["```json", "```", "```python"]:
                if tag in response:
                    response = response.replace(tag, "")
            
            contexto = json.loads(response.strip())
            
            # Validar y poner defaults
            defaults = {
                "tipo": "analisis",
                "liga": "nba",
                "template": "tiktok",
                "duracion_segundos": 45
            }
            
            for key, default_val in defaults.items():
                if key not in contexto or not contexto[key]:
                    contexto[key] = default_val
            
            return contexto
        
        except json.JSONDecodeError as e:
            print(f"⚠️ No se pudo parsear JSON: {response[:200]}")
            return {
                "tipo": "analisis",
                "liga": "nba",
                "template": "tiktok",
                "duracion_segundos": 45
            }
    
    def _consultar_datos(self, contexto: Dict) -> Dict:
        """
        Consulta SQLite según el contexto extraído.
        
        Returns:
            Dict con 'registros' (lista) y 'count' (int)
        """
        
        if not consultar_db_local:
            return {"registros": [], "count": 0, "error": "BD no disponible"}
        
        liga = contexto.get("liga", "nba")
        periodo = contexto.get("periodo", "semana")
        estadistica = contexto.get("estadistica", "pts")
        tipo = contexto.get("tipo", "analisis")
        
        sql = None
        
        # Construir SQL según tipo
        if tipo == "top3":
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
            elif liga == "euro":
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
        
        elif tipo == "resultado":
            sql = """
            SELECT game_date, home_team, away_team, home_score, away_score
            FROM games
            WHERE game_date >= date('now', '-1 day')
            ORDER BY game_date DESC
            LIMIT 5
            """
        
        # Default: algunos datos de ejemplo
        if not sql:
            sql = "SELECT player_name, team_abbreviation, pts FROM nba_stats LIMIT 10"
        
        try:
            datos = consultar_db_local(sql)
            
            if not datos:
                return {"registros": [], "count": 0}
            
            # Convertir a list de dicts si es necesario
            if isinstance(datos, list):
                registros = datos
            else:
                registros = [datos] if datos else []
            
            return {
                "registros": registros,
                "count": len(registros),
                "tipo": tipo,
                "liga": liga
            }
        
        except Exception as e:
            print(f"⚠️ Error consultando BD: {e}")
            return {"registros": [], "count": 0, "error": str(e)}
    
    def _generar_prompt_claude(
        self, 
        instruccion: str, 
        datos_bd: Dict, 
        contexto: Dict
    ) -> str:
        """Genera el mega-prompt para que Claude cree la composición Remotion"""
        
        template = contexto.get("template", "tiktok")
        duracion = contexto.get("duracion_segundos", 45)
        fps = 30
        frames = int(duracion * fps)
        
        datos_str = json.dumps(datos_bd, ensure_ascii=False, indent=2)[:1000]  # Limitar a 1000 chars
        
        prompt = f"""
        TAREA: Crear una composición Remotion (React/TypeScript) para generar un video.
        
        INSTRUCCIÓN DEL USUARIO:
        "{instruccion}"
        
        CONTEXTO:
        - Tipo: {contexto.get('tipo')}
        - Liga: {contexto.get('liga')}
        - Template: {template}
        - Duración: {duracion} segundos (~{frames} frames a {fps}fps)
        
        DATOS DE LA BD (para usar en el video):
        {datos_str}
        
        INSTRUCCIONES CRÍTICAS:
        
        1. ESTRUCTURA DEL CÓDIGO:
           - Usa React 19 + Remotion 4.0.440
           - TypeScript válido
           - Importa componentes SOLO de ../components o ../presets
           - Exporta como: export const [NombreComposicion] = () => {{ ... }}
        
        2. DIMENSIONES (según template):
           - {template}: 1080x1920
           - announcement/analysis: 1920x1080
        
        3. DURACIÓN:
           - Durationframes = {frames}
           - Compón con Sequence para cada sección
        
        4. COLORES DOS AROS:
           - Mint: #88D4AB
           - Coral: #FF8787
           - Gris: #5A5A5A
        
        5. DATOS REALES:
           - Incorpora nombres, números, estadísticas de los datos de BD
           - Úsalos en TypewriterText, AnimatedTitle, CaptionOverlay
        
        6. COMPONENTES DISPONIBLES:
        
           TEXT:
           - AnimatedTitle (8 estilos)
           - TypewriterText
           - WordByWordCaption
           - CaptionOverlay (TikTok-style)
           - LowerThird
        
           MEDIA:
           - FitVideo, FitImage (Ken Burns)
           - VideoClip, JumpCut
           - Slideshow
        
           BACKGROUNDS:
           - GradientBackground
           - ParticleField
           - ColorWash
           - GridPattern
        
           OVERLAYS:
           - ProgressBar
           - Watermark
           - CallToAction
           - CountdownTimer
        
           LAYOUT:
           - SplitScreen
           - PictureInPicture
           - SafeArea
        
           TRANSITIONS:
           - TransitionPresets (crossfade, slide, wipe, clock, etc)
        
        7. VALIDEZ:
           - El código DEBE compilar sin errores TypeScript
           - Sin import de paquetes externos (solo Remotion)
           - Sin fetch/async en render
           - Sin console.log en la composición final
        
        FORMATO DE RESPUESTA:
        
        Devuelve SOLO el código TypeScript entre triple backticks, sin explicaciones:
        
        \`\`\`tsx
        import {{ Composition, Sequence, interpolate, useCurrentFrame, useVideoConfig }} from 'remotion';
        // ... rest del código
        export const MiComposicion = () => {{
          // ... implementación
        }};
        \`\`\`
        """
        
        return prompt
    
    def _generar_composicion_tsx(self, prompt_claude: str, contexto: Dict) -> str:
        """
        Usa Claude para generar la composición TSX.
        
        Returns:
            Código TypeScript limpio sin markdown
        """
        
        system_prompt = (
            "Eres un experto en Remotion y React. "
            "Generas código TypeScript válido, limpio y listo para ejecutar. "
            "Responde SOLO con código, sin explicaciones adicionales."
        )
        
        response = self.api.generate_text(
            prompt=prompt_claude,
            system_prompt=system_prompt,
            providers=['claude', 'gemini']
        )
        
        # Extraer código de markdown
        code = response
        for delimiter in ["```tsx", "```typescript", "```"]:
            if delimiter in code:
                parts = code.split(delimiter)
                if len(parts) >= 2:
                    code = parts[1].split("```")[0] if "```" in parts[1] else parts[1]
                break
        
        return code.strip()
    
    def _guardar_composicion(self, codigo_tsx: str, usuario_id: str) -> Path:
        """Guarda la composición en src/compositions/"""
        
        # Crear nombre único
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"user_{usuario_id}_{timestamp}.tsx"
        
        # Ruta en Editor Pro Max
        compositions_dir = self.editor_pro_max_path / "src" / "compositions"
        compositions_dir.mkdir(parents=True, exist_ok=True)
        
        archivo_path = compositions_dir / nombre_archivo
        
        # Guardar
        with open(archivo_path, 'w', encoding='utf-8') as f:
            f.write(codigo_tsx)
        
        if not archivo_path.exists():
            raise FileNotFoundError(f"No se pudo guardar: {archivo_path}")
        
        return archivo_path
    
    def _renderizar_video(self, composicion_path: Path, usuario_id: str) -> Path:
        """
        Usa Remotion CLI para renderizar el video.
        
        Comando aproximado:
        npx remotion render NombreComposicion output.mp4
        """
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_salida = f"video_{usuario_id}_{timestamp}.mp4"
        output_path = self.output_dir / nombre_salida
        
        # Extraer nombre de la composición del archivo
        with open(composicion_path, encoding='utf-8') as f:
            contenido = f.read()
        
        import re
        match = re.search(r'export\s+const\s+(\w+)\s*=', contenido)
        nombre_composicion = match.group(1) if match else "MiComposicion"
        
        try:
            # Cambiar a directorio de Editor Pro Max
            original_cwd = os.getcwd()
            os.chdir(self.editor_pro_max_path)
            
            # Comando Remotion
            cmd = [
                "npx",
                "remotion",
                "render",
                nombre_composicion,
                str(output_path)
            ]
            
            print(f"   Ejecutando: {' '.join(cmd)}")
            print(f"   En directorio: {os.getcwd()}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minutos
            )
            
            # Volver al directorio original
            os.chdir(original_cwd)
            
            # Verificar resultado
            if result.returncode != 0:
                error_msg = result.stderr if result.stderr else result.stdout
                raise Exception(f"Remotion error: {error_msg}")
            
            # Verificar que el archivo existe
            if not output_path.exists():
                raise FileNotFoundError(
                    f"Video no generado en {output_path}\n"
                    f"stdout: {result.stdout}\n"
                    f"stderr: {result.stderr}"
                )
            
            file_size = output_path.stat().st_size / (1024 * 1024)  # MB
            print(f"   Tamaño: {file_size:.2f} MB")
            
            return output_path
        
        except subprocess.TimeoutExpired:
            os.chdir(original_cwd)
            raise Exception("⏱️ Timeout renderizando (>10 min)")
        except Exception as e:
            os.chdir(original_cwd)
            raise Exception(f"Error renderizando: {e}")


if __name__ == "__main__":
    # Test
    print("Inicializando VideoGenerator...")
    gen = VideoGenerator()
    
    print("\nTest: Generando video...")
    video = gen.generar_video(
        "Crea un TikTok con los top 3 tiradores de 3 puntos NBA esta semana",
        usuario_id="test_001"
    )
    
    if video:
        print(f"✅ Video generado: {video}")
    else:
        print("❌ Error generando video")
