"""
================================================================================
CLAUDE TWEET GENERATOR - Proyecto Dos Aros
================================================================================
Genera y mejora tweets NBA/EuroLeague usando Claude API.
Integrable con bot_consultas.py para generar contenido social automático.
================================================================================
"""

import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

MODELO = "claude-opus-4-1"

# System prompt específico para tweets de baloncesto
SYSTEM_TWEET = """Eres el redactor de redes sociales de Dos Aros, un medio de análisis NBA y EuroLeague.
Filosofía: "Datos primero. Contexto después. Opinión al final."
Estilo: conciso, analítico, con datos concretos. Sin emojis excesivos. Máximo 280 caracteres.
Siempre incluye el dato estadístico exacto. Termina con #DosAros y hashtag del equipo si aplica."""


class ClaudeTweetGenerator:
    """Genera y mejora tweets sobre baloncesto usando Claude."""

    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY no encontrada en variables de entorno")
        self.client = anthropic.Anthropic(api_key=api_key)

    def generate_tweet(self, data_context: str, stat_name: str, stat_value: str) -> str:
        """
        Genera un tweet a partir de un contexto de datos y una estadística destacada.

        Args:
            data_context: Contexto del partido o jugador (ej. "LeBron vs BOS 2024-03-15")
            stat_name: Nombre de la estadística (ej. "puntos", "asistencias")
            stat_value: Valor de la estadística (ej. "42", "15/10/8")

        Returns:
            Tweet listo para publicar (máx. 280 chars)
        """
        mensaje = (
            f"Genera un tweet sobre esta actuación:\n"
            f"Contexto: {data_context}\n"
            f"Estadística destacada: {stat_name} = {stat_value}\n"
            f"El tweet debe tener máximo 280 caracteres."
        )

        try:
            response = self.client.messages.create(
                model=MODELO,
                max_tokens=256,
                system=SYSTEM_TWEET,
                messages=[{"role": "user", "content": mensaje}],
            )
            return response.content[0].text.strip()
        except anthropic.APIError as e:
            print(f"[ClaudeTweetGenerator] Error API: {e}")
            return ""

    def improve_tweet(self, original_tweet: str) -> str:
        """
        Mejora un tweet existente manteniendo el dato clave pero mejorando el impacto.

        Args:
            original_tweet: Tweet original a mejorar

        Returns:
            Tweet mejorado (máx. 280 chars)
        """
        mensaje = (
            f"Mejora este tweet manteniendo el dato estadístico exacto:\n\n"
            f"{original_tweet}\n\n"
            f"Hazlo más impactante y conciso. Máximo 280 caracteres."
        )

        try:
            response = self.client.messages.create(
                model=MODELO,
                max_tokens=256,
                system=SYSTEM_TWEET,
                messages=[{"role": "user", "content": mensaje}],
            )
            return response.content[0].text.strip()
        except anthropic.APIError as e:
            print(f"[ClaudeTweetGenerator] Error API: {e}")
            return original_tweet

    def generate_multiple_variants(self, data_context: str, count: int = 3) -> list[str]:
        """
        Genera múltiples variantes de tweet para el mismo contexto.

        Args:
            data_context: Contexto completo del dato/actuación
            count: Número de variantes a generar (default 3)

        Returns:
            Lista de tweets variantes
        """
        mensaje = (
            f"Genera exactamente {count} versiones distintas de tweet sobre:\n\n"
            f"{data_context}\n\n"
            f"Devuelve SOLO los tweets, uno por línea, sin numeración ni explicaciones. "
            f"Cada tweet máximo 280 caracteres."
        )

        try:
            with self.client.messages.stream(
                model=MODELO,
                max_tokens=1024,
                thinking={"type": "adaptive"},
                system=SYSTEM_TWEET,
                messages=[{"role": "user", "content": mensaje}],
            ) as stream:
                texto = stream.get_final_message().content[-1].text.strip()

            variantes = [t.strip() for t in texto.split("\n") if t.strip()]
            return variantes[:count]
        except anthropic.APIError as e:
            print(f"[ClaudeTweetGenerator] Error API: {e}")
            return []


# ── Funciones de integración para bot_consultas.py ──────────────────────────

def generar_tweet_desde_resultado(data_context: str, stat_name: str, stat_value: str) -> str:
    """
    Wrapper directo para bot_consultas.py.
    Genera un tweet a partir del resultado de una consulta SQL.

    Ejemplo de uso en bot_consultas:
        from src.integrations.claude_tweet_generator import generar_tweet_desde_resultado
        tweet = generar_tweet_desde_resultado(contexto, "puntos", "42")
    """
    generador = ClaudeTweetGenerator()
    return generador.generate_tweet(data_context, stat_name, stat_value)


def mejorar_tweet_bot(tweet_original: str) -> str:
    """
    Wrapper para bot_consultas.py.
    Mejora un tweet generado previamente antes de enviarlo a Telegram.
    """
    generador = ClaudeTweetGenerator()
    return generador.improve_tweet(tweet_original)
