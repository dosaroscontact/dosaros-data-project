"""
video_generator.py — Generador de videos para Dos Aros
Integración: Editor Pro Max + Claude/Gemini + SQLite

Uso:
    gen = VideoGenerator()
    video_path = gen.generar_video("Top 3 tiradores 3P NBA esta semana")
"""

import json
import os
import re
import sqlite3
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from src.utils.api_manager import APIManager

DB_PATH         = os.getenv("LOCAL_DB", "/mnt/nba_data/dosaros_local.db")
EDITOR_PRO_PATH = os.getenv("EDITOR_PRO_MAX_PATH", "")  # path absoluto o vacío → autodetectar

# Paleta Dos Aros
BRAND_COLORS = {
    "azul":    "#0D1321",
    "magenta": "#B1005A",
    "naranja": "#F28C28",
    "gris":    "#E6E8EE",
    "mint":    "#88D4AB",   # makes en shot chart
    "coral":   "#FF8787",   # misses en shot chart
    "blanco":  "#FFFFFF",
}

# Columnas disponibles por tabla (para generar SQL correcto)
SCHEMA = {
    "nba_players_games": [
        "SEASON_ID", "PLAYER_ID", "PLAYER_NAME", "TEAM_ABBREVIATION", "TEAM_NAME",
        "GAME_ID", "GAME_DATE", "MATCHUP", "WL", "MIN",
        "PTS", "FGM", "FGA", "FG_PCT", "FG3M", "FG3A", "FG3_PCT",
        "FTM", "FTA", "FT_PCT", "OREB", "DREB", "REB", "AST",
        "STL", "BLK", "TOV", "PF", "PLUS_MINUS",
    ],
    "euro_players_games": [
        "game_id", "player_id", "team_id", "pts", "reb", "ast",
    ],
    "nba_games": [
        "SEASON_ID", "TEAM_ID", "TEAM_ABBREVIATION", "TEAM_NAME",
        "GAME_ID", "GAME_DATE", "MATCHUP", "WL", "PTS",
        "FGM", "FGA", "FG3M", "FG3A", "REB", "AST", "STL", "BLK",
    ],
    "euro_games": [
        "game_id", "date", "home_team", "away_team", "score_home", "score_away",
    ],
}


