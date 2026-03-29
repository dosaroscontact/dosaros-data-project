"""
================================================================================
CLAUDE DATA ANALYZER - Proyecto Dos Aros
================================================================================
Analiza estadísticas NBA/EuroLeague usando Claude API.
Detecta anomalías, compara equipos y responde preguntas sobre datasets.
================================================================================
"""

import os
import json
import anthropic
from dotenv import load_dotenv

load_dotenv()

MODELO = "claude-opus-4-1"

SYSTEM_ANALISTA = """Eres un analista de datos de baloncesto especializado en NBA y EuroLeague para Dos Aros.
Filosofía: "Datos primero. Contexto después. Opinión al final."
Cuando analices estadísticas:
- Identifica patrones y tendencias con datos concretos
- Contextualiza dentro de la liga/temporada correspondiente
- Sé preciso con los números, nunca inventes datos
- Responde en español, terminología técnica en inglés
- Formato: párrafos cortos, máximo 3 puntos clave"""


class ClaudeDataAnalyzer:
    """Analiza datos estadísticos de baloncesto con Claude."""

    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY no encontrada en variables de entorno")
        self.client = anthropic.Anthropic(api_key=api_key)

    def analyze_stats(self, columnas: list[str], filas: list[list], pregunta: str) -> str:
        """
        Analiza un dataset tabular y responde una pregunta específica.

        Args:
            columnas: Lista de nombres de columnas (ej. ["PLAYER_NAME", "PTS", "AST"])
            filas: Lista de filas como listas de valores
            pregunta: Pregunta en lenguaje natural sobre los datos

        Returns:
            Análisis textual con insights clave
        """
        # Formatea la tabla como texto para el prompt
        cabecera = " | ".join(columnas)
        filas_str = "\n".join(" | ".join(str(v) for v in fila) for fila in filas[:50])
        tabla = f"{cabecera}\n{'-' * len(cabecera)}\n{filas_str}"

        if len(filas) > 50:
            tabla += f"\n... ({len(filas) - 50} filas adicionales no mostradas)"

        mensaje = (
            f"Analiza estos datos y responde la pregunta:\n\n"
            f"DATOS:\n{tabla}\n\n"
            f"PREGUNTA: {pregunta}"
        )

        try:
            with self.client.messages.stream(
                model=MODELO,
                max_tokens=1024,
                thinking={"type": "adaptive"},
                system=SYSTEM_ANALISTA,
                messages=[{"role": "user", "content": mensaje}],
            ) as stream:
                final = stream.get_final_message()
                # El último bloque es el texto de respuesta
                for bloque in reversed(final.content):
                    if bloque.type == "text":
                        return bloque.text.strip()
            return ""
        except anthropic.APIError as e:
            print(f"[ClaudeDataAnalyzer] Error API analyze_stats: {e}")
            return ""

    def compare_teams(
        self,
        team1: str,
        stats1: dict,
        team2: str,
        stats2: dict,
    ) -> str:
        """
        Compara las estadísticas de dos equipos y genera un análisis comparativo.

        Args:
            team1: Nombre/código del primer equipo (ej. "LAL")
            stats1: Dict con estadísticas del equipo 1 (ej. {"PTS": 115.2, "REB": 44.1})
            team2: Nombre/código del segundo equipo (ej. "BOS")
            stats2: Dict con estadísticas del equipo 2

        Returns:
            Análisis comparativo con ventajas/desventajas de cada equipo
        """
        stats1_str = "\n".join(f"  {k}: {v}" for k, v in stats1.items())
        stats2_str = "\n".join(f"  {k}: {v}" for k, v in stats2.items())

        mensaje = (
            f"Compara estadísticamente estos dos equipos:\n\n"
            f"{team1}:\n{stats1_str}\n\n"
            f"{team2}:\n{stats2_str}\n\n"
            f"Identifica ventajas/desventajas de cada equipo en 3-4 puntos clave."
        )

        try:
            with self.client.messages.stream(
                model=MODELO,
                max_tokens=1024,
                thinking={"type": "adaptive"},
                system=SYSTEM_ANALISTA,
                messages=[{"role": "user", "content": mensaje}],
            ) as stream:
                final = stream.get_final_message()
                for bloque in reversed(final.content):
                    if bloque.type == "text":
                        return bloque.text.strip()
            return ""
        except anthropic.APIError as e:
            print(f"[ClaudeDataAnalyzer] Error API compare_teams: {e}")
            return ""

    def detect_anomalies(self, player_stats_history: list[dict]) -> str:
        """
        Detecta actuaciones anómalas (positivas o negativas) en el historial de un jugador.

        Args:
            player_stats_history: Lista de dicts con estadísticas por partido.
                Cada dict debe tener al menos: {"GAME_DATE": ..., "PTS": ..., "AST": ..., ...}

        Returns:
            Descripción de anomalías detectadas con contexto estadístico
        """
        if not player_stats_history:
            return "No hay datos para analizar."

        # Limita a los últimos 30 partidos para no saturar el contexto
        historial = player_stats_history[-30:]
        historial_str = json.dumps(historial, ensure_ascii=False, indent=2)

        mensaje = (
            f"Analiza el historial de partidos de este jugador y detecta anomalías estadísticas:\n\n"
            f"{historial_str}\n\n"
            f"Busca: actuaciones extraordinarias (positive outliers), bajones inusuales "
            f"(negative outliers), rachas, patrones por rival o local/visitante."
        )

        try:
            with self.client.messages.stream(
                model=MODELO,
                max_tokens=1536,
                thinking={"type": "adaptive"},
                system=SYSTEM_ANALISTA,
                messages=[{"role": "user", "content": mensaje}],
            ) as stream:
                final = stream.get_final_message()
                for bloque in reversed(final.content):
                    if bloque.type == "text":
                        return bloque.text.strip()
            return ""
        except anthropic.APIError as e:
            print(f"[ClaudeDataAnalyzer] Error API detect_anomalies: {e}")
            return ""


# ── Funciones de integración para bot_consultas.py ──────────────────────────

def analizar_resultado_consulta(
    columnas: list[str],
    filas: list[list],
    pregunta_original: str,
) -> str:
    """
    Wrapper para bot_consultas.py.
    Analiza el resultado de una consulta SQL con lenguaje natural.

    Ejemplo de uso en bot_consultas:
        from src.integrations.claude_data_analyzer import analizar_resultado_consulta
        insight = analizar_resultado_consulta(cols, rows, pregunta_usuario)
    """
    analizador = ClaudeDataAnalyzer()
    return analizador.analyze_stats(columnas, filas, pregunta_original)


def detectar_perlas_jugador(historial: list[dict]) -> str:
    """
    Wrapper para bot_consultas.py.
    Detecta actuaciones destacadas ('perlas') en el historial de un jugador.
    """
    analizador = ClaudeDataAnalyzer()
    return analizador.detect_anomalies(historial)