class VideoGenerator:
    """Generador de videos Dos Aros usando Editor Pro Max + IA."""

    def __init__(self):
        self.api = APIManager()
        self.editor_path = self._resolver_editor_path()
        self.output_dir  = Path(__file__).parents[3] / "assets" / "video_output"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    # ──────────────────────────────────────────────
    # Setup
    # ──────────────────────────────────────────────

    def _resolver_editor_path(self) -> Optional[Path]:
        """Devuelve el path de Editor Pro Max o None si no está instalado."""
        candidatos = [
            Path(EDITOR_PRO_PATH) if EDITOR_PRO_PATH else None,
            Path(__file__).parents[3] / "editor_pro_max",
            Path.cwd() / "editor_pro_max",
        ]
        for c in candidatos:
            if c and c.exists():
                return c
        return None

    def _verificar_editor(self):
        """Lanza ValueError si Editor Pro Max no está disponible."""
        if not self.editor_path:
            raise ValueError(
                "Editor Pro Max no encontrado. "
                "Clónalo en la raíz del proyecto: "
                "git clone https://github.com/Hainrixz/editor-pro-max.git"
            )

    # ──────────────────────────────────────────────
    # API pública
    # ──────────────────────────────────────────────

    def generar_video(self, instruccion: str, usuario_id: str = "bot") -> Optional[str]:
        """
        Genera un video MP4 a partir de una instrucción en lenguaje natural.

        Args:
            instruccion: Descripción del video (ej. "Top 3 tiradores 3P NBA")
            usuario_id:  Identificador del usuario (para nombrar el archivo)

        Returns:
            Path al MP4 generado, o None si falla.
        """
        print(f"\n{'='*60}")
        print(f"GENERADOR DE VIDEOS — Dos Aros")
        print(f"Instrucción: {instruccion}")
        print(f"{'='*60}")

        try:
            self._verificar_editor()

            print("[1/6] Extrayendo contexto...")
            contexto = self._extraer_contexto(instruccion)
            print(f"      {contexto}")

            print("[2/6] Consultando BD...")
            datos = self._consultar_datos(contexto)
            print(f"      {datos.get('count', 0)} registros")

            print("[3/6] Generando prompt para Claude...")
            prompt_claude = self._construir_prompt_tsx(instruccion, datos, contexto)

            print("[4/6] Claude generando composición TSX...")
            tsx = self._generar_tsx(prompt_claude)
            if not tsx or len(tsx) < 100:
                raise ValueError("Composición TSX demasiado corta o vacía")
            print(f"      {len(tsx)} caracteres")

            print("[5/6] Guardando composición...")
            comp_path = self._guardar_tsx(tsx, usuario_id)
            print(f"      {comp_path}")

            print("[6/6] Renderizando con Remotion...")
            video_path = self._renderizar(comp_path, usuario_id)

            print(f"\n✅ Video generado: {video_path}")
            return str(video_path)

        except Exception as e:
            print(f"\n❌ Error generando video: {e}")
            import traceback
            traceback.print_exc()
            return None

    # ──────────────────────────────────────────────
    # Pasos internos
    # ──────────────────────────────────────────────

    def _extraer_contexto(self, instruccion: str) -> Dict:
        """Usa IA para extraer parámetros del video desde lenguaje natural."""
        prompt = (
            f'Analiza esta instrucción de video y devuelve JSON puro (sin markdown):\n'
            f'"{instruccion}"\n\n'
            '{\n'
            '  "tipo": "top3|resultado|comparativa|analisis|hilo|otro",\n'
            '  "liga": "nba|euro|ambas",\n'
            '  "equipo": "codigo_o_null",\n'
            '  "jugador": "nombre_o_null",\n'
            '  "periodo": "hoy|semana|mes|temporada",\n'
            '  "estadistica": "PTS|FG3M|AST|REB|otro",\n'
            '  "template": "tiktok|instagram|youtube|analysis",\n'
            '  "duracion_seg": 45\n'
            '}'
        )
        try:
            resp = self.api.generate_text(prompt=prompt, providers=['gemini', 'groq'])
            resp = re.sub(r'```(?:json)?|```', '', resp).strip()
            match = re.search(r'\{.*\}', resp, re.DOTALL)
            contexto = json.loads(match.group(0)) if match else {}
        except Exception:
            contexto = {}

        # Defaults
        defaults = {
            "tipo": "analisis", "liga": "nba", "template": "tiktok",
            "duracion_seg": 45, "estadistica": "PTS", "periodo": "semana",
        }
        for k, v in defaults.items():
            if not contexto.get(k):
                contexto[k] = v
        return contexto

    def _consultar_datos(self, contexto: Dict) -> Dict:
        """Usa VideoDataExtractor para obtener datos precisos desde BD."""
        from src.integrations.video_generator.video_data_extractor import (
            extraer_jugador_desde_instruccion,
            obtener_datos_jugador,
        )

        instruccion = contexto.get("instruccion_original", "")

        # Intentar extraer jugador y obtener sus datos
        extraccion = extraer_jugador_desde_instruccion(instruccion)
        if extraccion:
            nombre_mapped = extraccion["nombre_mapped"]
            stat = extraccion["stat"]
            datos = obtener_datos_jugador(nombre_mapped, stat, num_partidos=20)
            if datos.get("count", 0) > 0:
                return datos

        # Fallback: usar la lógica anterior (genérica)
        liga = contexto.get("liga", "nba")
        tipo = contexto.get("tipo", "analisis")
        stat = contexto.get("estadistica", "PTS").upper()
        periodo = contexto.get("periodo", "semana")
        dias = {"hoy": 1, "semana": 7, "mes": 30, "temporada": 365}.get(periodo, 7)

        if liga == "nba":
            if tipo == "top3":
                sql = f"""
                    SELECT PLAYER_NAME, TEAM_ABBREVIATION,
                           ROUND(AVG({stat}), 1) AS valor
                    FROM nba_players_games
                    WHERE GAME_DATE >= date('now', '-{dias} days')
                      AND {stat} IS NOT NULL
                    GROUP BY PLAYER_NAME, TEAM_ABBREVIATION
                    HAVING COUNT(*) >= 1
                    ORDER BY valor DESC
                    LIMIT 5
                """
            else:
                sql = f"""
                    SELECT PLAYER_NAME, TEAM_ABBREVIATION,
                           ROUND(AVG({stat}), 1) AS valor
                    FROM nba_players_games
                    WHERE GAME_DATE >= date('now', '-{dias} days')
                      AND {stat} IS NOT NULL
                    GROUP BY PLAYER_NAME, TEAM_ABBREVIATION
                    ORDER BY valor DESC
                    LIMIT 5
                """
        else:
            stat_euro = stat.lower()
            if stat_euro not in ("pts", "reb", "ast"):
                stat_euro = "pts"
            sql = f"""
                SELECT player_id, team_id,
                       ROUND(AVG({stat_euro}), 1) AS valor
                FROM euro_players_games
                GROUP BY player_id, team_id
                ORDER BY valor DESC
                LIMIT 5
            """

        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.execute(sql)
            cols = [d[0] for d in cursor.description]
            filas = cursor.fetchall()
            conn.close()
            registros = [dict(zip(cols, f)) for f in filas]
            return {"registros": registros, "count": len(registros), "sql": sql}
        except Exception as e:
            print(f"  Error BD: {e}")
            return {"registros": [], "count": 0, "error": str(e)}

    def _construir_prompt_tsx(self, instruccion: str, datos: Dict, contexto: Dict) -> str:
        """Construye el mega-prompt que enviamos a Claude para generar la composición TSX."""
        template  = contexto.get("template", "tiktok")
        duracion  = contexto.get("duracion_seg", 45)
        fps       = 30
        frames    = duracion * fps
        dims      = "1080×1920" if template in ("tiktok", "instagram") else "1920×1080"

        datos_str = json.dumps(datos.get("registros", [])[:5], ensure_ascii=False, indent=2)

        return f"""
Crea una composición Remotion (React/TypeScript) para Dos Aros Basketball Analytics.

INSTRUCCIÓN: "{instruccion}"
TIPO: {contexto.get('tipo')} | LIGA: {contexto.get('liga')} | TEMPLATE: {template}
DIMENSIONES: {dims} | FRAMES: {frames} @ {fps}fps

DATOS REALES (usar en el video):
{datos_str}

PALETA DOS AROS:
- Azul (#0D1321): fondos principales, titulares
- Magenta (#B1005A): dato destacado, accents
- Naranja (#F28C28): detalles, íconos
- Gris (#E6E8EE): separadores, texto secundario
- Mint (#88D4AB): positivo / makes
- Coral (#FF8787): negativo / misses
- Blanco (#FFFFFF): fondo posts

TIPOGRAFÍAS: usa fontFamily "system-ui" o "sans-serif" (no importes fuentes externas)

REGLAS CRÍTICAS:
1. SOLO imports desde 'remotion' — NO importes desde '../components', '../presets' ni ningún otro módulo local
2. El componente debe ser 100% auto-contenido con React inline styles
3. Sin fetch/async en render · Sin console.log · Sin imports de imágenes
4. Usa AbsoluteFill, Sequence, interpolate, useCurrentFrame de remotion
5. Incorpora los datos reales de la BD en el texto del video
6. Estética: analítica y limpia, fondos sólidos con colores de la paleta

FORMATO: devuelve SOLO el código entre triple backticks tsx:

```tsx
import {{ AbsoluteFill, Sequence, interpolate, useCurrentFrame }} from 'remotion';

export const DosarosVideo = () => {{
  const frame = useCurrentFrame();
  // ... composición completa con datos reales incrustados
  return (
    <AbsoluteFill style={{{{ backgroundColor: '#0D1321' }}}}>
      ...
    </AbsoluteFill>
  );
}};
```
"""

    def _generar_tsx(self, prompt: str) -> str:
        """Llama a Claude/Gemini para generar la composición TSX."""
        system = (
            "Eres experto en Remotion y React. "
            "Generas TypeScript válido, limpio y listo para ejecutar. "
            "Responde SOLO con código, sin explicaciones."
        )
        resp = self.api.generate_text(
            prompt=prompt,
            system_prompt=system,
            providers=['claude', 'gemini', 'groq', 'openai'],
        )
        # Extraer código de markdown
        for delim in ["```tsx", "```typescript", "```"]:
            if delim in resp:
                partes = resp.split(delim)
                if len(partes) >= 2:
                    resp = partes[1].split("```")[0] if "```" in partes[1] else partes[1]
                break
        return resp.strip()

    def _guardar_tsx(self, tsx: str, usuario_id: str) -> Path:
        """Guarda el TSX en src/compositions/ dentro de Editor Pro Max."""
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre = f"dosaros_{usuario_id}_{ts}.tsx"
        compositions_dir = self.editor_path / "src" / "compositions"
        compositions_dir.mkdir(parents=True, exist_ok=True)
        path = compositions_dir / nombre
        path.write_text(tsx, encoding="utf-8")
        return path

    def _renderizar(self, comp_path: Path, usuario_id: str) -> Path:
        """Renderiza el video con Remotion CLI y devuelve el path al MP4."""
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        output = self.output_dir / f"video_{usuario_id}_{ts}.mp4"

        # Extraer nombre del componente exportado
        contenido = comp_path.read_text(encoding="utf-8")
        match = re.search(r'export\s+const\s+(\w+)\s*=', contenido)
        nombre_comp = match.group(1) if match else "DosarosVideo"

        # Registrar composición en Root.tsx de Editor Pro Max
        root_path = self.editor_path / "src" / "Root.tsx"
        root_original = root_path.read_text(encoding="utf-8")

        rel_import = f"./compositions/{comp_path.stem}"
        linea_import = f'import {{ {nombre_comp} }} from "{rel_import}";\n'
        linea_comp = (
            f'\n      <Composition\n'
            f'        id="{nombre_comp}"\n'
            f'        component={{{nombre_comp}}}\n'
            f'        durationInFrames={{1350}}\n'
            f'        fps={{30}}\n'
            f'        width={{1080}}\n'
            f'        height={{1920}}\n'
            f'      />'
        )

        nuevo_root = linea_import + root_original
        inyectado = False
        for patron in ['</>', '</RemotionRoot>', '</React.Fragment>']:
            if patron in nuevo_root:
                nuevo_root = nuevo_root.replace(patron, linea_comp + '\n    ' + patron, 1)
                inyectado = True
                break

        if not inyectado:
            raise RuntimeError(
                "No se pudo inyectar la composición en Root.tsx. "
                f"Patrones buscados: </>, </RemotionRoot>, </React.Fragment>"
            )

        cmd = ["npx", "remotion", "render", nombre_comp, str(output), "--log=error"]
        print(f"  Ejecutando: {' '.join(cmd)}")

        original_cwd = os.getcwd()
        try:
            root_path.write_text(nuevo_root, encoding="utf-8")
            os.chdir(self.editor_path)
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        finally:
            root_path.write_text(root_original, encoding="utf-8")
            comp_path.unlink(missing_ok=True)
            os.chdir(original_cwd)

        if result.returncode != 0:
            raise RuntimeError(f"Remotion error:\n{result.stderr or result.stdout}")

        if not output.exists():
            raise FileNotFoundError(f"MP4 no generado en {output}")

        print(f"  Tamaño: {output.stat().st_size / 1_048_576:.1f} MB")
        return output
